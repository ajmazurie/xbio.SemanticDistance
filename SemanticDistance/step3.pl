
print " > Associating genes and annotations\n";

test_file("step3.config.pl");
do "step3.config.pl";

my(%NAME) = (); # key: provided gene symbol, value: user defined gene name
my(%ASPECT) =
 (
  "P" => {}, # key: user defined gene name, value: array of GO terms
  "C" => {},
  "F" => {}
 ); # key: aspect, value: associations for this aspect

my(%GO_USAGE) = (); # key: GO ID, value: usage count
my(%GO_DEFS) = %{retrieve("step1.GO_DEFS.dump")}; # key: GO ID, value: definition

test_file($association_file);
open(LINK, $association_file);

my($last_gene_name);

my(%NAME2RAW) = (); # key: gene name, value: gene symbol

while (my $line = <LINK>)
 {
  chomp($line); next if ($line =~ /^!/);
  my(@data) = split("\t", $line);

    # we discard any association with unwanted evidence type
  next if ($evidence_checker->($data[6]) == 0); 

    # we discard any IS_NOT association
  next if ($data[3] eq "NOT");

  my($aspect) = $data[8];

  my($symbol) = $data[$gene_column];
	my($id) = $data[$id_column];
  my(@terms);

  # if it is the first time that this gene symbol is encountered
  # (for this aspect), we translate it into a user-defined gene name
  # AND we initialize the corresponding %ANNOTATION go terms array
  unless (defined($NAME{$symbol . $aspect}))
   {
    $last_gene_name = $gene_translator->($symbol);
		next if ($last_gene_name eq "");

    $NAME{$symbol . $aspect} = 1;
		$NAME2RAW{$last_gene_name} = $id;
    @terms = ();
   }
  else
   {
    # getting known associated terms for this aspect
    @terms = @{$ASPECT{$aspect}{$last_gene_name}};
   }

  push(@terms, $data[4]);
  $ASPECT{$aspect}{$last_gene_name} = [@terms];
 }

close(LINK);

while ((my $aspect, my $association) = each %ASPECT)
 {
  my(%ASSOCIATION) = %{$association};

	open(OUTPUT, ">genes." . $aspect);

	my($average_terms_by_genes) = 0;
	my($max_terms) = 0;
	my($max_gene) = "";
	
	foreach my $gene (sort (keys(%ASSOCIATION)))
   {
    my(@TERMS) = @{$ASSOCIATION{$gene}};
    
    if ((scalar @TERMS) > 1) # removing duplicates terms
     {
      my(%saw); @saw{@TERMS} = ();
      @TERMS = sort keys %saw;
     }

		print OUTPUT $gene . "\t" . $gene_link->($NAME2RAW{$gene});
		
    $ASSOCIATION{$gene} = [@TERMS];
		
		my(@terms) = ();
		
    foreach my $term (@TERMS)
     {
			$GO_USAGE{$term}++;
			push(@terms, $GO_DEFS{$term} . " &mdash; " . $go_link->($term));
		 }

		print OUTPUT "\t" . join("\t", @terms) . "\n";
		
		if ((scalar @TERMS) > 1)
		{
		 $average_terms_by_genes++;
		}

    if ((scalar @TERMS) > $max_terms)
		{
			$max_terms = (scalar @TERMS);
			$max_gene = $gene;
		}
	 }
	
	close(OUTPUT);

  print "   " . $aspect . " aspect: " . (scalar keys %ASSOCIATION) . " genes annotated.\n";
	print "   average: " . ($average_terms_by_genes / (scalar keys %ASSOCIATION)) * 100 . " %\n";
  print "   (max: $max_gene, with $max_terms terms)\n";
  nstore(\%ASSOCIATION, "step3.ANNOTATION." . $aspect . ".dump");
 }

nstore(\%GO_USAGE, "step3.GO_USAGE.dump");
