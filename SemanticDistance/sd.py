
import sys, os, math
import cPickle as pickle

# Pre-calculate information needed to calculate a distance between terms in
# an ontology. The outputs, i.e. the information content of each term and
# the list of there ancestors in the ontology, are used by SemanticDistance.
class InformationContent:

	# usage - a dictionary with all terms of the ontology as the keys, and
	#   the number of time these terms are used as values. Unused terms can
	#   be excluded from this dictionary
	# parents - a dictionary with all terms of the ontology as the keys, and
	#   the list of the direct parents as the values. Unused terms (i.e. terms
	#   with a usage of 0) MUST be included; the only term not to be included
	#   in this dictionary being the root term (which have no parent)
	def __init__ (self, usage, parents):

		# we ensure all terms have a non-negative usage count
		for (term_id, cnt) in usage.iteritems():
			assert (cnt >= 0), "Invalid usage count for term '%s': %s" % (term_id, cnt)

		# we ensure all terms have at least one parent
		for (term_id, parents_) in parents.iteritems():
			assert (not term_id in parents_), "Term '%s' is declared as its own parent" % term_id
			assert (len(parents_) > 0), "Term '%s' has no declared parent" % term_id

		# Identification of the term ancestors. For each given term, a
		# list of all the parents (down to the root term) are identified.
		self.__Ancestors = {}

		def back_propagation (term_id, ancestors):
			# the branching node is registered as its own parent
			ancestors[term_id] = True

			# the root node has been reached
			if (not term_id in parents):
				return ancestors

			# starting a new path from each parent
			for parent_id in parents[term_id]:
				ancestors = back_propagation(parent_id, ancestors)

			return ancestors

		for term_id in parents:
			ancestors = back_propagation(term_id, {})
			self.__Ancestors[term_id] = ancestors

		# Calculation of the information content. For each term, an information
		# content score is calculated using there declared usage.
		self.__InformationContent = {}

		# list all terms in the ontology
		terms = {}
		for term_id, ancestors in self.__Ancestors.iteritems():
			terms[term_id] = True
			for ancestor in ancestors:
				terms[ancestor] = True

		terms = terms.keys()

		# (1) find the root term
		root = None
		for term_id in terms:
			if (not term_id in parents):
				assert (root == None), "The ontology contains more than one root ('%s' and '%s')" % (root, term_id)
				root = term_id

		assert (root != None), "The ontology contains no root"

		# we don't compute an IC for unused terms, as this will result
		# in a break of the monotony (IC must be superior to zero)
		terms = filter(lambda x : (x in usage) and (usage[x] > 0) and (x != root), terms)

		# (2) propagation of the usage counts to terms' ancestors
		usage_ = {}
		for term_id in terms:
			cnt = usage[term_id]

			for ancestor in self.__Ancestors[term_id]:
				if (not ancestor in usage_):
					if (ancestor in usage):
						usage_[ancestor] = usage[ancestor]
					else:
						usage_[ancestor] = 0

				if (ancestor != term_id):
					usage_[ancestor] += cnt

		# (3) convert usage count to probability
		maximum_usage = usage_[root] + 0.0

#		print "root usage (%s): %s" % (root, maximum_usage)

		for term_id in terms:
			for term_id in self.__Ancestors[term_id]:
				if (term_id in self.__InformationContent):
					continue

				self.__InformationContent[term_id] = usage_[term_id] / maximum_usage
#				print "term, usage, IC:", term, usage[term], self.__InformationContent[term]

				# the IC should be > 0 as long as the term is used at least one time
				assert (not term_id in usage) or ((self.__InformationContent[term_id] > 0) and (self.__InformationContent[term_id] <= 1)), "information content not in ]0;1] for term %s (value is %s)" % (term_id, self.__InformationContent[term_id])

	def get_ancestors (self):
		return self.__Ancestors

	def get_information_content (self):
		return self.__InformationContent

	# Save the ancestors and information contents into a binary file. This file
	# file can be loaded through SemanticDistance.from_file() for further use.
	def to_file (self, fn):
		pickle.dump((self.__Ancestors, self.__InformationContent), open(fn, 'wb'), -1)

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

