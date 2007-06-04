#!/usr/bin/perl
#
# IPFire CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The IPFire Team
#

my $data_last = $ENV{'QUERY_STRING'};
my $rxb_last = 0;
my $txb_last = 0;

my (@fields, $field, $name, $value); 
@fields = split(/&/, $data_last);
foreach $field (@fields) {
  ($name, $value) = split(/=/, $field);
  $value =~ tr/+/ /;
  $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
  if ("$name" eq "rxb_last") {
		$rxb_last = $value;
	} elsif ("$name" eq "txb_last") {
		$txb_last = $value;
	}
}

my @data_now = `ip -s link show red0`;

my $lastline;
my $rxb_now = 0;
my $txb_now = 0;
foreach (@data_now) {
	if ( $lastline =~ /RX/ ) {
		@fields = split(/ /, $_);
		$rxb_now = $fields[4];
	} elsif ( $lastline =~ /TX/ ) {
		@fields = split(/ /, $_);
		$txb_now = $fields[4];
	}
	$lastline = $_;
}

my ($rx_kbs, $tx_kbs);
my $rxb_diff	= $rxb_now - $rxb_last;
my $txb_diff	= $txb_now - $txb_last;

if(( $rxb_diff == $rxb_now ) && ( $txb_diff == $txb_now ))
{
	$rx_kbs	= "0.00";
	$tx_kbs	= "0.00";
}
else
{
	$rx_kbs = $rxb_diff / 1024;
	$rx_kbs = $rx_kbs / 3.2;
	$rx_kbs = int($rx_kbs);
	$tx_kbs = $txb_diff / 1024;
	$tx_kbs = $tx_kbs / 3.2;
	$tx_kbs = int($tx_kbs);
}

print "Content-type: text/xml\n\n";
print "<?xml version=\"1.0\"?>\n";
print <<END
<inetinfo>
 <rx_kbs>$tx_kbs kb/s</rx_kbs>
 <tx_kbs>$rx_kbs kb/s</tx_kbs>
 <rxb>$rxb_now</rxb>
 <txb>$txb_now</txb>
</inetinfo>
END
;
