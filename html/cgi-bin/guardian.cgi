#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2016  IPFire Team  <info@ipfire.org>                          #
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
use Guardian::Socket;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

#workaround to suppress a warning when a variable is used only once
my @dummy = (
	${Header::colourred},
	${Header::colourgreen}
);

undef (@dummy);

my $string=();
my $memory=();
my @memory=();
my @pid=();
my @guardian=();

# Path to the guardian.ignore file.
my $ignorefile ='/var/ipfire/guardian/guardian.ignore';

# Hash which contains the supported modules and the
# file locations on IPFire systems.
my %module_file_locations = (
	"HTTPD" => "/var/log/httpd/error_log",
	"SSH" => "/var/log/messages",
);

our %netsettings = ();
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

our %color = ();
our %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/ipfire/include/colors.txt", \%color);

# File declarations.
my $settingsfile = "${General::swroot}/guardian/settings";
my $ignoredfile = "${General::swroot}/guardian/ignored";

# Create empty settings and ignoredfile if they do not exist yet.
unless (-e "$settingsfile") { system("touch $settingsfile"); }
unless (-e "$ignoredfile") { system("touch $ignoredfile"); }

our %settings = ();
our %ignored  = ();

$settings{'ACTION'} = '';

$settings{'GUARDIAN_ENABLED'} = 'off';
$settings{'GUARDIAN_MONITOR_SSH'} = 'on';
$settings{'GUARDIAN_MONITOR_HTTPD'} = 'on';
$settings{'GUARDIAN_MONITOR_OWNCLOUD'} = '';
$settings{'GUARDIAN_LOG_FACILITY'} = 'syslog';
$settings{'GUARDIAN_LOGLEVEL'} = 'info';
$settings{'GUARDIAN_BLOCKCOUNT'} = '3';
$settings{'GUARDIAN_BLOCKTIME'} = '86400';
$settings{'GUARDIAN_FIREWALL_ACTION'} = 'DROP';
$settings{'GUARDIAN_LOGFILE'} = '/var/log/guardian/guardian.log';

my $errormessage = '';

&Header::showhttpheaders();

# Get GUI values.
&Header::getcgihash(\%settings);

# Check if guardian is running and grab some stats.
&daemonstats();
my $pid = $pid[0];

