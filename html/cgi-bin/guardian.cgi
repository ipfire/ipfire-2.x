#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2014  IPFire Team  <info@ipfire.org>                          #
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
use Locale::Country;

# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::colouryellow} );
undef (@dummy);

my $string=();
my $memory=();
my @memory=();
my @pid=();
my @guardian=();

# Path to the guardian.ignore file.
my $ignorefile ='/var/ipfire/guardian/guardian.ignore';

our %netsettings = ();
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

our %color = ();
our %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

# Pakfire meta file for owncloud.
# (File exists when the addon is installed.)
my $owncloud_meta = "/opt/pakfire/db/meta/meta-owncloud";

our %settings = ();

$settings{'ACTION'} = '';

$settings{'GUARDIAN_ENABLED'} = 'off';
$settings{'GUARDIAN_ENABLE_SNORT'} = 'on';
$settings{'GUARDIAN_ENABLE_SSH'} = 'on';
$settings{'GUARDIAN_ENABLE_HTTPD'} = 'on';
$settings{'GUARDIAN_LOGLEVEL'} = 'info';
$settings{'GUARDIAN_BLOCKCOUNT'} = '3';
$settings{'GUARDIAN_BLOCKTIME'} = '86400';
$settings{'GUARDIAN_LOGFILE'} = '/var/log/guardian/guardian.log';
$settings{'GUARDIAN_SNORT_ALERTFILE'} = '/var/log/snort/alert';
$settings{'GUARDIAN_PRIORITY_LEVEL'} = '3';

# Default settings for owncloud if installed.
if ( -e "$owncloud_meta") {
	$settings{'GUARDIAN_ENABLE_OWNCLOUD'} = 'off';
}

my $errormessage = '';

&Header::showhttpheaders();

# Get GUI values.
&Header::getcgihash(\%settings);

# Check if guardian is running and grab some stats.
&daemonstats();
my $pid = @pid[0];

## Perform input checks and save settings.
#
if ($settings{'ACTION'} eq $Lang::tr{'save'}) {
	# Check for valid blocktime.
	unless(($settings{'GUARDIAN_BLOCKTIME'} =~ /^\d+$/) && ($settings{'GUARDIAN_BLOCKTIME'} ne "0")) {
			$errormessage = "$Lang::tr{'guardian invalid blocktime'}";
	}

	# Check if the bloccount is valid.
	unless(($settings{'GUARDIAN_BLOCKCOUNT'} =~ /^\d+$/) && ($settings{'GUARDIAN_BLOCKCOUNT'} ne "0")) {
			$errormessage = "$Lang::tr{'guardian invalid blockcount'}";
	}

	# Check Logfile.
	unless($settings{'GUARDIAN_LOGFILE'} =~ /^[a-zA-Z0-9\.\/]+$/) {
		$errormessage = "$Lang::tr{'guardian invalid logfile'}";
	}

	# Check input for snort alert file.
	unless($settings{'GUARDIAN_SNORT_ALERTFILE'} =~ /^[a-zA-Z0-9\.\/]+$/) {
		$errormessage = "$Lang::tr{'guardian invalid alertfile'}";
	}

	# Only continue if no error message has been set.
	if($errormessage eq '') {
		# Write configuration settings to file.
		&General::writehash("${General::swroot}/guardian/settings", \%settings);

		# Update configuration files.
		&BuildConfiguration();
	}

## Add a new entry to the ignore file.
#
} elsif ($settings{'ACTION'} eq $Lang::tr{'add'}) {

	# Check if any input has been performed.
	if ($settings{'NEW_IGNORE_ENTRY'} ne '') {

		# Check if the given input is no valid IP-address or IP-address with subnet, display an error message.
		if ((!&General::validip($settings{'NEW_IGNORE_ENTRY'})) && (!&General::validipandmask($settings{'NEW_IGNORE_ENTRY'}))) {
			$errormessage = "$Lang::tr{'guardian invalid address or subnet'}";
		}
	} else {
		$errormessage = "$Lang::tr{'guardian empty input'}";
	}

	# Go further if there was no error.
	if ($errormessage eq '') {
		my $new_entry = $settings{'NEW_IGNORE_ENTRY'};

		# Open file for appending the new entry.
		open (FILE, ">>$ignorefile") or die "Unable to open $ignorefile for writing";

		# Write the new entry to the ignore file.
		print FILE "$new_entry\n";
		close(FILE);
	}

	# Check if guardian is running.
	if ($pid > 0) {
		# Call guardianctrl to perform a reload.
		system("/usr/local/bin/guardianctrl reload &>/dev/null");
	}

## Remove entry from ignore list.
#
} elsif ($settings{'ACTION'} eq $Lang::tr{'remove'}) {
	my $id = 0;

	# Open ignorefile and read content.
	open(FILE, "<$ignorefile") or die "Unable to open $ignorefile.";
	my @current = <FILE>;
	close(FILE);

	# Re-open ignorefile for writing.
	open(FILE, ">$ignorefile") or die "Unable to open $ignorefile for writing";
	flock FILE, 2;

	# Read line by line from ignorefile and write them back except the line with the given ID.
	# So this line is missing in the new file and the entry has been deleted.
	foreach my $line (@current) {
		$id++;
		unless ($settings{'ID'} eq $id) {
			print FILE "$line";
		}
	}
	close(FILE);

	# Check if guardian is running.
	if ($pid > 0) {
		# Call guardianctrl to perform a reload.
		system("/usr/local/bin/guardianctrl reload &>/dev/null");
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

	# Get gateway address.
	my $gateway = &General::get_gateway();

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

                # Call helper to unblock address.
                system("/usr/local/bin/guardianctrl block $block &>/dev/null");
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

		# Call helper to unblock address.
		system("/usr/local/bin/guardianctrl unblock $unblock &>/dev/null");
	}

## Unblock all.
#
} elsif ($settings{'ACTION'} eq $Lang::tr{'unblock all'}) {

	# Call helper to flush iptables chain from guardian.
	system("/usr/local/bin/guardianctrl flush-chain &>/dev/null");
}

