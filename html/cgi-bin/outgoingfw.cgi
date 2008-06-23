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

my %outfwsettings = ();
my %checked = ();
my %selected= () ;
my %netsettings = ();
my $errormessage = "";
my $configentry = "";
my @configs = ();
my @configline = ();
my $p2pentry = "";
my @p2ps = ();
my @p2pline = ();

my $configfile = "/var/ipfire/outgoing/rules";
my $p2pfile = "/var/ipfire/outgoing/p2protocols";
my $servicefile = "/var/ipfire/outgoing/defaultservices";

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

&Header::showhttpheaders();

### Values that have to be initialized
$outfwsettings{'ACTION'} = '';
$outfwsettings{'VALID'} = 'yes';
$outfwsettings{'EDIT'} = 'no';
$outfwsettings{'NAME'} = '';
$outfwsettings{'SNET'} = '';
$outfwsettings{'SIP'} = '';
$outfwsettings{'SPORT'} = '';
$outfwsettings{'SMAC'} = '';
$outfwsettings{'DIP'} = '';
$outfwsettings{'DPORT'} = '';
$outfwsettings{'PROT'} = '';
$outfwsettings{'STATE'} = '';
$outfwsettings{'DISPLAY_DIP'} = '';
$outfwsettings{'DISPLAY_DPORT'} = '';
$outfwsettings{'DISPLAY_SMAC'} = '';
$outfwsettings{'DISPLAY_SIP'} = '';
$outfwsettings{'POLICY'} = 'MODE0';
$outfwsettings{'MODE1LOG'} = 'off';

&General::readhash("${General::swroot}/outgoing/settings", \%outfwsettings);
&Header::getcgihash(\%outfwsettings);

$checked{'MODE1LOG'}{'off'} = '';
$checked{'MODE1LOG'}{'on'} = '';
$checked{'MODE1LOG'}{$outfwsettings{'MODE1LOG'}} = "checked='checked'";

if ($outfwsettings{'POLICY'} eq 'MODE0'){ $selected{'POLICY'}{'MODE0'} = 'selected'; } else { $selected{'POLICY'}{'MODE0'} = ''; }
if ($outfwsettings{'POLICY'} eq 'MODE1'){ $selected{'POLICY'}{'MODE1'} = 'selected'; } else { $selected{'POLICY'}{'MODE1'} = ''; }
if ($outfwsettings{'POLICY'} eq 'MODE2'){ $selected{'POLICY'}{'MODE2'} = 'selected'; } else { $selected{'POLICY'}{'MODE2'} = ''; }

