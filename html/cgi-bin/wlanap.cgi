#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2021  IPFire Team  <info@ipfire.org>                     #
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
require '/var/ipfire/lang.pl';
require '/var/ipfire/header.pl';

my $errormessage = '';
my %selected=();
my %checked=();
my %wlanapsettings=();

# Read the configuration file
&General::readhash("/var/ipfire/wlanap/settings", \%wlanapsettings);

# Set defaults
&General::set_defaults(\%wlanapsettings, {
	"APMODE" => "on",
	"SSID" => "IPFire",
	"HIDESSID" => "off",
	"ENC" => "wpa2",
	"TXPOWER" => "auto",
	"CHANNEL" => "0",
	"COUNTRY" => "00",
	"HW_MODE" => "g",
	"PWD" => "",
	"HTCAPS" => "",
	"VHTCAPS" => "",
	"NOSCAN" => "on",
	"CLIENTISOLATION" => "off",
	"IEEE80211W" => "off",
});

my %cgiparams = ();

# Fetch arguments from browser
&Header::getcgihash(\%cgiparams);

# Find the selected interface
my $INTF = &Network::get_intf_by_address($wlanapsettings{'INTERFACE'});

delete $wlanapsettings{'__CGI__'};
delete $wlanapsettings{'x'};
delete $wlanapsettings{'y'};

&Header::showhttpheaders();

if ($cgiparams{'ACTION'} eq "$Lang::tr{'save'}") {
	# verify WPA Passphrase - only with enabled enc
	if ($cgiparams{'ENC'} ne "none") {
		# must be 8 .. 63 characters
		if ((length($cgiparams{'PWD'}) < 8) || (length($cgiparams{'PWD'}) > 63)) {
			$errormessage .= "$Lang::tr{'wlanap invalid wpa'}<br />";
		}

		# only ASCII alowed
		if (!($cgiparams{'PWD'} !~ /[^\x00-\x7f]/)) {
			$errormessage .= "$Lang::tr{'wlanap invalid wpa'}<br />";
		}
	}

	# XXX This needs validation
	$wlanapsettings{'INTERFACE'} = $cgiparams{'INTERFACE'};
	$wlanapsettings{'SSID'} = $cgiparams{'SSID'};
	$wlanapsettings{'HIDESSID'} = ($cgiparams{'HIDESSID'} eq 'on') ? 'on' : 'off';
	$wlanapsettings{'CLIENTISOLATION'} = ($cgiparams{'CLIENTISOLATION'} eq 'on') ? 'on' : 'off';
	$wlanapsettings{'COUNTRY'} = $cgiparams{'COUNTRY'};
	$wlanapsettings{'HW_MODE'} = $cgiparams{'HW_MODE'};
	$wlanapsettings{'CHANNEL'} = $cgiparams{'CHANNEL'};
	$wlanapsettings{'NOSCAN'} = ($cgiparams{'NOSCAN'} eq 'on') ? 'on' : 'off';
	$wlanapsettings{'ENC'} = $cgiparams{'ENC'};
	$wlanapsettings{'PWD'} = $cgiparams{'PWD'};
	$wlanapsettings{'IEEE80211W'} = ($cgiparams{'IEEE80211W'} eq 'on') ? 'on' : 'off';
	$wlanapsettings{'HTCAPS'} = $cgiparams{'HTCAPS'};
	$wlanapsettings{'VHTCAPS'} = $cgiparams{'VHTCAPS'};
	$wlanapsettings{'TX_POWER'} = $cgiparams{'TX_POWER'};

	if ($errormessage eq '') {
		&General::writehash("/var/ipfire/wlanap/settings", \%wlanapsettings);
		&WriteConfig_hostapd();

		&General::system("/usr/local/bin/wlanapctrl", "restart");
	}

# Start
} elsif ($cgiparams{'ACTION'} eq "$Lang::tr{'start'}") {
	&General::system("/usr/local/bin/wlanapctrl", "start");

# Stop
} elsif ($cgiparams{'ACTION'} eq "$Lang::tr{'stop'}") {
	&General::system("/usr/local/bin/wlanapctrl", "stop");
}

&Header::openpage($Lang::tr{'wlanap configuration'}, 1, '', '');
&Header::openbigbox('100%', 'left', '', $errormessage);

# Show any errors
&Header::errorbox($errormessage);

#
# Driver and status detection
#
my $message = "";

my %INTERFACES = &Network::list_wireless_interfaces();

foreach my $intf (keys %INTERFACES) {
	$selected{'INTERFACE'}{$intf} = '';
}
$selected{'INTERFACE'}{$wlanapsettings{'INTERFACE'}} = "selected='selected'";

