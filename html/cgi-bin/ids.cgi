#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2025  IPFire Team  <info@ipfire.org>                     #
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
use experimental 'smartmatch';

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/ids-functions.pl";
require "${General::swroot}/network-functions.pl";

# Import ruleset providers file.
require "$IDS::rulesetsourcesfile";

my %color = ();
my %mainsettings = ();
my %idsrules = ();
my %idssettings=();
my %used_providers=();
my %cgiparams=();
my %checked=();
my %selected=();
my %ignored=();

# Read-in main settings, for language, theme and colors.
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/ipfire/include/colors.txt", \%color);

# Get the available network zones, based on the config type of the system and store
# the list of zones in an array.
my @network_zones = &Network::get_available_network_zones();

# Always show IPsec & Wireguard
push(@network_zones, "ipsec", "wg");

# Check if openvpn is started and add it to the array of network zones.
if ( -e "/var/run/openvpn-rw.pid") {
	push(@network_zones, "ovpn");
}

my $errormessage;

# Create files if they does not exist yet.
&IDS::check_and_create_filelayout();

# Hash which contains the colour code of a network zone.
my %colourhash = (
	'red' => $Header::colourred,
	'green' => $Header::colourgreen,
	'blue' => $Header::colourblue,
	'orange' => $Header::colourorange,
	'ipsec' => $Header::colourvpn,
	'ovpn' => $Header::colourovpn,
	'wg' => $Header::colourwg,
);

&Header::showhttpheaders();

#Get GUI values
&Header::getcgihash(\%cgiparams);

