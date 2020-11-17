#!/usr/bin/perl
###############################################################################
#                                                                             #
# VLAN Management for IPFire                                                  #
# Copyright (C) 2019 Florian Bührle <fbuehrle@ipfire.org>                     #
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
use Scalar::Util qw(looks_like_number);

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my $css = <<END
<style>
	table {
		width: 100%;
		border-collapse: collapse;
		table-layout: fixed;
	}

	tr {
		height: 4em;
	}

	td.narrow {
		width: 11em;
	}

	td {
		padding: 5px;
		padding-left: 10px;
		padding-right: 10px;
		border: 0.5px solid black;
	}

	td.slightlygrey {
		background-color: #F0F0F0;
	}

	td.h {
		background-color: grey;
		color: white;
		font-weight: 800;
	}

	td.green {
		background-color: $Header::colourgreen;
	}

	td.red {
		background-color: $Header::colourred;
	}

	td.blue {
		background-color: $Header::colourblue;
	}

	td.orange {
		background-color: $Header::colourorange;
	}

	td.topleft {
		background-color: white;
		border-top-style: none;
		border-left-style: none;
	}

	td.textcenter {
		text-align: center;
	}

	input.vlanid {
		width: 4em;
	}

	#submit-container {
		width: 100%;
		padding-top: 20px;
		text-align: right;
		color: red;
	}

	#submit-container.input {
		margin-left: auto;
	}
</style>
END
;

my %ethsettings = ();
my %vlansettings = ();
my %cgiparams = ();

my $restart_notice = "";

&General::readhash("${General::swroot}/ethernet/settings",\%ethsettings);
&General::readhash("${General::swroot}/ethernet/vlans",\%vlansettings);

&Header::getcgihash(\%cgiparams);
&Header::showhttpheaders();

# Define all zones we will check for NIC assignment
my @zones = ("green", "red", "orange", "blue");

# Get all physical NICs present
opendir(my $dh, "/sys/class/net/");
my @nics = ();

while (my $nic = readdir($dh)) {
	if (-e "/sys/class/net/$nic/device") { # Indicates that the NIC is physical
		push(@nics, [&Network::get_nic_property($nic, "address"), $nic, 0]);
	}
}

closedir($dh);

@nics = sort {$a->[0] cmp $b->[0]} @nics; # Sort nics by their MAC address

# Name the physical NICs
# Even though they may not be really named like this, we will name them ethX or wlanX
my $ethcount = 0;
my $wlancount = 0;

foreach (@nics) {
	my $nic = $_->[1];

	if (-e "/sys/class/net/$nic/wireless") {
		$_->[1] = "wlan$wlancount";
		$_->[2] = 1;
		$wlancount++;
	} else {
		$_->[1] = "eth$ethcount";
		$ethcount++;
	}
}

&Header::openpage($Lang::tr{"zoneconf title"}, 1, $css);
&Header::openbigbox('100%', 'center');

### Evaluate POST parameters ###

