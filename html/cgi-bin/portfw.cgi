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

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::colouryellow} );
undef (@dummy);

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

my %cgiparams=();
my %selected=();
my %checked=();
my $prtrange1=0;
my $prtrange2=0;
my $errormessage = '';
my $filename = "${General::swroot}/portfw/config";
my $aliasfile = "${General::swroot}/ethernet/aliases";

&Header::showhttpheaders();

$cgiparams{'ENABLED'} = 'off';
$cgiparams{'KEY1'} = '0';
$cgiparams{'KEY2'} = '0';
$cgiparams{'PROTOCOL'} = '';
$cgiparams{'SRC_PORT'} = '';
$cgiparams{'DEST_IP'} = '';
$cgiparams{'DEST_PORT'} = '';
$cgiparams{'SRC_IP'} = '';
$cgiparams{'ORIG_IP'} = '';
$cgiparams{'REMARK'} = '';
$cgiparams{'OVERRIDE'} = 'off';
$cgiparams{'ACTION'} = '';

&Header::getcgihash(\%cgiparams);

my $disable_all = "0";
my $enable_all = "0";

if ($cgiparams{'ACTION'} eq $Lang::tr{'add'})
{
	&valaddupdate();
	
	# Darren Critchley - if there is an error, don't waste any more time processing
	if ($errormessage) { goto ERROR; }
	
	open(FILE, $filename) or die 'Unable to open config file.';
	my @current = <FILE>;
	close(FILE);
	my $key1 = 0; # used for finding last sequence number used 
	foreach my $line (@current)
	{
		my @temp = split(/\,/,$line);

		chomp ($temp[8]);
		if ($cgiparams{'KEY2'} eq "0"){ # if key2 is 0 then it is a portfw addition
			if ( $cgiparams{'SRC_PORT'} eq $temp[3] &&
				$cgiparams{'PROTOCOL'} eq $temp[2] &&
				$cgiparams{'SRC_IP'} eq $temp[7])
			{
				 $errormessage =  
					"$Lang::tr{'source port in use'} $cgiparams{'SRC_PORT'}";
			}
			# Check if key2 = 0, if it is then it is a port forward entry and we want the sequence number
			if ( $temp[1] eq "0") {
				$key1=$temp[0];
			}
			# Darren Critchley - Duplicate or overlapping Port range check
			if ($temp[1] eq "0" && 
				$cgiparams{'PROTOCOL'} eq $temp[2] &&
				$cgiparams{'SRC_IP'} eq $temp[7] &&
				$errormessage eq '') 
			{
				&portchecks($temp[3], $temp[5]);
			}
		} else {
			if ( $cgiparams{'KEY1'} eq $temp[0] &&
				$cgiparams{'ORIG_IP'} eq $temp[8])
			{
				 $errormessage =  
					"$Lang::tr{'source ip in use'} $cgiparams{'ORIG_IP'}";
			}
		}
	}

ERROR:
	unless ($errormessage)
	{
		# Darren Critchley - we only want to store ranges with Colons
		$cgiparams{'SRC_PORT'} =~ tr/-/:/; 
		$cgiparams{'DEST_PORT'} =~ tr/-/:/;

		if ($cgiparams{'KEY1'} eq "0") { # 0 in KEY1 indicates it is a portfw add
			$key1++; # Add one to last sequence number
			open(FILE,">>$filename") or die 'Unable to open config file.';
			flock FILE, 2;
				if ($cgiparams{'ORIG_IP'} eq '0.0.0.0/0') {
					# if the default/all is taken, then write it to the rule
						print FILE "$key1,0,$cgiparams{'PROTOCOL'},$cgiparams{'SRC_PORT'},$cgiparams{'DEST_IP'},$cgiparams{'DEST_PORT'},$cgiparams{'ENABLED'},$cgiparams{'SRC_IP'},$cgiparams{'ORIG_IP'},$cgiparams{'REMARK'}\n";
			} else { # else create an extra record so it shows up 
					print FILE "$key1,0,$cgiparams{'PROTOCOL'},$cgiparams{'SRC_PORT'},$cgiparams{'DEST_IP'},$cgiparams{'DEST_PORT'},$cgiparams{'ENABLED'},$cgiparams{'SRC_IP'},0,$cgiparams{'REMARK'}\n";
						print FILE "$key1,1,$cgiparams{'PROTOCOL'},0,$cgiparams{'DEST_IP'},$cgiparams{'DEST_PORT'},$cgiparams{'ENABLED'},0,$cgiparams{'ORIG_IP'},$cgiparams{'REMARK'}\n";
					}			
			close(FILE);
			undef %cgiparams;
			&General::log($Lang::tr{'forwarding rule added'});
			system('/usr/local/bin/setportfw');
		} else { # else key1 eq 0
			my $insertpoint = ($cgiparams{'KEY2'} - 1);
			open(FILE, ">$filename") or die 'Unable to open config file.';
			flock FILE, 2;
			foreach my $line (@current) {
				chomp($line);
				my @temp = split(/\,/,$line);
				if ($cgiparams{'KEY1'} eq $temp[0] && $insertpoint eq $temp[1]) {
					if ($temp[1] eq "0") { # this is the first xtaccess rule, therefore modify the portfw rule
						$temp[8] = '0';
					}
					print FILE "$temp[0],$temp[1],$temp[2],$temp[3],$temp[4],$temp[5],$temp[6],$temp[7],$temp[8],$temp[9]\n";
					print FILE "$cgiparams{'KEY1'},$cgiparams{'KEY2'},$cgiparams{'PROTOCOL'},0,$cgiparams{'DEST_IP'},$cgiparams{'DEST_PORT'},$cgiparams{'ENABLED'},0,$cgiparams{'ORIG_IP'},$cgiparams{'REMARK'}\n";
				} else {
					print FILE "$line\n";
				}
			}
			close(FILE);
			undef %cgiparams;
			&General::log($Lang::tr{'external access rule added'});
			system('/usr/local/bin/setportfw');
		} # end if if KEY1 eq 0
	} # end unless($errormessage)
}

