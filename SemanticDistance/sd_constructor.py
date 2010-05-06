
import sys, cPickle as pickle

class SemanticDistanceConstructor:
	"""
	Pre-calculate information needed to calculate a distance between terms in
	an ontology. The outputs, i.e. the information content of each term and
	the list of there ancestors in the ontology, are used by SemanticDistance.
	"""

	# usage - a dictionary with all terms of the ontology as the keys, and
	#   the number of time these terms are used as values. Unused terms can
	#   be excluded from this dictionary
	# parents -	a dictionary with all terms of the ontology as the keys, and
	#   the list of the direct parents as the values. Unused terms (i.e. terms
	#   with a usage of 0) MUST be included; the only term not to be included
	#   in this dictionary being the root term (which have no parent)
	def __init__ (self, usage, parents):

		self.USAGE = usage
		self.PARENTS = parents

		# we ensure all terms have a non-negative usage count
		for term, usage in self.USAGE.iteritems():
			assert (usage >= 0), "the term '%s' have an invalid usage count (%s)" % (term, usage)

		# we ensure all terms have at least one parent
		for term, parents in self.PARENTS.iteritems():
			assert (not term in parents), "the term '%s' is declared as its own parent" % term
			assert (len(parents) > 0), "the term '%s' have been declared with no parent" % term

		self.ANCESTORS = {}
		self.INFORMATION_CONTENT = {}

	# Identification of the term ancestors. For each given term, a list of all
	# the parents (down to the root term) are identified. If no term is
	# provided, the search is performed for all terms declared in 'parents'.
	# Must be called before calculate_ic()
	def find_ancestors (self, terms = None):

		if (terms == None):
			terms = self.PARENTS.keys()

		def back_propagation (term, ancestors):

			# the branching node is registered as its own parent
			ancestors[term] = True

			# the root node has been reached
			if (not term in self.PARENTS):
				return ancestors

			# starting a new path from each parent
			for parent in self.PARENTS[term]:
				ancestors = back_propagation(parent, ancestors)

				"""
				# reading from cache
				if (parent in self.ANCESTORS):
					for p in self.ANCESTORS[parent]:
						ancestors[p] = True

				# back-propagating
				else:
					ancestors = back_propagation(parent, ancestors)
				"""

			return ancestors

		for term in terms:
			ancestors = back_propagation(term, {})
			self.ANCESTORS[term] = ancestors

		return self.ANCESTORS

	# Calculation of the information content. For each term, an information
	# content score is calculated using there declared usage. If no term is
	# given, the information content is calculated for all the terms declared
	# in 'parents' (plus their ancestors)
	def calculate_ic (self, terms = None):
		assert (self.ANCESTORS != {}), "calculate_ic() must be called AFTER find_ancestors()"

		if (terms == None):
			terms = {}
			for term, ancestors in self.ANCESTORS.iteritems():
				terms[term] = True
				for ancestor in ancestors:
					terms[ancestor] = True

			terms = terms.keys()

		# (1) find the root term
		root = None
		for term in terms:
			if (not term in self.PARENTS):
				assert (root == None), "the ontology contains more than one root"
				root = term

		assert (root != None), "the ontology contains no root"

		# we don't compute an IC for unused terms, as this will result
		# in a break of the monotony (IC must be superior to zero)
		terms = filter(lambda x : (x in self.USAGE) and (self.USAGE[x] > 0) and (x != root), terms)

		# (2) propagation of the usage counts to terms' ancestors
		usage = {}
		for term in terms:
			u = self.USAGE[term]

			for ancestor in self.ANCESTORS[term]:
				if (not ancestor in usage):
					if (ancestor in self.USAGE):
						usage[ancestor] = self.USAGE[ancestor]
					else:
						usage[ancestor] = 0

				if (ancestor != term):
					usage[ancestor] += u

		# (3) convert usage count to probability
		maximum_usage = usage[root] + 0.0

#		print "root usage (%s): %s" % (root, maximum_usage)

		for term in terms:
			for term in self.ANCESTORS[term]:
				if (term in self.INFORMATION_CONTENT):
					continue

				self.INFORMATION_CONTENT[term] = usage[term] / maximum_usage
#				print "term, usage, IC:", term, usage[term], self.INFORMATION_CONTENT[term]

				# the IC should be > 0 as long as the term is used at least one time
				assert (not term in self.USAGE) or ((self.INFORMATION_CONTENT[term] > 0) and (self.INFORMATION_CONTENT[term] <= 1)), "information content not in ]0;1] for term %s (value is %s)" % (term, self.INFORMATION_CONTENT[term])

		return self.INFORMATION_CONTENT

	# Save the ancestors and information contents into a binary file. This file
	# can be loaded by SemanticDistanceLoader for further use.
	def save (self, file):
		pickle.dump((self.ANCESTORS, self.INFORMATION_CONTENT), open(file, 'wb'), -1)
