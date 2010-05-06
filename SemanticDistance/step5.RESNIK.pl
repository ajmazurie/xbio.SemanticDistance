
$kernel_name = "RESNIK";

sub KERNEL
 {
  my($pms, $p1, $p2) = @_; # all parameters are superior to 0
   
  # Resnik similarity
  return -log($pms);
 };