# Load settings from file.
&General::readhash("${General::swroot}/guardian/settings", \%settings);

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
	$checked{'GUARDIAN_ENABLE_SNORT'}{'off'} = '';
	$checked{'GUARDIAN_ENABLE_SNORT'}{'on'} = '';
	$checked{'GUARDIAN_ENABLE_SNORT'}{$settings{'GUARDIAN_ENABLE_SNORT'}} = "checked='checked'";
	$checked{'GUARDIAN_ENABLE_SSH'}{'off'} = '';
	$checked{'GUARDIAN_ENABLE_SSH'}{'on'} = '';
	$checked{'GUARDIAN_ENABLE_SSH'}{$settings{'GUARDIAN_ENABLE_SSH'}} = "checked='checked'";
	$checked{'GUARDIAN_ENABLE_HTTPD'}{'off'} = '';
	$checked{'GUARDIAN_ENABLE_HTTPD'}{'on'} = '';
	$checked{'GUARDIAN_ENABLE_HTTPD'}{$settings{'GUARDIAN_ENABLE_HTTPD'}} = "checked='checked'";
	$checked{'GUARDIAN_ENABLE_OWNCLOUD'}{'off'} = '';
	$checked{'GUARDIAN_ENABLE_OWNCLOUD'}{'on'} = '';
	$checked{'GUARDIAN_ENABLE_OWNCLOUD'}{$settings{'GUARDIAN_ENABLE_OWNCLOUD'}} = "checked='checked'";

	$selected{'GUARDIAN_LOGLEVEL'}{$settings{'GUARDIAN_LOGLEVEL'}} = 'selected';
	$selected{'GUARDIAN_PRIORITY_LEVEL'}{$settings{'GUARDIAN_PRIORITY_LEVEL'}} = 'selected';

	&Header::openpage($Lang::tr{'guardian configuration'}, 1, '');
	&Header::openbigbox('100%', 'left', '', $errormessage);

	# Print errormessage if there is one.
	if ($errormessage) {
		&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
		print "<font class='base'>$errormessage&nbsp;</font>\n";
		&Header::closebox();
	}


	# Draw current guardian state.
	&Header::openbox('100%', 'center', $Lang::tr{'guardian'});

	# Get current status of guardian.
	&daemonstats();
	$pid = @pid[0];

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
					<td bgcolor='$color{'color22'}' align='center'>@pid[0]</td>
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
				<td width='20%' class='base'>$Lang::tr{'guardian enabled'}:</td>
				<td><input type='checkbox' name='GUARDIAN_ENABLED' $checked{'GUARDIAN_ENABLED'}{'on'} /></td>
			</tr>
			<tr>
				<td colspan='2'><br></td>
			</tr>
			<tr>
				<td width='20%' class='base'>$Lang::tr{'guardian watch snort alertfile'}</td>
				<td align='left'>on <input type='radio' name='GUARDIAN_ENABLE_SNORT' value='on' $checked{'GUARDIAN_ENABLE_SNORT'}{'on'} /> /
				<input type='radio' name='GUARDIAN_ENABLE_SNORT' value='off' $checked{'GUARDIAN_ENABLE_SNORT'}{'off'} /> off</td>
			</tr>
			<tr>
				<td width='20%' class='base'>$Lang::tr{'guardian block ssh brute-force'}</td>
				<td align='left'>on <input type='radio' name='GUARDIAN_ENABLE_SSH' value='on' $checked{'GUARDIAN_ENABLE_SSH'}{'on'} /> /
				<input type='radio' name='GUARDIAN_ENABLE_SSH' value='off' $checked{'GUARDIAN_ENABLE_SSH'}{'off'} /> off</td>
			</tr>
			<tr>
				<td width='20%' class='base'>$Lang::tr{'guardian block httpd brute-force'}</td>
				<td align='left'>on <input type='radio' name='GUARDIAN_ENABLE_HTTPD' value='on' $checked{'GUARDIAN_ENABLE_HTTPD'}{'on'} /> /
				<input type='radio' name='GUARDIAN_ENABLE_HTTPD' value='off' $checked{'GUARDIAN_ENABLE_HTTPD'}{'off'} /> off</td>
			</tr>
