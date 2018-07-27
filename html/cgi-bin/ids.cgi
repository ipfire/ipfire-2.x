#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2018  IPFire Team  <info@ipfire.org>                     #
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
require "${General::swroot}/ids-functions.pl";

my %color = ();
my %mainsettings = ();
my %netsettings = ();
my %idsrules = ();
my %snortsettings=();
my %rulesetsources = ();
my %cgiparams=();
my %checked=();
my %selected=();

# Read-in main settings, for language, theme and colors.
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

# Get netsettings.
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

my $idsusedrulefilesfile = "$IDS::settingsdir/ids-used-rulefiles.conf";
my $errormessage;

&Header::showhttpheaders();

# Default settings for snort.
$snortsettings{'ENABLE_SNORT'} = 'off';
$snortsettings{'ENABLE_SNORT_GREEN'} = 'off';
$snortsettings{'ENABLE_SNORT_BLUE'} = 'off';
$snortsettings{'ENABLE_SNORT_ORANGE'} = 'off';
$snortsettings{'RULES'} = '';
$snortsettings{'OINKCODE'} = '';

#Get GUI values
&Header::getcgihash(\%cgiparams);

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


## Grab all available snort rules and store them in the idsrules hash.
#
# Open snort rules directory and do a directory listing.
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

		# Call subfunction to read-in rulefile and add rules to
		# the idsrules hash.
		&readrulesfile("$file");
	}

closedir(DIR);

# Gather used rulefiles.
#
# Check if the file for activated rulefiles is not empty.
if(-f $idsusedrulefilesfile) {
	# Open the file for used rulefile and read-in content.
	open(FILE, $idsusedrulefilesfile) or die "Could not open $idsusedrulefilesfile. $!\n";

	# Read-in content.
	my @lines = <FILE>;

	# Close file.
	close(FILE);

	# Loop through the array.
	foreach my $line (@lines) {
		# Remove newlines.
		chomp($line);

		# Skip comments.
		next if ($line =~ /\#/);

		# Skip blank  lines.
		next if ($line =~ /^\s*$/);

		# Gather rule sid and message from the ruleline.
		if ($line =~ /.*include \$RULE_PATH\/(.*)/) {
			my $rulefile = $1;

			# Add the rulefile to the %idsrules hash.
			$idsrules{$rulefile}{'Rulefile'}{'State'} = "on";
		}
	}
}

# Save ruleset.
if ($cgiparams{'RULESET'} eq $Lang::tr{'update'}) {
	my $enabled_sids_file = "$IDS::settingsdir/oinkmaster-enabled-sids.conf";
	my $disabled_sids_file = "$IDS::settingsdir/oinkmaster-disabled-sids.conf";

	# Arrays to store sid which should be added to the corresponding files.
	my @enabled_sids;
	my @disabled_sids;
	my @enabled_rulefiles;

	# Loop through the hash of idsrules.
	foreach my $rulefile(keys %idsrules) {
		# Check if the rulefile is enabled.
		if ($cgiparams{$rulefile} eq "on") {
			# Add rulefile to the array of enabled rulefiles.
			push(@enabled_rulefiles, $rulefile);

			# Drop item from cgiparams hash.
			delete $cgiparams{$rulefile};
		}
	}

	# Loop through the hash of idsrules.
	foreach my $rulefile (keys %idsrules) {
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
						# Add the sid to the enabled_sids array.
						push(@enabled_sids, $sid);

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
					# Add it to the disabled_sids array.
					push(@disabled_sids, $sid);

					# Drop item from cgiparams hash.
					delete $cgiparams{$rulefile}{$sid};
				}
			}
		}
	}

	# Open enabled sid's file for writing.
	open(FILE, ">$enabled_sids_file") or die "Could not write to $enabled_sids_file. $!\n";

	# Write header to file.
	print FILE "#Autogenerated file. Any custom changes will be overwritten!\n";

	# Check if the enabled_sids array contains any sid's.
	if (@enabled_sids) {
		# Loop through the array of enabled sids and write them to the file.
		foreach my $sid (@enabled_sids) {
			print FILE "enablesid $sid\n";
		}
	}

	# Close file after writing.
	close(FILE);

	# Open disabled sid's file for writing.
	open(FILE, ">$disabled_sids_file") or die "Could not write to $disabled_sids_file. $!\n";

	# Write header to file.
	print FILE "#Autogenerated file. Any custom changes will be overwritten!\n";

	# Check if the enabled_sids array contains any sid's.
        if (@disabled_sids) {
		# Loop through the array of disabled sids and write them to the file.
		foreach my $sid (@disabled_sids) {
			print FILE "disablesid $sid\n";
		}
	}

	# Close file after writing.
	close(FILE);

	# Open file for used rulefiles.
	open (FILE, ">$idsusedrulefilesfile") or die "Could not write to $idsusedrulefilesfile. $!\n";

	# Write header to file.
	print FILE "#Autogenerated file. Any custom changes will be overwritten!\n";

	# Check if the enabled_rulefiles array contains any entries.
	if (@enabled_rulefiles) {
		# Loop through the array of rulefiles which should be loaded and write the to the file.
		foreach my $file (@enabled_rulefiles) {
			print FILE "include \$RULE_PATH/$file\n";
		}
	}

	# Close file after writing.
	close(FILE);

	# Lock the webpage and print message.
	&working_notice("$Lang::tr{'snort working'}");

	# Call oinkmaster to alter the ruleset.
	&IDS::oinkmaster();

	# Reload page.
	&reload();

