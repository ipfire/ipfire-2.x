#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2020  IPFire Development Team                                 #
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
use IO::Socket;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/location-functions.pl";
require "${General::swroot}/ids-functions.pl";
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::colouryellow} );
undef (@dummy);

my %cgiparams=();
my %checked=();
my %selected=();
my $errormessage = '';

# Config file which stores the DNS settings.
my $settings_file = "${General::swroot}/dns/settings";

# File which stores the configured DNS-Servers.
my $servers_file = "${General::swroot}/dns/servers";

# Create files if the does not exist.
unless (-f $settings_file) { system("touch $settings_file") };
unless (-f $servers_file) { system("touch $servers_file") };

# File which stores the ISP assigned DNS servers.
my @ISP_nameserver_files = ( "/var/run/dns1", "/var/run/dns2" );

# File which contains the ca-certificates.
my $ca_certs_file = "/etc/ssl/certs/ca-bundle.crt";

# Server which is used, to determine if the whole DNS system works properly.
my $dns_test_server = "ping.ipfire.org";

my $check_servers;

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

&Header::showhttpheaders();
&Header::getcgihash(\%cgiparams);

##
# Save general settings.
#
if ($cgiparams{'GENERAL'} eq $Lang::tr{'save'}) {
	# Prevent form name from been stored in conf file.
	delete $cgiparams{'GENERAL'};

	# Add value for non-checked checkbox.
	if ($cgiparams{'USE_ISP_NAMESERVERS'} ne "on") {
		$cgiparams{'USE_ISP_NAMESERVERS'} = "off";
	}

	# Add value for non-checked checkbox.
	if ($cgiparams{'ENABLE_SAFE_SEARCH'} ne "on") {
		$cgiparams{'ENABLE_SAFE_SEARCH'} = "off";
	}

	# Check if using ISP nameservers and TLS is enabled at the same time.
	if (($cgiparams{'USE_ISP_NAMESERVERS'} eq "on") && ($cgiparams{'PROTO'} eq "TLS")) {
		$errormessage = $Lang::tr{'dns isp nameservers and tls not allowed'}
	}

	# Check if there was an error.
	if ( ! $errormessage) {

		# Store settings into settings file.
		&General::writehash("$settings_file", \%cgiparams);

		# Call function to handle unbound restart, etc.
		&_handle_unbound_and_more()
	}
}

