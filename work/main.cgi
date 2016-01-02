#!/usr/bin/perl -w

# written by David Mao San Wei Z5050807


use CGI qw/:all/;
use CGI::Session;
use CGI::Cookie;
use POSIX;
#use CGI qw(:standard);
use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;
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


$cgi = CGI->new();
$sid = param('CGISESSID');
$session    = new CGI::Session(undef, $sid, {Directory=>'/tmp'});

$currentUser = $session->param('userinfo') || param('userinfo');
$visitedUser = param('visit')||"$currentUser";
$userPass = $session->param('passinfo');
$loggedStatus = $session->param('loginStatus');
$submitform   = $session -> param("submitform");
$sendBleat = param('sendbleat') || "";
$listenstatus = param('listenstatus')||"";
$visitingBleat = param('bleatId')||"";
$replyToBleat = param('replyto')||"";
$deleteBleat = param('deletebleat')||"";
$pageIndex = param('pagenum')||"1";
$image1 = param('image1')||"";
$image2 = param('image2')||"";
$image3 = param('image3')||"";
$image4 = param('image4')||"";
$usrnamePageIndex = param('usrnamepage')||"1";
$viewingElements = "12";
$editpossible = "false";
$backgroundimage = "images/$visitedUser" . "background.jpg";

sub main() {

    print page_header();

    warningsToBrowser(1);
	
    $debug = 1;
    $nameSearch = param('userSearch')||"";
    $serchString = param('usrsearch');
    $bleatSearch = param('bleatSearch')||"";
    $bleatsearchstring = param('bleatsub')|"";
    #insertNewBleat if the parameter sendBleat is set
    if($sendBleat){
	insertNewBleat();
    }
    #insert bleat which reply to another bleat
    if($replyToBleat){
	insertReplyBleat();
    }
    #delete specified bleat and his responses
    if($deleteBleat){
	deleteBleat($visitingBleat);
	$visitingBleat="";
    }
    #check if the user is being listened or unlistened
    if($listenstatus eq "Start Listen This User"){
	$dbh->do("INSERT INTO Listens VALUES('$currentUser','$visitedUser')");
	my $sth = $dbh -> prepare("SELECT * FROM User WHERE username = '$visitedUser'");
   	 $sth->execute();
    	my $row;
    	$row = $sth->fetchrow_arrayref();
	if(@$row[9] eq '3'){
		open(MAIL, "|/usr/sbin/sendmail -t");
		# Email Header
		print MAIL "To: @$row[2]\n";
		print MAIL "From: z5050807\@bitter.com\n";
		print MAIL "Subject: You have a new listener,please check\n\n";
		# Email Body
		print MAIL "Please check your new listener:$currentUser";
		close(MAIL);
	}
    }elsif($listenstatus eq "Unlisten This User"){
	$dbh->do("DELETE FROM Listens WHERE username = '$currentUser' AND listen_name = '$visitedUser'");
    }
    if($nameSearch){
	print search_name_page();
    }elsif($bleatSearch){
	if($bleatsearchstring){
		print search_bleat_page();
	}else{
		print user_page();
	}
    }elsif($visitingBleat){
	print bleatDetailPage();
    }
    else{
	print user_page();
    }
    print page_trailer();
	$dbh->disconnect();
}


