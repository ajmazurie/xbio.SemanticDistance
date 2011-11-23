
class InvalidOntology:
	def __init__ (self, msg):
		self.msg = msg

	def __str__ (self):
		return self.msg

class NoInformationContent (Exception):
	def __init__ (self, *terms):
		self.offending_terms = terms

	def __str__ (self):
		return "No information content for term%s %s" % (
			{ True: 's', False: ''}[len(self.offending_terms) > 1],
			', '.join(["'%s'" % term_id for term_id in self.offending_terms])
		)

class NoAncestors (Exception):
	def __init__ (self, *terms):
		self.offending_terms = terms

	def __str__ (self):
		return "No ancestor for term%s %s" % (
			{ True: 's', False: ''}[len(self.offending_terms) > 1],
			', '.join(["'%s'" % term_id for term_id in self.offending_terms])
		)

class NoCommonAncestors (Exception):
	def __init__ (self, term_a, term_b):
		self.first_term = term_a
		self.second_term = term_b

	def __str__ (self):
		return "Terms '%s' and '%s' have no common ancestor" % (self.first_term, self.second_term)
