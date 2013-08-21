#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007  Michael Tremer & Christian Schmidt                      #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
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

use CGI;
use HTML::Entities;
use HTML::Template;

my $swroot="/var/ipfire";
my $templateroot = "/srv/web/ipfire/html/redirect-templates";

my %netsettings;
my %filtersettings;

&readhash("$swroot/ethernet/settings", \%netsettings);
&readhash("$swroot/urlfilter/settings", \%filtersettings);

# Read the template file.
my $template = $filtersettings{'REDIRECT_TEMPLATE'};
if (($template eq '') || (! -e "$templateroot/$template")) {
	$template = "legacy";
}
my $tmpl = HTML::Template->new(
	filename => "$templateroot/$template/template.html",
	die_on_bad_params => 0
);

# Address where to load more resources from.
$tmpl->param(ADDRESS => "http://$netsettings{'GREEN_ADDRESS'}:81");

# Message text 1
my $msgtext1 = $filtersettings{'MSG_TEXT_1'};
if ($msgtext1 eq '') {
	$msgtext1 = "A C C E S S &nbsp;&nbsp; D E N I E D";
}
$tmpl->param(MSG_TEXT_1 => $msgtext1);

# Message text 2
my $msgtext2 = $filtersettings{'MSG_TEXT_2'};
if ($msgtext2 eq '') {
	$msgtext2 = "Access to the requested page has been denied";
}
$tmpl->param(MSG_TEXT_2 => $msgtext2);

# Message text 3
my $msgtext3 = $filtersettings{'MSG_TEXT_3'};
if ($msgtext3 eq '') {
	$msgtext3 = "Please contact the Network Administrator if you think there has been an error";
}
$tmpl->param(MSG_TEXT_3 => $msgtext3);

# Category
my $category = CGI::param("category");
$tmpl->param(CATEGORY => &escape($category));

# URL
my $url = CGI::param("url");
$tmpl->param(URL => &escape($url));

# IP address
my $ip_address = CGI::param("ip");
$tmpl->param(IP_ADDRESS => &escape($ip_address));

# Print header
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
print $tmpl->output;

sub escape($) {
	my $s = shift;
	return HTML::Entities::encode_entities($s);
}

sub readhash {
	my $filename = $_[0];
	my $hash = $_[1];
	my ($var, $val);

	if (-e $filename) {
		open(FILE, $filename) or die "Unable to read file $filename";
		while (<FILE>) {
			chop;
			($var, $val) = split /=/, $_, 2;
			if ($var) {
				$val =~ s/^\'//g;
				$val =~ s/\'$//g;
	
				# Untaint variables read from hash
				$var =~ /([A-Za-z0-9_-]*)/;        $var = $1;
				$val =~ /([\w\W]*)/; $val = $1;
				$hash->{$var} = $val;
			}
		}

		close FILE;
	}
}
