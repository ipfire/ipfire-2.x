#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2016  Alexander Marx alexander.marx@ipfire.org                #
#                                                                             #
# This program is free software you can redistribute it and/or modify         #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

use strict;
use CGI ':standard';
use URI::Escape;
use HTML::Entities();
use HTML::Template;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";

#Set Variables
my %voucherhash=();
my %clientshash=();
my %cgiparams=();
my %settings=();
my $voucherout="${General::swroot}/captive/voucher_out";
my $clients="${General::swroot}/captive/clients";
my $settingsfile="${General::swroot}/captive/settings";
my $errormessage;
my $url=param('redirect');

#Create /var/ipfire/captive/clients if not exist
unless (-f $clients){ system("touch $clients"); }

#Get GUI variables
&getcgihash(\%cgiparams);

#Read settings
&General::readhash("$settingsfile", \%settings) if(-f $settingsfile);

# Actions
if ($cgiparams{'ACTION'} eq "SUBMIT") {
	# Get client IP address
	my $ip_address = $ENV{X_FORWARDED_FOR} || $ENV{REMOTE_ADDR};

	# Retrieve the MAC address from the ARP table
	my $mac_address = &Network::get_hardware_address($ip_address);

	&General::readhasharray("$clients", \%clientshash);
	my $key = &General::findhasharraykey(\%clientshash);

	# Create a new client line
	foreach my $i (0 .. 5) { $clientshash{$key}[$i] = ""; }

	# MAC address of the client
	$clientshash{$key}[0] = $mac_address;

	# IP address of the client
	$clientshash{$key}[1] = $ip_address;

	# Current time
	$clientshash{$key}[2] = time();

	if ($settings{"AUTH"} eq "VOUCHER") {
		&General::readhasharray("$voucherout", \%voucherhash);

		# Convert voucher input to uppercase
		$cgiparams{'VOUCHER'} = uc $cgiparams{'VOUCHER'};

		# Walk through all valid vouchers and find the right one
		my $found = 0;
		foreach my $voucher (keys %voucherhash) {
			if ($voucherhash{$voucher}[1] eq $cgiparams{'VOUCHER'}) {
				$found = 1;

				# Copy expiry time
				$clientshash{$key}[3] = $voucherhash{$voucher}[2];

				# Save voucher code
				$clientshash{$key}[4] = $cgiparams{'VOUCHER'};

				# Copy voucher remark
				$clientshash{$key}[5] = $voucherhash{$voucher}[3];

				# Delete used voucher
				delete $voucherhash{$voucher};
				&General::writehasharray("$voucherout", \%voucherhash);

				last;
			}
		}

		if ($found == 1) {
			&General::log("Captive", "Internet access granted via voucher ($clientshash{$key}[4]) for $ip_address until $clientshash{$key}[3]");
		} else {
			$errormessage = $Lang::tr{"Captive invalid_voucher"};
		}

	# License
	} else {
		# Copy expiry time
		$clientshash{$key}[3] = $settings{'EXPIRE'};

		# No voucher code
		$clientshash{$key}[4] = "LICENSE";

		&General::log("Captive", "Internet access granted via license agreement for $ip_address until $clientshash{$key}[3]");
	}

	# If no errors were found, save configruation and reload
	if (!$errormessage) {
		&General::writehasharray("$clients", \%clientshash);

		system("/usr/local/bin/captivectrl");

		# Redirect client to the original URL
		print "Status: 302 Moved Temporarily\n";
		print "Location: $url\n";
		print "Connection: close\n\n";
		exit 0;
	}
}

my $tmpl = HTML::Template->new(
	filename => "/srv/web/ipfire/html/captive/template.html",
	die_on_bad_params => 0
);

$tmpl->param(REDIRECT_URL => $url);

# Voucher
if ($settings{'AUTH'} eq "VOUCHER") {
	$tmpl->param(VOUCHER  => 1);
}

$tmpl->param(TITLE => $settings{'TITLE'});
$tmpl->param(ERROR => $errormessage);

$tmpl->param(TAC => &gettac());

# Some translated strings
$tmpl->param(L_ACTIVATE        => $Lang::tr{'Captive ACTIVATE'});
$tmpl->param(L_GAIN_ACCESS     => $Lang::tr{'Captive GAIN ACCESS'});
$tmpl->param(L_HEADING_TAC     => $Lang::tr{'Captive heading tac'});
$tmpl->param(L_HEADING_VOUCHER => $Lang::tr{'Captive heading voucher'});
$tmpl->param(L_AGREE_TAC       => $Lang::tr{'Captive agree tac'});

# Print header
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

# Print rendered template
print $tmpl->output();

sub getcgihash {
	my ($hash, $params) = @_;
	my $cgi = CGI->new ();
	$hash->{'__CGI__'} = $cgi;
	return if ($ENV{'REQUEST_METHOD'} ne 'POST');
	if (!$params->{'wantfile'}) {
		$CGI::DISABLE_UPLOADS = 1;
		$CGI::POST_MAX        = 1024 * 1024;
	} else {
		$CGI::POST_MAX = 10 * 1024 * 1024;
	}
	$cgi->referer() =~ m/^http?\:\/\/([^\/]+)/;
	my $referer = $1;
	$cgi->url() =~ m/^http?\:\/\/([^\/]+)/;
	my $servername = $1;
	return if ($referer ne $servername);

	### Modified for getting multi-vars, split by |
	my %temp = $cgi->Vars();
        foreach my $key (keys %temp) {
		$hash->{$key} = $temp{$key};
		$hash->{$key} =~ s/\0/|/g;
		$hash->{$key} =~ s/^\s*(.*?)\s*$/$1/;
        }

	if (($params->{'wantfile'})&&($params->{'filevar'})) {
		$hash->{$params->{'filevar'}} = $cgi->upload
						($params->{'filevar'});
	}
	return;
}

sub gettac() {
	my @tac = ();

	open(my $handle, "<:utf8", "/var/ipfire/captive/agb.txt" ) or die("$!");
	while(<$handle>) {
		$_ = HTML::Entities::decode_entities($_);
		push(@tac, $_);
	}
	close($handle);

	my $tac = join("\n", @tac);

	# Format paragraphs
	$tac =~ s/\n\n/<\/p>\n<p>/g;

	return $tac;
}
