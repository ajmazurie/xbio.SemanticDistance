
use DBI;
 
my($drh, $dbh, $sth);

sub OPEN
 {
  print "   Connecting to " . $db_host . " ... ";

  $drh = DBI->install_driver("mysql");
  $dbh = DBI->connect("DBI:mysql:$db_base:$db_host", $db_user, $db_pass)
   or die("Unable to connect to " . $db_host);

  print "Ok\n";
 }
 
my($table);
 
sub START_ASPECT
 {
  my($aspect) = @_;
  $table = $table_name->($aspect);

  my(@TABLE_STRUCTURE) =
   (
    "geneA varchar(50) NOT NULL",
    "geneB varchar(50) NOT NULL",
    "value float NOT NULL",
    "PRIMARY KEY (geneA, geneB)",
    "UNIQUE KEY (geneB, geneA)"
   );

  print "   Resetting table " . $table . " ... ";

  $dbh->do("DROP TABLE IF EXISTS " . $table);
  $dbh->do("CREATE TABLE " . $table . " (" . join(",", @TABLE_STRUCTURE) . ")");

  print "Ok\n";
 }

sub WRITE
 {
  my($geneA, $geneB, $value) = @_;

  $sth = $dbh->do("INSERT INTO $table VALUES (" .
                  "\"$geneA\",\"$geneB\",\"$value\")");
 }

sub END_ASPECT
 {
 }

sub CLOSE
 {
  $dbh->disconnect();
 }

