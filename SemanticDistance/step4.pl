
print " > Computing information content\n";

my(%GO_USAGE) = %{retrieve("step3.GO_USAGE.dump")}; # key: GO term, value: usage count
my(%GO_ASPECT) = %{retrieve("step1.GO_ASPECT.dump")}; # key: GO term, value: aspect

my(%GO_IC) = (); # key: GO term, value: information content

foreach my $aspect ("P", "F", "C")
 {
  print "   " . $aspect . " aspect\n";

  print "   - Computing terms occurences\n";

  my(%GO_CHILDREN) = %{retrieve("step2.GO_CHILDREN." . $aspect . ".dump")};
   # key: GO term, value: array of GO terms

  my(%GO_PARENTS) = %{retrieve("step2.GO_PARENTS." . $aspect . ".dump")};
   # key: GO term, value: array of GO terms

  my(%GO_ALL_PARENTS) = %{retrieve("step2.GO_ALL_PARENTS." . $aspect . ".dump")};
   # key: GO term, value: array of GO terms

  %GO_IC = ();
  my($max, $rank, $cnt) = (0,0,0);
  
  # finding root node
  my($root_node);
  while ((my $term, my $children) = each %GO_CHILDREN)
   {
    next if (defined $GO_PARENTS{$term});

    if (defined $root_node)
     { print " Error: there is more than one root node (" . $root_node . ", " . $term . ")\n"; exit; }

    $root_node = $term;
    $GO_IC{$root_node} = $GO_USAGE{$root_node};
   }
  
  print "     Root node: " . $root_node . "\n";
  
  while(1)
   {
    # - selecting all nodes (for this aspect) having no children
    my(@RANK) = (); $cnt = 0;
    while ((my $term, my $parents) = each %GO_PARENTS)
     {
      $cnt++;
      
      # we want to select any node having
      # parents and don't having children
      next if (defined $GO_CHILDREN{$term});

      push(@RANK, $term);
     }

    $rank++; print "     Rank " . $rank . " (" . (scalar @RANK) . " nodes between " . $cnt . ")\n";

    if ((scalar @RANK) == 0) # we have reached root's children
     {
      print "     Root node (" . $root_node . ") reached.\n";
      last;
     }

    # - registering leafs usage count against themselves and all parents
    # - deleting these leafs nodes
    foreach my $leaf (@RANK)
     {
      my(@parents) = @{$GO_PARENTS{$leaf}};
      my($usage) = $GO_USAGE{$leaf};

      if (defined $usage)
       {
        $max += $usage;

        # - propaging usage count on all term's parents (and term itself)
        my(@LIST) = @{$GO_ALL_PARENTS{$leaf}};

        foreach my $parent (@LIST) # $leaf is itself contained in @LIST
         { $GO_IC{$parent} += $usage; }
       }
        # if %GO_USAGE{$leaf} is not defined, we don't touch to the %GO_IC{$leaf}
        # since this value can have been modified through children of $leaf term

      # - unregistering this term from parent's children
      foreach my $parent (@parents)
       {
        my($parent_term) = @{$parent}[0];
         # $parent is an array: 0= GO term, 1= link type with child (cf. step2.pl)

        # removing any reference to this children, or
        # even removing %GO_CHILDREN entry if needed
        my(@siblings) = @{$GO_CHILDREN{$parent_term}};
        
        my($pos) = 0;
        foreach my $entry (@siblings)
         {
          my($sibling) = @{$entry}[0];
          last if ($sibling eq $leaf);
          $pos++;
         }

        if ($pos == (scalar @siblings))
         {
          print " Error: the current term (" . $leaf . ") has not been found within siblings.\n";
          exit;
         }

        splice(@siblings, $pos, 1);

        if ((scalar @siblings) == 0)
         { delete $GO_CHILDREN{$parent_term}; }
        else
         { $GO_CHILDREN{$parent_term} = [@siblings]; }
       }
       
      delete $GO_PARENTS{$leaf};
     }
   }

  print "   - Computing terms probabilities (m = " . $max . ")\n";

  my($rawRootIC) = $GO_IC{$root_node};

  while ((my $term, my $term_aspect) = each %GO_ASPECT)
   {
    next if ($term_aspect ne $aspect);
    
    if (defined $GO_IC{$term})
     {
      $GO_IC{$term} /= $max;
     }
    else
     {
      if (defined $GO_USAGE{$term})
       { print " Error: the term $term has not been found in %GO_IC (usage: " . $GO_USAGE{$term} . ")\n"; exit; }

      $GO_IC{$term} = 0;
     }
   }

  my($rootIC) = $GO_IC{$root_node};

  print "   - Checking root term IC: " . $rootIC;
  
  if ($rawRootIC != $max) 
   { print " Error ! (root IC = $rawRootIC, max = $max)\n"; exit; }
  else
   { print " Ok.\n"; }

  nstore(\%GO_IC, "step4.IC." . $aspect . ".dump");
  print "\n";
 }
 
