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
my $configpath = "/var/ipfire/outgoing/groups/";
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

$outfwsettings{'TIME_FROM'} = '00:00';
$outfwsettings{'TIME_TO'} = '00:00';

&General::readhash("${General::swroot}/outgoing/settings", \%outfwsettings);
&Header::getcgihash(\%outfwsettings);

###############
# DEBUG DEBUG
#&Header::openbox('100%', 'left', 'DEBUG');
#my $debugCount = 0;
#foreach my $line (sort keys %outfwsettings) {
#print "$line = $outfwsettings{$line}<br />\n";
# $debugCount++;
#}
#print "&nbsp;Count: $debugCount\n";
#&Header::closebox();
# DEBUG DEBUG
###############

$selected{'TIME_FROM'}{$outfwsettings{'TIME_FROM'}} = "selected='selected'";
$selected{'TIME_TO'}{$outfwsettings{'TIME_TO'}} = "selected='selected'";

$checked{'MODE1LOG'}{'off'} = '';
$checked{'MODE1LOG'}{'on'} = '';
$checked{'MODE1LOG'}{$outfwsettings{'MODE1LOG'}} = "checked='checked'";
$checked{'TIME_MON'}{'off'} = '';
$checked{'TIME_MON'}{'on'} = '';
$checked{'TIME_MON'}{$outfwsettings{'TIME_MON'}} = "checked='checked'";
$checked{'TIME_TUE'}{'off'} = '';
$checked{'TIME_TUE'}{'on'} = '';
$checked{'TIME_TUE'}{$outfwsettings{'TIME_TUE'}} = "checked='checked'";
$checked{'TIME_WED'}{'off'} = '';
$checked{'TIME_WED'}{'on'} = '';
$checked{'TIME_WED'}{$outfwsettings{'TIME_WED'}} = "checked='checked'";
$checked{'TIME_THU'}{'off'} = '';
$checked{'TIME_THU'}{'on'} = '';
$checked{'TIME_THU'}{$outfwsettings{'TIME_THU'}} = "checked='checked'";
$checked{'TIME_FRI'}{'off'} = '';
$checked{'TIME_FRI'}{'on'} = '';
$checked{'TIME_FRI'}{$outfwsettings{'TIME_FRI'}} = "checked='checked'";
$checked{'TIME_SAT'}{'off'} = '';
$checked{'TIME_SAT'}{'on'} = '';
$checked{'TIME_SAT'}{$outfwsettings{'TIME_SAT'}} = "checked='checked'";
$checked{'TIME_SUN'}{'off'} = '';
$checked{'TIME_SUN'}{'on'} = '';
$checked{'TIME_SUN'}{$outfwsettings{'TIME_SUN'}} = "checked='checked'";

if ($outfwsettings{'POLICY'} eq 'MODE0'){ $selected{'POLICY'}{'MODE0'} = 'selected'; } else { $selected{'POLICY'}{'MODE0'} = ''; }
if ($outfwsettings{'POLICY'} eq 'MODE1'){ $selected{'POLICY'}{'MODE1'} = 'selected'; } else { $selected{'POLICY'}{'MODE1'} = ''; }
if ($outfwsettings{'POLICY'} eq 'MODE2'){ $selected{'POLICY'}{'MODE2'} = 'selected'; } else { $selected{'POLICY'}{'MODE2'} = ''; }

# This is a little hack if poeple don´t mark any date then all will be selected, because they might have forgotten to select
# a valid day. A Rule without any matching day will never work, because the timeranges are new feature people might not notice
# that they have to select a day for the rule.

if ( $outfwsettings{'TIME_MON'} eq "" &&
     $outfwsettings{'TIME_TUE'} eq "" &&
	 $outfwsettings{'TIME_WED'} eq "" &&
	 $outfwsettings{'TIME_THU'} eq "" &&
	 $outfwsettings{'TIME_FRI'} eq "" &&
	 $outfwsettings{'TIME_SAT'} eq "" &&
	 $outfwsettings{'TIME_SUN'} eq "" )
	 {
		$outfwsettings{'TIME_MON'} = "on";
		$outfwsettings{'TIME_TUE'} = "on";
		$outfwsettings{'TIME_WED'} = "on";
		$outfwsettings{'TIME_THU'} = "on";
		$outfwsettings{'TIME_FRI'} = "on";
		$outfwsettings{'TIME_SAT'} = "on";
		$outfwsettings{'TIME_SUN'} = "on";
	 }

