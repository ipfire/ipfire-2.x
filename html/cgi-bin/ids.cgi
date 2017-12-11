#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2015  IPFire Team  <info@ipfire.org>                     #
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
use File::Copy;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

my %snortsettings=();
my %cgiparams=();
my %checked=();
my %selected=();
my %netsettings=();
our $errormessage = '';
our $results = '';
our $tempdir = '';
our $url='';
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

&Header::showhttpheaders();

$snortsettings{'ENABLE_SNORT'} = 'off';
$snortsettings{'ENABLE_SNORT_GREEN'} = 'off';
$snortsettings{'ENABLE_SNORT_BLUE'} = 'off';
$snortsettings{'ENABLE_SNORT_ORANGE'} = 'off';
$snortsettings{'ACTION'} = '';
$snortsettings{'RULES'} = '';
$snortsettings{'OINKCODE'} = '';
$snortsettings{'INSTALLDATE'} = '';
$snortsettings{'FILE'} = '';

#Get GUI values
&Header::getcgihash(\%cgiparams);

my $snortrulepath = "/etc/snort/rules";
my $restartsnortrequired = 0;
my %snortrules;
my $rule = '';
my $table1colour = '';
my $table2colour = '';
my $var = '';
my $value = '';
my $tmp = '';
my $linkedrulefile = '';
my $border = '';
my $checkboxname = '';

## Grab all available snort rules and store them in the snortrules hash.
#
# Open snort rules directory and do a directory listing.
opendir(DIR, $snortrulepath) or die $!;
	# Loop through the direcory.
	while (my $file = readdir(DIR)) {

		# We only want files.
		next unless (-f "$snortrulepath/$file");

		# Ignore empty files.
		next if (-z "$snortrulepath/$file");

		# Use a regular expression to find files ending in .rules
		next unless ($file =~ m/\.rules$/);

		# Ignore files which are not read-able.
		next unless (-R "$snortrulepath/$file");

		# Call subfunction to read-in rulefile and add rules to
		# the snortrules hash.
		&readrulesfile("$file");
	}

closedir(DIR);

# Save ruleset.
if ($cgiparams{'RULESET'} eq $Lang::tr{'update'}) {
	my $enabled_sids_file = "${General::swroot}/snort/oinkmaster-enabled-sids.conf";
	my $disabled_sids_file = "${General::swroot}/snort/oinkmaster-disabled-sids.conf";

	# Arrays to store sid which should be added to the corresponding files.
	my @enabled_sids;
	my @disabled_sids;

	# Loop through the hash of snortrules.
	foreach my $rulefile(keys %snortrules) {
		# Loop through the single rules of the rulefile.
		foreach my $sid (keys %{$snortrules{$rulefile}}) {
			# Check if there exists a key in the cgiparams hash for this sid.
			if (exists($cgiparams{$sid})) {
				# Look if the rule is disabled.
				if ($snortrules{$rulefile}{$sid}{'State'} eq "off") {
					# Check if the state has been set to 'on'.
					if ($cgiparams{$sid} eq "on") {
						# Add the sid to the enabled_sids array.
						push(@enabled_sids, $sid);

						# Drop item from cgiparams hash.
						delete $cgiparams{$sid};
					}
				}
			} else {
				# Look if the rule is enabled.
				if ($snortrules{$rulefile}{$sid}{'State'} eq "on") {
					# Check if the state is 'on' and should be disabled.
					# In this case there is no entry
					# for the sid in the cgiparams hash.
					# Add it to the disabled_sids array.
					push(@disabled_sids, $sid);

					# Drop item from cgiparams hash.
					delete $cgiparams{$sid};
				}
			}
		}
	}

	# Check if the enabled_sids array contains any sid's.
	if (@enabled_sids) {
		# Open enabled sid's file for writing.
		open(FILE, ">$enabled_sids_file") or die "Could not write to $enabled_sids_file. $!\n";

		# Write header to file.
		print FILE "#Autogenerated file. Any custom changes will be overwritten!\n";

		# Loop through the array of enabled sids and write them to the file.
		foreach my $sid (@enabled_sids) {
			print FILE "enable_sid $sid\n";
		}

		# Close file after writing.
		close(FILE);
	}

	# Check if the enabled_sids array contains any sid's.
	if (@disabled_sids) {
                # Open disabled sid's file for writing.
                open(FILE, ">$disabled_sids_file") or die "Could not write to $disabled_sids_file. $!\n";

                # Write header to file.
                print FILE "#Autogenerated file. Any custom changes will be overwritten!\n";

                # Loop through the array of disabled sids and write them to the file.
                foreach my $sid (@disabled_sids) {
                        print FILE "disable_sid $sid\n";
                }

                # Close file after writing.
                close(FILE);
        }
}