## Perform input checks and save settings.
#
if ($settings{'ACTION'} eq $Lang::tr{'save'}) {
	# Check for valid blocktime.
	unless(($settings{'GUARDIAN_BLOCKTIME'} =~ /^\d+$/) && ($settings{'GUARDIAN_BLOCKTIME'} ne "0")) {
			$errormessage = "$Lang::tr{'guardian invalid blocktime'}";
	}

	# Check if the blockcount is valid.
	unless(($settings{'GUARDIAN_BLOCKCOUNT'} =~ /^\d+$/) && ($settings{'GUARDIAN_BLOCKCOUNT'} ne "0")) {
			$errormessage = "$Lang::tr{'guardian invalid blockcount'}";
	}

	# Check Logfile.
	unless($settings{'GUARDIAN_LOGFILE'} =~ /^[a-zA-Z0-9\.\/]+$/) {
		$errormessage = "$Lang::tr{'guardian invalid logfile'}";
	}

	# Only continue if no error message has been set.
	if($errormessage eq '') {
		# Write configuration settings to file.
		&General::writehash("${General::swroot}/guardian/settings", \%settings);

		# Update configuration files.
		&BuildConfiguration();
	}

## Add/edit an entry to the ignore file.
#
} elsif (($settings{'ACTION'} eq $Lang::tr{'add'}) || ($settings{'ACTION'} eq $Lang::tr{'update'})) {

	# Check if any input has been performed.
	if ($settings{'IGNORE_ENTRY_ADDRESS'} ne '') {

		# Check if the given input is no valid IP-address or IP-address with subnet, display an error message.
		if ((!&General::validip($settings{'IGNORE_ENTRY_ADDRESS'})) && (!&General::validipandmask($settings{'IGNORE_ENTRY_ADDRESS'}))) {
			$errormessage = "$Lang::tr{'guardian invalid address or subnet'}";
		}
	} else {
		$errormessage = "$Lang::tr{'guardian empty input'}";
	}

	# Go further if there was no error.
	if ($errormessage eq '') {
		my %ignored = ();
		my $id;
		my $status;

		# Assign hash values.
		my $new_entry_address = $settings{'IGNORE_ENTRY_ADDRESS'};
		my $new_entry_remark = $settings{'IGNORE_ENTRY_REMARK'};

		# Read-in ignoredfile.
		&General::readhasharray($ignoredfile, \%ignored);

		# Check if we should edit an existing entry and got an ID.
		if (($settings{'ACTION'} eq $Lang::tr{'update'}) && ($settings{'ID'})) {
			# Assin the provided id.
			$id = $settings{'ID'};

			# Undef the given ID.
			undef($settings{'ID'});

			# Grab the configured status of the corresponding entry.
			$status = $ignored{$id}[2];
		} else {
			# Each newly added entry automatically should be enabled.
			$status = "enabled";

			# Generate the ID for the new entry.
			#
			# Sort the keys by their ID and store them in an array.
			my @keys = sort { $a <=> $b } keys %ignored;

			# Reverse the key array.
			my @reversed = reverse(@keys);

			# Obtain the last used id.
			my $last_id = @reversed[0];

			# Increase the last id by one and use it as id for the new entry.
			$id = ++$last_id;
		}

		# Add/Modify the entry to/in the ignored hash.
		$ignored{$id} = ["$new_entry_address", "$new_entry_remark", "$status"];

		# Write the changed ignored hash to the ignored file.
		&General::writehasharray($ignoredfile, \%ignored);

		# Regenerate the ignore file.
		&GenerateIgnoreFile();
	}

	# Check if guardian is running.
	if ($pid > 0) {
		# Send reload command through socket connection.
		&Guardian::Socket::Client("reload-ignore-list");
	}

## Toggle Enabled/Disabled for an existing entry on the ignore list.
#

} elsif ($settings{'ACTION'} eq $Lang::tr{'toggle enable disable'}) {
	my %ignored = ();

	# Only go further, if an ID has been passed.
	if ($settings{'ID'}) {
		# Assign the given ID.
		my $id = $settings{'ID'};

		# Undef the given ID.
		undef($settings{'ID'});

		# Read-in ignoredfile.
		&General::readhasharray($ignoredfile, \%ignored);

		# Grab the configured status of the corresponding entry.
		my $status = $ignored{$id}[2];

		# Switch the status.
		if ($status eq "disabled") {
			$status = "enabled";
		} else {
			$status = "disabled";
		}

		# Modify the status of the existing entry.
		$ignored{$id} = ["$ignored{$id}[0]", "$ignored{$id}[1]", "$status"];

		# Write the changed ignored hash to the ignored file.
		&General::writehasharray($ignoredfile, \%ignored);

		# Regenerate the ignore file.
		&GenerateIgnoreFile();

		# Check if guardian is running.
		if ($pid > 0) {
			# Send reload command through socket connection.
			&Guardian::Socket::Client("reload-ignore-list");
		}
	}

## Remove entry from ignore list.
#
} elsif ($settings{'ACTION'} eq $Lang::tr{'remove'}) {
	my %ignored = ();

	# Read-in ignoredfile.
	&General::readhasharray($ignoredfile, \%ignored);

	# Drop entry from the hash.
	delete($ignored{$settings{'ID'}});

	# Undef the given ID.
	undef($settings{'ID'});

	# Write the changed ignored hash to the ignored file.
	&General::writehasharray($ignoredfile, \%ignored);

	# Regenerate the ignore file.
	&GenerateIgnoreFile();

	# Check if guardian is running.
	if ($pid > 0) {
		# Send reload command through socket connection.
		&Guardian::Socket::Client("reload-ignore-list");
	}

## Block a user given address or subnet.
#
} elsif ($settings{'ACTION'} eq $Lang::tr{'block'}) {

	# Assign some temporary variables used for input validation.
	my $input = $settings{'ADDRESS_BLOCK'};
	my $green = $netsettings{'GREEN_ADDRESS'};
	my $blue = $netsettings{'BLUE_ADDRESS'};
	my $orange = $netsettings{'ORANGE_ADDRESS'};
	my $red = $netsettings{'RED_ADDRESS'};

	# File declarations.
	my $gatewayfile = "${General::swroot}/red/remote-ipaddress";

	# Get gateway address.
	my $gateway = &General::grab_address_from_file($gatewayfile);

	# Check if any input has been performed.
	if ($input eq '') {
		$errormessage = "$Lang::tr{'guardian empty input'}";
	}

	# Check if the given input is localhost (127.0.0.1).
	elsif ($input eq "127.0.0.1") {
		$errormessage = "$Lang::tr{'guardian blocking of this address is not allowed'}";
	}

	# Check if the given input is anywhere (0.0.0.0).
	elsif ($input eq "0.0.0.0") {
		$errormessage = "$Lang::tr{'guardian blocking of this address is not allowed'}";
	}

	# Check if the given input is one of the interface addresses or our gateway.
	elsif ($input eq "$green" || $input eq "$blue" || $input eq "$orange" || $input eq "$red" || $input eq "$gateway") {
		$errormessage = "$Lang::tr{'guardian blocking of this address is not allowed'}";
	}

	# Check if the given input is a valid IP address.
        elsif (!&General::validip($input)) {
                        $errormessage = "$Lang::tr{'guardian invalid address or subnet'}";
	}

        # Go further if there was no error.
        if ($errormessage eq '') {
                my $block = $settings{'ADDRESS_BLOCK'};

		# Send command to block the specified address through socket connection.
		&Guardian::Socket::Client("block $block");
        }

## Unblock address or subnet.
#
} elsif ($settings{'ACTION'} eq $Lang::tr{'unblock'}) {

	# Check if no empty input has been performed.
	if ($settings{'ADDRESS_UNBLOCK'} ne '') {

		# Check if the given input is no valid IP-address or IP-address with subnet, display an error message.
		if ((!&General::validip($settings{'ADDRESS_UNBLOCK'})) && (!&General::validipandmask($settings{'ADDRESS_UNBLOCK'}))) {
			$errormessage = "$Lang::tr{'guardian invalid address or subnet'}";
		}

	} else {
		$errormessage = "$Lang::tr{'guardian empty input'}";
	}

	# Go further if there was no error.
	if ($errormessage eq '') {
                my $unblock = $settings{'ADDRESS_UNBLOCK'};

		# Send command to unblock the given address through socket connection.
		&Guardian::Socket::Client("unblock $unblock");
	}

## Unblock all.
#
} elsif ($settings{'ACTION'} eq $Lang::tr{'unblock all'}) {

	# Send flush command through socket connection.
	&Guardian::Socket::Client("flush");
}