if ($cgiparams{"ACTION"} eq $Lang::tr{"save"}) {
	my %VALIDATE_nic_check = ();
	my $VALIDATE_error = "";

	foreach (@zones) {
		my $uc = uc $_;
		my $slave_string = "";
		my $zone_mode = $cgiparams{"MODE $uc"};
		my $VALIDATE_vlancount = 0;
		my $VALIDATE_zoneslaves = 0;

		$ethsettings{"${uc}_MACADDR"} = "";
		$ethsettings{"${uc}_MODE"} = "";
		$ethsettings{"${uc}_SLAVES"} = "";
		$vlansettings{"${uc}_PARENT_DEV"} = "";
		$vlansettings{"${uc}_VLAN_ID"} = "";
		$vlansettings{"${uc}_MAC_ADDRESS"} = "";

		# If RED is not in DHCP or static mode, we only set its MACADDR property
		if ($uc eq "RED" && ! $cgiparams{"PPPACCESS"} eq "") {
			foreach (@nics) {
				my $mac = $_->[0];

				if ($mac eq $cgiparams{"PPPACCESS"}) {
					$ethsettings{"${uc}_MACADDR"} = $mac;

					# Check if this interface is already accessed by any other zone
					# If this is the case, show an error message
					if ($VALIDATE_nic_check{"ACC $mac"}) {
						$VALIDATE_error = $Lang::tr{"zoneconf val ppp assignment error"};
					}

					$VALIDATE_nic_check{"RESTRICT $mac"} = 1;
					last;
				}
			}

			next;
		}

		foreach (@nics) {
			my $mac = $_->[0];
			my $nic_access = $cgiparams{"ACCESS $uc $mac"};

			next unless ($nic_access);

			if ($nic_access ne "NONE") {
				if ($VALIDATE_nic_check{"RESTRICT $mac"}) { # If this interface is already assigned to RED in PPP mode, throw an error
					$VALIDATE_error = $Lang::tr{"zoneconf val ppp assignment error"};
					last;
				}

				if ($zone_mode ne "BRIDGE" && $VALIDATE_zoneslaves > 0 && $nic_access ne "") {
					$VALIDATE_error = $Lang::tr{"zoneconf val zoneslave amount error"};
					last;
				}

				$VALIDATE_nic_check{"ACC $mac"} = 1;
				$VALIDATE_zoneslaves++;
			}

			if ($nic_access eq "NATIVE") {
				if ($VALIDATE_nic_check{"NATIVE $mac"}) {
					$VALIDATE_error = $Lang::tr{"zoneconf val native assignment error"};
					last;
				}

				$VALIDATE_nic_check{"NATIVE $mac"} = 1;

				if ($zone_mode eq "BRIDGE") {
					$slave_string = "${slave_string}${mac} ";
				} else {
					$ethsettings{"${uc}_MACADDR"} = $mac;
				}
			} elsif ($nic_access eq "VLAN") {
				my $vlan_tag = $cgiparams{"TAG $uc $mac"};

				if ($VALIDATE_nic_check{"VLAN $mac $vlan_tag"}) {
					$VALIDATE_error = $Lang::tr{"zoneconf val vlan tag assignment error"};
					last;
				}

				$VALIDATE_nic_check{"VLAN $mac $vlan_tag"} = 1;

				if (! looks_like_number($vlan_tag)) {
					last;
				}
				if ($vlan_tag < 1 || $vlan_tag > 4095) {
					last;
				}

				my $rnd_mac = &Network::random_mac();

				$vlansettings{"${uc}_PARENT_DEV"} = $mac;
				$vlansettings{"${uc}_VLAN_ID"} = $vlan_tag;
				$vlansettings{"${uc}_MAC_ADDRESS"} = $rnd_mac;

				if ($zone_mode eq "BRIDGE") {
					$slave_string = "${slave_string}${rnd_mac} ";
				}

				$VALIDATE_vlancount++; # We can't allow more than one VLAN per zone
			}
		}

		if ($VALIDATE_vlancount > 1) {
			$VALIDATE_error = $Lang::tr{"zoneconf val vlan amount assignment error"};
			last;
		}

		chop($slave_string);

		if ($zone_mode eq "BRIDGE") {
			$ethsettings{"${uc}_MODE"} = "bridge";
			$ethsettings{"${uc}_SLAVES"} = $slave_string;
		} elsif ($zone_mode eq "MACVTAP") {
			$ethsettings{"${uc}_MODE"} = "macvtap";
		}
	}

	if ($VALIDATE_error) {
		&Header::openbox('100%', 'left', $Lang::tr{"error"});

		print "$VALIDATE_error<br><br><a href='$ENV{'SCRIPT_NAME'}'>$Lang::tr{'back'}</a>\n";

		&Header::closebox();
		&Header::closebigbox();
		&Header::closepage();

		exit 0;
	}

	&General::writehash("${General::swroot}/ethernet/settings",\%ethsettings);
	&General::writehash("${General::swroot}/ethernet/vlans",\%vlansettings);

	$restart_notice = $Lang::tr{'zoneconf notice reboot'};
}

&Header::openbox('100%', 'left', $Lang::tr{"zoneconf nic assignment"});

### START OF TABLE ###

print <<END
<form method='post' enctype='multipart/form-data'>
	<table>
	<tr>
		<td class="h narrow topleft"></td>
END
;

# Fill the table header with all activated zones
foreach (@zones) {
	my $uc = uc $_;
	my $dev_name = $ethsettings{"${uc}_DEV"};

	if ($dev_name eq "") { # If the zone is not activated, don't show it
		next;
	}

	# If the zone is in PPP mode, don't show a mode dropdown
	if ($uc eq "RED") {
		my $red_type = $ethsettings{"RED_TYPE"};
		my $red_restricted = ($uc eq "RED" && ! ($red_type eq "STATIC" || $red_type eq "DHCP"));

		if ($red_restricted) {
			print "\t\t<td class='h textcenter $_'>$uc ($red_type)</td>\n";

			next; # We're done here
		}
	}

	my %mode_selected = ();
	my $zone_mode = $ethsettings{"${uc}_MODE"};

	if ($zone_mode eq "") {
		$mode_selected{"DEFAULT"} = "selected";
	} elsif ($zone_mode eq "bridge") {
		$mode_selected{"BRIDGE"} = "selected";
	} elsif ($zone_mode eq "macvtap") {
		$mode_selected{"MACVTAP"} = "selected";
	}

	print <<END
		<td class='h textcenter $_'>$uc<br>
			<select name="MODE $uc">
				<option value="DEFAULT" $mode_selected{"DEFAULT"}>$Lang::tr{"zoneconf nicmode default"}</option>
				<option value="BRIDGE" $mode_selected{"BRIDGE"}>$Lang::tr{"zoneconf nicmode bridge"}</option>
				<option value="MACVTAP" $mode_selected{"MACVTAP"}>$Lang::tr{"zoneconf nicmode macvtap"}</option>
			</select>
		</td>
END
;
}

