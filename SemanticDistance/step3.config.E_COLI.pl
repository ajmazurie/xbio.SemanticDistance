# Parameters for Escherichia coli GO annotations
# (sources: GenProtEC, EcoCyc)

$association_file = $directory . "/../E.coli/gene_association.ecoli";

$evidence_checker =
  sub
   {
    my($evidence) = @_;

    return ($evidence =~ /IEA/) ? 0 : 1; # All but IEA
 #  return 1; # Any evidence type
 #  return ($evidence =~ /(TAS|IDA)/) ? 1 : 0; # Only TAS or IDA
   };

$gene_column = 1; # we take the b-number (Blattner) as raw gene ID

#::: Initialization (for gene_translator)
 my($names_file) = $directory . "/../E.coli/gene-links.dat";
    # file provided by EcoCyc (http://EcoCyc.org/gene-links.dat )

 my(%COLI_NAMES) = (); # key: a gene name ID (EcoGene, Blattner, SwissProt...), value: b-number

 print "   Loading $names_file ... ";

 open(COLI_NAMES, $names_file);

 while (my $line = <COLI_NAMES>)
  {
   chomp($line); next if ($line =~ /^#/);
   my(@data) = split("\t", $line);

   my($ecogene) = $data[1]; # EcoGene ID
   my($b_number) = $data[2]; # Blattner GenBank record ID (= b-number)
   my($swissprot) = $data[3]; # Swiss-Prot ID
   my($name) = uc($data[5]); # Gene name (as provided by EcoCyc)

   if (defined $swissprot) { $COLI_NAMES{$swissprot} = $name; }
   if (defined $ecogene) { $COLI_NAMES{$ecogene} = $name; }
   if (defined $b_number) { $COLI_NAMES{$b_number} = $name; }
  }

 close(COLI_NAMES);

 print "Ok\n";
#:::

# Strategy to obtain a gene name:
#  - if a valid full name is associated to the given b-number, we take it
#  - else,
#     - if we have a variant (b-number by suffix), we do the same thing with
#       the b-number, without the suffix
#     - if not, we take the raw name as the gene name
#
# All this WILL BE CHANGED when a valid bioEntities dataset will be
# builded in GeNetDB to handle genes of Escherichia coli
$gene_translator =
  sub
   {
    my($raw_name) = @_;

    my($gene_id) = $COLI_NAMES{$raw_name};

    unless (defined $gene_id)
     {
      print "   gene_translator() warning: unknown b-number '$raw_name'\n";

      if ($raw_name =~ /(b[0-9]{4})_[0-9]/)
       {
        $gene_id = $COLI_NAMES{$1};
        unless (defined $gene_id)
         { print "   gene_translator() error: unable to find a variant for '$raw_name'\n"; exit; }

        print "   (we use '$1' = '$gene_id')\n";
       }
      else
       { $gene_id = uc($raw_name); }
     }

    return "ec:" . $gene_id . "#gene";
   };
