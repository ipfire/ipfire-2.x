#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2012  IPFire Team  <info@ipfire.org>                          #
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

# DEVICE,ENABLED,MODE,WPA_MODE,SSID,PSK,PRIO,AUTH,ANONYMOUS,IDENTITY,PASSWORD
# wlan0,on,WPA2,,Use This One Mum,ThisIsTheKey,2,TTLS,anonymous,username,password

use strict;

# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::colouryellow} );
undef (@dummy);

# Files used
my $setting = "${General::swroot}/main/settings";
our $datafile = "${General::swroot}/ethernet/wireless";

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

our %settings = ();
our %netsettings = ();

$settings{'ID'} = '';
$settings{'INTERFACE'} = '';
$settings{'ENABLED'} = '';
$settings{'ENCRYPTION'} = '';
$settings{'WPA_MODE'} = '';
$settings{'SSID'} = '';
$settings{'PSK'} = '';
$settings{'PRIO'} = '';

$settings{'ACTION'} = '';		# add/edit/remove
$settings{'ID'} = '';			# point record for ACTION

my $errormessage = '';
my $warnmessage = '';

&Header::showhttpheaders();

#Get GUI values
&Header::getcgihash(\%settings);

# Load multiline data
our @configs = ();
if (open(FILE, "$datafile")) {
    @configs = <FILE>;
    close (FILE);
}

&General::readhash("${General::swroot}/main/settings", \%settings);
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

# Toggle enable/disable field.
if ($settings{'ACTION'} eq $Lang::tr{'toggle enable disable'}) {
	my @update;

	foreach my $line (@configs) {
		chomp($line);
		my @config = split(/\,/, $line);

		# Update the entry with the matching ID.
		if ($config[0] eq $settings{'ID'}) {
			# Toggle enabled/disabled status.

			if ($config[2] eq 'on') {
				$config[2] = 'off';
			} else {
				$config[2] = 'on';
			}

			$line = join(',', @config);
		}

		push(@update, $line."\n");
	}

    # Save updated configuration settings.
    open(FILE, ">$datafile") or die 'wlan client datafile error';
    print FILE @update;
    close(FILE);

	@configs = @update;

	# Update configuration files.
	&BuildConfiguration();

	# Reset ACTION.
	$settings{'ACTION'} = '';
}

if ($settings{'ACTION'} eq $Lang::tr{'add'}) {
	# Validate input data.
	$errormessage = ValidateInput("add");

	unless ($errormessage) {
		# Search for the next free id.
		my $next_id = NextID();

		my @config = ($next_id);
		push(@config, $settings{'INTERFACE'});
		push(@config, $settings{'ENABLED'});
		push(@config, $settings{'ENCRYPTION'});
		push(@config, $settings{'WPA_MODE'});
		push(@config, $settings{'SSID'});
		push(@config, $settings{'PSK'});
		push(@config, $settings{'PRIO'});
		push(@config, $settings{'AUTH'});
		push(@config, $settings{'ANONYMOUS'});
		push(@config, $settings{'IDENTITY'});
		push(@config, $settings{'PASSWORD'});

		# Add the new configuration and write all the stuff to the configuration file.
		my $line = join(',', @config) . "\n";
		push(@configs, $line);

		# Save updated configuration settings.
		open(FILE, ">$datafile") or die 'wlan client datafile error';
		print FILE @configs;
		close(FILE);

		# Update configuration files.
		&BuildConfiguration();

		# Reset ACTION.
		$settings{'ACTION'} = '';
	}
}

if ($settings{'ACTION'} eq $Lang::tr{'edit'}) {
	foreach my $line (@configs) {
		chomp($line);
		my @config = split(/\,/, $line);

		if ($config[0] eq $settings{'ID'}) {
			$settings{'ID'}         = $config[0];
			$settings{'INTERFACE'}  = $config[1];
			$settings{'ENABLED'}    = $config[2];
			$settings{'ENCRYPTION'} = $config[3];
			$settings{'WPA_MODE'}   = $config[4];
			$settings{'SSID'}       = $config[5];
			$settings{'PSK'}        = $config[6];
			$settings{'PRIO'}       = $config[7];
			$settings{'AUTH'}	= $config[8];
			$settings{'ANONYMOUS'}	= $config[9];
			$settings{'IDENTITY'}	= $config[10];
			$settings{'PASSWORD'}	= $config[11];
		}
	}
}

