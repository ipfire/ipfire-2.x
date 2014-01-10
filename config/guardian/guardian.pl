#!/usr/bin/perl
# based on V 1.7 guardian enhanced for IPFire and snort 2.8
# Read the readme file for changes
#
# Enhanced for IPFire by IPFire Team
# Added Portscan detection for non syslog system
# Added SSH-Watch for SSH-Bruteforce Attacks
# An suppected IP will be blocked on all interfaces

$OS=`uname`;
chomp $OS;
print "OS shows $OS\n";

require 'getopts.pl';

&Getopts ('hc:d');
if (defined($opt_h)) {
	print "Guardian v1.7 \n";
	print "guardian.pl [-hd] <-c config>\n";
	print " -h  shows help\n";
	print " -d  run in debug mode (doesn't fork, output goes to STDOUT)\n";
	print " -c  specifiy a configuration file other than the default (/etc/guardian.conf)\n";
	exit;
}
&load_conf;
&sig_handler_setup;

print "My ip address and interface are: $hostipaddr $interface\n";

if ($hostipaddr !~ /\d+\.\d+\.\d+\.\d+/) {
	print "This ip address is bad : $hostipaddr\n";
	die "I need a good host ipaddress\n";
}

$networkaddr = $hostipaddr;
$networkaddr =~ s/\d+$/0/;
$gatewayaddr = `cat /var/ipfire/red/remote-ipaddress 2>/dev/null`;
$broadcastaddr = $hostipaddr;
$broadcastaddr =~ s/\d+$/255/;
&build_ignore_hash;

print "My gatewayaddess is: $gatewayaddr\n";

# This is the target hash. If a packet was destened to any of these, then the
# sender of that packet will get denied, unless it is on the ignore list..

%targethash = ( "$networkaddr" => 1,
	"$broadcastaddr" => 1,
	"0" => 1,	# This is what gets sent to &checkem if no
			# destination was found.
	"$hostipaddr" => 1);

&get_aliases;

%sshhash = ();

if ( -e $targetfile ) {
	&load_targetfile;
}

if (!defined($opt_d)) {
	print "Becoming a daemon..\n";
	&daemonize;
} else { print "Running in debug mode..\n"; }

open (ALERT, $alert_file) or die "can't open alert file: $alert_file: $!\n";
seek (ALERT, 0, 2); # set the position to EOF.
# this is the same as a tail -f :)
$counter=0;
open (ALERT2, "/var/log/messages" ) or die "can't open /var/log/messages: $!\n";
seek (ALERT2, 0, 2); # set the position to EOF.
# this is the same as a tail -f :)

for (;;) {
	sleep 1;
	if (seek(ALERT,0,1)){
		while (<ALERT>) {
			chop;
			if (defined($opt_d)) {
				print "$_\n";
			}
			if (/\[\*\*\]\s+(.*)\s+\[\*\*\]/){
				$type=$1;
			}
			if (/(\d+\.\d+\.\d+\.\d+):\d+ -\> (\d+\.\d+\.\d+\.\d+):\d+/) {
				&checkem ($1, $2, $type);
			}
			if (/(\d+\.\d+\.\d+\.\d+)+ -\> (\d+\.\d+\.\d+\.\d+)+/) {
				&checkem ($1, $2, $type);
			}
		}
	}

	sleep 1;
	if (seek(ALERT2,0,1)){
		while (<ALERT2>) {
			chop;
			if ($_=~/.*sshd.*Failed password for .* from.*/) {
				my @array=split(/ /,$_);
				my $temp = "";
				if ( $array[11] eq "port" ) {
					$temp = $array[10];
				} elsif ( $array[11] eq "from" ) {
					$temp = $array[12];
				} else {
					$temp = $array[11];
				}
				&checkssh ($temp, "possible SSH-Bruteforce Attack");}

			# This should catch Bruteforce Attacks with enabled preauth
			if ($_ =~ /.*sshd.*Received disconnect from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):.*\[preauth\]/) {
				&checkssh ($1, "possible SSH-Bruteforce Attack, failed preauth");}
			}
	}

# Run this stuff every 30 seconds..
	if ($counter == 30) {
		&remove_blocks; # This might get moved elsewhere, depending on how much load
				# it puts on the system..
		&check_log_name;
		$counter=0;
	} else {
		$counter=$counter+1;
	}
}

sub check_log_name {
	my ($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,
	$atime,$mtime,$ctime,$blksize,$blocks) = stat($alert_file);
	if ($size < $previous_size) {   # The filesize is smaller than last
		close (ALERT);               # we checked, so we need to reopen it
		open (ALERT, "$alert_file"); # This should still work in our main while
		$previous_size=$size;        # loop (I hope)
		write_log ("Log filename changed. Reopening $alert_file\n");
	} else {
		$previous_size=$size;
	}
}


