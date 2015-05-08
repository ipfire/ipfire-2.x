#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2014  IPFire Team  <info@ipfire.org>                     #
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

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::table2colour}, ${Header::colouryellow} );
undef (@dummy);

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

# Config file for basic configuration.
my $settingsfile = "${General::swroot}/ddns/settings";

# Config file to store the configured ddns providers.
my $datafile = "${General::swroot}/ddns/config";

# Call the ddnsctrl helper binary to perform the update.
my @ddnsprog = ("/usr/local/bin/ddnsctrl", "update-all");

my %settings=();
my $errormessage = '';

# DDNS General settings.
$settings{'BEHINDROUTER'} = 'RED_IP';

# Account settings.
$settings{'HOSTNAME'} = '';
$settings{'DOMAIN'} = '';
$settings{'LOGIN'} = '';
$settings{'PASSWORD'} = '';
$settings{'ENABLED'} = '';
$settings{'PROXY'} = '';
$settings{'SERVICE'} = '';

$settings{'ACTION'} = '';

# Get supported ddns providers.
my @providers = &GetProviders();

# Hook to regenerate the configuration files, if cgi got called from command line.
if ($ENV{"REMOTE_ADDR"} eq "") {
	&GenerateDDNSConfigFile();
	exit(0);
}

&Header::showhttpheaders();

#Get GUI values
&Header::getcgihash(\%settings);

# Read configuration file.
open(FILE, "$datafile") or die "Unable to open $datafile.";
my @current = <FILE>;
close (FILE);

#
# Save General Settings.
#
if ($settings{'ACTION'} eq $Lang::tr{'save'}) {
	# Open /var/ipfire/ddns/settings for writing.
	open(FILE, ">$settingsfile") or die "Unable to open $settingsfile.";

	# Lock file for writing.
	flock FILE, 2;

	# Check if BEHINDROUTER has been configured.
	if ($settings{'BEHINDROUTER'} ne '') {
		print FILE "BEHINDROUTER=$settings{'BEHINDROUTER'}\n";
	}

	# Close file after writing.
	close(FILE);

	# Update ddns config file.
	&GenerateDDNSConfigFile();
}

#
# Toggle enable/disable field.  Field is in second position
#
if ($settings{'ACTION'} eq $Lang::tr{'toggle enable disable'}) {
	# Open /var/ipfire/ddns/config for writing.
	open(FILE, ">$datafile") or die "Unable to open $datafile.";

	# Lock file for writing.
	flock FILE, 2;

	my @temp;
	my $id = 0;

	# Read file line by line.
	foreach my $line (@current) {
		# Remove newlines.
		chomp($line);

		if ($settings{'ID'} eq $id) {
			# Splitt lines (splitting element is a single ",") and save values into temp array.
			@temp = split(/\,/,$line);

			# Check if we want to toggle ENABLED or WILDCARDS.
			if ($settings{'ENABLED'} ne '') {
				# Update ENABLED.
				print FILE "$temp[0],$temp[1],$temp[2],$temp[3],$temp[4],$temp[5],$temp[6],$settings{'ENABLED'}\n";
			}
		} else {
			# Print unmodified line.
			print FILE "$line\n";
		}

		# Increase $id.
		$id++;
	}
	undef $settings{'ID'};

	# Close file after writing.
	close(FILE);

	# Write out logging notice.
	&General::log($Lang::tr{'ddns hostname modified'});

	# Update ddns config file.
	&GenerateDDNSConfigFile();
}