# Change old "n" to "gn"
if ( $wlanapsettings{'HW_MODE'} eq 'n' ) {
	$wlanapsettings{'HW_MODE'}='gn';
}

$checked{'HIDESSID'}{'off'} = '';
$checked{'HIDESSID'}{'on'} = '';
$checked{'HIDESSID'}{$wlanapsettings{'HIDESSID'}} = "checked='checked'";

$checked{'NOSCAN'}{'off'} = '';
$checked{'NOSCAN'}{'on'} = '';
$checked{'NOSCAN'}{$wlanapsettings{'NOSCAN'}} = "checked='checked'";

$checked{'CLIENTISOLATION'}{'off'} = '';
$checked{'CLIENTISOLATION'}{'on'} = '';
$checked{'CLIENTISOLATION'}{$wlanapsettings{'CLIENTISOLATION'}} = "checked='checked'";

$selected{'IEEE80211W'}{'off'} = '';
$selected{'IEEE80211W'}{'optional'} = '';
$selected{'IEEE80211W'}{'on'} = '';
$selected{'IEEE80211W'}{$wlanapsettings{'IEEE80211W'}} = "selected";

$selected{'ENC'}{$wlanapsettings{'ENC'}} = "selected='selected'";
$selected{'CHANNEL'}{$wlanapsettings{'CHANNEL'}} = "selected='selected'";
$selected{'COUNTRY'}{$wlanapsettings{'COUNTRY'}} = "selected='selected'";
$selected{'TXPOWER'}{$wlanapsettings{'TXPOWER'}} = "selected='selected'";
$selected{'HW_MODE'}{$wlanapsettings{'HW_MODE'}} = "selected='selected'";

# Fetch all available channels
my @channellist = &get_channellist($INTF);

# Fetch countries
my @countrylist = &get_countrylist();

# Show status
&Header::opensection();

&Header::ServiceStatus({
	"$Lang::tr{'wlanap'}" => {
		"process" => "hostapd",
	}
});

print <<EOF;
	<table class="form">
		<tr class="action">
			<td>
				<form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='submit' name='ACTION' value='$Lang::tr{'start'}' />
				</form>

				<form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='submit' name='ACTION' value='$Lang::tr{'stop'}' />
				</form>
			</td>
		</tr>
	</table>
EOF

&Header::closesection();

#
# Configuration
#
&Header::openbox("100%", "center", $Lang::tr{'wlanap configuration'});

print <<END;
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<h6>$Lang::tr{'wlanap configuration'}</h6>

		<table class="form">
			<tr>
				<td>$Lang::tr{'wlanap interface'}</td>

				<td>
					<select name="INTERFACE" required>
END

foreach my $intf (sort keys %INTERFACES) {
	print <<END;
						<option value="$intf" $selected{'INTERFACE'}{$intf}>
							$INTERFACES{$intf}
						</option>
END
}

print <<END;
					</select>
				</td>
			</tr>

			<tr>
				<td>$Lang::tr{'wlanap ssid'}</td>
				<td>
					<input type='text' name='SSID' value='$wlanapsettings{'SSID'}' required>
				</td>
			</tr>

			<tr>
				<td>$Lang::tr{'wlanap hide ssid'}</td>
				<td>
					<input type='checkbox' name='HIDESSID' $checked{'HIDESSID'}{'on'}>
				</td>
			</tr>

			<tr>
				<td>$Lang::tr{'wlanap client isolation'}</td>
				<td>
					<input type='checkbox' name='CLIENTISOLATION' $checked{'CLIENTISOLATION'}{'on'}>
				</td>
			</tr>

			<tr>
				<td>$Lang::tr{'wlanap country'}</td>
				<td>
					<select name="COUNTRY">
END

foreach my $country (@countrylist){
	print "					<option $selected{'COUNTRY'}{$country}>$country</option>";
}

print <<END;
					</select>
				</td>
			</tr>

			<tr>
				<td>$Lang::tr{'wlanap wireless mode'}</td>
				<td>
					<select name='HW_MODE'>
						<option value='a' $selected{'HW_MODE'}{'a'}>802.11a</option>
						<option value='b' $selected{'HW_MODE'}{'b'}>802.11b</option>
						<option value='g' $selected{'HW_MODE'}{'g'}>802.11g</option>
						<option value='an' $selected{'HW_MODE'}{'an'}>802.11an</option>
						<option value='gn' $selected{'HW_MODE'}{'gn'}>802.11gn</option>
						<option value='ac' $selected{'HW_MODE'}{'ac'}>802.11ac</option>
					</select>
				</td>
			</tr>

			<tr>
				<td>$Lang::tr{'wlanap channel'}</td>
				<td>
					<select name='CHANNEL'>