sub checkem {
	my ($source, $dest,$type) = @_;
	my $flag=0;

	return 1 if ($source eq $hostipaddr);
	# this should prevent is from nuking ourselves

	return 1 if ($source eq $gatewayaddr); # or our gateway
	if ($ignore{$source} == 1) { # check our ignore list..
		&write_log("$source\t$type\n");
		&write_log("Ignoring attack because $source is in my ignore list\n");
		return 1;
	}

# if the offending packet was sent to us, the network, or the broadcast, then
	if ($targethash{$dest} == 1) {
		&ipchain ($source, $dest, $type);
	}
# you will see this if the destination was not in the $targethash, and the
# packet was not ignored before the target check..
	else {
		&write_log ("Odd.. source = $source, dest = $dest - No action done.\n");
		if (defined ($opt_d)) {
			foreach $key (keys %targethash) {
				&write_log ("targethash{$key} = $targethash{$key}\n");
			}
		}
	}
}

sub checkssh {
	my ($source,$type) = @_;
	my $flag=0;

	return 1 if ($source eq $hostipaddr);
	# this should prevent is from nuking ourselves

	return 1 if ($source eq $gatewayaddr); # or our gateway

	return 0 if ($sshhash{$source} > 4); # allready blocked

	if ( ($ignore{$source} == 1) ){
		&write_log("Ignoring attack because $source is in my ignore list\n");
		return 1;
	}

	if ($sshhash{$source} == 4 ) {
		&write_log ("source = $source, blocking for ssh attack.\n");
		&ipchain ($source, "", $type);
		$sshhash{$source} = $sshhash{$source}+1;
		return 0;
	}

	if ($sshhash{$source} eq "" ){
		$sshhash{$source} = 1;
		&write_log ("SSH Attack = $source, ssh count only $sshhash{$source} - No action done.\n");
		return 0;
	}

	$sshhash{$source} = $sshhash{$source}+1;
	&write_log ("SSH Attack = $source, ssh count only $sshhash{$source} - No action done.\n");
}

sub ipchain {
	my ($source, $dest, $type) = @_;
	&write_log ("$source\t$type\n");
	if ($hash{$source} eq "") {
		&write_log ("Running '$blockpath $source $interface'\n");
		system ("$blockpath $source $interface");
		$hash{$source} = time() + $TimeLimit;
	} else {
# We have already blocked this one, but snort detected another attack. So
# we should update the time blocked..
		$hash{$source} = time() + $TimeLimit;
	}
}