#
# Add new accounts, or edit existing ones.
#
if (($settings{'ACTION'} eq $Lang::tr{'add'}) || ($settings{'ACTION'} eq $Lang::tr{'update'})) {
	# Check if a hostname has been given.
	if ($settings{'HOSTNAME'} eq '') {
		$errormessage = $Lang::tr{'hostname not set'};
	}

	# Check if a valid domainname has been provided.
	if (!&General::validdomainname($settings{'HOSTNAME'})) {
		$errormessage = $Lang::tr{'invalid domain name'};
	}

	# Check if a username has been sent.
	if ($settings{'LOGIN'} eq '') {
		$errormessage = $Lang::tr{'username not set'};
	}

	# Check if a password has been typed in.
	# freedns.afraid.org does not require this field.
	if (($settings{'PASSWORD'} eq '') && ($settings{'SERVICE'} ne 'freedns.afraid.org') && ($settings{'SERVICE'} ne 'regfish.com')) {
		$errormessage = $Lang::tr{'password not set'};
	}

	# Go furter if there was no error.
	if (!$errormessage) {
		# Splitt hostname field into 2 parts for storrage.
		my($hostname, $domain) = split(/\./, $settings{'HOSTNAME'}, 2);

		# Handle enabled checkbox. When the checkbox is selected a "on" will be returned,
		# if the checkbox is not checked nothing is returned in this case we set the value to "off".
		if ($settings{'ENABLED'} ne 'on') {
			$settings{'ENABLED'} = 'off';
		}

		# Handle adding new accounts.
		if ($settings{'ACTION'} eq $Lang::tr{'add'}) {
			# Open /var/ipfire/ddns/config for writing.
			open(FILE, ">>$datafile") or die "Unable to open $datafile.";

			# Lock file for writing.
			flock FILE, 2;

			# Add account data to the file.
			print FILE "$settings{'SERVICE'},$hostname,$domain,$settings{'PROXY'},$settings{'WILDCARDS'},$settings{'LOGIN'},$settings{'PASSWORD'},$settings{'ENABLED'}\n";

			# Close file after writing.
			close(FILE);

			# Write out notice to logfile.
			&General::log($Lang::tr{'ddns hostname added'});

		# Handle account edditing.
		} elsif ($settings{'ACTION'} eq $Lang::tr{'update'}) {
			# Open /var/ipfire/ddns/config for writing.
			open(FILE, ">$datafile") or die "Unable to open $datafile.";

			# Lock file for writing.
			flock FILE, 2;

			my $id = 0;

			# Read file line by line.
			foreach my $line (@current) {
				if ($settings{'ID'} eq $id) {
					print FILE "$settings{'SERVICE'},$hostname,$domain,$settings{'PROXY'},$settings{'WILDCARDS'},$settings{'LOGIN'},$settings{'PASSWORD'},$settings{'ENABLED'}\n";
				} else {
					print FILE "$line";
				}

				# Increase $id.
				$id++;
			}

			# Close file after writing.
			close(FILE);

			# Write out notice to logfile.
			&General::log($Lang::tr{'ddns hostname modified'});
		}
		undef $settings{'ID'};

		# Update ddns config file.
		&GenerateDDNSConfigFile();
	}
}

#
# Remove existing accounts.
#
if ($settings{'ACTION'} eq $Lang::tr{'remove'}) {
	# Open /var/ipfire/ddns/config for writing.
	open(FILE, ">$datafile") or die "Unable to open $datafile.";

	# Lock file for writing.
	flock FILE, 2;

	my $id = 0;

	# Read file line by line.
	foreach my $line (@current) {
		# Write back every line, except the one we want to drop
		# (identified by the ID)
		unless ($settings{'ID'} eq $id) {
			print FILE "$line";
		}

		# Increase id.
		$id++;
	}
	undef $settings{'ID'};

	# Close file after writing.
	close(FILE);

	# Write out notice to logfile.
	&General::log($Lang::tr{'ddns hostname removed'});

	# Update ddns config file.
	&GenerateDDNSConfigFile();
}

#
# Read items for editing.
#
if ($settings{'ACTION'} eq $Lang::tr{'edit'}) {
	my $id = 0;
	my @temp;

	# Read file line by line.
	foreach my $line (@current) {
		if ($settings{'ID'} eq $id) {
			# Remove newlines.
			chomp($line);

			# Splitt lines (splitting element is a single ",") and save values into temp array.
			@temp = split(/\,/,$line);

			# Handle hostname details. Only connect the values with a dott if both are available.
			my $hostname;

			if (($temp[1]) && ($temp[2])) {
				$hostname = "$temp[1].$temp[2]";
			} else {
				$hostname = "$temp[1]";
			}

			$settings{'SERVICE'} = $temp[0];
			$settings{'HOSTNAME'} = $hostname;
			$settings{'PROXY'} = $temp[3];
			$settings{'WILDCARDS'} = $temp[4];
			$settings{'LOGIN'} = $temp[5];
			$settings{'PASSWORD'} = $temp[6];
			$settings{'ENABLED'} = $temp[7];
		}

		# Increase $id.
		$id++;
	}

	&GenerateDDNSConfigFile();
}