&Header::openpage($Lang::tr{'outgoing firewall'}, 1, '');
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
		
		$configline[10] =  "on" if not exists $configline[11];
		$configline[11] =  "on" if not exists $configline[11];
		$configline[12] =  "on" if not exists $configline[12];
		$configline[13] =  "on" if not exists $configline[13];
		$configline[14] =  "on" if not exists $configline[14];
		$configline[15] =  "on" if not exists $configline[15];
		$configline[16] =  "on" if not exists $configline[16];
		$configline[17] =  "00:00" if not exists $configline[17];
		$configline[18] =  "00:00" if not exists $configline[18];

  		unless	(($configline[0] eq $outfwsettings{'STATE'}) && 
			($configline[1] eq $outfwsettings{'ENABLED'}) && 
			($configline[2] eq $outfwsettings{'SNET'}) && 
			($configline[3] eq $outfwsettings{'PROT'}) && 
			($configline[4] eq $outfwsettings{'NAME'}) && 
			($configline[5] eq $outfwsettings{'SIP'}) && 
			($configline[6] eq $outfwsettings{'SMAC'}) && 
			($configline[7] eq $outfwsettings{'DIP'}) &&
			($configline[9] eq $outfwsettings{'LOG'}) &&       
			($configline[8] eq $outfwsettings{'DPORT'}) &&
			($configline[10] eq $outfwsettings{'TIME_MON'}) &&       
			($configline[11] eq $outfwsettings{'TIME_TUE'}) &&       
			($configline[12] eq $outfwsettings{'TIME_WED'}) &&       
			($configline[13] eq $outfwsettings{'TIME_THU'}) &&       
			($configline[14] eq $outfwsettings{'TIME_FRI'}) &&       
			($configline[15] eq $outfwsettings{'TIME_SAT'}) &&       
			($configline[16] eq $outfwsettings{'TIME_SUN'}) &&       
			($configline[17] eq $outfwsettings{'TIME_FROM'}) &&       
			($configline[18] eq $outfwsettings{'TIME_TO'}))
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
		
		$configline[10] =  "on" if not exists $configline[11];
		$configline[11] =  "on" if not exists $configline[11];
		$configline[12] =  "on" if not exists $configline[12];
		$configline[13] =  "on" if not exists $configline[13];
		$configline[14] =  "on" if not exists $configline[14];
		$configline[15] =  "on" if not exists $configline[15];
		$configline[16] =  "on" if not exists $configline[16];
		$configline[17] =  "00:00" if not exists $configline[17];
		$configline[18] =  "00:00" if not exists $configline[18];
				
  		unless	(($configline[0] eq $outfwsettings{'STATE'}) && 
			($configline[1] eq $outfwsettings{'ENABLED'}) && 
			($configline[2] eq $outfwsettings{'SNET'}) && 
			($configline[3] eq $outfwsettings{'PROT'}) && 
			($configline[4] eq $outfwsettings{'NAME'}) && 
			($configline[5] eq $outfwsettings{'SIP'}) && 
			($configline[6] eq $outfwsettings{'SMAC'}) && 
			($configline[7] eq $outfwsettings{'DIP'}) && 
			($configline[9] eq $outfwsettings{'LOG'}) &&
			($configline[8] eq $outfwsettings{'DPORT'}) &&
			($configline[10] eq $outfwsettings{'TIME_MON'}) &&       
			($configline[11] eq $outfwsettings{'TIME_TUE'}) &&       
			($configline[12] eq $outfwsettings{'TIME_WED'}) &&       
			($configline[13] eq $outfwsettings{'TIME_THU'}) &&       
			($configline[14] eq $outfwsettings{'TIME_FRI'}) &&       
			($configline[15] eq $outfwsettings{'TIME_SAT'}) &&       
			($configline[16] eq $outfwsettings{'TIME_SUN'}) &&       
			($configline[17] eq $outfwsettings{'TIME_FROM'}) &&       
			($configline[18] eq $outfwsettings{'TIME_TO'}))
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

		if ( $outfwsettings{'SNET'} eq "all" ) {
			$outfwsettings{'SIP'} ="";
			$outfwsettings{'SMAC'}="";
		}
		open( FILE, ">> $configfile" ) or die "Unable to write $configfile";
		print FILE <<END
