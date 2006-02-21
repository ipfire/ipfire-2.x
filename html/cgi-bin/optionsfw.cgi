#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# Copyright (C) 01-02-2002 Graham Smith <grhm@grhm.co.uk>
#
# $Id: optionsfw.cgi,v 1.1.2.10 2005/10/03 00:34:10 gespinasse Exp $
#
#

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require 'CONFIG_ROOT/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";


my %checked =();     # Checkbox manipulations

# File used
my $filename = "${General::swroot}/optionsfw/settings";

our %settings=();
#Settings1
$settings{'DISABLEPING'} = 'NO';
$settings{'ACTION'} = '';		# add/edit/remove

my $errormessage = '';
my $warnmessage = '';

&Header::showhttpheaders();

#Get GUI values
&Header::getcgihash(\%settings);

if ($settings{'ACTION'} eq $Lang::tr{'save'}) {
	if ($settings{'DISABLEPING'} !~ /^(NO|ONLYRED|ALL)$/) {
		$errormessage = $Lang::tr{'invalid input'};
		goto ERROR; }
	unless ($errormessage) {					# Everything is ok, save settings
		&General::writehash($filename, \%settings);		# Save good settings
		$settings{'ACTION'} = $Lang::tr{'save'};		# Recreate  'ACTION'
		system('/usr/local/bin/setfilters');
	}

	ERROR:								# Leave the faulty field untouched
} else {
	&General::readhash($filename, \%settings);			# Get saved settings and reset to good if needed
}
$checked{'DISABLEPING'}{'NO'} = '';
$checked{'DISABLEPING'}{'ONLYRED'} = '';
$checked{'DISABLEPING'}{'ALL'} = '';
$checked{'DISABLEPING'}{$settings{'DISABLEPING'}} = "checked='checked'";

&Header::openpage($Lang::tr{'options fw'}, 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<font class='base'>$errormessage&nbsp;</font>";
	&Header::closebox();
}

&Header::openbox('100%', 'left', $Lang::tr{'options fw'});
print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>";

print <<END
<table width='100%'>
<tr>
	<td class='base' width='100%' colspan='3'><b>$Lang::tr{'ping disabled'}</b></td>
</tr>
<tr>
	<td class='base'><input type='radio' name='DISABLEPING' value='NO' $checked{'DISABLEPING'}{'NO'} />$Lang::tr{'no'}</td>
	<td>&nbsp;</td>
</tr>
<tr>
	<td><input type='radio' name='DISABLEPING' value='ONLYRED' $checked{'DISABLEPING'}{'ONLYRED'} />$Lang::tr{'only red'}</td>
	<td width='80%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
</tr>
<tr>
	<td><input type='radio' name='DISABLEPING' value='ALL' $checked{'DISABLEPING'}{'ALL'} />$Lang::tr{'all interfaces'}</td>
	<td class='base' width='10%' align='right'><!-- Space for future online help link --></td>
</tr>
</table>
</form>
END
;
&Header::closebox();

&Header::closebigbox();

&Header::closepage();