if ($settings{'ACTION'} eq $Lang::tr{'update'}) {
	$errormessage = ValidateInput("update");

	unless ($errormessage) {
		my @update;
		foreach my $line (@configs) {
			chomp($line);
			my @config = split(/\,/, $line);

			# Update the entry with the matching ID.
			if ($config[0] eq $settings{'ID'}) {
				# Update all configuration settings.
				# ID and INTERFACE cannot be changed.
				$config[2]  = $settings{'ENABLED'};
				$config[3]  = $settings{'ENCRYPTION'};
				$config[4]  = $settings{'WPA_MODE'};
				$config[5]  = $settings{'SSID'};
				$config[6]  = $settings{'PSK'};
				$config[7]  = $settings{'PRIO'};
				$config[8]  = $settings{'AUTH'};
				$config[9]  = $settings{'ANONYMOUS'};
				$config[10] = $settings{'IDENTITY'};
				$config[11] = $settings{'PASSWORD'};

				$line = join(',', @config);
			}

			push(@update, $line."\n");
		}

		# Save updated configuration settings.
		open(FILE, ">$datafile") or die 'wlan client datafile error';
		print FILE @update;
		close(FILE);

		@configs = @update;

		# Update configuration files.
		&BuildConfiguration();

		# Reset ACTION.
		$settings{'ACTION'} = '';
	}
}

if ($settings{'ACTION'} eq $Lang::tr{'remove'}) {
	my @update;

	foreach my $line (@configs) {
		chomp($line);
		my @config = split(/\,/, $line);

		# Skip the to be removed entry.
		if ($config[0] eq $settings{'ID'}) {
			next;
		}

		push(@update, $line."\n");
	}

    # Save updated configuration settings.
    open(FILE, ">$datafile") or die 'wlan client datafile error';
    print FILE @update;
    close(FILE);

	@configs = @update;

	# Update configuration files.
	&BuildConfiguration();

	# Reset ACTION.
	$settings{'ACTION'} = '';
}

if ($settings{'ACTION'} eq '') { # First launch from GUI
	&showMainBox();
} else {
	# Action has been set, so show the edit box.
	&showEditBox();
}

