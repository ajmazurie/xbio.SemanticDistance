
import pickle, os, sys

PATH = os.path.dirname(__file__)

class GoHelper:

	def __init__ (self, file = os.path.join(PATH, "go.terms")):
		self.TERMS = pickle.load(open(file, 'rb'))
		self.ASPECTS = {}

		for (aspect, name) in self.TERMS.values():
			self.ASPECTS[aspect] = True

		self.ASPECTS = self.ASPECTS.keys()

	# Return a list of all the GO terms
	def get_terms (self):
		return self.TERMS.keys()

	# From a given list of GO terms, return a map with each aspect as a key
	# and the corresponding terms (if presents in the list) as values
	def classify (self, terms, verbose = True):
		aspects = {}

		for aspect in self.ASPECTS:
			aspects[aspect] = []

		for term in terms:
			if (not term in self.TERMS):
				if (verbose):
					print >>sys.stderr, "classify(): unknown term '%s'" % term

				continue

			(aspect, name) = self.TERMS[term]
			aspects[aspect].append(term)

		return aspects

	# Return the name of a GO term, or None if the term is not found
	def get_name (self, term):
		if (term in self.TERMS):
			return self.TERMS[term][1]
		else:
			return None

	def get_aspect (self, term):
		if (term in self.TERMS):
			return self.TERMS[term][0]
		else:
			return None		

class EcHelper:

	def __init__ (self, file = os.path.join(PATH, "ec.terms")):
		self.TERMS = pickle.load(open(file, 'rb'))

	# Return a list of all the EC terms
	def get_terms (self):
		return self.TERMS.keys()

	# Return the name of a EC term, or None if the term is not found
	def get_name (self, term):
		return self.TERMS.get(term)
