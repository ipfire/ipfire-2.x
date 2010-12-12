#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2005-2010  IPFire Team                                        #
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
require "${General::swroot}/graphs.pl";

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

my @querry = split(/\?/,$ENV{'QUERY_STRING'});
$querry[0] = '' unless defined $querry[0];
$querry[1] = 'hour' unless defined $querry[1];

if ( $querry[0] =~ "memory"){
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	&Graphs::updatememorygraph($querry[1]);
}elsif ( $querry[0] =~ "swap"){
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	&Graphs::updateswapgraph($querry[1]);
}else{
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'memory information'}, 1, '');
	&Header::openbigbox('100%', 'left');

	&Header::openbox('100%', 'center', "Memory $Lang::tr{'graph'}");
	&Graphs::makegraphbox("memory.cgi","memory","day");
	&Header::closebox();

	if ( `ls $mainsettings{'RRDLOG'}/collectd/localhost/swap 2>/dev/null` ) {
	    &Header::openbox('100%', 'center', "Swap $Lang::tr{'graph'}");
	    &Graphs::makegraphbox("memory.cgi","swap","day");
	    &Header::closebox();
	}
	
	&Header::openbox('100%', 'center', $Lang::tr{'memory'});
	print "<table width='95%' cellspacing='5'>";
	my $ram=0;
	my $size=0;
	my $used=0;
	my $free=0;
	my $percent=0;
	my $shared=0;
	my $buffers=0;
	my $cached=0;

	open(FREE,'/usr/bin/free |');
	while(<FREE>){
		if ($_ =~ m/^\s+total\s+used\s+free\s+shared\s+buffers\s+cached$/ ){
			print <<END
<tr>
<td align='center'>&nbsp;</td>
<td align='center' class='boldbase'><b>$Lang::tr{'size'}</b></td>
<td align='center' class='boldbase'><b>$Lang::tr{'used'}</b></td>
<td align='center' class='boldbase'><b>$Lang::tr{'free'}</b></td>
<td align='left' class='boldbase' colspan='2'><b>$Lang::tr{'percentage'}</b></td>
</tr>
END
;
		}else{
			if ($_ =~ m/^Mem:\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)$/){
				($ram,$size,$used,$free,$shared,$buffers,$cached) = ($1,$1,$2,$3,$4,$5,$6);
				($percent = ($used/$size)*100) =~ s/^(\d+)(\.\d+)?$/$1%/;
				print <<END
<tr>
<td class='boldbase'><b>$Lang::tr{'ram'}</b></td>
<td align='center'>$size  KB</td>
END
;
			}elsif($_ =~ m/^Swap:\s+(\d+)\s+(\d+)\s+(\d+)$/){
				($size,$used,$free) = ($1,$2,$3);
				if ($size != 0){
					($percent = ($used/$size)*100) =~ s/^(\d+)(\.\d+)?$/$1%/;
				}else{
					($percent = '');
				}
				print <<END
<tr>
<td class='boldbase'><b>$Lang::tr{'swap'}</b></td>
<td align='center'>$size  KB</td>
END
;
			}elsif($ram and $_ =~ m/^-\/\+ buffers\/cache:\s+(\d+)\s+(\d+)$/ ){
				($used,$free) = ($1,$2);
				($percent = ($used/$ram)*100) =~ s/^(\d+)(\.\d+)?$/$1%/;
				print "<tr><td colspan='2' class='boldbase'><b>$Lang::tr{'excluding buffers and cache'}</b></td>";
			}
			print <<END
<td align='center'>$used KB</td>
<td align='center'>$free KB</td>
<td>
END
;
			&percentbar($percent);
			print <<END
</td>
<td align='left'>$percent</td>
</tr>
END
;
		}
	}
	close FREE;
	print <<END
<tr><td class='boldbase' colspan='2'><br /></td></tr>
<tr><td class='boldbase'><b>$Lang::tr{'shared'}</b></td><td align='center'>$shared KB</td></tr>
<tr><td class='boldbase'><b>$Lang::tr{'buffers'}</b></td><td align='center'>$buffers KB</td></tr>
<tr><td class='boldbase'><b>$Lang::tr{'cached'}</b></td><td align='center'>$cached KB</td></tr>
</table>
END
;
	&Header::closebox();

	&Header::closebigbox();
	&Header::closepage();
}

sub percentbar{
	my $percent = $_[0];
	my $fg = '#a0a0a0';
	my $bg = '#e2e2e2';

	if ($percent =~ m/^(\d+)%$/ ){
		print <<END
<table width='100' border='1' cellspacing='0' cellpadding='0' style='border-width:1px;border-style:solid;border-color:$fg;width:100px;height:10px;'>
<tr>
END
;
		if ($percent eq "100%"){
			print "<td width='100%' bgcolor='$fg' style='background-color:$fg;border-style:solid;border-width:1px;border-color:$bg'>";
		}elsif($percent eq "0%"){
			print "<td width='100%' bgcolor='$bg' style='background-color:$bg;border-style:solid;border-width:1px;border-color:$bg'>";
		}else{
			print "<td width='$percent' bgcolor='$fg' style='background-color:$fg;border-style:solid;border-width:1px;border-color:$bg'></td><td width='" . (100-$1) . "%' bgcolor='$bg' style='background-color:$bg;border-style:solid;border-width:1px;border-color:$bg'>";
		}
		print <<END
<img src='/images/null.gif' width='1' height='1' alt='' /></td></tr></table>
END
;
	}
}