## Add/edit an entry to the ignore file.
#
if (($cgiparams{'WHITELIST'} eq $Lang::tr{'add'}) || ($cgiparams{'WHITELIST'} eq $Lang::tr{'update'})) {

	# Check if any input has been performed.
	if ($cgiparams{'IGNORE_ENTRY_ADDRESS'} ne '') {

		# Check if the given input is no valid IP-address or IP-address with subnet, display an error message.
		if ((!&General::validip($cgiparams{'IGNORE_ENTRY_ADDRESS'})) && (!&General::validipandmask($cgiparams{'IGNORE_ENTRY_ADDRESS'}))) {
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
		my $new_entry_address = $cgiparams{'IGNORE_ENTRY_ADDRESS'};
		my $new_entry_remark = $cgiparams{'IGNORE_ENTRY_REMARK'};

		# Read-in ignoredfile.
		&General::readhasharray($IDS::ignored_file, \%ignored) if (-e $IDS::ignored_file);

		# Check if we should edit an existing entry and got an ID.
		if (($cgiparams{'WHITELIST'} eq $Lang::tr{'update'}) && ($cgiparams{'ID'})) {
			# Assin the provided id.
			$id = $cgiparams{'ID'};

			# Undef the given ID.
			undef($cgiparams{'ID'});

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
		&General::writehasharray($IDS::ignored_file, \%ignored);

		# Regenerate the ignore file.
		&IDS::generate_ignore_file();
	}

	# Check if the IDS is running.
	if(&IDS::ids_is_running()) {
		# Call suricatactrl to perform a reload.
		&IDS::call_suricatactrl("reload");
	}

## Toggle Enabled/Disabled for an existing entry on the ignore list.
#

} elsif ($cgiparams{'WHITELIST'} eq $Lang::tr{'toggle enable disable'}) {
	my %ignored = ();

	# Only go further, if an ID has been passed.
	if ($cgiparams{'ID'}) {
		# Assign the given ID.
		my $id = $cgiparams{'ID'};

		# Undef the given ID.
		undef($cgiparams{'ID'});

		# Read-in ignoredfile.
		&General::readhasharray($IDS::ignored_file, \%ignored) if (-e $IDS::ignored_file);

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
		&General::writehasharray($IDS::ignored_file, \%ignored);

		# Regenerate the ignore file.
		&IDS::generate_ignore_file();

		# Check if the IDS is running.
		if(&IDS::ids_is_running()) {
			# Call suricatactrl to perform a reload.
			&IDS::call_suricatactrl("reload");
		}
	}

## Remove entry from ignore list.
#
} elsif ($cgiparams{'WHITELIST'} eq $Lang::tr{'remove'}) {
	my %ignored = ();

	# Read-in ignoredfile.
	&General::readhasharray($IDS::ignored_file, \%ignored) if (-e $IDS::ignored_file);

	# Drop entry from the hash.
	delete($ignored{$cgiparams{'ID'}});

	# Undef the given ID.
	undef($cgiparams{'ID'});

	# Write the changed ignored hash to the ignored file.
	&General::writehasharray($IDS::ignored_file, \%ignored);

	# Regenerate the ignore file.
	&IDS::generate_ignore_file();

	# Check if the IDS is running.
	if(&IDS::ids_is_running()) {
		# Call suricatactrl to perform a reload.
		&IDS::call_suricatactrl("reload");
	}
}

# Check if the page is locked, in this case, the ids_page_lock_file exists.
if (-e $IDS::ids_page_lock_file) {
	# Lock the webpage and print notice about autoupgrade of the ruleset
	# is in progess.
	&working_notice("$Lang::tr{'ids ruleset autoupdate in progress'}");

	# Loop and check if the file still exists.
	while(-e $IDS::ids_page_lock_file) {
		# Sleep for a second and re-check.
		sleep 1;
	}

	# Page has been unlocked, perform a reload.
	&reload();
}

# Check if any error has been stored.
if (-e $IDS::storederrorfile) {
        # Open file to read in the stored error message.
        open(FILE, "<$IDS::storederrorfile") or die "Could not open $IDS::storederrorfile. $!\n";

        # Read the stored error message.
        $errormessage = <FILE>;

        # Close file.
        close (FILE);

        # Delete the file, which is now not longer required.
        unlink($IDS::storederrorfile);
}

# Gather ruleset details.
if ($cgiparams{'RULESET'}) {
	## Grab all available rules and store them in the idsrules hash.
	#

	# Get enabled providers.
	my @enabled_providers = &IDS::get_enabled_providers();

	# Open rules directory and do a directory listing.
	opendir(DIR, $IDS::rulespath) or die $!;
		# Loop through the direcory.
		while (my $file = readdir(DIR)) {

			# We only want files.
			next unless (-f "$IDS::rulespath/$file");

			# Ignore empty files.
			next if (-z "$IDS::rulespath/$file");

			# Use a regular expression to find files ending in .rules
			next unless ($file =~ m/\.rules$/);

			# Ignore files which are not read-able.
			next unless (-R "$IDS::rulespath/$file");

			# Skip whitelist rules file.
			next if( $file eq "whitelist.rules");

			# Splitt vendor from filename.
			my @filename_parts = split(/-/, $file);

			# Assign vendor name for easy processing.
			my $vendor = @filename_parts[0];

			# Skip rulefile if the provider is disabled.
			next unless ($vendor ~~ @enabled_providers);

			# Call subfunction to read-in rulefile and add rules to
			# the idsrules hash.
			&readrulesfile("$file");
		}

	closedir(DIR);

	# Loop through the array of used providers.
	foreach my $provider (@enabled_providers) {
		# Gather used rulefiles.
		my @used_rulesfiles = &IDS::get_provider_used_rulesfiles($provider);

		# Loop through the array of used rulesfiles.
		foreach my $rulefile (@used_rulesfiles) {
			# Check if the current rulefile exists in the %idsrules hash.
			# If not, the file probably does not exist anymore or contains
			# no rules.
			if($idsrules{$rulefile}) {
				# Add the rulefile state to the %idsrules hash.
				$idsrules{$rulefile}{'Rulefile'}{'State'} = "on";
			}
		}
	}
}

# Save ruleset.
if ($cgiparams{'RULESET'} eq $Lang::tr{'ids apply'}) {
	# Get enabled providers.
	my @enabled_providers = &IDS::get_enabled_providers();

	# Loop through the array of enabled providers.
	foreach my $provider (@enabled_providers) {
		# Hash to store the used-enabled and disabled sids.
		my %enabled_disabled_sids;

		# Hash to store the enabled rulefiles for the current processed provider.
		my %used_rulefiles;

		# Get name of the file which holds the ruleset modification of the provider.
		my $modifications_file = &IDS::get_provider_ruleset_modifications_file($provider);

		# Get the name of the file which contains the used rulefiles for this provider.
		my $used_rulefiles_file = &IDS::get_provider_used_rulesfiles_file($provider);

		# Read-in modifications file, if exists.
		&General::readhash("$modifications_file", \%enabled_disabled_sids) if (-f "$modifications_file");

		# Loop through the hash of idsrules.
		foreach my $rulefile (keys %idsrules) {
			# Split the rulefile to get the vendor.
			my @filename_parts = split(/-/, $rulefile);

			# Assign rulefile vendor.
			my $rulefile_vendor = @filename_parts[0];

			# Skip the rulefile if the vendor is not our current processed provider.
			next unless ($rulefile_vendor eq $provider);

			# Check if the rulefile is enabled.
			if ($cgiparams{$rulefile} eq "on") {
				# Add the rulefile to the hash of enabled rulefiles of this provider.
				$used_rulefiles{$rulefile} = "enabled";

				# Drop item from cgiparams hash.
				delete $cgiparams{$rulefile};
			}

			# Loop through the single rules of the rulefile.
			foreach my $sid (keys %{$idsrules{$rulefile}}) {
				# Skip the current sid if it is not numeric.
				next unless ($sid =~ /\d+/ );

				# Check if there exists a key in the cgiparams hash for this sid.
				if (exists($cgiparams{$sid})) {
					# Look if the rule is disabled.
					if ($idsrules{$rulefile}{$sid}{'State'} eq "off") {
						# Check if the state has been set to 'on'.
						if ($cgiparams{$sid} eq "on") {
							# Add/Modify the sid to/in the enabled_disabled_sids hash.
							$enabled_disabled_sids{$sid} = "enabled";

							# Drop item from cgiparams hash.
							delete $cgiparams{$rulefile}{$sid};
						}
					}
				} else {
					# Look if the rule is enabled.
					if ($idsrules{$rulefile}{$sid}{'State'} eq "on") {
						# Check if the state is 'on' and should be disabled.
						# In this case there is no entry
						# for the sid in the cgiparams hash.
						# Add/Modify it to/in the enabled_disabled_sids hash.
						$enabled_disabled_sids{$sid} = "disabled";

						# Drop item from cgiparams hash.
						delete $cgiparams{$rulefile}{$sid};
					}
				}
			}
		}

		# Check if the hash for enabled/disabled sids contains any entries.
		if (%enabled_disabled_sids) {
			# Write the modifications file.
			&General::writehash("$modifications_file", \%enabled_disabled_sids);
		}

		# Write the used rulefiles file.
		&General::writehash("$used_rulefiles_file", \%used_rulefiles);
	}

	# Call function to generate and write the used rulefiles file.
	&IDS::write_used_rulefiles_file(@enabled_providers);

	# Lock the webpage and print message.
	&oinkmaster_web();

	# Check if the IDS is running.
	if(&IDS::ids_is_running()) {
		# Call suricatactrl to perform a reload.
		&IDS::call_suricatactrl("reload");
	}

	# Reload page.
	&reload();

# Download new ruleset.
} elsif ($cgiparams{'PROVIDERS'} eq $Lang::tr{'ids force ruleset update'}) {
	# Assign given provider handle.
	my $provider = $cgiparams{'PROVIDER'};

	# Check if the red device is active.
	unless (-e "${General::swroot}/red/active") {
		$errormessage = "$Lang::tr{'could not download latest updates'} - $Lang::tr{'system is offline'}";
	}

	# Check if enought free disk space is availabe.
	if(&IDS::checkdiskspace()) {
		$errormessage = "$Lang::tr{'not enough disk space'}";
	}

	# Check if any errors happend.
	unless ($errormessage) {
		# Lock the webpage and print notice about downloading
		# a new ruleset.
		&_open_working_notice("$Lang::tr{'ids download new ruleset'}");

		# Call subfunction to download the ruleset.
		my $return = &IDS::downloadruleset($provider);

		# Check if the download function gives a return code.
		if ($return) {
			# Handle different return codes.
			if ($return eq "not modified") {
				$errormessage = "$provider - $Lang::tr{'ids ruleset is up to date'}";
			} else {
				$errormessage = "$provider - $Lang::tr{'could not download latest updates'}: $return";
			}

			# Call function to store the errormessage.
			&IDS::_store_error_message($errormessage);

			# Close the working notice.
			&_close_working_notice();

			# Preform a reload of the page.
			&reload();
		} else {
			# Call subfunction to launch oinkmaster.
			&oinkmaster_web("nolock");

			# Close the working notice.
			&_close_working_notice();

			# Check if the IDS is running.
			if(&IDS::ids_is_running()) {
				# Call suricatactrl to perform a reload.
				&IDS::call_suricatactrl("reload");
			}

			# Perform a reload of the page.
			&reload();
		}
	}

# Reset a provider to it's defaults.
} elsif ($cgiparams{'PROVIDERS'} eq "$Lang::tr{'ids reset provider'}") {
	# Get enabled providers.
	my @enabled_providers = &IDS::get_enabled_providers();

	# Grab provider handle from cgihash.
	my $provider = $cgiparams{'PROVIDER'};

	# Lock the webpage and print message.
	&working_notice("$Lang::tr{'ids apply ruleset changes'}");

	# Get the name of the file which contains the used rulefiles for this provider.
	my $used_rulefiles_file = &IDS::get_provider_used_rulesfiles_file($provider);

	# Remove the file if it exists.
	unlink("$used_rulefiles_file") if (-f "$used_rulefiles_file");

	# Call function to get the path and name for file which holds the ruleset modifications
	# for the given provider.
	my $modifications_file = &IDS::get_provider_ruleset_modifications_file($provider);

	# Check if the file exists.
	if (-f $modifications_file) {
		# Remove the file, as requested.
		unlink("$modifications_file");
	}

	# Write used rulesfiles file.
	&IDS::write_used_rulefiles_file(@enabled_providers);

	# Regenerate ruleset.
	&oinkmaster_web();

	# Check if the IDS is running.
	if(&IDS::ids_is_running()) {
		# Get amount of enabled providers.
		my $amount = @enabled_providers;

		# Check if at least one enabled provider remains.
		if ($amount >= 1) {
			# Call suricatactrl to perform a reload.
			&IDS::call_suricatactrl("reload");

		# Stop suricata if no enabled provider remains.
		} else {
			# Call suricatactrel to perform the stop.
			&IDS::call_suricatactrl("stop");
		}
	}

	# Undefine providers flag.
	undef($cgiparams{'PROVIDERS'});

	# Reload page.
	&reload();

# Save IDS settings.
} elsif ($cgiparams{'IDS'} eq $Lang::tr{'save'}) {
	my %oldidssettings;
	my $reload_page;
	my $monitored_zones = 0;

	# Read-in current (old) IDS settings.
	&General::readhash("$IDS::ids_settings_file", \%oldidssettings);

	# Get enabled providers.
	my @enabled_providers = &IDS::get_enabled_providers();

	# Prevent form name from been stored in conf file.
	delete $cgiparams{'IDS'};

	# Check if the IDS should be enabled.
	if ($cgiparams{'ENABLE_IDS'} eq "on") {
		# Check if at least one provider is enabled. Otherwise abort and display an error.
		unless(@enabled_providers) {
			$errormessage = $Lang::tr{'ids no enabled ruleset provider'};
		}

		# Loop through the array of available interfaces.
		foreach my $zone (@network_zones) {
			# Convert interface name into upper case.
			my $zone_upper = uc($zone);

			# Check if the IDS is enabled for these interfaces.
			if ($cgiparams{"ENABLE_IDS_$zone_upper"}) {
				# Increase count.
				$monitored_zones++;
			}
		}

		# Check if at least one zone should be monitored, or show an error.
		unless ($monitored_zones >= 1) {
			$errormessage = $Lang::tr{'ids no network zone'};
		}
	}

	# Check if the e-mail feature should be used.
	if (($cgiparams{'ENABLE_EMAIL'} eq "on") || ($cgiparams{'ENABLE_REPORT_DAILY'} eq "on") ||
	    ($cgiparams{'ENABLE_REPORT_WEEKLY'} eq "on") || ($cgiparams{'ENABLE_REPORT_MONTLY'} eq "on")) {
		# Check if a sender mail address has been provided.
		unless($cgiparams{'EMAIL_SENDER'}) {
			$errormessage = $Lang::tr{'ids no email sender'};
		}

		# Check if the given sender mail address is valid.
		if (&_validate_mail_address($cgiparams{'EMAIL_SENDER'})) {
			$errormessage = "$cgiparams{'EMAIL_SENDER'} - $Lang::tr{'ids invalid mail address'}";
		}

		# Check if at least one mail recipient has been given.
		unless($cgiparams{'EMAIL_RECIPIENTS'}) {
			$errormessage = $Lang::tr{'ids no email recipients'};
		}

		# Check if the given recipient mail address or addresses are valid.
		if (&_validate_mail_address($cgiparams{'EMAIL_RECIPIENTS'})) {
			$errormessage = "$cgiparams{'EMAIL_RECIPIENTS'} - $Lang::tr{'ids invalid mail address'}";
		}
	}

	# Go on if there are no error messages.
	if (!$errormessage) {
		# Store settings into settings file.
		&General::writehash("$IDS::ids_settings_file", \%cgiparams);
	}

	# Generate file to store the home net.
	&IDS::generate_home_net_file();

	# Generate file to the store the DNS servers.
	&IDS::generate_dns_servers_file();

	# Generate file to store the HTTP ports.
	&IDS::generate_http_ports_file();

	# Generate report generator config file.
	&IDS::generate_report_generator_config();

	# Check if the IDS currently is running.
	if(&IDS::ids_is_running()) {
		# Check if ENABLE_IDS is set to on.
		if($cgiparams{'ENABLE_IDS'} eq "on") {
			# Call suricatactrl to perform a reload of suricata.
			&IDS::call_suricatactrl("reload");
		} else {
			# Call suricatactrl to stop suricata.
			&IDS::call_suricatactrl("stop");
		}
	} else {
		# Call suricatactrl to start suricata.
		&IDS::call_suricatactrl("start");
	}

	# Check if the page should be reloaded.
	if ($reload_page) {
		# Perform a reload of the page.
		&reload();
	}

# Toggle Enable/Disable autoupdate for a provider
} elsif ($cgiparams{'AUTOUPDATE'} eq $Lang::tr{'toggle enable disable'}) {
	my %used_providers = ();

	# Only go further, if an ID has been passed.
	if ($cgiparams{'ID'}) {
		# Assign the given ID.
		my $id = $cgiparams{'ID'};

		# Undef the given ID.
		undef($cgiparams{'ID'});

		# Read-in providers settings file.
		&General::readhasharray($IDS::providers_settings_file, \%used_providers);

		# Grab the configured status of the corresponding entry.
		my $status_autoupdate = $used_providers{$id}[2];

		# Switch the status.
		if ($status_autoupdate eq "disabled") {
			$status_autoupdate = "enabled";
		} else {
			$status_autoupdate = "disabled";
		}

		# Modify the status of the existing entry.
		$used_providers{$id} = ["$used_providers{$id}[0]", "$used_providers{$id}[1]", "$status_autoupdate", "$used_providers{$id}[3]", "$used_providers{$id}[4]"];

		# Write the changed hash to the providers settings file.
		&General::writehasharray($IDS::providers_settings_file, \%used_providers);
	}

# Add/Edit a provider to the list of used providers.
#
} elsif (($cgiparams{'PROVIDERS'} eq "$Lang::tr{'add'}") || ($cgiparams{'PROVIDERS'} eq "$Lang::tr{'update'}")) {
	my %used_providers = ();

	# Read-in providers settings file.
	&General::readhasharray("$IDS::providers_settings_file", \%used_providers);

	# Assign some nice human-readable values.
	my $provider = $cgiparams{'PROVIDER'};
	my $subscription_code = $cgiparams{'SUBSCRIPTION_CODE'};
	my $status_autoupdate;
	my $mode;
	my $regenerate_ruleset_required;

	# Handle autoupdate checkbox.
	if ($cgiparams{'ENABLE_AUTOUPDATE'} eq "on") {
		$status_autoupdate = "enabled";
	} else {
		$status_autoupdate = "disabled";
	}

	# Handle monitor traffic only checkbox.
	if ($cgiparams{'MONITOR_TRAFFIC_ONLY'} eq "on") {
		$mode = "IDS";
	} else {
		$mode = "IPS";
	}

	# Check if we are going to add a new provider.
	if ($cgiparams{'PROVIDERS'} eq "$Lang::tr{'add'}") {
		# Loop through the hash of used providers.
		foreach my $id ( keys %used_providers) {
			# Check if the choosen provider is already in use.
			if ($used_providers{$id}[0] eq "$provider") {
				# Assign error message.
				$errormessage = "$Lang::tr{'ids the choosen provider is already in use'}";
			}
		}
	}

	# Check if the provider requires a subscription code.
	if ($IDS::Ruleset::Providers{$provider}{'requires_subscription'} eq "True") {
		# Check if an subscription code has been provided.
		if ($subscription_code) {
			# Check if the code contains unallowed chars.
			unless ($subscription_code =~ /^[a-z0-9]+$/) {
				$errormessage = $Lang::tr{'invalid input for subscription code'};
			}
		} else {
			# Print an error message, that an subsription code is required for this
			# provider.
			$errormessage = $Lang::tr{'ids subscription code required'};
		}
	}

	# Go further if there was no error.
	if ($errormessage eq '') {
		my $id;
		my $status;

		# Check if we should edit an existing entry and got an ID.
		if (($cgiparams{'PROVIDERS'} eq $Lang::tr{'update'}) && ($cgiparams{'ID'})) {
			# Assin the provided id.
			$id = $cgiparams{'ID'};

			# Undef the given ID.
			undef($cgiparams{'ID'});

			# Grab the configured mode.
			my $stored_mode = $used_providers{$id}[4];

			# Check if the ruleset action (mode) has been changed.
			if ($stored_mode ne $mode) {
				# It has been changed, so the ruleset needs to be regenerated.
				$regenerate_ruleset_required = "1";
			}

			# Grab the configured status of the corresponding entry.
			$status = $used_providers{$id}[3];
		} else {
			# Each newly added entry automatically should be enabled.
			$status = "enabled";

			# Generate the ID for the new entry.
			#
			# Sort the keys by their ID and store them in an array.
			my @keys = sort { $a <=> $b } keys %used_providers;

			# Reverse the key array.
			my @reversed = reverse(@keys);

			# Obtain the last used id.
			my $last_id = @reversed[0];

			# Increase the last id by one and use it as id for the new entry.
			$id = ++$last_id;
		}

		# Add/Modify the entry to/in the used providers hash..
		$used_providers{$id} = ["$provider", "$subscription_code", "$status_autoupdate", "$status", "$mode"];

		# Write the changed hash to the providers settings file.
		&General::writehasharray($IDS::providers_settings_file, \%used_providers);

		# Check if a new provider will be added.
		if ($cgiparams{'PROVIDERS'} eq $Lang::tr{'add'}) {
			# Check if the red device is active.
			unless (-e "${General::swroot}/red/active") {
				$errormessage = "$Lang::tr{'ids could not add provider'} - $Lang::tr{'system is offline'}";
			}

			# Check if enough free disk space is availabe.
			if(&IDS::checkdiskspace()) {
				$errormessage = "$Lang::tr{'ids could not add provider'} - $Lang::tr{'not enough disk space'}";
			}

			# Check if any errors happend.
			unless ($errormessage) {
				# Lock the webpage and print notice about downloading
				# a new ruleset.
				&working_notice("$Lang::tr{'ids working'}");

				# Download the ruleset.
				my $return = &IDS::downloadruleset($provider);

				# Check if the downloader returned a code.
				if ($return) {
					$errormessage = "$Lang::tr{'ids could not add provider'} - $Lang::tr{'ids unable to download the ruleset'}: $return";

					# Call function to store the errormessage.
					&IDS::_store_error_message($errormessage);

					# Remove the configured provider again.
					&remove_provider($id);
				} else {
					# Extract the ruleset
					&IDS::extractruleset($provider);

					# Move the ruleset.
					&IDS::move_tmp_ruleset();

					# Cleanup temporary directory.
					&IDS::cleanup_tmp_directory();
				}

				# Perform a reload of the page.
				&reload();
			} else {
				# Remove the configured provider again.
				&remove_provider($id);
			}
		}

		# Check if the ruleset has to be regenerated.
		if ($regenerate_ruleset_required) {
			# Call oinkmaster web function.
			&oinkmaster_web();

			# Perform a reload of the page.
			&reload();
		}
	}

	# Undefine providers flag.
	undef($cgiparams{'PROVIDERS'});

## Toggle Enabled/Disabled for an existing provider.
#
} elsif ($cgiparams{'PROVIDERS'} eq $Lang::tr{'toggle enable disable'}) {
	my %used_providers = ();
	my $provider_includes_action;

	# Value if oinkmaster has to be executed.
	my $oinkmaster = "False";

	# Only go further, if an ID has been passed.
	if ($cgiparams{'ID'}) {
		# Assign the given ID.
		my $id = $cgiparams{'ID'};

		# Undef the given ID.
		undef($cgiparams{'ID'});

		# Read-in file which contains the provider settings.
		&General::readhasharray($IDS::providers_settings_file, \%used_providers);

		# Grab the configured status of the corresponding entry.
		my $status = $used_providers{$id}[3];

		# Grab the provider handle.
		my $provider_handle = $used_providers{$id}[0];

		# Switch the status.
		if ($status eq "enabled") {
			$status = "disabled";

			# Set the provider includes action to "remove" for removing the entry.
			$provider_includes_action = "remove";
		} else {
			$status = "enabled";

			# Set the provider includes action to "add".
			$provider_includes_action = "add";

			# This operation requires to launch oinkmaster.
			$oinkmaster = "True";
		}

		# Modify the status of the existing entry.
		$used_providers{$id} = ["$used_providers{$id}[0]", "$used_providers{$id}[1]", "$used_providers{$id}[2]", "$status", "$used_providers{$id}[4]"];

		# Write the changed hash to the providers settings file.
		&General::writehasharray($IDS::providers_settings_file, \%used_providers);

		# Get all enabled providers.
		my @enabled_providers = &IDS::get_enabled_providers();

		# Write the main providers include file.
		&IDS::write_used_rulefiles_file(@enabled_providers);

		# Check if oinkmaster has to be executed.
		if ($oinkmaster eq "True") {
			# Launch oinkmaster.
			&oinkmaster_web();
		}

		# Check if the IDS is running.
		if(&IDS::ids_is_running()) {
			# Gather the amount of enabled providers (elements in the array).
			my $amount = @enabled_providers;

			# Check if there are still enabled ruleset providers.
			if ($amount >= 1) {
				# Call suricatactrl to perform a restart.
				&IDS::call_suricatactrl("restart");

			# No active ruleset provider, suricata has to be stopped.
			} else {
				# Stop suricata.
				&IDS::call_suricatactrl("stop");
			}
		}

		# Undefine providers flag.
		undef($cgiparams{'PROVIDERS'});

		# Reload page.
		&reload();
	}

## Remove provider from the list of used providers.
#
} elsif ($cgiparams{'PROVIDERS'} eq $Lang::tr{'remove'}) {
	# Assign a nice human-readable variable.
	my $id = $cgiparams{'ID'};

	# Grab the provider name bevore deleting.
	my $provider = &get_provider_handle($id);

	# Remove the provider.
	&remove_provider($id);

	# Undef the given ID.
	undef($cgiparams{'ID'});

	# Drop the stored ruleset file.
	&IDS::drop_dl_rulesfile($provider);

	# Remove may stored etag data.
	&IDS::remove_from_etags($provider);

	# Get the name of the provider rulessets include file.
	my $provider_used_rulefile = &IDS::get_provider_used_rulesfiles_file($provider);

	# Drop the file, it is not longer needed.
	unlink("$provider_used_rulefile");

	# Call function to get the path and name for the given providers
	# ruleset modifications file..
	my $modifications_file = &IDS::get_provider_ruleset_modifications_file($provider);

	# Check if the file exists.
	if (-f $modifications_file) {
		# Remove the file, which is not longer needed.
		unlink("$modifications_file");
	}

	# Regenerate ruleset.
	&oinkmaster_web();

	# Gather all enabled providers.
	my @enabled_providers = &IDS::get_enabled_providers();

	# Regenerate main providers include file.
	&IDS::write_used_rulefiles_file(@enabled_providers);

	# Check if the IDS is running.
	if(&IDS::ids_is_running()) {
		# Get amount of enabled providers.
		my $amount = @enabled_providers;

		# Check if at least one enabled provider remains.
		if ($amount >= 1) {
			# Call suricatactrl to perform a reload.
			&IDS::call_suricatactrl("restart");

		# Stop suricata if no enabled provider remains.
		} else {
			# Call suricatactrel to perform the stop.
			&IDS::call_suricatactrl("stop");
		}
	}

	# Undefine providers flag.
	undef($cgiparams{'PROVIDERS'});

	# Reload page.
	&reload();
}

&Header::openpage($Lang::tr{'intrusion detection system'}, 1, '');

&Header::openbigbox('100%', 'left', '', $errormessage);

&show_display_error_message();

if ($cgiparams{'RULESET'} eq "$Lang::tr{'ids customize ruleset'}" ) {
	&show_customize_ruleset();
} elsif ($cgiparams{'PROVIDERS'} ne "") {
	&show_add_provider();
} else {
	&show_mainpage();
}

&Header::closebigbox();
&Header::closepage();

#
## Tiny function to show if a error message happened.
#
sub show_display_error_message() {
	if ($errormessage) {
		&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
			print "<class name='base'>$errormessage\n";
			print "&nbsp;</class>\n";
		&Header::closebox();
	}
}

#
## Function to display the main IDS page.
#
sub show_mainpage() {
	# Read-in idssettings and provider settings.
	&General::readhash("$IDS::ids_settings_file", \%idssettings);
	&General::readhasharray("$IDS::providers_settings_file", \%used_providers);

	# Read-in ignored hosts.
	&General::readhasharray("$IDS::ignored_file", \%ignored) if (-e $IDS::ignored_file);

	$checked{'ENABLE_IDS'}{'off'} = '';
	$checked{'ENABLE_IDS'}{'on'} = '';
	$checked{'ENABLE_IDS'}{$idssettings{'ENABLE_IDS'}} = "checked='checked'";
	$checked{'ENABLE_EMAIL'}{'off'} = '';
	$checked{'ENABLE_EMAIL'}{'on'} = '';
	$checked{'ENABLE_EMAIL'}{$idssettings{'ENABLE_EMAIL'}} = "checked='checked'";

	$selected{'EMAIL_ALERT_SEVERITY'}{$idssettings{'EMAIL_ALERT_SEVERITY'}} = "selected";

	$checked{'ENABLE_REPORT_DAILY'}{'off'} = '';
	$checked{'ENABLE_REPORT_DAILY'}{'on'} = '';
	$checked{'ENABLE_REPORT_DAILY'}{$idssettings{'ENABLE_REPORT_DAILY'}} = "checked='checked'";
	$checked{'ENABLE_REPORT_WEEKLY'}{'off'} = '';
	$checked{'ENABLE_REPORT_WEEKLY'}{'on'} = '';
	$checked{'ENABLE_REPORT_WEEKLY'}{$idssettings{'ENABLE_REPORT_WEEKLY'}} = "checked='checked'";
	$checked{'ENABLE_REPORT_MONTHLY'}{'off'} = '';
	$checked{'ENABLE_REPORT_MONTHLY'}{'on'} = '';
	$checked{'ENABLE_REPORT_MONTHLY'}{$idssettings{'ENABLE_REPORT_MONTHLY'}} = "checked='checked'";

	# Set E-Mail settings from settings hash.
	my $email_sender = $idssettings{'EMAIL_SENDER'};
	my $email_recipients = $idssettings{'EMAIL_RECIPIENTS'};

	# Set form values to cgiparams state in error case.
	if ($errormessage) {
		$checked{'ENABLE_IDS'}{$cgiparams{'ENABLE_IDS'}} = "checked='checked'";
		$checked{'ENABLE_EMAIL'}{$cgiparams{'ENABLE_EMAIL'}} = "checked='checked'";
		$checked{'ENABLE_REPORT_DAILY'}{$cgiparams{'ENABLE_REPORT_DAILY'}} = "checked='checked'";
		$checked{'ENABLE_REPORT_WEEKLY'}{$cgiparams{'ENABLE_REPORT_WEEKLY'}} = "checked='checked'";
		$checked{'ENABLE_REPORT_MONTHLY'}{$cgiparams{'ENABLE_REPORT_MONTHLY'}} = "checked='checked'";

		$email_sender = $cgiparams{'EMAIL_SENDER'};
		$email_recipients = $cgiparams{'EMAIL_RECIPIENTS'};
	}

	# Draw current state of the IDS
	&Header::opensection();

	&Header::ServiceStatus({
		$Lang::tr{'intrusion prevention system'} => {
			"pidfile" => "/var/run/suricata.pid",
		},
	});

	# Only show this area, if at least one ruleset provider is configured.
	if (%used_providers) {
		my $num_zones = scalar @network_zones;

print <<END
		<br>

		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<table class='form'>
				<tr>
					<td>
						$Lang::tr{'ids enable'}
					</td>

					<td>
						<input type='checkbox' name='ENABLE_IDS' $checked{'ENABLE_IDS'}{'on'}>
					</td>
				</tr>
			</table>

			<h6>
				$Lang::tr{'ids monitored interfaces'}
			</h6>

			<table class="form">
END
;

		# Loop through the array of available networks and print config options.
		foreach my $zone (@network_zones) {
			my $checked_input;
			my $checked_forward;

			# Convert current zone name to upper case.
			my $zone_upper = uc($zone);

			# Set zone name.
			my $zone_name = $zone;

			# Dirty hack to get the correct language string for the red zone.
			if ($zone eq "red") {
				$zone_name = "red1";
			}

			# Grab checkbox status from settings hash.
			if ($idssettings{"ENABLE_IDS_$zone_upper"} eq "on") {
				$checked_input = "checked = 'checked'";
			}

			# Set the checkbox status to the cgiparams state in error case.
			if ($errormessage) {
				$checked_input = "checked = 'checked'" if ($cgiparams{"ENABLE_IDS_$zone_upper"} eq "on");
			}

			print <<END;
				<tr>
					<td>
						&nbsp; &nbsp; <font color='$colourhash{$zone}'> $Lang::tr{$zone_name}</font>
					</td>

					<td>
						<input type='checkbox' name='ENABLE_IDS_$zone_upper' $checked_input>
					</td>
				</tr>
END
		}

print <<END
			</table>

			<h6>
				$Lang::tr{'ids email alerts'}
			</h6>

			<table class="form">
				<tr>
					<td>
						<label for='EMAIL_SENDER'>$Lang::tr{'ids email sender'}</label>
					</td>

					<td>
						<input type="text" name="EMAIL_SENDER" value="$email_sender">
					<td>
				</tr>

				<tr>
					<td>
						<label for='EMAIL_RECIPIENTS'>$Lang::tr{'ids email recipients'}</label>
					</td>

					<td>
						<input type="text" name="EMAIL_RECIPIENTS" value="$email_recipients">
					</td>
				</tr>

				<tr>
					<td colspan="2">&nbsp;</td>
				</tr>

				<tr>
					<td>
						<label for="ENABLE_EMAIL">
							$Lang::tr{'ids send email on alert'}
						</label>
					</td>

					<td>
						<input type='checkbox' name='ENABLE_EMAIL' id="ENABLED_EMAIL" $checked{'ENABLE_EMAIL'}{'on'}>
					</td>
				</tr>

				<tr>
					<td>
						<label for="EMAIL_ALERT_SEVERITY">
							$Lang::tr{'ids email alert severity'}
						</label>
					</td>

					<td>
						<select name="EMAIL_ALERT_SEVERITY">
							<option value="4" $selected{'EMAIL_ALERT_SEVERITY'}{'4'}>
								$Lang::tr{'ids all including informational'}
							</option>
							<option value="3" $selected{'EMAIL_ALERT_SEVERITY'}{'3'}>
								$Lang::tr{'ids high, medium and low severity'}
							</option>
							<option value="2" $selected{'EMAIL_ALERT_SEVERITY'}{'2'}>
								$Lang::tr{'ids high and medium severity'}
							</option>
							<option value="1" $selected{'EMAIL_ALERT_SEVERITY'}{'1'}>
								$Lang::tr{'ids high severity only'}
							</option>
						</select>
					</td>
				</tr>

				<tr>
					<td colspan="2">&nbsp;</td>
				</tr>

				<tr>
					<td>
						<label for="ENABLE_REPORT_DAILY">
							$Lang::tr{'ids reports daily'}
						</label>
					</td>

					<td>
						<input type='checkbox' name='ENABLE_REPORT_DAILY' id="ENABLE_REPORT_DAILY" $checked{'ENABLE_REPORT_DAILY'}{'on'}>
					</td>
				</tr>

				<tr>
					<td>
						<label for="ENABLE_REPORT_WEEKLY">
							$Lang::tr{'ids reports weekly'}
						</label>
					</td>

					<td>
						<input type='checkbox' name='ENABLE_REPORT_WEEKLY' id="ENABLE_REPORT_WEEKLY" $checked{'ENABLE_REPORT_WEEKLY'}{'on'}>
					</td>
				</tr>

				<tr>
					<td>
						<label for="ENABLE_REPORT_MONTHLY">
							$Lang::tr{'ids reports monthly'}
						</label>
					</td>

					<td>
						<input type='checkbox' name='ENABLE_REPORT_MONTHLY' id="ENABLE_REPORT_MONTHLY" $checked{'ENABLE_REPORT_MONTHLY'}{'on'}>
					</td>
				</tr>

				<tr class="action">
					<td colspan="2">
						<input type='submit' name='IDS' value='$Lang::tr{'save'}' />
					</td>
				</tr>
			</table>
		</form>
END
;

	}

	&Header::closesection();

	# Throughput Graph
	if (-e "/var/log/rrd/collectd/localhost/iptables-mangle-IPS/ipt_bytes-BYPASSED.rrd"
			&& -e "/var/log/rrd/collectd/localhost/iptables-mangle-IPS/ipt_bytes-SCANNED.rrd"
			&& -e "/var/log/rrd/collectd/localhost/iptables-mangle-IPS/ipt_bytes-WHITELISTED.rrd") {
		&Header::graph("$Lang::tr{'ips throughput'}", "ids.cgi", "ips-throughput", "day");
	}

	#
	# Used Ruleset Providers section.
	#
	&Header::openbox('100%', 'center', $Lang::tr{'ids rulesets'});

print <<END;
	<table width='100%' border='0' class='tbl'>
		<tr>
			<th>$Lang::tr{'ids provider'}</td>
			<th>$Lang::tr{'last updated'}</td>
			<th align='center'>$Lang::tr{'ids autoupdates'}</td>
			<th align='center' colspan='3'>$Lang::tr{'action'}</td>
		</tr>
END
		my $line = 1;

		# Check if some providers has been configured.
		if (keys (%used_providers)) {
			my $col = "";

			# Loop through all entries of the hash.
			foreach my $id (sort keys(%used_providers)) {
				# Assign data array positions to some nice variable names.
				my $provider = $used_providers{$id}[0];
				my $provider_name = &get_provider_name($provider);
				my $rulesetdate = &IDS::get_ruleset_date($provider);

				my $subscription_code = $used_providers{$id}[1];
				my $autoupdate_status = $used_providers{$id}[2];
				my $status  = $used_providers{$id}[3];
				my $unsupported;

				# Handle providers which are not longer supported.
				unless ($IDS::Ruleset::Providers{$provider}{'dl_url'}) {
					$col = "bgcolor='$Header::colouryellow'";
					$unsupported = $Lang::tr{'ids provider eol'};
				}

				# Choose icons for the checkboxes.
				my $status_gif;
				my $status_gdesc;
				my $autoupdate_status_gif;
				my $autoupdate_status_gdesc;

				# Check if the status is enabled and select the correct image and description.
				if ($status eq 'enabled' ) {
					$status_gif = 'on.gif';
					$status_gdesc = $Lang::tr{'click to disable'};
				} else {
					$status_gif = 'off.gif';
					$status_gdesc = $Lang::tr{'click to enable'};
				}

				# Check if the autoupdate status is enabled and select the correct image and description.
				if ($autoupdate_status eq 'enabled') {
					$autoupdate_status_gif = 'on.gif';
					$autoupdate_status_gdesc = $Lang::tr{'click to disable'};
				} else {
					$autoupdate_status_gif = 'off.gif';
					$autoupdate_status_gdesc = $Lang::tr{'click to enable'};
				}

print <<END;
				<tr>
					<th scope='row' width='33%' $col>$provider_name $unsupported</th>
					<td width='30%' $col align='center'>$rulesetdate</td>

					<td align='center' $col>
						<form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='AUTOUPDATE' value='$Lang::tr{'toggle enable disable'}' />
							<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$autoupdate_status_gif' alt='$autoupdate_status_gdesc' title='$autoupdate_status_gdesc' />
							<input type='hidden' name='ID' value='$id' />
						</form>
					</td>

					<td align='center' $col>
						<form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='PROVIDERS' value='$Lang::tr{'toggle enable disable'}'>
							<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$status_gif' alt='$status_gdesc' title='$status_gdesc'>
							<input type='hidden' name='ID' value='$id'>
						</form>
					</td>

					<td align='center' $col>
						<form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='PROVIDERS' value='$Lang::tr{'edit'}'>
							<input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}'>
							<input type='hidden' name='ID' value='$id'>
						</form>
					</td>

					<td align='center' $col>
						<form method='post' name='$provider' action='$ENV{'SCRIPT_NAME'}'>
							<input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' title='$Lang::tr{'remove'}' alt='$Lang::tr{'remove'}'>
							<input type='hidden' name='ID' value='$id'>
							<input type='hidden' name='PROVIDERS' value='$Lang::tr{'remove'}'>
						</form>
					</td>
				</tr>
END
			# Increment lines value.
			$line++;

			}

		} else {
			# Print notice that currently no hosts are ignored.
			print "<tr>\n";
			print "<td class='base' colspan='6'>$Lang::tr{'guardian no entries'}</td>\n";
			print "</tr>\n";
		}

	print "</table>\n";

	# Section to add new elements or edit existing ones.
	print <<END;
	<br>

	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<div align='right'>
END

	# Only show this button if a ruleset provider is configured.
	if (%used_providers) {
		print "<input type='submit' name='RULESET' value='$Lang::tr{'ids customize ruleset'}'>\n";
	}

print <<END;
			<input type='submit' name='PROVIDERS' value='$Lang::tr{'ids add provider'}'>
		</div>
	</form>
END

	&Header::closebox();

	#
	# Whitelist / Ignorelist
	#
	&Header::openbox('100%', 'center', $Lang::tr{'ids ignored hosts'});

	print <<END;
	<table class='tbl'>
		<tr>
			<th>$Lang::tr{'ip address'}</td>
			<th>$Lang::tr{'remark'}</td>
			<th colspan='3'></td>
		</tr>
END
		# Check if some hosts have been added to be ignored.
		if (keys (%ignored)) {
			my $col = "";

			# Loop through all entries of the hash.
			foreach my $key (sort { $ignored{$a}[0] <=> $ignored{$b}[0] } keys %ignored)  {
				# Assign data array positions to some nice variable names.
				my $address = $ignored{$key}[0];
				my $remark = $ignored{$key}[1];
				my $status  = $ignored{$key}[2];

				# Check if the key (id) number is even or not.
				if ($cgiparams{'ID'} eq $key) {
					$col="bgcolor='${Header::colouryellow}'";
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
					<td width='20%' $col>$address</td>
					<td width='65%' $col>$remark</td>

					<td align='center' $col>
						<form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='WHITELIST' value='$Lang::tr{'toggle enable disable'}'>
							<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' alt='$gdesc' title='$gdesc'>
							<input type='hidden' name='ID' value='$key'>
						</form>
					</td>

					<td align='center' $col>
						<form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='WHITELIST' value='$Lang::tr{'edit'}'>
							<input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}'>
							<input type='hidden' name='ID' value='$key'>
						</form>
					</td>

					<td align='center' $col>
						<form method='post' name='$key' action='$ENV{'SCRIPT_NAME'}'>
							<input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' title='$Lang::tr{'remove'}' alt='$Lang::tr{'remove'}'>
							<input type='hidden' name='ID' value='$key'>
							<input type='hidden' name='WHITELIST' value='$Lang::tr{'remove'}'>
						</form>
						</td>
					</tr>
END
				}
			} else {
				# Print notice that currently no hosts are ignored.
				print "<tr>\n";
				print "<td class='base' colspan='5'>$Lang::tr{'guardian no entries'}</td>\n";
				print "</tr>\n";
			}

		print "</table>\n";

		# Section to add new elements or edit existing ones.
print <<END;
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='ID' value='$cgiparams{'ID'}'>

			<table class='form'>
END

		# Assign correct headline and button text.
		my $buttontext;
		my $entry_address;
		my $entry_remark;

		# Check if an ID (key) has been given, in this case an existing entry should be edited.
		if ($cgiparams{'ID'} ne '') {
			$buttontext = $Lang::tr{'update'};
				print "<tr><td colspan='2'><h6>$Lang::tr{'update'}</h6></td></tr>\n";

				# Grab address and remark for the given key.
				$entry_address = $ignored{$cgiparams{'ID'}}[0];
				$entry_remark = $ignored{$cgiparams{'ID'}}[1];
			} else {
				$buttontext = $Lang::tr{'add'};
				print "<tr><td colspan='2'><h6>$Lang::tr{'dnsforward add a new entry'}</h6></td></tr>\n";
			}

print <<END;
				<tr>
					<td>$Lang::tr{'ip address'}</td>
					<td>
						<input type='text' name='IGNORE_ENTRY_ADDRESS' value='$entry_address' size='24' />
					</td>
				</tr>

				<tr>
					<td>$Lang::tr{'remark'}</td>
					<td>
						<input type='text' name=IGNORE_ENTRY_REMARK
							value='@{[ &Header::escape($entry_remark) ]}' size='24' />
					</td>
				</tr>

				<tr class='action'>
					<td colspan='2'><input type='submit' name='WHITELIST' value='$buttontext' /></td>
				</tr>
			</table>
		</form>
END

	&Header::closebox();
}

#
## Function to show the customize ruleset section.
#
sub show_customize_ruleset() {
	### Java Script ###
	print"<script>\n";

	# Java script variable declaration for show and hide.
	print"var show = \"$Lang::tr{'ids show'}\"\;\n";
	print"var hide = \"$Lang::tr{'ids hide'}\"\;\n";

print <<END
	// Tiny javascript function to show/hide the rules
	// of a given category.
	function showhide(tblname) {
		\$("#" + tblname).toggle();

		// Get current content of the span element.
		var content = document.getElementById("span_" + tblname);

		if (content.innerHTML === show) {
			content.innerHTML = hide;
		} else {
			content.innerHTML = show;
		}
	}
	</script>
END
;
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'intrusion detection system rules'}" );
	print"<form method='POST' action='$ENV{'SCRIPT_NAME'}'>\n";

	# Output display table for rule files
	print "<table width='100%'>\n";

	# Loop over each rule file
	foreach my $rulefile (sort keys(%idsrules)) {
		my $rulechecked = '';

		# Check if rule file is enabled
		if ($idsrules{$rulefile}{'Rulefile'}{'State'} eq 'on') {
			$rulechecked = 'CHECKED';
		}

		# Convert rulefile name into category name.
		my $categoryname = &_rulefile_to_category($rulefile);

		# Table and rows for the rule files.
		print"<tr>\n";
		print"<td class='base' width='5%'>\n";
		print"<input type='checkbox' name='$rulefile' $rulechecked>\n";
		print"</td>\n";
		print"<td class='base' width='90%'><b>$rulefile</b></td>\n";
		print"<td class='base' width='5%' align='right'>\n";
		print"<a href=\"javascript:showhide('$categoryname')\"><span id='span_$categoryname'>$Lang::tr{'ids show'}</span></a>\n";
		print"</td>\n";
		print"</tr>\n";

		# Rows which will be hidden per default and will contain the single rules.
		print"<tr  style='display:none' id='$categoryname'>\n";
		print"<td colspan='3'>\n";

		# Local vars
		my $lines;
		my $rows;
		my $col;

		# New table for the single rules.
		print "<table width='100%'>\n";

		# Loop over rule file rules
		foreach my $sid (sort {$a <=> $b} keys(%{$idsrules{$rulefile}})) {
			# Local vars
			my $ruledefchecked = '';

			# Skip rulefile itself.
			next if ($sid eq "Rulefile");

			# If 2 rules have been displayed, start a new row
			if (($lines % 2) == 0) {
				print "</tr><tr>\n";

				# Increase rows by once.
				$rows++;
			}

			# Colour lines.
			if ($rows % 2) {
				$col="bgcolor='$color{'color20'}'";
			} else {
				$col="bgcolor='$color{'color22'}'";
			}

			# Set rule state
			if ($idsrules{$rulefile}{$sid}{'State'} eq 'on') {
				$ruledefchecked = 'CHECKED';
			}

			# Create rule checkbox and display rule description
			print "<td class='base' width='5%' align='right' $col>\n";
			print "<input type='checkbox' NAME='$sid' $ruledefchecked>\n";
			print "</td>\n";
			print "<td class='base' width='45%' $col>$idsrules{$rulefile}{$sid}{'Description'}</td>";

			# Increment rule count
			$lines++;
		}

		# If do not have a second rule for row, create empty cell
		if (($lines % 2) != 0) {
			print "<td class='base'></td>";
		}

		# Close display table
		print "</tr></table></td></tr>";
	}

	# Close display table
	print "</table>";

	print <<END
<table width='100%'>
<tr>
	<td width='100%' align='right'>
		<input type='submit' value='$Lang::tr{'fwhost back'}'>
		<input type='submit' name='RULESET' value='$Lang::tr{'ids apply'}'>
	</td>
</tr>
</table>
</form>
END
;
	&Header::closebox();
}