if ($cgiparams{'ACTION'} eq $Lang::tr{'update'})
{
	&valaddupdate();
	
	# Darren Critchley - If there is an error don't waste any more processing time
	if ($errormessage) { $cgiparams{'ACTION'} = $Lang::tr{'edit'}; goto UPD_ERROR; }

	open(FILE, $filename) or die 'Unable to open config file.';
	my @current = <FILE>;
	close(FILE);
	my $disabledpfw = '0';
	my $lastpfw = '';
	my $xtaccessdel = '0';
	
	foreach my $line (@current)
	{
		my @temp = split(/\,/,$line);
		if ( $temp[1] eq "0" ) { # keep track of the last portfw and if it is enabled
			$disabledpfw = $temp[6];
			$lastpfw = $temp[0];
		}		
		chomp ($temp[8]);
		if ( $cgiparams{'SRC_PORT'} eq $temp[3] &&
			$cgiparams{'PROTOCOL'} eq $temp[2] &&
			$cgiparams{'SRC_IP'} eq $temp[7])
		{
			 if ($cgiparams{'KEY1'} ne $temp[0] && $cgiparams{'KEY2'} eq "0")
			 { 
			 $errormessage =  
				"$Lang::tr{'source port in use'} $cgiparams{'SRC_PORT'}";
			 }
		}
		if ($cgiparams{'ORIG_IP'} eq $temp[8]) 
		{
			 if ($cgiparams{'KEY1'} eq $temp[0] && $cgiparams{'KEY2'} ne $temp[1])
			 # If we have the same source ip within a portfw group, then we have a problem!
			 {
				$errormessage =  "$Lang::tr{'source ip in use'} $cgiparams{'ORIG_IP'}";
				$cgiparams{'ACTION'} = $Lang::tr{'edit'};
			 }
		}
		
		# Darren Critchley - Flag when a user disables an xtaccess
		if ($cgiparams{'KEY1'} eq $temp[0] &&
				$cgiparams{'KEY2'} eq $temp[1] &&
				$cgiparams{'KEY2'} ne "0" && # if KEY2 is 0 then it is a portfw
				$cgiparams{'ENABLED'} eq "off" &&
				$temp[6] eq "on") { # we have determined that someone has turned an xtaccess off
			$xtaccessdel = "1";		
		}
		
		# Darren Critchley - Portfw enabled, then enable xtaccess for all associated xtaccess records
		if ($cgiparams{'ENABLED'} eq "on" && $cgiparams{'KEY2'} eq "0" && $cgiparams{'ENABLED'} ne $temp[6]) 
		{
			$enable_all = "1";
		} else {
			$enable_all = "0";
		}
		# Darren Critchley - Portfw disabled, then disable xtaccess for all associated xtaccess records
		if ($cgiparams{'ENABLED'} eq "off" && $cgiparams{'KEY2'} eq "0") 
		{
			$disable_all = "1";
		} else {
			$disable_all = "0";
		}

		# Darren Critchley - if we are enabling an xtaccess, only allow if the associated Portfw is enabled
		if ($cgiparams{'KEY1'} eq $lastpfw && $cgiparams{'KEY2'} ne "0") { # identifies an xtaccess record in the group
			if ($cgiparams{'ENABLED'} eq "on" && $cgiparams{'ENABLED'} ne $temp[6] ){ # a change has been made
				if ($disabledpfw eq "off")
				{ 
					$errormessage =  "$Lang::tr{'cant enable xtaccess'}";
					$cgiparams{'ACTION'} = $Lang::tr{'edit'};
				}
			}
		}
		
		# Darren Critchley - rule to stop someone from entering ALL into a external access rule, 
		# the portfw is the only place that ALL can be specified
		if ($cgiparams{'KEY2'} ne "0" && $cgiparams{'ORIG_IP'} eq "0.0.0.0/0") {
			$errormessage =  "$Lang::tr{'xtaccess all error'}";
			$cgiparams{'ACTION'} = $Lang::tr{'edit'};
		}
		
		# Darren Critchley - Duplicate or overlapping Port range check
		if ($temp[1] eq "0" &&
			$cgiparams{'KEY1'} ne $temp[0] && 
			$cgiparams{'PROTOCOL'} eq $temp[2] &&
			$cgiparams{'SRC_IP'} eq $temp[7] &&
			$errormessage eq '') 
		{
				&portchecks($temp[3], $temp[5]);
		} # end port testing
		
	}
	
	# Darren Critchley - if an xtaccess was disabled, now we need to check to see if it was the only xtaccess
	if($xtaccessdel eq "1") {
		my $xctr = 0;
		foreach my $line (@current)
		{
			my @temp = split(/\,/,$line);
			if($temp[0] eq $cgiparams{'KEY1'} &&
				$temp[6] eq "on") { # we only want to count the enabled xtaccess's
				$xctr++;
			}
		}
		if ($xctr == 2){
			$disable_all = "1";
		}
	}

UPD_ERROR:
	unless ($errormessage)
	{
		# Darren Critchley - we only want to store ranges with Colons
		$cgiparams{'SRC_PORT'} =~ tr/-/:/; 
		$cgiparams{'DEST_PORT'} =~ tr/-/:/;

		open(FILE, ">$filename") or die 'Unable to open config file.';
		flock FILE, 2;
		foreach my $line (@current) {
			chomp($line);
			my @temp = split(/\,/,$line);
			if ($cgiparams{'KEY1'} eq $temp[0] && $cgiparams{'KEY2'} eq $temp[1]) {
		print FILE "$cgiparams{'KEY1'},$cgiparams{'KEY2'},$cgiparams{'PROTOCOL'},$cgiparams{'SRC_PORT'},$cgiparams{'DEST_IP'},$cgiparams{'DEST_PORT'},$cgiparams{'ENABLED'},$cgiparams{'SRC_IP'},$cgiparams{'ORIG_IP'},$cgiparams{'REMARK'}\n";
			} else {
				# Darren Critchley - If it is a port forward record, then chances are good that a change was made to 
				# Destination Ip or Port, and we need to update all the associated external access records
				if ($cgiparams{'KEY2'} eq "0" && $cgiparams{'KEY1'} eq $temp[0]) {
					$temp[4] = $cgiparams{'DEST_IP'};
					$temp[5] = $cgiparams{'DEST_PORT'};
					$temp[2] = $cgiparams{'PROTOCOL'};
				}
				
				# Darren Critchley - If a Portfw has been disabled, then set all associated xtaccess as disabled
				if ( $disable_all eq "1" && $cgiparams{'KEY1'} eq $temp[0] ) {
					$temp[6] = 'off';
				}
				if ( $enable_all eq "1" && $cgiparams{'KEY1'} eq $temp[0] ) {
					$temp[6] = 'on';
				}
				# Darren Critchley - Deal with the override to allow ALL
				if ( $cgiparams{'OVERRIDE'} eq "on" && $temp[1] ne "0" && $cgiparams{'KEY1'} eq $temp[0] ) {
					$temp[6] = 'off';
				}
			print FILE "$temp[0],$temp[1],$temp[2],$temp[3],$temp[4],$temp[5],$temp[6],$temp[7],$temp[8],$temp[9]\n";
			}
		}
		close(FILE);
		undef %cgiparams;
		&General::log($Lang::tr{'forwarding rule updated'});
		system('/usr/local/bin/setportfw');
	} 
	if ($errormessage) {
	$cgiparams{'ACTION'} = $Lang::tr{'edit'};
	}
}

