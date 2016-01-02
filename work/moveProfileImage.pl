#!/usr/bin/perl -w

use File::Copy qw(copy);

foreach $dir (glob "dataset-medium/users/*") {

	my $userName = $dir;
	$userName =~ s/^.*\///;

	open(my $old_file, '<' . $dir . "/profile.jpg") or next;
	@lines = <$old_file>;
	
	open(my $new_file, ">images/" . $userName . "profile.jpg") or print "sth";
    	foreach $line (@lines) {
		print $new_file $line;
	}
	close($old_file);
	close($new_file);

}

