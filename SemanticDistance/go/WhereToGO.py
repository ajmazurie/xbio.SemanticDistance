#!/usr/bin/env python

# WhereToGO: semantic distance between Gene Ontology (GO) terms
# Part of the SemanticDistance library, http://oenone.net/tools/

# Destination of the data: %PATH%/go/, where %PATH% is the
# directory where SemanticDistance is installed

__DEBUG = True

import optparse, sys, os

p = optparse.OptionParser()

p.add_option("-d", "--go-directory", dest = "go_directory", default = '.',
  help = "Directory containing the content of the go_YYYYMM-assocdb-tables.tar.gz file")

p.add_option("--without-iea", dest = "without_iea", action = "store_true", default = False,
  help = "Ignore GO annotations infered by electronic annotations (IEA evidence code)")

(p, a) = p.parse_args()

def error (msg):
	print >>sys.stderr, " Error: %s" % msg
	print >>sys.stderr, " (use option '--help' for help)"
	sys.exit(1)

if (not os.path.exists(p.go_directory)):
	error("unknown directory '%s'." % p.go_directory)

class Reader:

	def __init__ (self, file):
		self.source = open(file, 'r')

	def __iter__ (self):
		return self

	def next (self):

		while True:
			line = self.source.readline()

			if (line == ''):
				self.source.close()
				raise StopIteration

			line = line.strip()

			if (line == ''):
				continue

			return line.split('	')

file_suffix = { True: "with_iea", False: "without_iea" }

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

import cPickle as pickle

print "\n Step 1 - Load GO ontology"

# reading mapping between GO term and internal ID
print "   list GO terms ...",
sys.stdout.flush()

TERMS = {}
TERM2ANNOTATION = {}

id2go = {}
meta_terms = {}

obsolete_tags = {
  "obsolete_biological_process": "GO:0008371",
  "obsolete_molecular_function": "GO:0008369",
  "obsolete_cellular_component": "GO:0008370",
 }

for data in Reader(os.path.join(p.go_directory, "term.txt")):
	id, name, aspect, go = data[0], data[1], data[2], data[3]

	# we assimilate the 'obsolete' tags terms to corresponding GO terms
	if go.startswith("obsolete_"):
		go = obsolete_tags[go]

	# we avoid meta-terms describing types of relations and the global root
	elif (not go.startswith("GO")):
		meta_terms[id] = True
		continue
 
	id2go[id] = go

	if (not aspect in TERMS):
		TERMS[aspect] = []

	TERMS[aspect].append(go)
	TERM2ANNOTATION[go] = name

print "%s terms loaded (P: %s, F: %s, C: %s)" % (
  len(id2go),
  len(TERMS["biological_process"]),
  len(TERMS["molecular_function"]),
  len(TERMS["cellular_component"]),
 )  

# reading associations and counting terms usage
print "   count terms usage ...",
sys.stdout.flush()

#USAGE = pickle.load(open("WhereToGO.%s.dump" % file_suffix[p.without_iea], 'rb'))
#"""
USAGE = {}

# black-list
bad_evidences = {}

if (p.without_iea):
	bad_evidences["IEA"] = True

print bad_evidences

association_id2evidence = {}

for data in Reader(os.path.join(p.go_directory, "evidence.txt")):
	association_id, evidence_code = data[2], data[1]
	association_id2evidence[association_id] = evidence_code

for data in Reader(os.path.join(p.go_directory, "association.txt")):

	# skip annotations with unwanted evidences
	evidence_code = association_id2evidence[data[0]]
	if (evidence_code in bad_evidences):
		continue

	# skip negative annotations
	if (data[4] == "1"):
		continue

	go = id2go[data[1]]

	if (not go in USAGE):
		USAGE[go] = 0

	USAGE[go] += 1
#"""
pickle.dump(USAGE, open("WhereToGO.%s.dump" % file_suffix[p.without_iea], 'wb'), -1)

print "%s terms used at least once" % len(USAGE)

# reconstructing the tree
print "   list terms parents ...",
sys.stdout.flush()

link_type = { "2": "is_a", "3": "part_of" }

PARENTS = {}

for data in Reader(os.path.join(p.go_directory, "term2term.txt")):
	link = link_type[data[1]]
	parent, children = data[2], data[3]

	# we don't take into account relations to meta-terms
	if (parent in meta_terms) or (children in meta_terms):
		continue

	parent = id2go[parent]
	children = id2go[children]

	if (not children in PARENTS):
		PARENTS[children] = []

	PARENTS[children].append(parent)

PARENTS["GO:0008371"] = ["GO:0008150"] # parent(obsolete_biological_process) = biological_process
PARENTS["GO:0008369"] = ["GO:0003674"] # parent(obsolete_molecular_function) = molecular_function
PARENTS["GO:0008370"] = ["GO:0005575"] # parent(obsolete_cellular_component) = cellular_component

print "%s relations loaded" % sum([len(PARENTS[children]) for children in PARENTS])

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

print "\n Step 2 - Calculate information contents"

from SemanticDistance import SemanticDistanceConstructor

# we use the same constructor for the three aspects of Gene Ontology
sdc = SemanticDistanceConstructor(USAGE, PARENTS)

for aspect, terms in TERMS.iteritems():

	print "   aspect '%s'" % aspect

	# step 1
	print "     get ancestors ...",
	sys.stdout.flush()

	sdc.find_ancestors(terms)

	print "done (%s terms)" % len(terms)

	# step 2
	print "     calculate IC ...",
	sys.stdout.flush()

	IC = sdc.calculate_ic(terms)
	IC = IC.values()

	print "done (min/max: %s / %s)" % (min(IC), max(IC))

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

from SemanticDistance import PATH

print "\n write data ...",
sys.stdout.flush()

sdc.save(os.path.join(PATH, "go", "go.%s.data" % file_suffix[p.without_iea]))

# inverting the TERMS map and adding annotations
terms = {}
for aspect in TERMS:
	for go in TERMS[aspect]:
		terms[go] = (aspect, TERM2ANNOTATION[go])

pickle.dump(terms, open(os.path.join(PATH, "go", "go.terms"), 'wb'), -1)

print "all done."