###
# Add / Edit entries.
#
if (($cgiparams{'SERVERS'} eq $Lang::tr{'save'}) || ($cgiparams{'SERVERS'} eq $Lang::tr{'update'})) {
	# Hash to store the generic DNS settings.
	my %settings = ();

	# Read-in generic settings.
	&General::readhash("$settings_file", \%settings);

	# Check if an IP-address has been given.
	if ($cgiparams{"NAMESERVER"} eq "") {
		$errormessage = "$Lang::tr{'dns no address given'}";
	}

	# Check if the given DNS server is valid.
	elsif(!&General::validip($cgiparams{"NAMESERVER"})) {
		$errormessage = "$Lang::tr{'invalid ip'}: $cgiparams{'NAMESERVER'}";
	}

	# Check if a TLS is enabled and no TLS_HOSTNAME has benn specified.
	elsif($settings{'PROTO'} eq "TLS") {
		unless($cgiparams{"TLS_HOSTNAME"}) {
			$errormessage = "$Lang::tr{'dns no tls hostname given'}";
		} else {
			# Check if the provided domain is valid.
			unless(&General::validfqdn($cgiparams{"TLS_HOSTNAME"})) {
				$errormessage = "$Lang::tr{'invalid ip or hostname'}: $cgiparams{'TLS_HOSTNAME'}";
			}
		}
	}

	# Go further if there was no error.
	if ( ! $errormessage) {
		# Check if a remark has been entered.
		$cgiparams{'REMARK'} = &Header::cleanhtml($cgiparams{'REMARK'});

		my %dns_servers = ();
		my $id;
		my $status;

		# Read-in configfile.
		&General::readhasharray($servers_file, \%dns_servers);

		# Check if we should edit an existing entry and got an ID.
		if (($cgiparams{'SERVERS'} eq $Lang::tr{'update'}) && ($cgiparams{'ID'})) {
			# Assin the provided id.
			$id = $cgiparams{'ID'};

			# Undef the given ID.
			undef($cgiparams{'ID'});

			# Grab the configured status of the corresponding entry.
			$status = $dns_servers{$id}[2];
		} else {
			# Each newly added entry automatically should be enabled.
			$status = "enabled";

			# Generate the ID for the new entry.
			#
			# Sort the keys by their ID and store them in an array.
			my @keys = sort { $a <=> $b } keys %dns_servers;

			# Reverse the key array.
			my @reversed = reverse(@keys);

			# Obtain the last used id.
			my $last_id = @reversed[0];

			# Increase the last id by one and use it as id for the new entry.
			$id = ++$last_id;

			# The first allowed id is 3 to keep space for
			# possible ISP assigned DNS servers.
			if ($id <= "2") {
				$id = "3";
			}
		}

		# Add/Modify the entry to/in the dns_servers hash.
		$dns_servers{$id} = ["$cgiparams{'NAMESERVER'}", "$cgiparams{'TLS_HOSTNAME'}", "$status", "$cgiparams{'REMARK'}"];

		# Write the changed hash to the config file.
		&General::writehasharray($servers_file, \%dns_servers);

		# Call function to handle unbound restart, etc.
		&_handle_unbound_and_more();
	} else {
		# Switch back to previous mode.
		$cgiparams{'SERVERS'} = $cgiparams{'MODE'};
	}
###
# Toggle enable / disable.
#
} elsif ($cgiparams{'SERVERS'} eq $Lang::tr{'toggle enable disable'}) {
	my %dns_servers = ();

	# Only go further, if an ID has been passed.
	if ($cgiparams{'ID'}) {
		# Assign the given ID.
		my $id = $cgiparams{'ID'};

		# Undef the given ID.
		undef($cgiparams{'ID'});

		# Read-in configfile.
		&General::readhasharray($servers_file, \%dns_servers);

		# Grab the configured status of the corresponding entry.
		my $status = $dns_servers{$id}[2];

		# Switch the status.
		if ($status eq "disabled") {
			$status = "enabled";
		} else {
			$status = "disabled";
		}

		# Modify the status of the existing entry.
		$dns_servers{$id} = ["$dns_servers{$id}[0]", "$dns_servers{$id}[1]", "$status", "$dns_servers{$id}[3]"];

		# Write the changed hash back to the config file.
		&General::writehasharray($servers_file, \%dns_servers);

		# Call function to handle unbound restart, etc.
		&_handle_unbound_and_more();
	}

## Remove entry from DNS servers list.
#
} elsif ($cgiparams{'SERVERS'} eq $Lang::tr{'remove'}) {
	my %dns_servers = ();

	# Read-in configfile.
	&General::readhasharray($servers_file, \%dns_servers);

	# Drop entry from the hash.
	delete($dns_servers{$cgiparams{'ID'}});

	# Undef the given ID.
	undef($cgiparams{'ID'});

	# Write the changed hash to the config file.
	&General::writehasharray($servers_file, \%dns_servers);

	# Call function to handle unbound restart, etc.
	&_handle_unbound_and_more();

## Handle request to check the servers.
#
} elsif ($cgiparams{'SERVERS'} eq $Lang::tr{'dns check servers'}) {
	$check_servers = 1;
}

# Hash to store the generic DNS settings.
my %settings = ();

# Read-in general DNS settings.
&General::readhash("$settings_file", \%settings);

# Hash which contains the configured DNS servers.
my %dns_servers = ();

# Read-in config file.
&General::readhasharray("$servers_file", \%dns_servers);

# Libloc database handle
my $libloc_db_handle = &Location::Functions::init();

&Header::openpage($Lang::tr{'dns title'}, 1, '');

&Header::openbigbox('100%', 'left', '', $errormessage);

