
print " > Building tables of GO terms (ID and aspects)\n";

my(%ASPECT) =
 (
  "Gene_Ontology" => "root",
  "biological_process" => "P",
  "cellular_component" => "C",
  "molecular_function" => "F",
  "relationship" => "link"
 );

my(%GO_TERM) = ();  # key: database ID, value: GO term
my(%GO_ASPECT) = (); # key: GO term, value: aspect
my(%GO_DEFS) = (); # key: GO term, value: GO definition
my(%cnt) = ();

my($term_file) = $directory . "/term.txt";
my($term_definition) = $directory . "/term_definition.txt";

test_file($term_file);

open(TERMS, $term_file);

while (my $line = <TERMS>)
 {
  chomp($line);
  my(@data) = split("\t", $line);
  
  $GO_TERM{$data[0]} = $data[3];
	$GO_DEFS{$data[3]} = $data[1];
  
  my($aspect) = $ASPECT{$data[2]};
  
  unless (defined $aspect)
   { print " Error: unknown aspect \"" . $data[2] . "\" (node: " . $data[3] . ")\n"; exit; }
   
  $GO_ASPECT{$data[3]} = $aspect;
  $cnt{$aspect}++;
 }

close(TERMS);

test_file($term_definition);

open(DEF, $term_definition);

while (my $line = <DEF>)
{
  chomp($line);
  my(@data) = split("\t", $line);
  
	my($id) = $GO_TERM{$data[0]};
	my($def) = $GO_DEFS{$id};
	
  $GO_DEFS{$id} = $def ## UNCOMMENT TO HAVE LONGUER DEFINITIONS ## . ". " . $data[1];

#  print " $id " . $GO_DEFS{$id} . "\n";
}

close(DEF);

nstore(\%GO_TERM, "step1.GO_TERM.dump");
nstore(\%GO_ASPECT, "step1.GO_ASPECT.dump");
nstore(\%GO_DEFS, "step1.GO_DEFS.dump");

print "   " . (scalar keys %GO_TERM) . " GO terms registered\n";
print "   (P: " . $cnt{"P"} . ", F: " . $cnt{"F"} . ", C: " . $cnt{"C"} . ")\n";