# Darren Critchley - Allows rules to be enabled and disabled
if ($cgiparams{'ACTION'} eq $Lang::tr{'toggle enable disable'})
{
	open(FILE, $filename) or die 'Unable to open config file.';
	my @current = <FILE>;
	close(FILE);
	my $disabledpfw = '0';
	my $lastpfw = '';
	my $xtaccessdel = '0';
	
	foreach my $line (@current)
	{
		my @temp = split(/\,/,$line);
		if ( $temp[1] eq "0" ) { # keep track of the last portfw and if it is enabled
			$disabledpfw = $temp[6];
			$lastpfw = $temp[0];
		}		
		# Darren Critchley - Flag when a user disables an xtaccess
		if ($cgiparams{'KEY1'} eq $temp[0] &&
				$cgiparams{'KEY2'} eq $temp[1] &&
				$cgiparams{'KEY2'} ne "0" && # if KEY2 is 0 then it is a portfw
				$cgiparams{'ENABLED'} eq "off" &&
				$temp[6] eq "on") { # we have determined that someone has turned an xtaccess off
			$xtaccessdel = "1";		
		}
		
		# Darren Critchley - Portfw enabled, then enable xtaccess for all associated xtaccess records
		if ($cgiparams{'ENABLED'} eq "on" && $cgiparams{'KEY2'} eq "0" && $cgiparams{'ENABLED'} ne $temp[6]) 
		{
			$enable_all = "1";
		} else {
			$enable_all = "0";
		}
		# Darren Critchley - Portfw disabled, then disable xtaccess for all associated xtaccess records
		if ($cgiparams{'ENABLED'} eq "off" && $cgiparams{'KEY2'} eq "0") 
		{
			$disable_all = "1";
		} else {
			$disable_all = "0";
		}

		# Darren Critchley - if we are enabling an xtaccess, only allow if the associated Portfw is enabled
		if ($cgiparams{'KEY1'} eq $lastpfw && $cgiparams{'KEY2'} ne "0") { # identifies an xtaccess record in the group
			if ($cgiparams{'ENABLED'} eq "on" && $cgiparams{'ENABLED'} ne $temp[6] ){ # a change has been made
				if ($disabledpfw eq "off")
				{ 
					$errormessage =  "$Lang::tr{'cant enable xtaccess'}";
					goto TOGGLEEXIT;
				}
			}
		}
	}
	
	# Darren Critchley - if an xtaccess was disabled, now we need to check to see if it was the only xtaccess
	if($xtaccessdel eq "1") {
		my $xctr = 0;
		foreach my $line (@current)
		{
			my @temp = split(/\,/,$line);
			if($temp[0] eq $cgiparams{'KEY1'} &&
				$temp[6] eq "on") { # we only want to count the enabled xtaccess's
				$xctr++;
			}
		}
		if ($xctr == 2){
			$disable_all = "1";
		}
	}

	open(FILE, ">$filename") or die 'Unable to open config file.';
	flock FILE, 2;
	foreach my $line (@current) {
		chomp($line);
		my @temp = split(/\,/,$line);
		if ($cgiparams{'KEY1'} eq $temp[0] && $cgiparams{'KEY2'} eq $temp[1]) {
		print FILE "$cgiparams{'KEY1'},$cgiparams{'KEY2'},$temp[2],$temp[3],$temp[4],$temp[5],$cgiparams{'ENABLED'},$temp[7],$temp[8],$temp[9]\n";
		} else {
			# Darren Critchley - If a Portfw has been disabled, then set all associated xtaccess as disabled
			if ( $disable_all eq "1" && $cgiparams{'KEY1'} eq $temp[0] ) {
				$temp[6] = 'off';
			}
			if ( $enable_all eq "1" && $cgiparams{'KEY1'} eq $temp[0] ) {
				$temp[6] = 'on';
			}
		print FILE "$temp[0],$temp[1],$temp[2],$temp[3],$temp[4],$temp[5],$temp[6],$temp[7],$temp[8],$temp[9]\n";
		}
	}
	close(FILE);
	&General::log($Lang::tr{'forwarding rule updated'});
	system('/usr/local/bin/setportfw');
TOGGLEEXIT:
	undef %cgiparams;
} 


# Darren Critchley - broke out Edit routine from the delete routine - Edit routine now just puts values in fields
if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'})
{
	open(FILE, "$filename") or die 'Unable to open config file.';
	my @current = <FILE>;
	close(FILE);

	unless ($errormessage)
	{
		foreach my $line (@current)
		{
			chomp($line);
			my @temp = split(/\,/,$line);
			if ($cgiparams{'KEY1'} eq $temp[0] && $cgiparams{'KEY2'} eq $temp[1] ) {
				$cgiparams{'PROTOCOL'} = $temp[2];
				$cgiparams{'SRC_PORT'} = $temp[3];
				$cgiparams{'DEST_IP'} = $temp[4];
				$cgiparams{'DEST_PORT'} = $temp[5];
				$cgiparams{'ENABLED'} = $temp[6];
				$cgiparams{'SRC_IP'} = $temp[7];
				$cgiparams{'ORIG_IP'} = $temp[8];
				$cgiparams{'REMARK'} = $temp[9];
			}
			
		}
	}
}

