#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2022  IPFire Team  <info@ipfire.org>                     #
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

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";


my %checked =();     # Checkbox manipulations
our %settings=();
my %fwdfwsettings=();
my %configfwdfw=();
my %configoutgoingfw=();

my $configfwdfw		= "${General::swroot}/firewall/config";
my $configoutgoing	= "${General::swroot}/firewall/outgoing";
my $errormessage = '';
my $warnmessage = '';
my $filename = "${General::swroot}/optionsfw/settings";

&General::readhash("${General::swroot}/firewall/settings", \%fwdfwsettings);
&Header::showhttpheaders();

#Get GUI values
&Header::getcgihash(\%settings);
if ($settings{'ACTION'} eq $Lang::tr{'save'}) {
	if ($settings{'defpol'} ne '1'){
		$errormessage .= $Lang::tr{'new optionsfw later'};
		&General::writehash($filename, \%settings);             # Save good settings
		&General::system("/usr/local/bin/firewallctrl");
	}else{
		if ($settings{'POLICY'} ne ''){
			$fwdfwsettings{'POLICY'} = $settings{'POLICY'};
		}
		if ($settings{'POLICY1'} ne ''){
			$fwdfwsettings{'POLICY1'} = $settings{'POLICY1'};
		}
		my $MODE = $fwdfwsettings{'POLICY'};
		my $MODE1 = $fwdfwsettings{'POLICY1'};
		%fwdfwsettings = ();
		$fwdfwsettings{'POLICY'} = "$MODE";
		$fwdfwsettings{'POLICY1'} = "$MODE1";
		&General::writehash("${General::swroot}/firewall/settings", \%fwdfwsettings);
		&General::readhash("${General::swroot}/firewall/settings", \%fwdfwsettings);
		&General::system("/usr/local/bin/firewallctrl");
	}
	&General::readhash($filename, \%settings);             # Load good settings
}

&Header::openpage($Lang::tr{'options fw'}, 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);
&General::readhash($filename, \%settings);
if ($errormessage) {
        &Header::openbox('100%', 'left', $Lang::tr{'warning messages'});
        print "<font color='red'>$errormessage&nbsp;</font>";
        &Header::closebox();
}

