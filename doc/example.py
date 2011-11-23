#!/usr/bin/env python

import SemanticDistance

"""
Example of ontology:

	 ,--> B (5) -->.    ,--> D (5)
	/               \  /
  A (3)             C (2)
	\               /  \
	 `--> E (2) -->'    `--> F (2)

The number on each node is the usage count (i.e., the number
of time this specific node was used to annotate an object)
"""

# Step 1: we declare the direct parents of all nodes (except the root node, A)
direct_parents = {'B': ['A'], 'C': ['B', 'E'], 'D': ['C'], 'E': ['A'], 'F': ['C']}

# Step 2: we declare the usage count of all nodes
usage_count = {'A': 3, 'B': 5, 'C': 2, 'D': 5, 'E': 2, 'F': 2}

# Step 3: we infer the ancestors and information content of all nodes
ancestors, ic = SemanticDistance.process(direct_parents, usage_count)

# At this stage the two variables 'ancestors' and 'ic' contains all what is
# needed to calculate a distance between terms in the ontology. These
# variables may be serialized for further use.

# Step 4: we create a 'semantic_distance' class with these information
sd = SemanticDistance.semantic_distance(ancestors, ic)

# From now we can calculate the distance between any two terms:
print sd.distance_between('B', 'B') # return 0.0 (the lowest distance)
print sd.distance_between('B', 'C') # return 0.419755281904
print sd.distance_between('D', 'C') # return 0.282289068435
print sd.distance_between('B', 'E') # return 1.0 (the highest distance)

# Let's imagine we have an object annotated with 'B', 'C' and 'D'.
# We can ...

# ... get the ancestor of these three terms that have the
# best information content (i.e. the most informative one)
print sd.best_common_ancestor(['B', 'C', 'D']) # return 'B'
print sd.best_common_ancestor(['C', 'D', 'F']) # return 'C'

# ... obtain the dispersion of the annotation (average distance
# between the terms)
print sd.dispersion(['B', 'C', 'D']) # return 0.443238197585

# Now let's imagine you have two objects, one annotated with 'B',
# the other with 'C' and 'D'. To know the distance between them,
print sd.distance_between_sets(['B'], ['C', 'D']) # return 0.489060268741