# Darren Critchley - broke out Remove routine as the logic is getting too complex to be combined with the Edit
if ($cgiparams{'ACTION'} eq $Lang::tr{'remove'})
{
	open(FILE, "$filename") or die 'Unable to open config file.';
	my @current = <FILE>;
	close(FILE);
	
	# If the record being deleted is an xtaccess record, and it is the only one for a portfw record
	# then we need to adjust the portfw record to be open to ALL ip addressess or an error will occur
	# in setportfw.c
	my $fixportfw = '0';
	if ($cgiparams{'KEY2'} ne "0") {
		my $counter = 0;
		foreach my $line (@current)
		{
			chomp($line);
			my @temp = split(/\,/,$line);
			if ($temp[0] eq $cgiparams{'KEY1'}) {
				$counter++;
			}
		} 
		if ($counter eq 2) {
			$fixportfw = '1';
		}
	}
	
	unless ($errormessage)
	{
		open(FILE, ">$filename") or die 'Unable to open config file.';
		flock FILE, 2;
		my $linedeleted = 0;
		foreach my $line (@current)
		{
			chomp($line);
			my @temp = split(/\,/,$line);

			if ($cgiparams{'KEY1'} eq $temp[0] && $cgiparams{'KEY2'} eq $temp[1] ||
				$cgiparams{'KEY1'} eq $temp[0] && $cgiparams{'KEY2'} eq "0" ) 
			{
				$linedeleted = 1;
			} else {
				if ($temp[0] eq $cgiparams{'KEY1'} && $temp[1] eq "0" && $fixportfw eq "1") {
					$temp[8] = '0.0.0.0/0';
				}
			print FILE "$temp[0],$temp[1],$temp[2],$temp[3],$temp[4],$temp[5],$temp[6],$temp[7],$temp[8],$temp[9]\n";
#				print FILE "$line\n";
			}
		}
		close(FILE);
		if ($linedeleted == 1) {
			&General::log($Lang::tr{'forwarding rule removed'});
			undef %cgiparams;
		}
		system('/usr/local/bin/setportfw');
	}
}

# Darren Critchley - Added routine to allow external access rules to be added
if ($cgiparams{'ACTION'} eq $Lang::tr{'add xtaccess'})
{
	open(FILE, $filename) or die 'Unable to open config file.';
	my @current = <FILE>;
	close(FILE);
	my $key = 0; # used for finding last sequence number used 
	foreach my $line (@current)
	{
		my @temp = split(/\,/,$line);
		if ($temp[0] eq $cgiparams{'KEY1'}) {
			$key = $temp[1]
		}
		if ($cgiparams{'KEY1'} eq $temp[0] && $cgiparams{'KEY2'} eq $temp[1] ) {
			$cgiparams{'PROTOCOL'} = $temp[2];
			$cgiparams{'SRC_PORT'} = $temp[3];
			$cgiparams{'DEST_IP'} = $temp[4];
			$cgiparams{'DEST_PORT'} = $temp[5];
			$cgiparams{'ENABLED'} = $temp[6];
			$cgiparams{'SRC_IP'} = $temp[7];
			$cgiparams{'ORIG_IP'} = '';
			$cgiparams{'REMARK'} = $temp[9];
		}
	}
	$key++;
	$cgiparams{'KEY2'} = $key;
	# Until the ADD button is hit, there needs to be no change to portfw rules
}

if ($cgiparams{'ACTION'} eq $Lang::tr{'reset'})
{
	undef %cgiparams;
}

if ($cgiparams{'ACTION'} eq '')
{
	$cgiparams{'PROTOCOL'} = 'tcp';
	$cgiparams{'ENABLED'} = 'on';
	$cgiparams{'SRC_IP'} = '0.0.0.0';
}

$selected{'PROTOCOL'}{'udp'} = '';
$selected{'PROTOCOL'}{'tcp'} = '';
$selected{'PROTOCOL'}{'gre'} = '';
$selected{'PROTOCOL'}{$cgiparams{'PROTOCOL'}} = "selected='selected'";

$selected{'SRC_IP'}{$cgiparams{'SRC_IP'}} = "selected='selected'";

$checked{'ENABLED'}{'off'} = '';
$checked{'ENABLED'}{'on'} = '';  
$checked{'ENABLED'}{$cgiparams{'ENABLED'}} = "checked='checked'";

&Header::openpage($Lang::tr{'port forwarding configuration'}, 1, '');

&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'><font color='${Header::colourred}'>$errormessage\n</font>";
	print "&nbsp;</class>\n";
	&Header::closebox();
}

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'}){
	&Header::openbox('100%', 'left', $Lang::tr{'edit a rule'});
} else {
	&Header::openbox('100%', 'left', $Lang::tr{'add a new rule'});
}

if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'} && $cgiparams{'KEY2'} ne "0" || $cgiparams{'ACTION'} eq $Lang::tr{'add xtaccess'}){ 
# if it is not a port forward record, don't validate as the fields are disabled
	my $PROT = "\U$cgiparams{'PROTOCOL'}\E";
	# Darren Critchley - Format the source and destination ports
	my $dstprt = $cgiparams{'DEST_PORT'};
	$dstprt =~ s/-/ - /;
	$dstprt =~ s/:/ - /;

print <<END
<table>
	<tr>
		<td class='base'>$Lang::tr{'protocol'}: <b>$PROT</b></td>
		<td width='20'>&nbsp;</td>
		<td class='base' align='right'>$Lang::tr{'destination ip'}:&nbsp;</td>
		<td><b>$cgiparams{'DEST_IP'}</b></td>
		<td width='20'>&nbsp;</td>
		<td class='base' align='right'>$Lang::tr{'destination port'}:&nbsp;</td>
		<td><b>$dstprt</b></td>
	</tr>
</table>

