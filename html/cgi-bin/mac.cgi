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

my %macsettings=();
my $errormessage = '';

&Header::showhttpheaders();

&General::readhash("${General::swroot}/mac/settings", \%macsettings);

&Header::getcgihash(\%macsettings);

&Header::openpage($Lang::tr{'mac address title'}, 1, );

&Header::openbigbox('100%', 'left', '', $errormessage);

if ($macsettings{'ACTION'} eq $Lang::tr{'save'}) {
	$macsettings{'MAC'} =~ s/\-/:/g;
	my @mac = split(/:/,$macsettings{"MAC"});
	if ($#mac == 5) { 
		foreach (@mac) {
			unless ($_ =~ /^[a-fA-F0-9]{1,2}$/) {
					$errormessage = $Lang::tr{'mac address error not valid'};
					last;			
			}
		}
	} else {
		$errormessage = $Lang::tr{'mac address error not valid'};
	}
	$macsettings{'MAC1'} =~ s/\-/:/g;
	if ( not ($macsettings{'MAC1'} eq "" )) {
		my @mac = split(/:/,$macsettings{"MAC1"});
		if ($#mac == 5) { 
			foreach (@mac) {
				unless ($_ =~ /^[a-fA-F0-9]{1,2}$/) {
						$errormessage = $Lang::tr{'mac address error not valid'};
						last;			
				}
			}
		} else {
			$errormessage = $Lang::tr{'mac address error not valid'};
		}
	}
	$macsettings{'MAC2'} =~ s/\-/:/g;
	if ( not ($macsettings{'MAC2'} eq "" )) {
		my @mac = split(/:/,$macsettings{"MAC2"});
		if ($#mac == 5) { 
			foreach (@mac) {
				unless ($_ =~ /^[a-fA-F0-9]{1,2}$/) {
						$errormessage = $Lang::tr{'mac address error not valid'};
						last;			
				}
			}
		} else {
			$errormessage = $Lang::tr{'mac address error not valid'};
		}
	}
	if ($errormessage eq "") {
		$macsettings{'MAC'} =~ s/\:/-/g;
		$macsettings{'MAC1'} =~ s/\:/-/g;
		$macsettings{'MAC2'} =~ s/\:/-/g;
		&General::writehash("${General::swroot}/mac/settings", \%macsettings);	
		&Header::openbox('100%', 'left', $Lang::tr{'mac address saved'});								
		print "<font class='base'>$Lang::tr{'mac address saved txt'}</font>\n";
		&Header::closebox();
	}
}
if ($macsettings{'ACTION'} eq $Lang::tr{'reconnect'}) {
	system("/usr/local/bin/redctrl restart >/dev/null 2>&1 &");
	&Header::openbox('100%', 'left', $Lang::tr{'mac address recon'} );
	print "<font class='base'>$Lang::tr{'mac address done'}</font>\n";
	&Header::closebox();	
}
if ($macsettings{'ACTION'} eq $Lang::tr{'delete'} ) {
	system("cat /dev/null > ${General::swroot}/mac/settings &");
	&Header::openbox('100%', 'left', $Lang::tr{'mac address deleted'} );
	print "<font class='base'>$Lang::tr{'mac address deleted txt'}</font>\n";
	&Header::closebox();	
}
if ($macsettings{'ACTION'} eq $Lang::tr{'reboot'}) {
	&General::log($Lang::tr{'rebooting ipfire'});
	system("/usr/local/bin/ipfirereboot boot");
	&Header::openbox('100%', 'left', $Lang::tr{'rebooting ipfire'} );
	print "&nbsp;&nbsp;<img src='/images/indicator.gif' /><br /><br />";
	print "<meta http-equiv='refresh' content='120;'>";
	&Header::closebox();
}

# DPC move error message to top so it is seen!
if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<font class='base'>$errormessage&nbsp;</font>\n";
	&Header::closebox();
}

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

&Header::openbox('100%', 'left', $Lang::tr{'mac address header'});
print <<END

<table border="0"  width='100%'>
  <tr>
    <td colspan="2"><font class='base'>$Lang::tr{'mac desc'}</font></td>
  </tr>
  <tr>
    <td colspan="2">&nbsp;</td>
  </tr>
  <tr>
    <td width="25%"><font class='base'>$Lang::tr{'mac new'}&nbsp;<img src='/blob.gif' alt='*' /></font></td><td>
END
;
if ($macsettings{'ACTION'} eq $Lang::tr{'delete'} ) {
print <<END 
      <input type="text" name="MAC" maxlength="17" value=''/></td>
END
;
} else {   
print <<END
      <input type="text" name="MAC" maxlength="17" value='$macsettings{"MAC"}'/></td>
END
;  
} 
print <<END    
  </tr>
    <tr>
    <td>&nbsp;</td>
  </tr>
  <tr>
    <td><font class='base'>$Lang::tr{'mac1 new'}&nbsp;</font></td><td>
END
;
if ($macsettings{'ACTION'} eq $Lang::tr{'delete'} ) {
print <<END 
      <input type="text" name="MAC1" maxlength="17" value=''/></td>
END
;
} else {   
print <<END
      <input type="text" name="MAC1" maxlength="17" value='$macsettings{"MAC1"}'/></td>
END
;  
} 
print <<END    
  </tr>
    <tr>
    <td>&nbsp;</td>
  </tr>
  <tr>
    <td><font class='base'>$Lang::tr{'mac2 new'}&nbsp;</font></td><td>
END
;
if ($macsettings{'ACTION'} eq $Lang::tr{'delete'} ) {
print <<END 
      <input type="text" name="MAC2" maxlength="17" value=''/></td>
END
;
} else {   
print <<END
      <input type="text" name="MAC2" maxlength="17" value='$macsettings{"MAC2"}'/></td>
END
;  
} 

print <<END    
  </tr>
    <tr>
    <td colspan="2"><br><hr /></td>
  </tr>
  <tr>
    <td align='left'><img src='/blob.gif' alt='*' />&nbsp;$Lang::tr{'required field'}</td><div align="right"></td>
    <td align='right'>
END
;
if ($macsettings{'ACTION'} eq $Lang::tr{'delete'} ) {
print <<END
      <input type='submit' name='ACTION' value='$Lang::tr{'save'}' />
      &nbsp;&nbsp;&nbsp;&nbsp;
      <input type='submit' name='ACTION' value='$Lang::tr{'delete'}' />
      &nbsp;&nbsp;&nbsp;&nbsp;
      <input type='submit' name='ACTION' value='$Lang::tr{'reboot'}' />
END
;
} elsif ($macsettings{'ACTION'} eq $Lang::tr{'save'} && $errormessage eq "") {	
print <<END
      <input type='submit' name='ACTION' value='$Lang::tr{'save'}' />
      &nbsp;&nbsp;&nbsp;&nbsp;
      <input type='submit' name='ACTION' value='$Lang::tr{'delete'}' />
      &nbsp;&nbsp;&nbsp;&nbsp;
      <input type='submit' name='ACTION' value='$Lang::tr{'reconnect'}' />
END
;
} elsif ($macsettings{'ACTION'} eq $Lang::tr{'save'}) {	
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
    </div></td>
  </tr>
</table>

END
;
&Header::closebox();

print "</form>\n";

&Header::closebigbox();

&Header::closepage();