sub showMainBox() {
	&Header::openpage($Lang::tr{'wlan client configuration'}, 1, '');
	&Header::openbigbox('100%', 'left', '', $errormessage);

	&Header::openbox('100%', 'left', $Lang::tr{'wlan client configuration'});

	print <<END;
		<form method='POST' action='$ENV{'SCRIPT_NAME'}' style='text-align: center;'>
			<input type='submit' name='ACTION' value='$Lang::tr{'wlan client new network'}' />
		</form>

		<br><hr><br>

		<table width="100%" class='tbl'>
			<tr>
				<th align='center'>$Lang::tr{'wlan client ssid'}</th>
				<th align='center'>$Lang::tr{'wlan client encryption'}</th>
				<th align='center'>$Lang::tr{'priority'}</th>
				<th></th>
				<th></th>
				<th></th>
			</tr>
END

	#
	# Print each line of @configs list
	#

	my $key = 0;
	my $col="";
	foreach my $line (@configs) {
		# Skip commented lines.
		my $firstchar = substr($line, 0, 1);
		next if ($firstchar eq "#");

		chomp($line);
		my @config = split(/\,/,$line);

		#Choose icon for checkbox
		my $gif = '';
		my $gdesc = '';
		if ($config[2] eq 'on' ) {
			$gif = 'on.gif';
			$gdesc = $Lang::tr{'click to disable'};
		} else {
			$gif = 'off.gif';
			$gdesc = $Lang::tr{'click to enable'}; 
		}

		# Colorize each line
		if ($key % 2) {
			print "<tr>";
			$col="bgcolor='$color{'color20'}'";
		} else {
			print "<tr>";
			$col="bgcolor='$color{'color22'}'";
		}

		my $encryption_mode = $Lang::tr{'unknown'};
		if ($config[3] eq "NONE") {
			$encryption_mode = $Lang::tr{'wlan client encryption none'};
		} elsif ($config[3] eq "WEP") {
			$encryption_mode = $Lang::tr{'wlan client encryption wep'};
		} elsif ($config[3] eq "WPA") {
			$encryption_mode = $Lang::tr{'wlan client encryption wpa'};
		} elsif ($config[3] eq "WPA2") {
			$encryption_mode = $Lang::tr{'wlan client encryption wpa2'};
		} elsif ($config[3] eq "EAP") {
			$encryption_mode = $Lang::tr{'wlan client encryption eap'};
		}

		if ($config[3] eq "EAP") {
			if ($config[8] eq "PEAP") {
				$encryption_mode .= " ($Lang::tr{'wlan client auth peap'})";
			} elsif ($config[8] eq "TTLS") {
				$encryption_mode .= " ($Lang::tr{'wlan client auth ttls'})";
			} else {
				$encryption_mode .= " ($Lang::tr{'wlan client auth auto'})";
			}

			$encryption_mode .= "<hr>";

			if ($config[10]) {
				$encryption_mode .= "<strong>$Lang::tr{'wlan client identity'}</strong>: ";
				$encryption_mode .= $config[10];
			}

			# Anonymous identity
			if ($config[9]) {
				$encryption_mode .= "<br>";
				$encryption_mode .= "<strong>$Lang::tr{'wlan client anonymous identity'}</strong>: ";
				$encryption_mode .= $config[9];
			}

		} elsif (($config[3] eq "WPA") || ($config[3] eq "WPA2")) {
			my $wpa_pairwise = "$Lang::tr{'wlan client ccmp'} $Lang::tr{'wlan client and'} $Lang::tr{'wlan client tkip'}";
			my $wpa_group = "$Lang::tr{'wlan client ccmp'} $Lang::tr{'wlan client and'} $Lang::tr{'wlan client tkip'}";

			if ($config[4] eq "CCMP-CCMP") {
				$wpa_pairwise = $Lang::tr{'wlan client ccmp'};
				$wpa_group = $Lang::tr{'wlan client ccmp'};
			} elsif ($config[4] eq "CCMP-TKIP") {
				$wpa_pairwise = $Lang::tr{'wlan client ccmp'};
				$wpa_group = $Lang::tr{'wlan client tkip'};
			} elsif ($config[4] eq "TKIP-TKIP") {
				$wpa_pairwise = $Lang::tr{'wlan client tkip'};
				$wpa_group = $Lang::tr{'wlan client tkip'};
			}

			$encryption_mode .= "<hr>";
			$encryption_mode .= "<strong>$Lang::tr{'wlan client pairwise key algorithm'}</strong>: ";
			$encryption_mode .= $wpa_pairwise;
			$encryption_mode .= "<br>";
			$encryption_mode .= "<strong>$Lang::tr{'wlan client group key algorithm'}</strong>: ";
			$encryption_mode .= $wpa_group;
		}

		print <<END;
				<td align='center' $col>$config[5]</td>
				<td align='center' $col>$encryption_mode</td>
				<td align='center' $col>$config[7]</td>
				<td align='center' width='5%' $col>
					<form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}' />
						<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' alt='$gdesc' title='$gdesc' />
						<input type='hidden' name='ID' value='$config[0]' />
					</form>
				</td>
				<td align='center' width='5%' $col>
					<form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
						<input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' />
						<input type='hidden' name='ID' value='$config[0]' />
					</form>
				</td>
				<td align='center' width='5%' $col>
					<form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='ACTION' value='$Lang::tr{'remove'}' />
						<input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' alt='$Lang::tr{'remove'}' title='$Lang::tr{'remove'}' />
						<input type='hidden' name='ID' value='$config[0]' />
					</form>
				</td>
			</tr>
END
		$key++;
	}
	print "</table>";

	# If table contains entries, print 'Key to action icons'
	if ($key) {
		print <<END;
			<table>
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
				</tr>
			</table>
END
	}

	&Header::closebox();

	# Show status box.
	&ShowStatus();

	&Header::closebigbox();
	&Header::closepage();
}

