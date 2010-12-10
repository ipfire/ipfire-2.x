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

my %outgrpsettings = ();
my %netsettings = ();
my %selected= () ;
my $errormessage = "";

my $configpath = "/var/ipfire/outgoing/groups/";
my $servicefile = "/var/ipfire/outgoing/defaultservices";

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

&Header::showhttpheaders();

### Values that have to be initialized
$outgrpsettings{'ACTION'} = '';
$outgrpsettings{'ipgroup'} = 'none';
$outgrpsettings{'macgroup'} = 'none';

&Header::getcgihash(\%outgrpsettings);
delete $outgrpsettings{'__CGI__'};delete $outgrpsettings{'x'};delete $outgrpsettings{'y'};

$selected{'ipgroup'}{$outgrpsettings{'ipgroup'}} = "selected='selected'";
$selected{'macgroup'}{$outgrpsettings{'macgroup'}} = "selected='selected'";

&Header::openpage($Lang::tr{'outgoing firewall groups'}, 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

###############
# DEBUG DEBUG
# &Header::openbox('100%', 'left', 'DEBUG');
# my $debugCount = 0;
# foreach my $line (sort keys %outgrpsettings) {
# print "$line = $outgrpsettings{$line}<br />\n";
# $debugCount++;
# }
# print "Count: $debugCount\n";
# &Header::closebox();
# DEBUG DEBUG
###############

############################################################################################################################
############################################################################################################################

if ($outgrpsettings{'ACTION'} eq 'newipgroup')
{
	&newipgroup();
}elsif ($outgrpsettings{'ACTION'} eq 'editipgroup')
{
	&editipgroup();
} elsif ($outgrpsettings{'ACTION'} eq 'deleteipgroup' ) {
	unlink("$configpath/ipgroups/$outgrpsettings{'ipgroup'}");
} elsif ($outgrpsettings{'ACTION'} eq 'addipgroup') {

	if ( -e "$configpath/macgroups/$outgrpsettings{'ipgroup'}" ){
		$errormessage =  "$Lang::tr{'outgoing firewall group error'}";
	} elsif ( $outgrpsettings{'ipgroup'} eq "all" || $outgrpsettings{'ipgroup'} eq "red" || $outgrpsettings{'ipgroup'} eq "blue" ||
			$outgrpsettings{'ipgroup'} eq "green" || $outgrpsettings{'ipgroup'} eq "orange" || $outgrpsettings{'ipgroup'} eq "ip" ||
			$outgrpsettings{'ipgroup'} eq "mac" || $outgrpsettings{'ipgroup'} eq "ovpn" || $outgrpsettings{'ipgroup'} eq "ipsec" ) {
		$errormessage =  "$Lang::tr{'outgoing firewall reserved groupname'}";
	} else {
		open (FILE, ">$configpath/ipgroups/$outgrpsettings{'ipgroup'}") or die "Can't save $outgrpsettings{'ipgroup'} settings $!";
		$outgrpsettings{'ipgroupcontent'} =~ s/\s*$//;
		flock (FILE, 2);
		print FILE $outgrpsettings{'ipgroupcontent'}."\n";
		close FILE;
	}
}

if ($outgrpsettings{'ACTION'} eq 'newmacgroup')
{
	&newmacgroup();
}elsif ($outgrpsettings{'ACTION'} eq 'editmacgroup')
{
	&editmacgroup();
}elsif ($outgrpsettings{'ACTION'} eq 'deletemacgroup' ) {
	unlink("$configpath/macgroups/$outgrpsettings{'macgroup'}");
} elsif ($outgrpsettings{'ACTION'} eq 'addmacgroup') {

	if ( -e "$configpath/ipgroups/$outgrpsettings{'macgroup'}" ){
		$errormessage =  "$Lang::tr{'outgoing firewall group error'}";
	} elsif ( $outgrpsettings{'macgroup'} eq "all" || $outgrpsettings{'macgroup'} eq "red" || $outgrpsettings{'macgroup'} eq "blue" ||
			$outgrpsettings{'macgroup'} eq "green" || $outgrpsettings{'macgroup'} eq "orange" || $outgrpsettings{'macgroup'} eq "ip" ||
			$outgrpsettings{'macgroup'} eq "mac" || $outgrpsettings{'macgroup'} eq "ovpn" || $outgrpsettings{'macgroup'} eq "ipsec" ) {
		$errormessage =  "$Lang::tr{'outgoing firewall reserved groupname'}";
	} else {
		open (FILE, ">$configpath/macgroups/$outgrpsettings{'macgroup'}") or die "Can't save $outgrpsettings{'macgroup'} settings $!";
		$outgrpsettings{'macgroupcontent'} =~ s/\s*$//;
		flock (FILE, 2);
		print FILE $outgrpsettings{'macgroupcontent'}."\n";
		close FILE;
	}
}

if ($errormessage)
{
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'><font color=red>$errormessage\n</font>";
	print "&nbsp;</class>\n";
	&Header::closebox();
}

############################################################################################################################
############################################################################################################################

my @ipgroups = qx(ls $configpath/ipgroups/);
if ($outgrpsettings{'ipgroup'} eq "none" and $#ipgroups >= 0 ){ $outgrpsettings{'ipgroup'} = $ipgroups[0];}

my $ipgroupcontent = `cat $configpath/ipgroups/$outgrpsettings{'ipgroup'} 2>/dev/null`;
$ipgroupcontent =~ s/\n/<br \/>/g;

&Header::openbox('100%', 'center', $Lang::tr{'outgoing firewall ip groups'});

print <<END
<a name="outgoing showipgroup"></a>
<br />
<form method='post' action='$ENV{'SCRIPT_NAME'}#outgoing showipgroup'>
<table width='95%' cellspacing='0'>
	<tr>
		<td bgcolor='$color{'color20'}' colspan='3' align='left'><b>$Lang::tr{'outgoing firewall ip groups'}</b></td>
	</tr>
	<tr>
		<td colspan='3'  align='left'><br /></td>
	</tr>
	<tr>
		<td  align='left' colspan='2'><select name='ipgroup' style="width: 200px">
END
;
foreach my $member (@ipgroups) {chomp $member;print"			<option value='$member' $selected{'ipgroup'}{$member}>$member</option>\n";}
print <<END
		</select></td>
		<td  align='left'>
				<input type='hidden' name='ACTION' value='showipgroup' />
				<input type='image' alt='$Lang::tr{'outgoing firewall view group'}' title='$Lang::tr{'outgoing firewall view group'}' src='/images/format-justify-fill.png' />
		</td>
	</tr>
	<tr>
		<td colspan='3' align='left'><br /></td>
	</tr>
	<tr>
		<td colspan='3' align='left'><font size=1>$ipgroupcontent</font></td>
	</tr>
	<tr>
		<td colspan='3' align='left'><br /></td>
	</tr>
	<tr>
		<td colspan='3' align='center'><font size=1>$Lang::tr{'outgoing firewall ip groups'} - $outgrpsettings{'ipgroup'}</font></td>
	</tr>
</table>
</form>
<table width='10%' cellspacing='0'>
<tr>
	<td align='center'>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='ACTION' value='editipgroup' />
			<input type='hidden' name='ipgroup' value='$outgrpsettings{'ipgroup'}' />
			<input type='image' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' src='/images/edit.gif' />
		</form>
	</td>
	<td align='center'>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='ACTION' value='newipgroup' />
			<input type='image' alt='$Lang::tr{'new'}' title='$Lang::tr{'new'}' src='/images/list-add.png' />
		</form>
	</td>
	<td align='center'>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='ACTION' value='saveipgroup' />
			<input type='hidden' name='ipgroup' value='$outgrpsettings{'ipgroup'}' />
			<input type='image' alt='$Lang::tr{'save'}' title='$Lang::tr{'save'}' src='/images/media-floppy.png' />
		</form>
	</td>
	<td align='center'>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='ACTION' value='deleteipgroup' />
			<input type='hidden' name='ipgroup' value='$outgrpsettings{'ipgroup'}' />
			<input type='image' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' src='/images/user-trash.png' />
		</form>
	</td>
</tr>
</table>

END
;
&Header::closebox();

############################################################################################################################
############################################################################################################################

my @macgroups = qx(ls $configpath/macgroups/);
if ($outgrpsettings{'macgroup'} eq "none" and $#macgroups >= 0 ){ $outgrpsettings{'macgroup'} = $macgroups[0];}

my $macgroupcontent = `cat $configpath/macgroups/$outgrpsettings{'macgroup'} 2>/dev/null`;
$macgroupcontent =~ s/\n/<br \/>/g;

&Header::openbox('100%', 'center', $Lang::tr{'outgoing firewall mac groups'});

print <<END
<a name="outgoing showmacgroup"></a>
<br />
<form method='post' action='$ENV{'SCRIPT_NAME'}#outgoing showmacgroup'>
<table width='95%' cellspacing='0'>
	<tr>
		<td bgcolor='$color{'color20'}' colspan='3' align='left'><b>$Lang::tr{'outgoing firewall mac groups'}</b></td>
	</tr>
	<tr>
		<td colspan='3'  align='left'><br /></td>
	</tr>
	<tr>
		<td  align='left' colspan='2'><select name='macgroup' style="width: 200px">
END
;
foreach my $member (@macgroups) {chomp $member;print"			<option value='$member' $selected{'macgroup'}{$member}>$member</option>\n";}
print <<END
		</select></td>
		<td  align='left'>
				<input type='hidden' name='ACTION' value='showmacgroup' />
				<input type='image' alt='$Lang::tr{'outgoing firewall view group'}' title='$Lang::tr{'outgoing firewall view group'}' src='/images/format-justify-fill.png' />
		</td>
	</tr>
	<tr>
		<td colspan='3' align='left'><br /></td>
	</tr>
	<tr>
		<td colspan='3' align='left'><font size=1>$macgroupcontent</font></td>
	</tr>
	<tr>
		<td colspan='3' align='left'><br /></td>
	</tr>
	<tr>
		<td colspan='3' align='center'><font size=1>$Lang::tr{'outgoing firewall mac groups'} - $outgrpsettings{'macgroup'}</font></td>
	</tr>
</table>
</form>
<table width='10%' cellspacing='0'>
<tr>
	<td align='center'>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='ACTION' value='editmacgroup' />
			<input type='hidden' name='macgroup' value='$outgrpsettings{'macgroup'}' />
			<input type='image' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' src='/images/edit.gif' />
		</form>
	</td>
	<td align='center'>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='ACTION' value='newmacgroup' />
			<input type='image' alt='$Lang::tr{'new'}' title='$Lang::tr{'new'}' src='/images/list-add.png' />
		</form>
	</td>
	<td align='center'>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='ACTION' value='savemacgroup' />
			<input type='hidden' name='macgroup' value='$outgrpsettings{'macgroup'}' />
			<input type='image' alt='$Lang::tr{'save'}' title='$Lang::tr{'save'}' src='/images/media-floppy.png' />
		</form>
	</td>
	<td align='center'>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='ACTION' value='deletemacgroup' />
			<input type='hidden' name='macgroup' value='$outgrpsettings{'macgroup'}' />
			<input type='image' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' src='/images/user-trash.png' />
		</form>
	</td>
</tr>
</table>

END
;
&Header::closebox();

&Header::closebigbox();
&Header::closepage();


############################################################################################################################
############################################################################################################################


sub newipgroup
{
	&Header::openbox('100%', 'center', $Lang::tr{'outgoing firewall add ip group'});

print <<END
	<form method='post' action='$ENV{'SCRIPT_NAME'}#outgoing showipgroup'>
	<table width='95%' cellspacing='0'>
		<tr>
			<td bgcolor='$color{'color20'}' colspan='3' align='left'><b>$Lang::tr{'outgoing firewall add ip group'}</b></td>
		</tr>
		<tr>
			<td colspan='3'  align='left'><br /></td>
		</tr>
		<tr>
			<td  align='left' colspan='2'>
				<input type='text' name='ipgroup' value='newipgroup' size="30" />
			</td>
			<td  align='left'>
				<input type='hidden' name='ACTION' value='addipgroup' />
				<input type='image' alt='$Lang::tr{'save'}' title='$Lang::tr{'save'}' src='/images/media-floppy.png' />
			</td>
		</tr>
		<tr>
			<td  align='left' colspan='3'>
				<textarea name="ipgroupcontent" cols="40" rows="5" Wrap="off">192.168.1.0/24\n192.168.3.0/255.255.255.0\n192.168.0.1\n192.168.0.2\n</textarea>
			</td>
		</tr>
	</table>
	</form>
END
;
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit 0;
}

sub editipgroup
{
my $ipgroupcontent = `cat $configpath/ipgroups/$outgrpsettings{'ipgroup'} 2>/dev/null`;

	&Header::openbox('100%', 'center', $Lang::tr{'outgoing firewall edit ip group'});

print <<END
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='95%' cellspacing='0'>
		<tr>
			<td bgcolor='$color{'color20'}' colspan='3' align='left'><b>$Lang::tr{'outgoing firewall edit ip group'}</b></td>
		</tr>
		<tr>
			<td colspan='3'  align='left'><br /></td>
		</tr>
		<tr>
			<td  align='left' colspan='2'>
				<input type='text' name='ipgroup' value='$outgrpsettings{'ipgroup'}' size='30' readonly style='color:$color{'color20'}'/>
			</td>
			<td  align='left'>
				<input type='hidden' name='ACTION' value='addipgroup' />
				<input type='image' alt='$Lang::tr{'save'}' title='$Lang::tr{'save'}' src='/images/media-floppy.png' />
			</td>
		</tr>
		<tr>
			<td  align='left' colspan='3'>
				<textarea name="ipgroupcontent" cols="40" rows="5" Wrap="off">$ipgroupcontent</textarea>
			</td>
		</tr>
	</table>
	</form>
END
;
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit 0;
}

sub newmacgroup
{
	&Header::openbox('100%', 'center', $Lang::tr{'outgoing firewall add mac group'});

print <<END
	<form method='post' action='$ENV{'SCRIPT_NAME'}#outgoing showmacgroup'>
	<table width='95%' cellspacing='0'>
		<tr>
			<td bgcolor='$color{'color20'}' colspan='3' align='left'><b>$Lang::tr{'outgoing firewall add mac group'}</b></td>
		</tr>
		<tr>
			<td colspan='3'  align='left'><br /></td>
		</tr>
		<tr>
			<td  align='left' colspan='2'>
				<input type='text' name='macgroup' value='newmacgroup' size="30" />
			</td>
			<td  align='left'>
				<input type='hidden' name='ACTION' value='addmacgroup' />
				<input type='image' alt='$Lang::tr{'save'}' title='$Lang::tr{'save'}' src='/images/media-floppy.png' />
			</td>
		</tr>
		<tr>
			<td  align='left' colspan='3'>
				<textarea name="macgroupcontent" cols="20" rows="5" Wrap="off">00:24:F6:04:5F:2b\n14:26:36:5A:5F:2B\n</textarea>
			</td>
		</tr>
	</table>
	</form>
END
;
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit 0;
}

sub editmacgroup
{
my $macgroupcontent = `cat $configpath/macgroups/$outgrpsettings{'macgroup'} 2>/dev/null`;

	&Header::openbox('100%', 'center', $Lang::tr{'outgoing firewall edit mac group'});

print <<END
	<form method='post' action='$ENV{'SCRIPT_NAME'}#outgoing editmacgroup'>
	<table width='95%' cellspacing='0'>
		<tr>
			<td bgcolor='$color{'color20'}' colspan='3' align='left'><b>$Lang::tr{'outgoing firewall edit mac group'}</b></td>
		</tr>
		<tr>
			<td colspan='3'  align='left'><br /></td>
		</tr>
		<tr>
			<td  align='left' colspan='2'>
				<input type='text' name='macgroup' value='$outgrpsettings{'macgroup'}' size='30' readonly style='color:$color{'color20'}'/>
			</td>
			<td  align='left'>
				<input type='hidden' name='ACTION' value='addmacgroup' />
				<input type='image' alt='$Lang::tr{'save'}' title='$Lang::tr{'save'}' src='/images/media-floppy.png' />
			</td>
		</tr>
		<tr>
			<td  align='left' colspan='3'>
				<textarea name="macgroupcontent" cols="20" rows="5" Wrap="off">$macgroupcontent</textarea>
			</td>
		</tr>
	</table>
	</form>
END
;
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit 0;
}
