
import math
import errors

# Pre-calculate all information needed to calculate a semantic distance between
# any two terms of an ontology.
# - direct_parents: a dictionary with terms of the ontology as the keys, and
#   a list of the direct parents as the values.
#   Note: unused terms (i.e. terms with a usage of 0) MUST be included; the
#   only term that may not be included is the root term).
# - usage_count: a dictionary with terms of the ontology as the keys, and
#   the number of time these terms are used to annoted an object as values.
#   Note: unused terms can be excluded from this dictionary.
def process (direct_parents, usage_count):

	# we ensure all terms have a non-negative usage count
	for (term_id, cnt) in usage_count.iteritems():
		if (cnt < 0):
			raise ValueError("Invalid usage count for term '%s': %s" % (term_id, cnt))

	# we ensure all terms have at least one parent
	for (term_id, parents) in direct_parents.iteritems():
		if (term_id in parents):
			raise ValueError("Term '%s' is declared as its own parent" % term_id)

		if (len(parents) == 0):
			raise ValueError("Term '%s' has no parent" % term_id)

	# Identification of the term ancestors. For each given term, a
	# list of all the parents (down to the root term) are identified.
	__ancestors = {}

	def back_propagation (term_id, ancestors):
		# the branching node is registered as its own parent
		ancestors[term_id] = True

		# the root node has been reached
		if (not term_id in direct_parents):
			return ancestors

		# starting a new path from each parent
		for parent_id in direct_parents[term_id]:
			ancestors = back_propagation(parent_id, ancestors)

		return ancestors

	for term_id in direct_parents:
		ancestors = back_propagation(term_id, {})
		__ancestors[term_id] = ancestors

	# Calculation of the information content. For each term, an information
	# content score is calculated using there declared usage.
	__ic = {}

	# list all terms in the ontology
	terms = {}
	for term_id, ancestors in __ancestors.iteritems():
		terms[term_id] = True
		for ancestor in ancestors:
			terms[ancestor] = True

	terms = terms.keys()

	# (1) find the root term
	root = []
	for term_id in terms:
		if (not term_id in direct_parents):
			root.append(term_id)

	if (len(root) > 1):
		raise errors.InvalidOntology("The ontology have more than one root: %s" % ', '.join(["'%s'" % term_id for term_id in root]))

	if (len(root) == 0):
		raise errors.InvalidOntology("The ontology contains no root")

	root = root[0]

	# we don't compute an IC for unused terms, as this will result
	# in a break of the monotony (IC must be superior to zero)
	terms = filter(lambda x : (x in usage_count) and (usage_count[x] > 0) and (x != root), terms)

	# (2) propagation of the usage counts to terms' ancestors
	usage_count_ = {}
	for term_id in terms:
		cnt = usage_count[term_id]

		for ancestor in __ancestors[term_id]:
			if (not ancestor in usage_count_):
				if (ancestor in usage_count):
					usage_count_[ancestor] = usage_count[ancestor]
				else:
					usage_count_[ancestor] = 0

			if (ancestor != term_id):
				usage_count_[ancestor] += cnt

	# (3) convert usage count to probability
	maximum_usage = usage_count_[root] + 0.0

	for term_id in terms:
		for term_id in __ancestors[term_id]:
			if (term_id in __ic):
				continue

			__ic[term_id] = usage_count_[term_id] / maximum_usage

			# the IC should be > 0 as long as the term is used at least one time
			assert (not term_id in usage_count) or ((__ic[term_id] > 0) and (__ic[term_id] <= 1)), "Information content not in ]0;1] for term %s (value is %s)" % (term_id, __ic[term_id])

	return __ancestors, __ic

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