sub showEditBox() {
	&Header::openpage($Lang::tr{'wlan client configuration'}, 1, '');
	&Header::openbigbox('100%', 'left', '', $errormessage);

	if ($errormessage) {
		&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
		print "<font class='base'>$errormessage&nbsp;</font>";
		&Header::closebox();
	}

	my $buttontext = $Lang::tr{'add'};
	if ($settings{'ID'} ne '') {
		$buttontext = $Lang::tr{'update'};
		&Header::openbox('100%', 'left', $Lang::tr{'wlan client edit entry'});
	} else {
		&Header::openbox('100%', 'left', $Lang::tr{'wlan client new entry'});
		$settings{'ENABLED'} = 'on';
	}
	my $action = $buttontext;

	my %checked = ();
	$checked{'ENABLED'} = ($settings{'ENABLED'} ne 'on' ) ? '' : "checked='checked'";

	my %selected = ();
	$selected{'ENCRYPTION'} = ();
	$selected{'ENCRYPTION'}{'NONE'} = '';
	$selected{'ENCRYPTION'}{'WPA2'} = '';
	$selected{'ENCRYPTION'}{'WPA'} = '';
	$selected{'ENCRYPTION'}{'WEP'} = '';
	$selected{'ENCRYPTION'}{$settings{'ENCRYPTION'}} = "selected='selected'";

	$selected{'WPA_MODE'} = ();
	$selected{'WPA_MODE'}{''} = '';
	$selected{'WPA_MODE'}{'CCMP-CCMP'} = '';
	$selected{'WPA_MODE'}{'CCMP-TKIP'} = '';
	$selected{'WPA_MODE'}{'TKIP-TKIP'} = '';
	$selected{'WPA_MODE'}{$settings{'WPA_MODE'}} = "selected='selected'";

	$selected{'AUTH'} = ();
	$selected{'AUTH'}{''} = '';
	$selected{'AUTH'}{'PEAP'} = '';
	$selected{'AUTH'}{'TTLS'} = '';
	$selected{'AUTH'}{$settings{'AUTH'}} = "selected='selected'";

	$selected{'PRIO'} = ();
	$selected{'PRIO'}{'0'} = '';
	$selected{'PRIO'}{'1'} = '';
	$selected{'PRIO'}{'2'} = '';
	$selected{'PRIO'}{'3'} = '';
	$selected{'PRIO'}{'4'} = '';
	$selected{'PRIO'}{$settings{'PRIO'}} = "selected='selected'";

	print <<END;
		<form method='POST' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='ID' value='$settings{'ID'}'>

			<table width='100%'>
				<tr>
					<td class='base' width='20%'>$Lang::tr{'wlan client ssid'}:</td>
					<td width='40%'><input type='text' name='SSID' value="$settings{'SSID'}" size='25'/></td>
					<td class='base' width='10%'>$Lang::tr{'enabled'}</td>
					<td width='30%'><input type='checkbox' name='ENABLED' $checked{'ENABLED'} /></td>
				</tr>
				<tr>
					<td class='base' width='20%'>$Lang::tr{'wlan client encryption'}:</td>
					<td width='40%'>
						<select name='ENCRYPTION'>
							<option value="NONE" $selected{'ENCRYPTION'}{'NONE'}>$Lang::tr{'wlan client encryption none'}</option>
							<option value="EAP"  $selected{'ENCRYPTION'}{'EAP'}>$Lang::tr{'wlan client encryption eap'}</option>
							<option value="WPA2" $selected{'ENCRYPTION'}{'WPA2'}>$Lang::tr{'wlan client encryption wpa2'}</option>
							<option value="WPA"  $selected{'ENCRYPTION'}{'WPA'}>$Lang::tr{'wlan client encryption wpa'}</option>
							<option value="WEP"  $selected{'ENCRYPTION'}{'WEP'}>$Lang::tr{'wlan client encryption wep'}</option>							
						</select>
					</td>
					<td colspan="2" width='40%'></td>
				</tr>
				<tr>
					<td class='base' width='20%'>$Lang::tr{'wlan client psk'}:&nbsp;</td>
					<td width='40%'><input type='password' name='PSK' value="$settings{'PSK'}" size='25'/></td>
					<td colspan="2" width='40%'></td>
				</tr>
			</table>

			<br>
			<hr>

			<strong>
				$Lang::tr{'wlan client authentication settings'}:
			</strong>

			<table width='100%'>
				<tr>
					<td class='base' width='20%'>
						$Lang::tr{'wlan client eap authentication method'}:
					</td>
					<td width='40%'>
						<select name='AUTH'>
							<option value="" $selected{'AUTH'}{''}>$Lang::tr{'wlan client auth auto'}</option>
							<option value="PEAP" $selected{'AUTH'}{'PEAP'}>$Lang::tr{'wlan client auth peap'}</option>
							<option value="TTLS" $selected{'AUTH'}{'TTLS'}>$Lang::tr{'wlan client auth ttls'}</option>
						</select>
					</td>
					<td colspan="2" width='40%'></td>
				</tr>
				<tr>
					<td class='base' width='20%'>
						$Lang::tr{'wlan client anonymous identity'}:
					</td>
					<td width='40%'>
						<input type="text" name="ANONYMOUS" value="$settings{"ANONYMOUS"}" size="25" />
					</td>
					<td colspan="2" width='40%'></td>
				</tr>
				<tr>
					<td class='base' width='20%'>
						$Lang::tr{'wlan client identity'}:
					</td>
					<td width='40%'>
						<input type="text" name="IDENTITY" value="$settings{"IDENTITY"}" size="25" />
					</td>
					<td colspan="2" width='40%'></td>
				</tr>
				<tr>
					<td class='base' width='20%'>
						$Lang::tr{'wlan client password'}:
					</td>
					<td width='40%'>
						<input type="password" name="PASSWORD" value="$settings{"PASSWORD"}" size="25" />
					</td>
					<td colspan="2" width='40%'></td>
				</tr>
			</table>

			<br>
			<hr>

			
			<strong>
				$Lang::tr{'wlan client advanced settings'}:
			</strong>

			<table width='100%'>
				<tr>
					<td class='base' width='20%'>
						$Lang::tr{'wlan client wpa mode'}:
					</td>
					<td width='40%'>
						<select name='WPA_MODE'>
							<option value="" $selected{'WPA_MODE'}{''}>$Lang::tr{'wlan client wpa mode all'}</option>
							<option value="CCMP-CCMP" $selected{'WPA_MODE'}{'CCMP-CCMP'}>$Lang::tr{'wlan client wpa mode ccmp ccmp'}</option>
							<option value="CCMP-TKIP" $selected{'WPA_MODE'}{'CCMP-TKIP'}>$Lang::tr{'wlan client wpa mode ccmp tkip'}</option>
							<option value="TKIP-TKIP" $selected{'WPA_MODE'}{'TKIP-TKIP'}>$Lang::tr{'wlan client wpa mode tkip tkip'}</option>
						</select>
					</td>
					<td colspan="2" width='40%'>
						<em>($Lang::tr{'wlan client pairwise key group key'})</em>
					</td>
				</tr>
				<tr>
					<td class='base' width='20%'>
						$Lang::tr{'priority'}:
					</td>
					<td width='40%'>
						<select name='PRIO'>
							<option value="0" $selected{'PRIO'}{'0'}>0 ($Lang::tr{'most preferred'})</option>
							<option value="1" $selected{'PRIO'}{'1'}>1</option>
							<option value="2" $selected{'PRIO'}{'2'}>2</option>
							<option value="3" $selected{'PRIO'}{'3'}>3</option>
							<option value="4" $selected{'PRIO'}{'4'}>4 ($Lang::tr{'least preferred'})</option>
						</select>
					</td>
					<td colspan="2" width='40%'></td>
				</tr>
			</table>

			<br>
			<hr>

			<table width='100%'>
				<tr>
					<td width='50%' align='center'>
						<input type='hidden' name='ACTION' value='$action' />
						<input type='submit' name='SUBMIT' value='$buttontext' />
					</td>
				</tr>
			</table>
		</form>
END
	&Header::closebox();

	&Header::closebigbox();
	&Header::closepage();
}

