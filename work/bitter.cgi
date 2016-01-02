#!/usr/bin/perl -w

use CGI qw/:all/;
use CGI::Session;
use CGI::Cookie;
use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;
use POSIX ();
use DBI;

print page_header();

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



$cgi = CGI->new();
#get the session if it already exists
#$sid = $cgi->cookie('CGISESSID') || $cgi->param('CGISESSID') || undef;
#print "SID: $sid\n";
#$session    = new CGI::Session(undef, $sid, {Directory=>'/tmp'});
$session = CGI::Session->new();


$sid = $session ->id();
#$cookie = $cgi->cookie(CGISESSID => $sid);
#print $cgi->header(-cookie=>$cookie);
#storing data in the session



my $errorMessage = "";
my $submit = $cgi->param('submitform')||"false";
my $userName = $cgi->param('user')||"";
my $userPassword = $cgi->param('pass')||"";
my $loginStatus = $cgi->param('loginStatus')||"notlogged";
my $delete = param('delete')||"";
#determine which script to jump
my $page;
$session -> param("userinfo",$userName);
$session -> param("passinfo",$userPassword);
$session -> param("loginStatus",$loginStatus);
$session -> param("submitform",$submit);
my $usr = param('visit')||"";
if($delete){
	my $sth = $dbh -> prepare("DELETE FROM User WHERE username = '$usr'");
	$sth->execute();
}
if(!$userName || !$userPassword){
	$page="";
}else{
	my $sth = $dbh -> prepare("SELECT * FROM User WHERE username = '$userName' AND password = '$userPassword'");
	$sth->execute();
	my $row;
	$row = $sth->fetchrow_arrayref();
	if($row){
		$page="main.cgi";
		$submit = "true";
		$loginStatus = "logged";
	}else{
		$errorMessage = "The username or password is incorrect, please try again!<br>\n";
	}
}

print login_page();
$dbh->disconnect();


sub login_page{
   return <<eof
 <body>
    <div class="login-card">
    <h1>Log-in</h1><br>
$errorMessage
  <form action="$page" method="POST" id="loginForm">
    <input type="text" name="user" placeholder="Username">
    <input type="password" name="pass" placeholder="Password">
    <input type="hidden" name="submitform" value="$submit" id="submitOrNot">
    <input type="hidden" name="passinfo" value="$userPassword">
    <input type="hidden" name="userinfo" value="$userName">
    <input type="hidden" name="loginStatus" value="$loginStatus">
    <input type="hidden" name="CGISESSID" value="$sid">
    <input type="hidden" name="visit" value="$userName">
    <input type="submit" name="login" class="login login-submit" value="login">
  </form>
<script>
	var x;
	x = document.getElementById("submitOrNot").value;
	if(x=="true"){
		document.getElementById('loginForm').submit();	
		document.getElementById("submitOrNot").value = "false";
	}
</script>
    
  <div class="login-help">
    <a href=\"creatNew.cgi\">Register</a>         <a href=\"recovery.cgi\">Forget my password</a>
  </div>
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