#
## Function to show section for add/edit a provider.
#
sub show_add_provider() {
	my %used_providers = ();
	my @subscription_providers;

	# Read -in providers settings file.
	&General::readhasharray("$IDS::providers_settings_file", \%used_providers);

	# Get all supported ruleset providers.
	my @ruleset_providers = &IDS::get_ruleset_providers();

	### Java Script ###
	print "<script>\n";

	# Generate Java Script Object which contains the URL of the providers.
	print "\t// Object, which contains the webpages of the ruleset providers.\n";
	print "\tvar url = {\n";

	# Loop through the array of supported providers.
	foreach my $provider (@ruleset_providers) {
		# Check if the provider requires a subscription.
		if ($IDS::Ruleset::Providers{$provider}{'requires_subscription'} eq "True") {
			# Add the provider to the array of subscription_providers.
			push(@subscription_providers, $provider);
		}

		# Grab the URL for the provider.
		my $url = $IDS::Ruleset::Providers{$provider}{'website'};

		# Print the URL to the Java Script Object.
		print "\t\t$provider: \"$url\"\,\n";
	}

	# Close the Java Script Object declaration.
	print "\t}\;\n\n";

	# Generate Java Script Array which contains the provider that requires a subscription.
	my $line = "";
	$line = join("', '", @subscription_providers);

	print "\t// Array which contains the providers that requires a subscription.\n";
	print "\tsubscription_provider = ['$line']\;\n\n";

print <<END
	// Java Script function to swap the text input field for
	// entering a subscription code.
	var update_provider = function() {
		if(inArray(\$('#PROVIDER').val(), subscription_provider)) {
			\$('.subscription_code').show();
		} else {
			\$('.subscription_code').hide();
		}

		// Call function to change the website url.
		change_url(\$('#PROVIDER').val());
	};

	// Java Script function to check if a given value is part of
	// an array.
	function inArray(value,array) {
		var count=array.length;

		for(var i=0;i<count;i++) {
			if(array[i]===value){
				return true;
			}
		}

		return false;
	}

	// Tiny function to change the website url based on the selected element in the "PROVIDERS"
	// dropdown menu.
	function change_url(provider) {
		// Get and change the href to the corresponding url.
		document.getElementById("website").href = url[provider];
	}

	// JQuery function to call corresponding function when
	// the ruleset provider is changed or the page is loaded for showing/hiding
	// the subscription_code area.
	\$(document).ready(function() {
		\$('#PROVIDER').change(update_provider);
			update_provider();
	});

	</script>
END
;

	# Check if an existing provider should be edited.
	if($cgiparams{'PROVIDERS'} eq "$Lang::tr{'edit'}") {
		# Check if autoupdate is enabled for this provider.
		if ($used_providers{$cgiparams{'ID'}}[2] eq "enabled") {
			# Set the checkbox to be checked.
			$checked{'ENABLE_AUTOUPDATE'} = "checked='checked'";
		}

		# Check if the monitor traffic only mode is set for this provider.
		if ($used_providers{$cgiparams{'ID'}}[4] eq "IDS") {
			# Set the checkbox to be checked.
			$checked{'MONITOR_TRAFFIC_ONLY'} = "checked='checked'";
		}

		# Display section to force an rules update and to reset the provider.
		&show_additional_provider_actions();

	} elsif ($cgiparams{'PROVIDERS'} eq "$Lang::tr{'ids add provider'}") {
		# Set the autoupdate to true as default.
		$checked{'ENABLE_AUTOUPDATE'} = "checked='checked'";
	}

	&Header::openbox('100%', 'center', $Lang::tr{'ids provider settings'});

print <<END
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='100%' border='0'>
			<tr>
				<td colspan='2'><b>$Lang::tr{'ids provider'}</b></td>
			</tr>

			<tr>
				<td width='40%'>
					<input type='hidden' name='ID' value='$cgiparams{'ID'}'>
END
;
					# Value to allow disabling the dropdown menu.
					my $disabled;

					# Check if we are in edit mode.
					if ($cgiparams{'PROVIDERS'} eq "$Lang::tr{'edit'}") {
						$disabled = "disabled";

						# Add hidden input with the provider because the disable select does not provider
						# this.
						print "<input type='hidden' name='PROVIDER' value='$used_providers{$cgiparams{'ID'}}[0]'>\n";
					}

					print "<select name='PROVIDER' id='PROVIDER' $disabled>\n";
						# Temporary hash to store the provier names and their handles.
						my %tmphash = ();

						# Loop through the array of ruleset providers.
						foreach my $handle (@ruleset_providers) {
							# Get the provider name.
							my $name = &get_provider_name($handle);

							# Add the grabbed provider  name and handle to the
							# temporary hash.
							$tmphash{$name} = "$handle";
						}

						# Sort and loop through the temporary hash.
						foreach my $provider_name ( sort keys %tmphash ) {
							# Grab the provider handle.
							my $provider = $tmphash{$provider_name};

							# Check if we are not in edit mode.
							if ($cgiparams{'PROVIDERS'} ne "$Lang::tr{'edit'}") {
								# Skip unsupported ruleset provider.
								next unless(exists($IDS::Ruleset::Providers{$provider}{"dl_url"}));
							}

							# Pre-select the provider if one is given.
							if (($used_providers{$cgiparams{'ID'}}[0] eq "$provider") || ($cgiparams{'PROVIDER'} eq "$provider")) {
								$selected{$provider} = "selected='selected'";
							}

							# Add the provider to the dropdown menu.
							print "<option value='$provider' $selected{$provider}>$provider_name</option>\n";
						}
print <<END
					</select>
				</td>

				<td width='60%'>
					<b><a id="website" target="_blank" href="#">$Lang::tr{'ids visit provider website'}</a></b>
				</td>
			</tr>

			<tr>
				<td colspan='2'><br><br></td>
			</tr>

			<tr class='subscription_code' style='display:none' id='subscription_code'>
				<td colspan='2'>
					<table border='0'>
						<tr>
							<td>
								<b>$Lang::tr{'subscription code'}</b>
							</td>
						</tr>

						<tr>
							<td>
								<input type='text' size='40' name='SUBSCRIPTION_CODE' value='$used_providers{$cgiparams{'ID'}}[1]'>
							</td>
						</tr>

						<tr>
							<td><br><br></td>
						</tr>
					</table>
				</td>
			</tr>

			<tr>
				<td>
					<input type='checkbox' name='ENABLE_AUTOUPDATE' $checked{'ENABLE_AUTOUPDATE'}>&nbsp;$Lang::tr{'ids enable automatic updates'}
				</td>

				<td>
					<input type='checkbox' name='MONITOR_TRAFFIC_ONLY' $checked{'MONITOR_TRAFFIC_ONLY'}>&nbsp;$Lang::tr{'ids monitor traffic only'}
				</td>
			</tr>

			<tr>
				<td colspan='2' align='right'>
					<input type='submit' value='$Lang::tr{'back'}'>
END
;
				# Check if a provider should be added or edited.
				if ($cgiparams{'PROVIDERS'} eq "$Lang::tr{'edit'}") {
					# Display button for updating the existing provider.
					print "<input type='submit' name='PROVIDERS' value='$Lang::tr{'update'}'>\n";
				} else {
					# Display button to add the new provider.
					print "<input type='submit' name='PROVIDERS' value='$Lang::tr{'add'}'>\n";
				}
print <<END
				</td>
			</tr>
		</table>
	</form>
END
;
	&Header::closebox();
}