<input type='hidden' name='PROTOCOL' value='$cgiparams{'PROTOCOL'}' />
<input type='hidden' name='SRC_IP' value='$cgiparams{'SRC_IP'}' />
<input type='hidden' name='SRC_PORT' value='$cgiparams{'SRC_PORT'}' />
<input type='hidden' name='DEST_IP' value='$cgiparams{'DEST_IP'}' />
<input type='hidden' name='DEST_PORT' value='$cgiparams{'DEST_PORT'}' />
END
;
} else {
print <<END
<table width='100%'>
	<tr>
		<td width='10%'>$Lang::tr{'protocol'}:&nbsp;</td>
		<td width='15%'> 
		<select name='PROTOCOL'>
			<option value='tcp' $selected{'PROTOCOL'}{'tcp'}>TCP</option>
			<option value='udp' $selected{'PROTOCOL'}{'udp'}>UDP</option>
			<option value='gre' $selected{'PROTOCOL'}{'gre'}>GRE</option>
		</select>
		</td>
		<td class='base' width='20%'><font color='${Header::colourred}'>$Lang::tr{'alias ip'}:</font></td>
		<td>
			<select name='SRC_IP'>
			<option value='0.0.0.0' $selected{'SRC_IP'}{'0.0.0.0'}>DEFAULT IP</option>
END
;
open(ALIASES, "$aliasfile") or die 'Unable to open aliases file.';
while (<ALIASES>)
{
	chomp($_);
	my @temp = split(/\,/,$_);
	if ($temp[1] eq 'on') {
		print "<option value='$temp[0]' $selected{'SRC_IP'}{$temp[0]}>$temp[0]";
		if (defined $temp[2] and ($temp[2] ne '')) { print " ($temp[2])"; }
		print "</option>\n";
	}
}
close(ALIASES);
print <<END
			</select>
		</td>
		<td class='base' width='20%'><font color='${Header::colourred}'>$Lang::tr{'source port'}:</font></td>
		<td width='10%'><input type='text' name='SRC_PORT' value='$cgiparams{'SRC_PORT'}' size='8' /></td>
	</tr>
	<tr>
		<td class='base'>&nbsp;</td>
		<td>&nbsp;</td>
		<td class='base'>$Lang::tr{'destination ip'}:</td>
		<td><input type='text' name='DEST_IP' value='$cgiparams{'DEST_IP'}' size='15' /></td>
		<td class='base'>$Lang::tr{'destination port'}:</td>
		<td><input type='text' name='DEST_PORT' value='$cgiparams{'DEST_PORT'}' size='8' /></td>
	</tr>
</table>
END
;
}

print <<END
<table>
	<tr>
		<td class='base'>$Lang::tr{'remark title'}&nbsp;<img src='/blob.gif' alt='*' />&nbsp;</td>
		<td><input type='text' name='REMARK' value='$cgiparams{'REMARK'}' size='55' maxlength='50' /></td>
END
;
unless ($cgiparams{'ACTION'} eq $Lang::tr{'add xtaccess'} && $cgiparams{'ENABLED'} eq "off") {
	print "<td width='20'>&nbsp;</td>";
	print "<td>$Lang::tr{'enabled'}&nbsp;</td><td><input type='checkbox' name='ENABLED' $checked{'ENABLED'}{'on'} /></td>\n";
}
print <<END
	</tr>
</table>
END
;

if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'} && $cgiparams{'KEY2'} eq "0" && ($cgiparams{'ORIG_IP'} eq "0" || $cgiparams{'ORIG_IP'} eq "0.0.0.0/0")){ 
# if it is a port forward rule with a 0 in the orig_port field, this means there are xtaccess records, and we
# don't want to allow a person to change the orig_ip field as it will mess other logic up
	print "<input type='hidden' name='ORIG_IP' value='$cgiparams{'ORIG_IP'}' />\n";
} else {
print <<END
<table>
	<tr>
		<td class='base'><font class='boldbase' color='${Header::colourred}'>$Lang::tr{'source network'}</font>&nbsp;<img src='/blob.gif' alt='*' />&nbsp;</td>
		<td><input type='text' name='ORIG_IP' value='$cgiparams{'ORIG_IP'}' size='15' /></td>
	</tr>
</table>
END
;
}

print <<END
<table width='100%'>
	<hr />
	<tr>
		<td class='base' width='25%'><img src='/blob.gif' alt ='*' align='top' />&nbsp;<font class='base'>$Lang::tr{'this field may be blank'}</font></td>
END
;


if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'}){
	if($cgiparams{'KEY2'} eq "0"){
		print "<td width='35%' align='right'>$Lang::tr{'open to all'}:&nbsp;</td><td width='5%'><input type='checkbox' name='OVERRIDE' $checked{'OVERRIDE'}{'on'} /></td>\n";
	} else {
		print "<td width='40%'>&nbsp;</td>\n";
	}
	print "<td align='center' width='15%'><input type='submit' name='ACTION' value='$Lang::tr{'update'}' />";
	print "<input type='hidden' name='KEY1' value='$cgiparams{'KEY1'}' />";
	print "<input type='hidden' name='KEY2' value='$cgiparams{'KEY2'}' /></TD>";
	print "<td align='center' width='15%'><input type='submit' name='ACTION' value='$Lang::tr{'reset'}' /></td>";
	# on an edit and an xtaccess add, for some reason the "Reset" button stops working, so I make it a submit button
} else {
	print "<td width='30%'>&nbsp;</td>\n";
	print "<td align='center' width='15%'><input type='submit' name='ACTION' value='$Lang::tr{'add'}' /></td>";
	if ($cgiparams{'ACTION'} eq $Lang::tr{'add xtaccess'}) {
		print "<td align='center' width='15%'><input type='hidden' name='KEY1' value='$cgiparams{'KEY1'}' />";
		print "<input type='hidden' name='KEY2' value='$cgiparams{'KEY2'}' />";
		print "<input type='submit' name='ACTION' value='$Lang::tr{'reset'}' /></td>";
	} elsif ($errormessage ne '') {
		print "<td align='center' width='15%'><input type='submit' name='ACTION' value='$Lang::tr{'reset'}' /></td>";
	} else {
		print "<td align='center' width='15%'><input type='reset' name='ACTION' value='$Lang::tr{'reset'}' /></td>";
	}
}
print <<END
	<td width='5%' align='right'>&nbsp;</td>
	</tr>
</table>
END
;
&Header::closebox();

print "</form>\n";

&Header::openbox('100%', 'left', $Lang::tr{'current rules'});
print <<END
<table width='100%'>
<tr>
<td width='7%' class='boldbase' align='center'><b>$Lang::tr{'proto'}</b></td>
<td width='31%' class='boldbase' align='center'><b>$Lang::tr{'source'}</b></td>
<td width='2%' class='boldbase' align='center'>&nbsp;</td>
<td width='31%' class='boldbase' align='center'><b>$Lang::tr{'destination'}</b></td>
<td width='24%' class='boldbase' align='center'><b>$Lang::tr{'remark'}</b></td>
<td width='4%' class='boldbase' colspan='4' align='center'><b>$Lang::tr{'action'}</b></td>
</tr>
END
;

