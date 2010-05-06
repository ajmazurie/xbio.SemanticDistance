
sub OPEN
 {
 }

sub START_ASPECT
 {
  my($aspect) = @_;

  open(MATRIX, ">" . $output_name->($aspect));
 }

sub WRITE
 {
  my($geneA, $geneB, $value) = @_;

  print MATRIX $geneA . "\t" . $geneB . "\t" . $value . "\n";
#    if ($geneA ne $geneB)
#     { print MATRIX $geneB . "\t" . $geneA . "\t" . $value . "\n"; }
 }

sub END_ASPECT
 {
  close(MATRIX);
 }

sub CLOSE
 {
 }