# Calculate a semantic distance between terms of an ontology, according to the
# pre-calculated information content and the known ancestors of the terms.
class semantic_distance:

	# ancestors - a dictionary with all terms of the ontology as the keys,
	#   and a list of all their ancestors as the values
	# ic - a dictionary with each term of the ontology as the keys, and their
	#   information content as the values. Terms having no information content
	#   (i.e. not used in the ontology and having no children being used) MUST
	#   be excluded from this dictionary (i.e. no i.c. of 0 is allowed)
	def __init__ (self, ancestors, ic):
		self.__ancestors = ancestors
		self.__ic = ic

		# we ensure each term have a valid information content
		for (term_id, ic) in self.__ic.iteritems():
			if (ic <= 0):
				raise ValueError("Invalid information content for term '%s': %s" % (term_id, ic))

		# we ensure each term is declared as its own ancestor
		for term_id in self.__ancestors:
			if (not term_id in self.__ancestors[term_id]):
				self.__ancestors[term_id][term_id] = True

	# Calculate a semantic distance between two terms of an ontology.
	# A, B - the two terms to compare. These terms must belong to the same
	#   ontology, i.e. must share at least one parent
	# matrix - optional pre-calculated distance matrix, as a dictionary of
	#   dictionaries. Must contains a distance for the two input terms (i.e.
	#   matrix[A][B] must exists)
	def distance_between (self, term_a, term_b, matrix = None):
		if (term_a == term_b):
			return 0.0

		if (matrix != None):
			if (not term_a in matrix):
				raise ValueError("The input matrix does not contain information for term '%s'" % term_a)

			if (not term_b in matrix[term_a]):
				raise ValueError("The input matrix does not contain distance between terms '%s' and '%s'" % (term_a, term_b))

			return matrix[term_a][term_b]

		# get information contents
		try:
			pA = self.__ic[term_a]
			pB = self.__ic[term_b]

		except KeyError as e:
			raise errors.NoInformationContent(e.message)

		# get common ancestors
		try:
			ancestors_of_a = self.__ancestors[term_a]
			ancestors_of_b = self.__ancestors[term_b]

		except KeyError as e:
			raise errors.NoAncestors(e.message)

		common_ancestors = []
		for parent in ancestors_of_a:
			if (parent in ancestors_of_b):
				common_ancestors.append(parent)

		if (len(common_ancestors) == 0):
			raise errors.NoCommonAncestors(term_a, term_b)

		# calculate the probability of the minimum subsumer
		try:
			p_ms = min([self.__ic[term] for term in common_ancestors])

		except KeyError as e:
			raise errors.NoInformationContent(e.message)

		assert (p_ms >= pA) and (p_ms >= pB), "Invalid monotony: p(%s) = %s, p(%s) = %s, Pms (%s) = %s" % (term_a, pA, term_b, pB, ','.join(common_ancestors), p_ms)

		# calculate the semantic distance (]0;1]), according to Lin et al.
		return 1 - 2.0 * math.log(p_ms) / (math.log(pA) + math.log(pB))

	# Calculate a semantic distance between two set of terms.
	# A, B - the two sets to compare
	# force - if True, any invalid pairwise comparison is ignored
	# matrix - optional pre-calculated distance matrix, as a dictionary of
	#   dictionaries
	def distance_between_sets (self, terms_a, terms_b, force = False, matrix = None):
		if (len(terms_a) == 0):
			raise ValueError("The first set must contains at least one term")

		if (len(terms_b) == 0):
			raise ValueError("The second set must contains at least one term")

		terms_a = dict.fromkeys(terms_a)
		terms_b = dict.fromkeys(terms_b)

		pairwise_distances = {}

		def add_distance (t, d):
			if (not t in pairwise_distances):
				pairwise_distances[t] = []

			pairwise_distances[t].append(d)

		# calculate pairwise distances
		for term_a in terms_a:
			for term_b in terms_b:
				if (force):
					try:
						d = self.distance_between(term_a, term_b, matrix)
					except Exception:
						continue
				else:
					d = self.distance_between(term_a, term_b, matrix)

				add_distance((term_a, 0), d)
				add_distance((term_b, 1), d)

		# for each term of one set, get the smallest
		# distance with the terms of the second set
		bpd = []
		for distances in pairwise_distances.values():
			distances.sort()
			bpd.append(distances[0])

		# ... and take the average
		n = len(bpd)
		if (n == 0):
			return None

		return sum(bpd) / n

	# Return the most informative common ancestor of a set of terms
	# (these terms included), or None if no common ancestor can be find
	def best_common_ancestor (self, terms):
		terms = dict.fromkeys(terms)
		terms = filter(lambda x: (x in self.__ancestors), terms)
		if (len(terms) == 0):
			raise ValueError("More than one term must be provided")

		# take the common ancestors
		previous = {}
		for ancestor_id in self.__ancestors[terms[0]]:
			previous[ancestor_id] = True

		for term_id in terms[1:]:
			current = {}
			for ancestor_id in self.__ancestors[term_id]:
				if (ancestor_id in previous):
					current[ancestor_id] = True

			previous = current

		ancestors = previous.keys()

		# get the one with the lowest I.C.
		best = (2, None)
		for ancestor_id in ancestors:
			if (not ancestor_id in self.__ic):
				continue

			ic = self.__ic[ancestor_id]
			if (ic < best[0]):
				best = (ic, ancestor_id)

		return best[1]

	# Calculate the diameter of a cluster of terms.
	# These terms must have an information content, and belong to the same
	# ontology. If 'force' is set to True, any invalid pairwise comparison
	# will be ignored.
	def dispersion (self, terms, force = False, matrix = None):
		terms = dict.fromkeys(terms).keys()
		if (len(terms) < 2):
			raise ValueError("More than one term must be provided")

		distances = []
		for i, term_a in enumerate(terms):
			for term_b in terms[i+1:]:
				if (force):
					try:
						d = self.distance_between(term_a, term_b, matrix)
					except:
						pass
				else:
					d = self.distance_between(term_a, term_b, matrix)

				distances.append(d)

		n = len(distances)
		if (n == 0):
			return None

		return sum(distances) / n

	# Filter a list of terms to keep only those having an information content.
	def exclude_null_ic (self, terms):
		return filter(lambda x: (x in self.__ic), terms)

	# Filter a list of terms so that no term is an ancestor of any other one.
	def exclude_ancestors (self, terms):
		exclude = {}
		for term in terms:
			for ancestor in self.__ancestors.get(term, []):
				if (ancestor != term) and (not ancestor in exclude) and (ancestor in terms):
					exclude[ancestor] = True

		return filter(lambda x: x not in exclude, terms)
