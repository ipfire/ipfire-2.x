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

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";


my %checked =();     # Checkbox manipulations

# File used
my $filename = "${General::swroot}/optionsfw/settings";

our %settings=();
$settings{'DISABLEPING'} = 'NO';
$settings{'DROPNEWNOTSYN'} = 'on';
$settings{'DROPINPUT'} = 'on';
$settings{'DROPOUTPUT'} = 'on';
$settings{'DROPPORTSCAN'} = 'on';
$settings{'DROPWIRELESSINPUT'} = 'on';
$settings{'DROPWIRELESSFORWARD'} = 'on';

my $errormessage = '';
my $warnmessage = '';

&Header::showhttpheaders();

#Get GUI values
&Header::getcgihash(\%settings);

if ($settings{'ACTION'} eq $Lang::tr{'save'}) {
	 $errormessage = $Lang::tr{'new optionsfw later'};
	 delete $settings{'__CGI__'};delete $settings{'x'};delete $settings{'y'};
	 &General::writehash($filename, \%settings);             # Save good settings
   } else {
	 &General::readhash($filename, \%settings);                      # Get saved settings and reset to good if needed
	 }

&Header::openpage($Lang::tr{'options fw'}, 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
        &Header::openbox('100%', 'left', $Lang::tr{'warning messages'});
        print "<font color='red'>$errormessage&nbsp;</font>";
        &Header::closebox();
}

$checked{'DROPNEWNOTSYN'}{'off'} = '';
$checked{'DROPNEWNOTSYN'}{'on'} = '';
$checked{'DROPNEWNOTSYN'}{$settings{'DROPNEWNOTSYN'}} = "checked='checked'";
$checked{'DROPINPUT'}{'off'} = '';
$checked{'DROPINPUT'}{'on'} = '';
$checked{'DROPINPUT'}{$settings{'DROPINPUT'}} = "checked='checked'";
$checked{'DROPOUTPUT'}{'off'} = '';
$checked{'DROPOUTPUT'}{'on'} = '';
$checked{'DROPOUTPUT'}{$settings{'DROPOUTPUT'}} = "checked='checked'";
$checked{'DROPPORTSCAN'}{'off'} = '';
$checked{'DROPPORTSCAN'}{'on'} = '';
$checked{'DROPPORTSCAN'}{$settings{'DROPPORTSCAN'}} = "checked='checked'";
$checked{'DROPWIRELESSINPUT'}{'off'} = '';
$checked{'DROPWIRELESSINPUT'}{'on'} = '';
$checked{'DROPWIRELESSINPUT'}{$settings{'DROPWIRELESSINPUT'}} = "checked='checked'";
$checked{'DROPWIRELESSFORWARD'}{'off'} = '';
$checked{'DROPWIRELESSFORWARD'}{'on'} = '';
$checked{'DROPWIRELESSFORWARD'}{$settings{'DROPWIRELESSFORWARD'}} = "checked='checked'";
$checked{'DROPPROXY'}{'off'} = '';
$checked{'DROPPROXY'}{'on'} = '';
$checked{'DROPPROXY'}{$settings{'DROPPROXY'}} = "checked='checked'";
$checked{'DROPSAMBA'}{'off'} = '';
$checked{'DROPSAMBA'}{'on'} = '';
$checked{'DROPSAMBA'}{$settings{'DROPSAMBA'}} = "checked='checked'";

&Header::openbox('100%', 'center', $Lang::tr{'options fw'});
print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>";

print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
<tr bgcolor='$color{'color20'}'><td colspan='2' align='left'><b>$Lang::tr{'fw logging'}</b></td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'drop newnotsyn'}</td><td align='left'>on <input type='radio' name='DROPNEWNOTSYN' value='on' $checked{'DROPNEWNOTSYN'}{'on'} />/
																						<input type='radio' name='DROPNEWNOTSYN' value='off' $checked{'DROPNEWNOTSYN'}{'off'} /> off</td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'drop input'}</td><td align='left'>on <input type='radio' name='DROPINPUT' value='on' $checked{'DROPINPUT'}{'on'} />/
																						<input type='radio' name='DROPINPUT' value='off' $checked{'DROPINPUT'}{'off'} /> off</td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'drop output'}</td><td align='left'>on <input type='radio' name='DROPOUTPUT' value='on' $checked{'DROPOUTPUT'}{'on'} />/
																						<input type='radio' name='DROPOUTPUT' value='off' $checked{'DROPOUTPUT'}{'off'} /> off</td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'drop portscan'}</td><td align='left'>on <input type='radio' name='DROPPORTSCAN' value='on' $checked{'DROPPORTSCAN'}{'on'} />/
																						<input type='radio' name='DROPPORTSCAN' value='off' $checked{'DROPPORTSCAN'}{'off'} /> off</td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'drop wirelessinput'}</td><td align='left'>on <input type='radio' name='DROPWIRELESSINPUT' value='on' $checked{'DROPWIRELESSINPUT'}{'on'} />/
																						<input type='radio' name='DROPWIRELESSINPUT' value='off' $checked{'DROPWIRELESSINPUT'}{'off'} /> off</td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'drop wirelessforward'}</td><td align='left'>on <input type='radio' name='DROPWIRELESSFORWARD' value='on' $checked{'DROPWIRELESSFORWARD'}{'on'} />/
																						<input type='radio' name='DROPWIRELESSFORWARD' value='off' $checked{'DROPWIRELESSFORWARD'}{'off'} /> off</td></tr>
</table>
<br />
<table width='95%' cellspacing='0'>
<tr bgcolor='$color{'color20'}'><td colspan='2' align='left'><b>$Lang::tr{'fw blue'}</b></td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'drop proxy'}</td><td align='left'>on <input type='radio' name='DROPPROXY' value='on' $checked{'DROPPROXY'}{'on'} />/
																						<input type='radio' name='DROPPROXY' value='off' $checked{'DROPPROXY'}{'off'} /> off</td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'drop samba'}</td><td align='left'>on <input type='radio' name='DROPSAMBA' value='on' $checked{'DROPSAMBA'}{'on'} />/
																						<input type='radio' name='DROPSAMBA' value='off' $checked{'DROPSAMBA'}{'off'} /> off</td></tr>
</table>
<br />
<table width='10%' cellspacing='0'>
<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value=$Lang::tr{'save'} />
												<input type='image' alt='$Lang::tr{'save'}' title='$Lang::tr{'save'}' src='/images/media-floppy.png' /></form></td></tr>
</table>
</form>
END
;
&Header::closebox();
&Header::closebigbox();
&Header::closepage();