# Download new ruleset.
} elsif ($cgiparams{'RULESET'} eq $Lang::tr{'download new ruleset'}) {
	# Check if the red device is active.
	unless (-e "${General::swroot}/red/active") {
		$errormessage = $Lang::tr{'could not download latest updates'};
	}

	# Check if enought free disk space is availabe.
	$errormessage = &IDS::checkdiskspace();

	# Check if any errors happend.
	unless ($errormessage) {
		# Lock the webpage and print notice about downloading
		# a new ruleset.
		&working_notice("$Lang::tr{'snort working'}");

		# Call subfunction to download the ruleset.
		$errormessage = &IDS::downloadruleset();

		# Check if the downloader returned an error.
		if ($errormessage) {
			# Call function to store the errormessage.
			&IDS::log_error($errormessage);

			# Preform a reload of the page.
			&reload();
		} else {
			# Call subfunction to launch oinkmaster.
			&IDS::oinkmaster();

			# Perform a reload of the page.
			&reload();
		}
	}
# Save snort settings.
} elsif ($cgiparams{'SNORT'} eq $Lang::tr{'save'}) {
	# Prevent form name from been stored in conf file.
	delete $cgiparams{'SNORT'};

	# Check if an oinkcode has been provided.
	if ($cgiparams{'OINKCODE'}) {
		# Check if the oinkcode contains unallowed chars.
		unless ($cgiparams{'OINKCODE'} =~ /^[a-z0-9]+$/) {
			$errormessage = $Lang::tr{'invalid input for oink code'};
		}
	}

	# Go on if there are no error messages.
	if (!$errormessage) {
		# Store settings into settings file.
		&General::writehash("$IDS::settingsdir/settings", \%cgiparams);

		# Call snortctrl to restart snort
		system('/usr/local/bin/snortctrl restart >/dev/null');
	}
}

# Read-in snortsettings
&General::readhash("$IDS::settingsdir/settings", \%snortsettings);

$checked{'ENABLE_SNORT'}{'off'} = '';
$checked{'ENABLE_SNORT'}{'on'} = '';
$checked{'ENABLE_SNORT'}{$snortsettings{'ENABLE_SNORT'}} = "checked='checked'";
$checked{'ENABLE_SNORT_GREEN'}{'off'} = '';
$checked{'ENABLE_SNORT_GREEN'}{'on'} = '';
$checked{'ENABLE_SNORT_GREEN'}{$snortsettings{'ENABLE_SNORT_GREEN'}} = "checked='checked'";
$checked{'ENABLE_SNORT_BLUE'}{'off'} = '';
$checked{'ENABLE_SNORT_BLUE'}{'on'} = '';
$checked{'ENABLE_SNORT_BLUE'}{$snortsettings{'ENABLE_SNORT_BLUE'}} = "checked='checked'";
$checked{'ENABLE_SNORT_ORANGE'}{'off'} = '';
$checked{'ENABLE_SNORT_ORANGE'}{'on'} = '';
$checked{'ENABLE_SNORT_ORANGE'}{$snortsettings{'ENABLE_SNORT_ORANGE'}} = "checked='checked'";
$selected{'RULES'}{'nothing'} = '';
$selected{'RULES'}{'community'} = '';
$selected{'RULES'}{'emerging'} = '';
$selected{'RULES'}{'registered'} = '';
$selected{'RULES'}{'subscripted'} = '';
$selected{'RULES'}{$snortsettings{'RULES'}} = "selected='selected'";

&Header::openpage($Lang::tr{'intrusion detection system'}, 1, '');

### Java Script ###
print <<END
<script>
	// Tiny java script function to show/hide the rules
	// of a given category.
	function showhide(tblname) {
		\$("#" + tblname).toggle();
	}
</script>
END
;

&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
}

&Header::openbox('100%', 'left', $Lang::tr{'intrusion detection system'});

my $rulesdate;

# Check if a ruleset allready has been downloaded.
if ( -f "$IDS::rulestarball"){
	# Call stat on the filename to obtain detailed information.
        my @Info = stat("$IDS::rulestarball");

	# Grab details about the creation time.
        $rulesdate = localtime($Info[9]);
}

