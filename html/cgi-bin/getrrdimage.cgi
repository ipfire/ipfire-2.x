#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2005-2021  IPFire Team                                        #
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

use strict;
use URI;
use Text::Wrap;
use experimental 'smartmatch';

# debugging
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/graphs.pl";

# List of graph origins that getrrdimage.cgi can process directly
# (unknown origins are forwarded to ensure compatibility)
my @supported_origins = ("entropy.cgi", "hardwaregraphs.cgi", "media.cgi",
	"memory.cgi", "netexternal.cgi", "netinternal.cgi", "netother.cgi",
	"netovpnrw.cgi", "netovpnsrv.cgi", "qos.cgi", "services.cgi", "system.cgi");

### Process GET parameters ###
# URL format: /?origin=[graph origin cgi]&graph=[graph name]&range=[time range]
my $uri = URI->new($ENV{'REQUEST_URI'});
my %query = $uri->query_form;

my $origin = lc $query{'origin'}; # lower case
my $graph = $query{'graph'};
my $range = lc $query{'range'}; # lower case

# Check parameters
unless(($origin =~ /^\w+?\.cgi$/) && ($graph =~ /^[\w\-.,; ]+?$/) && ($range ~~ @Graphs::time_ranges)) {
	# Send HTTP headers
	_start_svg_output();

	_print_error("URL parameters missing or malformed.");
	exit;
}

# Unsupported graph origin: Redirect request to the CGI specified in the "origin" parameter
# This enables backwards compatibility with addons that use Graphs::makegraphbox to ouput their own graphs
unless(($origin ~~ @supported_origins) || ($origin eq "getrrdimage.cgi")) {
	# Rewrite to old URL format: /[graph origin cgi]?[graph name]?[time range]
	my $location = "https://$ENV{'SERVER_NAME'}:$ENV{'SERVER_PORT'}/cgi-bin/${origin}?${graph}?${range}";

	# Send HTTP redirect
	print "Status: 302 Found\n";
	print "Location: $location\n";
	print "Content-type: text/html; charset=UTF-8\n";
	print "\n"; # End of HTTP headers

	print "Unsupported origin, request redirected to '$location'";
	exit;
}

### Create graphs ###
# Send HTTP headers
_start_svg_output();

# Graphs are first grouped by their origin.
# This is because some graph categories require special parameter handling.
my $graphstatus = '';
if($origin eq "entropy.cgi") {				## entropy.cgi
	$graphstatus = Graphs::updateentropygraph($range);
# ------

} elsif($origin eq "hardwaregraphs.cgi") {	## hardwaregraphs.cgi
	if($graph eq "hwtemp") {
		$graphstatus = Graphs::updatehwtempgraph($range);
	} elsif($graph eq "hwfan") {
		$graphstatus = Graphs::updatehwfangraph($range);
	} elsif($graph eq "hwvolt") {
		$graphstatus = Graphs::updatehwvoltgraph($range);
	} elsif($graph eq "thermaltemp") {
		$graphstatus = Graphs::updatethermaltempgraph($range);
	} elsif($graph =~ "sd?") {
		$graphstatus = Graphs::updatehddgraph($graph, $range);
	} elsif($graph =~ "nvme?") {
		$graphstatus = Graphs::updatehddgraph($graph, $range);
	} else {
		$graphstatus = "Unknown graph name.";
	}
# ------

} elsif($origin eq "media.cgi") {			## media.cgi
	if ($graph =~ "sd?" || $graph =~ "mmcblk?" || $graph =~ "nvme?n?" || $graph =~ "xvd??" || $graph =~ "vd?" || $graph =~ "md*" ) {
		$graphstatus = Graphs::updatediskgraph($graph, $range);
	} else {
		$graphstatus = "Unknown graph name.";
	}
# ------

} elsif($origin eq "memory.cgi") {			## memory.cgi
	if($graph eq "memory") {
		$graphstatus = Graphs::updatememorygraph($range);
	} elsif($graph eq "swap") {
		$graphstatus = Graphs::updateswapgraph($range);
	} else {
		$graphstatus = "Unknown graph name.";
	}
# ------

} elsif($origin eq "netexternal.cgi") {		## netexternal.cgi
	$graphstatus = Graphs::updateifgraph($graph, $range);
# ------

} elsif($origin eq "netinternal.cgi") {		## netinternal.cgi
	if ($graph =~ /wireless/){
		$graph =~ s/wireless//g;
		$graphstatus = Graphs::updatewirelessgraph($graph, $range);
	} else {
		$graphstatus = Graphs::updateifgraph($graph, $range);
	}
# ------

} elsif($origin eq "netother.cgi") {		## netother.cgi
	if($graph eq "conntrack") {
		$graphstatus = Graphs::updateconntrackgraph($range);
	} elsif($graph eq "fwhits") {
		$graphstatus = Graphs::updatefwhitsgraph($range);
	} else {
		$graphstatus = Graphs::updatepinggraph($graph, $range);
	}
# ------

} elsif($origin eq "netovpnrw.cgi") {		## netovpnrw.cgi
	if($graph ne "UNDEF") {
		$graphstatus = Graphs::updatevpngraph($graph, $range);
	} else {
		$graphstatus = "Unknown graph name.";
	}
# ------

} elsif($origin eq "netovpnsrv.cgi") {		## netovpnsrv.cgi
	if ($graph =~ /ipsec-/){
		$graph =~ s/ipsec-//g;
		$graphstatus = Graphs::updateifgraph($graph, $range);
	} else {
		$graphstatus = Graphs::updatevpnn2ngraph($graph, $range);
	}
# ------

} elsif($origin eq "qos.cgi") { 			## qos.cgi
	$graphstatus = Graphs::updateqosgraph($graph, $range);
# ------

} elsif($origin eq "services.cgi") {		## services.cgi
	if($graph eq "processescpu") {
		$graphstatus = Graphs::updateprocessescpugraph($range);
	} elsif($graph eq "processesmemory") {
		$graphstatus = Graphs::updateprocessesmemorygraph($range);
	} else {
		$graphstatus = "Unknown graph name.";
	}
# ------

} elsif($origin eq "system.cgi") { 			## system.cgi
	if($graph eq "cpu") {
		$graphstatus = Graphs::updatecpugraph($range);
	} elsif($graph eq "cpufreq") {
		$graphstatus = Graphs::updatecpufreqgraph($range);
	} elsif($graph eq "load") {
		$graphstatus = Graphs::updateloadgraph($range);
	} else {
		$graphstatus = "Unknown graph name.";
	}
# ------

} else {
	$graphstatus = "Unknown graph origin.";
}