#
## Function to show the area where additional provider actions can be done.
#
sub show_additional_provider_actions() {
	my $disabled_reset;
	my $disabled_update;
	my %used_providers = ();

	# Read-in providers settings file.
	&General::readhasharray("$IDS::providers_settings_file", \%used_providers);

	# Assign variable for provider handle.
	my $provider = "$used_providers{$cgiparams{'ID'}}[0]";

	# Call function to get the path and name for the given provider
	# ruleset modifications file.
	my $modifications_file = &IDS::get_provider_ruleset_modifications_file($provider);

	# Disable the reset provider button if no provider modified sids file exists.
	unless (-f $modifications_file) {
		$disabled_reset = "disabled";
	}

	# Disable the manual update button if the provider is not longer supported.
	unless ($IDS::Ruleset::Providers{$provider}{"dl_url"}) {
		$disabled_update = "disabled";
	}

	&Header::openbox('100%', 'center', "");
	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<table width='100%' border="0">
				<tr>
					<td align='center'>
						<input type='hidden' name='PROVIDER' value='$provider'>
						<input type='submit' name='PROVIDERS' value='$Lang::tr{'ids reset provider'}' $disabled_reset>
						<input type='submit' name='PROVIDERS' value='$Lang::tr{'ids force ruleset update'}' $disabled_update>
					</td>
				</tr>
			</table>
		</form>
END
;
	&Header::closebox();
}

