
# ID for GO terms representing links types (cf. term.*)
my(%LINK_TYPE) =
 (
  "5"  => "IS_A",
  "3"  => "PART_OF"
 );

print " > Getting trees of GO terms\n";

my(%GO_CHILDREN) =
 (
  "P" => {},  # array of direct children of each GO term
  "C" => {},
  "F" => {} 
 );

my(%GO_PARENTS) =
 (
  "P" => {},  # array of direct parents of each GO term
  "C" => {},
  "F" => {} 
 );

my(%GO_TERM) = %{retrieve("step1.GO_TERM.dump")}; # key: database ID, value: GO ID
my(%GO_ASPECT) = %{retrieve("step1.GO_ASPECT.dump")}; # key: GO term, value: aspect

my(%p_cnt, %c_cnt) = (0,0);

my($tree_file) = $directory . "/term2term.txt";

test_file($tree_file);

open(TREE, $tree_file);
open(DOT, ">dot.graph");

print DOT "digraph GO\n {\n";

while (my $line = <TREE>)
 {
  chomp($line);
  my(@data) = split("\t", $line);

  my($type) = $LINK_TYPE{$data[1]};
  my($parent) = $GO_TERM{$data[2]};
  my($child) = $GO_TERM{$data[3]};

  unless (defined $child)
   { print " Error: unknown GO term ID (child): \"" . $data[3] . "\")\n"; exit; }

  unless (defined $parent)
   { print " Error: unknown GO term ID (parent): \"" . $data[2] . "\")\n"; exit; }

  my($aspect) = $GO_ASPECT{$parent};
  my($child_aspect) = $GO_ASPECT{$child};

  next unless ($aspect =~ /P|F|C/); # we drop any "root" or "link" term

  print DOT "  \"" . $parent . "\" -> \"" . $child . "\"\n";

  if ($aspect ne $child_aspect)
   { print " Error: no compatible aspect between child (" . $child_aspect . ") and parent (" . $aspect . ")\n"; exit; }

  # An entry in %GO_CHILDREN is defined if a term have at least one child
  # (which is the case for $parent here)
  my($children_) = $GO_CHILDREN{$aspect}{$parent};
  my(@children_) = (defined $children_) ? @{$children_} : ();

    push(@children_, [$child, $type]);
    $c_cnt{$aspect}++;
    $GO_CHILDREN{$aspect}{$parent} = [@children_];

  # An entry in %GO_PARENTS is defined if a term have at least one parent
  # (which is the case for $child here)
  my($parents_) = $GO_PARENTS{$aspect}{$child};
  my(@parents_) = (defined $parents_) ? @{$parents_} : ();

    push(@parents_, [$parent, $type]);
    $p_cnt{$aspect}++;
    $GO_PARENTS{$aspect}{$child} = [@parents_];
 }

close(TREE);

print DOT " }\n";

close(DOT);

while ((my $aspect, my $children) = each %GO_CHILDREN)
 {
  my(%CHILDREN) = %{$children};
  
  print "   " . $aspect . " aspect: " . (scalar keys %CHILDREN) . " GO nodes have declared " . $c_cnt{$aspect} . " children.\n";
  nstore(\%CHILDREN, "step2.GO_CHILDREN." . $aspect . ".dump");
 }

print "\n";

while ((my $aspect, my $parents) = each %GO_PARENTS)
 {
  my(%PARENTS) = %{$parents};
  
  print "   " . $aspect . " aspect: " . (scalar keys %PARENTS) . " GO nodes have declared " . $p_cnt{$aspect} . " parents.\n";
  nstore(\%PARENTS, "step2.GO_PARENTS." . $aspect . ".dump");
 }

#_______________________________________________________________

print " > Populating all parents for each node\n";

foreach my $aspect ("P", "F", "C")
 {
  my(%GO_ALL_PARENTS) = (); # key: GO term, value: array of GO terms

  %GO_PARENTS = %{retrieve("step2.GO_PARENTS." . $aspect . ".dump")};
   # key: GO term, value: array of GO terms

  print "   " . $aspect . " aspect\n";

  while ((my $term, my $term_aspect) = each %GO_ASPECT)
   {
    next if ($term_aspect ne $aspect);

    my(%LIST) = (); %LIST = crawlToRoot($term, \%LIST);

    $GO_ALL_PARENTS{$term} = [keys %LIST];
   }

  nstore(\%GO_ALL_PARENTS, "step2.GO_ALL_PARENTS." . $aspect . ".dump");
 }
 
sub crawlToRoot
 { 
  my($node, $list) = @_;

# L'idee de cache n'est pas retenue car il y a des erreurs:
# tous les chemins en amont d'un noeud ne sont pas parcourus
# puisque ce noeud est deja mis dans le cache des que l'un de
# ces chemins est parcouru.

  my(%LIST) = %$list;
  $LIST{$node} = 1; # we register the branching node as its own parent

  unless (defined $GO_PARENTS{$node})
   { return %LIST; }

  my(@node_parents) = @{$GO_PARENTS{$node}};

  foreach my $node_parent (@node_parents)
   {
    my($term) = @{$node_parent}[0];
    next if (defined $LIST{$term});

    %LIST = crawlToRoot($term, \%LIST);
    #$LIST{$node} = 1;  # <<< MOVED (l.142) because we want that GO_ALL_PARENTS contains parents of nodes as well as node itself
   }
   
  return %LIST;
 }