sub build_ignore_hash {
#  This would cause is to ignore all broadcasts if it
#  got set.. However if unset, then the attacker could spoof the packet to make
#  it look like it came from the network, and a reply to the spoofed packet
#  could be seen if the attacker were on the local network.
#  $ignore{$networkaddr}=1;

# same thing as above, just with the broadcast instead of the network.
#  $ignore{$broadcastaddr}=1;
	my $count =0;
	$ignore{$gatewayaddr}=1;
	$ignore{$hostipaddr}=1;
	if ($ignorefile ne "") {
		open (IGNORE, $ignorefile);
		while (<IGNORE>) {
			$_=~ s/\s+$//;
			chomp;
			next if (/\#/);  #skip comments
			next if (/^\s*$/); # and blank lines
			$ignore{$_}=1;
			$count++;
		}
		close (IGNORE);
		&write_log("Loaded $count addresses from $ignorefile\n");
	} else {
		&write_log("No ignore file was loaded!\n");
	}
}

sub load_conf {
	if ($opt_c eq "") {
		$opt_c = "/etc/guardian.conf";
	}

	if (! -e $opt_c) {
		die "Need a configuration file.. please use to the -c option to name a configuration file\n";
	}

	open (CONF, $opt_c) or die "Cannot read the config file $opt_c, $!\n";
	while (<CONF>) {
		chop;
		next if (/^\s*$/); #skip blank lines
		next if (/^#/); # skip comment lines
		if (/LogFile\s+(.*)/) {
			$logfile = $1;
		}
		if (/Interface\s+(.*)/) {
			$interface = $1;
			if ( $interface eq "" ) {
				$interface = `cat /var/ipfire/ethernet/settings | grep RED_DEV | cut -d"=" -f2`;
			}
		}
		if (/AlertFile\s+(.*)/) {
			$alert_file = $1;
		}
		if (/IgnoreFile\s+(.*)/) {
			$ignorefile = $1;
		}
		if (/TargetFile\s+(.*)/) {
			$targetfile = $1;
		}
		if (/TimeLimit\s+(.*)/) {
			$TimeLimit = $1;
		}
		if (/HostIpAddr\s+(.*)/) {
			$hostipaddr = $1;
		}
		if (/HostGatewayByte\s+(.*)/) {
			$hostgatewaybyte = $1;
		}
	}

	if ($alert_file eq "") {
		print "Warning! AlertFile is undefined.. Assuming /var/log/snort.alert\n";
		$alert_file="/var/log/snort.alert";
	}
	if ($hostipaddr eq "") {
		print "Warning! HostIpAddr is undefined! Attempting to guess..\n";
		$hostipaddr = `cat /var/ipfire/red/local-ipaddress`;
		print "Got it.. your HostIpAddr is $hostipaddr\n";
	}
	if ($ignorefile eq "") {
		print "Warning! IgnoreFile is undefined.. going with default ignore list (hostname and gateway)!\n";
	}
	if ($hostgatewaybyte eq "") {
		print "Warning! HostGatewayByte is undefined.. gateway will not be in ignore list!\n";
	}
	if ($logfile eq "") {
		print "Warning! LogFile is undefined.. Assuming debug mode, output to STDOUT\n";
		$opt_d = 1;
	}
	if (! -w $logfile) {
		print "Warning! Logfile is not writeable! Engaging debug mode, output to STDOUT\n";
		$opt_d = 1;
	}

	foreach $mypath (split (/:/, $ENV{PATH})) {
		if (-x "$mypath/guardian_block.sh") {
		$blockpath = "$mypath/guardian_block.sh";
		}
		if (-x "$mypath/guardian_unblock.sh") {
		$unblockpath = "$mypath/guardian_unblock.sh";
		}
	}

	if ($blockpath eq "") {
		print "Error! Could not find guardian_block.sh. Please consult the README. \n";
		exit;
	}
	if ($unblockpath eq "") {
		print "Warning! Could not find guardian_unblock.sh. Guardian will not be\n";
		print "able to remove blocked ip addresses. Please consult the README file\n";
	}
	if ($TimeLimit eq "") {
		print "Warning! Time limit not defined. Defaulting to absurdly long time limit\n";
		$TimeLimit = 999999999;
	}
}

sub write_log {
	my $message = $_[0];
	my $date = localtime();
	if (defined($opt_d)) {  # we are in debug mode, and not daemonized
		print STDOUT $message;
	} else {
		open (LOG, ">>$logfile");
		print LOG $date.": ".$message;
		close (LOG);
	}
}

sub daemonize {
	my ($home);
 	if (fork()) {
# parent
		exit(0);
	} else {
# child
		&write_log ("Guardian process id $$\n");
		$home = (getpwuid($>))[7] || die "No home directory!\n";
		chdir($home);                   # go to my homedir
		setpgrp(0,0);                   # become process leader
		close(STDOUT);
		close(STDIN);
		close(STDERR);
		print "Testing...\n";
	}
}

sub sig_handler_setup {
	$SIG{INT} = \&clean_up_and_exit; # kill -2
	$SIG{TERM} = \&clean_up_and_exit; # kill -9
	$SIG{QUIT} = \&clean_up_and_exit; # kill -3
#  $SIG{HUP} = \&flush_and_reload; # kill -1
}

sub remove_blocks {
	my $source;
	my $time = time();
	foreach $source (keys %hash) {
		if ($hash{$source} < $time) {
			&call_unblock ($source, "expiring block of $source\n");
			delete ($hash{$source});
		}
	}
}

sub call_unblock {
	my ($source, $message) = @_;
	&write_log ("$message");
	system ("$unblockpath $source $interface");
}

sub clean_up_and_exit {
	my $source;
	&write_log ("received kill sig.. shutting down\n");
	foreach $source (keys %hash) {
		&call_unblock ($source, "removing $source for shutdown\n");
	}
	exit;
}

sub load_targetfile {
	my $count = 0;
	open (TARG, "$targetfile") or die "Cannot open $targetfile\n";
	while (<TARG>) {
		chop;
		next if (/\#/);  #skip comments
		next if (/^\s*$/); # and blank lines
		$targethash{$_}=1;
		$count++;
	}
	close (TARG);
	print "Loaded $count addresses from $targetfile\n";
}

sub get_aliases {
	my $ip;
	print "Scanning for aliases on $interface and add them to the target hash...";

	open (IFCONFIG, "/sbin/ip addr show $interface |");
	my @lines = <IFCONFIG>;
	close(IFCONFIG);

	foreach $line (@lines) {
		if ( $line =~ /inet (\d+\.\d+\.\d+\.\d+)/) {
			$ip = $1;
			print " got $ip on $interface ... ";
			$targethash{'$ip'} = "1";
		}
	}

	print "done \n";
}
