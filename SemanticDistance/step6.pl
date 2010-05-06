
print " > Building gene/gene similarity matrix\n";

test_file("step6.config.pl");
do "step6.config.pl";

my($skip) = 0; # value to skip

my(%term2term);

OPEN();

foreach my $aspect ("C", "P", "F")
 {
  print "   " . $aspect . " aspect\n";

	START_ASPECT($aspect);

	open(LOG, ">step6." . $aspect . ".log");

  my(%ANNOTATION) = %{retrieve("step3.ANNOTATION." . $aspect . ".dump")};
   # key: user defined gene name, value: array of GO terms

	print "   loading term/term matrix...\n";
	
  %term2term = %{retrieve("step5.TERM2TERM." . $aspect . ".dump")};

#	$term2term{"GO:0006412_GO:0006412"} = 0;
#	$term2term{"GO:0042255_GO:0042255"} = 0;
#	$term2term{"GO:0006412_GO:0042255"} = 0.939887008598567;
#	$term2term{"GO:0042255_GO:0006412"} = 0.939887008598567;
	
	print "   done.\n";

  my($nb) = (scalar keys %ANNOTATION);
  my($max) = $nb * ($nb - 1) / 2;
  my($cnt) = 0;

  print "   (" . $nb . " genes, " . $max . " comparisons)\n";

  my(@A) = sort(keys %ANNOTATION);
  my(@B) = @A;
  my(@termsA, @termsB);

  my($zero_cnt, $one_cnt) = (0,0);
	my($value);

  foreach my $geneA (@A)
   {
    @termsA = @{$ANNOTATION{$geneA}};

# if 'shift' is placed here, auto-comparisons are skipped
		shift(@B);

    foreach my $geneB (@B)
     {
      @termsB = @{$ANNOTATION{$geneB}};

      $value = compareGenes(\@termsA, \@termsB);
			$cnt++;

#      if ($value == $skip) { $zero_cnt++; next; }
      if ($value == 0) { $zero_cnt++; }
			if ($value == 1) { $one_cnt++; }

#print "$geneA $geneB : $value\n\n";
			
      WRITE($geneA, $geneB, $value);
#			goto FIN;
     }

# if 'shift' is placed here, auto-comparisons are NOT skipped

    print LOG "$aspect: comparison $cnt / $max (zeros:$zero_cnt, ones:$one_cnt)\n";

		$value = compareGenes(\@termsA, \@termsA);
    if ($value != 0)
		{ error("auto-comparison doesn't give the lowest distance ! ($value)"); }
	 }

  print "   $cnt comparisons done.\n";

	if ($cnt != $max)
   {
		error("incorrect number of comparisons. $cnt, should be $max");
	 }

FIN:
	
  END_ASPECT($aspect);
	close(LOG);
 }

CLOSE();

# Comparison of genes by taking the average score of term/term pairs of
# maximum score for each term of each gene
sub compareGenes
 {
	my($a, $b) = @_;
			
	my(@A) = @$a;
	my(@B) = @$b;
	
	if (((scalar @A) == 1) && ((scalar @B) == 1))
		{ return getValue($A[0], $B[0]); }

	my($value, $mean, $nb) = (0, 0, 0);
  my(@scoreA, @scoreB);
	my($keyA, $keyB);
	my(%scores) = ();

  foreach my $termA (@A) # array of GO terms for gene A
	{
		$keyA = "A".$termA;
		@scoreA = (defined $scores{$keyA}) ? @{$scores{$keyA}} : (1e10, "");

		foreach my $termB (@B) # .. for gene B
		{
			$keyB = "B".$termB;
			@scoreB = (defined $scores{$keyB}) ? @{$scores{$keyB}} : (1e10, "");
			
			$value = getValue($termA, $termB);

#			print "A: $termA  B: $termB $value \n";
			
      if ($value < $scoreA[0])
			{ @scoreA = ($value, $termA.$termB); }
			
			if ($value < $scoreB[0])
			{ @scoreB = ($value, $termA.$termB); }

			$scores{$keyB} = [@scoreB];
		}

		$scores{$keyA} = [@scoreA];
	 }
	
	my(%winners) = (); $value = 0;
	while ((my $key, my $val) = each %scores)
	{
		my($link) = @{$val}[1];
		
		next if (defined $winners{$link});
		$nb++;
		$value += @{$val}[0];

#		print ">> $link\n";
		
		$winners{$link} = 1;
	}

	return $value / $nb;
 }

# Comparison of genes by taking the average score of each term/term pairs
sub compareGenes_
 {
  my($a, $b) = @_;

  my($value, $mean, $nb) = (0, 0, 0);

  foreach my $termA (@{@$a}) # array of GO terms for gene A
   {
    foreach my $termB (@{@$b}) # .. for gene B
     {
  		$value = getValue($termA, $termB);
      $nb++;
			
      $mean += $value; 
     }
   }

  return $mean / $nb;
 }

sub getValue
 {
	 my($termA, $termB) = @_;
	 my($id) = $termA . "_" . $termB;

	 $value = $term2term{$id};

	 unless (defined $value)
	 { error("getValue: unknown value for ($termA, $termB)"); }
		 
	 return $value;
 }

sub error
 {
  my($msg) = @_;
  print LOG "ERROR: $msg\n";
  close(LOG);
  CLOSE();
  print $msg . "\n";
  die;
 }