if ($snortsettings{'OINKCODE'} ne "") {
	$errormessage = $Lang::tr{'invalid input for oink code'} unless ($snortsettings{'OINKCODE'} =~ /^[a-z0-9]+$/);
}

if (!$errormessage) {
	if ($snortsettings{'RULES'} eq 'subscripted') {
		$url=" https://www.snort.org/rules/snortrules-snapshot-29111.tar.gz?oinkcode=$snortsettings{'OINKCODE'}";
	} elsif ($snortsettings{'RULES'} eq 'registered') {
		$url=" https://www.snort.org/rules/snortrules-snapshot-29111.tar.gz?oinkcode=$snortsettings{'OINKCODE'}";
	} elsif ($snortsettings{'RULES'} eq 'community') {
		$url=" https://www.snort.org/rules/community";
	} else {
		$url="http://rules.emergingthreats.net/open/snort-2.9.0/emerging.rules.tar.gz";
	}

	if ($snortsettings{'ACTION'} eq $Lang::tr{'save'} && $snortsettings{'ACTION2'} eq "snort" ) {
		&General::writehash("${General::swroot}/snort/settings", \%snortsettings);
		if ($snortsettings{'ENABLE_SNORT'} eq 'on')
		{
			system ('/usr/bin/touch', "${General::swroot}/snort/enable");
		} else {
			unlink "${General::swroot}/snort/enable";
		}
		if ($snortsettings{'ENABLE_SNORT_GREEN'} eq 'on')
		{
			system ('/usr/bin/touch', "${General::swroot}/snort/enable_green");
		} else {
			unlink "${General::swroot}/snort/enable_green";
		}
		if ($snortsettings{'ENABLE_SNORT_BLUE'} eq 'on')
		{
			system ('/usr/bin/touch', "${General::swroot}/snort/enable_blue");
		} else {
			unlink "${General::swroot}/snort/enable_blue";
		}
		if ($snortsettings{'ENABLE_SNORT_ORANGE'} eq 'on')
		{
			system ('/usr/bin/touch', "${General::swroot}/snort/enable_orange");
		} else {
			unlink "${General::swroot}/snort/enable_orange";
		}
		if ($snortsettings{'ENABLE_PREPROCESSOR_HTTP_INSPECT'} eq 'on')
		{
			system ('/usr/bin/touch', "${General::swroot}/snort/enable_preprocessor_http_inspect");
		} else {
			unlink "${General::swroot}/snort/enable_preprocessor_http_inspect";
		}

		system('/usr/local/bin/snortctrl restart >/dev/null');
	}

	# INSTALLMD5 is not in the form, so not retrieved by getcgihash
	&General::readhash("${General::swroot}/snort/settings", \%snortsettings);

	if ($snortsettings{'ACTION'} eq $Lang::tr{'download new ruleset'}) {
		my @df = `/bin/df -B M /var`;
		foreach my $line (@df) {
			next if $line =~ m/^Filesystem/;
			my $return;

			if ($line =~ m/dev/ ) {
				$line =~ m/^.* (\d+)M.*$/;
				my @temp = split(/ +/,$line);
				if ($1<300) {
					$errormessage = "$Lang::tr{'not enough disk space'} < 300MB, /var $1MB";
				} else {
					if ( $snortsettings{'ACTION'} eq $Lang::tr{'download new ruleset'}) {
						&downloadrulesfile();
						sleep(3);
						$return = `cat /var/tmp/log 2>/dev/null`;

					}

					if ($return =~ "ERROR") {
						$errormessage = "<br /><pre>".$return."</pre>";
					} else {
						system("/usr/local/bin/oinkmaster.pl -v -s -u file:///var/tmp/snortrules.tar.gz -C /var/ipfire/snort/oinkmaster.conf -o /etc/snort/rules >>/var/tmp/log 2>&1 &");
						sleep(2);
					}
				}
			}
		}
	}
}

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

