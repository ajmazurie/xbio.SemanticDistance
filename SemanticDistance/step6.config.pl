
#### CONFIGURATION FILE FOR STEP 6

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# STEP 6 PARAMETERS (DO NOT MODIFY !)                                          #

# FILE (output)
	# Perl file managing similarity values and saving them (one of
	# step5.2TXT.pl -- for output in text file -- or step5.2SQL.pl
    # -- for output in MySQL database --)

# SUB $output_name
	# Subroutine taking a GO aspect and returning a file name to store
    # gene/gene similarity measures for this aspect (used by step5.2TXT.pl)

# SUB $table_name
	# Subroutine taking a GO aspect and returning a table name to store
    # gene/gene similarity measures for this aspect (used by step5.2SQL.pl)

# END PARAMETERS                                                               #
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

## USER VALUES (VALUES FOR EACH PARAMETERS)

######################## Output
do "step6.2TXT.pl";
#do "step6.2SQL.pl";

######################## Parameters

$output_name =
  sub
   {
    my($aspect) = @_;

    return "../yeast.FUNCTION." . uc($aspect) . ".s.matrix.txt"; ####
#  For Saccharomyces cerevisiae

#    return "../ecoli.FUNCTION." . uc($aspect) . ".s.matrix.txt"; ####
#  For Escherichia coli
   };

$table_name =
  sub
   {
    my($aspect) = @_;

#    return "yeast_FUNCTION_" . $aspect . "_s_matrix"; ####
#  For Saccharomyces cerevisiae

    return "ecoli_FUNCTION_" . $aspect . "_s_matrix"; ####
#  For Escherichia coli
   };

$db_host = "localhost";
$db_base = "work";
$db_user = "serial";
$db_pass = "";

## END USER VALUES

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