print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='100%' border='0'>
		<tr>
			<td class='base' width='25%'>
				<input type='checkbox' name='ENABLE_SNORT' $checked{'ENABLE_SNORT'}{'on'}>RED Snort
			</td>

			<td class='base' width='25%'>
				<input type='checkbox' name='ENABLE_SNORT_GREEN' $checked{'ENABLE_SNORT_GREEN'}{'on'}>GREEN Snort
			</td>

			<td class='base' width='25%'>
END
;

# Check if a blue device is configured.
if ($netsettings{'BLUE_DEV'}) {
  print "<input type='checkbox' name='ENABLE_SNORT_BLUE' $checked{'ENABLE_SNORT_BLUE'}{'on'} />BLUE Snort\n";
}

print "</td>\n";

print "<td width='25%'>\n";

# Check if an orange device is configured.
if ($netsettings{'ORANGE_DEV'}) {
  print "<input type='checkbox' name='ENABLE_SNORT_ORANGE' $checked{'ENABLE_SNORT_ORANGE'}{'on'} />ORANGE Snort\n";
}

print <<END
			</td>
		</tr>

		<tr>
			<td colspan='4'><br><br></td>
		</tr>

		<tr>
			<td colspan='4'><b>$Lang::tr{'ids rules update'}</b></td>
		</tr>

		<tr>
			<td colspan='4'><select name='RULES'>
				<option value='nothing' $selected{'RULES'}{'nothing'} >$Lang::tr{'no'}</option>
				<option value='emerging' $selected{'RULES'}{'emerging'} >$Lang::tr{'emerging rules'}</option>
				<option value='community' $selected{'RULES'}{'community'} >$Lang::tr{'community rules'}</option>
				<option value='registered' $selected{'RULES'}{'registered'} >$Lang::tr{'registered user rules'}</option>
				<option value='subscripted' $selected{'RULES'}{'subscripted'} >$Lang::tr{'subscripted user rules'}</option>
			</select>
			</td>
		</tr>

		<tr>
			<td colspan='4'>
				<br>$Lang::tr{'ids rules license'} <a href='https://www.snort.org/subscribe' target='_blank'>www.snort.org</a>$Lang::tr{'ids rules license1'}</br>
				<br>$Lang::tr{'ids rules license2'} <a href='https://www.snort.org/account/oinkcode' target='_blank'>Get an Oinkcode</a>, $Lang::tr{'ids rules license3'}</br>
			</td>
		</tr>

		<tr>
			<td colspan='4' nowrap='nowrap'>Oinkcode:&nbsp;<input type='text' size='40' name='OINKCODE' value='$snortsettings{'OINKCODE'}'></td>
		</tr>

		<tr>
			<td colspan='4' align='left'><br>
				<input type='submit' name='RULESET' value='$Lang::tr{'download new ruleset'}'>&nbsp;$Lang::tr{'updates installed'}: $rulesdate
			</td>

		</tr>
	</table>

	<br><br>

	<table width='100%'>
		<tr>
			<td align='right'><input type='submit' name='SNORT' value='$Lang::tr{'save'}' /></td>
		</tr>
	</table>
</form>
END
;

&Header::closebox();

&Header::openbox('100%', 'LEFT', $Lang::tr{'intrusion detection system rules'});
	print"<form method='POST' action='$ENV{'SCRIPT_NAME'}'>\n";

	# Output display table for rule files
	print "<table width='100%'>\n";

	# Local variable required for java script to show/hide
	# rules of a rulefile.
	my $rulesetcount = 1;

	# Loop over each rule file
	foreach my $rulefile (sort keys(%idsrules)) {
		my $rulechecked = '';

		# Check if rule file is enabled
		if ($idsrules{$rulefile}{'Rulefile'}{'State'} eq 'on') {
			$rulechecked = 'CHECKED';
		}

		# Table and rows for the rule files.
		print"<tr>\n";
		print"<td class='base' width='5%'>\n";
		print"<input type='checkbox' name='$rulefile' $rulechecked>\n";
		print"</td>\n";
		print"<td class='base' width='90%'><b>$rulefile</b></td>\n";
		print"<td class='base' width='5%' align='right'>\n";
		print"<a href=\"javascript:showhide('ruleset$rulesetcount')\">SHOW</a>\n";
		print"</td>\n";
		print"</tr>\n";

		# Rows which will be hidden per default and will contain the single rules.
		print"<tr  style='display:none' id='ruleset$rulesetcount'>\n";
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

		# Finished whith the rule file, increase count.
		$rulesetcount++;
	}

	# Close display table
	print "</table>";

print <<END
<table width='100%'>
<tr>
	<td width='100%' align='right'><input type='submit' name='RULESET' value='$Lang::tr{'update'}'>
		&nbsp; <!-- space for future online help link -->
	</td>
</tr>
</table>
</form>
END
;
&Header::closebox();
&Header::closebigbox();
&Header::closepage();

#
## A function to display a notice, to lock the webpage and
## tell the user which action currently will be performed.
#
sub working_notice ($) {
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
			</table>
END
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
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
		if ($line =~ m/.*msg:\"(.*?)\"\; .* sid:(.*?); /) {
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
