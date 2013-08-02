#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2013  IPFire Team  <info@ipfire.org>                          #
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

my @bandwidth_limits = (
	1000 * 1024, # 1G
	 500 * 1024,
	 200 * 1024,
	 100 * 1024, # 100M
	  64 * 1024,
	  50 * 1024,
	  25 * 1024,
	  20 * 1024,
	  16 * 1024,
	  10 * 1024,
	   8 * 1024,
	   4 * 1024,
	   2 * 1024,
	       1024, # 1M
	        512,
	        256,
	        160
);
my @accounting_periods = ('daily', 'weekly', 'monthly');

my $TOR_CONTROL_PORT = 9051;

our %netsettings = ();
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

our %settings = ();

$settings{'TOR_ENABLED'} = 'off';
$settings{'TOR_SOCKS_PORT'} = 9050;
$settings{'TOR_EXIT_COUNTRY'} = '';
$settings{'TOR_USE_EXIT_NODES'} = '';
$settings{'TOR_ALLOWED_SUBNETS'} = "$netsettings{'GREEN_NETADDRESS'}\/$netsettings{'GREEN_NETMASK'}";
if (&Header::blue_used()) {
	$settings{'TOR_ALLOWED_SUBNETS'} .= ",$netsettings{'BLUE_NETADDRESS'}\/$netsettings{'BLUE_NETMASK'}";
}

$settings{'TOR_RELAY_ENABLED'} = 'off';
$settings{'TOR_RELAY_MODE'} = 'exit';
$settings{'TOR_RELAY_PORT'} = 9001;
$settings{'TOR_RELAY_NOADVERTISE'} = 'off';
$settings{'TOR_RELAY_BANDWIDTH_RATE'} = 0;
$settings{'TOR_RELAY_BANDWIDTH_BURST'} = 0;
$settings{'TOR_RELAY_ACCOUNTING_LIMIT'} = 0;
$settings{'TOR_RELAY_ACCOUNTING_PERIOD'} = 'daily';

$settings{'ACTION'} = '';

my $errormessage = '';
my $warnmessage = '';

&Header::showhttpheaders();

# Get GUI values.
&Header::getcgihash(\%settings);

# Create tor command connection.
our $torctrl = &TorConnect();

# Toggle enable/disable field.
if ($settings{'ACTION'} eq $Lang::tr{'save'}) {
	my @temp = split(/[\n,]/,$settings{'TOR_ALLOWED_SUBNETS'});
	$settings{'TOR_ALLOWED_SUBNETS'} = "";
	foreach (@temp) {
		s/^\s+//g; s/\s+$//g;
		if ($_) {
			unless (&General::validipandmask($_)) {
				$errormessage = "$Lang::tr{'tor errmsg invalid ip or mask'}: $_";
			}
			$settings{'TOR_ALLOWED_SUBNETS'} .= $_.",";
		}
	}

	@temp = split(/[\n,]/,$settings{'TOR_USE_EXIT_NODES'});
	$settings{'TOR_USE_EXIT_NODES'} = "";
	foreach (@temp) {
		s/^\s+//g; s/\s+$//g;
		if ($_) {
			$settings{'TOR_USE_EXIT_NODES'} .= $_.",";
		}
	}

	if ($errormessage eq '') {
		# Write configuration settings to file.
		&General::writehash("${General::swroot}/tor/settings", \%settings);

		# Update configuration files.
		&BuildConfiguration();
	}

	# Reset ACTION.
	$settings{'ACTION'} = '';
}

# Load settings from file.
&General::readhash("${General::swroot}/tor/settings", \%settings);

&showMainBox();

# Close Tor control connection.
&TorClose($torctrl);

# Functions