###############
# DEBUG DEBUG
# &Header::openbox('100%', 'left', 'DEBUG');
# my $debugCount = 0;
# foreach my $line (sort keys %snortsettings) {
# print "$line = $snortsettings{$line}<br />\n";
# $debugCount++;
# }
# print "&nbsp;Count: $debugCount\n";
# &Header::closebox();
# DEBUG DEBUG
###############

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
}

my $return = `pidof oinkmaster.pl -x`;
chomp($return);
if ($return) {
	&Header::openbox( 'Waiting', 1, "<meta http-equiv='refresh' content='10;'>" );
	print <<END;
	<table>
		<tr><td>
				<img src='/images/indicator.gif' alt='$Lang::tr{'aktiv'}' />&nbsp;
			<td>
				$Lang::tr{'snort working'}
		<tr><td colspan='2' align='center'>
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
				<input type='image' alt='$Lang::tr{'reload'}' title='$Lang::tr{'reload'}' src='/images/view-refresh.png' />
			</form>
		<tr><td colspan='2' align='left'><pre>
END
	my @output = `tail -20 /var/tmp/log`;
	foreach (@output) {
		print "$_";
	}
	print <<END;
			</pre>
		</table>
END
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit;
	refreshpage();
}

&Header::openbox('100%', 'left', $Lang::tr{'intrusion detection system'});
print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'><table width='100%'>
<tr><td class='base'><input type='checkbox' name='ENABLE_SNORT_GREEN' $checked{'ENABLE_SNORT_GREEN'}{'on'} />GREEN Snort
END
;
if ($netsettings{'BLUE_DEV'} ne '') {
  print "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type='checkbox' name='ENABLE_SNORT_BLUE' $checked{'ENABLE_SNORT_BLUE'}{'on'} />   BLUE Snort";
}
if ($netsettings{'ORANGE_DEV'} ne '') {
  print "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type='checkbox' name='ENABLE_SNORT_ORANGE' $checked{'ENABLE_SNORT_ORANGE'}{'on'} />   ORANGE Snort";
}
  print "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type='checkbox' name='ENABLE_SNORT' $checked{'ENABLE_SNORT'}{'on'} />   RED Snort";

print <<END
</td></tr>
<tr>
	<td><br><br></td>
</tr>
<tr>
	<td><b>$Lang::tr{'ids rules update'}</b></td>
</tr>
<tr>
	<td><select name='RULES'>
				<option value='nothing' $selected{'RULES'}{'nothing'} >$Lang::tr{'no'}</option>
				<option value='emerging' $selected{'RULES'}{'emerging'} >$Lang::tr{'emerging rules'}</option>
				<option value='community' $selected{'RULES'}{'community'} >$Lang::tr{'community rules'}</option>
				<option value='registered' $selected{'RULES'}{'registered'} >$Lang::tr{'registered user rules'}</option>
				<option value='subscripted' $selected{'RULES'}{'subscripted'} >$Lang::tr{'subscripted user rules'}</option>
			</select>
	</td>
</tr>
<tr>
	<td><br />
		$Lang::tr{'ids rules license'} <a href='https://www.snort.org/subscribe' target='_blank'>www.snort.org</a>$Lang::tr{'ids rules license1'}<br /><br />
		$Lang::tr{'ids rules license2'} <a href='https://www.snort.org/account/oinkcode' target='_blank'>Get an Oinkcode</a>, $Lang::tr{'ids rules license3'}
	</td>
</tr>
<tr>
	<td nowrap='nowrap'>Oinkcode:&nbsp;<input type='text' size='40' name='OINKCODE' value='$snortsettings{'OINKCODE'}' /></td>
