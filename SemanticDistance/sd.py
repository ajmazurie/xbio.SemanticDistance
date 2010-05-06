
import sys, os, math

class SemanticDistance:
	"""
	Calculate a semantic distance between terms of an ontology, according to
	the pre-calculated information content and the known ancestors of the
	terms.
	"""

	# ancestors - a dictionary with all terms of the ontology as the keys,
	#   and a list of all their ancestors as the values
	# ic - a dictionary with each term of the ontology as the keys, and their
	#   information content as the values. Terms having no information content
	#   (i.e. not used in the ontology and having no children being used) MUST
	#   be excluded from this dictionary (i.e. no i.c. of 0 is allowed)
	def __init__ (self, ancestors = {}, ic = {}):

		self.ANCESTORS = ancestors
		self.INFORMATION_CONTENT = ic

		# we ensure each term have a valid information content
		for term, ic in self.INFORMATION_CONTENT.iteritems():
			assert (ic > 0), "the term '%s' have an invalid information content (%s)" % (term, ic)

		# we ensure each term is declared as its own ancestor
		for term in self.ANCESTORS:
			if (not term in self.ANCESTORS[term]):
				self.ANCESTORS[term][term] = True

	# Return the ancestors of a given term, or None if the term is not found.
	# The list of ancestors contains the input term.
	def get_ancestors (self, term):
		if (term in self.ANCESTORS):
			return self.ANCESTORS[term].keys()
		else:
			return None

	# Return the information content of a given term, or None if the term is
	# not found.
	def get_ic (self, term):
		return self.INFORMATION_CONTENT.get(term)

	# Error code: No result because of a lack of information content (for at
	# least one term provided as input)
	NO_INFORMATION_CONTENT = -1

	# Error code: No result because terms are not part of the same ontology
	# (at least two terms share no parent)
	NO_SHARED_PARENT = -2

	# Error code: No result because no data is available (possible reasons:
	# the custom distance matrix provided don't have the requested distance;
	# the 'force' flag was set to True but no distance have been successfully
	# calculated)
	NO_DATA = -3

	# Calculate a semantic distance between two terms of an ontology.
	# A, B - the two terms to compare. These terms must belong to the same
	#   ontology, i.e. must share at least one parent (NO_SHARED_PARENT is
	#   returned if invalid)
	# verbose - if True (default), print warning messages on the standard error
	# check_ic - if True (default), check the two input terms for their
	#   information content (NO_INFORMATION_CONTENT is returned if invalid)
	# matrix - optional pre-calculated distance matrix, as a dictionary of
	#   dictionaries. Must contains a distance for the two input terms (i.e.
	#   matrix[A][B] must exists)
	def distance_between (self, A, B, verbose = True, check_ic = True, matrix = None):

		if (matrix != None):
			if (A == B):
				return 0.0

			if (not A in matrix):
				return self.NO_DATA

			if (not B in matrix[A]):
				return self.NO_DATA

			return matrix[A][B]

		if (check_ic):
			for term in (A, B):
				if (not term in self.INFORMATION_CONTENT):
					if (verbose):
						print >>sys.stderr, "distance_between(): no information content for term '%s'" % A

					return self.NO_INFORMATION_CONTENT

		if (A == B):
			return 0.0

		# get information contents
		pA, pB = self.INFORMATION_CONTENT[A], self.INFORMATION_CONTENT[B]

		# get shared parents
		shared_parents = []

		for parent in self.ANCESTORS[A]:
			if (parent in self.ANCESTORS[B]):
				shared_parents.append(parent)

		if (len(shared_parents) == 0):
			if (verbose):
				print >>sys.stderr, "distance_between(): terms '%s' and '%s' share no parents" % (A, B)

			return self.NO_SHARED_PARENT

		# calculate the probability of the minimum subsumer
		p_ms = min([self.INFORMATION_CONTENT[term] for term in shared_parents])

		assert (p_ms >= pA) and (p_ms >= pB), "invalid monotony: p(%s) = %s, p(%s) = %s, Pms (%s) = %s" % (A, pA, B, pB, ','.join(shared_parents), p_ms)

		# calculate the semantic distance (]0;1]), according to Lin et al.
		return 1 - 2.0 * math.log(p_ms) / (math.log(pA) + math.log(pB))

	# Calculate a semantic distance between two set of terms.
	# A, B - the two sets to compare
	# force - if True, any invalid pairwise comparison is ignored
	# verbose - if True (default), print warning messages on the standard error
	# check_ic - if True (default), check the two input terms for their
	#   information content (NO_INFORMATION_CONTENT is returned if invalid)
	# matrix - optional pre-calculated distance matrix, as a dictionary of
	#   dictionaries
	def distance_between_sets (self, A, B, force = False, verbose = True, check_ic = True, matrix = None):

		# eliminate any potential redundancy
		A, B = unique(A), unique(B)

		# calculate pairwise distances
		pd = {}
		def add_distance (t, d):
			if (not t in pd):
				pd[t] = []

			pd[t].append(d)

		for termA in A:
			for termB in B:
				d = self.distance_between(termA, termB, verbose, check_ic, matrix)

				if (d < 0): # an error occured
					if (verbose):
						print >>sys.stderr, "distance_between_sets(): unable to calculate a distance between '%s' and '%s' (error code %s)" % (termA, termB, d)

					if (not force):
						return d
				else:
					add_distance((termA, 0), d)
					add_distance((termB, 1), d)

		# for each term of one set, get the smallest
		# distance with the terms of the second set
		bpd = []
		for distances in pd.values():
			distances.sort()
			bpd.append(distances[0])

		# ... and take the average
		n = len(bpd)

		if (n == 0):
			return self.NO_DATA
		else:
			return sum(bpd) / n

	# Return the most informative common ancestor of a set of terms
	# (these terms included), or None if no common ancestor can be find
	def best_common_ancestor (self, terms, verbose = True):

		terms = filter(lambda x: (x in self.ANCESTORS), unique(terms))
		if (len(terms) == 0):
			if verbose:
				print >>sys.stderr, "best_common_ancestor(): no ancestor found for the set %s" % ", ".join(terms)

			return None

		# take the common ancestors
		previous = {}
		for ancestor in self.ANCESTORS[terms[0]]:
			previous[ancestor] = True

		for term in terms[1:]:
			current = {}
			for ancestor in self.ANCESTORS[term]:
				if (ancestor in previous):
					current[ancestor] = True

			previous = current

		ancestors = previous.keys()

		# get the one with the lowest I.C.
		best = (2, None)
		for ancestor in ancestors:
			if (not ancestor in self.INFORMATION_CONTENT):
				continue

			ic = self.INFORMATION_CONTENT[ancestor]
			if (ic < best[0]):
				best = (ic, ancestor)

		return best[1]

	IS_SINGLETON = -4

	# Calculate the diameter of a cluster of terms.
	# These terms must have an information content, and belong to the same
	# ontology. If 'force' is set to True, any invalid pairwise comparison
	# will be ignored. An IS_SINGLETON error code is returned if the list
	# of terms contains only one element, or if no valid distance between
	# the terms can be obtained
	def dispersion (self, terms, force = False, verbose = True, check_ic = True, matrix = None):
		terms = unique(terms)

		if (len(terms) == 1):
			return self.IS_SINGLETON

		distances = []
		for i, A in enumerate(terms):
			for B in terms[i+1:]:
				d = self.distance_between(A, B, verbose, check_ic, matrix)

				if (d < 0): # an error occured
					if (not force):
						return d
				else:
					distances.append(d)

		n = len(distances)

		if (n == 0):
			return self.IS_SINGLETON
		else:
			return sum(distances) / n

	# Filter a list of terms to keep only those having an information content.
	def exclude_null_ic (self, terms):
		return filter(lambda x: (x in self.INFORMATION_CONTENT), terms)

	# Filter a list of terms so that no term is an ancestor of any other one.
	def exclude_ancestors (self, terms):
		exclude = {}
		for term in terms:
			for ancestor in self.ANCESTORS.get(term, []):
				if (ancestor != term) and (not ancestor in exclude) and (ancestor in terms):
					exclude[ancestor] = True

		return filter(lambda x: x not in exclude, terms)

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

import cPickle as pickle

# Instantiate a new class from a dumped datafile
# created by SemanticDistanceConstructor.save()
def SemanticDistanceLoader (file):
	ancestors, ic = pickle.load(open(file, 'rb'))

	return SemanticDistance(ancestors, ic)

def unique (items):
	map = {}
	for item in items:
		map[item] = True

	return map.keys()

def order (a, b):
	if (a <= b):
		return (a, b)
	else:
		return (b, a)
