
#### CONFIGURATION FILE FOR STEP 5

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# STEP 5 PARAMETERS (DO NOT MODIFY !)                                          #

# FILE (kernel)
	# Perl file providing the kernel used to compute similarity between
    # two GO terms (one of step5.LIN.pl or step5.RESNIK.pl)

# END PARAMETERS                                                               #
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

## USER VALUES (VALUES FOR EACH PARAMETERS)

######################## Kernel
#do "step5.LIN.pl";
do "step5.JIANG.pl";

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
