#!/usr/bin/perl -w

use CGI qw/:all/;
use CGI::Session;
use CGI::Cookie;
use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;
use POSIX ();
use DBI;

#use sqlite3 data base!!~
my $dbfile = "data.db";
my $user = "";
my $password = "";
my $dsn = "dbi:SQLite:dbname=$dbfile";
my $dbh = DBI->connect($dsn,$user,$password,{
   PrintError       => 0,
   RaiseError       => 1,
   AutoCommit       => 1,
   FetchHashKeyName => 'NAME_lc',
});

print page_header();
my $recoveruser = param('recoveruser')||"";
my $useremail = param('useremail')||"";
#print "recover:$recoveruser useremail:$useremail\n";
my $warning = "";
if($recoveruser && $useremail){
	my $sth = $dbh -> prepare("SELECT password FROM User WHERE username = '$recoveruser' AND email = '$useremail'");
	$sth->execute();
	my $row;
	$row = $sth->fetchrow_arrayref();
	if(@$row[0]){
		open(MAIL, "|/usr/sbin/sendmail -t");
		# Email Header
		print MAIL "To: $useremail\n";
		print MAIL "From: z5050807\@bitter.com\n";
		print MAIL "Subject: Recovery your password\n\n";
		# Email Body
		print MAIL "Your password is:@$row[0]";

		close(MAIL);
		print successsend();
	}else{	
		$warning = "Please enter a valid username and correct email!<br>";
		print recoverypage();
	}
}else{
	$warning = "Please enter your username and email and we'll send you email<br>";
	print recoverypage();
}

$dbh->disconnect;

sub successsend{
	return <<eof
<body>
<p class="success">The email is successfully sent, please check your e-mail! Thank you!</p>
<form method="POST" action="bitter.cgi">
<input type="submit" value="Back to login page" class=\"login login-submit\">
</body>
</html>
eof
}

sub recoverypage{
	return <<eof
<body>
<div class="login-card">
$warning
<form method="POST" action="">
Please enter your username:<br>
<input type="text" name="recoveruser" value="$recoveruser"><br>
Please confirm your email:<br>
<input type="text" name="useremail" value="$useremail"><br>
<input type="submit" value="Submit" class="login login-submit"><br>
</form>
</div>
</body>
</html>
eof
}



sub page_header {
    return <<eof
Content-Type: text/html

<!DOCTYPE html>
<html >
  <head>
    <meta charset="UTF-8">
    <title>Log-in</title>

    <link rel="stylesheet" href="login.css">
  </head>
eof
}