sub showMainBox() {
	my %checked = ();
	my %selected = ();

	$checked{'TOR_ENABLED'}{'on'} = '';
	$checked{'TOR_ENABLED'}{'off'} = '';
	$checked{'TOR_ENABLED'}{$settings{'TOR_ENABLED'}} = 'checked';

	$checked{'TOR_RELAY_ENABLED'}{'on'} = '';
	$checked{'TOR_RELAY_ENABLED'}{'off'} = '';
	$checked{'TOR_RELAY_ENABLED'}{$settings{'TOR_RELAY_ENABLED'}} = 'checked';

	&Header::openpage($Lang::tr{'tor configuration'}, 1, '');
	&Header::openbigbox('100%', 'left', '', $errormessage);

	if ($errormessage) {
		&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
		print "<font class='base'>$errormessage&nbsp;</font>\n";
		&Header::closebox();
	}

	print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

	&Header::openbox('100%', 'left', $Lang::tr{'tor configuration'});

	print <<END;
		<table width='100%'>
			<tr>
				<td colspan='4' class='base'><b>$Lang::tr{'tor common settings'}</b></td>
			</tr>
			<tr>
				<td width='25%' class='base'>$Lang::tr{'tor enabled'}:</td>
				<td width='30%'><input type='checkbox' name='TOR_ENABLED' $checked{'TOR_ENABLED'}{'on'} /></td>
				<td width='25%' class='base'>$Lang::tr{'tor socks port'}:</td>
				<td width='20%'><input type='text' name='TOR_SOCKS_PORT' value='$settings{'TOR_SOCKS_PORT'}' size='5' /></td>
			</tr>
			<tr>
				<td width='25%' class='base'>$Lang::tr{'tor relay enabled'}:</td>
				<td width='30%'><input type='checkbox' name='TOR_RELAY_ENABLED' $checked{'TOR_RELAY_ENABLED'}{'on'} /></td>
				<td width='25%' class='base'></td>
				<td width='20%'></td>
			</tr>
		</table>
END

	if ($settings{'TOR_ENABLED'} eq 'on') {
		my @temp = split(",", $settings{'TOR_ALLOWED_SUBNETS'});
		$settings{'TOR_ALLOWED_SUBNETS'} = join("\n", @temp);

		@temp = split(",", $settings{'TOR_USE_EXIT_NODES'});
		$settings{'TOR_USE_EXIT_NODES'} = join("\n", @temp);

		print <<END;
			<br>
			<hr size='1'>
			<br>

			<table width='100%'>
				<tr>
					<td colspan='4' class='base'><b>$Lang::tr{'tor acls'}</b></td>
				</tr>
				<tr>
					<td colspan='2' class='base' width='55%'>
						$Lang::tr{'tor allowed subnets'}:
					</td>
					<td colspan='2' width='45%'></td>
				</tr>
				<tr>
					<td colspan='2' class='base' width='55%'>
						<textarea name='TOR_ALLOWED_SUBNETS' cols='32' rows='3' wrap='off'>$settings{'TOR_ALLOWED_SUBNETS'}</textarea>
					</td>
					<td colspan='2' width='45%'></td>
				</tr>
			</table>

			<br>
			<hr size='1'>
			<br>

			<table width='100%'>
				<tr>
					<td colspan='4' class='base'><b>$Lang::tr{'tor exit nodes'}</b></td>
				</tr>
				<tr>
					<td colspan='2' class='base' width='55%'></td>
					<td colspan='2' class='base' width='45%'>$Lang::tr{'tor use exit nodes'}:</td>
				</tr>
				<tr>
					<td width='50%' colspan='2'>
						<select name='TOR_EXIT_COUNTRY'>
							<option value=''>- $Lang::tr{'tor exit country any'} -</option>
END

			my @country_names = Locale::Country::all_country_names();
			foreach my $country_name (sort @country_names) {
				my $country_code = Locale::Country::country2code($country_name);
				$country_code = uc($country_code);
				print "<option value='$country_code'>$country_name ($country_code)</option>\n";
			}

		print <<END;
						</select>
					</td>
					<td width='50%' colspan='2'>
						<textarea name='TOR_USE_EXIT_NODES' cols='32' rows='3' wrap='off'>$settings{'TOR_USE_EXIT_NODES'}</textarea>
					</td>
				</tr>
			</table>
			<br><br>
END
	}

	&Header::closebox();

	if ($settings{'TOR_RELAY_ENABLED'} eq 'on') {
		$checked{'TOR_RELAY_NOADVERTISE'}{'on'} = '';
		$checked{'TOR_RELAY_NOADVERTISE'}{'off'} = '';
		$checked{'TOR_RELAY_NOADVERTISE'}{$settings{'TOR_RELAY_NOADVERTISE'}} = 'checked';

		$selected{'TOR_RELAY_MODE'}{'bridge'} = '';
		$selected{'TOR_RELAY_MODE'}{'exit'} = '';
		$selected{'TOR_RELAY_MODE'}{'private-bridge'} = '';
		$selected{'TOR_RELAY_MODE'}{'relay'} = '';
		$selected{'TOR_RELAY_MODE'}{$settings{'TOR_RELAY_MODE'}} = 'selected';

		$selected{'TOR_RELAY_BANDWIDTH_RATE'}{'0'} = '';
		foreach (@bandwidth_limits) {
			$selected{'TOR_RELAY_BANDWIDTH_RATE'}{$_} = '';
		}
		$selected{'TOR_RELAY_BANDWIDTH_RATE'}{$settings{'TOR_RELAY_BANDWIDTH_RATE'}} = 'selected';

		$selected{'TOR_RELAY_BANDWIDTH_BURST'}{'0'} = '';
		foreach (@bandwidth_limits) {
			$selected{'TOR_RELAY_BANDWIDTH_BURST'}{$_} = '';
		}
		$selected{'TOR_RELAY_BANDWIDTH_BURST'}{$settings{'TOR_RELAY_BANDWIDTH_BURST'}} = 'selected';

		foreach (@accounting_periods) {
			$selected{'TOR_RELAY_ACCOUNTING_PERIOD'}{$_} = '';
		}
		$selected{'TOR_RELAY_ACCOUNTING_PERIOD'}{$settings{'TOR_RELAY_ACCOUNTING_PERIOD'}} = 'selected';

		&Header::openbox('100%', 'left', $Lang::tr{'tor relay configuration'});

		print <<END;
			<table width='100%'>
				<tr>
					<td width='25%' class='base'>$Lang::tr{'tor relay mode'}:</td>
					<td width='30%'>
						<select name='TOR_RELAY_MODE'>
							<option value='exit' $selected{'TOR_RELAY_MODE'}{'exit'}>$Lang::tr{'tor relay mode exit'}</option>
							<option value='relay' $selected{'TOR_RELAY_MODE'}{'relay'}>$Lang::tr{'tor relay mode relay'}</option>
							<option value='bridge' $selected{'TOR_RELAY_MODE'}{'bridge'}>$Lang::tr{'tor relay mode bridge'}</option>
							<option value='private-bridge' $selected{'TOR_RELAY_MODE'}{'private-bridge'}>$Lang::tr{'tor relay mode private bridge'}</option>
						</select>
					</td>
					<td width='25%' class='base'>$Lang::tr{'tor relay port'}:</td>
					<td width='20%'>
						<input type='text' name='TOR_RELAY_PORT' value='$settings{'TOR_RELAY_PORT'}' size='5' />
					</td>
				</tr>
				<tr>
					<td width='25%' class='base'>$Lang::tr{'tor relay address'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
					<td width='30%'>
						<input type='text' name='TOR_RELAY_ADDRESS' value='$settings{'TOR_RELAY_ADDRESS'}' />
					</td>
					<td width='25%' class='base'>$Lang::tr{'tor do not advertise relay'}:</td>
					<td width='20%'>
						<input type='checkbox' name='TOR_RELAY_NOADVERTISE' $checked{'TOR_RELAY_NOADVERTISE'}{'on'} />
					</td>
				</tr>
				<tr>
					<td width='25%' class='base'>$Lang::tr{'tor relay nickname'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
					<td width='30%'>
						<input type='text' name='TOR_RELAY_NICKNAME' value='$settings{'TOR_RELAY_NICKNAME'}' />
					</td>
					<td colspan='2'></td>
				</tr>
				<tr>
					<td width='25%' class='base'>$Lang::tr{'tor contact info'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
					<td width='75%' colspan='3'>
						<input type='text' name='TOR_RELAY_CONTACT_INFO' value='$settings{'TOR_RELAY_CONTACT_INFO'}' size='60' />
					</td>
				</tr>
			</table>

			<hr size='1'>

			<table width='100%'>
				<tr>
					<td colspan='4' class='base'><b>$Lang::tr{'tor bandwidth settings'}</b></td>
				</tr>
				<tr>
					<td width='25%' class='base'>$Lang::tr{'tor bandwidth rate'}:</td>
					<td width='30%' class='base'>
						<select name='TOR_RELAY_BANDWIDTH_RATE'>
END

		foreach (@bandwidth_limits) {
			if ($_ >= 1024) {
				print "<option value='$_' $selected{'TOR_RELAY_BANDWIDTH_RATE'}{$_}>". $_ / 1024 ." MBit/s</option>\n";
			} else {
				print "<option value='$_' $selected{'TOR_RELAY_BANDWIDTH_RATE'}{$_}>$_ kBit/s</option>\n";
			}
		}

		print <<END;
							<option value='0' $selected{'TOR_RELAY_BANDWIDTH_RATE'}{'0'}>$Lang::tr{'tor bandwidth unlimited'}</option>
						</select>
					</td>
					<td width='25%' class='base'>$Lang::tr{'tor accounting limit'}:</td>
					<td width='20%'>
						<input type='text' name='TOR_RELAY_ACCOUNTING_LIMIT' value='$settings{'TOR_RELAY_ACCOUNTING_LIMIT'}' size='12' />
					</td>
				</tr>
				<tr>
					<td width='25%' class='base'>$Lang::tr{'tor bandwidth burst'}:</td>
					<td width='20%' class='base'>
						<select name='TOR_RELAY_BANDWIDTH_BURST'>
END

		foreach (@bandwidth_limits) {
			if ($_ >= 1024) {
				print "<option value='$_' $selected{'TOR_RELAY_BANDWIDTH_BURST'}{$_}>". $_ / 1024 ." MBit/s</option>\n";
			} else {
				print "<option value='$_' $selected{'TOR_RELAY_BANDWIDTH_BURST'}{$_}>$_ kBit/s</option>\n";
			}
		}
		print <<END;
							<option value='0' $selected{'TOR_RELAY_BANDWIDTH_BURST'}{'0'}>$Lang::tr{'tor bandwidth unlimited'}</option>
						</select>
					</td>
					<td width='25%' class='base'>$Lang::tr{'tor accounting period'}:</td>
					<td width='20%'>
						<select name='TOR_RELAY_ACCOUNTING_PERIOD'>
END

		foreach (@accounting_periods) {
			print "<option value='$_' $selected{'TOR_RELAY_ACCOUNTING_PERIOD'}{$_}>$Lang::tr{'tor accounting period '.$_}</option>";
		}

		print <<END;
						</select>
					</td>
				</tr>
			</table>
END

		&Header::closebox();
	}

	print <<END;
		<table width='100%'>
			<tr>
				<td>
					<img src='/blob.gif' align='top' alt='*' />&nbsp;<font class='base'>$Lang::tr{'this field may be blank'}</font>
				</td>
				<td align='right'>&nbsp;</td>
			</tr>
		</table>

		<hr>

		<table width='100%'>
			<tr>
				<td>&nbsp;</td>
				<td align='center'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
				<td>&nbsp;</td>
			</tr>
		</table>
END

	# If we have a control connection, show the stats.
	if ($torctrl) {
		&Header::openbox('100%', 'left', $Lang::tr{'tor stats'});

		my @traffic = &TorTrafficStats($torctrl);

		if (@traffic) {
			print <<END;
				<table width='100%'>
END

		if ($settings{'TOR_RELAY_ENABLED'} eq 'on') {
			my $fingerprint = &TorRelayFingerprint($torctrl);
			if ($fingerprint) {
				print <<END;
					<tr>
						<td width='40%' class='base'>$Lang::tr{'tor relay fingerprint'}:</td>
						<td width='60%'>
							<a href='https://atlas.torproject.org/#details/$fingerprint' target='_blank'>$fingerprint</a>
						</td>
					</tr>
END
			}
		}

		my $address = TorGetInfo($torctrl, "address");
		if ($address) {
			print <<END;
				<tr>
					<td width='40%' class='base'>$Lang::tr{'tor relay external address'}:</td>
					<td width='60%'>$address</td>
				</tr>
END
		}

		print <<END;
					<tr>
						<td width='40%'>$Lang::tr{'tor traffic read written'}:</td>
END
			print "<td width='60%'>" . &FormatBytes($traffic[0]) ."/". &FormatBytes($traffic[1]) . "</td>";
			print <<END;
					</tr>
				</table>
END
		}

		my $accounting = &TorAccountingStats($torctrl);
		if ($accounting) {
			print <<END;
				<table width='100%'>
					<tr>
						<td colspan='2' class='base'><b>$Lang::tr{'tor accounting'}</b></td>
					</tr>
END

			if ($accounting->{'hibernating'} eq "hard") {
				print <<END;
					<tr>
						<td class='base' colspan='2' bgcolor="$Header::colourred" align='center'>
							<font color='white'>$Lang::tr{'tor traffic limit hard'}</font>
						</td>
					</tr>
END
			} elsif ($accounting->{'hibernating'} eq "soft") {
				print <<END;
					<tr>
						<td class='base' colspan='2' bgcolor="$Header::colourorange" align='center'>
							<font color='white'>$Lang::tr{'tor traffic limit soft'}</font>
						</td>
					</tr>
END
			}

			print <<END;
					<tr>
						<td width='40%' class='base'>$Lang::tr{'tor accounting interval'}</td>
						<td width='60%'>
							$accounting->{'interval-start'} - $accounting->{'interval-end'}
						</td>
					</tr>
					<tr>
						<td width='40%' class='base'>$Lang::tr{'tor accounting bytes'}</td>
						<td width='60%'>
END

			print &FormatBytes($accounting->{'bytes_read'}) . "/" . &FormatBytes($accounting->{'bytes_written'});
			print " (" . &FormatBytes($accounting->{'bytes-left_read'}) . "/" . &FormatBytes($accounting->{'bytes-left_written'});
			print " $Lang::tr{'tor accounting bytes left'})";

			print <<END;
						</td>
					</tr>
				</table>
END
		}

		my @nodes = &TorORConnStatus($torctrl);
		if (@nodes) {
			my $nodes_length = scalar @nodes;
			print <<END;
				<table width='100%'>
					<tr>
						<td width='40%' class='base'><b>$Lang::tr{'tor connected relays'}</b></td>
						<td width='60%' colspan='2'>($nodes_length)</td>
					</tr>
END

			foreach my $node (@nodes) {
				print <<END;
					<tr>
						<td width='40%'>
							<a href='https://atlas.torproject.org/#details/$node->{'fingerprint'}' target='_blank'>
								$node->{'name'}
							</a>
						</td>
						<td width='30%'>
END

				if (exists($node->{'country_code'})) {
						print "<a href='country.cgi#$node->{'country_code'}'><img src='/images/flags/$node->{'country_code'}.png' border='0' align='absmiddle' alt='$node->{'country_code'}'></a>";
				}

				print <<END;
							<a href='ipinfo.cgi?ip=$node->{'address'}'>$node->{'address'}</a>:$node->{'port'}
						</td>
						<td width='30%' align='right'>
							~$node->{'bandwidth_string'}
						</td>
					</tr>
END
			}
			print "</table>";
		}

		&Header::closebox();
	}

	print "</form>\n";

	&Header::closebigbox();
	&Header::closepage();
}

sub BuildConfiguration() {
	my %settings = ();
	&General::readhash("${General::swroot}/tor/settings", \%settings);

	my $torrc = "${General::swroot}/tor/torrc";

	open(FILE, ">$torrc");

	# Global settings.
	print FILE "ControlPort $TOR_CONTROL_PORT\n";

	if ($settings{'TOR_ENABLED'} eq 'on') {
		my $strict_nodes = 0;

		print FILE "SocksPort 0.0.0.0:$settings{'TOR_SOCKS_PORT'}\n";

		my @subnets = split(",", $settings{'TOR_ALLOWED_SUBNETS'});
		foreach (@subnets) {
			print FILE "SocksPolicy accept $_\n" if (&General::validipandmask($_));
		}
		print FILE "SocksPolicy reject *\n" if (@subnets);

		if ($settings{'TOR_EXIT_COUNTRY'} ne '') {
			$strict_nodes = 1;

			print FILE "ExitNodes {$settings{'TOR_EXIT_COUNTRY'}}\n";
		}

		if ($settings{'TOR_USE_EXIT_NODES'} ne '') {
			$strict_nodes = 1;

			my @nodes = split(",", $settings{'TOR_USE_EXIT_NODES'});
			foreach (@nodes) {
				print FILE "ExitNode $_\n";
			}
		}

		if ($strict_nodes > 0) {
			print FILE "StrictNodes 1\n";
		}
	}

	if ($settings{'TOR_RELAY_ENABLED'} eq 'on') {
		# Reject access to private networks.
		print FILE "ExitPolicyRejectPrivate 1\n";

		print FILE "ORPort $settings{'TOR_RELAY_PORT'}";
		if ($settings{'TOR_RELAY_NOADVERTISE'} eq 'on') {
			print FILE " NoAdvertise";
		}
		print FILE "\n";

		if ($settings{'TOR_RELAY_ADDRESS'} ne '') {
			print FILE "Address $settings{'TOR_RELAY_ADDRESS'}\n";
		}

		if ($settings{'TOR_RELAY_NICKNAME'} ne '') {
			print FILE "Nickname $settings{'TOR_RELAY_NICKNAME'}\n";
		}

		if ($settings{'TOR_RELAY_CONTACT_INFO'} ne '') {
			print FILE "ContactInfo $settings{'TOR_RELAY_CONTACT_INFO'}\n";
		}

		# Limit to bridge mode.
		my $is_bridge = 0;

		if ($settings{'TOR_RELAY_MODE'} eq 'bridge') {
			$is_bridge++;

		# Private bridge.
		} elsif ($settings{'TOR_RELAY_MODE'} eq 'private-bridge') {
			$is_bridge++;

			print FILE "PublishServerDescriptor 0\n";

		# Exit node.
		} elsif ($settings{'TOR_RELAY_MODE'} eq 'exit') {
			print FILE "ExitPolicy accept *:*\n";

		# Relay only.
		} elsif ($settings{'TOR_RELAY_MODE'} eq 'relay') {
			print FILE "ExitPolicy reject *:*\n";
		}

		if ($is_bridge > 0) {
			print FILE "BridgeRelay 1\n";
			print FILE "Exitpolicy reject *:*\n";
		}

		if ($settings{'TOR_RELAY_BANDWIDTH_RATE'} > 0) {
			print FILE "RelayBandwidthRate ";
			print FILE $settings{'TOR_RELAY_BANDWIDTH_RATE'} / 8;
			print FILE " KB\n";

			if ($settings{'TOR_RELAY_BANDWIDTH_BURST'} > 0) {
				print FILE "RelayBandwidthBurst ";
				print FILE $settings{'TOR_RELAY_BANDWIDTH_BURST'} / 8;
				print FILE " KB\n";
			}
		}

		if ($settings{'TOR_RELAY_ACCOUNTING_LIMIT'} > 0) {
			print FILE "AccountingMax ".$settings{'TOR_RELAY_ACCOUNTING_LIMIT'}." MB\n";

			if ($settings{'TOR_RELAY_ACCOUNTING_PERIOD'} eq 'daily') {
				print FILE "AccountingStart day 00:00\n";
			} elsif ($settings{'TOR_RELAY_ACCOUNTING_PERIOD'} eq 'weekly') {
				print FILE "AccountingStart week 1 00:00\n";
			} elsif ($settings{'TOR_RELAY_ACCOUNTING_PERIOD'} eq 'monthly') {
				print FILE "AccountingStart month 1 00:00\n";
			}
		}
	}

	close(FILE);

	# Restart the service.
	if (($settings{'TOR_ENABLED'} eq 'on') || ($settings{'TOR_RELAY_ENABLED'} eq 'on')) {
		system("/usr/local/bin/torctrl restart &>/dev/null");
	} else {
		system("/usr/local/bin/torctrl stop &>/dev/null");
	}
}

sub TorConnect() {
	my $socket = new IO::Socket::INET(
		Proto => 'tcp', PeerAddr => '127.0.0.1', PeerPort => $TOR_CONTROL_PORT,
	) or return;

	$socket->autoflush(1);

	# Authenticate.
	&TorSendCommand($socket, "AUTHENTICATE");

	return $socket;
}

sub TorSendCommand() {
	my ($socket, $cmd) = @_;

	# Replace line ending with \r\n.
	chomp $cmd;
	$cmd .= "\r\n";

	$socket->send($cmd);

	my @output = ();
	while (my $line = <$socket>) {
		# Skip empty lines.
		if ($line =~ /^.\r\n$/) {
			next;
		}

		# Command has been successfully executed.
		if ($line =~ /250 OK/) {
			last;

		# Error.
		} elsif ($line =~ /^5\d+/) {
			last;

		} else {
			# Remove line endings.
			$line =~ s/\r\n$//;

			push(@output, $line);
		}
	}

	return @output;
}

sub TorSendCommandOneLine() {
	my ($tor, $cmd) = @_;

	my @output = &TorSendCommand($tor, $cmd);
	return $output[0];
}

sub TorGetInfo() {
	my ($tor, $cmd) = @_;

	my $output = &TorSendCommandOneLine($tor, "GETINFO ".$cmd);

	my ($key, $value) = split("=", $output);
	return $value;
}

sub TorClose() {
	my $socket = shift;

	if ($socket) {
		$socket->shutdown(2);
	}
}

sub TorTrafficStats() {
	my $tor = shift;

	my $output_read    = &TorGetInfo($tor, "traffic/read");
	my $output_written = &TorGetInfo($tor, "traffic/written");

	return ($output_read, $output_written);
}

sub TorRelayFingerprint() {
	my $tor = shift;

	return &TorGetInfo($tor, "fingerprint");
}

sub TorORConnStatus() {
	my $tor = shift;
	my @nodes = ();

	my @output = &TorSendCommand($tor, "GETINFO orconn-status");
	foreach (@output) {
		$_ =~ s/^250[\+-]orconn-status=//;
		next if ($_ eq "");
		last if ($_ eq ".");
		next unless ($_ =~ /^\$/);

		my @line = split(" ", $_);
		my @node = split(/[=~]/, $line[0]);

		my $node = &TorNodeDescription($tor, $node[0]);
		if ($node) {
			push(@nodes, $node);
		}
	}

	# Sort by names.
	@nodes = sort { $a->{'name'} cmp $b->{'name'} } @nodes;

	return @nodes;
}

sub TorNodeDescription() {
	my ($tor, $fingerprint) = @_;
	$fingerprint =~ s/\$//;

	my $node = {
		fingerprint  => $fingerprint,
		exit_node    => 0,
	};

	my @output = &TorSendCommand($tor, "GETINFO ns/id/$node->{'fingerprint'}");

	foreach (@output) {
		# Router
		if ($_ =~ /^r (\w+) (.*) (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) (\d+)/) {
			$node->{'name'}    = $1;
			$node->{'address'} = $3;
			$node->{'port'}    = $4;

			my $country_code = &TorGetInfo($tor, "ip-to-country/$node->{'address'}");
			$node->{'country_code'} = $country_code;

		# Flags
		} elsif ($_ =~ /^s (.*)$/) {
			$node->{'flags'} = split(" ", $1);

			foreach my $flag ($node->{'flags'}) {
				if ($flag eq "Exit") {
					$node->{'exit_node'}++;
				}
			}

		# Bandwidth
		} elsif ($_ =~ /^w Bandwidth=(\d+)/) {
			$node->{'bandwidth'} = $1 * 8;
			$node->{'bandwidth_string'} = &FormatBitsPerSecond($node->{'bandwidth'});
		}
	}

	if (exists($node->{'name'})) {
		return $node;
	}
}

sub TorAccountingStats() {
	my $tor = shift;
	my $ret = {};

	my $enabled = &TorGetInfo($tor, "accounting/enabled");
	if ($enabled ne '1') {
		return;
	}

	my @cmds = ("hibernating", "interval-start", "interval-end");
	foreach (@cmds) {
		$ret->{$_} = &TorGetInfo($tor, "accounting/$_");
	}

	my @cmds = ("bytes", "bytes-left");
	foreach (@cmds) {
		my $output = &TorGetInfo($tor, "accounting/$_");
		my @bytes = split(" ", $output);

		$ret->{$_."_read"}    = $bytes[0];
		$ret->{$_."_written"} = $bytes[1];
	}

	return $ret;
}

sub FormatBytes() {
	my $bytes = shift;

	my @units = ("B", "KB", "MB", "GB", "TB");
	my $units_index = 0;

	while (($units_index <= $#units) && ($bytes >= 1024)) {
		$units_index++;
		$bytes /= 1024;
	}

	return sprintf("%.2f %s", $bytes, $units[$units_index]);
}

sub FormatBitsPerSecond() {
	my $bits = shift;

	my @units = ("Bit/s", "KBit/s", "MBit/s", "GBit/s", "TBit/s");
	my $units_index = 0;

	while (($units_index <= $#units) && ($bits >= 1024)) {
		$units_index++;
		$bits /= 1024;
	}

	return sprintf("%.2f %s", $bits, $units[$units_index]);
}