# Show unformatted details for user "n".
# Increment parameter n and store it as a hidden variable
#
sub user_page {
    #if the user is in his page
    #get user information
    my $user_to_show  = $visitedUser;
    my $sth = $dbh -> prepare("SELECT * FROM User WHERE username = '$user_to_show'");
    $sth->execute();
    my $row;
    $row = $sth->fetchrow_arrayref();
    my $username = addBreakLine(@$row[0],"User Name");
    my $full_name = addBreakLine(@$row[3],"Full Name");
    my $home_latitude = addBreakLine(@$row[4],"Home Latitude");
    my $home_longitude = addBreakLine(@$row[5],"Home Longitude");
    my $home_suburb = addBreakLine(@$row[6],"Home Suburb");
    my $profileimage = "images/$visitedUser" . "profile.jpg";
    my $backgroundimage = @$row[8];
    #my $details_filename = "$user_to_show/details.txt";
    #open my $p, "$details_filename" or die "can not open $details_filename: $!";
    #$details = join '', <$p>;
    #close $p;
    #my $next_user = $n + 1;
    #get user's bleats
    my @userBleats;
    $sth = $dbh -> prepare("SELECT * FROM Bleats WHERE username = '$user_to_show' ORDER BY time DESC");
    $sth->execute();
    while($row = $sth->fetchrow_arrayref()){
	#save time, username and bleat information in order to display them later (0 bleat ID, 1 username, 2 latitude, 3 longitude, 4 time, 5 bleat, 6 in_reply_to, 7 image 1 url, 8 image 2 url...
	push @userBleats,"@$row[4] | @$row[1] | @$row[2] | @$row[3] | @$row[0] | @$row[5] | @$row[6] | @$row[7] | @$row[8] | @$row[9] | @$row[10]";
    }
    #get listening users
    my @listeners;
    $sth = $dbh -> prepare("SELECT listen_name FROM Listens WHERE username = '$user_to_show'");
    $sth->execute();
    while($row = $sth->fetchrow_arrayref()){
	push @listeners,"@$row[0]";
    }
    #get current listening user for the logged user
    my @currentListenning;
    $sth = $dbh -> prepare("SELECT listen_name FROM Listens WHERE username = '$currentUser'");
    $sth->execute();
    while($row = $sth->fetchrow_arrayref()){
	push @currentListenning,"@$row[0]";
    }

    foreach $listener (@listeners){
	$sth = $dbh -> prepare("SELECT * FROM Bleats WHERE username = '$listener' ORDER BY time DESC");
    	$sth->execute();
    	while($row = $sth->fetchrow_arrayref()){
	#save time, username and bleat information in order to display them later (0 bleat ID, 1 username, 2 latitude, 3 longitude, 4 time, 5 bleat, 6 in_reply_to, 7 image 1 url, 8 image 2 url...
		push @userBleats,"@$row[4] | @$row[1] | @$row[2] | @$row[3] | @$row[0] | @$row[5] | @$row[6] | @$row[7] | @$row[8] | @$row[9] | @$row[10]";
    	}
    }
    #get bleats that mention the user
    my @mentionIDs;
    $sth = $dbh -> prepare("SELECT bleatID FROM Bleatmention WHERE username = '$user_to_show'");
    $sth ->execute();
    while($row=$sth->fetchrow_arrayref()){
	push @mentionIDs,"@$row[0]";
    }
    foreach $mentionID (@mentionIDs){
	$sth = $dbh -> prepare("SELECT * FROM Bleats WHERE bleatID = '$mentionID' ORDER BY time DESC");
    	$sth->execute();
    	while($row = $sth->fetchrow_arrayref()){
	#save time, username and bleat information in order to display them later (0 bleat ID, 1 username, 2 latitude, 3 longitude, 4 time, 5 bleat, 6 in_reply_to, 7 image 1 url, 8 image 2 url...
		push @userBleats,"@$row[4] | @$row[1] | @$row[2] | @$row[3] | @$row[0] | @$row[5] | @$row[6] | @$row[7] | @$row[8] | @$row[9] | @$row[10]";
    	}
    }
    #reorder the @userBleats
    @userBleats = sort{substr($b,0,10)<=>substr($a,0,10)}@userBleats;

    my $bleatNumber = @userBleats;
    my @displayedBleats;
    my $maximumPage = ceil($bleatNumber/$viewingElements);
    if($pageIndex<$maximumPage){
	for(my $i=0;$i<$viewingElements;$i++){
		my $var = $i+$viewingElements*($pageIndex-1);
		push @displayedBleats,"$userBleats[$i+$viewingElements*($pageIndex-1)]";
	}
    }
    if($pageIndex==$maximumPage){
	for(my $i=0;$i<($bleatNumber-($maximumPage-1)*$viewingElements);$i++){
		my $var = $i+$viewingElements*($pageIndex-1);
		push @displayedBleats,"$userBleats[$i+$viewingElements*($pageIndex-1)]";
	}
    }
    my $next="";
    my $previous="";
    my $nextpage=$pageIndex+1;
    my $previouspage=$pageIndex-1;
    if($pageIndex=="1"){
	$next = "<a href=\"main.cgi?visit=$visitedUser&userinfo=$currentUser&pagenum=$nextpage\">nextpage</a> <br>\n";
    }elsif($pageIndex>"1" and $pageIndex<$maximumPage){
	$next = "<a href=\"main.cgi?visit=$visitedUser&userinfo=$currentUser&pagenum=$nextpage\">nextpage</a> <br>\n";
	$previous = "<a href=\"main.cgi?visit=$visitedUser&userinfo=$currentUser&pagenum=$previouspage\">previouspage</a> <br>\n";
    }elsif($pageIndex==$maximumPage){
	$previous = "<a href=\"main.cgi?visit=$visitedUser&userinfo=$currentUser&pagenum=$previouspage\">previouspage</a> <br>\n";
    }
    $bleatString = "";
    foreach $bleat (@displayedBleats){
	#$bleatString = "$BleatString <br>";
	$bleatString = "$bleatString <div class=\"jumbotron\">\n";
	my @bleatInfo = split(/ \| /,$bleat);
	$bleatString = "$bleatString Name: <a href=\"main.cgi?visit=$bleatInfo[1]&userinfo=$currentUser\">$bleatInfo[1]</a> <br>\n";
	$bleatString = "$bleatString Bleat: <a href=\"main.cgi?userinfo=$currentUser&bleatId=$bleatInfo[4]&visit=$bleatInfo[1]\">$bleatInfo[5]</a><br>\n";
	$bleatString = "$bleatString <div class=\"row\">\n
			<div class=\"col-md-3\"><img src=\"images/$bleatInfo[4]image1.jpg\" alt=\"\" style=\"width:128px;height:128px;\"></div>\n
			<div class=\"col-md-3\"><img src=\"images/$bleatInfo[4]image2.jpg\" alt=\"\" style=\"width:128px;height:128px;\"></div>\n
			<div class=\"col-md-3\"><img src=\"images/$bleatInfo[4]image3.jpg\" alt=\"\" style=\"width:128px;height:128px;\"></div>\n
			<div class=\"col-md-3\"><img src=\"images/$bleatInfo[4]image4.jpg\" alt=\"\" style=\"width:128px;height:128px;\"></div>\n
			</div>"; 
	$bleatString = "$bleatString Time: $bleatInfo[0] latitude: $bleatInfo[2] longitude: $bleatInfo[3]\n";
	if($bleatInfo[6]){
		$bleatString = "$bleatString<br>\n in_reply_to: $bleatInfo[6]\n";
	}
	
	$bleatString = "$bleatString </div>\n";
    }
#Add postBleat and listening user features!~
    my $postBleat="";
    my $listenOrUnlisten="";
    my $backToMyPage="";
    if($currentUser eq $visitedUser){
	$editpossible = "true";
	$postBleat="$postBleat <h3><span class=\"label label-primary\">Post bleat:</span></h3>\n";
	$postBleat="$postBleat <div class=\"form-group\"><form method=\"POST\" action\"\" enctype=\"multipart/form-data\">\n";
	$postBleat="$postBleat <input type=\"text\" class=\"form-control input-lg\" id=\"inputLarge\" name=\"bleattext\">\n";
	$postBleat="$postBleat <h5><span class=\"label label-primary\">Attach image1:</span><imatnput type=\"file\" name=\"image1\"></h4>
			       <h5><span class=\"label label-primary\">Attach image2:</span><input type=\"file\" name=\"image2\"></h4>
			       <h5><span class=\"label label-primary\">Attach image3:</span><input type=\"file\" name=\"image3\"></h4>
			       <h5><span class=\"label label-primary\">Attach image4:</span><input type=\"file\" name=\"image4\"></h4>";
	$postBleat="$postBleat <input type=\"hidden\" name=\"sendbleat\" value=\"true\">";
	$postBleat="$postBleat <input type=\"hidden\" name=\"userinfo\" value=\"$currentUser\">";
	$postBleat="$postBleat <input type=\"submit\" value=\"Send Bleat\" class=\"btn btn-primary\">\n</form></div>";
    }else{
	$listenOrUnlisten="$listenOrUnlisten <form method=\"POST\" action\"\">\n";
	my $status;
	if ( grep( /^$user_to_show$/, @currentListenning ) ) {
		$status = "Unlisten This User";
	}else{
		$status = "Start Listen This User";
	}
	$listenOrUnlisten="$listenOrUnlisten <input type=\"hidden\" name=\"listenstatus\" value=\"$status\">";
	$listenOrUnlisten="$listenOrUnlisten <input type=\"hidden\" name=\"userinfo\" value=\"$currentUser\">";
	$listenOrUnlisten="$listenOrUnlisten <input type=\"hidden\" name=\"visit\" value=\"$visitedUser\">";
	$listenOrUnlisten="$listenOrUnlisten <br><input type=\"submit\" value=\"$status\" class=\"btn btn-warning\" >\n</form>";
	$backToMyPage="<ul class=\"nav navbar-nav navbar-right\">
<li><a href=\"main.cgi?visit=$currentUser&userinfo=$currentUser\">My page!</a></li>
</ul>\n";
    }
#Add search for the bleat word feature


    return <<eof




<nav class="navbar navbar-default">
	<div class="container-fluid">
    		<div class="navbar-header">
			<div class="user_name"> $currentUser </div>
		</div>

		<form method="POST" action="" class="navbar-form navbar-left" role="search">
			<div class="form-group">
			<input type="text" name="usrsearch" class="form-control" placeholder="Search for user">
			</div>
		<input type="hidden" name="userSearch" value="true">
		<input type="hidden" name="userinfo" value="$currentUser">
		<input type="hidden" name="pagenum" value="1">
		<input type="submit" value="Search" class="btn btn-default">
		</form>


		<form method="POST" action="" class="navbar-form navbar-left" role="search">
			<div class="form-group">
			<input type="text" name="bleatsub" class="form-control" placeholder="Search for bleat">
			</div>
		<input type="hidden" name="bleatSearch" value="true">
		<input type="hidden" name="userinfo" value="$currentUser">
		<input type="hidden" name="visit" value="$visitedUser">
		<input type="submit" value="Search" class="btn btn-default">
		</form>
		<li class="nav navbar-nav navbar-right">
		<form method="POST" action="viewprofile.cgi" class="navbar-form navbar-left">
		<input type="hidden" name="userinfo" value="$currentUser">
		<input type="hidden" name="visit" value="$visitedUser">
		<input type="submit" value="viewProfile" class="btn btn-default"/>
		</form>
		</li>
		<ul class="nav navbar-nav navbar-right">
		<form method="POST" action="bitter.cgi" class="navbar-form navbar-left">
		<input type="hidden" name="submitform" value="false">
		<input type="submit" value="Log Out" class="btn btn-default">
		</form>
		</ul>
	
		$backToMyPage


	</div>
</nav>
<div class="allinfo">
<div class="bitter_user_details">
$visitedUser
</div>
<div class="row">
	<div class="col-md-6">
	<img src="$profileimage" alt="Please upload a profileimage" style="width:128px;height:128px;"></div>
	<div class="col-md-6">
	<br><br><label class="listening">Listening to: @listeners</label>
	</div>
</div> 
$postBleat
$listenOrUnlisten

<br>


$bleatString

<p>
<br>$bleatsearchstring
$next
$previous
</div>
eof
}