# Load settings from files.
&General::readhash("${General::swroot}/guardian/settings", \%settings);
&General::readhasharray("${General::swroot}/guardian/ignored", \%ignored);

# Call functions to generate whole page.
&showMainBox();
&showIgnoreBox();

# Display area only if guardian is running.
if ( ($memory != 0) && ($pid > 0) ) {
	&showBlockedBox();
}

# Function to display the status of guardian and allow base configuration.
sub showMainBox() {
	my %checked = ();
	my %selected = ();

	$checked{'GUARDIAN_ENABLED'}{'on'} = '';
	$checked{'GUARDIAN_ENABLED'}{'off'} = '';
	$checked{'GUARDIAN_ENABLED'}{$settings{'GUARDIAN_ENABLED'}} = 'checked';
	$checked{'GUARDIAN_MONITOR_SSH'}{'off'} = '';
	$checked{'GUARDIAN_MONITOR_SSH'}{'on'} = '';
	$checked{'GUARDIAN_MONITOR_SSH'}{$settings{'GUARDIAN_MONITOR_SSH'}} = "checked='checked'";
	$checked{'GUARDIAN_MONITOR_HTTPD'}{'off'} = '';
	$checked{'GUARDIAN_MONITOR_HTTPD'}{'on'} = '';
	$checked{'GUARDIAN_MONITOR_HTTPD'}{$settings{'GUARDIAN_MONITOR_HTTPD'}} = "checked='checked'";
	$checked{'GUARDIAN_MONITOR_OWNCLOUD'}{'off'} = '';
	$checked{'GUARDIAN_MONITOR_OWNCLOUD'}{'on'} = '';
	$checked{'GUARDIAN_MONITOR_OWNCLOUD'}{$settings{'GUARDIAN_MONITOR_OWNCLOUD'}} = "checked='checked'";

	$selected{'GUARDIAN_LOG_FACILITY'}{$settings{'GUARDIAN_LOG_FACILITY'}} = 'selected';
	$selected{'GUARDIAN_LOGLEVEL'}{$settings{'GUARDIAN_LOGLEVEL'}} = 'selected';
	$selected{'GUARDIAN_FIREWALL_ACTION'}{$settings{'GUARDIAN_FIREWALL_ACTION'}} = 'selected';

	&Header::openpage($Lang::tr{'guardian configuration'}, 1, '');
	&Header::openbigbox('100%', 'left', '', $errormessage);

	# Print errormessage if there is one.
	if ($errormessage) {
		&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
		print "<font class='base'>$errormessage&nbsp;</font>\n";
		&Header::closebox();
	}

	### Java Script ###
	print<<END;
	<script>
		var update_options = function() {

			var logfacility = \$("#GUARDIAN_LOG_FACILITY").val();
			var loglevel = \$("#GUARDIAN_LOGLEVEL").val();

			if (logfacility === undefined)
				return;

			if (loglevel === undefined)
				return;

			// Show / Hide input for specifying the path to the logfile.
			if (logfacility === "file") {
				\$(".GUARDIAN_LOGFILE").show();
			} else {
				\$(".GUARDIAN_LOGFILE").hide();
			}

			// Show / Hide loglevel debug if the facility is set to syslog.
			if (logfacility === "syslog") {
				\$("#loglevel_debug").hide();
			} else {
				\$("#loglevel_debug").show();
			}

			// Show / Hide logfacility syslog if the loglevel is set to debug.
			if (loglevel === "debug") {
				\$("#logfacility_syslog").hide();
			} else {
				\$("#logfacility_syslog").show();
			}
		};

		\$(document).ready(function() {
			\$("#GUARDIAN_LOG_FACILITY").change(update_options);
			\$("#GUARDIAN_LOGLEVEL").change(update_options);
			update_options();
		});
	</script>
END



	# Draw current guardian state.
	&Header::openbox('100%', 'center', $Lang::tr{'guardian'});

	# Get current status of guardian.
	&daemonstats();
	$pid = $pid[0];

	# Display some useful information related to guardian, if daemon is running.
	if ( ($memory != 0) && ($pid > 0) ){
		print <<END;
			<table width='95%' cellspacing='0' class='tbl'>
				<tr>
					<th bgcolor='$color{'color20'}' colspan='3' align='left'><strong>$Lang::tr{'guardian service'}</strong></th>
				</tr>
				<tr>
					<td class='base'>$Lang::tr{'guardian daemon'}</td>
					<td align='center' colspan='2' width='75%' bgcolor='${Header::colourgreen}'><font color='white'><strong>$Lang::tr{'running'}</strong></font></td>
				</tr>
				<tr>
					<td class='base'></td>
					<td bgcolor='$color{'color20'}' align='center'><strong>PID</strong></td>
					<td bgcolor='$color{'color20'}' align='center'><strong>$Lang::tr{'memory'}</strong></td>
				</tr>
				<tr>
					<td class='base'></td>
					<td bgcolor='$color{'color22'}' align='center'>$pid</td>
					<td bgcolor='$color{'color22'}' align='center'>$memory KB</td>
				</tr>
			</table>
END
	} else {
		# Otherwise display a hint that the service is not launched.
		print <<END;
			<table width='95%' cellspacing='0' class='tbl'>
				<tr>
					<th bgcolor='$color{'color20'}' colspan='3' align='left'><strong>$Lang::tr{'guardian service'}</strong></th>
				</tr>
				<tr>
					<td class='base'>$Lang::tr{'guardian daemon'}</td>
					<td align='center' width='75%' bgcolor='${Header::colourred}'><font color='white'><strong>$Lang::tr{'stopped'}</strong></font></td>
				</tr>
			</table>
END
	}

	&Header::closebox();

	# Draw elements for guardian configuration.
	&Header::openbox('100%', 'center', $Lang::tr{'guardian configuration'});

	print <<END;
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>

		<table width='95%'>
			<tr>
				<td colspan='2' class='base' bgcolor='$color{'color20'}'><b>$Lang::tr{'guardian common settings'}</b></td>
			</tr>

			<tr>
				<td width='25%' class='base'>$Lang::tr{'guardian enabled'}:</td>
				<td><input type='checkbox' name='GUARDIAN_ENABLED' $checked{'GUARDIAN_ENABLED'}{'on'} /></td>
			</tr>

			<tr>
				<td colspan='2'><br></td>
			</tr>

			<tr>
				<td width='25%' class='base'>$Lang::tr{'guardian block ssh brute-force'}</td>
				<td align='left'>on <input type='radio' name='GUARDIAN_MONITOR_SSH' value='on' $checked{'GUARDIAN_MONITOR_SSH'}{'on'} /> /
				<input type='radio' name='GUARDIAN_MONITOR_SSH' value='off' $checked{'GUARDIAN_MONITOR_SSH'}{'off'} /> off</td>
			</tr>

			<tr>
				<td width='25%' class='base'>$Lang::tr{'guardian block httpd brute-force'}</td>
				<td align='left'>on <input type='radio' name='GUARDIAN_MONITOR_HTTPD' value='on' $checked{'GUARDIAN_MONITOR_HTTPD'}{'on'} /> /
				<input type='radio' name='GUARDIAN_MONITOR_HTTPD' value='off' $checked{'GUARDIAN_MONITOR_HTTPD'}{'off'} /> off</td>
			</tr>

			<tr>
				<td colspan='2'><br></td>
			</tr>

			<tr>
				<td align='left' width='20%'>$Lang::tr{'guardian logfacility'}:</td>
				<td width='25%'><select id='GUARDIAN_LOG_FACILITY' name='GUARDIAN_LOG_FACILITY'>
					<option id='logfacility_syslog' value='syslog' $selected{'GUARDIAN_LOG_FACILITY'}{'syslog'}>$Lang::tr{'guardian logtarget_syslog'}</option>
					<option id='logfacility_file' value='file' $selected{'GUARDIAN_LOG_FACILITY'}{'file'}>$Lang::tr{'guardian logtarget_file'}</option>
					<option id='logfacility_console' value='console' $selected{'GUARDIAN_LOG_FACILITY'}{'console'}>$Lang::tr{'guardian logtarget_console'}</option>
				</select></td>

				<td align='left' width='20%'>$Lang::tr{'guardian loglevel'}:</td>
				<td width='25%'><select id='GUARDIAN_LOGLEVEL' name='GUARDIAN_LOGLEVEL'>
					<option id='loglevel_off' value='off' $selected{'GUARDIAN_LOGLEVEL'}{'off'}>$Lang::tr{'guardian loglevel_off'}</option>
					<option id='loglevel_info' value='info' $selected{'GUARDIAN_LOGLEVEL'}{'info'}>$Lang::tr{'guardian loglevel_info'}</option>
					<option id='loglevel_debug' value='debug' $selected{'GUARDIAN_LOGLEVEL'}{'debug'}>$Lang::tr{'guardian loglevel_debug'}</option>
				</select></td>
			</tr>

			<tr class="GUARDIAN_LOGFILE">
				<td colspan='2'><br></td>
			</tr>

			<tr class="GUARDIAN_LOGFILE">
				<td width='25%' class='base'>$Lang::tr{'guardian logfile'}:</td>
				<td><input type='text' name='GUARDIAN_LOGFILE' value='$settings{'GUARDIAN_LOGFILE'}' size='30' /></td>
			</tr>

			<tr>
				<td colspan='2'><br></td>
			</tr>

			<tr>
				<td width='25%' class='base'>$Lang::tr{'guardian firewallaction'}:</td>
				<td><select name='GUARDIAN_FIREWALL_ACTION'>
					<option value='DROP' $selected{'GUARDIAN_FIREWALL_ACTION'}{'DROP'}>Drop</option>
					<option value='REJECT' $selected{'GUARDIAN_FIREWALL_ACTION'}{'REJECT'}>Reject</option>
				</select></td>

				<td width='25%' class='base'>$Lang::tr{'guardian blockcount'}:</td>
				<td><input type='text' name='GUARDIAN_BLOCKCOUNT' value='$settings{'GUARDIAN_BLOCKCOUNT'}' size='5' /></td>
			</tr>

			<tr>
				<td colspan='2'><br></td>
			</tr>

			<tr>
				<td width='25%' class='base'>$Lang::tr{'guardian blocktime'}:</td>
				<td><input type='text' name='GUARDIAN_BLOCKTIME' value='$settings{'GUARDIAN_BLOCKTIME'}' size='10' /></td>
			</tr>

		</table>
END

	print <<END;
		<hr>

		<table width='95%'>
			<tr>
				<td>&nbsp;</td>
				<td align='center'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
				<td>&nbsp;</td>
			</tr>
		</table>
	</form>
END

	&Header::closebox();
}