print "\t</tr>\n";

my $slightlygrey = "";

foreach (@nics) {
	my $mac = $_->[0];
	my $nic = $_->[1];
	my $wlan = $_->[2];

	print "\t<tr>\n";
	print "\t\t<td class='h narrow textcenter'>$nic<br>$mac</td>\n";

	# Iterate through all zones and check if the current NIC is assigned to it
	foreach (@zones) {
		my $uc = uc $_;
		my $dev_name = $ethsettings{"${uc}_DEV"};

		if ($dev_name eq "") { # Again, skip the zone if it is not activated
			next;
		}

		if ($uc eq "RED") {
			my $red_type = $ethsettings{"RED_TYPE"};
			my $red_restricted = ($uc eq "RED" && ! ($red_type eq "STATIC" || $red_type eq "DHCP"));

			# VLANs/Bridging is not possible if the RED interface is set to PPP, PPPoE, VDSL, ...
			if ($red_restricted) {
				my $checked = "";

				if ($mac eq $ethsettings{"${uc}_MACADDR"}) {
					$checked = "checked";
				}

				print <<END
		<td class="textcenter $slightlygrey">
			<input type="radio" name="PPPACCESS" value="$mac" $checked>
		</td>
END
;
				next; # We're done here
			}
		}

		my %access_selected = ();
		my $zone_mode = $ethsettings{"${uc}_MODE"};
		my $zone_parent_dev = $vlansettings{"${uc}_PARENT_DEV"};  # ZONE_PARENT_DEV is set if this zone accesses any interface via a VLAN
		my $field_disabled = "disabled"; # Only enable the VLAN ID input field if the current access mode is VLAN
		my $zone_vlan_id = "";

		# If ZONE_PARENT_DEV is set to a NICs name (e.g. green0 or eth0) instead of a MAC address, we have to find out this NICs MAC address
		$zone_parent_dev = &Network::get_mac_by_name($zone_parent_dev);

		# If the current NIC is accessed by the current zone via a VLAN, the ZONE_PARENT_DEV option corresponds to the current NIC
		if ($mac eq $zone_parent_dev) {
			$access_selected{"VLAN"} = "selected";
			$field_disabled = "";
			$zone_vlan_id = $vlansettings{"${uc}_VLAN_ID"};
		} elsif ($zone_mode eq "bridge") { # If the current zone is in bridge mode, all corresponding NICs (Native as well as VLAN) are set via the ZONE_SLAVES option
			my @slaves = split(/ /, $ethsettings{"${uc}_SLAVES"});

			foreach (@slaves) {
				# Slaves can be set to a NICs name so we have to find out its MAC address
				$_ = &Network::get_mac_by_name($_);

				if ($_ eq $mac) {
					$access_selected{"NATIVE"} = "selected";
					last;
				}
			}
		} elsif ($mac eq $ethsettings{"${uc}_MACADDR"}) { # Native access via ZONE_MACADDR is only set if the zone does not access a NIC via a VLAN and the zone is not in bridge mode
			$access_selected{"NATIVE"} = "selected";
		}

		$access_selected{"NONE"} = ($access_selected{"NATIVE"} eq "") && ($access_selected{"VLAN"} eq "") ? "selected" : "";
		my $vlan_disabled = ($wlan) ? "disabled" : "";

		print <<END
		<td class="textcenter $slightlygrey">
			<select name="ACCESS $uc $mac" onchange="document.getElementById('TAG-$uc-$mac').disabled = (this.value === 'VLAN' ? false : true)">
				<option value="NONE" $access_selected{"NONE"}>- $Lang::tr{"zoneconf access none"} -</option>
				<option value="NATIVE" $access_selected{"NATIVE"}>$Lang::tr{"zoneconf access native"}</option>
				<option value="VLAN" $access_selected{"VLAN"} $vlan_disabled>$Lang::tr{"zoneconf access vlan"}</option>
			</select>
			<input type="number" class="vlanid" id="TAG-$uc-$mac" name="TAG $uc $mac" min="1" max="4095" value="$zone_vlan_id" $field_disabled>
		</td>
END
;
	}

	print "\t</tr>\n";

	if ($slightlygrey) {
		$slightlygrey = "";
	} else {
		$slightlygrey = "slightlygrey";
	}
}

print <<END
	</table>

	<div id="submit-container">
		$restart_notice
		<input type="submit" name="ACTION" value="$Lang::tr{"save"}">
	</div>
</form>
END
;

### END OF TABLE ###

&Header::closebox();
&Header::closebigbox();
&Header::closepage();