# Set new defaults
if (!$settings{'MASQUERADE_GREEN'}) {
	$settings{'MASQUERADE_GREEN'} = 'on';
}
if (!$settings{'MASQUERADE_ORANGE'}) {
	$settings{'MASQUERADE_ORANGE'} = 'on';
}
if (!$settings{'MASQUERADE_BLUE'}) {
	$settings{'MASQUERADE_BLUE'} = 'on';
}
if (!$settings{'DROPSPOOFEDMARTIAN'}) {
	$settings{'DROPSPOOFEDMARTIAN'} = 'on';
}
if (!$settings{'DROPHOSTILE'}) {
	$settings{'DROPHOSTILE'} = 'off';
}
if (!$settings{'LOGDROPCTINVALID'}) {
	$settings{'LOGDROPCTINVALID'} = 'on';
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
$checked{'DROPSPOOFEDMARTIAN'}{'off'} = '';
$checked{'DROPSPOOFEDMARTIAN'}{'on'} = '';
$checked{'DROPSPOOFEDMARTIAN'}{$settings{'DROPSPOOFEDMARTIAN'}} = "checked='checked'";
$checked{'DROPHOSTILE'}{'off'} = '';
$checked{'DROPHOSTILE'}{'on'} = '';
$checked{'DROPHOSTILE'}{$settings{'DROPHOSTILE'}} = "checked='checked'";
$checked{'LOGDROPCTINVALID'}{'off'} = '';
$checked{'LOGDROPCTINVALID'}{'on'} = '';
$checked{'LOGDROPCTINVALID'}{$settings{'LOGDROPCTINVALID'}} = "checked='checked'";
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
$checked{'SHOWDROPDOWN'}{'off'} = '';
$checked{'SHOWDROPDOWN'}{'on'} = '';
$checked{'SHOWDROPDOWN'}{$settings{'SHOWDROPDOWN'}} = "checked='checked'";
$selected{'FWPOLICY'}{$settings{'FWPOLICY'}}= 'selected';
$selected{'FWPOLICY1'}{$settings{'FWPOLICY1'}}= 'selected';
$selected{'FWPOLICY2'}{$settings{'FWPOLICY2'}}= 'selected';
$selected{'MASQUERADE_GREEN'}{'off'} = '';
$selected{'MASQUERADE_GREEN'}{'on'} = '';
$selected{'MASQUERADE_GREEN'}{$settings{'MASQUERADE_GREEN'}} = 'selected="selected"';
$selected{'MASQUERADE_ORANGE'}{'off'} = '';
$selected{'MASQUERADE_ORANGE'}{'on'} = '';
$selected{'MASQUERADE_ORANGE'}{$settings{'MASQUERADE_ORANGE'}} = 'selected="selected"';
$selected{'MASQUERADE_BLUE'}{'off'} = '';
$selected{'MASQUERADE_BLUE'}{'on'} = '';
$selected{'MASQUERADE_BLUE'}{$settings{'MASQUERADE_BLUE'}} = 'selected="selected"';

&Header::openbox('100%', 'center',);
print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>";

print <<END;
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='95%' cellspacing='0'>
		<tr bgcolor='$color{'color20'}'>
			<td colspan='2' align='left'><b>$Lang::tr{'masquerading'}</b></td>
		</tr>
		<tr>
			<td align='left' width='60%'>$Lang::tr{'masquerade green'}</td>
			<td>
				<select name='MASQUERADE_GREEN'>
					<option value='on' $selected{'MASQUERADE_GREEN'}{'on'}>$Lang::tr{'masquerading enabled'}</option>
					<option value='off' $selected{'MASQUERADE_GREEN'}{'off'}>$Lang::tr{'masquerading disabled'}</option>
				</select>
			</td>
		</tr>
END

	if (&Header::orange_used()) {
		print <<END;
			<tr>
				<td align='left' width='60%'>$Lang::tr{'masquerade orange'}</td>
				<td>
					<select name='MASQUERADE_ORANGE'>
						<option value='on' $selected{'MASQUERADE_ORANGE'}{'on'}>$Lang::tr{'masquerading enabled'}</option>
						<option value='off' $selected{'MASQUERADE_ORANGE'}{'off'}>$Lang::tr{'masquerading disabled'}</option>
					</select>
				</td>
			</tr>
END
	}

	if (&Header::blue_used()) {
		print <<END;
			<tr>
				<td align='left' width='60%'>$Lang::tr{'masquerade blue'}</td>
				<td>
					<select name='MASQUERADE_BLUE'>
						<option value='on' $selected{'MASQUERADE_BLUE'}{'on'}>$Lang::tr{'masquerading enabled'}</option>
						<option value='off' $selected{'MASQUERADE_BLUE'}{'off'}>$Lang::tr{'masquerading disabled'}</option>
					</select>
				</td>
			</tr>
END
	}

	print <<END
	</table>

	<br>

<table width='95%' cellspacing='0'>
	<tr bgcolor='$color{'color20'}'>
		<td colspan='2' align='left'><b>$Lang::tr{'fw logging'}</b></td>
	</tr>
	<tr>
		<td align='left' width='60%'>$Lang::tr{'drop newnotsyn'}</td>
		<td align='left'>
			$Lang::tr{'on'} <input type='radio' name='DROPNEWNOTSYN' value='on' $checked{'DROPNEWNOTSYN'}{'on'} />/
			<input type='radio' name='DROPNEWNOTSYN' value='off' $checked{'DROPNEWNOTSYN'}{'off'} /> $Lang::tr{'off'}
		</td>
	</tr>
	<tr>
		<td align='left' width='60%'>$Lang::tr{'log dropped conntrack invalids'}</td>
		<td align='left'>
			$Lang::tr{'on'} <input type='radio' name='LOGDROPCTINVALID' value='on' $checked{'LOGDROPCTINVALID'}{'on'} />/
			<input type='radio' name='LOGDROPCTINVALID' value='off' $checked{'LOGDROPCTINVALID'}{'off'} /> $Lang::tr{'off'}
		</td>
	</tr>
	<tr>
		<td align='left' width='60%'>$Lang::tr{'drop input'}</td>
		<td align='left'>
			$Lang::tr{'on'} <input type='radio' name='DROPINPUT' value='on' $checked{'DROPINPUT'}{'on'} />/
			<input type='radio' name='DROPINPUT' value='off' $checked{'DROPINPUT'}{'off'} /> $Lang::tr{'off'}
		</td>
	</tr>
	<tr>
		<td align='left' width='60%'>$Lang::tr{'drop forward'}</td>
		<td align='left'>
			$Lang::tr{'on'} <input type='radio' name='DROPFORWARD' value='on' $checked{'DROPFORWARD'}{'on'} />/
			<input type='radio' name='DROPFORWARD' value='off' $checked{'DROPFORWARD'}{'off'} /> $Lang::tr{'off'}
		</td>
	</tr>
	<tr>
		<td align='left' width='60%'>$Lang::tr{'drop outgoing'}</td>
		<td align='left'>
			$Lang::tr{'on'} <input type='radio' name='DROPOUTGOING' value='on' $checked{'DROPOUTGOING'}{'on'} />/
			<input type='radio' name='DROPOUTGOING' value='off' $checked{'DROPOUTGOING'}{'off'} /> $Lang::tr{'off'}
		</td>
	</tr>
	<tr>
		<td align='left' width='60%'>$Lang::tr{'drop portscan'}</td>
		<td align='left'>
			$Lang::tr{'on'} <input type='radio' name='DROPPORTSCAN' value='on' $checked{'DROPPORTSCAN'}{'on'} />/
			<input type='radio' name='DROPPORTSCAN' value='off' $checked{'DROPPORTSCAN'}{'off'} /> $Lang::tr{'off'}
		</td>
	</tr>
	<tr>
		<td align='left' width='60%'>$Lang::tr{'drop wirelessinput'}</td>
		<td align='left'>
			$Lang::tr{'on'} <input type='radio' name='DROPWIRELESSINPUT' value='on' $checked{'DROPWIRELESSINPUT'}{'on'} />/
			<input type='radio' name='DROPWIRELESSINPUT' value='off' $checked{'DROPWIRELESSINPUT'}{'off'} /> $Lang::tr{'off'}
		</td>
	</tr>
	<tr>
		<td align='left' width='60%'>$Lang::tr{'drop wirelessforward'}</td>
		<td align='left'>
			$Lang::tr{'on'} <input type='radio' name='DROPWIRELESSFORWARD' value='on' $checked{'DROPWIRELESSFORWARD'}{'on'} />/
			<input type='radio' name='DROPWIRELESSFORWARD' value='off' $checked{'DROPWIRELESSFORWARD'}{'off'} /> $Lang::tr{'off'}
		</td>
	</tr>
	<tr>
		<td align='left' width='60%'>$Lang::tr{'drop spoofed martians'}</td>
		<td align='left'>
			$Lang::tr{'on'} <input type='radio' name='DROPSPOOFEDMARTIAN' value='on' $checked{'DROPSPOOFEDMARTIAN'}{'on'} />/
			<input type='radio' name='DROPSPOOFEDMARTIAN' value='off' $checked{'DROPSPOOFEDMARTIAN'}{'off'} /> $Lang::tr{'off'}
		</td>
	</tr>
</table>
<br/>

<table width='95%' cellspacing='0'>
	<tr bgcolor='$color{'color20'}'>
		<td colspan='2' align='left'><b>$Lang::tr{'fw red'}</b></td>
	</tr>
	<tr>
		<td align='left' width='60%'>$Lang::tr{'drop hostile'}</td>
		<td align='left'>
			$Lang::tr{'on'} <input type='radio' name='DROPHOSTILE' value='on' $checked{'DROPHOSTILE'}{'on'} />/
			<input type='radio' name='DROPHOSTILE' value='off' $checked{'DROPHOSTILE'}{'off'} /> $Lang::tr{'off'}
		</td>
	</tr>
</table>
<br>

<table width='95%' cellspacing='0'>
<tr bgcolor='$color{'color20'}'><td colspan='2' align='left'><b>$Lang::tr{'fw blue'}</b></td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'drop proxy'}</td><td align='left'>$Lang::tr{'on'} <input type='radio' name='DROPPROXY' value='on' $checked{'DROPPROXY'}{'on'} />/
																						<input type='radio' name='DROPPROXY' value='off' $checked{'DROPPROXY'}{'off'} /> $Lang::tr{'off'}</td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'drop samba'}</td><td align='left'>$Lang::tr{'on'} <input type='radio' name='DROPSAMBA' value='on' $checked{'DROPSAMBA'}{'on'} />/
																						<input type='radio' name='DROPSAMBA' value='off' $checked{'DROPSAMBA'}{'off'} /> $Lang::tr{'off'}</td></tr>
