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
require "${General::swroot}/network-functions.pl";

###--- HTML HEAD ---###
my $extraHead = <<END
<style>
	table#zoneconf {
		width: 100%;
		border-collapse: collapse;
		border-style: hidden;
		table-layout: fixed;
	}

	/* row height */
	#zoneconf tr {
		height: 4em;
	}
	#zoneconf tr.half-height {
		height: 2em;
	}
	#zoneconf tr.half-height > td {
		padding: 2px 10px;
	}

	/* section separators */
	#zoneconf tr.divider-top {
			border-top: 2px solid $Header::bordercolour;
	}
	#zoneconf tr.divider-bottom {
			border-bottom: 2px solid $Header::bordercolour;
	}

	/* table cells */
	#zoneconf td {
		padding: 5px 10px;
		border-left: 0.5px solid $Header::bordercolour;
		text-align: center;
	}

	/* grey header cells */
	#zoneconf td.heading {
		background-color: lightgrey;
		color: white;
	}	
	#zoneconf td.heading.bold::first-line {
		font-weight: bold;
		line-height: 1.6;
	}

	/* narrow left column with background color */
	#zoneconf tr > td:first-child {
		width: 11em;
	}
	#zoneconf tr.nic-row > td:first-child {
			background-color: darkgray;
	}
	#zoneconf tr.nic-row {
		border-bottom: 0.5px solid $Header::bordercolour;
	}
	#zoneconf tr.option-row > td:first-child {
			background-color: gray;
	}

	/* alternating row background color */
	#zoneconf tr {
		background-color: $Header::table2colour;
	}
	#zoneconf tr:nth-child(2n+3) {
		background-color: $Header::table1colour;
	}

	/* special cell colors */
	#zoneconf td.green {
		background-color: $Header::colourgreen;
	}

	#zoneconf td.red {
		background-color: $Header::colourred;
	}

	#zoneconf td.blue {
		background-color: $Header::colourblue;
	}

	#zoneconf td.orange {
		background-color: $Header::colourorange;
	}

	#zoneconf td.topleft {
		background-color: $Header::pagecolour;
	}

	input.vlanid {
		width: 4em;
	}
	input.stp-priority {
		width: 5em;
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

<script src="/include/zoneconf.js"></script>
END
;
###--- END HTML HEAD ---###

### Read configuration ###
my %ethsettings = ();
my %vlansettings = ();
my %cgiparams = ();

my $restart_notice = "";

&General::readhash("${General::swroot}/ethernet/settings",\%ethsettings);
&General::readhash("${General::swroot}/ethernet/vlans",\%vlansettings);

&Header::getcgihash(\%cgiparams);
&Header::showhttpheaders();

# Get all network zones that are currently enabled
my @zones = Network::get_available_network_zones();

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

### START PAGE ###
&Header::openpage($Lang::tr{"zoneconf title"}, 1, $extraHead);
&Header::openbigbox('100%', 'center');

### Evaluate POST parameters ###

if ($cgiparams{"ACTION"} eq $Lang::tr{"save"}) {
	my %VALIDATE_nic_check = ();
	my $VALIDATE_error = "";

	# Loop trough all known zones to ensure a complete configuration file is created
	foreach (@Network::known_network_zones) {
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

			# skip NIC/VLAN assignment and additional zone options for RED in PPP mode
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

		# STP options
		# (this has already been skipped when RED is in PPP mode, so we don't need to check for PPP here)
		$ethsettings{"${uc}_STP"} = "";
		my $stp_enabled = $cgiparams{"STP-$uc"} eq "on";
		my $stp_priority = $cgiparams{"STP-PRIORITY-$uc"};

		if($stp_enabled) {
			unless($ethsettings{"${uc}_MODE"} eq "bridge") { # STP is only available in bridge mode
				$VALIDATE_error = $Lang::tr{"zoneconf val stp zone mode error"};
				last;
			}
			unless (looks_like_number($stp_priority) && ($stp_priority >= 1) && ($stp_priority <= 65535)) { # STP bridge priority range: 1..65535
				$VALIDATE_error = $Lang::tr{"zoneconf val stp priority range error"};
				last;
			}
			$ethsettings{"${uc}_STP"} = "on"; # network-hotplug-bridges expects "on"
			$ethsettings{"${uc}_STP_PRIORITY"} = $stp_priority;
		}
	}

	# validation failed, show error message and exit
	if ($VALIDATE_error) {
		&Header::openbox('100%', 'left', $Lang::tr{"error"});

		print "$VALIDATE_error<br><br><a href='$ENV{'SCRIPT_NAME'}'>$Lang::tr{'back'}</a>\n";

		&Header::closebox();
		&Header::closebigbox();
		&Header::closepage();

		exit 0;
	}

	# new settings are valid, write configuration files
	&General::writehash("${General::swroot}/ethernet/settings",\%ethsettings);
	&General::writehash("${General::swroot}/ethernet/vlans",\%vlansettings);

	$restart_notice = $Lang::tr{'zoneconf notice reboot'};
}

### START OF TABLE ###

&Header::openbox('100%', 'left', $Lang::tr{"zoneconf nic assignment"});

print <<END
<form method='post' enctype='multipart/form-data'>
	<table id="zoneconf">
	<tr class="divider-bottom">
		<td class="topleft"></td>
END
;

# Fill the table header with all activated zones
foreach (@zones) {
	my $uc = uc $_;

	# If the red zone is in PPP mode, don't show a mode dropdown
	if ($uc eq "RED") {
		my $red_type = $ethsettings{"RED_TYPE"};

		unless (Network::is_red_mode_ip()) {
			print "\t\t<td class='heading bold $_'>$uc ($red_type)</td>\n";

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
		<td class='heading bold $_'>$uc<br>
			<select name="MODE $uc" data-zone="$uc" onchange="changeZoneMode(this)">
				<option value="DEFAULT" $mode_selected{"DEFAULT"}>$Lang::tr{"zoneconf nicmode default"}</option>
				<option value="BRIDGE" $mode_selected{"BRIDGE"}>$Lang::tr{"zoneconf nicmode bridge"}</option>
				<option value="MACVTAP" $mode_selected{"MACVTAP"}>$Lang::tr{"zoneconf nicmode macvtap"}</option>
			</select>
		</td>
END
;
}

print "\t</tr>\n";

# NIC assignment matrix
foreach (@nics) {
	my $mac = $_->[0];
	my $nic = $_->[1];
	my $wlan = $_->[2];

	print "\t<tr class='nic-row'>\n";
	print "\t\t<td class='heading bold'>$nic<br>$mac</td>\n";

	# Iterate through all zones and check if the current NIC is assigned to it
	foreach (@zones) {
		my $uc = uc $_;
		my $highlight = "";

		if ($uc eq "RED") {
			# VLANs/Bridging is not possible if the RED interface is set to PPP, PPPoE, VDSL, ...
			unless (Network::is_red_mode_ip()) {
				my $checked = "";

				if ($mac eq $ethsettings{"${uc}_MACADDR"}) {
					$checked = "checked";
					$highlight = $_;
				}

				print <<END
		<td class="$highlight">
			<input type="radio" name="PPPACCESS" value="$mac" data-zone="RED" data-mac="$mac" onchange="highlightAccess(this)" $checked>
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

		# If the interface is assigned, hightlight table cell
		if ($access_selected{"NONE"} eq "") {
			$highlight = $_;
		}

		print <<END
		<td class="$highlight">
			<select name="ACCESS $uc $mac" data-zone="$uc" data-mac="$mac" onchange="highlightAccess(this)">
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
}

# STP options
my @stp_html = (); # form fields buffer (two rows)

foreach (@zones) { # load settings and prepare form elements for each zone
	my $uc = uc $_;

	# STP is not available if the RED interface is set to PPP, PPPoE, VDSL, ...
	if ($uc eq "RED") {
		unless (Network::is_red_mode_ip()) {
			push(@stp_html, ["\t\t<td></td>\n", "\t\t<td></td>\n"]); # print empty cell
			next;
		}
	}

	# load configuration
	my $stp_available = $ethsettings{"${uc}_MODE"} eq "bridge"; # STP is only available in bridge mode
	my $stp_enabled = $ethsettings{"${uc}_STP"} eq "on";
	my $stp_priority = $ethsettings{"${uc}_STP_PRIORITY"};

	# form element modifiers
	my $checked = "";
	my $disabled = "";
	$checked = "checked" if ($stp_available && $stp_enabled);
	$disabled = "disabled" unless $stp_available;

	# enable checkbox HTML
	my $row_1 = <<END
		<td>
			<input type="checkbox" id="STP-$uc" name="STP-$uc" data-zone="$uc" onchange="changeEnableSTP(this)" $disabled $checked>
		</td>
END
;
	$disabled = "disabled" unless $stp_enabled; # STP priority can't be entered if STP is disabled

	# priority input box HTML
	my $row_2 = <<END
		<td>
			<input type="number" class="stp-priority" id="STP-PRIORITY-$uc" name="STP-PRIORITY-$uc" min="1" max="65535" value="$stp_priority" $disabled>
		</td>
END
;
	# add fields to buffer
	push(@stp_html, [$row_1, $row_2]);
}

# print two rows of prepared form elements
print <<END
	<tr class="half-height divider-top option-row">
		<td class="heading bold">$Lang::tr{"zoneconf stp enable"}</td>
END
;
foreach (@stp_html) {
	print $_->[0]; # row 1
}
print <<END
	</tr>
	<tr class="half-height option-row">
		<td class="heading">$Lang::tr{"zoneconf stp priority"}</td>
END
;
foreach (@stp_html) {
	print $_->[1]; # row 2
}
print "\t</tr>\n";

# footer and submit button
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
