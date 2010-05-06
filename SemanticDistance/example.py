#!/usr/bin/env python

# First phase: marshalling information about the ontology

from SemanticDistance import SemanticDistanceConstructor

# Declaration of the new ontology.
# Let's say we have 6 terms organized like this (A is the root):
#
#     ,--> B (5) -->.    ,--> D (5)
#    /               \  /
#  A (3)             C (2)
#    \               /  \
#     `--> E (2) -->'    `--> F (2)
#
# (the number being the usage of each term)

# First we create a structure that contains the usage of each term.
# Terms that are not used can be excluded.
usage = {
  'A': 3,
  'B': 5,
  'C': 2,
  'D': 5,
  'E': 2,
  'F': 2
 }

# Then we create a structure declaring the direct parents of each term.
# The ONLY node that must not be present in this structure is the
# root node (which have no parents by definition).
parents = {
  'B': ['A'],
  'C': ['B', 'E'],
  'D': ['C'],
  'E': ['A'],
  'F': ['C']
 }

# Finally, we use SemanticDistanceConstructor to calculate the
# information content of each node ...
sdc = SemanticDistanceConstructor(usage, parents)

sdc.find_ancestors()
sdc.calculate_ic()

# ... then to save it
sdc.save("example.data")

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

# Second phase: use of this information to calculate semantic distances

from SemanticDistance import SemanticDistanceLoader

# First, loading the information generated for this ontology
sd = SemanticDistanceLoader("example.data")

# You can then calculate the distance between two terms by doing
print sd.distance_between('B', 'B') # return 0.0 (the lowest distance)
print sd.distance_between('B', 'C') # return 0.419755281904
print sd.distance_between('D', 'C') # return 0.282289068435
print sd.distance_between('B', 'E') # return 1.0 (the highest distance)

# Let's imagine we have a gene annotated with 'B', 'C' and 'D'.
# You can ...

# ... get the ancestor of these three terms that have the
# best information content (i.e. the most informative one)
print sd.best_common_ancestor(['B', 'C', 'D']) # return 'B'
print sd.best_common_ancestor(['C', 'D', 'F']) # return 'C'

# ... obtain the dispersion of the annotation (average distance
# between the terms)
print sd.dispersion(['B', 'C', 'D']) # return 0.443238197585

# Now let's imagine you have two genes, one annotated with 'B',
# the other with 'C' and 'D'. To know the distance between them,
print sd.distance_between_sets(['B'], ['C', 'D']) # return 0.489060268741

print sd.exclude_ancestors(['A', 'B', 'C', 'D', 'E', 'F']) # return ['D', 'F']