### Print error message ###
# Add request parameters for debugging
if($graphstatus) {
	$graphstatus = "$graphstatus\n($origin, $graph, $range)";

	# Save message in system log for further inspection
	General::log($graphstatus);

	_print_error($graphstatus);
}

###--- Internal functions ---###

# Send HTTP headers
# (don't print any non-image data to STDOUT afterwards)
sub _start_svg_output {
	print "Cache-Control: no-cache, no-store\n";
	print "Content-Type: image/svg+xml\n";
	print "\n"; # End of HTTP headers
}

# Print error message to SVG output
sub _print_error {
	my ($message) = @_;

	# Prepare image options
	my %img = (
		'width' => $Graphs::image_size{'width'},
		'height' => $Graphs::image_size{'height'},
		'text_center' => int($Graphs::image_size{'width'} / 2),
		'line_height' => 20,
		'font_family' => "DejaVu Sans, Helvetica, sans-serif" # Matching the IPFire theme
	);

	# Line-wrap message to fit image (adjust to font width if necessary)
	local($Text::Wrap::columns) = int($img{'width'} / 10);
	$message = wrap('', '', $message);

	# Create new image with fixed background and border
	print <<END
<?xml version="1.0" encoding="UTF-8"?>
<svg width="$img{'width'}px" height="$img{'height'}px" viewBox="0 0 $img{'width'} $img{'height'}" version="1.1" xmlns="http://www.w3.org/2000/svg">
	<!-- Background -->
	<rect width="100%" height="100%" fill="white"/>
	<rect width="100%" height="100%" fill="none" stroke="red" stroke-width="2" transform="scale(0.95)" transform-origin="center"/>
	<!-- Message -->
	<text x="$img{'text_center'}" y="50" font-size="20" font-family="$img{'font_family'}" text-anchor="middle">- $Lang::tr{'error'} -</text>
	<text x="$img{'text_center'}" y="90" font-size="14" font-family="$img{'font_family'}" text-anchor="middle">
END
;

	# Print message lines
	my $shift_y = 0; # Shifts text along y-axis
	foreach my $line (split(/\n/, $message)) {
		if($line ne "") { # Don't create empty tspan elements
			print <<END
		<tspan x="$img{'text_center'}" dy="$shift_y">$line</tspan>
END
;
			$shift_y = $img{'line_height'};
		} else { # Create blank lines by summing up unused line height
			$shift_y += $img{'line_height'};
		}
	}

	# Finish SVG output
	print <<END
	</text>
</svg>
END
;
}