&Header::openpage('Ausgehende Firewall', 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
############################################################################################################################

if ($outfwsettings{'ACTION'} eq $Lang::tr{'reset'})
{
	$outfwsettings{'POLICY'}='MODE0';
	unlink $configfile;
	system("/usr/bin/touch $configfile");
	my $MODE = $outfwsettings{'POLICY'};
	%outfwsettings = ();
	$outfwsettings{'POLICY'} = "$MODE";
	&General::writehash("${General::swroot}/outgoing/settings", \%outfwsettings);
}
if ($outfwsettings{'ACTION'} eq $Lang::tr{'save'})
{
	my $MODE = $outfwsettings{'POLICY'};
	my $MODE1LOG = $outfwsettings{'MODE1LOG'};
	%outfwsettings = ();
	$outfwsettings{'POLICY'} = "$MODE";
	$outfwsettings{'MODE1LOG'} = "$MODE1LOG";
	&General::writehash("${General::swroot}/outgoing/settings", \%outfwsettings);
	system("/usr/local/bin/outgoingfwctrl");
}
if ($outfwsettings{'ACTION'} eq 'enable')
{
	open( FILE, "< $p2pfile" ) or die "Unable to read $p2pfile";
	@p2ps = <FILE>;
	close FILE;
	open( FILE, "> $p2pfile" ) or die "Unable to write $p2pfile";
	foreach $p2pentry (sort @p2ps)
	{
		@p2pline = split( /\;/, $p2pentry );
		if ($p2pline[1] eq $outfwsettings{'P2PROT'}) {
			print FILE "$p2pline[0];$p2pline[1];on;\n";
		} else {
			print FILE "$p2pline[0];$p2pline[1];$p2pline[2];\n";
		}
	}
	close FILE;
	system("/usr/local/bin/outgoingfwctrl");
}
if ($outfwsettings{'ACTION'} eq 'disable')
{
	open( FILE, "< $p2pfile" ) or die "Unable to read $p2pfile";
	@p2ps = <FILE>;
	close FILE;
	open( FILE, "> $p2pfile" ) or die "Unable to write $p2pfile";
	foreach $p2pentry (sort @p2ps)
	{
		@p2pline = split( /\;/, $p2pentry );
		if ($p2pline[1] eq $outfwsettings{'P2PROT'}) {
			print FILE "$p2pline[0];$p2pline[1];off;\n";
		} else {
			print FILE "$p2pline[0];$p2pline[1];$p2pline[2];\n";
		}
	}
	close FILE;
	system("/usr/local/bin/outgoingfwctrl");
}
if ($outfwsettings{'ACTION'} eq $Lang::tr{'edit'})
{
	open( FILE, "< $configfile" ) or die "Unable to read $configfile";
	@configs = <FILE>;
	close FILE;
	open( FILE, "> $configfile" ) or die "Unable to write $configfile";
	foreach $configentry (sort @configs)
	{
		@configline = split( /\;/, $configentry );
  		unless	(($configline[0] eq $outfwsettings{'STATE'}) && 
			($configline[1] eq $outfwsettings{'ENABLED'}) && 
			($configline[2] eq $outfwsettings{'SNET'}) && 
			($configline[3] eq $outfwsettings{'PROT'}) && 
			($configline[4] eq $outfwsettings{'NAME'}) && 
			($configline[5] eq $outfwsettings{'SIP'}) && 
			($configline[6] eq $outfwsettings{'SMAC'}) && 
			($configline[7] eq $outfwsettings{'DIP'}) &&
			($configline[9] eq $outfwsettings{'LOG'}) &&       
			($configline[8] eq $outfwsettings{'DPORT'}))
  		{
			print FILE $configentry;
		}
	}
	close FILE;
	$selected{'SNET'}{"$outfwsettings{'SNET'}"} = 'selected';
	$selected{'PROT'}{"$outfwsettings{'PROT'}"} = 'selected';
	$selected{'LOG'}{"$outfwsettings{'LOG'}"} = 'selected';
	&addrule();
	&Header::closebigbox();
	&Header::closepage();
	exit
  system("/usr/local/bin/outgoingfwctrl");	
}
if ($outfwsettings{'ACTION'} eq $Lang::tr{'delete'})
{
	open( FILE, "< $configfile" ) or die "Unable to read $configfile";
	@configs = <FILE>;
	close FILE;
	open( FILE, "> $configfile" ) or die "Unable to write $configfile";
	foreach $configentry (sort @configs)
	{
		@configline = split( /\;/, $configentry );
  		unless	(($configline[0] eq $outfwsettings{'STATE'}) && 
			($configline[1] eq $outfwsettings{'ENABLED'}) && 
			($configline[2] eq $outfwsettings{'SNET'}) && 
			($configline[3] eq $outfwsettings{'PROT'}) && 
			($configline[4] eq $outfwsettings{'NAME'}) && 
			($configline[5] eq $outfwsettings{'SIP'}) && 
			($configline[6] eq $outfwsettings{'SMAC'}) && 
			($configline[7] eq $outfwsettings{'DIP'}) && 
			($configline[9] eq $outfwsettings{'LOG'}) &&
			($configline[8] eq $outfwsettings{'DPORT'}))
  		{
			print FILE $configentry;
		}
	}
	close FILE;
	system("/usr/local/bin/outgoingfwctrl");
}
if ($outfwsettings{'ACTION'} eq $Lang::tr{'add'})
{
	if ( $outfwsettings{'VALID'} eq 'yes' ) {
		open( FILE, ">> $configfile" ) or die "Unable to write $configfile";
		print FILE <<END
$outfwsettings{'STATE'};$outfwsettings{'ENABLED'};$outfwsettings{'SNET'};$outfwsettings{'PROT'};$outfwsettings{'NAME'};$outfwsettings{'SIP'};$outfwsettings{'SMAC'};$outfwsettings{'DIP'};$outfwsettings{'DPORT'};$outfwsettings{'LOG'};
END
;
		close FILE;
		system("/usr/local/bin/outgoingfwctrl");
	} else {
		$outfwsettings{'ACTION'} = 'Add rule';
	}
}
if ($outfwsettings{'ACTION'} eq 'Add rule')
{
	&addrule();
	exit
}

&General::readhash("${General::swroot}/outgoing/settings", \%outfwsettings);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
}

############################################################################################################################
############################################################################################################################