</table>
<br>
<table width='95%' cellspacing='0'>
<tr bgcolor='$color{'color20'}'><td colspan='2' align='left'><b>$Lang::tr{'fw settings'}</b></td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'fw settings color'}</td><td align='left'>$Lang::tr{'on'} <input type='radio' name='SHOWCOLORS' value='on' $checked{'SHOWCOLORS'}{'on'} />/
																						<input type='radio' name='SHOWCOLORS' value='off' $checked{'SHOWCOLORS'}{'off'} /> $Lang::tr{'off'}</td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'fw settings remark'}</td><td align='left'>$Lang::tr{'on'} <input type='radio' name='SHOWREMARK' value='on' $checked{'SHOWREMARK'}{'on'} />/
																						<input type='radio' name='SHOWREMARK' value='off' $checked{'SHOWREMARK'}{'off'} /> $Lang::tr{'off'}</td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'fw settings ruletable'}</td><td align='left'>$Lang::tr{'on'} <input type='radio' name='SHOWTABLES' value='on' $checked{'SHOWTABLES'}{'on'} />/
																						<input type='radio' name='SHOWTABLES' value='off' $checked{'SHOWTABLES'}{'off'} /> $Lang::tr{'off'}</td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'fw settings dropdown'}</td><td align='left'>$Lang::tr{'on'} <input type='radio' name='SHOWDROPDOWN' value='on' $checked{'SHOWDROPDOWN'}{'on'} />/
																						<input type='radio' name='SHOWDROPDOWN' value='off' $checked{'SHOWDROPDOWN'}{'off'} /> $Lang::tr{'off'}</td></tr>