#
## A function to display a notice, to lock the webpage and
## tell the user which action currently will be performed.
#
sub working_notice ($) {
	my ($message) = @_;

	&_open_working_notice ($message);
	&_close_working_notice();
}

#
## Private function to lock the page and tell the user what is going on.
#
sub _open_working_notice ($) {
	my ($message) = @_;

	&Header::openpage($Lang::tr{'intrusion detection system'}, 1, '');
	&Header::openbigbox('100%', 'left', '', $errormessage);
	&Header::openbox( 'Waiting', 1,);
		print <<END;
			<table>
				<tr>
					<td><img src='/images/indicator.gif' alt='$Lang::tr{'aktiv'}' /></td>
					<td>$message</td>
				</tr>
END
}

#
## Private function to close a working notice.
#
sub _close_working_notice () {
	print "</table>\n";

	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
}

#
## Function which locks the webpage and basically does the same as the
## oinkmaster function, but provides a lot of HTML formated status output.
#
sub oinkmaster_web () {
	my ($nolock) = @_;

	my @enabled_providers = &IDS::get_enabled_providers();

	# Lock the webpage and print message.
	unless ($nolock) {
		&_open_working_notice("$Lang::tr{'ids apply ruleset changes'}");
	}

        # Check if the files in rulesdir have the correct permissions.
        &IDS::_check_rulesdir_permissions();

	print "<tr><td><br><br></td></tr>\n";

        # Cleanup the rules directory before filling it with the new rulests.
        &_add_to_notice("$Lang::tr{'ids remove rule structures'}");
        &IDS::_cleanup_rulesdir();

        # Loop through the array of enabled providers.
        foreach my $provider (@enabled_providers) {
                &_add_to_notice("$Lang::tr{'ids extract ruleset'} $provider");
                # Call the extractruleset function.
                &IDS::extractruleset($provider);
        }

        # Call function to process the ruleset and do all modifications.
        &_add_to_notice("$Lang::tr{'ids adjust ruleset'}");
        &IDS::process_ruleset(@enabled_providers);

        # Call function to merge the classification files.
        &_add_to_notice("$Lang::tr{'ids merge classifications'}");
        &IDS::merge_classifications(@enabled_providers);

        # Call function to merge the sid to message mapping files.
        &_add_to_notice("$Lang::tr{'ids merge sid files'}");
        &IDS::merge_sid_msg(@enabled_providers);

        # Cleanup temporary directory.
        &_add_to_notice("$Lang::tr{'ids cleanup tmp dir'}");
        &IDS::cleanup_tmp_directory();

	# Finished - print a notice.
        &_add_to_notice("$Lang::tr{'ids finished'}");

	# Close the working notice.
	unless ($nolock) {
		&_close_working_notice();
	}
}