if ($outfwsettings{'POLICY'} ne 'MODE0'){
	&Header::openbox('100%', 'center', 'Rules');
		print <<END
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type='submit' name='ACTION' value='Add rule' />
	</form>
END
;
	open( FILE, "< $configfile" ) or die "Unable to read $configfile";
	@configs = <FILE>;
	close FILE;
	if (@configs) {
		print <<END
		<hr />
		<table border='0' width='100%' cellspacing='0'>
		<tr bgcolor='$color{'color22'}'>
		    <td width='14%' align='center'><b>$Lang::tr{'protocol'}</b></td>
		    <td width='14%' align='center'><b>$Lang::tr{'network'}</b></td>
		    <td width='14%' align='center'><b>$Lang::tr{'destination'}</b></td>
		    <td width='14%' align='center'><b>$Lang::tr{'description'}</b></td>
		    <td width='14%' align='center'><b>$Lang::tr{'policy'}</b></td>
		    <td width='16%' align='center'><b>$Lang::tr{'logging'}</b></td>
		    <td width='14%' align='center'><b>$Lang::tr{'action'}</b></td>
END
;
		foreach $configentry (sort @configs)
		  	{
		  		@configline = split( /\;/, $configentry );
				$outfwsettings{'STATE'} = $configline[0];
				$outfwsettings{'ENABLED'} = $configline[1];
				$outfwsettings{'SNET'} = $configline[2];
				$outfwsettings{'PROT'} = $configline[3];
				$outfwsettings{'NAME'} = $configline[4];
				$outfwsettings{'SIP'} = $configline[5];
				$outfwsettings{'SMAC'} = $configline[6];
				$outfwsettings{'DIP'} = $configline[7];
				$outfwsettings{'DPORT'} = $configline[8];
				$outfwsettings{'LOG'} = $configline[9];
				if ($outfwsettings{'DIP'} eq ''){ $outfwsettings{'DISPLAY_DIP'} = 'ALL'; } else { $outfwsettings{'DISPLAY_DIP'} = $outfwsettings{'DIP'}; }
				if ($outfwsettings{'DPORT'} eq ''){ $outfwsettings{'DISPLAY_DPORT'} = 'ALL'; } else { $outfwsettings{'DISPLAY_DPORT'} = $outfwsettings{'DPORT'}; }
				if ($outfwsettings{'STATE'} eq 'DENY'){ $outfwsettings{'DISPLAY_STATE'} = "<img src='/images/stock_stop.png' alt='DENY' />"; }
				if ($outfwsettings{'STATE'} eq 'ALLOW'){ $outfwsettings{'DISPLAY_STATE'} = "<img src='/images/stock_ok.png' alt='ALLOW' />"; }
				if ((($outfwsettings{'POLICY'} eq 'MODE1') && ($outfwsettings{'STATE'} eq 'ALLOW')) || (($outfwsettings{'POLICY'} eq 'MODE2') && ($outfwsettings{'STATE'} eq 'DENY'))){
			  		print <<END
					<tr bgcolor='$color{'color20'}'>
					    <td align='center'>$outfwsettings{'PROT'}
					    <td align='center'>$outfwsettings{'SNET'}
					    <td align='center'>$outfwsettings{'DISPLAY_DIP'}:$outfwsettings{'DISPLAY_DPORT'}
					    <td align='center'>$outfwsettings{'NAME'}
					    <td align='center'>$outfwsettings{'DISPLAY_STATE'}
					    <td align='center'>$outfwsettings{'LOG'}
					    <td align='center'>
					     <table border='0' cellpadding='0' cellspacing='0'><tr>
						<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='PROT' value='$outfwsettings{'PROT'}' />
							<input type='hidden' name='STATE' value='$outfwsettings{'STATE'}' />
							<input type='hidden' name='SNET' value='$outfwsettings{'SNET'}' />
							<input type='hidden' name='DPORT' value='$outfwsettings{'DPORT'}' />
							<input type='hidden' name='DIP' value='$outfwsettings{'DIP'}' />
							<input type='hidden' name='SIP' value='$outfwsettings{'SIP'}' />
							<input type='hidden' name='NAME' value='$outfwsettings{'NAME'}' />
							<input type='hidden' name='SMAC' value='$outfwsettings{'SMAC'}' />
							<input type='hidden' name='ENABLED' value='$outfwsettings{'ENABLED'}' />
							<input type='hidden' name='LOG' value='$outfwsettings{'LOG'}' />
							<input type='hidden' name='ACTION' value=$Lang::tr{'edit'} />
							<input type='image' src='/images/edit.gif' width="20" height="20" alt=$Lang::tr{'edit'} />
						</form>
						<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='PROT' value='$outfwsettings{'PROT'}' />
							<input type='hidden' name='STATE' value='$outfwsettings{'STATE'}' />
							<input type='hidden' name='SNET' value='$outfwsettings{'SNET'}' />
							<input type='hidden' name='DPORT' value='$outfwsettings{'DPORT'}' />
							<input type='hidden' name='DIP' value='$outfwsettings{'DIP'}' />
							<input type='hidden' name='SIP' value='$outfwsettings{'SIP'}' />
							<input type='hidden' name='NAME' value='$outfwsettings{'NAME'}' />
							<input type='hidden' name='SMAC' value='$outfwsettings{'SMAC'}' />
							<input type='hidden' name='ENABLED' value='$outfwsettings{'ENABLED'}' />
							<input type='hidden' name='LOG' value='$outfwsettings{'LOG'}' />
							<input type='hidden' name='ACTION' value=$Lang::tr{'delete'} />
							<input type='image' src='/images/delete.gif' width="20" height="20" alt=$Lang::tr{'delete'} />
						</form></table>
END
;
					if (($outfwsettings{'SIP'}) || ($outfwsettings{'SMAC'})) {
						unless ($outfwsettings{'SIP'}) { $outfwsettings{'DISPLAY_SIP'} = 'ALL'; } else { $outfwsettings{'DISPLAY_SIP'} = $outfwsettings{'SIP'}; }
						unless ($outfwsettings{'SMAC'}) { $outfwsettings{'DISPLAY_SMAC'} = 'ALL'; } else { $outfwsettings{'DISPLAY_SMAC'} = $outfwsettings{'SMAC'}; }
						print <<END
						<tr><td width='14%' align='right'>$Lang::tr{'source ip'}:
						    <td width='14%' align='left'>$outfwsettings{'DISPLAY_SIP'}
						    <td width='44%' colspan='2' align='center'>
END
;
					}
					print <<END
					</form>
END
;
				}
			}
if ($outfwsettings{'POLICY'} eq 'MODE1'){
print <<END
					<tr bgcolor='$color{'color20'}'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					    <td align='center'>tcp&udp
					    <td align='center'>all
					    <td align='center'>ALL
					    <td align='center'>drop
					    <td align='center'><img src='/images/stock_stop.png' alt='DENY' />
					    <td align='center'>on <input type='radio' name='MODE1LOG' value='on' $checked{'MODE1LOG'}{'on'} /><input type='radio' name='MODE1LOG' value='off' $checked{'MODE1LOG'}{'off'} /> off
					    <td align='center'><input type='hidden' name='ACTION' value=$Lang::tr{'save'} /><input type='image' src='/images/media-floppy.png' width="18" height="18" alt=$Lang::tr{'save'} /></form></tr>
					     <table border='0' cellpadding='0' cellspacing='0'><tr>
						<td>
						<td></table>
END
;
}
		print <<END
		</table>
END
;

	}
	&Header::closebox();
}