sub ShowStatus() {
	my $device = $netsettings{'RED_DEV'};

	# Exit if no device is configured.
	return if ($device eq "");

	# Exit if wpa_supplicant is not running on this interface.
	#return if (! -e "/var/run/wpa_supplicant/$device");

	open(FILE, "/usr/local/bin/wirelessclient status |");

	my %status = ();
	while (<FILE>) {
		chomp($_);

		my ($key, $value) = split("=", $_);
		$status{$key} = $value;
	}

	close(FILE);

	# End here, if no there is no input.
	return if (!keys %status);

	&Header::openbox('100%', 'left', $Lang::tr{'status'});

	if ($status{'ssid'} eq "") {
		print "<p>$Lang::tr{'wlan client disconnected'}</p>";

	} else {
		print <<END;
			<table width='100%'>
				<tr>
					<td width='20%'>
						$Lang::tr{'wlan client ssid'}
					</td>
					<td width='80%'>
						$status{'ssid'}
					</td>
				</tr>
				<tr>
					<td width='20%'>
						$Lang::tr{'wlan client bssid'}
					</td>
					<td width='80%'>
						$status{'bssid'}
					</td>
				</tr>
END

		if ($status{'EAP state'}) {
			my $selected_method = $status{'selectedMethod'};
			$selected_method =~ s/\d+ \((.*)\)/$1/e;

			print <<END;
				<tr>
					<td colspan='2'>
						<strong>$Lang::tr{'wlan client encryption eap'}</strong>
					</td>
				</tr>
				<tr>
					<td width='20%'>
						$Lang::tr{'wlan client eap state'}
					</td>
					<td width='80%'>
						$status{'EAP state'}
					</td>
				</tr>
				<tr>
					<td width='20%'>
						$Lang::tr{'wlan client method'}
					</td>
					<td width='80%'>
						$selected_method
					</td>
				</tr>
				<tr>
					<td width='20%'>
						$Lang::tr{'wlan client tls version'}
					</td>
					<td width='80%'>
						$status{'eap_tls_version'}
					</td>
				</tr>
				<tr>
					<td width='20%'>
						$Lang::tr{'wlan client tls cipher'}
					</td>
					<td width='80%'>
						$status{'EAP TLS cipher'}
					</td>
				</tr>
				<tr>
					<td width='20%'>
						$Lang::tr{'wlan client eap phase2 method'}
					</td>
					<td width='80%'>
						$status{"${selected_method}v0 Phase2 method"}
					</td>
				</tr>
END
		}

		if (($status{'pairwise_cipher'} ne "NONE") || ($status{'group_cipher'} ne "NONE")) {
			print <<END;
				<tr>
					<td colspan='2'>
						<strong>$Lang::tr{'wlan client encryption wpa'}</strong>
					</td>
				</tr>
				<tr>
					<td width='20%'>
						$Lang::tr{'wlan client pairwise cipher'}
					</td>
					<td width='80%'>
						$status{'pairwise_cipher'}
					</td>
				</tr>
				<tr>
					<td width='20%'>
						$Lang::tr{'wlan client group cipher'}
					</td>
					<td width='80%'>
						$status{'group_cipher'}
					</td>
				</tr>
END
		}

		print "</table>";
	}

	&Header::closebox();
}