sub search_name_page{
    my $sth = $dbh -> prepare("SELECT * FROM User WHERE username LIKE '%$serchString%' OR full_name LIKE '%$serchString%' ");
    
    $sth->execute();
    my $row;
    my @resultUsr;
    my $pageString="";
    while($row = $sth->fetchrow_arrayref()){
	if (@$row[7] ne '1') {
	push @resultUsr,"@$row[0]";
	}
    }
    #add pagination here
    my $usrNumber = @resultUsr;

    my @displayedUsrs;
    my $maximumPage = ceil($usrNumber/$viewingElements);
    if($pageIndex<$maximumPage){
	for(my $i=0;$i<$viewingElements;$i++){
		my $var = $i+$viewingElements*($pageIndex-1);
		push @displayedUsrs,"$resultUsr[$i+$viewingElements*($pageIndex-1)]";
	}
    }
    if($pageIndex==$maximumPage){
	for(my $i=0;$i<($usrNumber-($maximumPage-1)*$viewingElements);$i++){
		my $var = $i+$viewingElements*($pageIndex-1);
		push @displayedUsrs,"$resultUsr[$i+$viewingElements*($pageIndex-1)]";
	}
    }
    my $next="";
    my $previous="";
    my $nextpage=$pageIndex+1;
    my $previouspage=$pageIndex-1;
    if($pageIndex=="1"){
	$next = "<a href=\"main.cgi?userSearch=$nameSearch&userinfo=$currentUser&pagenum=$nextpage&usrsearch=$serchString\">nextpage</a> <br>\n";
    }elsif($pageIndex>"1" and $pageIndex<$maximumPage){
	$next = "<a href=\"main.cgi?userSearch=$nameSearch&userinfo=$currentUser&pagenum=$nextpage&usrsearch=$serchString\">nextpage</a> <br>\n";
	$previous = "<a href=\"main.cgi?userSearch=$nameSearch&userinfo=$currentUser&pagenum=$previouspage&usrsearch=$serchString\">previouspage</a> <br>\n";
    }elsif($pageIndex==$maximumPage){
	$previous = "<a href=\"main.cgi?userSearch=$nameSearch&userinfo=$currentUser&pagenum=$previouspage&usrsearch=$serchString\">previouspage</a> <br>\n";
    }
    #endOfPagination

    foreach $usr (@displayedUsrs){
	$pageString="$pageString <a href=\"main.cgi?visit=$usr&userinfo=$currentUser\">$usr</a><br>";
    }
    return <<eof
<div class="allinfo">
<form method="POST" action="">
	<input type="hidden" name="userSearch" value="">
	<input type="hidden" name="userinfo" value="$currentUser">
	<input type="submit" value="Back to User" class="btn btn-primary">
</form>
$pageString<br><br>
$next
$previous
</div>
eof
}
#
# HTML placed at the top of every page
#
sub page_header {
    return <<eof
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
<head>
<title>Bitter</title>
<!-- Latest compiled and minified CSS -->
<link rel="stylesheet" href="bootstrap.min.css">

<!-- jQuery library -->
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>

<!-- Latest compiled JavaScript -->
<script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>

<link href="bitter.css" rel="stylesheet">
</head>
<body background="$backgroundimage">
<script type="text/javascript">
    var width = window.innerWidth;
    var height = window.innerHeight;

    document.getElementsByTagName("body")[0].style.backgroundSize = width + "px " + height + "px";
</script>
eof
}