if ($outfwsettings{'POLICY'} ne 'MODE0'){
	open( FILE, "< $p2pfile" ) or die "Unable to read $p2pfile";
	@p2ps = <FILE>;
	close FILE;
	&Header::openbox('100%', 'center', 'P2P-Block');
	print <<END
	<table width='40%'>
		<tr bgcolor='$color{'color22'}'><td width='66%' align=center><b>$Lang::tr{'protocol'}</b>
		    <td width='33%' align=center><b>$Lang::tr{'status'}</b>
END
;
	my $id = 1;
	foreach $p2pentry (sort @p2ps)
  	{
  		@p2pline = split( /\;/, $p2pentry );
		print <<END
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
END
;
			print "\t\t\t<tr bgcolor='$color{'color20'}'>\n"; 
  		print <<END
			<td width='66%' align='center'>$p2pline[0]:	
			<td width='33%' align='center'><input type='hidden' name='P2PROT' value='$p2pline[1]' />
END
;
		if ($p2pline[2] eq 'on') {
			print <<END
				<input type='hidden' name='ACTION' value='disable' />
				<input type='image' name='submit' src='/images/stock_ok.png' alt='' />
END
;
		} else {
			print <<END
				<input type='hidden' name='ACTION' value='enable' />
				<input type='image' name='submit' src='/images/stock_stop.png' alt='' />
END
;
		}
		print <<END
			</form>
END
;
	}
	print <<END
	</table>
  <br />$Lang::tr{'outgoingfw p2p description'}
END
;
	&Header::closebox();
}