###
# Error messages layout.
#
if ($errormessage) {
        &Header::openbox('100%', 'left', $Lang::tr{'error messages'});
        print "<class name='base'>$errormessage\n";
        print "&nbsp;</class>\n";
        &Header::closebox();
}

# Handle if a nameserver should be added or edited.
if (($cgiparams{'SERVERS'} eq "$Lang::tr{'add'}") || ($cgiparams{'SERVERS'} eq "$Lang::tr{'edit'}")) {
	# Display the sub page.
	&show_add_edit_nameserver();

	# Close webpage.
	&Header::closebigbox();
	&Header::closepage();

	# Finished here for the moment.
	exit(0);
}

$cgiparams{'GENERAL'} = '';
$cgiparams{'SERVERS'} = '';
$cgiparams{'NAMESERVER'} = '';
$cgiparams{'TLS_HOSTNAME'} = '';
$cgiparams{'REMARK'} ='';

$checked{'USE_ISP_NAMESERVERS'}{'off'} = '';
$checked{'USE_ISP_NAMESERVERS'}{'on'} = '';
$checked{'USE_ISP_NAMESERVERS'}{$settings{'USE_ISP_NAMESERVERS'}} = "checked='checked'";

$checked{'ENABLE_SAFE_SEARCH'}{'off'} = '';
$checked{'ENABLE_SAFE_SEARCH'}{'on'} = '';
$checked{'ENABLE_SAFE_SEARCH'}{$settings{'ENABLE_SAFE_SEARCH'}} = "checked='checked'";

$selected{'PROTO'}{'UDP'} = '';
$selected{'PROTO'}{'TLS'} = '';
$selected{'PROTO'}{'TCP'} = '';
$selected{'PROTO'}{$settings{'PROTO'}} = "selected='selected'";

$selected{'QNAME_MIN'}{'standard'} = '';
$selected{'QNAME_MIN'}{'strict'} = '';
$selected{'QNAME_MIN'}{$settings{'QNAME_MIN'}} = "selected='selected'";

# Display nameserver and configuration sections.
&show_nameservers();
&show_general_dns_configuration();

&Header::closebigbox();
&Header::closepage();

###
# General DNS-Servers sektion.
#
sub show_general_dns_configuration () {
	&Header::openbox('100%', 'center', "$Lang::tr{'dns configuration'}");

	print <<END;
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width="100%">
			<tr>
				<td width="33%">
					$Lang::tr{'dns use isp assigned nameservers'}
				</td>

				<td>
					<input type="checkbox" name="USE_ISP_NAMESERVERS" $checked{'USE_ISP_NAMESERVERS'}{'on'}>
				</td>
			</tr>

			<tr>
				<td colspan="2">
					<br>
				</td>
			</tr>

			<tr>
				<td width="33%">
					$Lang::tr{'dns use protocol for dns queries'}
				</td>

				<td>
					<select name="PROTO">
						<option value="UDP" $selected{'PROTO'}{'UDP'}>UDP</option>
						<option value="TLS" $selected{'PROTO'}{'TLS'}>TLS</option>
						<option value="TCP" $selected{'PROTO'}{'TCP'}>TCP</option>
					</select>
				</td>
			</tr>

			<tr>
				<td colspan="2">
					<br>
				</td>
			</tr>

			<tr>
				<td width="33%">
					$Lang::tr{'dns enable safe-search'}
				</td>

				<td>
					<input type="checkbox" name="ENABLE_SAFE_SEARCH" $checked{'ENABLE_SAFE_SEARCH'}{'on'}>
				</td>
			</tr>

			<tr>
				<td colspan="2">
					<br>
				</td>
			</tr>

			<tr>
				<td width="33%">
					$Lang::tr{'dns mode for qname minimisation'}
				</td>

				<td>
					<select name="QNAME_MIN">
						<option value="standard" $selected{'QNAME_MIN'}{'standard'}>$Lang::tr{'standard'}</option>
						<option value="strict" $selected{'QNAME_MIN'}{'strict'}>$Lang::tr{'strict'}</option>
					</select>
				</td>
			</tr>

			<tr>
				<td colspan="2" align="right">
					<input type="submit" name="GENERAL" value="$Lang::tr{'save'}">
				</td>
			</tr>
		</table>
	</form>
END

	&Header::closebox();
}