$outfwsettings{'STATE'};$outfwsettings{'ENABLED'};$outfwsettings{'SNET'};$outfwsettings{'PROT'};$outfwsettings{'NAME'};$outfwsettings{'SIP'};$outfwsettings{'SMAC'};$outfwsettings{'DIP'};$outfwsettings{'DPORT'};$outfwsettings{'LOG'};$outfwsettings{'TIME_MON'};$outfwsettings{'TIME_TUE'};$outfwsettings{'TIME_WED'};$outfwsettings{'TIME_THU'};$outfwsettings{'TIME_FRI'};$outfwsettings{'TIME_SAT'};$outfwsettings{'TIME_SUN'};$outfwsettings{'TIME_FROM'};$outfwsettings{'TIME_TO'};
END
;
		close FILE;
		system("/usr/local/bin/outgoingfwctrl");
	} else {
		$outfwsettings{'ACTION'} = 'Add rule';
	}
}
if ($outfwsettings{'ACTION'} eq $Lang::tr{'Add Rule'})
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
		<input type='submit' name='ACTION' value='$Lang::tr{'Add Rule'}' />
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
				
				$configline[10] =  "on" if not exists $configline[11];
				$configline[11] =  "on" if not exists $configline[11];
				$configline[12] =  "on" if not exists $configline[12];
				$configline[13] =  "on" if not exists $configline[13];
				$configline[14] =  "on" if not exists $configline[14];
				$configline[15] =  "on" if not exists $configline[15];
				$configline[16] =  "on" if not exists $configline[16];
				$configline[17] =  "00:00" if not exists $configline[17];
				$configline[18] =  "00:00" if not exists $configline[18];
				
				$outfwsettings{'TIME_MON'} =  $configline[10];
				$outfwsettings{'TIME_TUE'} =  $configline[11];
				$outfwsettings{'TIME_WED'} =  $configline[12];
				$outfwsettings{'TIME_THU'} =  $configline[13];
				$outfwsettings{'TIME_FRI'} =  $configline[14];
				$outfwsettings{'TIME_SAT'} =  $configline[15];
				$outfwsettings{'TIME_SUN'} =  $configline[16];
				$outfwsettings{'TIME_FROM'} =  $configline[17];
				$outfwsettings{'TIME_TO'} =  $configline[18];

				if ($outfwsettings{'DIP'} eq ''){ $outfwsettings{'DISPLAY_DIP'} = 'ALL'; } else { $outfwsettings{'DISPLAY_DIP'} = $outfwsettings{'DIP'}; }
				if ($outfwsettings{'DPORT'} eq ''){ $outfwsettings{'DISPLAY_DPORT'} = 'ALL'; } else { $outfwsettings{'DISPLAY_DPORT'} = $outfwsettings{'DPORT'}; }
				if ($outfwsettings{'STATE'} eq 'DENY'){ $outfwsettings{'DISPLAY_STATE'} = "<img src='/images/stock_stop.png' alt='DENY' />"; }
				if ($outfwsettings{'STATE'} eq 'ALLOW'){ $outfwsettings{'DISPLAY_STATE'} = "<img src='/images/stock_ok.png' alt='ALLOW' />"; }
				if ((($outfwsettings{'POLICY'} eq 'MODE1') && ($outfwsettings{'STATE'} eq 'ALLOW')) || (($outfwsettings{'POLICY'} eq 'MODE2') && ($outfwsettings{'STATE'} eq 'DENY'))){
				if ( $outfwsettings{'ENABLED'} eq "on" ){
					print "<tr bgcolor='$color{'color20'}'>";
				} else {
					print "<tr bgcolor='$color{'color18'}'>";
				}
					print <<END
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
							<input type='hidden' name='TIME_MON' value='$outfwsettings{'TIME_MON'}' />
							<input type='hidden' name='TIME_TUE' value='$outfwsettings{'TIME_TUE'}' />
							<input type='hidden' name='TIME_WED' value='$outfwsettings{'TIME_WED'}' />
							<input type='hidden' name='TIME_THU' value='$outfwsettings{'TIME_THU'}' />
							<input type='hidden' name='TIME_FRI' value='$outfwsettings{'TIME_FRI'}' />
							<input type='hidden' name='TIME_SAT' value='$outfwsettings{'TIME_SAT'}' />
							<input type='hidden' name='TIME_SUN' value='$outfwsettings{'TIME_SUN'}' />
							<input type='hidden' name='TIME_FROM' value='$outfwsettings{'TIME_FROM'}' />
							<input type='hidden' name='TIME_TO' value='$outfwsettings{'TIME_TO'}' />
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
							<input type='hidden' name='TIME_MON' value='$outfwsettings{'TIME_MON'}' />
							<input type='hidden' name='TIME_TUE' value='$outfwsettings{'TIME_TUE'}' />
							<input type='hidden' name='TIME_WED' value='$outfwsettings{'TIME_WED'}' />
							<input type='hidden' name='TIME_THU' value='$outfwsettings{'TIME_THU'}' />
							<input type='hidden' name='TIME_FRI' value='$outfwsettings{'TIME_FRI'}' />
							<input type='hidden' name='TIME_SAT' value='$outfwsettings{'TIME_SAT'}' />
							<input type='hidden' name='TIME_SUN' value='$outfwsettings{'TIME_SUN'}' />
							<input type='hidden' name='TIME_FROM' value='$outfwsettings{'TIME_FROM'}' />
							<input type='hidden' name='TIME_TO' value='$outfwsettings{'TIME_TO'}' />
							<input type='hidden' name='ACTION' value=$Lang::tr{'delete'} />
							<input type='image' src='/images/delete.gif' width="20" height="20" alt=$Lang::tr{'delete'} />
						</form></table>
END
;
					if (($outfwsettings{'SIP'}) || ($outfwsettings{'SMAC'})) {

						unless ($outfwsettings{'SIP'}) {
							$outfwsettings{'DISPLAY_SIP'} = 'ALL';
						} else {
							$outfwsettings{'DISPLAY_SIP'} = $outfwsettings{'SIP'};
						}

						unless ($outfwsettings{'SMAC'}) {
							$outfwsettings{'DISPLAY_SMAC'} = 'ALL';
							print "<tr><td /><td align='left'>$Lang::tr{'source ip or net'}: </td>";
							print "<td align='left' colspan='2'>$outfwsettings{'DISPLAY_SIP'}</td>";
						} else {
							$outfwsettings{'DISPLAY_SMAC'} = $outfwsettings{'SMAC'};
							print "<tr><td /><td align='left'>$Lang::tr{'source'} $Lang::tr{'mac address'}: </td>";
							print "<td align='left' colspan='2'>$outfwsettings{'DISPLAY_SMAC'}</td>";
						}
					}
						print <<END
						<tr><td width='14%' align='right'>$Lang::tr{'time'} -  </td>
						    <td width='14%' align='left'>
END
;
							if ($outfwsettings{'TIME_MON'} eq 'on') { print "<font color='$Header::colourgreen'>";}
							else { print "<font color='$Header::colourred'>";}
								print "$Lang::tr{'advproxy monday'}</font>,"; 
							if ($outfwsettings{'TIME_TUE'} eq 'on') { print "<font color='$Header::colourgreen'>";}
							else { print "<font color='$Header::colourred'>";}
								print "$Lang::tr{'advproxy tuesday'}</font>,"; 
							if ($outfwsettings{'TIME_WED'} eq 'on') { print "<font color='$Header::colourgreen'>";}
							else { print "<font color='$Header::colourred'>";}
								print "$Lang::tr{'advproxy wednesday'}</font>,"; 
							if ($outfwsettings{'TIME_THU'} eq 'on') { print "<font color='$Header::colourgreen'>";}
							else { print "<font color='$Header::colourred'>";}
								print "$Lang::tr{'advproxy thursday'}</font>,"; 
							if ($outfwsettings{'TIME_FRI'} eq 'on') { print "<font color='$Header::colourgreen'>";}
							else { print "<font color='$Header::colourred'>";}
								print "$Lang::tr{'advproxy friday'}</font>,"; 
							if ($outfwsettings{'TIME_SAT'} eq 'on') { print "<font color='$Header::colourgreen'>";}
							else { print "<font color='$Header::colourred'>";}
								print "$Lang::tr{'advproxy saturday'}</font>,"; 
							if ($outfwsettings{'TIME_SUN'} eq 'on') { print "<font color='$Header::colourgreen'>";}
							else { print "<font color='$Header::colourred'>";}
								print "$Lang::tr{'advproxy sunday'}</font>";		
							print <<END
							</td>
						    <td width='22%' align='center'>$Lang::tr{'advproxy from'} $outfwsettings{'TIME_FROM'}</td>
							<td width='22%' align='center'>$Lang::tr{'advproxy to'} $outfwsettings{'TIME_TO'}</td>
					</form>
END
;
				}
			}
