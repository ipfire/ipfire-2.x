#!/usr/bin/perl

###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
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
# Copyright (C) 2018 - 2020 The IPFire Team                                   #
#                                                                             #
###############################################################################

use strict;

# enable the following only for debugging purposes
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/ipblocklist-functions.pl";

# Import blockist sources and settings file.
require "${General::swroot}/ipblocklist/sources";

###############################################################################
# Configuration variables
###############################################################################

my $settings      = "${General::swroot}/ipblocklist/settings";
my %cgiparams     = ('ACTION' => '');

###############################################################################
# Variables
###############################################################################

my $errormessage  = '';
my $updating      = 0;
my %mainsettings;
my %color;

# Default settings - normally overwritten by settings file
my %settings = (
	'DEBUG'           => 0,
	'LOGGING'         => 'on',
	'ENABLE'          => 'off'
);

# Read all parameters
&Header::getcgihash( \%cgiparams);
&General::readhash( "${General::swroot}/main/settings", \%mainsettings );
&General::readhash( "/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color );

# Get list of supported blocklists.
my @blocklists = &IPblocklist::get_blocklists();

# Show Headers
&Header::showhttpheaders();

# Process actions
if ($cgiparams{'ACTION'} eq "$Lang::tr{'save'}") {
	# Array to store if blocklists are missing on the system
	# and needs to be downloaded first.
	my @missing_blocklists = ();

	# Loop through the array of supported blocklists.
	foreach my $blocklist (@blocklists) {
		# Skip the blocklist if it is not enabled.
		next if($cgiparams{$blocklist} ne "on");

		# Get the file name which keeps the converted blocklist.
		my $ipset_db_file = &IPblocklist::get_ipset_db_file($blocklist);

		# Check if the blocklist already has been downloaded.
		if(-f "$ipset_db_file") {
			# Blocklist already exits, we can skip it.
			next;
		} else {
			# Blocklist not present, store in array to download it.
			push(@missing_blocklists, $blocklist);
		}
	}

	# Check if the red device is not active and blocklists are missing.
	if ((not -e "${General::swroot}/red/active") && (@missing_blocklists)) {
		# The system is offline, cannot download the missing blocklists.
		# Store an error message.
		$errormessage = "$Lang::tr{'system is offline'}";
	} else {
		# Loop over the array of missing blocklists.
		foreach my $missing_blocklist (@missing_blocklists) {
			# Call the download and convert function to get the missing blocklist.
			my $status = &IPblocklist::download_and_create_blocklist($missing_blocklist);

			# Check if there was an error during download.
			# XXX - fill with messages.
			if ($status eq "dl_error") {
				$errormessage = "XXX - dl_error";
			} elsif ($status eq "empty_list") {
				$errormessage = "XXX - empty";
			}
		}
	}

	# Check if there was an error.
	unless($errormessage) {
		# Write configuration hash.
		&General::writehash($settings, \%cgiparams);

		# XXX display firewall reload stuff
	}
}

# Show site
&Header::openpage($Lang::tr{'ipblocklist'}, 1, '');
&Header::openbigbox('100%', 'left');

# Display error message if there was one.
&error() if ($errormessage);

# Read-in ipblocklist settings.
&General::readhash( $settings, \%settings ) if (-r $settings);

# Display configuration section.
&configsite();

# End of page
&Header::closebigbox();
&Header::closepage();


#------------------------------------------------------------------------------
# sub configsite()
#
# Displays configuration
#------------------------------------------------------------------------------

sub configsite {
	# Find preselections
	my $enable = 'checked';

	&Header::openbox('100%', 'left', $Lang::tr{'settings'});

	# Enable checkbox
	$enable = ($settings{'ENABLE'} eq 'on') ? ' checked' : '';

print<<END;
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table style='width:100%' border='0'>
			<tr>
				<td style='width:24em'>$Lang::tr{'ipblocklist use ipblocklists'}</td>
				<td><input type='checkbox' name='ENABLE' id='ENABLE'$enable></td>
			</tr>
		</table><br>
END

	# The following are only displayed if the blacklists are enabled
	$enable = ($settings{'LOGGING'} eq 'on') ? ' checked' : '';

print <<END;
		<div class='sources'>
			<table style='width:100%' border='0'>
				<tr>
					<td style='width:24em'>$Lang::tr{'ipblocklist log'}</td>
					<td><input type='checkbox' name="LOGGING" id="LOGGING"$enable></td>
				</tr>
			</table>

			<br><br>
			<h2>$Lang::tr{'ipblocklist blocklist settings'}</h2>

			<table width='100%' cellspacing='1' class='tbl'>
				<tr>
					<th align='left'>$Lang::tr{'ipblocklist id'}</th>
					<th align='left'>$Lang::tr{'ipblocklist name'}</th>
					<th align='left'>$Lang::tr{'ipblocklist category'}</th>
					<th align='center'>$Lang::tr{'ipblocklist enable'}</th>
				</tr>
END

	# Iterate through the list of sources
	my $lines = 0;

	foreach my $blocklist (@blocklists) {
		# Display blocklist name or provide a link to the website if available.
		my $website = "$blocklist";
		if ($IPblocklist::List::sources{$blocklist}{info}) {
			$website ="<a href='$IPblocklist::List::sources{$blocklist}{info}' target='_blank'>$blocklist</a>";
		}

		# Get the full name for the blocklist.
		my $name = &CGI::escapeHTML( $IPblocklist::List::sources{$blocklist}{'name'} );

		# Get category for this blocklist.
		my $category = $Lang::tr{"ipblocklist category $IPblocklist::List::sources{$blocklist}{'category'}"};

		# Determine if the blocklist is enabled.
		my $enable = '';
		$enable = 'checked' if ($settings{$blocklist} eq 'on');

		# Set colour for the table columns.
		my $col = ($lines++ % 2) ? "bgcolor='$color{'color20'}'" : "bgcolor='$color{'color22'}'";


print <<END;
				<tr $col>
					<td>$website</td>
					<td>$name</td>
					<td>$category</td>
					<td align='center'><input type='checkbox' name="$blocklist" id="$blocklist"$enable></td>
				</tr>
END
	}

# The save button at the bottom of the table
print <<END;
			</table>

		</div>

		<table style='width:100%;'>
			<tr>
				<td colspan='3' display:inline align='right'><input type='submit' name='ACTION' value='$Lang::tr{'save'}'></td>
			</tr>
		</table>
	</form>
END

	&Header::closebox();
}

#------------------------------------------------------------------------------
# sub error()
#
# Shows error messages
#------------------------------------------------------------------------------

sub error {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
		print "<class name='base'>$errormessage\n";
		print "&nbsp;</class>\n";
	&Header::closebox();
}