###
# Section to display the configured and used DNS servers.
#
sub show_nameservers () {
	&Header::openbox('100%', 'center', "$Lang::tr{'dns servers'}");

	# Determine if we are running in recursor mode
	my $recursor = 0;
	my $unbound_forward = qx(unbound-control forward);
	if ($unbound_forward =~ m/^off/) {
		$recursor = 1;
	}

	my $dns_status_string;
	my $dns_status_col;
	my $dns_working;


	# Test if the DNS system is working.
	#
	# Simple send a request to unbound and check if it can resolve the
	# DNS test server.
	my $dns_status_ret = &check_nameserver("127.0.0.1", "$dns_test_server", "UDP", undef, "+timeout=5", "+retry=0");

	if ($dns_status_ret eq "2") {
		$dns_status_string = "$Lang::tr{'working'}";
		$dns_status_col = "${Header::colourgreen}";
		$dns_working = 1;
	} else {
		$dns_status_string = "$Lang::tr{'broken'}";
		$dns_status_col = "${Header::colourred}";
	}

	if ($recursor) {
		$dns_status_string .= " (" . $Lang::tr{'dns recursor mode'} . ")";
	}

	print <<END;
		<table width='100%'>
			<tr>
				<td>
					<strong>$Lang::tr{'status'}:&nbsp;</strong>
					<strong><font color='$dns_status_col'>$dns_status_string</font></strong>
				</td>
			</tr>
		</table>
END

	# Check the usage of ISP assigned nameservers is enabled.
	my $id = 1;

	# Loop through the array which stores the files.
	foreach my $file (@ISP_nameserver_files) {
		# Grab the address of the nameserver.
		my $address = &General::grab_address_from_file($file);

		# Check if we got an address.
		if ($address) {
			# Add the address to the hash of nameservers.
			$dns_servers{$id} = [ "$address", "none",
				($settings{'USE_ISP_NAMESERVERS'} eq "on") ? "enabled" : "disabled",
				"$Lang::tr{'dns isp assigned nameserver'}" ];

			# Increase id by one.
			$id++;
		}
	}

	# Check some DNS servers have been configured. In this case
	# the hash contains at least one key.
	my $server_amount;
	if (keys %dns_servers) {
		# Sort the keys by their ID and store them in an array.
		my @keys = sort { $a <=> $b } keys %dns_servers;

		print <<END;
		<br>

		<table class="tbl" width='100%'>
			<tr>
				<td align="center">
					<strong>$Lang::tr{'nameserver'}</strong>
				</td>

				<td align="center">
					<strong>$Lang::tr{'country'}</strong>
				</td>

				<td align="center">
					<strong>$Lang::tr{'rdns'}</strong>
				</td>

				<td align="center">
					<strong>$Lang::tr{'remark'}</strong>
				</td>
END

		# Check if the status should be displayed.
		if ($check_servers) {
			print <<END;
				<td align="center">
					<strong>$Lang::tr{'status'}</strong>
				</td>
END
		}

		print <<END;

				<td align="center" colspan="3">
					<strong>$Lang::tr{'action'}</strong>
				</td>
			</tr>
END

			# Loop through all entries of the array/hash.
			foreach my $id (@keys) {
				# Inrease server_amount.
				$server_amount++;

				# Assign data array positions to some nice variable names.
				my $nameserver = $dns_servers{$id}[0];
				my $tls_hostname = $dns_servers{$id}[1];
				my $enabled = $dns_servers{$id}[2];
				my $remark = $dns_servers{$id}[3];

				my $col = '';
				my $toggle = '';
				my $gif = '';
				my $gdesc = '';
				my $notice = "";

				# Colorize columns.
				if ($server_amount % 2) {
					$col="bgcolor='$color{'color22'}'"; }
				else {
					$col="bgcolor='$color{'color20'}'";
				}

				if ($enabled eq 'enabled') {
					$gif='on.gif'; $toggle='off'; $gdesc=$Lang::tr{'click to disable'};
				} else {
					$gif='off.gif'; $toggle='on'; $gdesc=$Lang::tr{'click to enable'};
				}

				my $status;
				my $status_short;
				my $status_message;
				my $status_colour;

				# Only grab the status if the nameserver is enabled.
				if (($check_servers) && ($enabled eq "enabled")) {
					$status = &check_nameserver("$nameserver", "ping.ipfire.org", "$settings{'PROTO'}", "$tls_hostname");
				}

				if (!defined $status) {
					$status_short = "$Lang::tr{'disabled'}";

				# DNSSEC Not supported
				} elsif ($status eq 0) {
					$status_short = "$Lang::tr{'broken'}";
					$status_message = $Lang::tr{'dnssec not supported'};
					$status_colour = ${Header::colourred};

				# DNSSEC Aware
				} elsif ($status eq 1) {
					$status_short = "$Lang::tr{'not validating'}";
					$status_message = $Lang::tr{'dnssec aware'};
					$status_colour = ${Header::colourblack};

				# DNSSEC Validating
				} elsif ($status eq 2) {
					$status_short = "$Lang::tr{'ok'}";
					$status_message = $Lang::tr{'dnssec validating'};
					$status_colour = ${Header::colourgreen};

				# Error
				} else {
					$status_short = "$Lang::tr{'error'}";
					$status_message = $status;
					$status_colour = ${Header::colourred};
				}

				# collect more information about name server (rDNS, country code)
				my $ccode = &Location::Functions::lookup_country_code($libloc_db_handle, $nameserver);
				my $flag_icon = &Location::Functions::get_flag_icon($ccode);

				my $rdns;

				# Only do the reverse lookup if the system is online.
				if ($dns_working) {
					my $iaddr = inet_aton($nameserver);
					$rdns = gethostbyaddr($iaddr, AF_INET);
				}

				if (!$rdns) { $rdns = $Lang::tr{'lookup failed'}; }

				# Mark ISP name servers as disabled
				if ($id <= 2 && $enabled eq "disabled") {
					$nameserver = "<del>$nameserver</del>";
				}

print <<END;
			<tr>
				<td align="center" $col>
					$nameserver
				</td>

				<td align="center" $col>
					<a href='country.cgi#$ccode'><img src="$flag_icon" border="0" alt="$ccode" title="$ccode" /></a>
				</td>

				<td align="center" $col>
					$rdns
				</td>

				<td align="center" $col>
					$remark
				</td>
END
;
				# Display server status if requested.
				if ($check_servers) {
print <<END
					<td align="center" $col>
						<strong><font color="$status_colour"><abbr title="$status_message">$status_short</abbr></font></strong>
					</td>
END
;
				}

				# Check if the id is greater than "2".
				#
				# Nameservers with an ID's of one or two are ISP assigned,
				# and we cannot perform any actions on them, so hide the tools for
				# them.
				if ($id > 2) {

print <<END;
					<td align='center' width='5%' $col>
						<form method='post' name='frma$id' action='$ENV{'SCRIPT_NAME'}'>
							<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' title='$gdesc' alt='$gdesc' />
							<input type='hidden' name='ID' value='$id' />
							<input type='hidden' name='ENABLE' value='$toggle' />
							<input type='hidden' name='SERVERS' value='$Lang::tr{'toggle enable disable'}' />
						</form>
					</td>

					<td align='center' width='5%' $col>
						<form method='post' name='frmb$id' action='$ENV{'SCRIPT_NAME'}'>
							<input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' title='$Lang::tr{'edit'}' alt='$Lang::tr{'edit'}' />
							<input type='hidden' name='ID' value='$id' />
							<input type='hidden' name='SERVERS' value='$Lang::tr{'edit'}' />
						</form>
					</td>

					<td align='center' width='5%' $col>
						<form method='post' name='frmc$id' action='$ENV{'SCRIPT_NAME'}'>
							<input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' title='$Lang::tr{'remove'}' alt='$Lang::tr{'remove'}' />
							<input type='hidden' name='ID' value='$id' />
							<input type='hidden' name='SERVERS' value='$Lang::tr{'remove'}' />
						</form>
					</td>
END
;
			} else {
					print "<td colspan='3' $col>&nbsp;</td>\n";
			}


			print"</tr>\n";

		}

		print"</table>\n";

		print"<table width='100%'>\n";

		# Check if the usage of the ISP nameservers is enabled and there are more than 2 servers.
		if (($settings{'USE_ISP_NAMESERVERS'} eq "on") && ($server_amount > 2)) {
print <<END;
			<tr>
				<td class='boldbase'>&nbsp; <b>$Lang::tr{'legend'}:</b></td>
				<td>&nbsp; <img src='/images/on.gif' alt='$Lang::tr{'click to disable'}' /></td>
				<td class='base'>$Lang::tr{'click to disable'}</td>
				<td>&nbsp; &nbsp; <img src='/images/off.gif' alt='$Lang::tr{'click to enable'}' /></td>
				<td class='base'>$Lang::tr{'click to enable'}</td>
				<td>&nbsp; &nbsp; <img src='/images/edit.gif' alt='$Lang::tr{'edit'}' /></td>
				<td class='base'>$Lang::tr{'edit'}</td>
				<td>&nbsp; &nbsp; <img src='/images/delete.gif' alt='$Lang::tr{'remove'}' /></td>
				<td class='base'>$Lang::tr{'remove'}</td>
			</tr>
END
;
		}
print <<END;
			<tr>
				<form method="post" action="$ENV{'SCRIPT_NAME'}">
					<td colspan="9" align="right">
						<input type="submit" name="SERVERS" value="$Lang::tr{'add'}">
						<input type="submit" name="SERVERS" value="$Lang::tr{'dns check servers'}">
					</td>
				</form>
			</tr>
		</table>
END
;
		} else {
			print <<END;
		<table width="100%">
			<tr>
				<form method="post" action="$ENV{'SCRIPT_NAME'}">
					<td colspan="6" align="right"><input type="submit" name="SERVERS" value="$Lang::tr{'add'}"></td>
				</form>
			</tr>
		</table>
END
		}

	&Header::closebox();
}

