
$kernel_name = "LIN";

sub KERNEL
 {
  my($pms, $p1, $p2) = @_; # all parameters are superior to 0
 
  # Lin similarity
  my($d) = log($p1) + log($p2);

#  return ($d == 0) ? -1 : ((2 * log($pms)) / $d);

## Convertion to distance, according to Nuno Seco et al.
	return ($d == 0) ? -1 : 1 - ((2 * log($pms)) / $d);
 };

