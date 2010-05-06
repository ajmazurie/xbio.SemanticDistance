
#### CONFIGURATION FILE FOR STEP 3

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# STEP 3 PARAMETERS (DO NOT MODIFY !)                                          #

# STRING $association_file;
	# File containing associations between genes and GO terms
	# (format described at http://www.geneontology.org/GO.annotation.html)

# SUB $evidence_checker;
	# Subroutine taking an evidence code in entry (as provided by
	# the association file), and returning either 1 (if this code
	# is accepted) or 0 (if this code is refused)

# INTEGER $gene_column;
	# Index of the column, in the association file, containing the gene
	# name (that will be given to the gene_translator routine)

# SUB $gene_translator;
	# Subroutine taking a gene name (as provided by the association file)
	# and returning an user-defined gene name

# END PARAMETERS                                                               #
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

## USER VALUES (VALUES FOR EACH PARAMETERS)

print " CONFIGURATION FOR S.cerevisiae\n";
do "step3.config.S_CEREVISIAE.pl";
 # parameters for Saccharomyces cerevisiae (SGD + GeNetDB)

#print "   CONFIGURATION FOR E.COLI\n";
#do "step3.config.E_COLI.pl";
 # parameters for Escherichia coli (GenProtEC + EcoCyc)

## END USER VALUES

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