END

foreach my $channel (@channellist){
	print "<option value='$channel' $selected{'CHANNEL'}{$channel}>";
	if ($channel eq 0) {
		print "- $Lang::tr{'wlanap auto'} -";
	} else {
		print $channel;
	}
	print "</option>";
}

print <<END;
					</select>
				</td>
			</tr>

			<tr>
				<td>$Lang::tr{'wlanap neighbor scan'}</td>
				<td>
					<input type='checkbox' name='NOSCAN' $checked{'NOSCAN'}{'on'}>

					$Lang::tr{'wlanap neighbor scan warning'}
				</td>
			</tr>

			<tr>
				<td>$Lang::tr{'wlanap encryption'}</td>
				<td>
					<select name='ENC'>
						<option value='none' $selected{'ENC'}{'none'}>$Lang::tr{'wlanap none'}</option>
						<option value='wpa1' $selected{'ENC'}{'wpa1'}>WPA1</option>
						<option value='wpa2' $selected{'ENC'}{'wpa2'}>WPA2</option>
						<option value='wpa3' $selected{'ENC'}{'wpa3'}>WPA3</option>
						<option value='wpa1+2' $selected{'ENC'}{'wpa1+2'}>WPA1+2</option>
						<option value='wpa2+3' $selected{'ENC'}{'wpa2+3'}>WPA2+3</option>
					</select>
				</td>
			</tr>

			<tr>
				<td>$Lang::tr{'wlanap psk'}</td>
				<td>
					<input type='text' name='PWD' value='$wlanapsettings{'PWD'}' />
				</td>
			</tr>

			<tr>
				<td>$Lang::tr{'wlanap management frame protection'}</td>
				<td>
					<select name="IEEE80211W">
						<option value="off" $selected{'IEEE80211W'}{'off'}>
							$Lang::tr{'wlanap 802.11w disabled'}
						</option>
						<option value="optional" $selected{'IEEE80211W'}{'optional'}>
							$Lang::tr{'wlanap 802.11w optional'}
						</option>
						<option value="on" $selected{'IEEE80211W'}{'on'}>
							$Lang::tr{'wlanap 802.11w enforced'}
						</option>
					</select>
				</td>
			</tr>

			<tr>
				<td>HT Caps</td>
				<td>
					<input type='text' name='HTCAPS' value='$wlanapsettings{'HTCAPS'}' />
				</td>
			</tr>

			<tr>
				<td>VHT Caps</td>
				<td>
					<input type='text' name='VHTCAPS' value='$wlanapsettings{'VHTCAPS'}' />
				</td>
			</tr>

			<tr>
				<td>Tx Power</td>
				<td>
					<input type='text' name='TXPOWER' value='$wlanapsettings{'TXPOWER'}' />
				</td>
			</tr>

			<tr class="action">
				<td colspan="2">
					<input type='submit' name='ACTION' value='$Lang::tr{'save'}' />
				</td>
			</tr>
		</table>
	</form>
END
;

&Header::closebox();

if ($INTF) {
	&Header::opensection();

	my @status = `iw dev $INTF info`;

	if (@status) {
		print <<END;
			<h6>$Lang::tr{'wlanap wlan status'}</h6>

			<pre>@status</pre>
END
	}

	@status = `iw dev $INTF station dump`;

	if (@status) {
		print <<END;
			<h6>$Lang::tr{'wlanap clients'}</h6>

			<pre>@status</pre>
END
	}

	&Header::closesection();
}

&Header::closebigbox();
&Header::closepage();