###
# Section to display the add or edit subpage.
#
sub show_add_edit_nameserver() {
	print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

	my $buttontext = $Lang::tr{'save'};
	my $dnssec_checked;
	my $dot_checked;
	if ($cgiparams{'SERVERS'} eq $Lang::tr{'edit'}) {
		&Header::openbox('100%', 'left', $Lang::tr{'dnsforward edit an entry'});

		# Update button text for upate the existing entry.
		$buttontext = $Lang::tr{'update'};

		# Add hidden input for sending ID.
		print"<input type='hidden' name='ID' value='$cgiparams{'ID'}'>\n";

		# Check if an ID has been given.
		if ($cgiparams{'ID'}) {
			# Assign cgiparams values.
			$cgiparams{'NAMESERVER'} = $dns_servers{$cgiparams{'ID'}}[0];
			$cgiparams{'TLS_HOSTNAME'} = $dns_servers{$cgiparams{'ID'}}[1];
			$cgiparams{'REMARK'} = $dns_servers{$cgiparams{'ID'}}[3];
		}
	} else {
		&Header::openbox('100%', 'left', $Lang::tr{'dnsforward add a new entry'});
	}

	my $tls_required_image;

	# If the protocol is TLS, dispaly the required image.
	if ($settings{'PROTO'} eq "TLS") {
		$tls_required_image = "<img src='/blob.gif' alt='*'>";
	}

	# Add hidden input to store the mode.
	print "<input type='hidden' name='MODE' value='$cgiparams{'SERVERS'}'>\n";

print <<END
	<table width='100%'>
		<tr>
			<td width='20%' class='base'>$Lang::tr{'ip address'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
			<td><input type='text' name='NAMESERVER' value='$cgiparams{"NAMESERVER"}' size='24' /></td>
		</tr>


		<tr>
			<td width='20%' class='base'>$Lang::tr{'dns tls hostname'}:&nbsp;$tls_required_image</td>
			<td><input type='text' name='TLS_HOSTNAME' value='$cgiparams{'TLS_HOSTNAME'}' size='24'></td>
		</tr>


		<tr>
			<td width ='20%' class='base'>$Lang::tr{'remark'}:</td>
			<td><input type='text' name='REMARK' value='$cgiparams{'REMARK'}' size='40' maxlength='50' /></td>
		</tr>
	</table>

	<br>
	<hr>

	<table width='100%'>
		<tr>
			<td class='base' width='55%'><img src='/blob.gif' alt ='*' align='top' />&nbsp;$Lang::tr{'required field'}</td>
			<td width='40%' align='right'>
				<input type="submit" name="SERVERS" value="$buttontext">
				<input type="submit" name="SERVERS" value="$Lang::tr{'back'}">
			</td>
		</tr>
	</table>
END
;

	&Header::closebox();
	print "</form>\n";

	&Header::closebox();
}

# Private function to handle the restart of unbound and more.
sub _handle_unbound_and_more () {
	# Check if the IDS is running.
	if(&IDS::ids_is_running()) {
		# Re-generate the file which contains the DNS Server
		# details.
		&IDS::generate_dns_servers_file();

		# Call suricatactrl to perform a reload.
		&IDS::call_suricatactrl("restart");
	}
	# Restart unbound
	system('/usr/local/bin/unboundctrl reload >/dev/null');
}

# Check if the system is online (RED is connected).
sub red_is_active () {
	# Check if the "active" file is present.
	if ( -f "${General::swroot}/red/active") {
		# Return "1" - True.
		return 1;
	} else {
		# Return nothing - False.
		return;
	}
}

# Function to check a given nameserver against propper work.
sub check_nameserver($$$$$) {
	my ($nameserver, $record, $proto, $tls_hostname, @args) = @_;

	# Check if the system is online.
	unless (&red_is_active()) {
		return "$Lang::tr{'system is offline'}";
	}

	# Default values.
	my @command = ("kdig", "+dnssec",
		"+bufsize=1232", @args);

	# Handle different protols.
	if ($proto eq "TCP") {
		# Add TCP switch to the command.
		push(@command, "+tcp");

	} elsif($proto eq "TLS") {
		# Add TLS switch to the command and provide the
		# path to our file which contains the ca certs.
		push(@command, "+tls-ca=$ca_certs_file");

		# Check if a TLS hostname has been provided.
		if ($tls_hostname) {
			# Add TLS hostname to the command.
			push(@command, "+tls-hostname=$tls_hostname");
		} else {
			return "$Lang::tr{'dns no tls hostname given'}";
		}
	}

	# Add record to the command array.
	push(@command, "$record");

	# Add nameserver to the command array.
	push(@command, "\@$nameserver");

	# Connect to STDOUT and STDERR.
	push(@command, "2>&1");

        my @output = qx(@command);
        my $output = join("", @output);

	my $status = 0;

	if ($output =~ m/status: (\w+)/) {
		$status = ($1 eq "NOERROR");

		if (!$status) {
			return -1;
		}
	} else {
		my $warning;

		while ($output =~ m/WARNING: (.*)/g) {
			# Add the current grabbed warning to the warning string.
			$warning .= "$1\; ";
		}

		# Return the warning string, if we grabbed at least one.
		if ($warning) {
			return $warning;
		}
	}

	my @flags = ();
	if ($output =~ m/Flags: (.*);/) {
		@flags = split(/ /, $1);
	}

	my $aware = ($output =~ m/RRSIG/);
	my $validating = (grep(/ad;/, @flags));

	return $aware + $validating;
}
