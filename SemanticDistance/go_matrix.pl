#!/usr/bin/perl -w

use Getopt::Long;
use Storable qw{nstore retrieve};

use warnings;

#______________________________________________________________________________'

$directory = ".";
my($step) = -1;
my($help);

GetOptions(
           "d|directory=s"	=> \$directory,
           "s|step=s"		=> \$step,
           "help|?"		=> \$help
          );

if ($help)
 {
  print STDOUT << "HELP_END";

  Options:
    directory 	- repository of go_YYYYMM-assocdb-tables
                 files (after decompressing)
    step       - wanted step (all steps if missing)

  Steps:
    1 - Creating tables of GO terms
    2 - Registering structure of GO trees
    3 - Association of genes and GO terms
    4 - Computing information content
    5 - Building gene/gene similarity matrix

HELP_END
  exit;
 }

# _____________________________________________________________________________'

if ($step == -1) # running all steps
 {
  print "Running all steps...\n";
  
  my($cnt) = 1;
  while (-e "step$cnt.pl")
   {
    print "STEP " . $cnt . "\n";
    do "step$cnt.pl";
    $cnt++;
   }
  
  print "All (found) steps done.\n";
  exit;
 }

my($stepFile) = "step" . $step . ".pl";

if (-e $stepFile)
 {
  print "STEP " . $step . ": Running...\n";
  do $stepFile;
  print "STEP " . $step . ": Done.\n";
 }
else
 { print "Unknown step number.\n"; }

exit;

sub test_file
 {
  my($filename) = @_;

  unless (-e $filename)
   {
    print "The file \"$filename\" don't exist.\n";
    exit;
   }

  unless(open(FILE, $filename))
   {
    print "Error: unable to open \"$filename\"\n";
    exit;
   } 	
 
  close FILE;
 }

# _____________________________________________________________________________'
