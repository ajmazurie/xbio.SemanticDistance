
$kernel_name = "JIANG";

sub KERNEL
 {
  my($pms, $p1, $p2) = @_; # all parameters are superior to 0
 
  # Jiang distance [0; 2*ln(t)]
	return - 2 * log($pms) - (log($p1) + log($p2));
 };

