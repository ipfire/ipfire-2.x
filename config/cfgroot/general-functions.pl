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
use Net::SSLeay;
use Net::IPv4Addr;

$|=1; # line buffering

$General::version = 'VERSION';
$General::swroot = 'CONFIG_ROOT';
$General::noipprefix = 'noipg-';
$General::adminmanualurl = 'http://wiki.ipfire.org';

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
	system('logger', '-t', $tag, $logmessage);
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

sub writehashpart
{
	# This function replaces the given hash in the original hash by keeping the old
	# content and just replacing the new content

	my $filename = $_[0];
	my $newhash = $_[1];
	my %oldhash;
	my ($var, $val);

	readhash("${filename}", \%oldhash);

	foreach $var (keys %$newhash){
		$oldhash{$var}=$newhash->{$var};
	}

	# write cgi vars to the file.
	open(FILE, ">${filename}") or die "Unable to write file $filename";
	flock FILE, 2;
	foreach $var (keys %oldhash) 
	{
		if ( $var eq "__CGI__"){next;}
		$val = $oldhash{$var};
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

sub age
{
	my ($dev, $ino, $mode, $nlink, $uid, $gid, $rdev, $size,
	        $atime, $mtime, $ctime, $blksize, $blocks) = stat $_[0];
	my $now = time;

	my $totalsecs = $now - $mtime;
	my $days = int($totalsecs / 86400);
	my $totalhours = int($totalsecs / 3600);
	my $hours = $totalhours % 24;
	my $totalmins = int($totalsecs / 60);
	my $mins = $totalmins % 60;
	my $secs = $totalsecs % 60;

	return "${days}d ${hours}h ${mins}m ${secs}s";
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

sub validmask
{
	my $mask = $_[0];

	# secord part an ip?
	if (&validip($mask)) {
		return 1; }
	# second part a number?
	if (/^0/) {
		return 0; }
	if (!($mask =~ /^\d+$/)) {
		return 0; }
	if ($mask >= 0 && $mask <= 32) {
		return 1; }
	return 0;
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

sub validipandmask
{
	my $ipandmask = $_[0];

	# split it into number and mask.
	if (!($ipandmask =~ /^(.*?)\/(.*?)$/)) {
		return 0; }
	my $ip = $1;
	my $mask = $2;
	# first part not a ip?
	if (!(&validip($ip))) {
		return 0; }
	return &validmask($mask);
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

	# Each part should be at least two characters in length
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

	# Checks a domain name against RFC1035
        my $domainname = $_[0];
	my @parts = split (/\./, $domainname);	# Split hostname at the '.'

	foreach $part (@parts) {
		# Each part should be at least two characters in length
		# but no more than 63 characters
		if (length ($part) < 2 || length ($part) > 63) {
			return 0;}
		# Only valid characters are a-z, A-Z, 0-9 and -
		if ($part !~ /^[a-zA-Z0-9-]*$/) {
			return 0;}
		# First character can only be a letter or a digit
		if (substr ($part, 0, 1) !~ /^[a-zA-Z0-9]*$/) {
			return 0;}
		# Last character can only be a letter or a digit
		if (substr ($part, -1, 1) !~ /^[a-zA-Z0-9]*$/) {
			return 0;}
	}
	return 1;
}

sub validfqdn
{
	my $part;

	# Checks a fully qualified domain name against RFC1035
        my $fqdn = $_[0];
	my @parts = split (/\./, $fqdn);	# Split hostname at the '.'
	if (scalar(@parts) < 2) {		# At least two parts should
		return 0;}			# exist in a FQDN
						# (i.e. hostname.domain)
	foreach $part (@parts) {
		# Each part should be at least one character in length
		# but no more than 63 characters
		if (length ($part) < 1 || length ($part) > 63) {
			return 0;}
		# Only valid characters are a-z, A-Z, 0-9 and -
		if ($part !~ /^[a-zA-Z0-9-]*$/) {
			return 0;}
		# First character can only be a letter or a digit
		if (substr ($part, 0, 1) !~ /^[a-zA-Z0-9]*$/) {
			return 0;}
		# Last character can only be a letter or a digit
		if (substr ($part, -1, 1) !~ /^[a-zA-Z0-9]*$/) {
			return 0;}
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

# Test if IP is within a subnet
# Call: IpInSubnet (Addr, Subnet, Subnet Mask)
#       Subnet can be an IP of the subnet: 10.0.0.0 or 10.0.0.1
#       Everything in dottted notation
# Return: TRUE/FALSE
sub IpInSubnet
{
    my $ip = unpack('N', &Socket::inet_aton(shift));
    my $start = unpack('N', &Socket::inet_aton(shift));
    my $mask  = unpack('N', &Socket::inet_aton(shift));
       $start &= $mask;  # base of subnet...
    my $end   = $start + ~$mask;
    return (($ip >= $start) && ($ip <= $end));
}

#
# Return the following IP (IP+1) in dotted notation.
# Call: NextIP ('1.1.1.1');
# Return: '1.1.1.2'
#
sub NextIP
{
    return &Socket::inet_ntoa( pack("N", 1 +  unpack('N', &Socket::inet_aton(shift))
				   )
			     );
}

sub ipcidr
{
	my ($ip,$cidr) = &Net::IPv4Addr::ipv4_parse(shift);
	return "$ip\/$cidr";
}

sub ipcidr2msk
{
       my ($ip,$cidr) = &Net::IPv4Addr::ipv4_parse(shift);
       my $netmask = &Net::IPv4Addr::ipv4_cidr2msk($cidr);
       return "$ip\/$netmask";
}


sub validemail {
    my $mail = shift;
    return 0 if ( $mail !~ /^[0-9a-zA-Z\.\-\_]+\@[0-9a-zA-Z\.\-]+$/ );
    return 0 if ( $mail =~ /^[^0-9a-zA-Z]|[^0-9a-zA-Z]$/);
    return 0 if ( $mail !~ /([0-9a-zA-Z]{1})\@./ );
    return 0 if ( $mail !~ /.\@([0-9a-zA-Z]{1})/ );
    return 0 if ( $mail =~ /.\.\-.|.\-\..|.\.\..|.\-\-./g );
    return 0 if ( $mail =~ /.\.\_.|.\-\_.|.\_\..|.\_\-.|.\_\_./g );
    return 0 if ( $mail !~ /\.([a-zA-Z]{2,4})$/ );
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

sub srtarray 
# Darren Critchley - darrenc@telus.net - (c) 2003
# &srtarray(SortOrder, AlphaNumeric, SortDirection, ArrayToBeSorted)
# This subroutine will take the following parameters:
#   ColumnNumber = the column which you want to sort on, starts at 1
#   AlphaNumberic = a or n (lowercase) defines whether the sort should be alpha or numberic
#   SortDirection = asc or dsc (lowercase) Ascending or Descending sort
#   ArrayToBeSorted = the array that wants sorting
#
#   Returns an array that is sorted to your specs
#
#   If SortOrder is greater than the elements in array, then it defaults to the first element
# 
{
	my ($colno, $alpnum, $srtdir, @tobesorted) = @_;
	my @tmparray;
	my @srtedarray;
	my $line;
	my $newline;
	my $ctr;
	my $ttlitems = scalar @tobesorted; # want to know the number of rows in the passed array
	if ($ttlitems < 1){ # if no items, don't waste our time lets leave
		return (@tobesorted);
	}
	my @tmp = split(/\,/,$tobesorted[0]);
	$ttlitems = scalar @tmp; # this should be the number of elements in each row of the passed in array

	# Darren Critchley - validate parameters
	if ($colno > $ttlitems){$colno = '1';}
	$colno--; # remove one from colno to deal with arrays starting at 0
	if($colno < 0){$colno = '0';}
	if ($alpnum ne '') { $alpnum = lc($alpnum); } else { $alpnum = 'a'; }
	if ($srtdir ne '') { $srtdir = lc($srtdir); } else { $srtdir = 'src'; }

	foreach $line (@tobesorted)
	{
		chomp($line);
		if ($line ne '') {
			my @temp = split(/\,/,$line);
			# Darren Critchley - juggle the fields so that the one we want to sort on is first
			my $tmpholder = $temp[0];
			$temp[0] = $temp[$colno];
			$temp[$colno] = $tmpholder;
			$newline = "";
			for ($ctr=0; $ctr < $ttlitems ; $ctr++) {
				$newline=$newline . $temp[$ctr] . ",";
			}
			chop($newline);
			push(@tmparray,$newline);
		}
	}
	if ($alpnum eq 'n') {
		@tmparray = sort {$a <=> $b} @tmparray;
	} else {
		@tmparray = (sort @tmparray);
	}
	foreach $line (@tmparray)
	{
		chomp($line);
		if ($line ne '') {
			my @temp = split(/\,/,$line);
			my $tmpholder = $temp[0];
			$temp[0] = $temp[$colno];
			$temp[$colno] = $tmpholder;
			$newline = "";
			for ($ctr=0; $ctr < $ttlitems ; $ctr++){
				$newline=$newline . $temp[$ctr] . ",";
			}
			chop($newline);
			push(@srtedarray,$newline);
		}
	}

	if ($srtdir eq 'dsc') {
		@tmparray = reverse(@srtedarray);
		return (@tmparray);
	} else {
		return (@srtedarray);
	}
}

sub FetchPublicIp {
    my %proxysettings;
    &General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
    if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
        my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
        Net::SSLeay::set_proxy($peer,$peerport,$proxysettings{'UPSTREAM_USER'},$proxysettings{'UPSTREAM_PASSWORD'} );
    }
    my ($out, $response) = Net::SSLeay::get_http(  'checkip.dyndns.org',
                				    80,
        					    "/",
						    Net::SSLeay::make_headers('User-Agent' => 'IPFire' )
						);
    if ($response =~ m%HTTP/1\.. 200 OK%) {
	$out =~ /Current IP Address: (\d+.\d+.\d+.\d+)/;
	return $1;
    }
    return '';
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
#
# This sub returns the red IP used to compare in DyndnsServiceSync
#
sub GetDyndnsRedIP {
    my %settings;
    &General::readhash("${General::swroot}/ddns/settings", \%settings);

    open(IP, "${General::swroot}/red/local-ipaddress") or return 'unavailable';
    my $ip = <IP>;
    close(IP);
    chomp $ip;

    if (&General::IpInSubnet ($ip,'10.0.0.0','255.0.0.0') ||
        &General::IpInSubnet ($ip,'172.16.0.0.','255.240.0.0') ||
        &General::IpInSubnet ($ip,'192.168.0.0','255.255.0.0'))
    {
	if ($settings{'BEHINDROUTER'} eq 'FETCH_IP') {
    	    my $RealIP = &General::FetchPublicIp;
	    $ip = (&General::validip ($RealIP) ?  $RealIP : 'unavailable');
	}
    }
    return $ip;
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
    if ($index>41) {return 'unknown'} else {return @icmp_description[$index]};
}
1;