sub BuildConfiguration() {
	system("/usr/local/bin/wirelessclient restart");
}

sub NextID() {
	my $highest_id = 0;
	foreach my $line (@configs) {
		# Skip commented lines.
		my $firstchar = substr($line, 0, 1);
		next if ($firstchar eq "#");

		my @config = split(/\,/, $line);
		if ($config[0] > $highest_id) {
			$highest_id = $config[0];
		}
	}

	return $highest_id + 1;
}

sub DuplicateSSID($) {
	my $ssid = shift;

	foreach my $line (@configs) {
		# Skip commented lines.
		my $firstchar = substr($line, 0, 1);
		next if ($firstchar eq "#");

		my @config = split(/\,/, $line);
		if ($config[5] eq $ssid) {
			return 1;
		}
	}

	return 0;
}

sub ValidKeyLength($$) {
	my $algo = shift;
	my $key = shift;

	my $key_length = length($key);

	if ($algo eq "WEP") {
		# Key must be 13 or 26 characters.
		if (($key_length == 13) || ($key_length == 26)) {
			return 0;
		}

		return 1;

	} elsif (($algo eq "WPA2") || ($algo eq "WPA")) {
		# Key must be between 8 and 63 chars.
		if (($key_length >= 8) && ($key_length <= 63)) {
			return 0;
		}

		return 1;
	}

	# Say okay for all other algorithms.
	return 0;
}

sub ValidateInput($) {
	my $mode = shift;

	# Check for duplicate SSIDs.
	if (($mode eq "add") && (DuplicateSSID($settings{'SSID'}))) {
		return "$Lang::tr{'wlan client duplicate ssid'}: $settings{'SSID'}";

	# Check for invalid key length.
	} elsif (ValidKeyLength($settings{'ENCRYPTION'}, $settings{'PSK'})) {
		return "$Lang::tr{'wlan client invalid key length'}";

	}

	# Reset WPA mode, if WPA(2) is not selected.
	if (($settings{'ENCRYPTION'} ne "WPA") && ($settings{'ENCRYPTION'} ne "WPA2")) {
		$settings{'WPA_MODE'} = '';
	}

	if ($settings{'ENABLED'} ne "") {
		$settings{'ENABLED'} = 'on';
	} else {
		$settings{'ENABLED'} = 'off';
	}

	return;
}
