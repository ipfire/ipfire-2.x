# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
# Copyright (C) 2002 Alex Hudson - getcgihash() rewrite
# Copyright (C) 2002 Bob Grant <bob@cache.ucr.edu> - validmac()
# Copyright (c) 2002/04/13 Steve Bootes - add alias section, helper functions
# Copyright (c) 2002/08/23 Mark Wormgoor <mark@wormgoor.com> validfqdn()
# Copyright (c) 2003/09/11 Darren Critchley <darrenc@telus.net> srtarray()
#
# $Id: general-functions.pl,v 1.1.2.26 2006/01/04 16:33:55 franck78 Exp $
#

package General;

use strict;
use Socket;
use IO::Socket;
use Net::IPv4Addr qw(:all);

$General::version = 'VERSION';
$General::swroot = 'CONFIG_ROOT';
$General::noipprefix = 'noipg-';

require "${General::swroot}/network-functions.pl";
require "${General::swroot}/wireguard-functions.pl";

# Load the main settings file
our %mainsettings = ();
&readhash("${General::swroot}/main/settings", \%mainsettings);

# This function executes a shell command without forking a shell or do any other
# Perl-voodoo before it. It deprecates the "system" command and is the only way
# to call shell commands.
sub safe_system($) {
	my @command = @_;

	system { ${command[0]} } @command;

	# Return exit code
	return $? >> 8;
}

# Calls a process in the background and returns nothing
sub system_background($) {
	my $pid = fork();

	unless ($pid) {
		my $rc = &system(@_);
		exit($rc);
	}

	return 0;
}

# Returns the output of a shell command
sub system_output($) {
	my @command = @_;
	my $pid;
	my @output = ();

	unless ($pid = open(OUTPUT, "-|")) {
		open(STDERR, ">&STDOUT");
		exec { ${command[0]} } @command;
		die "Could not execute @command: $!";
	}

	waitpid($pid, 0);

	while (<OUTPUT>) {
		push(@output, $_);
	}
	close(OUTPUT);

	return @output;
}

# Calls a shell command and throws away the output
sub system($) {
	my @command = @_;

	open(SAVEOUT, ">&STDOUT");
	open(SAVEERR, ">&STDERR");

	open(STDOUT, ">/dev/null");
	open(STDERR, ">&STDOUT");

	select(STDERR); $|=1;
	select(STDOUT); $|=1;

	my $rc = &safe_system(@command);

	close(STDOUT);
	close(STDERR);

	# Restore
	open(STDOUT, ">&SAVEOUT");
	open(STDERR, ">&SAVEERR");

	return $rc;
}

sub read_pids($) {
	my $pidfile = shift;

	# Open the PID file
	open(PIDFILE, "<${pidfile}");

	# Store all PIDs here
	my @pids = ();

	# Read all PIDs
	while (<PIDFILE>) {
		chomp $_;

		if (-d "/proc/$_") {
			push(@pids, $_);
		}
	}

	# Close the PID file
	close(PIDFILE);

	return @pids;
}

