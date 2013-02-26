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
$settings{'DROPFORWARD'} = 'on';
$settings{'DROPOUTGOING'} = 'on';
$settings{'DROPPORTSCAN'} = 'on';
$settings{'DROPWIRELESSINPUT'} = 'on';
$settings{'DROPWIRELESSFORWARD'} = 'on';
$settings{'SHOWCOLORS'} = 'off';
$settings{'SHOWREMARK'} = 'on';
$settings{'SHOWTABLES'} = 'on';

my $errormessage = '';
my $warnmessage = '';

&Header::showhttpheaders();

#Get GUI values
&Header::getcgihash(\%settings);

if ($settings{'ACTION'} eq $Lang::tr{'save'}) {
	
	 $errormessage = $Lang::tr{'new optionsfw later'};
	 delete $settings{'__CGI__'};
	 delete $settings{'x'};
	 delete $settings{'y'};
	 &General::writehash($filename, \%settings);             # Save good settings
   }else {
		&General::readhash($filename, \%settings);                      # Get saved settings and reset to good if needed
	}
	system("/usr/local/bin/forwardfwctrl");
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
$checked{'DROPFORWARD'}{'off'} = '';
$checked{'DROPFORWARD'}{'on'} = '';
$checked{'DROPFORWARD'}{$settings{'DROPFORWARD'}} = "checked='checked'";
$checked{'DROPOUTGOING'}{'off'} = '';
$checked{'DROPOUTGOING'}{'on'} = '';
$checked{'DROPOUTGOING'}{$settings{'DROPOUTGOING'}} = "checked='checked'";
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
$checked{'SHOWCOLORS'}{'off'} = '';
$checked{'SHOWCOLORS'}{'on'} = '';
$checked{'SHOWCOLORS'}{$settings{'SHOWCOLORS'}} = "checked='checked'";
$checked{'SHOWREMARK'}{'off'} = '';
$checked{'SHOWREMARK'}{'on'} = '';
$checked{'SHOWREMARK'}{$settings{'SHOWREMARK'}} = "checked='checked'";
$checked{'SHOWTABLES'}{'off'} = '';
$checked{'SHOWTABLES'}{'on'} = '';
$checked{'SHOWTABLES'}{$settings{'SHOWTABLES'}} = "checked='checked'";
$checked{'FWPOLICY'}{'DROP'} = '';
$checked{'FWPOLICY'}{'REJECT'} = '';
$checked{'FWPOLICY'}{$settings{'FWPOLICY'}} = "checked='checked'";
$checked{'FWPOLICY1'}{'DROP'} = '';
$checked{'FWPOLICY1'}{'REJECT'} = '';
$checked{'FWPOLICY1'}{$settings{'FWPOLICY1'}} = "checked='checked'";


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
<tr><td align='left' width='60%'>$Lang::tr{'drop forward'}</td><td align='left'>on <input type='radio' name='DROPFORWARD' value='on' $checked{'DROPFORWARD'}{'on'} />/
																						<input type='radio' name='DROPFORWARD' value='off' $checked{'DROPFORWARD'}{'off'} /> off</td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'drop outgoing'}</td><td align='left'>on <input type='radio' name='DROPOUTGOING' value='on' $checked{'DROPOUTGOING'}{'on'} />/
																						<input type='radio' name='DROPOUTGOING' value='off' $checked{'DROPOUTGOING'}{'off'} /> off</td></tr>																						
<tr><td align='left' width='60%'>$Lang::tr{'drop portscan'}</td><td align='left'>on <input type='radio' name='DROPPORTSCAN' value='on' $checked{'DROPPORTSCAN'}{'on'} />/
																						<input type='radio' name='DROPPORTSCAN' value='off' $checked{'DROPPORTSCAN'}{'off'} /> off</td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'drop wirelessinput'}</td><td align='left'>on <input type='radio' name='DROPWIRELESSINPUT' value='on' $checked{'DROPWIRELESSINPUT'}{'on'} />/
																						<input type='radio' name='DROPWIRELESSINPUT' value='off' $checked{'DROPWIRELESSINPUT'}{'off'} /> off</td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'drop wirelessforward'}</td><td align='left'>on <input type='radio' name='DROPWIRELESSFORWARD' value='on' $checked{'DROPWIRELESSFORWARD'}{'on'} />/
																						<input type='radio' name='DROPWIRELESSFORWARD' value='off' $checked{'DROPWIRELESSFORWARD'}{'off'} /> off</td></tr>
</table>
<br/>

<table width='95%' cellspacing='0'>
<tr bgcolor='$color{'color20'}'><td colspan='2' align='left'><b>$Lang::tr{'fw blue'}</b></td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'drop proxy'}</td><td align='left'>on <input type='radio' name='DROPPROXY' value='on' $checked{'DROPPROXY'}{'on'} />/
																						<input type='radio' name='DROPPROXY' value='off' $checked{'DROPPROXY'}{'off'} /> off</td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'drop samba'}</td><td align='left'>on <input type='radio' name='DROPSAMBA' value='on' $checked{'DROPSAMBA'}{'on'} />/
																						<input type='radio' name='DROPSAMBA' value='off' $checked{'DROPSAMBA'}{'off'} /> off</td></tr>
</table>
<br>
<table width='95%' cellspacing='0'>
<tr bgcolor='$color{'color20'}'><td colspan='2' align='left'><b>$Lang::tr{'fw settings'}</b></td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'fw settings color'}</td><td align='left'>on <input type='radio' name='SHOWCOLORS' value='on' $checked{'SHOWCOLORS'}{'on'} />/
																						<input type='radio' name='SHOWCOLORS' value='off' $checked{'SHOWCOLORS'}{'off'} /> off</td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'fw settings remark'}</td><td align='left'>on <input type='radio' name='SHOWREMARK' value='on' $checked{'SHOWREMARK'}{'on'} />/
																						<input type='radio' name='SHOWREMARK' value='off' $checked{'SHOWREMARK'}{'off'} /> off</td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'fw settings ruletable'}</td><td align='left'>on<input type='radio' name='SHOWTABLES' value='on' $checked{'SHOWTABLES'}{'on'} />/
																						<input type='radio' name='SHOWTABLES' value='off' $checked{'SHOWTABLES'}{'off'} /> off</td></tr>
</table>
<br />
<table width='95%' cellspacing='0'>
<tr bgcolor='$color{'color20'}'><td colspan='2' align='left'><b>$Lang::tr{'fw default drop'}</b></td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'drop action'}</td><td align='left'>DROP <input type='radio' name='FWPOLICY' value='DROP' $checked{'FWPOLICY'}{'DROP'} />/
																						<input type='radio' name='FWPOLICY' value='REJECT' $checked{'FWPOLICY'}{'REJECT'} /> REJECT</td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'drop action1'}</td><td align='left'>DROP <input type='radio' name='FWPOLICY1' value='DROP' $checked{'FWPOLICY1'}{'DROP'} />/
																						<input type='radio' name='FWPOLICY1' value='REJECT' $checked{'FWPOLICY1'}{'REJECT'} /> REJECT</td></tr>

</table>

<br />
<table width='10%' cellspacing='0'>
<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='submit' name='ACTION' value=$Lang::tr{'save'} />
</form></td></tr>
</table>
</form>
END
;
&Header::closebox();
&Header::closebigbox();
&Header::closepage();