&Header::openbox('100%', 'center', 'Policy');
print <<END
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='100%'>
		<tr><td width='10%' align='left'><b>$Lang::tr{'mode'} 0:</b><td width='90%' align='left' colspan='2'>$Lang::tr{'outgoingfw mode0'}</td></tr>
		<tr><td width='10%' align='left'><b>$Lang::tr{'mode'} 1:</b><td width='90%' align='left' colspan='2'>$Lang::tr{'outgoingfw mode1'}</td></tr>
		<tr><td width='10%' align='left'><b>$Lang::tr{'mode'} 2:</b><td width='90%' align='left' colspan='2'>$Lang::tr{'outgoingfw mode2'}</td></tr>
		<tr><td colspan='3'><hr /></td></tr>
		<tr><td width='10%' align='left'>	<select name='POLICY' style="width: 85px"><option value='MODE0' $selected{'POLICY'}{'MODE0'}>$Lang::tr{'mode'} 0</option><option value='MODE1' $selected{'POLICY'}{'MODE1'}>$Lang::tr{'mode'} 1</option><option value='MODE2' $selected{'POLICY'}{'MODE2'}>$Lang::tr{'mode'} 2</option></select>
		    <td width='45%' align='left'><input type='submit' name='ACTION' value=$Lang::tr{'save'} />
		    <td width='45%' align='left'>
END
;
	if ($outfwsettings{'POLICY'} ne 'MODE0') {
		print <<END
		    $Lang::tr{'outgoingfw reset'}: <input type='submit' name='ACTION' value=$Lang::tr{'reset'} />
END
;
	}
print <<END
	</table>
	</form>
END
;
&Header::closebox();

&Header::closebigbox();
&Header::closepage();

############################################################################################################################
############################################################################################################################