#
# Handle forced updates.
#
if ($settings{'ACTION'} eq $Lang::tr{'instant update'}) {
    system(@ddnsprog) == 0 or die "@ddnsprog failed: $?\n";
}

#
# Set default values.
#
if (!$settings{'ACTION'}) {
	$settings{'SERVICE'} = 'dyndns.org';
	$settings{'ENABLED'} = 'on';
	$settings{'ID'} = '';
}

&Header::openpage($Lang::tr{'dynamic dns'}, 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

# Read file for general ddns settings.
&General::readhash($settingsfile, \%settings);

my %checked =();
$checked{'BEHINDROUTER'}{'RED_IP'} = '';
$checked{'BEHINDROUTER'}{'FETCH_IP'} = '';
$checked{'BEHINDROUTER'}{$settings{'BEHINDROUTER'}} = "checked='checked'";

$checked{'ENABLED'}{'on'} = '';
$checked{'ENABLED'}{'off'} = '';
$checked{'ENABLED'}{$settings{'ENABLED'}} = "checked='checked'";

# Show box for errormessages..
if ($errormessage) {
    &Header::openbox('100%', 'left', $Lang::tr{'error messages'});
    print "<font class='base'>$errormessage&nbsp;</font>";
    &Header::closebox();
}

&Header::openbox('100%', 'left', $Lang::tr{'settings'});

##
# Section for general ddns setup.
print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='100%'>
	<tr>
		<td class='base'>$Lang::tr{'dyn dns source choice'}</td>
	</tr>
	<tr>
		<td class='base'><input type='radio' name='BEHINDROUTER' value='RED_IP' $checked{'BEHINDROUTER'}{'RED_IP'} />
		$Lang::tr{'use ipfire red ip'}</td>
	</tr>
	<tr>
		<td class='base'><input type='radio' name='BEHINDROUTER' value='FETCH_IP' $checked{'BEHINDROUTER'}{'FETCH_IP'} />
		$Lang::tr{'fetch ip from'}</td>
	</tr>
</table>
<br />
<hr />

<table width='100%'>
	<tr>
		<td align='right' valign='top' class='base'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
	</tr>
</table>
</form>
END
;

&Header::closebox();

##
# Section to add or edit an existing entry.

# Default is add.
my $buttontext = $Lang::tr{'add'};

# Change buttontext and headline if we edit an account.
if ($settings{'ACTION'} eq $Lang::tr{'edit'}) {
	# Rename button and print headline for updating.
	$buttontext = $Lang::tr{'update'};
	&Header::openbox('100%', 'left', $Lang::tr{'edit an existing host'});
} else {
	# Otherwise use default button text and show headline for adding a new account.
	&Header::openbox('100%', 'left', $Lang::tr{'add a host'});
}

print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ID' value='$settings{'ID'}' />
<table width='100%'>
	<tr>
		<td width='25%' class='base'>$Lang::tr{'service'}:</td>
		<td width='25%'>
END
;
		# Generate dropdown menu for service selection.
		print"<select size='1' name='SERVICE'>\n";

		my $selected;

		# Loop to print the providerlist.
		foreach my $provider (@providers) {
			# Check if the current provider needs to be selected.
			if ($provider eq $settings{'SERVICE'}) {
				$selected = 'selected';
			} else {
				$selected = "";
			}

			# Print out the HTML option field.
			print "<option value=\"$provider\" $selected>$provider</option>\n";
		}

		print"</select></td>\n";
print <<END
		<td width='20%' class='base'>$Lang::tr{'hostname'}:</td>
		<td width='30%'><input type='text' name='HOSTNAME' value='$settings{'HOSTNAME'}' /></td>
	</tr>

	<tr>
		<td class='base'>$Lang::tr{'enabled'}</td>
		<td><input type='checkbox' name='ENABLED' $checked{'ENABLED'}{'on'} /></td>
		<td class='base'>$Lang::tr{'username'}</td>
		<td><input type='text' name='LOGIN' value='$settings{'LOGIN'}' /></td>
	</tr>

	<tr>
		<td class='base'></td>
		<td></td>
		<td class='base'>$Lang::tr{'password'}</td>
		<td><input type='password' name='PASSWORD' value='$settings{'PASSWORD'}' /></td>
	</tr>
</table>
<br>
<hr>

<table width='100%'>
<tr>
    <td width='30%' align='right' class='base'>
	<input type='hidden' name='ACTION' value='$buttontext'>
	<input type='submit' name='SUBMIT' value='$buttontext'></td>
</tr>
</table>
</form>
END
;
&Header::closebox();

##
# Third section, display all created ddns hosts.
# Re-open file to get changes.
open(FILE, $datafile) or die "Unable to open $datafile.";
@current = <FILE>;
close(FILE);

# Get IP address of the red interface.
my $ip = &General::GetDyndnsRedIP();
my $id = 0;
my $toggle_enabled;

if (@current) {
	&Header::openbox('100%', 'left', $Lang::tr{'current hosts'});

	print <<END;
<table width='100%' class='tbl'>
	<tr>
		<th width='30%' align='center' class='boldbase'><b>$Lang::tr{'service'}</b></th>
		<th width='50%' align='center' class='boldbase'><b>$Lang::tr{'hostname'}</b></th>
		<th width='20%' colspan='3' class='boldbase' align='center'><b>$Lang::tr{'action'}</b></th>
	</tr>
END

	foreach my $line (@current) {
		# Remove newlines.
		chomp(@current);
		my @temp = split(/\,/,$line);

		# Handle hostname details. Only connect the values with a dott if both are available.
		my $hostname="";

		if (($temp[1]) && ($temp[2])) {
			$hostname="$temp[1].$temp[2]";
		} else {
			$hostname="$temp[1]";
		}

		# Generate value for enable/disable checkbox.
		my $sync = '';
		my $gif = '';
		my $gdesc = '';

		if ($temp[7] eq "on") {
			$gif = 'on.gif';
			$gdesc = $Lang::tr{'click to disable'};

			# Check if the given hostname is a FQDN before doing a nslookup.
			if (&General::validfqdn($hostname)) {
				$sync = (&General::DyndnsServiceSync ($ip,$temp[1], $temp[2]) ? "<font color='green'>": "<font color='red'>") ;
			}

			$toggle_enabled = 'off';
		} else {
			$sync = "<font color='blue'>";
			$gif = 'off.gif';
			$gdesc = $Lang::tr{'click to enable'};
			$toggle_enabled = 'on';
		}

		# Background color.
		my $col="";

		if ($settings{'ID'} eq $id) {
			$col="bgcolor='${Header::colouryellow}'";
		} elsif (!($temp[0] ~~ @providers)) {
			$col="bgcolor='#FF4D4D'";
		} elsif ($id % 2) {
			$col="bgcolor='$color{'color20'}'";
		} else {
			$col="bgcolor='$color{'color22'}'";
		}

		# Handle hostname details. Only connect the values with a dott if both are available.
		my $hostname="";

		if (($temp[1]) && ($temp[2])) {
			$hostname="$temp[1].$temp[2]";
		} else {
			$hostname="$temp[1]";
		}

		# The following HTML Code still is part of the loop.
		print <<END;
<tr>
	<td align='center' $col><a href='http://$temp[0]'>$temp[0]</a></td>
	<td align='center' $col>$sync$hostname</td>

	<td align='center' $col><form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type='hidden' name='ID' value='$id'>
		<input type='hidden' name='ENABLED' value='$toggle_enabled'>
		<input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}' />
		<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' alt='$gdesc' title='$gdesc' />
	</form></td>

	<td align='center' $col><form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type='hidden' name='ID' value='$id'>
		<input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
		<input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' />
	</form></td>

	<td align='center' $col><form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type='hidden' name='ID' value='$id'>
		<input type='hidden' name='ACTION' value='$Lang::tr{'remove'}' />
		<input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' alt='$Lang::tr{'remove'}' title='$Lang::tr{'remove'}' />
	</form></td>
</tr>
END
 	   	$id++;
	}

	print <<END;
</table>
<table width='100%'>
	<tr>
		<td class='boldbase'>&nbsp;<b>$Lang::tr{'legend'}:&nbsp;</b></td>
		<td><img src='/images/on.gif' alt='$Lang::tr{'click to disable'}' /></td>
		<td class='base'>$Lang::tr{'click to disable'}</td>
		<td>&nbsp;&nbsp;</td>
		<td><img src='/images/off.gif' alt='$Lang::tr{'click to enable'}' /></td>
		<td class='base'>$Lang::tr{'click to enable'}</td>
		<td>&nbsp;&nbsp;</td>
		<td><img src='/images/edit.gif' alt='$Lang::tr{'edit'}' /></td>
		<td class='base'>$Lang::tr{'edit'}</td>
		<td>&nbsp;&nbsp;</td>
		<td><img src='/images/delete.gif' alt='$Lang::tr{'remove'}' /></td>
		<td class='base'>$Lang::tr{'remove'}</td>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<td align='right' width='30%'><input type='submit' name='ACTION' value='$Lang::tr{'instant update'}' /></td>
		</form>
	</tr>
</table>
END

	&Header::closebox();
}