#
## Tiny private function to add a given message to a notice table.
#
sub _add_to_notice ($) {
	my ($message) = @_;

	print "<tr><td colspan='2'><li><b>$message</b></li></td></tr>\n";
}

#
## A tiny function to perform a reload of the webpage after one second.
#
sub reload () {
	print "<meta http-equiv='refresh' content='1'>\n";

	# Stop the script.
	exit;
}

#
## Private function to read-in and parse rules of a given rulefile.
#
## The given file will be read, parsed and all valid rules will be stored by ID,
## message/description and it's state in the idsrules hash.
#
sub readrulesfile ($) {
	my $rulefile = shift;

	# Open rule file and read in contents
	open(RULEFILE, "$IDS::rulespath/$rulefile") or die "Unable to read $rulefile!";

	# Store file content in an array.
	my @lines = <RULEFILE>;

	# Close file.
	close(RULEFILE);

	# Loop over rule file contents
	foreach my $line (@lines) {
		# Remove whitespaces.
		chomp $line;

		# Skip blank  lines.
		next if ($line =~ /^\s*$/);

		# Local vars.
		my $sid;
		my $msg;

		# Gather rule sid and message from the ruleline.
		if ($line =~ m/.*msg:\s*\"(.*?)\"\;.*sid:\s*(.*?); /) {
			$msg = $1;
			$sid = $2;

			# Check if a rule has been found.
			if ($sid && $msg) {
				# Add rule to the idsrules hash.
				$idsrules{$rulefile}{$sid}{'Description'} = $msg;

				# Grab status of the rule. Check if ruleline starts with a "dash".
				if ($line =~ /^\#/) {
					# If yes, the rule is disabled.
					$idsrules{$rulefile}{$sid}{'State'} = "off";
				} else {
					# Otherwise the rule is enabled.
					$idsrules{$rulefile}{$sid}{'State'} = "on";
				}
			}
		}
	}
}

