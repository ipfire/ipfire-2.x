#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007  Michael Tremer & Christian Schmidt                      #
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

my %dnssettings=();
my $errormessage = '';

&Header::showhttpheaders();

&General::readhash("${General::swroot}/dns/settings", \%dnssettings);

&Header::getcgihash(\%dnssettings);

&Header::openpage($Lang::tr{'dns title'}, 1, );

&Header::openbigbox('100%', 'left', '', $errormessage);

if ($dnssettings{'ACTION'} eq $Lang::tr{'save'}) {
	if ((&General::validip($dnssettings{"DNS0"}) == 1)&&(&General::validip($dnssettings{"DNS1"}) == 1)) {	
		if ($errormessage eq "") {
			&General::writehash("${General::swroot}/dns/settings", \%dnssettings);	
			&Header::openbox('100%', 'left', $Lang::tr{'dns saved'});								
			print "<font class='base'>$Lang::tr{'dns saved txt'}</font>\n";
			&Header::closebox();		
		}
	} else {
		if ((&General::validip($dnssettings{"DNS0"}) == 0)&&(&General::validip($dnssettings{"DNS1"}) == 1)){
			$errormessage = $Lang::tr{'dns error 0'};
		}		
		if ((&General::validip($dnssettings{"DNS1"}) == 0)&&(&General::validip($dnssettings{"DNS0"}) == 1)){
			$errormessage = $Lang::tr{'dns error 1'};
		}
		if ((&General::validip($dnssettings{"DNS1"}) == 0)&&(&General::validip($dnssettings{"DNS0"}) == 0)){
			$errormessage = $Lang::tr{'dns error 01'};
		}
	}
}

if ($dnssettings{'ACTION'} eq $Lang::tr{'reconnect'}) {
	system("/usr/local/bin/redctrl restart >/dev/null 2>&1 &");
	&Header::openbox('100%', 'left', $Lang::tr{'dns address recon'} );
	print "<font class='base'>$Lang::tr{'dns address done'}</font>\n";
	&Header::closebox();	
}

if ($dnssettings{'ACTION'} eq $Lang::tr{'delete'}) {
	system("cat /dev/null > ${General::swroot}/dns/settings &");
	&Header::openbox('100%', 'left', $Lang::tr{'dns address deleted'} );
	print "<font class='base'>$Lang::tr{'dns address deleted txt'}</font>\n";
	&Header::closebox();	
}

# DPC move error message to top so it is seen!
if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<font class='base'>$errormessage&nbsp;</font>\n";
	&Header::closebox();
}

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

&Header::openbox('100%', 'left', $Lang::tr{'dns header'});
print <<END

<table border="0"  width='100%'>
  <tr>
    <td colspan="2"><font class='base'>$Lang::tr{'dns desc'}<br /><img src="/images/dns_link.png" border="0" align="absmiddle"/><a href="http://wiki.ipfire.org/en/dns/public-servers" target="_blank">$Lang::tr{'dns list'}</a></font></td>
  </tr>
  <tr>
    <td colspan="2">&nbsp;</td>
  </tr>
  <tr>
    <td width="25%"><font class='base'>$Lang::tr{'dns new 0'}</font></td>
END
;     
if ($dnssettings{'ACTION'} eq $Lang::tr{'delete'}) {
print <<END    
    <td width="75%"><input type="text" name="DNS0" maxlength="15" value=""/></td>
END
; 
} else {   
print <<END
    <td width="75%"><input type="text" name="DNS0" maxlength="15" value="$dnssettings{"DNS0"}"/></td>
END
;  
}
print <<END
  </tr>
  <tr>
    <td><font class='base'>$Lang::tr{'dns new 1'}</font></td>
END
;     
if ($dnssettings{'ACTION'} eq $Lang::tr{'delete'}) {
print <<END
    <td><input type="text" name="DNS1" maxlength="15" value=""/></td>
END
; 
} else {   
print <<END
    <td><input type="text" name="DNS1" maxlength="15" value="$dnssettings{"DNS1"}"/></td>
END
; 
}
print <<END 
  </tr>
  <tr>
    <td colspan="2"><hr /></td>
  </tr>
  <tr>
    <td colspan="2"><div align="center">
END
;     
if ($dnssettings{'ACTION'} eq $Lang::tr{'save'} && $errormessage eq "") {
print <<END 	  
        <input type='submit' name='ACTION' value='$Lang::tr{'save'}' />
        &nbsp;&nbsp;&nbsp;&nbsp;
        <input type='submit' name='ACTION' value='$Lang::tr{'delete'}' />
        &nbsp;&nbsp;&nbsp;&nbsp;
        <input type='submit' name='ACTION' value='$Lang::tr{'reconnect'}' />
END
; 
} elsif ($dnssettings{'ACTION'} eq $Lang::tr{'delete'}) {
print <<END 	  
        <input type='submit' name='ACTION' value='$Lang::tr{'save'}' />
        &nbsp;&nbsp;&nbsp;&nbsp;
        <input type='submit' name='ACTION' value='$Lang::tr{'reconnect'}' />
END
;
} elsif ($dnssettings{'ACTION'} eq $Lang::tr{'save'}) {
print <<END 	  
        <input type='submit' name='ACTION' value='$Lang::tr{'save'}' />
END
; 
} else {   
print <<END
        <input type='submit' name='ACTION' value='$Lang::tr{'save'}' />
        &nbsp;&nbsp;&nbsp;&nbsp;
        <input type='submit' name='ACTION' value='$Lang::tr{'delete'}' />
END
;  
} 
print <<END     
        </div>
      </td>
  </tr>
</table>

END
;

&Header::closebox();

print "</form>\n";

&Header::closebigbox();

&Header::closepage();