#
# HTML placed at the bottom of every page
# It includes all supplied parameter values as a HTML comment
# if global variable $debug is set
#
sub page_trailer {
    my $html = "";
    $html .= join("", map("<!-- $_=".param($_)." -->\n", param())) if $debug;
    $html .= end_html;
    return $html;
}

sub addBreakLine{
    my ($input,$property) = @_;
    if($input){
	$input = "<br>$property: $input";
    }
    return $input;
}

sub insertNewBleat{
	my $bleatText = param('bleattext');
	my $time = time();
	my $bleatID = "";
	#get the maximum bleatID
	my $sth = $dbh -> prepare("SELECT bleatID FROM Bleats ORDER BY bleatID DESC LIMIT 1");
   	$sth->execute();
    	my $row;
	$row = $sth->fetchrow_arrayref();
 	$bleatID = @$row[0] + 1;
	if($bleatText){
		#creatNewBleat(insert value to our db)
		#escape single quote
		$bleatText =~ s/\'/\'\'/g;
		$dbh->do("INSERT INTO Bleats VALUES('$bleatID','$currentUser','-33','151','$time','$bleatText','','','','','')");
		#Check if there is any @ or #
		my @keywords;
		my @usernames;
		if($bleatText=~/\#/){
			@keywords = ($bleatText =~ /\#[^ ]+/g);
			foreach $keyword (@keywords){
				$keyword =~ s/^\#//;
				$dbh->do("INSERT INTO Bleatkeyword VALUES('$bleatID','$keyword')");
			}
		}
		if($bleatText=~/\@/){
			@usernames = ($bleatText =~ /\@[^\ ]+/g);
			foreach $userId (@usernames){
				$userId =~ s/^\@//;
				$userId =~ s/\ //g;
				$sth = $dbh -> prepare("SELECT * FROM User WHERE username = '$userId'");
				$sth->execute();
				$row = $sth->fetchrow_arrayref();
				if($row){
					if(@$row[9] eq "1"){

						open(MAIL, "|/usr/sbin/sendmail -t");
						# Email Header
						print MAIL "To: @$row[2]\n";
						print MAIL "From: z5050807\@bitter.com\n";
						print MAIL "Subject: You are mentioned by $bleatID,please check\n\n";
						# Email Body
						print MAIL "Please check your bleat";
						close(MAIL);
					}
					$dbh->do("INSERT INTO Bleatmention VALUES('$bleatID','$userId')");

				}
			}
		}
		if($image1){
			uploadImage("$bleatID","1",$image1);
		}
		if($image2){
			uploadImage("$bleatID","2",$image2);
		}
		if($image3){
			uploadImage("$bleatID","3",$image3);
		}
		if($image4){
			uploadImage("$bleatID","4",$image4);
		}				
	}

}

sub insertReplyBleat{
	my $bleatText = param('replyBleat');
	my $time = time();
	my $bleatID = "";
	#get the maximum bleatID
	my $sth = $dbh -> prepare("SELECT bleatID FROM Bleats ORDER BY bleatID DESC LIMIT 1");
   	$sth->execute();
    	my $row;
	$row = $sth->fetchrow_arrayref();
 	$bleatID = @$row[0] + 1;
	if($bleatText){
		#creatNewBleat(insert value to our db)
		#escape single quote
		$bleatText =~ s/\'/\'\'/g;
		$dbh->do("INSERT INTO Bleats VALUES('$bleatID','$currentUser','-33','151','$time','$bleatText','$replyToBleat','','','','')");
		#Check if there is any @ or #
		my @keywords;
		my @usernames;
		if($bleatText=~/\#/){
			@keywords = ($bleatText =~ /\#[^ ]+/g);
			foreach $keyword (@keywords){
				$keyword =~ s/^\#//;
				$dbh->do("INSERT INTO Bleatkeyword VALUES('$bleatID','$keyword')");
			}
		}
		if($bleatText=~/\@/){
			@usernames = ($bleatText=~/\@[^ ]+/g);
			foreach $userId (@usernames){
				$userId =~ s/^\@//;
				$sth = $dbh -> prepare("SELECT username FROM User WHERE username = '$userId'");
				$sth -> execute();
				$row = $sth->fetchrow_arrayref();
				if($row){
					
					$dbh->do("INSERT INTO Bleatmention VALUES('$bleatID','$userId')");
					if(@$row[9] eq "1"){
						open(MAIL, "|/usr/sbin/sendmail -t");
						# Email Header
						print MAIL "To: @$row[2]\n";
						print MAIL "From: z5050807\@bitter.com\n";
						print MAIL "Subject: You are mentioned by $bleatID,please check\n\n";
						# Email Body
						print MAIL "Please check your bleat";
						close(MAIL);
					}
				}
			}
		}
		
		$sth = $dbh -> prepare("SELECT * FROM User WHERE username = (SELECT username FROM Bleats WHERE bleatID = '$replyToBleat')");
   		$sth->execute();	
		$row = $sth->fetchrow_arrayref();

		if(@$row[9] eq "2") {
			open(MAIL, "|/usr/sbin/sendmail -t");
			# Email Header
			print MAIL "To: @$row[2]\n";
			print MAIL "From: z5050807\@bitter.com\n";
			print MAIL "Subject: Someone replied you to your bleat\n\n";
			# Email Body
			print MAIL "$currentUser replies you, please check";
			close(MAIL);
		}
		if($image1){
			uploadImage("$bleatID","1",$image1);
		}
		if($image2){
			uploadImage("$bleatID","2",$image2);
		}
		if($image3){
			uploadImage("$bleatID","3",$image3);
		}
		if($image4){
			uploadImage("$bleatID","4",$image4);
		}					
			
	}
}

sub search_bleat_page{
    my $sth = $dbh -> prepare("SELECT * FROM Bleats WHERE bleat REGEXP '$bleatsearchstring|#$bleatsearchstring' ORDER BY time DESC");
    $sth->execute();
    my $row;
    my @resultBleats;
    my $pageString="";
    while($row = $sth->fetchrow_arrayref()){
	my $name=@$row[1];
    	my $bleat=@$row[5];
    	my $time=@$row[4];
    	my $latitude=@$row[2];
    	my $longitude=@$row[3];
    	my $in_reply_to=@$row[6];
	my $bleatID = @$row[0];

	push @resultBleats,"$name | $bleat | $time | $latitude | $longitude | $in_reply_to | $bleatID";	

    }
    
        #add pagination here
    my $usrNumber = @resultBleats;

    my @displayedBleats;
    my $maximumPage = ceil($usrNumber/$viewingElements);
    if($pageIndex<$maximumPage){
	for(my $i=0;$i<$viewingElements;$i++){
		my $var = $i+$viewingElements*($pageIndex-1);
		push @displayedBleats,"$resultBleats[$i+$viewingElements*($pageIndex-1)]";
	}
    }
    if($pageIndex==$maximumPage){
	for(my $i=0;$i<($usrNumber-($maximumPage-1)*$viewingElements);$i++){
		my $var = $i+$viewingElements*($pageIndex-1);
		push @displayedBleats,"$resultBleats[$i+$viewingElements*($pageIndex-1)]";
	}
    }
    my $next="";
    my $previous="";
    my $nextpage=$pageIndex+1;
    my $previouspage=$pageIndex-1;
    if($pageIndex=="1"){
	$next = "<a href=\"main.cgi?bleatSearch=$bleatSearch&userinfo=$currentUser&pagenum=$nextpage&bleatsub=$bleatsearchstring\">nextpage</a> <br>\n";
    }elsif($pageIndex>"1" and $pageIndex<$maximumPage){
	$next = "<a href=\"main.cgi?bleatSearch=$bleatSearch&userinfo=$currentUser&pagenum=$nextpage&bleatsub=$bleatsearchstring\">nextpage</a> <br>\n";
	$previous = "<a href=\"main.cgi?bleatSearch=$bleatSearch&userinfo=$currentUser&pagenum=$previouspage&bleatsub=$bleatsearchstring\">previouspage</a> <br>\n";
    }elsif($pageIndex==$maximumPage){
	$previous = "<a href=\"main.cgi?bleatSearch=$bleatSearch&userinfo=$currentUser&pagenum=$previouspage&bleatsub=$bleatsearchstring\">previouspage</a> <br>\n";
    }
    #endOfPagination

    foreach $bleatInfo (@displayedBleats){
	my @bleatInformation = split(/ \| /,$bleatInfo);	
	my $name=$bleatInformation[0];
	my $bleat=$bleatInformation[1];
	my $time=$bleatInformation[2];
	my $latitude=$bleatInformation[3];
	my $longitude=$bleatInformation[4];
	my $in_reply_to=$bleatInformation[5];
	my $bleatID=$bleatInformation[6];
	$pageString="$pageString <div class=\"jumbotron\">\n";	
	$pageString="$pageString <table>\n";
	$pageString="$pageString <tr>\n";
	$pageString="$pageString <td>Name:<a href=\"main.cgi?visit=$name&userinfo=$currentUser\">$name</a></td>\n";
	$pageString="$pageString </tr>\n";
	$pageString="$pageString <tr>\n";
	# MARK USELESS
	$pageString="$pageString <td>Bleat: <a href=\"main.cgi?&userinfo=$currentUser&bleatId=$bleatID&visit=$name\">$bleat</a></td>\n";
	$pageString="$pageString </tr>\n";
	$pageString="$pageString <tr>\n";
	$pageString="$pageString <td>Time:$time latitude:$latitude longitude:$longitude</td>\n";
	$pageString="$pageString </tr>\n";
	if($in_reply_to){
		$pageString="$pageString <tr>\n";
		$pageString="$pageString <td>in_rely_to: $in_reply_to</td>\n";
		$pageString="$pageString </tr>\n";
	}
	$pageString="$pageString </table>\n";
	$pageString="$pageString </div>";
    }




    return <<eof
<div class="allinfo">
<form method="POST" action="">
	<input type="hidden" name="userSearch" value="">
	<input type="hidden" name="userinfo" value="$currentUser">
	<input type="hidden" name="visit" value="$visitedUser">
	<input type="submit" value="Back to User" class="btn btn-primary" >
</form>
$pageString
$next
$previous
</div>
eof
}


sub bleatDetailPage{
	my $pageString="";
	my $sth = $dbh -> prepare("SELECT * FROM Bleats WHERE bleatID = '$visitingBleat'");
	$sth->execute();
	my $row = $sth->fetchrow_arrayref();
	my $bleatId = @$row[0];
	my $name=@$row[1];
    	my $bleat=@$row[5];
    	my $time=@$row[4];
    	my $latitude=@$row[2];
    	my $longitude=@$row[3];
    	my $in_reply_to=@$row[6];
	my $deleteForm = "";
	if($visitedUser eq $currentUser){
		$deleteForm = "<br><form method=\"POST\" action=\"\">
		<input type=\"hidden\" name=\"userinfo\" value=\"$currentUser\">
		<input type=\"hidden\" name=\"visit\" value=\"$visitedUser\">
		<input type=\"hidden\" name=\"bleatId\" value=\"$visitingBleat\">
		<input type=\"hidden\" name=\"deletebleat\" value=\"true\">
		<input type=\"submit\" value=\"Delete this bleat\" class=\"btn btn-primary\">
		</form>";
	}

#get replys
	my $reply = getReplyBleats($visitingBleat);
	my $url1 = "images/$visitingBleat"."image1.jpg";
	my $url2 = "images/$visitingBleat"."image2.jpg";
	my $url3 = "images/$visitingBleat"."image3.jpg";
	my $url4 = "images/$visitingBleat"."image4.jpg";
	$pageString="$pageString <div class=\"replying\">\n";
	$pageString="$pageString <div class=\"bleatinfo\">\n";
	$pageString="$pageString Name:<a href=\"main.cgi?visit=$name&userinfo=$currentUser\">$name</a><br>\n";
	$pageString="$pageString Bleat:$bleat\n";
	$pageString = "$pageString <div class=\"row\">\n
			<div class=\"col-md-3\"><img src=\"$url1\" alt=\"\" style=\"width:128px;height:128px;\"></div>\n
			<div class=\"col-md-3\"><img src=\"$url2\" alt=\"\" style=\"width:128px;height:128px;\"></div>\n
			<div class=\"col-md-3\"><img src=\"$url3\" alt=\"\" style=\"width:128px;height:128px;\"></div>\n
			<div class=\"col-md-3\"><img src=\"$url4\" alt=\"\" style=\"width:128px;height:128px;\"></div>\n
			</div>"; 	
	$pageString="$pageString Time:$time latitude:$latitude longitude:$longitude<br>\n";


	if($in_reply_to){
		$pageString="$pageString in_rely_to: $in_reply_to<br>\n";
	}
	$pageString="$pageString <form method=\"POST\" action=\"\" enctype=\"multipart/form-data\">\n
	<input type=\"text\" name=\"replyBleat\" class=\"form-control\" id=\"inputDefault\">\n
			       Attach image1:<br><input type=\"file\" name=\"image1\">
			       Attach image2:<br><input type=\"file\" name=\"image2\">
			       Attach image3:<br><input type=\"file\" name=\"image3\">
			       Attach image4:<br><input type=\"file\" name=\"image4\">
	<input type=\"hidden\" name=\"replyto\" value=\"$bleatId\">\n
	<input type=\"hidden\" name=\"userinfo\" value=\"$currentUser\">\n
	<input type=\"hidden\" name=\"bleatId\" value=\"$visitingBleat\">
	<input type=\"hidden\" name=\"visit\" value=\"$visitedUser\">\n
	<input type=\"submit\" value=\"Reply\" class=\"btn btn-primary\"></form></div>$reply</div>\n$deleteForm";

	
	return <<eof
<form method="POST" action="">
	<input type="hidden" name="userSearch" value="">
	<input type="hidden" name="userinfo" value="$currentUser">
	<input type="hidden" name="visit" value="$visitedUser">
	<input type="submit" value="Back to User" class="btn btn-primary">
</form>
$pageString
eof
}


sub getReplyBleats {
    my ($bleatID) = @_;

    my $sth = $dbh -> prepare("SELECT * FROM Bleats WHERE in_reply_to = '$bleatID'");
    $sth ->execute();
    

    my $replies = "";
    my $succReplies = "";
    my @bleatIDs = ();
    my @names = ();
    my @latitudes = ();
    my @longitudes = ();
    my @times = ();
    my @bleatMessages = ();
    my @in_reply_to = ();
    while(my @row = $sth->fetchrow_array()){
	push @bleatIDs,"$row[0]";
	push @names,"$row[1]";
	push @latitudes,"$row[2]";
	push @longitudes,"$row[3]";
	push @times,"$row[4]";
	push @bleatMessages,"$row[5]";
	push @in_reply_to,"$row[6]";
    }    

    foreach my $index (0..$#bleatIDs) {

	my $in_reply_to = "";
	my $bleatID = $bleatIDs[$index];
	my $name = $names[$index];
	my $bleat = $bleatMessages[$index];
	my $time = $times[$index];
	my $latitude = $latitudes[$index];
	my $longitude = $longitudes[$index];
	my $in_reply_to = $in_reply_to[$index];
	my $url1 = "images/$bleatID"."image1.jpg";
	my $url2 = "images/$bleatID"."image2.jpg";
	my $url3 = "images/$bleatID"."image3.jpg";
	my $url4 = "images/$bleatID"."image4.jpg";

	$succReplies = getReplyBleats($bleatID);	

        $replies="$replies <div class=\"replying\">\n";
	$replies="$replies <div class=\"bleatinfo\">\n";
	$replies="$replies Name:<a href=\"main.cgi?visit=$name&userinfo=$currentUser\">$name</a><br>\n";
	$replies="$replies Bleat:$bleat\n";
	$replies = "$replies <div class=\"row\">\n
			<div class=\"col-md-3\"><img src=\"$url1\" alt=\"\" style=\"width:128px;height:128px;\"></div>\n
			<div class=\"col-md-3\"><img src=\"$url2\" alt=\"\" style=\"width:128px;height:128px;\"></div>\n
			<div class=\"col-md-3\"><img src=\"$url3\" alt=\"\" style=\"width:128px;height:128px;\"></div>\n
			<div class=\"col-md-3\"><img src=\"$url4\" alt=\"\" style=\"width:128px;height:128px;\"></div>\n
			</div>"; 
	$replies="$replies Time:$time latitude:$latitude longitude:$longitude<br>\n";	
	if($in_reply_to){
		$replies="$replies in_rely_to: $in_reply_to<br>\n";
	}
	$replies="$replies <form method=\"POST\" action=\"\" enctype=\"multipart/form-data\">\n
	<input type=\"text\" name=\"replyBleat\" class=\"form-control\" id=\"inputDefault\">\n
	<input type=\"hidden\" name=\"replyto\" value=\"$bleatID\">\n
	<input type=\"hidden\" name=\"userinfo\" value=\"$currentUser\">\n
	<input type=\"hidden\" name=\"visit\" value=\"$visitedUser\">\n
	<input type=\"hidden\" name=\"bleatId\" value=\"$bleatID\">
	Attach image1:<input type=\"file\" name=\"image1\">
	Attach image2:<input type=\"file\" name=\"image2\">
	Attach image3:<input type=\"file\" name=\"image3\">
	Attach image4:<input type=\"file\" name=\"image4\">
	<input type=\"submit\" value=\"Reply\"></form></div>$succReplies</div>\n";          
    }
    return $replies;
}

sub deleteBleat {
	my ($bleatID) = @_;
	my $sth = $dbh -> prepare("SELECT bleatID FROM Bleats WHERE in_reply_to = '$bleatID'");
	$sth->execute();
	my @bleatIDs = ();
	while(my @row = $sth->fetchrow_array()){
		push @bleatIDs,"$row[0]";
    	}
	$dbh->do("DELETE FROM Bleats WHERE bleatID='$bleatID'");
	$dbh->do("DELETE FROM Bleatmention WHERE bleatID='$bleatID'");
	$dbh->do("DELETE FROM Bleatkeyword WHERE bleatID='$bleatID'");
	my $url1 = "images/$bleatID" . "image1.jpg";
	my $url2 = "images/$bleatID" . "image2.jpg";
	my $url3 = "images/$bleatID" . "image3.jpg";
	my $url4 = "images/$bleatID" . "image4.jpg";
	if ( -e $url1){
		system("rm","$url1");
	}
	if ( -e $url2){
		system("rm","$url2");
	}
	if ( -e $url3){
		system("rm","$url3");
	}
	if ( -e $url4){
		system("rm","$url4");
	}
	#system("rm","images/$bleatID " . "image1.jpg");
	foreach my $subid (@bleatIDs){
		deleteBleat($subid);
	}    
}

sub uploadImage{
	my ($bleatID,$number,$image) = @_;
	my $imagesuffix = $image;
	$imagesuffix =~ s/.*\./\./;
	open(my $fh, '>' . "images/$bleatID" . "image$number" . "$imagesuffix"); 
   	while ($line = <$image>) {
       		 print $fh $line;
   	}
	close($fh);
	if($imagesuffix ne ".jpg"){
		system("convert", "images/$bleatID". "image$number" . "$imagesuffix", "images/$bleatID" . "image$number".".jpg");
		system("rm", "images/$bleatID" . "image$number" . "$imagesuffix");
	}
}


main();