&Header::closebigbox();
&Header::closepage();

# Function to generate the required configuration file for the DDNS tool.
sub GenerateDDNSConfigFile {
	# Open datafile file
	open(SETTINGS, "<$datafile") or die "Could not open $datafile.";

	open(FILE, ">${General::swroot}/ddns/ddns.conf");

	# Global configuration options.
	print FILE "[config]\n";

	# Check if we guess our IP address by an extranal server.
	if ($settings{'BEHINDROUTER'} eq "FETCH_IP") {
		print FILE "guess_external_ip = true\n";
	} else {
		print FILE "guess_external_ip = false\n";
	}

	# Use an upstream proxy and generate proxy url.
	my %proxysettings;
	&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
	if ($proxysettings{'UPSTREAM_PROXY'}) {
		my $proxy_string = "http://";

		if ($proxysettings{'UPSTREAM_USER'} && $proxysettings{'UPSTREAM_PASSWORD'}) {
			$proxy_string .= "$proxysettings{'UPSTREAM_USER'}:$proxysettings{'UPSTREAM_PASSWORD'}@";
		}

		$proxy_string .= $proxysettings{'UPSTREAM_PROXY'};

		print FILE "proxy = $proxy_string\n";
	}

	print FILE "\n";

	while (<SETTINGS>) {
		my $line = $_;
		chomp($line);

		# Generate array based on the line content (seperator is a single or multiple space's)
		my @settings = split(/,/, $line);
		my ($provider, $hostname, $domain, $proxy, $wildcards, $username, $password, $enabled) = @settings;

		# Skip entries if they are not (longer) supported.
		next unless ($provider ~~ @providers);

		# Skip disabled entries.
		next unless ($enabled eq "on");

		# Handle hostname details. Only connect the values with a dott if both are available.
		if (($hostname) && ($domain)) {
			print FILE "[$hostname.$domain]\n";
		} else {
			print FILE "[$hostname]\n";
		}

		print FILE "provider = $provider\n";

		my $use_token = 0;

		# Handle token based auth for various providers.
		if ($provider ~~ ["dns.lightningwirelabs.com", "entrydns.net", "regfish.com",
				  "spdns.de", "zzzz.io"] && $username eq "token") {
			$use_token = 1;

		# Handle token auth for freedns.afraid.org and regfish.com.
		} elsif ($provider ~~ ["freedns.afraid.org", "regfish.com"] && $password eq "") {
			$use_token = 1;
			$password = $username;

		# Handle keys for nsupdate
		} elsif (($provider eq "nsupdate") && $username && $password) {
			print FILE "key = $username\n";
			print FILE "secret = $password\n";

			$username = "";
			$password = "";

		# Handle keys for nsupdate.info
		} elsif (($provider eq "nsupdate.info") && $password) {
			print FILE "secret = $password\n";

			$username = "";
			$password = "";
		}

		# Write auth details.
		if ($use_token) {
			print FILE "token = $password\n";
		} elsif ($username && $password) {
			print FILE "username = $username\n";
			print FILE "password = $password\n";
		}

		print FILE "\n";
	}

	close(SETTINGS);
	close(FILE);
}

# Function which generates an array (@providers) which contains the supported providers.
sub GetProviders {
	# Get supported providers.
	open(PROVIDERS, "/usr/bin/ddns list-providers |");

	# Create new array to store the providers.
	my @providers = ();

	while (<PROVIDERS>) {
		my $provider = $_;

		# Remove following newlines.
		chomp($provider);

		# Add provider to the array.
		push(@providers, $provider);
	}

	close(PROVIDERS);

	# Return our array.
	return @providers;
}