if ($outfwsettings{'POLICY'} eq 'MODE1'){
print <<END
					<tr bgcolor='$color{'color20'}'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					    <td align='center'>all
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
				<input type='image' name='submit' src='/images/stock_ok.png' alt='$Lang::tr{'outgoing firewall p2p allow'}' title='$Lang::tr{'outgoing firewall p2p allow'}'/>
END
;
		} else {
			print <<END
				<input type='hidden' name='ACTION' value='enable' />
				<input type='image' name='submit' src='/images/stock_stop.png' alt='$Lang::tr{'outgoing firewall p2p deny'}' title='$Lang::tr{'outgoing firewall p2p deny'}' />
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
  <br />$Lang::tr{'outgoing firewall p2p description 1'} <img src='/images/stock_ok.png' align='absmiddle' alt='$Lang::tr{'outgoing firewall p2p deny'}'> $Lang::tr{'outgoing firewall p2p description 2'} <img src='/images/stock_stop.png' align='absmiddle' alt='$Lang::tr{'outgoing firewall p2p deny'}'> $Lang::tr{'outgoing firewall p2p description 3'}
END
;
	&Header::closebox();
}

&Header::openbox('100%', 'center', 'Policy');
print <<END
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='100%'>
		<tr><td width='10%' align='left'><b>$Lang::tr{'mode'} 0:</b><td width='90%' align='left' colspan='2'>$Lang::tr{'outgoing firewall mode0'}</td></tr>
		<tr><td width='10%' align='left'><b>$Lang::tr{'mode'} 1:</b><td width='90%' align='left' colspan='2'>$Lang::tr{'outgoing firewall mode1'}</td></tr>
		<tr><td width='10%' align='left'><b>$Lang::tr{'mode'} 2:</b><td width='90%' align='left' colspan='2'>$Lang::tr{'outgoing firewall mode2'}</td></tr>
		<tr><td colspan='3'><hr /></td></tr>
		<tr><td width='10%' align='left'>	<select name='POLICY' style="width: 85px"><option value='MODE0' $selected{'POLICY'}{'MODE0'}>$Lang::tr{'mode'} 0</option><option value='MODE1' $selected{'POLICY'}{'MODE1'}>$Lang::tr{'mode'} 1</option><option value='MODE2' $selected{'POLICY'}{'MODE2'}>$Lang::tr{'mode'} 2</option></select>
		    <td width='45%' align='left'><input type='submit' name='ACTION' value=$Lang::tr{'save'} />
		    <td width='45%' align='left'>