class NoInformationContent (Exception):
	def __init__ (self, *terms):
		self.offending_terms = terms

	def __str__ (self):
		return "No information content for terms %s" % ', '.join(["'%s'" % term_id for term_id in self.offending_terms])

class NoAncestor (Exception):
	def __init__ (self, *terms):
		self.offending_terms = terms

	def __str__ (self):
		return "No ancestor for terms %s" % ', '.join(["'%s'" % term_id for term_id in self.offending_terms])

class NoCommonAncestor (Exception):
	def __init__ (self, term_a, term_b):
		self.first_term = term_a
		self.second_term = term_b

	def __str__ (self):
		return "Terms '%s' and '%s' have no common ancestor" % (self.first_term, self.second_term)

# Calculate a semantic distance between terms of an ontology, according to the
# pre-calculated information content and the known ancestors of the terms.
class SemanticDistance:

	# ancestors - a dictionary with all terms of the ontology as the keys,
	#   and a list of all their ancestors as the values
	# ic - a dictionary with each term of the ontology as the keys, and their
	#   information content as the values. Terms having no information content
	#   (i.e. not used in the ontology and having no children being used) MUST
	#   be excluded from this dictionary (i.e. no i.c. of 0 is allowed)
	def __init__ (self, ancestors, ic):
		self.__Ancestors = ancestors
		self.__InformationContent = ic

		# we ensure each term have a valid information content
		for term_id, ic in self.__InformationContent.iteritems():
			assert (ic > 0), "Invalid information content for term '%s': %s" % (term_id, ic)

		# we ensure each term is declared as its own ancestor
		for term_id in self.__Ancestors:
			if (not term_id in self.__Ancestors[term_id]):
				self.__Ancestors[term_id][term_id] = True

	@classmethod
	def from_file (cls, fn):
		ancestors, ic = pickle.load(open(fn, 'rb'))
		return cls(ancestors, ic)

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
			pA = self.__InformationContent[term_a]
			pB = self.__InformationContent[term_b]

		except KeyError, exception:
			raise NoInformationContent(exception.message)

		# get common ancestors
		try:
			ancestors_of_a = self.__Ancestors[term_a]
			ancestors_of_b = self.__Ancestors[term_b]

		except KeyError, exception:
			raise NoAncestor(exception.message)

		common_ancestors = []
		for parent in ancestors_of_a:
			if (parent in ancestors_of_b):
				common_ancestors.append(parent)

		if (len(common_ancestors) == 0):
			raise NoCommonAncestor(term_a, term_b)

		# calculate the probability of the minimum subsumer
		try:
			p_ms = min([self.__InformationContent[term] for term in common_ancestors])

		except KeyError, exception:
			raise NoInformationContent(exception.message)

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
			raise Exception("No pairwise distance could be calculated")

		return sum(bpd) / n

	# Return the most informative common ancestor of a set of terms
	# (these terms included), or None if no common ancestor can be find
	def best_common_ancestor (self, terms):
		terms = dict.fromkeys(terms)
		terms = filter(lambda x: (x in self.__Ancestors), terms)
		if (len(terms) == 0):
			raise ValueError("More than one term must be provided")

		# take the common ancestors
		previous = {}
		for ancestor_id in self.__Ancestors[terms[0]]:
			previous[ancestor_id] = True

		for term_id in terms[1:]:
			current = {}
			for ancestor_id in self.__Ancestors[term_id]:
				if (ancestor_id in previous):
					current[ancestor_id] = True

			previous = current

		ancestors = previous.keys()

		# get the one with the lowest I.C.
		best = (2, None)
		for ancestor_id in ancestors:
			if (not ancestor_id in self.__InformationContent):
				continue

			ic = self.__InformationContent[ancestor_id]
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
			raise Exception("No pairwise distance could be calculated")

		return sum(distances) / n

	# Filter a list of terms to keep only those having an information content.
	def exclude_null_ic (self, terms):
		return filter(lambda x: (x in self.__InformationContent), terms)

	# Filter a list of terms so that no term is an ancestor of any other one.
	def exclude_ancestors (self, terms):
		exclude = {}
		for term in terms:
			for ancestor in self.__Ancestors.get(term, []):
				if (ancestor != term) and (not ancestor in exclude) and (ancestor in terms):
					exclude[ancestor] = True

		return filter(lambda x: x not in exclude, terms)
