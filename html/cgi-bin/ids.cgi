#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#

use LWP::UserAgent;
use File::Copy;
use File::Temp qw/ tempfile tempdir /;
use strict;

# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

my %snortsettings=();
my %checked=();
my %selected=();
my %netsettings=();
our $errormessage = '';
our $md5 = '0';# not '' to avoid displaying the wrong message when INSTALLMD5 not set
our $realmd5 = '';
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
$snortsettings{'INSTALLMD5'} = '';

&Header::getcgihash(\%snortsettings, {'wantfile' => 1, 'filevar' => 'FH'});

####################### Added for snort rules control #################################
my $snortrulepath;
my @snortconfig;
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

if (-e "/etc/snort/snort.conf") {
	# Open snort.conf file, read it in, close it, and re-open for writing
	open(FILE, "/etc/snort/snort.conf") or die 'Unable to read snort config file.';
	@snortconfig = <FILE>;
	close(FILE);
	open(FILE, ">/etc/snort/snort.conf") or die 'Unable to write snort config file.';

	# Loop over each line
	foreach my $line (@snortconfig) {
		# Trim the line
		chomp $line;

		# Check for a line with .rules
		if ($line =~ /\.rules$/) {
			# Parse out rule file name
			$rule = $line;
			$rule =~ s/\$RULE_PATH\///i;
			$rule =~ s/ ?include ?//i;
			$rule =~ s/\#//i;
			my $snortrulepathrule = "$snortrulepath/$rule";

			# Open rule file and read in contents
			open(RULEFILE, "$snortrulepath/$rule") or die "Unable to read snort rule file for reading => $snortrulepath/$rule.";
			my @snortrulefile = <RULEFILE>;
			close(RULEFILE);
			open(RULEFILE, ">$snortrulepath/$rule") or die "Unable to write snort rule file for writing $snortrulepath/$rule";

			# Local vars
			my $dashlinecnt = 0;
			my $desclook = 1;
			my $snortruledesc = '';
			my %snortruledef = ();
			my $rulecnt = 1;

			# Loop over rule file contents
			foreach my $ruleline (@snortrulefile) {
				chomp $ruleline;

				# If still looking for a description
				if ($desclook) {
					# If line does not start with a # anymore, then done looking for a description
					if ($ruleline !~ /^\#/) {
						$desclook = 0;
					}

					# If see more than one dashed line, (start to) create rule file description
					if ($dashlinecnt > 1) {
						# Check for a line starting with a #
						if ($ruleline =~ /^\#/) {
							# Create tempruleline
							my $tempruleline = $ruleline;

							# Strip off # and clean up line
							$tempruleline =~ s/\# ?//i;

							# Check for part of a description
							if ($snortruledesc eq '') {
								$snortruledesc = $tempruleline;
							} else {
								$snortruledesc .= " $tempruleline";
							}
						} else {
							# Must be done
							$desclook = 0;
						}
					}

					# If have a dashed line, increment count
					if ($ruleline =~ /\# ?\-+/) {
						$dashlinecnt++;
					}
				} else {
					# Parse out rule file rule's message for display
					if ($ruleline =~ /(msg\:\"[^\"]+\";)/) {
						my $msg = '';
						$msg = $1;
						$msg =~ s/msg\:\"//i;
						$msg =~ s/\";//i;
						$snortruledef{$rulecnt}{'Description'} = $msg;

						# Check for 'Save' and rule file displayed in query string
						if (($snortsettings{'ACTION'} eq $Lang::tr{'update'}) && ($ENV{'QUERY_STRING'} =~ /$rule/i)) {
							# Check for a disable rule which is now enabled, or an enabled rule which is now disabled
							if ((($ruleline =~ /^\#/) && (exists $snortsettings{"SNORT_RULE_$rule\_$rulecnt"})) || (($ruleline !~ /^\#/) && (!exists $snortsettings{"SNORT_RULE_$rule\_$rulecnt"}))) {
								$restartsnortrequired = 1;
							}

							# Strip out leading # from rule line
							$ruleline =~ s/\# ?//i;

							# Check if it does not exists (which means it is disabled), append a #
							if (!exists $snortsettings{"SNORT_RULE_$rule\_$rulecnt"}) {
								$ruleline = "#"." $ruleline";
							}
						}

						# Check if ruleline does not begin with a #, so it is enabled
						if ($ruleline !~ /^\#/) {
							$snortruledef{$rulecnt++}{'State'} = 'Enabled';
						} else {
							# Otherwise it is disabled
							$snortruledef{$rulecnt++}{'State'} = 'Disabled';
						}
					}
				}

				# Print ruleline to RULEFILE
				print RULEFILE "$ruleline\n";
			}

			# Close RULEFILE
			close(RULEFILE);

			# Check for 'Save'
			if ($snortsettings{'ACTION'} eq $Lang::tr{'update'}) {
				# Check for a disable rule which is now enabled, or an enabled rule which is now disabled
				if ((($line =~ /^\#/) && (exists $snortsettings{"SNORT_RULE_$rule"})) || (($line !~ /^\#/) && (!exists $snortsettings{"SNORT_RULE_$rule"}))) {
					$restartsnortrequired = 1;
				}

				# Strip out leading # from rule line
				$line =~ s/\# ?//i;

				# Check if it does not exists (which means it is disabled), append a #
				if (!exists $snortsettings{"SNORT_RULE_$rule"}) {
					$line = "# $line";
				}
			}

			# Check for rule state
			if ($line =~ /^\#/) {
				$snortrules{$rule}{"State"} = "Disabled";
			} else {
				$snortrules{$rule}{"State"} = "Enabled";
			}

			# Set rule description
			$snortrules{$rule}{"Description"} = $snortruledesc;

			# Loop over sorted rules
			foreach my $ruledef (sort {$a <=> $b} keys(%snortruledef)) {
				$snortrules{$rule}{"Definition"}{$ruledef}{'Description'} = $snortruledef{$ruledef}{'Description'};
				$snortrules{$rule}{"Definition"}{$ruledef}{'State'} = $snortruledef{$ruledef}{'State'};
			}

			$snortruledesc = '';
			print FILE "$line\n";
		} elsif ($line =~ /var RULE_PATH/) {
			($tmp, $tmp, $snortrulepath) = split(' ', $line);
			print FILE "$line\n";
		} else {
			print FILE "$line\n";
		}
	}
	close(FILE);

	if ($restartsnortrequired) {
		system('/usr/local/bin/snortctrl restart >/dev/null');
	}
}

#######################  End added for snort rules control  #################################

if ($snortsettings{'RULES'} eq 'subscripted') {
	$url="http://www.snort.org/pub-bin/oinkmaster.cgi/$snortsettings{'OINKCODE'}/snortrules-snapshot-CURRENT_s.tar.gz";
} elsif ($snortsettings{'RULES'} eq 'registered') {
	$url="http://www.snort.org/pub-bin/oinkmaster.cgi/$snortsettings{'OINKCODE'}/snortrules-snapshot-CURRENT.tar.gz";
} else {
	$url="http://www.snort.org/pub-bin/downloads.cgi/Download/comm_rules/Community-Rules-CURRENT.tar.gz";
}

if ($snortsettings{'ACTION'} eq $Lang::tr{'save'})
{
	$errormessage = $Lang::tr{'invalid input for oink code'} unless (
	    ($snortsettings{'OINKCODE'} =~ /^[a-z0-9]+$/)  ||
	    ($snortsettings{'RULESTYPE'} eq 'nothing' )       );

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

		system('/usr/local/bin/snortctrl restart >/dev/null');

} else {
	 # INSTALLMD5 is not in the form, so not retrieved by getcgihash
	&General::readhash("${General::swroot}/snort/settings", \%snortsettings);
}

if ($snortsettings{'ACTION'} eq $Lang::tr{'download new ruleset'}) {
	$md5 = &getmd5;
	if (($snortsettings{'INSTALLMD5'} ne $md5) && defined $md5 ) {
		chomp($md5);
		my $filename = &downloadrulesfile();
		if (defined $filename) {
			# Check MD5sum
			$realmd5 = `/usr/bin/md5sum $filename`;
			chomp ($realmd5);
			$realmd5 =~ s/^(\w+)\s.*$/$1/;
			if ($md5 ne $realmd5) {
				$errormessage = "$Lang::tr{'invalid md5sum'}";
			} else {
				$results = "<b>$Lang::tr{'installed updates'}</b>\n<pre>";
				$results .=`/usr/local/bin/oinkmaster.pl -s -u file://$filename -C /var/ipfire/snort/oinkmaster.conf -o /etc/snort/rules 2>&1`;
				$results .= "</pre>";
			}
			unlink ($filename);
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
$selected{'RULES'}{'registered'} = '';
$selected{'RULES'}{'subscripted'} = '';
$selected{'RULES'}{$snortsettings{'RULES'}} = "selected='selected'";

&Header::openpage($Lang::tr{'intrusion detection system'}, 1, '');

####################### Added for snort rules control #################################
print "<SCRIPT LANGUAGE='JavaScript' SRC='/include/snortupdateutility.js'></SCRIPT>";
print <<END
<STYLE TYPE="text/css">   
<!--
.section {
	border: groove;
}
.row1color {
	border: ridge;
	background-color: $color{'color22'};
}
.row2color {
	border: ridge;
	background-color: $color{'color20'};
}
.rowselected {
	border: double #FF0000;
	background-color: #DCDCDC;
}
-->
</STYLE>
END
;
#######################  End added for snort rules control  #################################

&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
}

&Header::openbox('100%', 'left', $Lang::tr{'intrusion detection system2'});
print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'><table width='100%'>
<tr>
	<td class='base'><input type='checkbox' name='ENABLE_SNORT_GREEN' $checked{'ENABLE_SNORT_GREEN'}{'on'} />
		GREEN Snort</td>
</tr>
END
;
if ($netsettings{'BLUE_DEV'} ne '') {
print <<END
<tr>
	<td class='base'><input type='checkbox' name='ENABLE_SNORT_BLUE' $checked{'ENABLE_SNORT_BLUE'}{'on'} />
		BLUE Snort</td>
</tr>
END
;
}
if ($netsettings{'ORANGE_DEV'} ne '') {
print <<END
<tr>
	<td class='base'><input type='checkbox' name='ENABLE_SNORT_ORANGE' $checked{'ENABLE_SNORT_ORANGE'}{'on'} />
		ORANGE Snort</td>
</tr>
END
;
}
print <<END
<tr>
	<td class='base'><input type='checkbox' name='ENABLE_SNORT' $checked{'ENABLE_SNORT'}{'on'} />
		RED Snort</td>
</tr>
<tr>
	<td><hr /></td>
</tr>
<tr>
	<td><b>$Lang::tr{'ids rules update'}</b></td>
</tr>
<tr>
	<td><select name='RULES'>
				<option value='nothing' $selected{'RULES'}{'nothing'} >$Lang::tr{'no'}</option>
				<option value='community' $selected{'RULES'}{'community'} >$Lang::tr{'community rules'}</option>
				<option value='registered' $selected{'RULES'}{'registered'} >$Lang::tr{'registered user rules'}</option>
				<option value='subscripted' $selected{'RULES'}{'subscripted'} >$Lang::tr{'subscripted user rules'}</option>
			</select>
	</td>
</tr>
<tr>
	<td><br />
		$Lang::tr{'ids rules license'} <a href='http://www.snort.org/' target='_blank'>http://www.snort.org</a>.<br />
		<br />
		$Lang::tr{'ids rules license2'} <a href='http://www.snort.org/reg-bin/userprefs.cgi' target='_blank'>USER PREFERENCES</a>, $Lang::tr{'ids rules license3'}<br />
	</td>
</tr>
<tr>
	<td nowrap='nowrap'>Oinkcode:&nbsp;<input type='text' size='40' name='OINKCODE' value='$snortsettings{'OINKCODE'}' /></td>
</tr>
<tr>
	<td width='30%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'download new ruleset'}' />
END
;

if ($snortsettings{'INSTALLMD5'} eq $md5) {
	print "&nbsp;$Lang::tr{'rules already up to date'}</td>";
} else {
	if ( $snortsettings{'ACTION'} eq $Lang::tr{'download new ruleset'} && $md5 eq $realmd5 ) {
		$snortsettings{'INSTALLMD5'} = $realmd5;
		$snortsettings{'INSTALLDATE'} = `/bin/date +'%Y-%m-%d'`;
		&General::writehash("${General::swroot}/snort/settings", \%snortsettings);
	}
	print "&nbsp;$Lang::tr{'updates installed'}: $snortsettings{'INSTALLDATE'}</td>";
}
print <<END
</tr>
</table>
<hr />
<table width='100%'>
<tr>
	<td width='55%'>&nbsp;</td>
	<td width='40%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
	<td width='5%'>
		&nbsp; <!-- space for future online help link -->
	</td>
</tr>
</table>
</form>
END
;

if ($results ne '') {
	print "$results";
}

&Header::closebox();
####################### Added for snort rules control #################################
if ( -e "${General::swroot}/snort/enable" || -e "${General::swroot}/snort/enable_green" || -e "${General::swroot}/snort/enable_blue" || -e "${General::swroot}/snort/enable_orange" ) {
	&Header::openbox('100%', 'LEFT', $Lang::tr{'intrusion detection system rules'});
		# Output display table for rule files
		print "<TABLE width='100%'><TR><TD VALIGN='TOP'><TABLE>";
		
		print "<form method='post'>";

		# Local vars
		my $ruledisplaycnt = 1;
		my $rulecnt = keys %snortrules;
		$rulecnt++;
		$rulecnt = $rulecnt / 2;

		# Loop over each rule file
		foreach my $rulefile (sort keys(%snortrules)) {
			my $rulechecked = '';

			# Check if reached half-way through rule file rules to start new column
			if ($ruledisplaycnt > $rulecnt) {
				print "</TABLE></TD><TD VALIGN='TOP'><TABLE>";
				$ruledisplaycnt = 0;
			}

			# Check if rule file is enabled
			if ($snortrules{$rulefile}{"State"} eq 'Enabled') {
				$rulechecked = 'CHECKED';
			}

			# Create rule file link, vars array, and display flag
			my $rulefilelink = "?RULEFILE=$rulefile";
			my $rulefiletoclose = '';
			my @queryvars = ();
			my $displayrulefilerules = 0;

			# Check for passed in query string
			if ($ENV{'QUERY_STRING'}) {
				# Split out vars
				@queryvars = split(/\&/, $ENV{'QUERY_STRING'});

				# Loop over values
				foreach $value (@queryvars) {
					# Split out var pairs
					($var, $linkedrulefile) = split(/=/, $value);

					# Check if var is 'RULEFILE'
					if ($var eq 'RULEFILE') {
						# Check if rulefile equals linkedrulefile
						if ($rulefile eq $linkedrulefile) {
							# Set display flag
							$displayrulefilerules = 1;

							# Strip out rulefile from rulefilelink
							$rulefilelink =~ s/RULEFILE=$linkedrulefile//g;
						} else {
							# Add linked rule file to rulefilelink
							$rulefilelink .= "&RULEFILE=$linkedrulefile";
						}
					}
				}
			}

			# Strip out extra & & ? from rulefilelink
			$rulefilelink =~ s/^\?\&/\?/i;

			# Check for a single '?' and replace with page for proper link display
			if ($rulefilelink eq '?') {
				$rulefilelink = "ids.cgi";
			}

			# Output rule file name and checkbox
			print "<TR><TD CLASS='base' VALIGN='TOP'><INPUT TYPE='checkbox' NAME='SNORT_RULE_$rulefile' $rulechecked> <A HREF='$rulefilelink'>$rulefile</A></TD></TR>";
			print "<TR><TD CLASS='base' VALIGN='TOP'>";

			# Check for empty 'Description'
			if ($snortrules{$rulefile}{'Description'} eq '') {
				print "<TABLE WIDTH='100%'><TR><TD CLASS='base'>No description available</TD></TR>";
			} else {
				# Output rule file 'Description'
				print "<TABLE WIDTH='100%'><TR><TD CLASS='base'>$snortrules{$rulefile}{'Description'}</TD></TR>";
			}

			# Check for display flag
			if ($displayrulefilerules) {
				# Rule file definition rule display
				print "<TR><TD CLASS='base' VALIGN='TOP'><TABLE border=1><TR>";

				# Local vars
			 	my $ruledefdisplaycnt = 0;
				my $ruledefcnt = keys %{$snortrules{$rulefile}{"Definition"}};
				$ruledefcnt++;
				$ruledefcnt = $ruledefcnt / 2;

				# Loop over rule file rules
				foreach my $ruledef (sort {$a <=> $b} keys(%{$snortrules{$rulefile}{"Definition"}})) {
					# Local vars
					my $ruledefchecked = '';

					# If have display 2 rules, start new row
					if (($ruledefdisplaycnt % 2) == 0) {
						print "</TR><TR>";
						$ruledefdisplaycnt = 0;
					}

					# Check for rules state
					if ($snortrules{$rulefile}{'Definition'}{$ruledef}{'State'} eq 'Enabled') {
						$ruledefchecked = 'CHECKED';
					}

					# Create rule file rule's checkbox
					$checkboxname = "SNORT_RULE_$rulefile";
					$checkboxname .= "_$ruledef";
					print "<TD CLASS='base'><INPUT TYPE='checkbox' NAME='$checkboxname' $ruledefchecked> $snortrules{$rulefile}{'Definition'}{$ruledef}{'Description'}</TD>";

					# Increment count
					$ruledefdisplaycnt++;
				}
	
				# If do not have second rule for row, create empty cell
				if (($ruledefdisplaycnt % 2) != 0) {
					print "<TD CLASS='base'></TD>";
				}

				# Close display table
				print "</TR></TABLE></TD></TR>";
			}

			# Close display table
			print "</TABLE>";

			# Increment ruledisplaycnt
			$ruledisplaycnt++;
		}

	print "</TD></TR></TABLE></TD></TR></TABLE>";
	print <<END
<table width='100%'>
<tr>
	<td width='33%'>&nbsp;</td>
	<td width='33%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'update'}' /></td>
	<td width='33%'>
		&nbsp; <!-- space for future online help link -->
	</td>
</tr>
</table>
</form>
END
;
	&Header::closebox();
}
#######################  End added for snort rules control  #################################
&Header::closebigbox();
&Header::closepage();

sub getmd5 {
	# Retrieve MD5 sum from $url.md5 file
	#
	my $md5buf = &geturl("$url.md5");
	return undef unless $md5buf;

	if (0) { # 1 to debug
		my $filename='';
		my $fh='';
		($fh, $filename) = tempfile('/tmp/XXXXXXXX',SUFFIX => '.md5' );
		binmode ($fh);
		syswrite ($fh, $md5buf->content);
		close($fh);
	}
	return $md5buf->content;
}
sub downloadrulesfile {
	my $return = &geturl($url);
	return undef unless $return;

	if (index($return->content, "\037\213") == -1 ) { # \037\213 is .gz beginning
		$errormessage = $Lang::tr{'invalid loaded file'};
		return undef;
	}

	my $filename='';
	my $fh='';
	($fh, $filename) = tempfile('/tmp/XXXXXXXX',SUFFIX => '.tar.gz' );#oinkmaster work only with this extension
	binmode ($fh);
	syswrite ($fh, $return->content);
	close($fh);
	return $filename;
}

sub geturl ($) {
	my $url=$_[0];

	unless (-e "${General::swroot}/red/active") {
		$errormessage = $Lang::tr{'could not download latest updates'};
		return undef;
	}

	my $downloader = LWP::UserAgent->new;
	$downloader->timeout(5);

	my %proxysettings=();
	&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);

	if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
		my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
		if ($proxysettings{'UPSTREAM_USER'}) {
			$downloader->proxy("http","http://$proxysettings{'UPSTREAM_USER'}:$proxysettings{'UPSTREAM_PASSWORD'}@"."$peer:$peerport/");
		} else {
			$downloader->proxy("http","http://$peer:$peerport/");
		}
	}

	my $return = $downloader->get($url,'Cache-Control','no-cache');

	if ($return->code == 403) {
		$errormessage = $Lang::tr{'access refused with this oinkcode'};
		return undef;
	} elsif (!$return->is_success()) {
		$errormessage = $Lang::tr{'could not download latest updates'};
		return undef;
	}

	return $return;

}