</table>

<br />
<table width='95%' cellspacing='0'>
<tr bgcolor='$color{'color20'}'><td colspan='2' align='left'><b>$Lang::tr{'fw default drop'}</b></td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'drop action'}</td><td><select name='FWPOLICY'>
<option value='DROP' $selected{'FWPOLICY'}{'DROP'}>DROP</option>
<option value='REJECT' $selected{'FWPOLICY'}{'REJECT'}>REJECT</option></select>
</td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'drop action1'}</td><td><select name='FWPOLICY1'>
<option value='DROP' $selected{'FWPOLICY1'}{'DROP'}>DROP</option>
<option value='REJECT' $selected{'FWPOLICY1'}{'REJECT'}>REJECT</option></select>
</td></tr>
<tr><td align='left' width='60%'>$Lang::tr{'drop action2'}</td><td><select name='FWPOLICY2'>
<option value='DROP' $selected{'FWPOLICY2'}{'DROP'}>DROP</option>
<option value='REJECT' $selected{'FWPOLICY2'}{'REJECT'}>REJECT</option></select>
</td></tr>
</table>

<br />
<table width='100%' cellspacing='0'>
<tr><td align='right'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='submit' name='ACTION' value='$Lang::tr{'save'}' />
</form></td></tr>
</table>
</form>
END
;
&Header::closebox();

&Header::openbox('100%', 'center', $Lang::tr{'fwdfw pol title'});
	if ($fwdfwsettings{'POLICY'} eq 'MODE1'){ $selected{'POLICY'}{'MODE1'} = 'selected'; } else { $selected{'POLICY'}{'MODE1'} = ''; }
	if ($fwdfwsettings{'POLICY'} eq 'MODE2'){ $selected{'POLICY'}{'MODE2'} = 'selected'; } else { $selected{'POLICY'}{'MODE2'} = ''; }
	if ($fwdfwsettings{'POLICY1'} eq 'MODE1'){ $selected{'POLICY1'}{'MODE1'} = 'selected'; } else { $selected{'POLICY1'}{'MODE1'} = ''; }
	if ($fwdfwsettings{'POLICY1'} eq 'MODE2'){ $selected{'POLICY1'}{'MODE2'} = 'selected'; } else { $selected{'POLICY1'}{'MODE2'} = ''; }
print <<END;
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='100%' border='0'>
		<tr><td colspan='3' style='font-weight:bold;color:red;' align='left'>FORWARD </td></tr>
		<tr><td colspan='3' align='left'>$Lang::tr{'fwdfw pol text'}</td></tr>
		<tr><td colspan='3'><hr /></td></tr>
		<tr><td width='15%' align='left'>	<select name='POLICY' style="width: 100px">
		<option value='MODE1' $selected{'POLICY'}{'MODE1'}>$Lang::tr{'fwdfw pol block'}</option>
		<option value='MODE2' $selected{'POLICY'}{'MODE2'}>$Lang::tr{'fwdfw pol allow'}</option></select>
	    <input type='submit' name='ACTION' value='$Lang::tr{'save'}' /><input type='hidden' name='defpol' value='1'></td>
END
	print "</tr></table></form>";
	print"<br><br>";
	print <<END;
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='100%' border='0'>
		<tr><td colspan='3' style='font-weight:bold;color:red;' align='left'>OUTGOING </td></tr>
		<tr><td colspan='3' align='left'>$Lang::tr{'fwdfw pol text1'}</td></tr>
		<tr><td colspan='3'><hr /></td></tr>
		<tr><td width='15%' align='left'>	<select name='POLICY1' style="width: 100px">
		<option value='MODE1' $selected{'POLICY1'}{'MODE1'}>$Lang::tr{'fwdfw pol block'}</option>
		<option value='MODE2' $selected{'POLICY1'}{'MODE2'}>$Lang::tr{'fwdfw pol allow'}</option></select>
	    <input type='submit' name='ACTION' value='$Lang::tr{'save'}' /><input type='hidden' name='defpol' value='1'></td>
END
	print "</tr></table></form>";
	&Header::closebox();

&Header::closebigbox();
&Header::closepage();
