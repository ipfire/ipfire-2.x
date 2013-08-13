#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2013 Alexander Marx <amarx@ipfire.org>                        #
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
no warnings 'uninitialized';
# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my $errormessage='';
my $p2pfile			= "${General::swroot}/forward/p2protocols";

my @p2ps = ();
my %fwdfwsettings=();
my %color=();
my %mainsettings=();

&General::readhash("${General::swroot}/forward/settings", \%fwdfwsettings);
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);



&Header::showhttpheaders();
&Header::getcgihash(\%fwdfwsettings);
&Header::openpage($Lang::tr{'fwdfw menu'}, 1, '');
&Header::openbigbox('100%', 'center',$errormessage);

if ($fwdfwsettings{'ACTION'} eq ''){
&p2pblock;
}
if ($fwdfwsettings{'ACTION'} eq 'togglep2p')
{
	open( FILE, "< $p2pfile" ) or die "Unable to read $p2pfile";
	@p2ps = <FILE>;
	close FILE;
	open( FILE, "> $p2pfile" ) or die "Unable to write $p2pfile";
	foreach my $p2pentry (sort @p2ps)
	{
		my @p2pline = split( /\;/, $p2pentry );
		if ($p2pline[1] eq $fwdfwsettings{'P2PROT'}) {
			if($p2pline[2] eq 'on'){
				$p2pline[2]='off';
			}else{
				$p2pline[2]='on';
			}
		}
		print FILE "$p2pline[0];$p2pline[1];$p2pline[2];\n";
	}
	close FILE;
	&rules;
	&p2pblock;
}
if ($fwdfwsettings{'ACTION'} eq $Lang::tr{'fwdfw reread'})
{
	&reread_rules;
	&p2pblock;
}


sub p2pblock
{
	if (-f "${General::swroot}/forward/reread"){
		print "<table border='0'><form method='post'><td><input type='submit' name='ACTION' value='$Lang::tr{'fwdfw reread'}' style='font-face: Comic Sans MS; color: red; font-weight: bold;'>$Lang::tr{'fwhost reread'}</td></tr></table></form><hr><br>";
	}
	my $gif;
	open( FILE, "< $p2pfile" ) or die "Unable to read $p2pfile";
	@p2ps = <FILE>;
	close FILE;
	&Header::openbox('100%', 'center', 'P2P-Block');
	print <<END;
	<table width='35%' border='0'>
	<tr bgcolor='$color{'color22'}'><td align=center colspan='2' ><b>$Lang::tr{'protocol'}</b></td><td align='center'><b>$Lang::tr{'status'}</b></td></tr>
END
	foreach my $p2pentry (sort @p2ps)
	{
		my @p2pline = split( /\;/, $p2pentry );
		if($p2pline[2] eq 'on'){
			$gif="/images/on.gif"
		}else{
			$gif="/images/off.gif"
		}
		print <<END;
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<tr bgcolor='$color{'color20'}'>
		<td align='center' colspan='2' >$p2pline[0]:</td><td align='center'><input type='hidden' name='P2PROT' value='$p2pline[1]' /><input type='image' img src='$gif' alt='$Lang::tr{'click to disable'}' title='$Lang::tr{'fwdfw toggle'}' style='padding-top: 0px; padding-left: 0px; padding-bottom: 0px ;padding-right: 0px ;display: block;' ><input type='hidden' name='ACTION' value='togglep2p'></td></tr></form>
END
	}
	print"<tr><td><img src='/images/on.gif'></td><td  align='left'>$Lang::tr{'outgoing firewall p2p allow'}</td></tr>";
	print"<tr><td><img src='/images/off.gif'></td><td align='left'>$Lang::tr{'outgoing firewall p2p deny'}</td></tr></table>";
	print"<br><br><br><table width='100%'><tr><td align='left'>$Lang::tr{'fwdfw p2p txt'}</td></tr></table>";
	&Header::closebox();
}
sub rules
{
	if (!-f "${General::swroot}/forward/reread"){
		system("touch ${General::swroot}/forward/reread");
		system("touch ${General::swroot}/fwhosts/reread");
	}
}
sub reread_rules
{
	system("/usr/local/bin/forwardfwctrl");
	if ( -f "${General::swroot}/forward/reread"){
		system("rm ${General::swroot}/forward/reread");
		system("rm ${General::swroot}/fwhosts/reread");
	}
}
&Header::closebigbox();
&Header::closepage();