#
## Function to get the provider handle by a given ID.
#
sub get_provider_handle($) {
	my ($id) = @_;

	my %used_providers = ();

	# Read-in provider settings file.
	&General::readhasharray($IDS::providers_settings_file, \%used_providers);

	# Obtain the provider handle for the given ID.
	my $provider_handle = $used_providers{$cgiparams{'ID'}}[0];

	# Return the handle.
	return $provider_handle;
}

#
## Function to get the provider name from the language file or providers file for a given handle.
#
sub get_provider_name($) {
	my ($handle) = @_;
	my $provider_name;

	# Early exit if the given provider does not longer exist.
	return unless ($IDS::Ruleset::Providers{$handle});

	# Get the required translation string for the given provider handle.
	my $tr_string = $IDS::Ruleset::Providers{$handle}{'tr_string'};

	# Check if the translation string is available in the language files.
	if ($Lang::tr{$tr_string}) {
		# Use the translated string from the language file.
		$provider_name = $Lang::tr{$tr_string};
	} else {
		# Fallback and use the provider summary from the providers file.
		$provider_name = $IDS::Ruleset::Providers{$handle}{'summary'};
	}

	# Return the obtained provider name.
	return $provider_name;
}

#
## Function to remove a provider by a given ID.
#
sub remove_provider($) {
	my ($id) = @_;

	my %used_providers = ();

	# Read-in provider settings file.
	&General::readhasharray($IDS::providers_settings_file, \%used_providers);

	# Drop entry from the hash.
	delete($used_providers{$id});

	# Write the changed hash to the provider settings file.
	&General::writehasharray($IDS::providers_settings_file, \%used_providers);
}

#
## Private function to convert a given rulefile to a category name.
## ( No file extension anymore and if the name contained a dot, it
## would be replaced by a underline sign.)
#
sub _rulefile_to_category($) {
        my ($filename) = @_;

	# Splitt the filename into single chunks and store them in a
	# temorary array.
        my @parts = split(/\./, $filename);

	# Return / Remove last element of the temporary array.
	# This removes the file extension.
        pop @parts;

	# Join together the single elements of the temporary array.
	# If these are more than one, use a "underline" for joining.
        my $category = join '_', @parts;

	# Return the converted filename.
        return $category;
}

#
## Private function to validate if a given string contains one or
## more valid mail addresses.
#
sub _validate_mail_address($) {
	my ($address) = @_;

	# Temporary array, which holds the single mail addresses.
	my @temp;

	# Split the string of mail addresses into single pieces and
	# store them into the temporary array.
	@temp = split(/\,/, $address);

	# Loop through the array of mail addresses.
	foreach my $addr (@temp) {
		# If the address contains a '@' with at least one character before and after,
		# we consider it valid.
		return 1 unless ($address =~ m/.@./);
	}

	# Return nothing if the address is valid.
	return;
}