sub addrule
{
	&Header::openbox('100%', 'center', 'Rules hinzufuegen');
	if ($outfwsettings{'EDIT'} eq 'no') { $selected{'ENABLED'} = 'checked'; }
	print <<END
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='80%'>
		<tr><td width='20%' align='right'>$Lang::tr{'description'}: <img src='/blob.gif' />
		    <td width='30%' align='left'><input type='text' name='NAME' maxlength='30' value='$outfwsettings{'NAME'}' />
		    <td width='20%' align='right'>$Lang::tr{'active'}:
		    <td width='30%' align='left'><input type='checkbox' name='ENABLED' $selected{'ENABLED'} />
		<tr><td width='20%' align='right'>$Lang::tr{'protocol'}:
		    <td width='30%' align='left'><select name='PROT'><option value='tcp' $selected{'PROT'}{'tcp'}>TCP</option><option value='tcp&udp' $selected{'PROT'}{'tcp&udp'}>TCP & UDP</option><option value='udp' $selected{'PROT'}{'udp'}>UDP</option></select>
		    <td width='20%' align='right'>$Lang::tr{'policy'}:
		    <td width='30%' align='left'>
END
;
	if ($outfwsettings{'POLICY'} eq 'MODE1'){
		print "\t\t\tALLOW<input type='hidden' name='STATE' value='ALLOW' />\n";
	} elsif ($outfwsettings{'POLICY'} eq 'MODE2'){
		print "\t\t\tDENY<input type='hidden' name='STATE' value='DENY' />\n";
	}
	print <<END
		<tr><td width='20%' align='right'>$Lang::tr{'source net'}:
		    <td width='30%' align='left'><select name='SNET'>
			<option value='all' $selected{'SNET'}{'ALL'}>$Lang::tr{'all'}</option>
			<option value='ip' $selected{'SNET'}{'ip'}>$Lang::tr{'source ip'}</option>
			<option value='green' $selected{'SNET'}{'green'}>$Lang::tr{'green'}</option>
END
;
	if (&Header::blue_used()){
		print "\t\t\t<option value='blue' $selected{'SNET'}{'blue'}>$Lang::tr{'wireless'}</option>\n";
	}
	if (&Header::orange_used()){
		print "\t\t\t<option value='orange' $selected{'SNET'}{'orange'}>$Lang::tr{'dmz'}</option>\n";
	}
	print <<END
			</select>
		    <td width='20%' align='right'>$Lang::tr{'source ip'}: <img src='/blob.gif' />
		    <td width='30%' align='left'><input type='text' name='SIP' maxlength='15' value='$outfwsettings{'SIP'}' />
		<tr><td width='20%' align='right'>$Lang::tr{'logging'}:
END
;
if ($outfwsettings{'POLICY'} eq 'MODE1'){
	 print "<td width='30%' align='left'><input type='text' name='LOG' maxlength='10' value='$Lang::tr{'inactive'}' readonly='true' /></td>";
}
else{
	 print "<td width='30%' align='left'><select name='LOG'><option value='$Lang::tr{'active'}' $selected{'LOG'}{$Lang::tr{'active'}}>$Lang::tr{'active'}</option><option value='$Lang::tr{'inactive'}' $selected{'LOG'}{$Lang::tr{'inactive'}}>$Lang::tr{'inactive'}</option></select></td>";
}
print <<END
		    <td width='20%' align='right' />
		    <td width='30%' align='left' />
		<tr><td width='20%' align='right'>$Lang::tr{'destination ip'}: <img src='/blob.gif' />
		    <td width='30%' align='left'><input type='text' name='DIP' maxlength='15' value='$outfwsettings{'DIP'}' />
		    <td width='20%' align='right'>$Lang::tr{'destination port'}: <img src='/blob.gif' />
		    <td width='30%' align='left'><input type='text' name='DPORT' maxlength='11' value='$outfwsettings{'DPORT'}' />
		<tr><td colspan='4'>
		<tr><td width='40%' align='right' colspan='2'><img src='/blob.gif' />$Lang::tr{'this field may be blank'}
		    <td width='60%' align='left' colspan='2'><input type='submit' name='ACTION' value=$Lang::tr{'add'} />
	</table></form>
END
;
	&Header::closebox();

if ($outfwsettings{'POLICY'} eq 'MODE1' || $outfwsettings{'POLICY'} eq 'MODE2')
{
&Header::openbox('100%', 'center', 'Quick Add');

	open( FILE, "< /var/ipfire/outgoing/defaultservices" ) or die "Unable to read default services";
	my @defservices = <FILE>;
	close FILE;

print "<table width='100%'><tr bgcolor='$color{'color20'}'><td><b>$Lang::tr{'service'}</b></td><td><b>$Lang::tr{'description'}</b></td><td><b>$Lang::tr{'port'}</b></td><td><b>$Lang::tr{'protocol'}</b></td><td><b>$Lang::tr{'source net'}</b></td><td><b>$Lang::tr{'logging'}</b></td><td><b>$Lang::tr{'action'}</b></td></tr>";
foreach my $serviceline(@defservices)
	{
	my @service = split(/,/,$serviceline);
	print <<END
	<tr><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<td>$service[0]<input type='hidden' name='NAME' value='@service[0]' /></td>
												<td>$service[3]</td>
												<td><a href='http://isc.sans.org/port_details.php?port=$service[1]' target='top'>$service[1]</a><input type='hidden' name='DPORT' value='@service[1]' /></td>
												<td>$service[2]<input type='hidden' name='PROT' value='@service[2]' /></td>
												<td><select name='SNET'><option value='all' $selected{'SNET'}{'ALL'}>$Lang::tr{'all'}</option><option value='green' $selected{'SNET'}{'green'}>$Lang::tr{'green'}</option>
END
;
	if (&Header::blue_used()){
		print "<option value='blue' $selected{'SNET'}{'blue'}>$Lang::tr{'wireless'}</option>";
	}
	if (&Header::orange_used()){
		print "<option value='orange' $selected{'SNET'}{'orange'}>$Lang::tr{'dmz'}</option>";
	}
	print <<END
					</select></td>
          <td><select name='LOG'><option value='$Lang::tr{'active'}'>$Lang::tr{'active'}</option><option value='$Lang::tr{'inactive'}' 'selected'>$Lang::tr{'inactive'}</option></select></td><td>
					<input type='hidden' name='ACTION' value=$Lang::tr{'add'} />
					<input type='image' alt='$Lang::tr{'add'}' src='/images/add.gif' />
					<input type='hidden' name='ENABLED' value='on' />
END
;
	if ($outfwsettings{'POLICY'} eq 'MODE1'){	print "<input type='hidden' name='STATE' value='ALLOW' /></form></td></tr>";}
	elsif ($outfwsettings{'POLICY'} eq 'MODE2'){print "<input type='hidden' name='STATE' value='DENY' /></form></td></tr>";}
	}
	print "</table>";
	&Header::closebox();
  }
}