# Function to show elements of the guardian ignorefile and allow to add or remove single members of it.
sub showIgnoreBox() {
        &Header::openbox('100%', 'center', $Lang::tr{'guardian ignored hosts'});

	print <<END;
		<table width='80%'>
			<tr>
				<td class='base' bgcolor='$color{'color20'}'><b>$Lang::tr{'ip address'}</b></td>
				<td class='base' bgcolor='$color{'color20'}'><b>$Lang::tr{'remark'}</b></td>
				<td class='base' colspan='3' bgcolor='$color{'color20'}'></td>
			</tr>
END
			# Check if some hosts have been added to be ignored.
			if (keys (%ignored)) {
				my $col = "";

				# Loop through all entries of the hash.
				while( (my $key) = each %ignored)  {
					# Assign data array positions to some nice variable names.
					my $address = $ignored{$key}[0];
					my $remark = $ignored{$key}[1];
					my $status  = $ignored{$key}[2];

					# Check if the key (id) number is even or not.
					if ($settings{'ID'} eq $key) {
						$col="bgcolor='${Header::colouryellow}'";
					} elsif ($key % 2) {
						$col="bgcolor='$color{'color22'}'";
					} else {
						$col="bgcolor='$color{'color20'}'";
					}

					# Choose icon for the checkbox.
					my $gif;
					my $gdesc;

					# Check if the status is enabled and select the correct image and description.
					if ($status eq 'enabled' ) {
						$gif = 'on.gif';
						$gdesc = $Lang::tr{'click to disable'};
					} else {
						$gif = 'off.gif';
						$gdesc = $Lang::tr{'click to enable'};
					}

					print <<END;
					<tr>
						<td width='20%' class='base' $col>$address</td>
						<td width='65%' class='base' $col>$remark</td>

						<td align='center' $col>
							<form method='post' action='$ENV{'SCRIPT_NAME'}'>
								<input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}' />
								<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' alt='$gdesc' title='$gdesc' />
								<input type='hidden' name='ID' value='$key' />
							</form>
						</td>

						<td align='center' $col>
							<form method='post' action='$ENV{'SCRIPT_NAME'}'>
								<input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
								<input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' />
								<input type='hidden' name='ID' value='$key' />
							</form>
						</td>

						<td align='center' $col>
							<form method='post' name='$key' action='$ENV{'SCRIPT_NAME'}'>
								<input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' title='$Lang::tr{'remove'}' alt='$Lang::tr{'remove'}'>
								<input type='hidden' name='ID' value='$key'>
								<input type='hidden' name='ACTION' value='$Lang::tr{'remove'}'>
							</form>
						</td>
					</tr>
END
				}
			} else {
				# Print notice that currently no hosts are ignored.
				print "<tr>\n";
				print "<td class='base' colspan='2'>$Lang::tr{'guardian no entries'}</td>\n";
				print "</tr>\n";
			}

		print "</table>\n";

	# Section to add new elements or edit existing ones.
	print <<END;
	<br>
	<hr>
	<br>

	<div align='center'>
		<table width='100%'>
