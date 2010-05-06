#!/usr/bin/env python

# WhatTheEC: semantic distance between Enzyme Content (EC) terms
# Part of the SemanticDistance library, http://oenone.net/tools/

# Destination of the data: %PATH%/ec/, where %PATH% is the
# directory where SemanticDistance is installed

__DEBUG = True

import optparse, sys, os, re

p = optparse.OptionParser()

p.add_option("-d", "--ec-directory", dest = "ec_directory", default = '.',
  help = "Directory containing the enzyme.dat and enzclass.txt files.")

(p, a) = p.parse_args()

def error (msg):
	print >>sys.stderr, " Error: %s" % msg
	print >>sys.stderr, " (use option '--help' for help)"
	sys.exit(1)

if (not os.path.exists(p.ec_directory)):
	error("unknown directory '%s'." % p.ec_directory)

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

			return line

#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

import cPickle as pickle

print " Step 1 - Loading EC ontology"

# reading mapping between GO term and internal ID
print "   getting terms list ...",
sys.stdout.flush()

TERMS = {}
TERM2ANNOTATION = {}
PARENTS = {}

ENTRY = re.compile("([0-9])\.\s?([0-9\-]+)\.\s?([0-9\-]+)\.\s?([0-9\-]+)\s+(.*?)\.\n", re.S)

previous = [''] * 3
file = os.path.join(p.ec_directory, "enzclass.txt")
data = open(file, 'r').read()

def remove_duplicates (text, character):
	key = character * 2

	while True:
		p = text.find(key)
		if (p == -1):
			return text

		text = text.replace(key, character)

def build_name (*items):
	items = [TERM2ANNOTATION[item] for item in items[:-1]] + [items[-1]]
	name = items[0]

	for item in items[1:]:
		if (item.startswith(items[0])):
			item = item.replace(items[0] + ' ', '')
		else:
			item = item[0].lower() + item[1:]
		name += ' ' + item

	return name

for g in ENTRY.findall(data):

	ec = '.'.join(g[:4])
	name = remove_duplicates(filter(lambda x: (x != '\n'), g[4]), ' ')
	level = len(filter(lambda x: (x != '-'), g[:4]))

	previous[level - 1] = ec

	# we add a root node for the whole ontology
	if (level == 1):
		PARENTS[ec] = ["-.-.-.-"]

	# we connect each node to its (here unique) parent
	if (level == 2):
		PARENTS[ec] = [previous[0]]
		name = build_name(previous[0], name)

	if (level == 3):
		PARENTS[ec] = [previous[1]]
		name = build_name(previous[0], previous[1], name)

#	print ec, name, previous

	TERMS[ec] = True
	TERM2ANNOTATION[ec] = name

print "%s terms loaded" % len(TERMS)

# reading associations and counting terms usage
print "   counting associations ...",
sys.stdout.flush()

USAGE = {}
usage = -1

for line in Reader(os.path.join(p.ec_directory, "enzyme.dat")):

	# EC code
	if (line[:2] == "ID"):
		ec = line[5:]
		usage = 0

	# associations
	elif (line[:2] == "DR"):
		usage += line.count(';')

	# end of the entry
	elif (line[:2] == "//") and (usage > 0):

		ec_ = ec.split('.')
		parent = None

		for level in range(1, 3):
			pparent = '.'.join(ec_[:-level]) + ".-" * level

			if (not PARENTS.has_key(pparent)):
				continue
			else:
				parent = pparent
				break

		if (parent == None):
			print " Error: unable to find the parent of term '%s'." % ec
			sys.exit(1)

		PARENTS[ec] = [parent]
		USAGE[ec] = usage

print "%s terms used at least once" % len(USAGE)

#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

print " Step 2 - Calculating terms information content"

from SemanticDistance import SemanticDistanceConstructor

# we use the same constructor for the three aspects of Gene Ontology
sdc = SemanticDistanceConstructor(USAGE, PARENTS)

print "   get ancestors ...",
sys.stdout.flush()

sdc.find_ancestors()
print "done"

print "   calculate IC ...",
sys.stdout.flush()

IC = sdc.calculate_ic()
IC = IC.values()

print "done (min/max: %s / %s)" % (min(IC), max(IC))

#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

from SemanticDistance import PATH

print "\n writing data ...",
sys.stdout.flush()

sdc.save(os.path.join(PATH, "ec", "ec.data"))

pickle.dump(TERM2ANNOTATION, open(os.path.join(PATH, "ec", "ec.terms"), 'wb'), -1)

print "all done."