END
;
	if ($outfwsettings{'POLICY'} ne 'MODE0') {
		print <<END
		    $Lang::tr{'outgoing firewall reset'}: <input type='submit' name='ACTION' value=$Lang::tr{'reset'} />
END
;
	}
print <<END
	</table>
	</form>
END
;
&Header::closebox();

############################################################################################################################
############################################################################################################################

sub addrule
{
	&Header::openbox('100%', 'center', $Lang::tr{'Add Rule'});
	if ($outfwsettings{'EDIT'} eq 'no') { $selected{'ENABLED'} = 'checked'; }
	$selected{'TIME_FROM'}{$outfwsettings{'TIME_FROM'}} = "selected='selected'";
	$selected{'TIME_TO'}{$outfwsettings{'TIME_TO'}} = "selected='selected'";
print <<END
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='80%'>
		<tr>
			<td width='20%' align='right'>$Lang::tr{'description'}: <img src='/blob.gif' /></td>
			<td width='30%' align='left'><input type='text' name='NAME' maxlength='30' value='$outfwsettings{'NAME'}' /></td>
			<td width='20%' align='right' colspan='2'>$Lang::tr{'active'}:</td>
			<td width='30%' align='left' colspan='2'><input type='checkbox' name='ENABLED' $selected{'ENABLED'} /></td>
		</tr>
		<tr>
			<td width='20%' align='right'>$Lang::tr{'protocol'}</td>
			<td width='30%' align='left'>
				<select name='PROT'>
					<option value='all' $selected{'PROT'}{'all'}>All</option>
					<option value='tcp' $selected{'PROT'}{'tcp'}>TCP</option>
					<option value='udp' $selected{'PROT'}{'udp'}>UDP</option>
					<option value='gre' $selected{'PROT'}{'gre'}>GRE</option>
					<option value='esp' $selected{'PROT'}{'esp'}>ESP</option>
				</select>
			</td>
			<td width='20%' align='right' colspan='2'>$Lang::tr{'policy'}:</td>
			<td width='30%' align='left' colspan='2'>
END
;
	if ($outfwsettings{'POLICY'} eq 'MODE1'){
		print "\t\t\t\tALLOW<input type='hidden' name='STATE' value='ALLOW' />\n";
	} elsif ($outfwsettings{'POLICY'} eq 'MODE2'){
		print "\t\t\t\tDENY<input type='hidden' name='STATE' value='DENY' />\n";
	}
	print <<END
			</td>
		</tr>
		<tr>
			<td width='20%' align='right'>$Lang::tr{'source'}:</td>
			<td width='30%' align='left'>
				<select name='SNET'>
					<optgroup label='---'>
						<option value='all' $selected{'SNET'}{'ALL'}>$Lang::tr{'all'}</option>
					<optgroup label='$Lang::tr{'mac address'}'>
						<option value='mac' $selected{'SNET'}{'mac'}>$Lang::tr{'source'} $Lang::tr{'mac address'}</option>
					</optgroup>
					<optgroup label='$Lang::tr{'ip address'}'>
						<option value='ip' $selected{'SNET'}{'ip'}>$Lang::tr{'source ip or net'}</option>
						<option value='red' $selected{'SNET'}{'red'}>$Lang::tr{'red'} IP</option>
					</optgroup>
					<optgroup label='$Lang::tr{'alt vpn'}'>
						<option value='ovpn' $selected{'SNET'}{'ovpn'}>OpenVPN $Lang::tr{'interface'}</option>
					</optgroup>
					<optgroup label='$Lang::tr{'network'}'>
						<option value='green' $selected{'SNET'}{'green'}>$Lang::tr{'green'}</option>
END
;
	if (&Header::blue_used()){
		print "\t\t\t\t\t<option value='blue' $selected{'SNET'}{'blue'}>$Lang::tr{'wireless'}</option>\n";
	}
	if (&Header::orange_used()){
		print "\t\t\t\t\t<option value='orange' $selected{'SNET'}{'orange'}>$Lang::tr{'dmz'}</option>\n";
	}
	print <<END
					</optgroup>
					<optgroup label='IP $Lang::tr{'advproxy NCSA group'}'>
END
;
	my @ipgroups = qx(ls $configpath/ipgroups/);
	foreach (sort @ipgroups){
		chomp($_);
		print "\t\t\t\t\t<option value='$_' $selected{'SNET'}{$_}>$_</option>\n";
	}
	print <<END
					</optgroup>
					<optgroup label='MAC $Lang::tr{'advproxy NCSA group'}'>
END
;
	my @macgroups = qx(ls $configpath/macgroups/);
	foreach (sort @macgroups){
		chomp($_);
		print "\t\t\t\t\t<option value='$_' $selected{'SNET'}{$_}>$_</option>\n";
	}
	print <<END
					</optgroup>
				</select>
			</td>
			<td align='right' colspan='4'><font color='red'>$Lang::tr{'outgoing firewall warning'}</font></td>
		</tr>
		<tr>
			<td align='right' colspan='4' >$Lang::tr{'source ip or net'}<img src='/blob.gif' /></td>
			<td align='left' colspan='4' ><input type='text' name='SIP' value='$outfwsettings{'SIP'}' /></td>
		</tr>
		<tr>
			<td align='right' colspan='4' >$Lang::tr{'source'} $Lang::tr{'mac address'}: <img src='/blob.gif' />
			<td align='left' colspan='4' ><input type='text' name='SMAC' maxlength='23' value='$outfwsettings{'SMAC'}' />
		</tr>
		<tr>
			<td width='20%' align='right'>$Lang::tr{'logging'}:</td>
			<td width='30%' align='left'>
				<select name='LOG'>
					<option value='$Lang::tr{'active'}' $selected{'LOG'}{$Lang::tr{'active'}}>$Lang::tr{'active'}</option>
					<option value='$Lang::tr{'inactive'}' $selected{'LOG'}{$Lang::tr{'inactive'}}>$Lang::tr{'inactive'}</option>
				</select>
			</td>
			<td width='20%' align='right' colspan='2' />
			<td width='30%' align='left' colspan='2' />
		<tr>
			<td width='20%' align='right'>$Lang::tr{'destination ip or net'}: <img src='/blob.gif' /></td>
			<td width='30%' align='left'><input type='text' name='DIP'  value='$outfwsettings{'DIP'}' /></td>
			<td width='20%' align='right' colspan='2'>$Lang::tr{'destination port'}(s) <img src='/blob.gif' /></td>
			<td width='30%' align='left' colspan='2'><input type='text' name='DPORT' value='$outfwsettings{'DPORT'}' /></td>
		</tr>
		<tr>
			<td width='20%' align='right'>$Lang::tr{'time'}:</td>
			<td width='30%' align='left'>$Lang::tr{'advproxy monday'} $Lang::tr{'advproxy tuesday'} $Lang::tr{'advproxy wednesday'} $Lang::tr{'advproxy thursday'} $Lang::tr{'advproxy friday'} $Lang::tr{'advproxy saturday'} $Lang::tr{'advproxy sunday'}</td>
			<td width='20%' align='right' colspan='2' />
			<td width='15%' align='left'>$Lang::tr{'advproxy from'}</td>
			<td width='15%' align='left'>$Lang::tr{'advproxy to'}</td>
		</tr>
		<tr>
			<td width='20%' align='right'></td>
			<td width='30%' align='left'>
				<input type='checkbox' name='TIME_MON' $checked{'TIME_MON'}{'on'} />
				<input type='checkbox' name='TIME_TUE' $checked{'TIME_TUE'}{'on'} />
				<input type='checkbox' name='TIME_WED' $checked{'TIME_WED'}{'on'} />
				<input type='checkbox' name='TIME_THU' $checked{'TIME_THU'}{'on'} />
				<input type='checkbox' name='TIME_FRI' $checked{'TIME_FRI'}{'on'} />
				<input type='checkbox' name='TIME_SAT' $checked{'TIME_SAT'}{'on'} />
				<input type='checkbox' name='TIME_SUN' $checked{'TIME_SUN'}{'on'} />
			</td>
			<td width='20%' align='right' colspan='2' />
			<td width='15%' align='left'>
				<select name='TIME_FROM'>
END
;
for (my $i=0;$i<=23;$i++) {
	$i = sprintf("%02s",$i);
	for (my $j=0;$j<=45;$j+=15) {
		$j = sprintf("%02s",$j);
		my $time = $i.":".$j;
		print "\t\t\t\t\t<option $selected{'TIME_FROM'}{$time}>$i:$j</option>\n";
	}
}
print <<END	
				</select>
			</td>
			<td width='15%' align='left'><select name='TIME_TO'>
END
;
for (my $i=0;$i<=23;$i++) {
	$i = sprintf("%02s",$i);
	for (my $j=0;$j<=45;$j+=15) {
		$j = sprintf("%02s",$j);
		my $time = $i.":".$j;
		print "\t\t\t\t\t<option $selected{'TIME_TO'}{$time}>$i:$j</option>\n";
	}
}
print <<END	
				</select>
			</td>
		</tr>
		<tr>
			<td colspan='6' />
		<tr>
		<tr>
			<td width='40%' align='right' colspan='2'><img src='/blob.gif' />$Lang::tr{'this field may be blank'}</td>
			<td width='60%' align='left' colspan='4'><input type='submit' name='ACTION' value=$Lang::tr{'add'} /></td>
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

&Header::closebigbox();
&Header::closepage();