sub WriteConfig_hostapd{
	open (CONFIGFILE, ">/var/ipfire/wlanap/hostapd.conf");
	print CONFIGFILE <<END
driver=nl80211
######################### basic hostapd configuration ##########################
#
country_code=$wlanapsettings{'COUNTRY'}
country3=0x49 # indoor
ieee80211d=1
ieee80211h=1
channel=$wlanapsettings{'CHANNEL'}

# Always advertise TPC
local_pwr_constraint=3
spectrum_mgmt_required=1
END
;
 if ( $wlanapsettings{'HW_MODE'} eq 'an' ){
	print CONFIGFILE <<END
hw_mode=a
ieee80211n=1
wmm_enabled=1
ht_capab=$wlanapsettings{'HTCAPS'}
END
;

 }elsif ( $wlanapsettings{'HW_MODE'} eq 'gn' ){
	print CONFIGFILE <<END
hw_mode=g
ieee80211n=1
wmm_enabled=1
ht_capab=$wlanapsettings{'HTCAPS'}
END
;

 }elsif ( $wlanapsettings{'HW_MODE'} eq 'ac' ){
	print CONFIGFILE <<END
hw_mode=a
ieee80211ac=1
ieee80211n=1
wmm_enabled=1
ht_capab=$wlanapsettings{'HTCAPS'}
vht_capab=$wlanapsettings{'VHTCAPS'}
vht_oper_chwidth=1
END
;

 }else{
 	print CONFIGFILE <<END
hw_mode=$wlanapsettings{'HW_MODE'}
END
;

 }

print CONFIGFILE <<END;
# Enable logging
logger_syslog=-1
logger_syslog_level=4
auth_algs=1
ctrl_interface=/var/run/hostapd
ctrl_interface_group=0
disassoc_low_ack=1

# SSID
ssid2=\"$wlanapsettings{'SSID'}\"
utf8_ssid=1

END

if ( $wlanapsettings{'HIDESSID'} eq 'on' ){
	print CONFIGFILE <<END
ignore_broadcast_ssid=2
END
;
 }

 # https://forum.ipfire.org/viewtopic.php?f=22&t=12274&p=79070#p79070
 if ( $wlanapsettings{'CLIENTISOLATION'} eq 'on' ){
	print CONFIGFILE <<END
ap_isolate=1
END
;
 }

 if ( $wlanapsettings{'NOSCAN'} eq 'on' ){
	print CONFIGFILE <<END
noscan=1
END
;

 }else{
 	print CONFIGFILE <<END
noscan=0
END
;

 }

 # Management Frame Protection (802.11w)
 if ($wlanapsettings{'IEEE80211W'} eq "on") {
	print CONFIGFILE "ieee80211w=2\n";
 } elsif ($wlanapsettings{'IEEE80211W'} eq "optional") {
	print CONFIGFILE "ieee80211w=1\n";
 } else {
	print CONFIGFILE "ieee80211w=0\n";
 }

 if ( $wlanapsettings{'ENC'} eq 'wpa1'){
	print CONFIGFILE <<END
######################### wpa hostapd configuration ############################
#
wpa=1
wpa_passphrase=$wlanapsettings{'PWD'}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
END
;
 }elsif ( $wlanapsettings{'ENC'} eq 'wpa2'){
	print CONFIGFILE <<END
######################### wpa hostapd configuration ############################
#
wpa=2
wpa_passphrase=$wlanapsettings{'PWD'}
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
END
;
 }elsif ( $wlanapsettings{'ENC'} eq 'wpa3'){
	print CONFIGFILE <<END
######################### wpa hostapd configuration ############################
#
wpa=2
wpa_passphrase=$wlanapsettings{'PWD'}
wpa_key_mgmt=SAE
rsn_pairwise=CCMP
END
;
 } elsif ( $wlanapsettings{'ENC'} eq 'wpa1+2'){
	print CONFIGFILE <<END
######################### wpa hostapd configuration ############################
#
wpa=3
wpa_passphrase=$wlanapsettings{'PWD'}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
END
;
 }elsif ( $wlanapsettings{'ENC'} eq 'wpa2+3'){
	print CONFIGFILE <<END
######################### wpa hostapd configuration ############################
#
wpa=2
wpa_passphrase=$wlanapsettings{'PWD'}
wpa_key_mgmt=WPA-PSK SAE
rsn_pairwise=CCMP
END
;
 }
	close CONFIGFILE;
}

sub get_phy($) {
	my $intf = shift;
	my $phy;

	open(my $file, "/sys/class/net/$intf/phy80211/index") or return undef;

	while (<$file>) {
		chomp $_;

		$phy = $_;
		last;
	}

	close($file);

	return $phy;
}

sub get_channellist($) {
	my $intf = shift;

	# Fetch the PHY ID
	my $phy = &get_phy($intf);

	my @channels = (0);

	open(my $command, "iw phy phy$phy info |");

	while (<$command>) {
		# Skip everything we are not interested in
		next unless ($_ =~ m/MHz \[(\d+)\]/);

		my $channel = $1;

		# Skip disabled and otherwise unusable channels
		next if ($_ =~ m/disabled/);
		next if ($_ =~ m/no IBSS/);
		next if ($_ =~ m/no IR/);
		next if ($_ =~ m/passive scanning/);

		push(@channels, $channel);
	}

	close($command);

	return @channels;
}

sub get_countrylist() {
	open(my $file, "</lib/firmware/regulatorydb.txt");

	my @countries = ();

	while (<$file>)	{
		if ($_ =~ m/^country ([A-Z0-9]{2}):/) {
			push(@countries, $1);
		}
	}

	close($file);

	return @countries;
}