END

	# Assign correct headline and button text.
	my $buttontext;
	my $entry_address;
	my $entry_remark;

	# Check if an ID (key) has been given, in this case an existing entry should be edited.
	if ($settings{'ID'} ne '') {
		$buttontext = $Lang::tr{'update'};
		print "<tr><td class='boldbase' colspan='3'><b>$Lang::tr{'update'}</b></td></tr>\n";

		# Grab address and remark for the given key.
		$entry_address = $ignored{$settings{'ID'}}[0];
		$entry_remark = $ignored{$settings{'ID'}}[1];
	} else {
		$buttontext = $Lang::tr{'add'};
		print "<tr><td class='boldbase' colspan='3'><b>$Lang::tr{'dnsforward add a new entry'}</b></td></tr>\n";
	}

	print <<END;
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='ID' value='$settings{'ID'}'>
			<tr>
				<td width='30%'>$Lang::tr{'ip address'}: </td>
				<td width='50%'><input type='text' name='IGNORE_ENTRY_ADDRESS' value='$entry_address' size='24' /></td>

				<td width='30%'>$Lang::tr{'remark'}: </td>
				<td wicth='50%'><input type='text' name=IGNORE_ENTRY_REMARK value='$entry_remark' size='24' /></td>
				<td align='center' width='20%'><input type='submit' name='ACTION' value='$buttontext' /></td>
			</tr>
			</form>
		</table>
	</div>