sub find_pids($) {
	my $process = shift;

	# Store all PIDs here
	my @pids = ();

	foreach my $status (</proc/*/status>) {
		# Open the status file
		open(STATUS, "<${status}");

		# Read the status file
		while (<STATUS>) {
			# If the name does not match, we break the loop immediately
			if ($_ =~ m/^Name:\s+(.*)$/) {
				last if ($process ne $1);

			# Push the PID onto the list
			} elsif ($_ =~ m/^Pid:\s+(\d+)$/) {
				push(@pids, $1);

				# Once we got here, we are done
				last;
			}
		}

		# Close the status file
		close(STATUS);
	}

	return @pids;
}

sub get_memory_consumption() {
	my $memory = 0;

	foreach my $pid (@_) {
		# Open the status file or skip on error
		open(STATUS, "/proc/${pid}/status") or next;

		while (<STATUS>) {
			if ($_ =~ m/^VmRSS:\s+(\d+) kB/) {
				$memory += $1 * 1024;
				last;
			}
		}

		close(STATUS);
	}

	return $memory;
}

# Function to remove duplicates from an array
sub uniq { my %seen; grep !$seen{$_}++, @_ }

#
# log ("message") use default 'ipcop' tag
# log ("tag","message") use your tag
#
sub log
{
	my $tag='ipfire';
	$tag = shift if (@_>1);
	my $logmessage = $_[0];
	$logmessage =~ /([\w\W]*)/;
	$logmessage = $1;
	&system('logger', '-t', $tag, $logmessage);
}
sub setup_default_networks
{
	my %netsettings = %Network::ethernet;
	my $defaultNetworks = shift;

	# Get current defined networks (Red, Green, Blue, Orange)
	$defaultNetworks->{$Lang::tr{'fwhost any'}}{'IPT'} = "0.0.0.0/0.0.0.0";
	$defaultNetworks->{$Lang::tr{'fwhost any'}}{'NAME'} = "ALL";

	$defaultNetworks->{$Lang::tr{'green'}}{'IPT'} = "$netsettings{'GREEN_NETADDRESS'}/$netsettings{'GREEN_NETMASK'}";
	$defaultNetworks->{$Lang::tr{'green'}}{'NET'} = "$netsettings{'GREEN_ADDRESS'}";
	$defaultNetworks->{$Lang::tr{'green'}}{'NAME'} = "GREEN";

	if ($netsettings{'RED_DEV'} ne ''){
		$defaultNetworks->{$Lang::tr{'fwdfw red'}}{'IPT'} = "$netsettings{'RED_NETADDRESS'}/$netsettings{'RED_NETMASK'}";
		$defaultNetworks->{$Lang::tr{'fwdfw red'}}{'NET'} = "$netsettings{'RED_ADDRESS'}";
		$defaultNetworks->{$Lang::tr{'fwdfw red'}}{'NAME'} = "RED";
	}
	if ($netsettings{'ORANGE_DEV'} ne ''){
		$defaultNetworks->{$Lang::tr{'orange'}}{'IPT'} = "$netsettings{'ORANGE_NETADDRESS'}/$netsettings{'ORANGE_NETMASK'}";
		$defaultNetworks->{$Lang::tr{'orange'}}{'NET'} = "$netsettings{'ORANGE_ADDRESS'}";
		$defaultNetworks->{$Lang::tr{'orange'}}{'NAME'} = "ORANGE";
	}

	if ($netsettings{'BLUE_DEV'} ne ''){
		$defaultNetworks->{$Lang::tr{'blue'}}{'IPT'} = "$netsettings{'BLUE_NETADDRESS'}/$netsettings{'BLUE_NETMASK'}";
		$defaultNetworks->{$Lang::tr{'blue'}}{'NET'} = "$netsettings{'BLUE_ADDRESS'}";
		$defaultNetworks->{$Lang::tr{'blue'}}{'NAME'} = "BLUE";
	}

	#IPFire himself
	$defaultNetworks->{'IPFire'}{'NAME'} = "IPFire";

	# OpenVPN
	if(-e "${General::swroot}/ovpn/settings")
	{
		my %ovpnSettings = ();
		&readhash("${General::swroot}/ovpn/settings", \%ovpnSettings);

		# OpenVPN on Red?
		if(defined($ovpnSettings{'DOVPN_SUBNET'}))
		{
			my ($ip,$sub) = split(/\//,$ovpnSettings{'DOVPN_SUBNET'});
			$sub=&General::iporsubtocidr($sub);
			my @tempovpnsubnet = split("\/", $ovpnSettings{'DOVPN_SUBNET'});
			$defaultNetworks->{'OpenVPN ' ."($ip/$sub)"}{'ADR'} = $tempovpnsubnet[0];
			$defaultNetworks->{'OpenVPN ' ."($ip/$sub)"}{'NAME'} = "OpenVPN-Dyn";
		}
	} # end OpenVPN
	# IPsec RW NET
	if(-e "${General::swroot}/vpn/settings")
	{
		my %ipsecsettings = ();
		&readhash("${General::swroot}/vpn/settings", \%ipsecsettings);
		if($ipsecsettings{'RW_NET'} ne '')
		{
			my $netaddress = &Network::get_netaddress($ipsecsettings{'RW_NET'});
			my $prefix     = &Network::get_prefix($ipsecsettings{'RW_NET'});

			$defaultNetworks->{"IPsec RW (${netaddress}/${prefix})"}{'ADR'}  = $netaddress;
			$defaultNetworks->{"IPsec RW (${netaddress}/${prefix})"}{'NAME'} = "IPsec RW";
			$defaultNetworks->{"IPsec RW (${netaddress}/${prefix})"}{'NET'}  = $netaddress;
		}
	}

	# WireGuard
	if ($Wireguard::settings{'CLIENT_POOL'}) {
		my $name = $Lang::tr{'wg rw peers'};

		$defaultNetworks->{$name}{'NAME'} = "WGRW";
	}
}
sub get_aliases
{

	my $defaultNetworks = shift;
	open(FILE, "${General::swroot}/ethernet/aliases") or die 'Unable to open aliases file.';
	my @current = <FILE>;
	close(FILE);
	my $ctr = 0;
	foreach my $line (@current)
	{
		if ($line ne ''){
			chomp($line);
			my @temp = split(/\,/,$line);
			if ($temp[2] eq '') {
				$temp[2] = "Alias $ctr : $temp[0]";
			}
			$defaultNetworks->{$temp[2]}{'IPT'} = "$temp[0]";
			$defaultNetworks->{$temp[2]}{'NET'} = "$temp[0]";

			$ctr++;
		}
	}
}

sub set_defaults($$) {
	my $hash = shift;
	my $defaults = shift;

	foreach my $key (keys %$defaults) {
		unless (defined($hash->{$key})) {
			$hash->{$key} = $defaults->{$key};
		}
	}
}

sub readhash
{
	my $filename = $_[0];
	my $hash = $_[1];
	my ($var, $val);


	# Some ipcop code expects that readhash 'complete' the hash if new entries
	# are presents. Not clear it !!!
	#%$hash = ();

	open(FILE, $filename) or die "Unable to read file $filename";

	while (<FILE>)
	{
		chop;

		# Skip comments.
		next if ($_ =~ /^#/);

		($var, $val) = split /=/, $_, 2;
		if ($var)
		{
			$val =~ s/^\'//g;
			$val =~ s/\'$//g;

			# Untaint variables read from hash
			# trim space from begin and end
			$var =~ s/^\s+//;
			$var =~ s/\s+$//;
			$var =~ /([A-Za-z0-9_-]*)/;
			$var = $1;
			$val =~ /([\w\W]*)/;
			$val = $1;
			$hash->{$var} = $val;
		}
	}
	close FILE;
}


sub writehash
{
	my $filename = $_[0];
	my $hash = $_[1];
	my ($var, $val);

	# write cgi vars to the file.
	open(FILE, ">${filename}") or die "Unable to write file $filename";
	flock FILE, 2;
	foreach $var (keys %$hash)
	{
		if ( $var eq "__CGI__"){next;}
		$val = $hash->{$var};
		# Darren Critchley Jan 17, 2003 added the following because when submitting with a graphic, the x and y
		# location of the mouse are submitted as well, this was being written to the settings file causing
		# some serious grief! This skips the variable.x and variable.y
		if (!($var =~ /(.x|.y)$/)) {
			if ($val =~ / /) {
				$val = "\'$val\'"; }
			if (!($var =~ /^ACTION/)) {
				print FILE "${var}=${val}\n"; }
		}
	}
	close FILE;
}

sub age {
	my ($dev, $ino, $mode, $nlink, $uid, $gid, $rdev, $size,
		$atime, $mtime, $ctime, $blksize, $blocks) = stat $_[0];
	my $t = time() - $mtime;

	return &format_time($t);
}

sub format_time($) {
	my $totalsecs = shift;
	my @s = ();

	my $secs = $totalsecs % 60;
	$totalsecs /= 60;
	if ($secs > 0) {
		push(@s, "${secs}s");
	}

	my $min = $totalsecs % 60;
	$totalsecs /= 60;
	if ($min > 0) {
		push(@s, "${min}m");
	}

	my $hrs = $totalsecs % 24;
	$totalsecs /= 24;
	if ($hrs > 0) {
		push(@s, "${hrs}h");
	}

	my $days = int($totalsecs);
	if ($days > 0) {
		push(@s, "${days}d");
	}

	return join(" ", reverse(@s));
}

sub validip
{
	my $ip = $_[0];

	if (!($ip =~ /^(\d+)\.(\d+)\.(\d+)\.(\d+)$/)) {
		return 0; }
	else
	{
		my @octets = ($1, $2, $3, $4);
		foreach $_ (@octets)
		{
			if (/^0./) {
				return 0; }
			if ($_ < 0 || $_ > 255) {
				return 0; }
		}
		return 1;
	}
}

sub validmask {
	my $mask = shift;

	return &Network::check_netmask($mask) || &Network::check_prefix($mask);
}

sub validipormask
{
	my $ipormask = $_[0];

	# see if it is a IP only.
	if (&validip($ipormask)) {
		return 1; }
	# split it into number and mask.
	if (!($ipormask =~ /^(.*?)\/(.*?)$/)) {
		return 0; }
	my $ip = $1;
	my $mask = $2;
	# first part not a ip?
	if (!(&validip($ip))) {
		return 0; }
	return &validmask($mask);
}

sub subtocidr {
	return &Network::convert_netmask2prefix(shift);
}

sub cidrtosub {
	return &Network::convert_prefix2netmask(shift);
}

sub iporsubtodec
{
	#Gets: Ip address or subnetmask in decimal oder CIDR
	#Gives: What it gets only in CIDR format
	my $subnet=$_[0];
	my $net;
	my $mask;
	my $full=0;
	if ($subnet =~ /^(.*?)\/(.*?)$/) {
		($net,$mask) = split (/\//,$subnet);
		$full=1;
		return "$subnet";
	}else{
		$mask=$subnet;
	}
	#Subnet already in decimal and valid?
	if ($mask=~/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/ &&(($1<=255  && $2<=$1 && $3<=$2  && $4<=$3 )))	{
		for (my $i=0;$i<=32;$i++){
			if (&General::cidrtosub($i) eq $mask){
				if ($full == 0){return $mask;}else{
							 return $net."/".$mask;
				}
			}
		}
	}
	#Subnet in binary format?
	if ($mask=~/^(\d{1,2})$/ && (($1<=32 && $1>=0))){
			if($full == 0){ return &General::cidrtosub($mask);}else{
						 return $net."/".&General::cidrtosub($mask);
			}
	}else{
			return 3;
	}
	return 3;
}


sub iporsubtocidr
{
	#gets: Ip Address  or subnetmask in decimal oder CIDR
	#Gives: What it gets only in CIDR format
	my $subnet=$_[0];
	my $net;
	my $mask;
	my $full=0;
	if ($subnet =~ /^(.*?)\/(.*?)$/) {
		($net,$mask) = split (/\//,$subnet);
		$full=1;
	}else{
		$mask=$subnet;
	}
	#Subnet in decimal and valid?
	if ($mask=~/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/ &&(($1<=255  && $2<=$1 && $3<=$2  && $4<=$3 )))	{
		for (my $i=0;$i<=32;$i++){
			if (&General::cidrtosub($i) eq $mask){
				if ($full == 0){return &General::subtocidr($mask);}else{
							 return $net."/".&General::subtocidr($mask);
				}
			}
		}
	}
	#Subnet already in binary format?
	if ($mask=~/^(\d{1,2})$/ && (($1<=32 && $1>=0))){
			if($full == 0){ return $mask;}else{
						 return $net."/".$mask;
			}
	}else{
			return 3;
	}
	return 3;
}

sub getnetworkip {
	my $arg = join("/", @_);

	return &Network::get_netaddress($arg);
}

sub ip2dec  {
	return &Network::ip2bin(shift);
}

sub dec2ip  {
	return &Network::bin2ip(shift);
}

sub validipandmask
{
	#Gets: Ip address in 192.168.0.0/24 or 192.168.0.0/255.255.255.0 and checks if subnet valid
	#Gives: True bzw 0 if success or false
	my $ccdnet=$_[0];
	my $subcidr;

	if (!($ccdnet =~ /^(.*?)\/(.*?)$/)) {
		return 0;
	}
	my ($ccdip,$ccdsubnet)=split (/\//, $ccdnet);
	#IP valid?
	if ($ccdip=~/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/ &&(($1>0 && $1<=255 && $2>=0 && $2<=255 && $3>=0 && $3<=255 && $4<=255 ))) {
		#Subnet in decimal and valid?
		if ($ccdsubnet=~/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/ &&(($1<=255  && $2<=$1 && $3<=$2  && $4<=$3 )))	{
			for (my $i=0;$i<=32;$i++){
				if (&General::cidrtosub($i) eq $ccdsubnet){
					return 1;
				}
			}
		#Subnet already in binary format?
		}elsif ($ccdsubnet=~/^(\d{1,2})$/ && (($1<=32 && $1>=0))){
			return 1;
		}else{
			return 0;
		}

	}
	return 0;
}

sub checksubnets
{
	my %ccdconfhash=();
	my %ovpnconfhash=();
	my %vpnconf=();
	my %ipsecconf=();
	my %ownnet=();
	my %ovpnconf=();
	my @ccdconf=();
	my $ccdname=$_[0];
	my $ccdnet=$_[1];
	my $ownnet=$_[2];
	my $checktype=$_[3];
	my $errormessage;
	my ($ip,$cidr)=split(/\//,$ccdnet);
	$cidr=&iporsubtocidr($cidr);

	#get OVPN-Subnet (dynamic range)
	&readhash("${General::swroot}/ovpn/settings", \%ovpnconf);
	my ($ovpnip,$ovpncidr)= split (/\//,$ovpnconf{'DOVPN_SUBNET'});
	$ovpncidr=&iporsubtocidr($ovpncidr);

	#check if we try to use same network as ovpn server
	if ("$ip/$cidr" eq "$ovpnip/$ovpncidr") {
			$errormessage=$errormessage.$Lang::tr{'ccd err isovpnnet'}."<br>";
			return $errormessage;
	}

	#check if we try to use same network as another ovpn N2N
	if($ownnet ne 'ovpn'){
		&readhasharray("${General::swroot}/ovpn/ovpnconfig", \%ovpnconfhash);
		foreach my $key (keys %ovpnconfhash) {
			if ($ovpnconfhash{$key}[3] eq 'net'){
				my @ovpnnet=split (/\//,$ovpnconfhash{$key}[11]);
				if (&IpInSubnet($ip,$ovpnnet[0],&iporsubtodec($ovpnnet[1]))){
					$errormessage=$errormessage.$Lang::tr{'ccd err isovpnn2n'}." $ovpnconfhash{$key}[1] <br>";
					return $errormessage;
				}
			}
		}
	}

	#check if we use a network-name/subnet (static-ovpn) that already exists
	&readhasharray("${General::swroot}/ovpn/ccd.conf", \%ccdconfhash);
	foreach my $key (keys %ccdconfhash) {
		@ccdconf=split(/\//,$ccdconfhash{$key}[1]);
		if ($ccdname eq $ccdconfhash{$key}[0])
		{
			$errormessage=$errormessage.$Lang::tr{'ccd err nameexist'}."<br>";
			return $errormessage;
		}
		my ($newip,$newsub) = split(/\//,$ccdnet);
		if (&IpInSubnet($newip,$ccdconf[0],&iporsubtodec($ccdconf[1])))
		{
			$errormessage=$errormessage.$Lang::tr{'ccd err issubnet'}." $ccdconfhash{$key}[0]<br>";
			return $errormessage;
		}
	}

	#check if we use a ipsec right network which is already defined
	if($ownnet ne 'ipsec'){
		&General::readhasharray("${General::swroot}/vpn/config", \%ipsecconf);
		foreach my $key (keys %ipsecconf){
			if ($ipsecconf{$key}[11] ne '' && $ipsecconf{$key}[36] eq ""){
				foreach my $ipsecsubitem (split(/\|/, $ipsecconf{$key}[11])) {
					my ($ipsecip,$ipsecsub) = split (/\//, $ipsecsubitem);
					$ipsecsub=&iporsubtodec($ipsecsub);
					if($ipsecconf{$key}[1] ne $ccdname){
						if ( &IpInSubnet ($ip,$ipsecip,$ipsecsub) ){
							$errormessage=$Lang::tr{'ccd err isipsecnet'}." Name:  $ipsecconf{$key}[1]";
							return $errormessage;
						}
					}
				}
			}
		}
	}

	#check if we use the ipsec RW Network (if defined)
	&readhash("${General::swroot}/vpn/settings", \%vpnconf);
	if ($vpnconf{'RW_NET'} ne ''){
		my ($ipsecrwnet,$ipsecrwsub)=split (/\//, $vpnconf{'RW_NET'});
		if (&IpInSubnet($ip,$ipsecrwnet,&iporsubtodec($ipsecrwsub)))
		{
			$errormessage=$errormessage.$Lang::tr{'ccd err isipsecrw'}."<br>";
			return $errormessage;
		}
	}

	#call check_net_internal
	if ($checktype eq "exact")
	{
		&General::check_net_internal_exact($ccdnet);
	}else{
		&General::check_net_internal_range($ccdnet);
	}
}

sub check_net_internal_range{
	my $network=shift;
	my ($ip,$cidr)=split(/\//,$network);
	my %ownnet = %Network::ethernet;
	my $errormessage;
	$cidr=&iporsubtocidr($cidr);
	#check if we use one of ipfire's networks (green,orange,blue)
	if (($ownnet{'GREEN_NETADDRESS'}  	ne '' && $ownnet{'GREEN_NETADDRESS'} 	ne '0.0.0.0') && &IpInSubnet($ip,$ownnet{'GREEN_NETADDRESS'},&iporsubtodec($ownnet{'GREEN_NETMASK'}))){ $errormessage=$Lang::tr{'ccd err green'};return $errormessage;}
	if (($ownnet{'ORANGE_NETADDRESS'}	ne '' && $ownnet{'ORANGE_NETADDRESS'} 	ne '0.0.0.0') && &IpInSubnet($ip,$ownnet{'ORANGE_NETADDRESS'},&iporsubtodec($ownnet{'ORANGE_NETMASK'}))){ $errormessage=$Lang::tr{'ccd err orange'};return $errormessage;}
	if (($ownnet{'BLUE_NETADDRESS'} 	ne '' && $ownnet{'BLUE_NETADDRESS'} 	ne '0.0.0.0') && &IpInSubnet($ip,$ownnet{'BLUE_NETADDRESS'},&iporsubtodec($ownnet{'BLUE_NETMASK'}))){ $errormessage=$Lang::tr{'ccd err blue'};return $errormessage;}
	if (($ownnet{'RED_NETADDRESS'} 		ne '' && $ownnet{'RED_NETADDRESS'} 		ne '0.0.0.0') && &IpInSubnet($ip,$ownnet{'RED_NETADDRESS'},&iporsubtodec($ownnet{'RED_NETMASK'}))){ $errormessage=$Lang::tr{'ccd err red'};return $errormessage;}
}

sub check_net_internal_exact{
	my $network=shift;
	my ($ip,$cidr)=split(/\//,$network);
	my %ownnet = %Network::ethernet;
	my $errormessage;
	$cidr=&iporsubtocidr($cidr);
	#check if we use one of ipfire's networks (green,orange,blue)
	if (($ownnet{'GREEN_NETADDRESS'}  	ne '' && $ownnet{'GREEN_NETADDRESS'} 	ne '0.0.0.0') && &Network::network_equal("$ownnet{'GREEN_NETADDRESS'}/$ownnet{'GREEN_NETMASK'}", $network)){ $errormessage=$Lang::tr{'ccd err green'};return $errormessage;}
	if (($ownnet{'ORANGE_NETADDRESS'}	ne '' && $ownnet{'ORANGE_NETADDRESS'} 	ne '0.0.0.0') && &Network::network_equal("$ownnet{'ORANGE_NETADDRESS'}/$ownnet{'ORANGE_NETMASK'}", $network)){ $errormessage=$Lang::tr{'ccd err orange'};return $errormessage;}
	if (($ownnet{'BLUE_NETADDRESS'} 	ne '' && $ownnet{'BLUE_NETADDRESS'} 	ne '0.0.0.0') && &Network::network_equal("$ownnet{'BLUE_NETADDRESS'}/$ownnet{'BLUE_NETMASK'}", $network)){ $errormessage=$Lang::tr{'ccd err blue'};return $errormessage;}
	if (($ownnet{'RED_NETADDRESS'} 		ne '' && $ownnet{'RED_NETADDRESS'} 		ne '0.0.0.0') && &Network::network_equal("$ownnet{'RED_NETADDRESS'}/$ownnet{'RED_NETMASK'}", $network)){ $errormessage=$Lang::tr{'ccd err red'};return $errormessage;}
}

sub validport
{
	$_ = $_[0];

	if (!/^\d+$/) {
		return 0; }
	if (/^0./) {
		return 0; }
	if ($_ >= 1 && $_ <= 65535) {
		return 1; }
	return 0;
}

sub validproxyport
{
	$_ = $_[0];

	if (!/^\d+$/) {
		return 0; }
	if (/^0./) {
		return 0; }
	if ($_ == 53 || $_ == 222 || $_ == 444 || $_ == 81 ) {
		return 0; }
	elsif ($_ >= 1 && $_ <= 65535) {
		return 1; }
	return 0;
}

sub validmac
{
	my $checkmac = $_[0];
	my $ot = '[0-9a-f]{2}'; # 2 Hex digits (one octet)
	if ($checkmac !~ /^$ot:$ot:$ot:$ot:$ot:$ot$/i)
	{
		return 0;
	}
	return 1;
}

sub validhostname
{
	# Checks a hostname against RFC1035
        my $hostname = $_[0];

	# Hostname should be at least one character in length
	# but no more than 63 characters
	if (length ($hostname) < 1 || length ($hostname) > 63) {
		return 0;}
	# Only valid characters are a-z, A-Z, 0-9 and -
	if ($hostname !~ /^[a-zA-Z0-9-]*$/) {
		return 0;}
	# First character can only be a letter or a digit
	if (substr ($hostname, 0, 1) !~ /^[a-zA-Z0-9]*$/) {
		return 0;}
	# Last character can only be a letter or a digit
	if (substr ($hostname, -1, 1) !~ /^[a-zA-Z0-9]*$/) {
		return 0;}
	return 1;
}

sub validdomainname
{
	my $part;

	# Checks a domain name against RFC1035 and RFC2181
        my $domainname = $_[0];
	my @parts = split (/\./, $domainname);	# Split domain name at the '.'

	foreach $part (@parts) {
		# Each part should be at least one character in length
		# but no more than 63 characters
		if (length ($part) < 1 || length ($part) > 63) {
			return 0;}
		# Only valid characters are a-z, A-Z, 0-9, _ and -
		if ($part !~ /^[a-zA-Z0-9_-]*$/) {
			return 0;}
	}
	return 1;
}

sub validwildcarddomainname($) {
	my $domainname = shift;

	# Ignore any leading dots
	if ($domainname =~ m/^\*\.([^\*]*)\*?/) {
		$domainname = $1;
	}

	return &validdomainname($domainname);
}

sub validfqdn
{
	# Checks a fully qualified domain name against RFC1035 and RFC2181
        my $fqdn = $_[0];
	my @parts = split (/\./, $fqdn);	# Split FQDN at the '.'
	if (scalar(@parts) < 2) {		# At least two parts should
		return 0;}			# exist in a FQDN
						# (i.e.hostname.domain)

	for (my $index=0; $index < scalar(@parts); $index++) {
		# Each part should be at least one character in length
		# but no more than 63 characters
		if (length ($parts[$index]) < 1 || length ($parts[$index]) > 63) {
			return 0;}
		if ($index eq 0) {
			# This is the hostname part
			# Only valid characters are a-z, A-Z, 0-9 and -
			if ($parts[$index] !~ /^[a-zA-Z0-9-]*$/) {
				return 0;}
			# First character can only be a letter or a digit
			if (substr ($parts[$index], 0, 1) !~ /^[a-zA-Z0-9]*$/) {
				return 0;}
			# Last character can only be a letter or a digit
			if (substr ($parts[$index], -1, 1) !~ /^[a-zA-Z0-9]*$/) {
				return 0;}
		} else{
			# This is the domain part
			# Only valid characters are a-z, A-Z, 0-9, _ and -
			if ($parts[$index] !~ /^[a-zA-Z0-9_-]*$/) {
				return 0;}
		}
	}
	return 1;
}

sub validportrange # used to check a port range
{
	my $port = $_[0]; # port values
	$port =~ tr/-/:/; # replace all - with colons just in case someone used -
	my $srcdst = $_[1]; # is it a source or destination port

	if (!($port =~ /^(\d+)\:(\d+)$/)) {

		if (!(&validport($port))) {
			if ($srcdst eq 'src'){
				return $Lang::tr{'source port numbers'};
			} else 	{
				return $Lang::tr{'destination port numbers'};
			}
		}
	}
	else
	{
		my @ports = ($1, $2);
		if ($1 >= $2){
			if ($srcdst eq 'src'){
				return $Lang::tr{'bad source range'};
			} else 	{
				return $Lang::tr{'bad destination range'};
			}
		}
		foreach $_ (@ports)
		{
			if (!(&validport($_))) {
				if ($srcdst eq 'src'){
					return $Lang::tr{'source port numbers'};
				} else 	{
					return $Lang::tr{'destination port numbers'};
				}
			}
		}
		return;
	}
}

# Checks for a valid country code
sub validcc($) {
	my $cc = shift;

	# Must contain of exactly two uppercase characters, or must be A1, A2, or A3
	return ($cc =~ m/^([A-Z]{2}|A[123])$/);
}

sub IpInSubnet {
	my $addr = shift;
	my $network = shift;
	my $netmask = shift;

	return &Network::ip_address_in_network($addr, "$network/$netmask");
}

sub ipcidr {
	my ($ip,$cidr) = &Net::IPv4Addr::ipv4_parse(shift);
	return "$ip\/$cidr";
}

sub ipcidr2msk {
       my ($ip,$cidr) = &Net::IPv4Addr::ipv4_parse(shift);
       my $netmask = &Net::IPv4Addr::ipv4_cidr2msk($cidr);
       return "$ip\/$netmask";
}

sub validemail {
    my $address = shift;
    my @parts = split( /\@/, $address );
    my $count=@parts;

    #check if we have one part before and after '@'
    return 0 if ( $count != 2 );

    #check if one of the parts starts or ends with a dot
    return 0 if ( substr($parts[0],0,1) eq '.' );
    return 0 if ( substr($parts[0],-1,1) eq '.' );
    return 0 if ( substr($parts[1],0,1) eq '.' );
    return 0 if ( substr($parts[1],-1,1) eq '.' );

    #check first addresspart (before '@' sign)
    return 0 if  ( $parts[0] !~ m/^[a-zA-Z0-9\.!\-\_\+#]+$/ );

    #check second addresspart (after '@' sign)
    return 0 if  ( $parts[1] !~ m/^[a-zA-Z0-9\.\-]+$/ );

    return 1;
}

#
# Currently only vpnmain use this three procs (readhasharray, writehasharray, findhasharray)
# The 'key' used is numeric but is perfectly unneeded! This will to be removed so don't use
# this code. Vpnmain will be splitted in parts: x509/pki, connection ipsec, connection other,... .
#
sub readhasharray {
    my ($filename, $hash) = @_;
    %$hash = ();

    open(FILE, $filename) or die "Unable to read file $filename";

    while (<FILE>) {
	my ($key, $rest, @temp);
	chomp;
	($key, $rest) = split (/,/, $_, 2);
	if ($key =~ /^[0-9]+$/) {
	    @temp = split (/,/, $rest);
	    $hash->{$key} = \@temp;
        }
    }
    close FILE;
    return;
}

sub writehasharray {
    my ($filename, $hash) = @_;
    my ($key, @temp, $i);

    open(FILE, ">$filename") or die "Unable to write to file $filename";

    foreach $key (keys %$hash) {
		if ($key =~ /^[0-9]+$/) {
			print FILE "$key";
			foreach $i (0 .. $#{$hash->{$key}}) {
				print FILE ",$hash->{$key}[$i]";
			}
			print FILE "\n";
		}
    }
    close FILE;
    return;
}

sub findhasharraykey {
    foreach my $i (1 .. 1000000) {
	if ( ! exists $_[0]{$i}) {
	     return $i;
	}
    }
}

#
# Check if hostname.domain provided have IP provided
# use gethostbyname to verify that
# Params:
#	IP
#	hostname
#	domain
# Output
#	1 IP matches host.domain
#	0 not in sync
#
sub DyndnsServiceSync ($;$;$) {

    my ($ip,$hostName,$domain) = @_;
    my @addresses;

    #fix me no ip GROUP, what is the name ?
    $hostName =~ s/$General::noipprefix//;
    if ($hostName) { #may be empty
	$hostName = "$hostName.$domain";
	@addresses = gethostbyname($hostName);
    }

    if ($addresses[0] eq '') {		   	# nothing returned ?
	$hostName = $domain;   			# try resolving with domain only
        @addresses = gethostbyname($hostName);
    }

    if ($addresses[0] ne '') { 		   	# got something ?
	#&General::log("name:$addresses[0], alias:$addresses[1]");
	# Build clear text list of IP
	@addresses = map ( &Socket::inet_ntoa($_), @addresses[4..$#addresses]);
	if (grep (/$ip/, @addresses)) {
	    return 1;
	}
    }
    return 0;
}

# Translate ICMP code to text
# ref: http://www.iana.org/assignments/icmp-parameters
sub GetIcmpDescription ($) {
    my $index = shift;
    my @icmp_description = (
    'Echo Reply',			#0
    'Unassigned',
    'Unassigned',
    'Destination Unreachable',
    'Source Quench',
    'Redirect',
    'Alternate Host Address',
    'Unassigned',
    'Echo',
    'Router Advertisement',
    'Router Solicitation',		#10
    'Time Exceeded',
    'Parameter Problem',
    'Timestamp',
    'Timestamp Reply',
    'Information Request',
    'Information Reply',
    'Address Mask Request',
    'Address Mask Reply',
    'Reserved (for Security)',
    'Reserved (for Robustness Experiment)', #20
    'Reserved',
    'Reserved',
    'Reserved',
    'Reserved',
    'Reserved',
    'Reserved',
    'Reserved',
    'Reserved',
    'Reserved',
    'Traceroute',				#30
    'Datagram Conversion Error',
    'Mobile Host Redirect',
    'IPv6 Where-Are-You',
    'IPv6 I-Am-Here',
    'Mobile Registration Request',
    'Mobile Registration Reply',
    'Domain Name Request',
    'Domain Name Reply',
    'SKIP',
    'Photur',				#40
    'Experimental');
    if ($index>41) {return 'unknown'} else {return $icmp_description[$index]};
}

sub GetCoreUpdateVersion() {
	my $core_update;

	open(FILE, "/opt/pakfire/db/core/mine");
	while (<FILE>) {
		$core_update = $_;
		last;
	}
	close(FILE);

	return $core_update;
}

sub MakeUserAgent() {
	my $user_agent = "IPFire/$General::version";

	my $core_update = &GetCoreUpdateVersion();
	if ($core_update ne "") {
		$user_agent .= "/$core_update";
	}

	return $user_agent;
}

sub RedIsWireless() {
	# This function checks if a network device is a wireless device.

	# Find the name of the network device.
	my $device = $Network::ethernet{'RED_DEV'};

	# Exit, if no device is configured.
	return 0 if ($device eq "");

	# Return 1 if the device is a wireless one.
	my $path = "/sys/class/net/$device/wireless";
	if (-d $path) {
		return 1;
	}

	# Otherwise return zero.
	return 0;
}

# Function to read a file with UTF-8 charset.
sub read_file_utf8 ($) {
	my ($file) = @_;

	open my $in, '<:encoding(UTF-8)', $file or die "Could not open '$file' for reading $!";
	local $/ = undef;
	my $all = <$in>;
	close $in;

	return $all;
}

# Function to write a file with UTF-8 charset.
sub write_file_utf8 ($) {
	my ($file, $content) = @_;

	open my $out, '>:encoding(UTF-8)', $file or die "Could not open '$file' for writing $!";;
	print $out $content;
	close $out;

	return;
}

my $FIREWALL_RELOAD_INDICATOR = "${General::swroot}/firewall/reread";

sub firewall_config_changed() {
	open FILE, ">$FIREWALL_RELOAD_INDICATOR" or die "Could not open $FIREWALL_RELOAD_INDICATOR";
	close FILE;
}

sub firewall_needs_reload() {
	if (-e "$FIREWALL_RELOAD_INDICATOR") {
		return 1;
	}

	return 0;
}

sub firewall_reload() {
	&system("/usr/local/bin/firewallctrl");
}

# Function which will return the used interface for the red network zone (red0, ppp0, etc).
# if you change this also check speed.cgi that include a local copy for systemload reasons
sub get_red_interface() {
	my $interface;
	my $red_iface_file = "${General::swroot}/red/iface";

	if (-e $red_iface_file) {
		open(IFACE, "$red_iface_file") or die "Could not open $red_iface_file";
		$interface = <IFACE>;
		close(IFACE);
		chomp $interface;
	}

	return $interface;
}

sub number_cpu_cores() {
	open my $cpuinfo, "/proc/cpuinfo" or die "Can't open cpuinfo: $!\n";
	my $cores = scalar (map /^processor/, <$cpuinfo>);
	close $cpuinfo;

	return $cores;
}

# Tiny function to grab a single IP-address from a given file.
sub grab_address_from_file($) {
	my ($file) = @_;

	my $address;

	# Check if the given file exists.
	if(-f $file) {
		# Open the file for reading.
		open(FILE, $file) or die "Could not read from $file. $!\n";

		# Read the address from the file.
		$address = <FILE>;

		# Close filehandle.
		close(FILE);

		# Remove newlines.
		chomp($address);

		# Check if the obtained address is valid.
		if (&validip($address)) {
			# Return the address.
			return $address;
		}
	}

	# Return nothing.
	return;
}

# Function to get all configured and enabled nameservers.
sub get_nameservers () {
	my %settings;
	my %servers;

	my @nameservers;

	# Read DNS configuration.
	&readhash("$General::swroot/dns/settings", \%settings);

	# Read configured DNS servers.
	&readhasharray("$General::swroot/dns/servers", \%servers);

	# Check if the ISP assigned server should be used.
	if ($settings{'USE_ISP_NAMESERVERS'} eq "on") {
		# Assign ISP nameserver files.
		my @ISP_nameserver_files = ( "/var/run/dns1", "/var/run/dns2" );

		# Loop through the array of ISP assigned DNS servers.
		foreach my $file (@ISP_nameserver_files) {
			# Grab the IP address.
			my $address = &grab_address_from_file($file);

			# Check if an address has been grabbed.
			if ($address) {
				# Add the address to the array of nameservers.
				push(@nameservers, $address);
			}
		}
	}

	# Check if DNS servers are configured.
	if (%servers) {
		# Loop through the hash of configured DNS servers.
		foreach my $id (keys %servers) {
			my $address = $servers{$id}[0];
			my $status = $servers{$id}[2];

			# Check if the current processed server is enabled.
			if ($status eq "enabled") {
				# Add the address to the array of nameservers.
				push(@nameservers, $address);
			}
		}
	}

	# Return the array.
	return &uniq(@nameservers);
}

# Function to format a string containing the amount of bytes to
# something human-readable.
sub formatBytes {
	# Private array which contains the units.
	my @units = qw(B KB MB GB TB PB);

	my $bytes = shift;
	my $unit;

	# Loop through the array of units.
	foreach my $element (@units) {
		# Assign current processed element to unit.
		$unit = $element;

		# Break loop if the bytes are less than the next unit.
		last if $bytes < 1024;

		# Divide bytes amount with 1024.
        	$bytes /= 1024;
    	}

	# Return the divided and rounded bytes count and the unit.
	return sprintf("%.2f %s", $bytes, $unit);
}

# Function to collect and generate a hash for translating protocol numbers into
# their names.
sub generateProtoTransHash () {
	# File which contains the protocol definitions.
	my $protocols_file = "/etc/protocols";

	my %protocols = ();

	# Open protocols file.
	open(FILE, "$protocols_file") or die "Could not open $protocols_file. $!\n";

	# Loop through the file.
	while (my $line = <FILE>) {
		# Skip comments.
		next if ($line =~ /^\#/);

		# Skip blank  lines.
		next if ($line =~ /^\s*$/);

		# Remove any newlines.
		chomp($line);

		# Split line content.
		my ($protocol_lc, $number, $protocol_uc, $comment) = split(' ', $line);

		# Add proto details to the hash of protocols.
		$protocols{$number} = $protocol_uc;
	}

	# Close file handle.
	close(FILE);

	# Return the hash.
	return %protocols;
}

# Cloud Stuff

sub running_in_cloud() {
	return &running_on_ec2() || &running_on_gcp();
}

sub running_on_ec2() {
	if (-e "/var/run/aws-instance-id") {
		return 1;
	}

	return 0;
}

sub running_on_gcp() {
	if (-e "/var/run/gcp-instance-id") {
		return 1;
	}

	return 0;
}

1;