</tr>
<tr>
	<td width='30%' align='left'><br><input type='submit' name='ACTION' value='$Lang::tr{'download new ruleset'}' />
END
;
if ( -e "/var/tmp/snortrules.tar.gz"){
	my @Info = stat("/var/tmp/snortrules.tar.gz");
	$snortsettings{'INSTALLDATE'} = localtime($Info[9]);
}
print "&nbsp;$Lang::tr{'updates installed'}: $snortsettings{'INSTALLDATE'}</td>";

print <<END
</tr>
</table>
<br><br>
<table width='100%'>
<tr>
	<td align='right'><input type='hidden' name='ACTION2' value='snort' /><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
</tr>
</table>
</form>
END
;

if ($results ne '') {
	print "$results";
}

&Header::closebox();

&Header::openbox('100%', 'LEFT', $Lang::tr{'intrusion detection system rules'});
	print"<form method='POST' action='$ENV{'SCRIPT_NAME'}'>\n";

	# Output display table for rule files
	print "<table width='100%'>\n";

	# Local variable required for java script to show/hide
	# rules of a rulefile.
	my $rulesetcount = 1;

	# Loop over each rule file
	foreach my $rulefile (sort keys(%snortrules)) {
		my $rulechecked = '';

		# Check if rule file is enabled
		if ($snortrules{$rulefile}{"State"} eq 'On') {
			$rulechecked = 'CHECKED';
		}

		# Table and rows for the rule files.
		print"<tr>\n";
		print"<td class='base' width='5%'>\n";
		print"<input type='checkbox' name='SNORT_RULE_$rulefile' $rulechecked>\n";
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
		foreach my $sid (sort {$a <=> $b} keys(%{$snortrules{$rulefile}})) {
			# Local vars
			my $ruledefchecked = '';

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
			if ($snortrules{$rulefile}{$sid}{'State'} eq 'on') {
				$ruledefchecked = 'CHECKED';
			}

			# Create rule checkbox and display rule description
			print "<td class='base' width='5%' align='right' $col>\n";
			print "<input type='checkbox' NAME='$sid' $ruledefchecked>\n";
			print "</td>\n";
			print "<td class='base' width='45%' $col>$snortrules{$rulefile}{$sid}{'Description'}</td>";

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

sub refreshpage {
	&Header::openbox( 'Waiting', 1, "<meta http-equiv='refresh' content='1;'>" );
		print "<center><img src='/images/clock.gif' alt='' /><br/><font color='red'>$Lang::tr{'pagerefresh'}</font></center>";
	&Header::closebox();
}

sub downloadrulesfile {
	my $peer;
	my $peerport;

	unlink("/var/tmp/log");

	unless (-e "${General::swroot}/red/active") {
		$errormessage = $Lang::tr{'could not download latest updates'};
		return undef;
	}

	my %proxysettings=();
	&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);

	if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
		($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
	}

	if ($peer) {
		system("wget -r --proxy=on --proxy-user=$proxysettings{'UPSTREAM_USER'} --proxy-passwd=$proxysettings{'UPSTREAM_PASSWORD'} -e http_proxy=http://$peer:$peerport/ -o /var/tmp/log --output-document=/var/tmp/snortrules.tar.gz $url");
	} else {
		system("wget -r -o /var/tmp/log --output-document=/var/tmp/snortrules.tar.gz $url");
	}
}

sub readrulesfile ($) {
	my $rulefile = shift;

	# Open rule file and read in contents
	open(RULEFILE, "$snortrulepath/$rulefile") or die "Unable to read $rulefile!";

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
				# Add rule to the snortrules hash.
				$snortrules{$rulefile}{$sid}{'Description'} = $msg;

				# Grab status of the rule. Check if ruleline starts with a "dash".
				if ($line =~ /^\#/) {
					# If yes, the rule is disabled.
					$snortrules{$rulefile}{$sid}{'State'} = "off";
				} else {
					# Otherwise the rule is enabled.
					$snortrules{$rulefile}{$sid}{'State'} = "on";
				}
			}
		}
        }
}