END

	&Header::closebox();
}

# Function to list currently blocked addresses from guardian and unblock them or add custom entries to block.
sub showBlockedBox() {
	&Header::openbox('100%', 'center', $Lang::tr{'guardian blocked hosts'});

	print <<END;
	<table width='60%'>
		<tr>
			<td colspan='2' class='base' bgcolor='$color{'color20'}'><b>$Lang::tr{'guardian blocked hosts'}</b></td>
		</tr>
END

		# Launch function to get the currently blocked hosts.
		my @blocked_hosts = &GetBlockedHosts();

		my $id = 0;
		my $col = "";

		# Loop through our blocked hosts array.
		foreach my $blocked_host (@blocked_hosts) {

			# Increase id number for each element in the ignore file.
			$id++;

			# Check if the id number is even or not.
			if ($id % 2) {
				$col="bgcolor='$color{'color22'}'";
			} else {
				$col="bgcolor='$color{'color20'}'";
			}

			print <<END;
			<tr>
				<td width='80%' class='base' $col><a href='/cgi-bin/ipinfo.cgi?ip=$blocked_host'>$blocked_host</a></td>
				<td width='20%' align='center' $col>
					<form method='post' name='frmb$id' action='$ENV{'SCRIPT_NAME'}'>
						<input type='image' name='$Lang::tr{'unblock'}' src='/images/delete.gif' title='$Lang::tr{'unblock'}' alt='$Lang::tr{'unblock'}'>
						<input type='hidden' name='ADDRESS_UNBLOCK' value='$blocked_host'>
						<input type='hidden' name='ACTION' value='$Lang::tr{'unblock'}'>
					</form>
				</td>
			</tr>
END
		}

	# If the loop only has been run once the id still is "0", which means there are no
	# additional entries (blocked hosts) in the iptables chain.
	if ($id == 0) {

		# Print notice that currently no hosts are blocked.
		print "<tr>\n";
		print "<td class='base' colspan='2'>$Lang::tr{'guardian no entries'}</td>\n";
		print "</tr>\n";
	}

	print "</table>\n";

        # Section for a manual block of an IP-address.
	print <<END;
	<br>
	<div align='center'>
		<table width='60%' border='0'>
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<tr>
				<td width='30%'>$Lang::tr{'guardian block a host'}: </td>
				<td width='40%'><input type='text' name='ADDRESS_BLOCK' value='' size='24' /></td>
				<td align='center' width='15%'><input type='submit' name='ACTION' value='$Lang::tr{'block'}'></td>
				<td align='center' width='15%'><input type='submit' name='ACTION' value='$Lang::tr{'unblock all'}'></td>
			</tr>
			</form>
		</table>
	</div>
END

	&Header::closebox();
}

