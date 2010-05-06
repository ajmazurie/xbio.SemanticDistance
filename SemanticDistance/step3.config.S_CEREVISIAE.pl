# Parameters for Saccharomyces cerevisae GO annotations
# (sources: SGD, GeNetDB)

$association_file = $directory . "/../s_cerevisiae/gene_association.sgd";

$evidence_checker =
  sub
   {
    my($evidence) = @_;

    return ($evidence =~ /IEA/) ? 0 : 1; # All but IEA
 #  return 1; # Any evidence type
 #  return ($evidence =~ /(TAS|IDA)/) ? 1 : 0; # Only TAS or IDA
   };

$gene_column = 10; # we take the first synonym as raw gene ID
$id_column = 1;

#::: Initialization (for gene_translator)

 open(TRANSLAT, $directory . "/../s_cerevisiae/liste.converted");

 my(%name2code) = ();

 while (my $line = <TRANSLAT>)
  {
   chomp($line); my(@data) = split("\t", $line);
	 
   $name2code{$data[0]} = $data[1];
  }

close(TRANSLAT);

$gene_translator =
  sub
   {
    my($raw_name) = @_;

    my(@raws) = split(/\|/, uc($raw_name));
    $raw_name = $raws[0];

    $real_name = $name2code{$raw_name};

    if (defined $real_name)
     { return $real_name; }
    else
     { print "Gene name not found: " . $raw_name . "\n"; return ""; }
   };

$gene_link =
  sub
   {
		my($raw_name) = @_;
		 
		return "<a href='http://db.yeastgenome.org/cgi-bin/SGD/locus.pl?locus=$raw_name' target='_blank'>SGD</a>";
   };

$go_link =
  sub
   {
		my($term_id) = @_;
		
	  $term_id =~ /GO:([0-9]{7})/;
    return "(<a href='http://db.yeastgenome.org/cgi-bin/SGD/GO/go.pl?goid=$1' target='_blank'>SGD</a>, " .
			     "<a href='http://www.godatabase.org/cgi-bin/amigo/go.cgi?open_1=$term_id' target='_blank'>AmiGO</a>)";
	 };