END
			# Display owncloud checkbox when the addon is installed.
			if ( -e "$owncloud_meta" ) {
				print"<tr>\n";
				print"<td width='20%' class='base'>$Lang::tr{'guardian block owncloud brute-force'}</td>\n";
				print"<td align='left'>on <input type='radio' name='GUARDIAN_ENABLE_OWNCLOUD' value='on' $checked{'GUARDIAN_ENABLE_OWNCLOUD'}{'on'} /> /\n";
				print"<input type='radio' name='GUARDIAN_ENABLE_OWNCLOUD' value='off' $checked{'GUARDIAN_ENABLE_OWNCLOUD'}{'off'} /> off</td>\n";
				print"</tr>\n";
			}
	print <<END;
			<tr>
				<td colspan='2'><br></td>
			</tr>
			<tr>
				<td align='left' width='20%'>$Lang::tr{'guardian loglevel'}:</td>
				<td><select name='GUARDIAN_LOGLEVEL'>
					<option value='off' $selected{'GUARDIAN_LOGLEVEL'}{'off'}>off</option>
					<option value='info' $selected{'GUARDIAN_LOGLEVEL'}{'info'}>info</option>
					<option value='debug' $selected{'GUARDIAN_LOGLEVEL'}{'debug'}>debug</option>
				</select></td>
			</tr>
			<tr>
				<td colspan='2'><br></td>
			</tr>
			<tr>
				<td align='left' width='20%'>$Lang::tr{'guardian priority level'}:</td>
				<td><select name='GUARDIAN_PRIORITY_LEVEL'>
					<option value='1' $selected{'GUARDIAN_PRIORITY_LEVEL'}{'1'}>1</option>
					<option value='2' $selected{'GUARDIAN_PRIORITY_LEVEL'}{'2'}>2</option>
					<option value='3' $selected{'GUARDIAN_PRIORITY_LEVEL'}{'3'}>3</option>
					<option value='4' $selected{'GUARDIAN_PRIORITY_LEVEL'}{'4'}>4</option>
				</select></td>
			</tr>
			<tr>
				<td colspan='2'><br></td>
			</tr>
			<tr>
				<td width='20%' class='base'>$Lang::tr{'guardian blockcount'}:</td>
				<td><input type='text' name='GUARDIAN_BLOCKCOUNT' value='$settings{'GUARDIAN_BLOCKCOUNT'}' size='5' /></td>
			</tr>
			<tr>
				<td width='20%' class='base'>$Lang::tr{'guardian blocktime'}:</td>
				<td><input type='text' name='GUARDIAN_BLOCKTIME' value='$settings{'GUARDIAN_BLOCKTIME'}' size='10' /></td>
			</tr>
			<tr>
                                <td width='20%' class='base'>$Lang::tr{'guardian logfile'}:</td>
                                <td><input type='text' name='GUARDIAN_LOGFILE' value='$settings{'GUARDIAN_LOGFILE'}' size='30' /></td>
                        </tr>
                        <tr>
                                <td width='20%' class='base'>$Lang::tr{'guardian snort alertfile'}:</td>
                                <td><input type='text' name='GUARDIAN_SNORT_ALERTFILE' value='$settings{'GUARDIAN_SNORT_ALERTFILE'}' size='30' /></td>
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
		<table width='60%'>
			<tr>
				<td colspan='2' class='base' bgcolor='$color{'color20'}'><b>$Lang::tr{'guardian ignored hosts'}</b></td>
			</tr>