my $id = 0;
my $xtaccesscolor = '#F6F4F4';
open(RULES, "$filename") or die 'Unable to open config file.';
while (<RULES>)
{
	my $protocol = '';
	my $gif = '';
	my $gdesc = '';
	my $toggle = '';
	chomp($_);
	my @temp = split(/\,/,$_);
	$temp[9] ='' unless defined $temp[9];# Glles ESpinasse : suppress warning on page init
	if ($temp[2] eq 'udp') {
		$protocol = 'UDP'; }
	elsif ($temp[2] eq 'gre') {
		$protocol = 'GRE' }
	else {
		$protocol = 'TCP' }
	# Change bgcolor when a new portfw rule is added
	if ($temp[1] eq "0"){
		$id++;
	}
	# Darren Critchley highlight the row we are editing
	if ( $cgiparams{'ACTION'} eq $Lang::tr{'edit'} && $cgiparams{'KEY1'} eq $temp[0] && $cgiparams{'KEY2'} eq $temp[1] ) { 
		print "<tr bgcolor='${Header::colouryellow}'>\n";
	} else {
		if ($id % 2) {
			print "<tr bgcolor='$color{'color22'}'>\n"; 
		}
		else {
			print "<tr bgcolor='$color{'color20'}'>\n";
		}
	}
	
	if ($temp[6] eq 'on') { $gif = 'on.gif'; $toggle='off'; $gdesc=$Lang::tr{'click to disable'};}
		else { $gif = 'off.gif'; $toggle='on'; $gdesc=$Lang::tr{'click to enable'}; }

		# Darren Critchley - this code no longer works - should we remove?
	# catch for 'old-style' rules file - assume default ip if
	# none exists
	if (!&General::validip($temp[7]) || $temp[7] eq '0.0.0.0') {
		$temp[7] = 'DEFAULT IP'; }
		if ($temp[1] eq '0') { # Port forwarding entry

		# Darren Critchley - Format the source and destintation ports
		my $srcprt = $temp[3];
		$srcprt =~ s/-/ - /;
		$srcprt =~ s/:/ - /;
		my $dstprt = $temp[5];
		$dstprt =~ s/-/ - /;
		$dstprt =~ s/:/ - /;

		# Darren Critchley - Get Port Service Name if we can - code borrowed from firewalllog.dat
		$_=$temp[3];
		if (/^\d+$/) {
			my $servi = uc(getservbyport($temp[3], lc($temp[2])));
			if ($servi ne '' && $temp[3] < 1024) {
				$srcprt = "$srcprt($servi)"; }
		}
		$_=$temp[5];
		if (/^\d+$/) {
			my $servi = uc(getservbyport($temp[5], lc($temp[2])));
			if ($servi ne '' && $temp[5] < 1024) {
				$dstprt = "$dstprt($servi)"; }
		}

		# Darren Critchley - If the line is too long, wrap the port numbers
		my $srcaddr = "$temp[7] : $srcprt";
		if (length($srcaddr) > 22) {
			$srcaddr = "$temp[7] :<br /> $srcprt";
		}
		my $dstaddr = "$temp[4] : $dstprt";
		if (length($dstaddr) > 26) {
			$dstaddr = "$temp[4] :<br /> $dstprt";
		}
print <<END
<td align='center'>$protocol</td>
<td align='center'>$srcaddr</td>
<td align='center'><img src='/images/forward.gif' alt='=&gt;' /></td>
<td align='center'>$dstaddr</td>
<td align='left'>&nbsp;$temp[9]</td>
<td align='center'>
	<form method='post' name='frm$temp[0]c' action='$ENV{'SCRIPT_NAME'}'>
	<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' alt='$gdesc' title='$gdesc' />
	<input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}' />
	<input type='hidden' name='KEY1' value='$temp[0]' />
	<input type='hidden' name='KEY2' value='$temp[1]' />
	<input type='hidden' name='ENABLED' value='$toggle' />
	</form>
</td>

<td align='center'>
	<form method='post' name='frm$temp[0]' action='$ENV{'SCRIPT_NAME'}'>
	<input type='hidden' name='ACTION' value='$Lang::tr{'add xtaccess'}' />
	<input type='image' name='$Lang::tr{'add xtaccess'}' src='/images/add.gif' alt='$Lang::tr{'add xtaccess'}' title='$Lang::tr{'add xtaccess'}' />
	<input type='hidden' name='KEY1' value='$temp[0]' />
	<input type='hidden' name='KEY2' value='$temp[1]' />
	</form>
</td>

<td align='center'>
	<form method='post' name='frm$temp[0]' action='$ENV{'SCRIPT_NAME'}'>
	<input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
	<input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' />
	<input type='hidden' name='KEY1' value='$temp[0]' />
	<input type='hidden' name='KEY2' value='$temp[1]' />
	</form>
</td>

<td align='center'>
	<form method='post' name='frm$temp[0]b' action='$ENV{'SCRIPT_NAME'}'>
	<input type='hidden' name='ACTION' value='$Lang::tr{'remove'}' />
	<input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' alt='$Lang::tr{'remove'}' title='$Lang::tr{'remove'}' />
	<input type='hidden' name='KEY1' value='$temp[0]' />
	<input type='hidden' name='KEY2' value='$temp[1]' />
	</form>
</td>

</tr>
END
	;
	} else { # external access entry
print <<END
<td align='center'>&nbsp;</td>

<td align='left' colspan='4'>&nbsp;<font color='${Header::colourred}'>$Lang::tr{'access allowed'}</font> $temp[8]&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;($temp[9])</td>

<td align='center'>
	<form method='post' name='frm$temp[0]$temp[1]t' action='$ENV{'SCRIPT_NAME'}'>
	<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' alt='$Lang::tr{'toggle enable disable'}' title='$Lang::tr{'toggle enable disable'}' />
	<input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}' />
	<input type='hidden' name='KEY1' value='$temp[0]' />
	<input type='hidden' name='KEY2' value='$temp[1]' />
	<input type='hidden' name='ENABLED' value='$toggle' />
	</form>
</td>

<td align='center'>&nbsp;</td>

<td align='center'>
	<form method='post' name='frm$temp[0]$temp[1]' action='$ENV{'SCRIPT_NAME'}'>
	<input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
	<input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' />
	<input type='hidden' name='KEY1' value='$temp[0]' />
	<input type='hidden' name='KEY2' value='$temp[1]' />
	</form>
</td>

<td align='center'>
	<form method='post' name='frm$temp[0]b$temp[1]b' action='$ENV{'SCRIPT_NAME'}'>
	<input type='hidden' name='ACTION' value='$Lang::tr{'remove'}' />
	<input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' alt='$Lang::tr{'remove'}' title='$Lang::tr{'remove'}' />
	<input type='hidden' name='KEY1' value='$temp[0]' />
	<input type='hidden' name='KEY2' value='$temp[1]' />
	</form>