&Header::closebigbox();
&Header::closepage();

# Function to check if guardian has been started.
# Grab process id and consumed memory if the daemon is running.
sub daemonstats() {
        $memory = 0;
        # for pid and memory
        open(FILE, '/usr/local/bin/addonctrl guardian status | ');
        @guardian = <FILE>;
        close(FILE);
        $string = join("", @guardian);
        $string =~ s/[a-z_]//gi;
        $string =~ s/\[[0-1]\;[0-9]+//gi;
        $string =~ s/[\(\)\.]//gi;
        $string =~ s/  //gi;
        $string =~ s/\e//gi;
        @pid = split(/\s/,$string);
        if (open(FILE, "/proc/$pid[0]/statm")){
                my $temp = <FILE>;
                @memory = split(/ /,$temp);
                close(FILE);
        }
        $memory+=$memory[0];
}

sub GetBlockedHosts() {
	# Create new, empty array.
	my @hosts;

	# Launch helper to get chains from iptables.
	open (FILE, '/usr/local/bin/getipstat | ');

	# Loop through the entire output.
	while (<FILE>) {
		my $line = $_;

		# Search for the guardian chain and extract
		# the lines between it and the next empty line
		# which is placed before the next firewall
		# chain starts.
		if ($line =~ /^Chain GUARDIAN/ .. /^\s*$/) {
			# Skip descriptive lines.
			next if ($line =~ /^Chain/);
			next if ($line =~ /^ pkts/);

			# Generate array, based on the line content (separator is a single or multiple space)
			my @comps = split(/\s{1,}/, $line);
			my ($lead, $pkts, $bytes, $target, $prot, $opt, $in, $out, $source, $destination) = @comps;

			# Assign different variable names.
			my $blocked_host = $source;

			# Add host to our hosts array.
			if ($blocked_host) {
				push(@hosts, $blocked_host);
			}
		}
	}

	# Close filehandle.
	close(FILE);

	# Convert entries, sort them, write back and store the sorted entries into new array.
	my @sorted = map  { $_->[0] }
             sort { $a->[1] <=> $b->[1] }
             map  { [$_, int sprintf("%03.f%03.f%03.f%03.f", split(/\./, $_))] }
             @hosts;

	# Return our sorted list.
	return @sorted
}

sub BuildConfiguration() {
	my %settings = ();
	&General::readhash("${General::swroot}/guardian/settings", \%settings);

	my $configfile = "${General::swroot}/guardian/guardian.conf";

	# Create the configfile if none exists yet.
	unless (-e "$configfile") { system("touch $configfile"); }

	# Open configfile for writing.
	open(FILE, ">$configfile");

	# Config file header.
	print FILE "# Autogenerated configuration file.\n";
	print FILE "# All user modifications will be overwritten.\n\n";

	# Settings for the logging mechanism.
	print FILE "# Log settings.\n";
	print FILE "LogFacility = $settings{'GUARDIAN_LOG_FACILITY'}\n";

	if ($settings{'GUARDIAN_LOG_FACILITY'} eq "file") {
		print FILE "LogFile = $settings{'GUARDIAN_LOGFILE'}\n";
	}

	print FILE "LogLevel = $settings{'GUARDIAN_LOGLEVEL'}\n\n";

	# IPFire related static settings.
	print FILE "# IPFire related settings.\n";
	print FILE "FirewallEngine = IPtables\n";
	print FILE "SocketOwner = nobody:nobody\n";
	print FILE "IgnoreFile = $ignorefile\n\n";

	# Configured block values.
	print FILE "# Configured block settings.\n";
	print FILE "BlockCount = $settings{'GUARDIAN_BLOCKCOUNT'}\n";
	print FILE "BlockTime = $settings{'GUARDIAN_BLOCKTIME'}\n";
	print FILE "FirewallAction = $settings{'GUARDIAN_FIREWALL_ACTION'}\n\n";

	# Enabled modules.
	# Loop through whole settings hash.
	print FILE "# Enabled modules.\n";
	foreach my $option (keys %settings) {
		# Search for enabled modules.
		if ($option =~ /GUARDIAN_MONITOR_(.*)/) {
			# Skip if module is not enabled.
			next unless($settings{$option} eq "on");

			# Skip module if no file location is available.
			next unless(exists($module_file_locations{$1}));

			# Add enabled module and defined path to the config file.
			print FILE "Monitor_$1 = $module_file_locations{$1}\n";
		}
	}

	# Module settings.
	print FILE "\n# Module settings.\n";
	close(FILE);

	# Generate ignore file.
	&GenerateIgnoreFile();

	# Check if guardian should be started or stopped.
	if($settings{'GUARDIAN_ENABLED'} eq 'on') {
		if($pid > 0) {
			# Send reload command through socket connection.
			&Guardian::Socket::Client("reload");
		} else {
			# Launch guardian.
			system("/usr/local/bin/addonctrl guardian start &>/dev/null");
		}
	} else {
		# Stop the daemon.
		system("/usr/local/bin/addonctrl guardian stop &>/dev/null");
	}
}

sub GenerateIgnoreFile() {
	my %ignored = ();

	# Read-in ignoredfile.
	&General::readhasharray($ignoredfile, \%ignored);

	# Create the guardian.ignore file if not exist yet.
	unless (-e "$ignorefile") { system("touch $ignorefile"); }

	# Open ignorefile for writing.
	open(FILE, ">$ignorefile");

	# Config file header.
	print FILE "# Autogenerated configuration file.\n";
	print FILE "# All user modifications will be overwritten.\n\n";

	# Add IFPire interfaces and gateway to the ignore file.
	#
	# Assign some temporary variables for the IPFire interfaces.
	my $green = $netsettings{'GREEN_ADDRESS'};
	my $blue = $netsettings{'BLUE_ADDRESS'};
	my $orange = $netsettings{'ORANGE_ADDRESS'};

	# File declarations.
	my $public_address_file = "${General::swroot}/red/local-ipaddress";
	my $gatewayfile = "${General::swroot}/red/remote-ipaddress";

	# Write the obtained addresses to the ignore file.
	print FILE "# IPFire local interfaces.\n";
	print FILE "$green\n";

	# Check if a blue interface exists.
	if ($blue) {
		# Add blue address.
		print FILE "$blue\n";
	}

	# Check if an orange interface exists.
	if ($orange) {
		# Add orange address.
		print FILE "$orange\n";
	}

	print FILE "\n# IPFire red interface, gateway and used DNS-servers.\n";
	print FILE "# Include the corresponding files to obtain the addresses.\n";
	print FILE "Include_File = $public_address_file\n";
	print FILE "Include_File = $gatewayfile\n";

	# Add all user defined hosts and networks to the ignore file.
	#
	# Check if the hash contains any elements.
	if (keys (%ignored)) {
		# Write headline.
		print FILE "\n# User defined hosts/networks.\n";

		# Loop through the entire hash and write the host/network
		# and remark to the ignore file.
		while ( (my $key) = each %ignored) {
			my $address = $ignored{$key}[0];
			my $remark = $ignored{$key}[1];
			my $status = $ignored{$key}[2];

			# Check if the status of the entry is "enabled".
			if ($status eq "enabled") {
				# Check if the address/network is valid.
				if ((&General::validip($address)) || (&General::validipandmask($address))) {
					# Write the remark to the file.
					print FILE "# $remark\n";

					# Write the address/network to the ignore file.
					print FILE "$address\n\n";
				}
			}
                }
	}

	close(FILE);
}
