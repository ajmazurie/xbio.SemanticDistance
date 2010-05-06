
print " > Building terms/terms similarity matrix\n";

test_file("step5.config.pl");
do "step5.config.pl";

my(%IC, %GO_ALL_PARENTS, %term2term);
my($nb, $nb_zero, $nb_one) = (0,0,0);

foreach my $aspect ("P", "F", "C")
 {
  print "   " . $aspect . " aspect\n";

  %IC = %{retrieve("step4.IC." . $aspect . ".dump")};
   # key: GO term, value: information content 

  my(%ANNOTATION) = %{retrieve("step3.ANNOTATION." . $aspect . ".dump")};
   # key: user defined gene name, value: array of GO terms

  %GO_ALL_PARENTS = %{retrieve("step2.GO_ALL_PARENTS." . $aspect . ".dump")};
   # key: GO term, value: array of GO terms

  # Just some checkers, just in case...
  while ((my $term, my $terms) = each %GO_ALL_PARENTS)
   {
    my(@GO_TERMS) = ($term, (@{$terms}));
    foreach my $go_term (@GO_TERMS)
     {
      unless (defined $IC{$go_term})
       { error("the term $go_term is defined in %GO_ALL_PARENTS but not in %IC."); }
     }
   }

  while ((my $gene, my $terms) = each %ANNOTATION)
   {
    foreach my $go_term (@{$terms})
     {
      unless (defined $IC{$go_term})
       { error("the term $go_term is defined in %ANNOTATION but not in %IC."); }
     }
   }

  %term2term = ();

  print "   (" . (scalar keys %ANNOTATION) . " genes, " . (scalar keys %IC) . " terms)\n";

  my(@A) = sort(keys %ANNOTATION);
  my(@B) = @A;
  my(@termsA, @termsB);

	$nb = 0; $nb_zero = 0; $nb_one = 0;
	
  foreach my $geneA (@A)
   {
    @termsA = @{$ANNOTATION{$geneA}};

    foreach my $geneB (@B)
     {
      @termsB = @{$ANNOTATION{$geneB}};

      compareTerms(\@termsA, \@termsB);
     }

		shift(@B);
   }

	print "   $nb comparisons ($nb_zero zero, $nb_one one)\n";
	
  nstore(\%term2term, "step5.TERM2TERM." . $aspect . ".dump");
 }

# - Do the comparison of each terms of gene A against terms of gene B
#   (using the kernel provided)
sub compareTerms
 {
  my($a, $b) = @_;
  my($value) = 0;

  foreach my $termA (@{@$a}) # array of GO terms for gene A
   {
    foreach my $termB (@{@$b}) # .. for gene B
     {
      my($iid) = $termB . "_" . $termA;
      my($id) = $termA . "_" . $termB;

      next if ((defined $term2term{$id}) || (defined $term2term{$iid}));

      # a first check... each term must be known !
      unless (defined $GO_ALL_PARENTS{$termA})
       { error("compareTerms: $termA (A) not found in %GO_ALL_PARENTS"); }

      unless (defined $GO_ALL_PARENTS{$termB})
       { error("compareTerms: $termB (B) not found in %GO_ALL_PARENTS"); }

      # a second check... p(c) must be ]0;1]
      # (c is used by at leasy one gene, so p(c) > 0)
      my($pA, $pB) = ($IC{$termA}, $IC{$termB});

      if (($pA == 0) || ($pA > 1))
       { error("$termA (A) is not in ]0;1] (p=$pA)."); }

      if (($pB == 0) || ($pB > 1))
       { error("$termB (B) is not in ]0;1] (p=$pB)."); }

      my($Pms) = 2;

      if ($termA ne $termB)
       {
        # Computation of the Pms(termA, termB):
        # - looking for common parents to A and B
        my(@parents_of_A) = @{$GO_ALL_PARENTS{$termA}};
        my(@parents_of_B) = @{$GO_ALL_PARENTS{$termB}};

        ###
        my(%isect) = ();
        my(%union) = ();
        foreach my $item (@parents_of_A, @parents_of_B)
         { $union{$item}++ && $isect{$item}++; }

        my(@shared) = keys %isect;
        ###
          # intersection of @parents_of_A and _B
          # (cf http://iis1.cps.unizar.es/Oreilly/perl/cookbook/ch04_09.htm )

        # - looking for minimum IC
        foreach my $parent (@shared)
         {
          my($pParent) = $IC{$parent};

          # a third check... IC can't be null, as $parent is associated to (at least) one gene
          if ($pParent == 0)
           { error("broken monotony: the parent $parent of ($termA, $termB) as a IC = 0"); }

          # a fourth check... IC(parent) must be >= IC(children)
          if (($pParent < $pA) || ($pParent < $pB))
           { error("broken monotony: IC of parent p($parent)=$pParent is lesser than pA($termA)=$pA or pB($termB)=$pB"); }

          if ($pParent < $Pms) { $Pms = $pParent; }
         }

        if ($Pms == 2)
         { error("no shared parents between $termA and $termB."); }
       }

      # in case of $termA == $termB, then
      # Pms($termA, $termB) = p($termA) = p($termB)
      else
       {
        $Pms = $pA;       
       }

      if ($Pms == 0)
       { error("Pms(A: $termA, B: $termB) = 0"); }

      my($value) =
        KERNEL(
          $Pms, # Probability of the minimum subsumer, [min(pA, pB);1]
          $pA,  # Probability of term A, ]0;1]
          $pB   # Probability of term B, ]0;1]
              );

      # if error in formula, we skip this term/term comparison
      if ($value == -1)
       { error("unable to compare two terms: $termA and $termB ($Pms, $pA, $pB)"); }

			if ($value == 0) { $nb_zero++; }#print "0: $termA $termB\n"; }
			if ($value == 1) { $nb_one++; }# print "1: $termA $termB\n"; }
			$nb++;

      $term2term{$id} = $value;
      $term2term{$iid} = $value;
     }
   }
 }

sub error
 {
  my($msg) = @_;
  die $msg . "\n";
  CLOSE();
 }