</td>

</tr>
END
	;
	}
}

close(RULES);

print "</table>";

# If the fixed lease file contains entries, print Key to action icons
if ( ! -z "$filename") {
print <<END
<table>
<tr>
	<td class='boldbase'>&nbsp;<b>$Lang::tr{'legend'}:&nbsp;</b></td>
	<td><img src='/images/on.gif' alt='$Lang::tr{'click to disable'}' /></td>
	<td class='base'>$Lang::tr{'click to disable'}</td>
	<td>&nbsp;&nbsp;</td>
	<td><img src='/images/off.gif' alt='$Lang::tr{'click to enable'}' /></td>
	<td class='base'>$Lang::tr{'click to enable'}</td>
	<td>&nbsp;&nbsp;</td>
	<td><img src='/images/add.gif' alt='$Lang::tr{'add xtaccess'}' /></td>
	<td class='base'>$Lang::tr{'add xtaccess'}</td>
	<td>&nbsp;&nbsp;</td>
	<td><img src='/images/edit.gif' alt='$Lang::tr{'edit'}' /></td>
	<td class='base'>$Lang::tr{'edit'}</td>
	<td>&nbsp;&nbsp;</td>
	<td><img src='/images/delete.gif' alt='$Lang::tr{'remove'}' /></td>
	<td class='base'>$Lang::tr{'remove'}</td>
</tr>
</table>
END
;
}

&Header::closebox();

&Header::closebigbox();

&Header::closepage();

# Validate Field Entries
sub validateparams 
{
	# Darren Critchley - Get rid of dashes in port ranges
	$cgiparams{'DEST_PORT'}=~ tr/-/:/;
	$cgiparams{'SRC_PORT'}=~ tr/-/:/;
	
	# Darren Critchley - code to substitue wildcards
	if ($cgiparams{'SRC_PORT'} eq "*") {
		$cgiparams{'SRC_PORT'} = "1:65535";
	}
	if ($cgiparams{'SRC_PORT'} =~ /^(\D)\:(\d+)$/) {
		$cgiparams{'SRC_PORT'} = "1:$2";
	}
	if ($cgiparams{'SRC_PORT'} =~ /^(\d+)\:(\D)$/) {
		$cgiparams{'SRC_PORT'} = "$1:65535";
	}
	if ($cgiparams{'DEST_PORT'} eq "*") {
		$cgiparams{'DEST_PORT'} = "1:65535";
	}
	if ($cgiparams{'DEST_PORT'} =~ /^(\D)\:(\d+)$/) {
		$cgiparams{'DEST_PORT'} = "1:$2";
	}
	if ($cgiparams{'DEST_PORT'} =~ /^(\d+)\:(\D)$/) {
		$cgiparams{'DEST_PORT'} = "$1:65535";
	}

	# Darren Critchley - Add code for GRE protocol - we want to ignore ports, but we need a place holder
	if ($cgiparams{'PROTOCOL'} eq 'gre') {
		$cgiparams{'SRC_PORT'} = "GRE";
		$cgiparams{'DEST_PORT'} = "GRE";
	}

	unless($cgiparams{'PROTOCOL'} =~ /^(tcp|udp|gre)$/) { $errormessage = $Lang::tr{'invalid input'}; }
	# Darren Critchley - Changed how the error routine works a bit - for the validportrange check, we need to 
	# pass in src or dest to determine which side we are working with.
	# the routine returns the complete error or ''
	if ($cgiparams{'PROTOCOL'} ne 'gre') {
		$errormessage = &General::validportrange($cgiparams{'SRC_PORT'}, 'src');
	}
	if( ($cgiparams{'ORIG_IP'} ne "0" && $cgiparams{'KEY2'} ne "0") || $cgiparams{'ACTION'} eq $Lang::tr{'add'}) { 
	# if it is a port forward record with 0 in orig_ip then ignore checking this field
		unless(&General::validipormask($cgiparams{'ORIG_IP'}))
		{
			if ($cgiparams{'ORIG_IP'} ne '') {
				$errormessage = $Lang::tr{'source ip bad'}; }
			else {
				$cgiparams{'ORIG_IP'} = '0.0.0.0/0'; }
		}
	}
	# Darren Critchey - New rule that sets destination same as source if dest_port is blank.
	if ($cgiparams{'DEST_PORT'} eq ''){
		$cgiparams{'DEST_PORT'} = $cgiparams{'SRC_PORT'};
	}
	# Darren Critchey - Just in case error message is already set, this routine would wipe it out if
	# we don't do a test here
	if ($cgiparams{'PROTOCOL'} ne 'gre') {
		unless($errormessage) {$errormessage = &General::validportrange($cgiparams{'DEST_PORT'}, 'dest');}
	}
	unless(&General::validip($cgiparams{'DEST_IP'})) { $errormessage = $Lang::tr{'destination ip bad'}; }
	return;
}

# Darren Critchley - we want to make sure that a port range does not overlap another port range
sub checkportoverlap
{
	my $portrange1 = $_[0]; # New port range
	my $portrange2 = $_[1]; # existing port range
	my @tempr1 = split(/\:/,$portrange1);
	my @tempr2 = split(/\:/,$portrange2);

	unless (&checkportinc($tempr1[0], $portrange2)){ return 0;}
	unless (&checkportinc($tempr1[1], $portrange2)){ return 0;}
	
	unless (&checkportinc($tempr2[0], $portrange1)){ return 0;}
	unless (&checkportinc($tempr2[1], $portrange1)){ return 0;}

	return 1; # Everything checks out!
}

# Darren Critchley - we want to make sure that a port entry is not within an already existing range
sub checkportinc
{
	my $port1 = $_[0]; # Port
	my $portrange2 = $_[1]; # Port range
	my @tempr1 = split(/\:/,$portrange2);

	if ($port1 < $tempr1[0] || $port1 > $tempr1[1]) {
		return 1; 
	} else {
		return 0; 
	}
}