END
			# Check if the guardian ignore file contains any content.
			if (-s $ignorefile) {

				# Open file and print contents.
				open FILE, $ignorefile or die "Could not open $ignorefile";

				my $id = 0;
				my $col = "";

				# Read file line by line and print out the elements.
				while( my $ignored_element = <FILE> )  {

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
						<td width='80%' class='base' $col>$ignored_element</td>
						<td width='20%' align='center' $col>
							<form method='post' name='$id' action='$ENV{'SCRIPT_NAME'}'>
								<input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' title='$Lang::tr{'remove'}' alt='$Lang::tr{'remove'}'>
								<input type='hidden' name='ID' value='$id'>
								<input type='hidden' name='ACTION' value='$Lang::tr{'remove'}'>
							</form>
						</td>
					</tr>
END
				}
			close (FILE);
			} else {
				# Print notice that currently no elements are stored in the ignore file.
				print "<tr>\n";
				print "<td class='base' colspan='2'>$Lang::tr{'guardian no entries'}</td>\n";
				print "</tr>\n";
			}

		print "</table>\n";

	# Section to add new elements to the ignore list.
	print <<END;
	<br>
	<div align='center'>
		<table width='60%'>
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<tr>
				<td width='30%'>$Lang::tr{'dnsforward add a new entry'}: </td>
				<td width='50%'><input type='text' name='NEW_IGNORE_ENTRY' value='' size='24' /></td>
				<td align='center' width='20%'><input type='submit' name='ACTION' value='$Lang::tr{'add'}' /></td>
			</tr>
			</form>
		</table>
	</div>
END

	&Header::closebox();
}

# Function to list currently bocked addresses from guardian and unblock them or add custom entries to block.
sub showBlockedBox() {
	&Header::openbox('100%', 'center', $Lang::tr{'guardian blocked hosts'});

	print <<END;
	<table width='60%'>
		<tr>
			<td colspan='2' class='base' bgcolor='$color{'color20'}'><b>$Lang::tr{'guardian blocked hosts'}</b></td>
		</tr>
END

		# Lauch function to get the currently blocked hosts.
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

	# If the loop only has been runs once the id still is "0", which means there are no
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

	# Lauch helper to get chains from iptables.
	open(FILE, "/usr/local/bin/guardianctrl get-chain |");

	# Read file line by line and print out the elements.
	foreach my $line (<FILE>) {

		# Skip descriptive lines.
		next if ($line =~ /^Chain/);
		next if ($line =~ /^ pkts/);

		# Generate array, based on the line content (seperator is a single or multiple space's)
		my @comps = split(/\s{1,}/, $line);
		my ($lead, $pkts, $bytes, $target, $prot, $opt, $in, $out, $source, $destination) = @comps;

		# Assign different variable names.
		my $blocked_host = $source;

		# Add host to our hosts array.
		push(@hosts, $blocked_host);
	}

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

	# We set this to 1 (enabled) to prevent guardian from blocking the ISP gateway.
	my $HostGatewayByte = "1";

	# Open configfile for writing.
	open(FILE, ">$configfile");

	print FILE "EnableSnortMonitoring\t\t$settings{'GUARDIAN_ENABLE_SNORT'}\n";
	print FILE "EnableSSHMonitoring\t\t$settings{'GUARDIAN_ENABLE_SSH'}\n";
	print FILE "EnableHTTPDMonitoring\t\t$settings{'GUARDIAN_ENABLE_HTTPD'}\n";

	# Check if owncloud settings should be written.
	if (exists $settings{'GUARDIAN_ENABLE_OWNCLOUD'}) {
		print FILE "EnableOwncloudMonitoring\t$settings{'GUARDIAN_ENABLE_OWNCLOUD'}\n";
	}

	print FILE "LogLevel\t\t\t$settings{'GUARDIAN_LOGLEVEL'}\n";
	print FILE "BlockCount\t\t\t$settings{'GUARDIAN_BLOCKCOUNT'}\n";
	print FILE "HostGatewayByte\t\t\t$HostGatewayByte\n";
	print FILE "LogFile\t\t\t\t$settings{'GUARDIAN_LOGFILE'}\n";
	print FILE "AlertFile\t\t\t$settings{'GUARDIAN_SNORT_ALERTFILE'}\n";
	print FILE "IgnoreFile\t\t\t$ignorefile\n";
	print FILE "TimeLimit\t\t\t$settings{'GUARDIAN_BLOCKTIME'}\n";
	print FILE "PriorityLevel\t\t\t$settings{'GUARDIAN_PRIORITY_LEVEL'}\n";

	close(FILE);

	# Check if guardian should be started or stopped.
	if($settings{'GUARDIAN_ENABLED'} eq 'on') {
		if($pid > 0) {
			# Call guardianctl to perform a reload.
			system("/usr/local/bin/guardianctrl reload &>/dev/null");
		} else {
			# Launch guardian.
			system("/usr/local/bin/guardianctrl start &>/dev/null");
		}
	} else {
		# Stop the daemon.
		system("/usr/local/bin/guardianctrl stop &>/dev/null");
	}
}