# Darren Critchley - certain ports are reserved for Ipcop 
# TCP 67,68,81,222,445
# UDP 67,68
# Params passed in -> port, rangeyn, protocol
sub disallowreserved
{
	# port 67 and 68 same for tcp and udp, don't bother putting in an array
	my $msg = "";
	my @tcp_reserved = ();
	my $prt = $_[0]; # the port or range
	my $ryn = $_[1]; # tells us whether or not it is a port range
	my $prot = $_[2]; # protocol
	my $srcdst = $_[3]; # source or destination
	
	if ($ryn) { # disect port range
		if ($srcdst eq "src") {
			$msg = "$Lang::tr{'rsvd src port overlap'}";
		} else {
			$msg = "$Lang::tr{'rsvd dst port overlap'}";
		}
		my @tmprng = split(/\:/,$prt);
		unless (67 < $tmprng[0] || 67 > $tmprng[1]) { $errormessage="$msg 67"; return; }
		unless (68 < $tmprng[0] || 68 > $tmprng[1]) { $errormessage="$msg 68"; return; }
		if ($prot eq "tcp") {
			foreach my $prange (@tcp_reserved) {
				unless ($prange < $tmprng[0] || $prange > $tmprng[1]) { $errormessage="$msg $prange"; return; }
			}
		}
	} else {
		if ($srcdst eq "src") {
			$msg = "$Lang::tr{'reserved src port'}";
		} else {
			$msg = "$Lang::tr{'reserved dst port'}";
		}
		if ($prt == 67) { $errormessage="$msg 67"; return; }
		if ($prt == 68) { $errormessage="$msg 68"; return; }
		if ($prot eq "tcp") {
			foreach my $prange (@tcp_reserved) {
				if ($prange == $prt) { $errormessage="$msg $prange"; return; }
			}
		}
	}
	return;
}

# Darren Critchley - Attempt to combine Add/Update validation as they are almost the same
sub valaddupdate
{
	if ($cgiparams{'KEY2'} eq "0"){ # if it is a port forward rule, then validate properly
		&validateparams();
	} else { # it is an xtaccess rule, just check for a valid ip
		unless(&General::validipormask($cgiparams{'ORIG_IP'}))
		{
			if ($cgiparams{'ORIG_IP'} ne '') {
				$errormessage = $Lang::tr{'source ip bad'}; }
			else { # this rule stops someone from adding an ALL xtaccess record
				$errormessage = $Lang::tr{'xtaccess all error'}; 
				$cgiparams{'ACTION'} = $Lang::tr{'add xtaccess'};
			}
		}
		# Darren Critchley - check for 0.0.0.0/0 - not allowed for xtaccess
		if ($cgiparams{'ORIG_IP'} eq "0.0.0.0/0" || $cgiparams{'ORIG_IP'} eq "0.0.0.0") {
			$errormessage = $Lang::tr{'xtaccess all error'}; 
			$cgiparams{'ACTION'} = $Lang::tr{'add xtaccess'};
		}
	}
	# Darren Critchley - Remove commas from remarks
	$cgiparams{'REMARK'} = &Header::cleanhtml($cgiparams{'REMARK'});

	# Darren Critchley - Check to see if we are working with port ranges
	our ($prtrange1, $prtrange2);
	$_ = $cgiparams{'SRC_PORT'};
	if ($cgiparams{'KEY2'} eq "0" && m/:/){
		$prtrange1 = 1;
	}
	if ($cgiparams{'SRC_IP'} eq '0.0.0.0') { # Dave Roberts - only check if using DEFAULT IP
		if ($prtrange1 == 1){ # check for source ports reserved for Ipcop
			&disallowreserved($cgiparams{'SRC_PORT'},1,$cgiparams{'PROTOCOL'},"src");
			if ($errormessage) { goto EXITSUB; }
		} else { # check for source port reserved for Ipcop
			&disallowreserved($cgiparams{'SRC_PORT'},0,$cgiparams{'PROTOCOL'},"src");
			if ($errormessage) { goto EXITSUB; }
		}
	}
	
	$_ = $cgiparams{'DEST_PORT'};
	if ($cgiparams{'KEY2'} eq "0" && m/:/){
		$prtrange2 = 1;
	}
	if ($cgiparams{'SRC_IP'} eq '0.0.0.0') { # Dave Roberts - only check if using DEFAULT IP
		if ($prtrange2 == 1){ # check for destination ports reserved for IPFire
			&disallowreserved($cgiparams{'DEST_PORT'},1,$cgiparams{'PROTOCOL'},"dst");
			if ($errormessage) { goto EXITSUB; }
		} else { # check for destination port reserved for IPFire
			&disallowreserved($cgiparams{'DEST_PORT'},0,$cgiparams{'PROTOCOL'},"dst");
			if ($errormessage) { goto EXITSUB; }
		}
	}
	

EXITSUB:
	return;
}

# Darren Critchley - Duplicate or overlapping Port range check
sub portchecks
{
	$_ = $_[0];
	our ($prtrange1, $prtrange2);
	if (m/:/ && $prtrange1 == 1) { # comparing two port ranges
		unless (&checkportoverlap($cgiparams{'SRC_PORT'},$_[0])) {
			$errormessage = "$Lang::tr{'source port overlaps'} $_[0]";
		}
	}
	if (m/:/ && $prtrange1 == 0 && $errormessage eq '') { # compare one port to a range
		unless (&checkportinc($cgiparams{'SRC_PORT'}, $_[0])) {
			$errormessage = "$Lang::tr{'srcprt within existing'} $_[0]";
		}
	}
	if (! m/:/ && $prtrange1 == 1 && $errormessage eq '') { # compare one port to a range
		unless (&checkportinc($_[0], $cgiparams{'SRC_PORT'})) {
			$errormessage = "$Lang::tr{'srcprt range overlaps'} $_[0]";
		}
	}

	if ($errormessage eq ''){
		$_ = $_[1];
		if (m/:/ && $prtrange2 == 1) { # if true then there is a port range
			unless (&checkportoverlap($cgiparams{'DEST_PORT'},$_[1])) {
				$errormessage = "$Lang::tr{'destination port overlaps'} $_[1]";
			}
		}
		if (m/:/ && $prtrange2 == 0 && $errormessage eq '') { # compare one port to a range
			unless (&checkportinc($cgiparams{'DEST_PORT'}, $_[1])) {
				$errormessage = "$Lang::tr{'dstprt within existing'} $_[1]";
			}
		}
		if (! m/:/ && $prtrange2 == 1 && $errormessage eq '') { # compare one port to a range
			unless (&checkportinc($_[1], $cgiparams{'DEST_PORT'})) {
				$errormessage = "$Lang::tr{'dstprt range overlaps'} $_[1]";
			}
		}
	}
	return;
}
