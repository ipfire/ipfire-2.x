#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2011  IPFire Team  <info@ipfire.org>                     #
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

use RRDs;
use strict;
# enable only the following on debugging purpose
# use warnings;
# use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/graphs.pl";

my %qossettings = ();
my %checked = ();
my %netsettings = ();
my $message = '';
my $errormessage = "";
my $c = "";
my $direntry = "";
my $classentry = "";
my $subclassentry = "";
my $l7ruleentry = "";
my $portruleentry = "";
my $tosruleentry = "";
my @tmp = ();
my @classes = ();
my @subclasses = ();
my @l7rules = ();
my @portrules = ();
my @tosrules = ();
my @tmpline = ();
my @classline = ();
my @subclassline = ();
my @l7ruleline = ();
my @portruleline = ();
my @tosruleline = ();
my @proto = ();
my %selected= ();
my @checked = ();
my $classfile = "/var/ipfire/qos/classes";
my $subclassfile = "/var/ipfire/qos/subclasses";
my $level7file = "/var/ipfire/qos/level7config";
my $portfile = "/var/ipfire/qos/portconfig";
my $tosfile = "/var/ipfire/qos/tosconfig";
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

$qossettings{'ENABLED'} = 'off';
$qossettings{'EDIT'} = 'no';
$qossettings{'OUT_SPD'} = '';
$qossettings{'INC_SPD'} = '';
$qossettings{'DEF_OUT_SPD'} = '';
$qossettings{'DEF_INC_SPD'} = '';
$qossettings{'DEFCLASS_INC'} = '';
$qossettings{'DEFCLASS_OUT'} = '';
$qossettings{'ACK'} = '';
$qossettings{'RED_DEV'} = 'ppp0';
$qossettings{'IMQ_DEV'} = 'imq0';
$qossettings{'VALID'} = 'yes';
### Values that have to be initialized
$qossettings{'ACTION'} = '';
$qossettings{'ACTIONDEF'} = '';
$qossettings{'ACTIONBW'} = '';
$qossettings{'RED_DEV_SEL'} = '';
$qossettings{'IMQ_DEV_SEL'} = '';
$qossettings{'PRIO'} = '';
$qossettings{'SPD'} = '';
$qossettings{'CLASS'} = '';
$qossettings{'SCLASS'} = '';
$qossettings{'QPORT'} = '';
$qossettings{'DPORT'} = '';
$qossettings{'QIP'} = '';
$qossettings{'DIP'} = '';
$qossettings{'PPROT'} = '';
$qossettings{'L7PROT'} = '';
$qossettings{'DEVICE'} = '';
$qossettings{'MINBWDTH'} = '';
$qossettings{'MAXBWDTH'} = '';
$qossettings{'BURST'} = '';
$qossettings{'CBURST'} = '';
$qossettings{'DOCLASS'} = '';
$qossettings{'DOSCLASS'} = '';
$qossettings{'DOLEVEL7'} = '';
$qossettings{'DOPORT'} = '';
$qossettings{'CLASS'} = '';
$qossettings{'CLASSPRFX'} = '';
$qossettings{'DEV'} = '';
$qossettings{'TOS'} = '';


&General::readhash("${General::swroot}/qos/settings", \%qossettings);
&Header::getcgihash(\%qossettings);

$qossettings{'RED_DEV'} = `cat /var/ipfire/red/iface`;

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

my @querry = split(/\?/,$ENV{'QUERY_STRING'});
$querry[0] = '' unless defined $querry[0];
$querry[1] = 'hour' unless defined $querry[1];

if ( $querry[0] ne ""){
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	&Graphs::updateqosgraph($querry[0],$querry[1]);
}else{
	&Header::showhttpheaders();

	&Header::openpage('QoS', 1, '');
	&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
############################################################################################################################

if ($qossettings{'DOCLASS'} eq $Lang::tr{'save'})
{
	&validclass();
	&validminbwdth();
	&validmaxbwdth();
	if ( $qossettings{'VALID'} eq 'yes' ) {
		open( FILE, ">> $classfile" ) or die "Unable to write $classfile";
		print FILE <<END
$qossettings{'DEVICE'};$qossettings{'CLASS'};$qossettings{'PRIO'};$qossettings{'MINBWDTH'};$qossettings{'MAXBWDTH'};$qossettings{'BURST'};$qossettings{'CBURST'};$qossettings{'TOS'};$qossettings{'REMARK'};
END
;
		close FILE;
	} else {
		$qossettings{'ACTION'} = $Lang::tr{'parentclass add'};
	}
}
elsif ($qossettings{'DOCLASS'} eq $Lang::tr{'edit'})
{
	open( FILE, "< $classfile" ) or die "Unable to read $classfile";
	@classes = <FILE>;
	close FILE;
	open( FILE, "> $classfile" ) or die "Unable to write $classfile";
	foreach $classentry (sort @classes)
	{
		@classline = split( /\;/, $classentry );
		if ( $classline[1] ne $qossettings{'CLASS'} ) {
			print FILE $classentry;
		} else {
			$qossettings{'DEVICE'} = $classline[0];
			$qossettings{'PRIO'} = $classline[2];
			$qossettings{'MINBWDTH'} = $classline[3];
			$qossettings{'MAXBWDTH'} = $classline[4];
			$qossettings{'BURST'} = $classline[5];
			$qossettings{'CBURST'} = $classline[6];
			$qossettings{'TOS'} = $classline[7];
			$qossettings{'REMARK'} = $classline[8];
			$qossettings{'EDIT'} = 'yes';
		}
	}
	close FILE;
	&parentclass();
	&Header::closebigbox();
	&Header::closepage();
	exit
}
elsif ($qossettings{'DOCLASS'} eq $Lang::tr{'delete'})
{
	open( FILE, "< $classfile" ) or die "Unable to read $classfile";
	@tmp = <FILE>;
	close FILE;
	open( FILE, "> $classfile" ) or die "Unable to write $classfile";
	foreach $classentry (sort @tmp)
	{
		@tmpline = split( /\;/, $classentry );
		if ( $tmpline[1] ne $qossettings{'CLASS'} )
		{
			print FILE $classentry;
		}
	}
	close FILE;
	open( FILE, "< $subclassfile" ) or die "Unable to read $classfile";
	@tmp = <FILE>;
	close FILE;
	open( FILE, "> $subclassfile" ) or die "Unable to write $classfile";
	foreach $subclassentry (sort @tmp)
	{
		@tmpline = split( /\;/, $subclassentry );
		if ( $tmpline[1] ne $qossettings{'CLASS'} )
		{
			print FILE $subclassentry;
		}
	}
	close FILE;
	$message = "$Lang::tr{'Class'} $qossettings{'CLASS'} $Lang::tr{'Class was deleted'}";
}

############################################################################################################################
############################################################################################################################

if ($qossettings{'DOSCLASS'} eq $Lang::tr{'save'})
{
	&validsubclass();
	&validminbwdth();
	if ( $qossettings{'VALID'} eq 'yes' ) {
		open( FILE, ">> $subclassfile" ) or die "Unable to write $subclassfile";
		print FILE <<END
$qossettings{'DEVICE'};$qossettings{'CLASS'};$qossettings{'SCLASS'};$qossettings{'PRIO'};$qossettings{'MINBWDTH'};$qossettings{'MAXBWDTH'};$qossettings{'BURST'};$qossettings{'CBURST'};$qossettings{'TOS'};
END
;
		close FILE;
	} else {
		$qossettings{'ACTION'} = $Lang::tr{'qos add subclass'};
	}
} elsif ($qossettings{'DOSCLASS'} eq $Lang::tr{'delete'})
{
	open( FILE, "< $subclassfile" ) or die "Unable to read $classfile";
	@tmp = <FILE>;
	close FILE;
	open( FILE, "> $subclassfile" ) or die "Unable to write $classfile";
	foreach $subclassentry (sort @tmp)
	{
		@tmpline = split( /\;/, $subclassentry );
		if ( $tmpline[2] ne $qossettings{'CLASS'} )
		{
			print FILE $subclassentry;
		}
	}
	close FILE;
	$message = "$Lang::tr{'Subclass'} $qossettings{'CLASS'} $Lang::tr{'was deleted'}.";
}

############################################################################################################################
############################################################################################################################

if ($qossettings{'DOLEVEL7'} eq $Lang::tr{'save'})
{
	if ( $qossettings{'QIP'} ne '' ) {
		if ((!&General::validipandmask($qossettings{'QIP'})) && (!&General::validip($qossettings{'QIP'}))) {
			$qossettings{'VALID'} = 'no';
			$message = $Lang::tr{'The source IP address is invalid.'};
		}
	}
	if ( $qossettings{'DIP'} ne '' ) {
		if ((!&General::validipandmask($qossettings{'DIP'})) && (!&General::validip($qossettings{'DIP'}))) {
			$qossettings{'VALID'} = 'no';
			$message = $Lang::tr{'The destination IP address is invalid.'};
		}
	}
	if ($qossettings{'CLASS'} >= 100 && $qossettings{'CLASS'} < 121) {
		$qossettings{'DEVICE'} = $qossettings{'RED_DEV'};
	} elsif ($qossettings{'CLASS'} >= 1000 && $qossettings{'CLASS'} < 1021) {
		$qossettings{'DEVICE'} = $qossettings{'RED_DEV'};
	} elsif ($qossettings{'CLASS'} >= 200 && $qossettings{'CLASS'} < 221) {
		$qossettings{'DEVICE'} = $qossettings{'IMQ_DEV'};
	} elsif ($qossettings{'CLASS'} >= 2000 && $qossettings{'CLASS'} < 2021) {
		$qossettings{'DEVICE'} = $qossettings{'IMQ_DEV'};
	}
	if ( $qossettings{'VALID'} eq 'yes' ) {
		open( FILE, ">> $level7file" ) or die "Unable to write $level7file";
		print FILE <<END
$qossettings{'CLASS'};$qossettings{'DEVICE'};$qossettings{'L7PROT'};$qossettings{'QIP'};$qossettings{'DIP'};
END
;
		close FILE;
	} else {
		$qossettings{'ACTION'} = $Lang::tr{'Add Level7 rule'};
	}
} elsif ($qossettings{'DOLEVEL7'} eq $Lang::tr{'delete'})
{
	open( FILE, "< $level7file" ) or die "Unable to read $level7file";
	@l7rules = <FILE>;
	close FILE;
  system("rm $level7file");
  	foreach $l7ruleentry (sort @l7rules)
  	{
  		@l7ruleline = split( /\;/, $l7ruleentry );
  		if ( ($l7ruleline[0] eq $qossettings{'CLASS'}) && ($l7ruleline[2] eq $qossettings{'L7PROT'}))
            {$message = "$Lang::tr{'Level7 Rule'} ($qossettings{'CLASS'} - $qossettings{'L7PROT'}) $Lang::tr{'was deleted'}.";}
      else
        { open( FILE, ">> $level7file" ) or die "Unable to read $level7file";
          print FILE $l7ruleentry;
	        close FILE;
        }
	  }
	open( FILE, "< $level7file" ) or system("touch $level7file");close FILE;
	} elsif ($qossettings{'DOLEVEL7'} eq $Lang::tr{'edit'})
{
	open( FILE, "< $level7file" ) or die "Unable to read $level7file";
	@l7rules = <FILE>;
	close FILE;
	system("rm $level7file");
  	foreach $l7ruleentry (sort @l7rules)
  	{
  		@l7ruleline = split( /\;/, $l7ruleentry );
  		if ( ($l7ruleline[0] eq $qossettings{'CLASS'}) && ($l7ruleline[2] eq $qossettings{'L7PROT'}))
  		        {$qossettings{'QIP'} = $l7ruleline[3];$qossettings{'DIP'} = $l7ruleline[4];}
  	  else {
		        open( FILE, ">> $level7file" ) or die "Unable to write $level7file";
		        print FILE $l7ruleentry;
		        close FILE;
      }
    }
  &level7rule;
  open( FILE, "< $level7file" ) or system("touch $level7file");close FILE;
 }

############################################################################################################################
############################################################################################################################

if ($qossettings{'DOPORT'} eq $Lang::tr{'save'})
{
	if ( $qossettings{'QIP'} ne '' ) {
		if ((!&General::validipandmask($qossettings{'QIP'})) && (!&General::validip($qossettings{'QIP'}))) {
			$qossettings{'VALID'} = 'no';
			$message = $Lang::tr{'The source IP address is invalid.'};
		}
	}
	if ( $qossettings{'DIP'} ne '' ) {
		if ((!&General::validipandmask($qossettings{'DIP'})) && (!&General::validip($qossettings{'DIP'}))) {
			$qossettings{'VALID'} = 'no';
			$message = $Lang::tr{'The destination IP address is invalid.'};
		}
	}
	if ($qossettings{'CLASS'} >= 100 && $qossettings{'CLASS'} < 121) {
		$qossettings{'DEVICE'} = $qossettings{'RED_DEV'};
	} elsif ($qossettings{'CLASS'} >= 1000 && $qossettings{'CLASS'} < 1021) {
		$qossettings{'DEVICE'} = $qossettings{'RED_DEV'};
	} elsif ($qossettings{'CLASS'} >= 200 && $qossettings{'CLASS'} < 221) {
		$qossettings{'DEVICE'} = $qossettings{'IMQ_DEV'};
	} elsif ($qossettings{'CLASS'} >= 2000 && $qossettings{'CLASS'} < 2021) {
		$qossettings{'DEVICE'} = $qossettings{'IMQ_DEV'};
	}
	if ( $qossettings{'VALID'} eq 'yes' ) {
		open( FILE, ">> $portfile" ) or die "Unable to write $portfile";
		print FILE <<END
$qossettings{'CLASS'};$qossettings{'DEVICE'};$qossettings{'PPROT'};$qossettings{'QIP'};$qossettings{'QPORT'};$qossettings{'DIP'};$qossettings{'DPORT'};
END
;
		close FILE;
	} else {
		$qossettings{'ACTION'} = $Lang::tr{'Add Port Rule'};
	}
} elsif ($qossettings{'DOPORT'} eq $Lang::tr{'delete'})
{
	open( FILE, "< $portfile" ) or die "Unable to read $portfile";
	@portrules = <FILE>;
	close FILE;
	open( FILE, "> $portfile" ) or die "Unable to read $portfile";
  	foreach $portruleentry (sort @portrules)
  	{
  		@portruleline = split( /\;/, $portruleentry );
  		unless ( ($portruleline[0] eq $qossettings{'CLASS'}) && ($portruleline[2] eq $qossettings{'PPROT'}) && ($portruleline[3] eq $qossettings{'QIP'}) && ($portruleline[4] eq $qossettings{'QPORT'}) && ($portruleline[5] eq $qossettings{'DIP'}) && ($portruleline[6] eq $qossettings{'DPORT'}))
  		{
			print FILE $portruleentry;
		}
	}
	close FILE;
	$message = "$Lang::tr{'Port Rule'} ($qossettings{'CLASS'} - $qossettings{'PPROT'}) $Lang::tr{'was deleted'}.";
}  elsif ($qossettings{'DOPORT'} eq $Lang::tr{'edit'})
{
	open( FILE, "< $portfile" ) or die "Unable to read $portfile";
	@portrules = <FILE>;
	close FILE;
	system("rm $portfile");
  	foreach $portruleentry (sort @portrules)
  	{
  		@portruleline = split( /\;/, $portruleentry );
  		if ( ($portruleline[0] eq $qossettings{'CLASS'}) && ($portruleline[2] eq $qossettings{'PPROT'}) && ($portruleline[3] eq $qossettings{'QIP'}) && ($portruleline[4] eq $qossettings{'QPORT'}) && ($portruleline[5] eq $qossettings{'DIP'}) && ($portruleline[6] eq $qossettings{'DPORT'}))
  		        {$qossettings{'CLASS'}=$portruleline[0];$qossettings{'PPROT'}=$portruleline[2];$qossettings{'QIP'}=$portruleline[3];$qossettings{'QPORT'}=$portruleline[4];$qossettings{'DIP'}=$portruleline[5];$qossettings{'DPORT'}=$portruleline[6];}
  	  else {
		        open( FILE, ">> $portfile" ) or die "Unable to write $portfile";
		        print FILE $portruleentry;
		        close FILE;
      }
    }
   &portrule;
  open( FILE, "< $portfile" ) or system("touch $portfile");close FILE;
 }

############################################################################################################################
############################################################################################################################

if ($qossettings{'DOTOS'} eq $Lang::tr{'save'})
{
	if ($qossettings{'CLASS'} >= 100 && $qossettings{'CLASS'} < 121) {
		$qossettings{'DEVICE'} = $qossettings{'RED_DEV'};
	} elsif ($qossettings{'CLASS'} >= 1000 && $qossettings{'CLASS'} < 1021) {
		$qossettings{'DEVICE'} = $qossettings{'RED_DEV'};
	} elsif ($qossettings{'CLASS'} >= 200 && $qossettings{'CLASS'} < 221) {
		$qossettings{'DEVICE'} = $qossettings{'IMQ_DEV'};
	} elsif ($qossettings{'CLASS'} >= 2000 && $qossettings{'CLASS'} < 2021) {
		$qossettings{'DEVICE'} = $qossettings{'IMQ_DEV'};
	}
	open( FILE, ">> $tosfile" ) or die "Unable to write $tosfile";
	print FILE <<END
$qossettings{'CLASS'};$qossettings{'DEVICE'};$qossettings{'TOS'};
END
;
	close FILE;
}
elsif ($qossettings{'DOTOS'} eq 'Loeschen')
{
	open( FILE, "< $tosfile" ) or die "Unable to read $tosfile";
	@tosrules = <FILE>;
	close FILE;
	open( FILE, "> $tosfile" ) or die "Unable to read $tosfile";
  	foreach $tosruleentry (sort @tosrules)
  	{
  		@tosruleline = split( /\;/, $tosruleentry );
  		unless ( ($tosruleline[0] eq $qossettings{'CLASS'}) && ($tosruleline[2] eq $qossettings{'TOS'}))
  		{
			print FILE $tosruleentry;
		}
	}
	close FILE;
	$message = "$Lang::tr{'TOS Rule'} ($qossettings{'CLASS'} - $qossettings{'TOS'}) $Lang::tr{'was deleted'}.";
} elsif ($qossettings{'DOTOS'} eq $Lang::tr{'edit'})
{
	open( FILE, "< $tosfile" ) or die "Unable to read $tosfile";
	@tosrules = <FILE>;
	close FILE;
	open( FILE, "> $tosfile" ) or die "Unable to write $tosfile";
	foreach $tosruleentry (sort @tosrules)
	{
		@tosruleline = split( /\;/, $tosruleentry );
		if (( $tosruleline[0] eq $qossettings{'CLASS'} ) && ( $tosruleline[2] eq $qossettings{'TOS'} )) {
			$qossettings{'DEVICE'} = $tosruleline[1];
			$qossettings{'CLASS'} = $tosruleline[0];
			$qossettings{'TOS'} = $tosruleline[2];
			$qossettings{'EDIT'} = 'yes';
		} else {
			print FILE $tosruleentry;
		}
	}
	close FILE;
	&tosrule();
	&Header::closebigbox();
	&Header::closepage();
	exit
}

############################################################################################################################
############################################################################################################################

if ($qossettings{'ACTION'} eq $Lang::tr{'start'})
{
	$qossettings{'ENABLED'} = 'on';
	&General::writehash("${General::swroot}/qos/settings", \%qossettings);
	system("/usr/local/bin/qosctrl generate >/dev/null 2>&1");
	system("/usr/local/bin/qosctrl start >/dev/null 2>&1");
	system("logger -t ipfire 'QoS started'");
}
elsif ($qossettings{'ACTION'} eq $Lang::tr{'stop'})
{
	$qossettings{'ENABLED'} = 'off';
	&General::writehash("${General::swroot}/qos/settings", \%qossettings);
	system("/usr/local/bin/qosctrl stop >/dev/null 2>&1");
	system("/usr/local/bin/qosctrl generate >/dev/null 2>&1");
	system("logger -t ipfire 'QoS stopped'");
}
elsif ($qossettings{'ACTION'} eq $Lang::tr{'restart'})
{
	if ($qossettings{'ENABLED'} eq 'on'){
		system("/usr/local/bin/qosctrl stop >/dev/null 2>&1");
		system("/usr/local/bin/qosctrl generate >/dev/null 2>&1");
		system("/usr/local/bin/qosctrl start >/dev/null 2>&1");
		system("logger -t ipfire 'QoS restarted'");
	}
}
elsif ($qossettings{'ACTION'} eq $Lang::tr{'save'})
{
	if ($qossettings{'DEF_INC_SPD'} eq '') {
		$qossettings{'DEF_INC_SPD'} = int($qossettings{'INC_SPD'} * 0.9);
	}
	if ($qossettings{'DEF_OUT_SPD'} eq '') {
		$qossettings{'DEF_OUT_SPD'} = int($qossettings{'OUT_SPD'} * 0.9);
	}
	&General::writehash("${General::swroot}/qos/settings", \%qossettings);
}
elsif ($qossettings{'ACTION'} eq $Lang::tr{'template'} )
{
	if (($qossettings{'OUT_SPD'} > 0) && ($qossettings{'INC_SPD'} > 0)) {
		my @UP;
		#print "UP<br />";
		for(my $i = 1; $i <= 10; $i++) {
		$UP[$i] = int($qossettings{'OUT_SPD'} / $i );
		#print $i."=".$UP[$i]." ";
		}
		my @DOWN;
		#print "<br /><br />Down<br />";
		for(my $i = 1; $i <= 20; $i++) {
		$DOWN[$i] = int($qossettings{'INC_SPD'} / $i);
		#print $i."=".$DOWN[$i]." ";
		}
		open( FILE, "> $classfile" ) or die "Unable to write $classfile";
		print FILE <<END
imq0;200;1;$DOWN[20];$DOWN[1];;;8;VoIP;
imq0;203;4;$DOWN[20];$DOWN[1];;;0;VPN;
imq0;204;5;$DOWN[20];$DOWN[1];;;8;Webtraffic;
imq0;210;6;1;$DOWN[1];;;0;Default;
imq0;220;7;1;$DOWN[1];;;1;P2P;
$qossettings{'RED_DEV'};101;1;$UP[10];$UP[1];;;8;ACKs;
$qossettings{'RED_DEV'};102;2;$UP[10];$UP[1];;;8;VoIP;
$qossettings{'RED_DEV'};103;4;$UP[10];$UP[1];;;2;VPN;
$qossettings{'RED_DEV'};104;5;$UP[10];$UP[1];;;8;Webtraffic;
$qossettings{'RED_DEV'};110;6;1;$UP[1];;;0;Default;
$qossettings{'RED_DEV'};120;7;1;$UP[1];;;1;P2P;
END
;
		close FILE;
		open( FILE, "> $level7file" ) or die "Unable to write $level7file";
		print FILE <<END
102;$qossettings{'RED_DEV'};dns;;;
102;$qossettings{'RED_DEV'};rtp;;;
102;$qossettings{'RED_DEV'};skypetoskype;;;
103;$qossettings{'RED_DEV'};ssh;;;
103;$qossettings{'RED_DEV'};rdp;;;
104;$qossettings{'RED_DEV'};http;;;
104;$qossettings{'RED_DEV'};ssl;;;
104;$qossettings{'RED_DEV'};pop3;;;
120;$qossettings{'RED_DEV'};applejuice;;;
120;$qossettings{'RED_DEV'};bittorrent;;;
200;imq0;rtp;;;
200;imq0;skypetoskype;;;
203;imq0;ssh;;;
203;imq0;rdp;;;
204;imq0;http;;;
204;imq0;pop3;;;
204;imq0;ssl;;;
220;imq0;applejuice;;;
220;imq0;bittorrent;;;
END
;
		close FILE;
		open( FILE, "> $portfile" ) or die "Unable to write $portfile";
		print FILE <<END
101;$qossettings{'RED_DEV'};icmp;;;;;
102;$qossettings{'RED_DEV'};tcp;;;;53;
102;$qossettings{'RED_DEV'};udp;;;;53;
103;$qossettings{'RED_DEV'};esp;;;;;
103;$qossettings{'RED_DEV'};tcp;;1194;;;
103;$qossettings{'RED_DEV'};udp;;1194;;;
103;$qossettings{'RED_DEV'};tcp;;;;1194;
103;$qossettings{'RED_DEV'};udp;;;;1194;
103;$qossettings{'RED_DEV'};udp;;4500;;4500;
103;$qossettings{'RED_DEV'};udp;;500;;500;
104;$qossettings{'RED_DEV'};tcp;;;;80;
200;imq0;icmp;;;;;
203;imq0;esp;;;;;
203;imq0;tcp;;;;1194;
203;imq0;udp;;;;1194;
203;imq0;tcp;;1194;;;
203;imq0;udp;;1194;;;
203;imq0;udp;;4500;;4500;
203;imq0;udp;;500;;500;
204;imq0;tcp;;80;;;
END
;
		close FILE;
		if ($qossettings{'DEF_INC_SPD'} eq '') {
			$qossettings{'DEF_INC_SPD'} = int($qossettings{'INC_SPD'} * 0.9);
		}
		if ($qossettings{'DEF_OUT_SPD'} eq '') {
			$qossettings{'DEF_OUT_SPD'} = int($qossettings{'OUT_SPD'} * 0.9);
		}
		$qossettings{'DEFCLASS_INC'} = "210";
		$qossettings{'DEFCLASS_OUT'} = "110";
		$qossettings{'ACK'} ="101";
		$qossettings{'ENABLED'} = 'on';
		&General::writehash("${General::swroot}/qos/settings", \%qossettings);
		system("/usr/local/bin/qosctrl generate >/dev/null 2>&1");
		system("/usr/local/bin/qosctrl start >/dev/null 2>&1");
		system("logger -t ipfire 'QoS started'");
	} else {
		$message = $Lang::tr{'qos enter bandwidths'};
	}
}
elsif ($qossettings{'ACTION'} eq $Lang::tr{'status'} )
{
	&Header::openbox('100%', 'left', 'QoS Status');
	if ($qossettings{'ENABLED'} eq 'on'){
		my $output = "";
		$output = `/usr/local/bin/qosctrl status`;
		$output = &Header::cleanhtml($output,"y");
		print "<pre>$output</pre>\n";
	} else { print "$Lang::tr{'QoS not enabled'}"; }
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit
}
elsif ($qossettings{'ACTION'} eq $Lang::tr{'parentclass add'} )
{
	&parentclass();
	&Header::closebigbox();
	&Header::closepage();
	exit
}
elsif ($qossettings{'ACTION'} eq $Lang::tr{'qos add subclass'})
{
	&subclass();
	&Header::closebigbox();
	&Header::closepage();
	exit
}
elsif ($qossettings{'ACTION'} eq $Lang::tr{'Add Rule'})
{
	&Header::openbox('100%', 'center', $Lang::tr{'Add Rule'});
	print <<END
		<table>
		<tr><td align='center'>$Lang::tr{'Choose Rule'}
		<tr><td align='center'>
			<input type="button" onClick="swapVisibility('l7rule')" value='$Lang::tr{'Level7 Rule'}' />
			<input type="button" onClick="swapVisibility('portrule')" value='$Lang::tr{'Port Rule'}' />
			<input type="button" onClick="swapVisibility('tosrule')" value='$Lang::tr{'TOS rule'}' />
		</table>
END
;
	&Header::closebox();
	print <<END
		<div id='l7rule' style='display: none'>
END
;
		&level7rule();
	print <<END
		</div>
		<div id='portrule' style='display: none'>
END
;
		&portrule();
	print <<END
		</div>
		<div id='tosrule' style='display: none'>
END
;
		&tosrule();
	print <<END
		</div>
END
;
	&Header::closebigbox();
	&Header::closepage();
	exit
}
if ($qossettings{'ACTIONBW'} eq "$Lang::tr{'modify'}" )
{
	&changebandwidth();
	&Header::closebigbox();
	&Header::closepage();
	exit
}
if ($qossettings{'ACTIONDEF'} eq "$Lang::tr{'modify'}" )
{
	&changedefclasses();
	&Header::closebigbox();
	&Header::closepage();
	exit
}

&General::readhash("${General::swroot}/qos/settings", \%qossettings);

my $status = $Lang::tr{'stopped'};
my $statuscolor = '#993333';
if ( $qossettings{'ENABLED'} eq 'on' ) {
  $status = $Lang::tr{'running'};
  $statuscolor = '#339933';
}

if ( $netsettings{'RED_TYPE'} ne 'PPPOE' ) {
	$qossettings{'RED_DEV'} = $netsettings{'RED_DEV'};
}

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
}

############################################################################################################################
############################################################################################################################

&Header::openbox('100%', 'center', );

print <<END
  <form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='66%'>
END
;
	if ( $message ne "" ) {
		print "<tr><td colspan='2' align='center'><font color='red'>$message</font></tr>";
	}
	print <<END
		<tr><td width='50%' align='left'><b>Quality of Service:</b></td>
		    <td width='50%' align='center' bgcolor='$statuscolor'><font color='white'>$status</font></td></tr>
		    <tr>
				<td colspan='2'><br></td>
			</tr>
		<tr><td width='100%' align='right' colspan='2'>
		<input type='submit' name='ACTION' value="$Lang::tr{'start'}">
		<input type='submit' name='ACTION' value="$Lang::tr{'stop'}">
		<input type='submit' name='ACTION' value="$Lang::tr{'restart'}" ></td></tr></table></form>
END
;
	if (($qossettings{'OUT_SPD'} ne '') && ($qossettings{'INC_SPD'} ne '')) {
		print <<END
    <form method='post' action='$ENV{'SCRIPT_NAME'}'>
	  <table width='66%'>
		<tr><td colspan='3'>&nbsp;
		<tr><td width='50%' align='right'>$Lang::tr{'downlink speed'}: 	<td width='30%' align='left'>$qossettings{'INC_SPD'}
		    <td width='20%' rowspan='2' align='center' valign='middle'><input type='submit' name='ACTIONBW' value='$Lang::tr{'modify'}' />
		<tr><td width='50%' align='right'>$Lang::tr{'uplink speed'}: 	<td width='30%' align='left'>$qossettings{'OUT_SPD'}
		</table></form>
END
;
	}
	if (($qossettings{'DEFCLASS_OUT'} ne '') && ($qossettings{'DEFCLASS_INC'} ne '')&& ($qossettings{'ACK'} ne '')) {
		print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='66%'>
		<tr><td colspan='3'><hr />
		<tr><td width='50%' align='right'>$Lang::tr{'downlink std class'}: 	<td width='30%' align='left'>$qossettings{'DEFCLASS_INC'}
		    <td width='20%' rowspan='3' align='center' valign='middle'><input type='submit' name='ACTIONDEF' value='$Lang::tr{'modify'}' />
		<tr><td width='50%' align='right'>$Lang::tr{'uplink std class'}: 	<td width='30%' align='left'>$qossettings{'DEFCLASS_OUT'}
		<tr><td width='50%' align='right'>ACKs:				<td width='30%' align='left'>$qossettings{'ACK'}
	 	<tr><td colspan='3' width='100%'><hr />
		<tr><td colspan='3' width='100%' align='center'>
		</table>
		</form>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='66%' border='0'>
			<tr><td width='100%' align='center'>
			     <input type='submit' name='ACTION' value='$Lang::tr{'parentclass add'}' />
			     <input type='submit' name='ACTION' value='$Lang::tr{'status'}' />
			</td></tr></table>
	</form>
END
;
	}
&Header::closebox();

if ( ($qossettings{'OUT_SPD'} eq '') || ($qossettings{'INC_SPD'} eq '') ) {
	&changebandwidth();
	&Header::closebigbox();
	&Header::closepage();
	exit
}

if ( ($qossettings{'DEFCLASS_INC'} eq '') || ($qossettings{'DEFCLASS_OUT'} eq '') || ($qossettings{'ACK'} eq '') ) {
	&changedefclasses();
	&Header::closebigbox();
	&Header::closepage();
	exit
}

	&Header::openbox('100%', 'center', "$qossettings{'RED_DEV'} $Lang::tr{'graph'}, $Lang::tr{'uplink'}");
	&Graphs::makegraphbox("qos.cgi",$qossettings{'RED_DEV'},"hour");
	&Header::closebox();
	&Header::openbox('100%', 'center', "$qossettings{'IMQ_DEV'} $Lang::tr{'graph'}, $Lang::tr{'downlink'}");
	&Graphs::makegraphbox("qos.cgi",$qossettings{'IMQ_DEV'},"hour");
	&Header::closebox();

&showclasses($qossettings{'RED_DEV'});
&showclasses($qossettings{'IMQ_DEV'});

&Header::closebigbox();
&Header::closepage();

}

############################################################################################################################
############################################################################################################################

sub changedefclasses {
	&Header::openbox('100%', 'center', $Lang::tr{'std classes'});
	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='66%'>
		<tr><td width='100%' colspan='3'>$Lang::tr{'no filter pass'}
		<tr><td width='33%' align='right'>$Lang::tr{'download'}:<td width='33%' align='left'><select name='DEFCLASS_INC'>
END
;
		for ( $c = 200 ; $c <= 220 ; $c++ )
		{
			if ( $qossettings{'DEFCLASS_INC'} ne $c )
			{ print "<option value='$c'>$c</option>\n"; }
			else	{ print "<option selected value='$c'>$c</option>\n"; }
		}
		print <<END
		</select><td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>$Lang::tr{'upload'}:<td width='33%' align='left'><select name='DEFCLASS_OUT'>
END
;
		for ( $c = 100 ; $c <= 120 ; $c++ )
		{
			if ( $qossettings{'DEFCLASS_OUT'} ne $c )
			{ print "<option value='$c'>$c</option>\n"; }
			else { print "<option selected value='$c'>$c</option>\n"; }
		}
		print <<END
		</select><td width='33%' align='center'>&nbsp;
		</table>
		<hr />
		<table width='66%'>
		<tr><td width='100%' colspan='3'>$Lang::tr{'enter ack class'}
		<tr><td width='33%' align='right'>ACKs:<td width='33%' align='left'><select name='ACK'>
END
;
		for ( $c = 100 ; $c <= 120 ; $c++ )
		{
			if ( $qossettings{'ACK'} ne $c )
			{ print "<option value='$c'>$c</option>\n"; }
			else {	print "<option selected value='$c'>$c</option>\n"; }
		}
		print <<END
		</select><td width='33%' align='center'><input type='submit' name='ACTION' value="$Lang::tr{'save'}" />
		</table>
		</form>
END
;
		&Header::closebox();
}

sub changebandwidth {
	&Header::openbox('100%', 'center', $Lang::tr{'bandwithsettings'});
	if ($qossettings{'ENABLED'} eq 'on') {
		print "$Lang::tr{'bandwitherror'}";
		print "<a href='/cgi-bin/qos.cgi'>$Lang::tr{'back'}</a>";
	} else {
		print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type='hidden' name='DEF_OUT_SPD' value='' /><input type='hidden' name='DEF_INC_SPD' value='' />
		<table width='66%'>
		<tr><td width='100%' colspan='3'>$Lang::tr{'down and up speed'}</td></tr>
		<tr><td width='50%' align='right'>$Lang::tr{'downlink speed'}:</td>
				<td width='30%' align='left'><input type='text' name='INC_SPD' maxlength='8' value="$qossettings{'INC_SPD'}" /></td>
				<td width='20%' align='center' rowspan='2'><input type='submit' name='ACTION' value="$Lang::tr{'template'}" /><br /><input type='submit' name='ACTION' value="$Lang::tr{'save'}" /><br /><input type='reset' name='ACTION' value="$Lang::tr{'reset'}" /></td></tr>
		<tr><td width='50%' align='right'>$Lang::tr{'uplink speed'}:</td>
				<td width='30%' align='left'><input type='text' name='OUT_SPD' maxlength='8' value="$qossettings{'OUT_SPD'}" /></td></tr>
		</table>
		</form>
		<font color='red'>$Lang::tr{'template warning'}</font>
END
;
	}
	&Header::closebox();
}

sub parentclass {
	&Header::openbox('100%', 'center', $Lang::tr{'parentclass'});
	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='66%'>
END
;
	if ( $message ne "" ) {
		print "<tr><td colspan='3' align='center'>$message";
	}
	if ( $qossettings{'EDIT'} eq 'yes' ) {
		print "<input type='hidden' name='CLASS' value='$qossettings{'CLASS'}' />";
		print "<input type='hidden' name='DEVICE' value='$qossettings{'DEVICE'}' />";
	}
	print <<END
		<tr><td width='100%' colspan='3'>$Lang::tr{'enter data'}
		<tr><td width='33%' align='right'>$Lang::tr{'interface'}:
		    <td width='33%' align='left'>
END
;
		if ( $qossettings{'EDIT'} eq 'yes' ) {
			print "<select name='DEVICE' disabled>";
		} else {
			print "<select name='DEVICE'>";
		}
		if ( $qossettings{'DEVICE'} eq $qossettings{'RED_DEV'} ) {
			$qossettings{'RED_DEV_SEL'} = 'selected';
		} elsif ( $qossettings{'DEVICE'} eq $qossettings{'IMQ_DEV'} ) {
			$qossettings{'IMQ_DEV_SEL'} = 'selected';
		}
		print <<END
			<option value='$qossettings{'RED_DEV'}' $qossettings{'RED_DEV_SEL'}>$qossettings{'RED_DEV'}</option>
			<option value='$qossettings{'IMQ_DEV'}' $qossettings{'IMQ_DEV_SEL'}>$qossettings{'IMQ_DEV'}</option></select>
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>$Lang::tr{'Class'}:<td width='33%' align='left'>
END
;
		if ( $qossettings{'EDIT'} eq 'yes' ) {
			print "<select name='CLASS' disabled>";
		} else {
			print "<select name='CLASS'>";
		}
		for ( $c = 100 ; $c <= 120 ; $c++ )
		{
			if ( $qossettings{'CLASS'} ne $c )
			{ print "<option value='$c'>$c</option>\n"; }
			else { print "<option selected value='$c'>$c</option>\n"; }
		}
		for ( $c = 200 ; $c <= 220 ; $c++ )
		{
			if ( $qossettings{'CLASS'} ne $c )
			{ print "<option value='$c'>$c</option>\n"; }
			else { print "<option selected value='$c'>$c</option>\n"; }
		}
		print <<END
		</select>
		<td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>$Lang::tr{'priority'}:<td width='33%' align='left'><select name='PRIO'>
END
;
		for ( $c = 1 ; $c <= 7 ; $c++ )
		{
			if ( $qossettings{'PRIO'} ne $c )
			{ print "<option value='$c'>$c</option>\n"; }
			else { print "<option selected value='$c'>$c</option>\n"; }
		}
		if ($qossettings{'MINBWDTH'} eq "") { $qossettings{'MINBWDTH'} = "1"; }
		print <<END
		</select>
		<td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>$Lang::tr{'guaranteed bandwith'}:
		    <td width='33%' align='left'><input type='text' size='20' name='MINBWDTH' maxlength='8' required='1' value="$qossettings{'MINBWDTH'}" />
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>$Lang::tr{'max bandwith'}&nbsp;<img src='/blob.gif' alt='*' />:
		    <td width='33%' align='left'><input type='text' size='20' name='MAXBWDTH' maxlength='8' required='1' value="$qossettings{'MAXBWDTH'}" />
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Burst:
		    <td width='33%' align='left'><input type='text' size='20' name='BURST' maxlength='8' value="$qossettings{'BURST'}" />
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Ceilburst:
		    <td width='33%' align='left'><input type='text' size='20' name='CBURST' maxlength='8' value="$qossettings{'CBURST'}" />
		    <td width='33%' align='center'>&nbsp;
END
;
			$selected{'TOS'}{$qossettings{'TOS'}} = "selected='selected'";
print <<END
		<tr><td width='33%' align='right'>TOS-Bit:
		    <td width='33%' align='left'><select name='TOS'>
				<option value='0' $selected{'TOS'}{'0'}>$Lang::tr{'disabled'} (0)</option>
				<option value='8' $selected{'TOS'}{'8'}>$Lang::tr{'min delay'} (8)</option>
				<option value='4' $selected{'TOS'}{'4'}>$Lang::tr{'max throughput'} (4)</option>
				<option value='2' $selected{'TOS'}{'2'}>$Lang::tr{'max reliability'} (2)</option>
				<option value='1' $selected{'TOS'}{'1'}>$Lang::tr{'min costs'} (1)</option></select>
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>$Lang::tr{'remark'}:
		    <td width='66%' colspan='2' align='left'><input type='text' name='REMARK' size='40' maxlength='40' value="$qossettings{'REMARK'}" />
		<tr><td width='33%' align='right'><img src='/blob.gif' alt='*' />&nbsp;$Lang::tr{'required field'}
		    <td width='33%' align='left'>&nbsp;
		    <td width='33%' align='center'><input type='submit' name='DOCLASS' value='$Lang::tr{'save'}' />&nbsp;<input type='reset' value='$Lang::tr{'reset'}' />
		</table></form>
END
;
	&Header::closebox();
}

sub subclass {
	&Header::openbox('100%', 'center', $Lang::tr{'Subclass'});
	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='66%'>
END
;
	if ( $message ne "" ) {
		print "<tr><td colspan='3' align='center'>$message";
	}
	print <<END
		<tr><td colspan='3' width='100%'>$Lang::tr{'current class'}: $qossettings{'CLASS'}
		<tr><td width='100%' colspan='3'>$Lang::tr{'enter data'}
		<tr><td width='33%' align='right'>$Lang::tr{'Subclass'}:<td width='33%' align='left'><select name='SCLASS'>
END
;
	if ($qossettings{'CLASS'} >= 100 && $qossettings{'CLASS'} < 121) {
		$qossettings{'DEVICE'} = $qossettings{'RED_DEV'};
		for ( $c = 1000 ; $c <= 1020 ; $c++ )
		{
			if ( $qossettings{'SCLASS'} ne $c )
			{ print "<option value='$c'>$c</option>\n"; }
			else { print "<option selected value='$c'>$c</option>\n"; }
		}
	} elsif ($qossettings{'CLASS'} >= 200 && $qossettings{'CLASS'} < 221) {
		$qossettings{'DEVICE'} = $qossettings{'IMQ_DEV'};
		for ( $c = 2000 ; $c <= 2020 ; $c++ )
		{
			if ( $qossettings{'SCLASS'} ne $c )
			{ print "<option value='$c'>$c</option>\n"; }
			else { print "<option selected value='$c'>$c</option>\n"; }
		}
	}
	print <<END
		</select>
		<td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>$Lang::tr{'priority'}:<td width='33%' align='left'><select name='PRIO'>
END
;
		for ( $c = 1 ; $c <= 7 ; $c++ )
		{
			if ( $qossettings{'PRIO'} ne $c )
			{ print "<option value='$c'>$c</option>\n"; }
			else { print "<option selected value='$c'>$c</option>\n"; }
		}
		print <<END
		<td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>$Lang::tr{'guaranteed bandwith'}:
		    <td width='33%' align='left'><input type='text' name='MINBWDTH' maxlength='8' required='1' value="$qossettings{'MINBWDTH'}" />
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>$Lang::tr{'max bandwith'}:
		    <td width='33%' align='left'><input type='text' name='MAXBWDTH' maxlength='8' required='1' value="$qossettings{'MAXBWDTH'}" />
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Burst:
		    <td width='33%' align='left'><input type='text' name='BURST' maxlength='8' value="$qossettings{'BURST'}" />
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Ceilburst:
		    <td width='33%' align='left'><input type='text' name='CBURST' maxlength='8' value="$qossettings{'CBURST'}" />
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>TOS-Bit:
		    <td width='33%' align='left'><select name='TOS'>
				<option value='0'>$Lang::tr{'disabled'} (0)</option>
				<option value='8'>$Lang::tr{'min delay'} (8)</option>
				<option value='4'>$Lang::tr{'max throughput'} (4)</option>
				<option value='2'>$Lang::tr{'max reliability'} (2)</option>
				<option value='1'>$Lang::tr{'min costs'} (1)</option></select>
		    <td width='33%' align='center'><input type='hidden' name='CLASS' value="$qossettings{'CLASS'}" />
							<input type='hidden' name='DEVICE' value="$qossettings{'DEVICE'}" />
							<input type='submit' name='DOSCLASS' value='$Lang::tr{'save'}' />&nbsp;<input type='reset' value='$Lang::tr{'reset'}' />
		</table></form>
END
;
	&Header::closebox();
}

sub level7rule {
	&Header::openbox('100%', 'center', $Lang::tr{'Level7 Rule'});
	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='66%'>
END
;
	if ( $message ne "" ) {
		print "<tr><td colspan='3' align='center'><font color='red'>$message</font>";
	}
	print <<END
		<tr><td colspan='3' width='100%'>$Lang::tr{'current class'}: $qossettings{'CLASS'}
		<tr><td width='100%' colspan='3'>$Lang::tr{'enter data'}
		<tr><td width='33%' align='right'>$Lang::tr{'protocol'}:
		    <td width='33%' align='left'><select name='L7PROT'>
END
;
		opendir( DIR, "/etc/l7-protocols/protocols" );
		foreach $direntry ( sort readdir(DIR) )
		{
			next if $direntry eq ".";
			next if $direntry eq "..";
			next if -d "/etc/l7-protocols/protocols/$direntry";
			@proto = split( /\./, $direntry );
			if ( $proto[0] eq $qossettings{'L7PROT'} ) {
				print "<option value='$proto[0]' selected>$proto[0]</option>\n";
			} else {
				print "<option value='$proto[0]'>$proto[0]</option>\n";
			}
		}
		closedir DIR;
	print <<END
		    </select><td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>$Lang::tr{'source ip'}:
		    <td width='33%' align='left'><input type='text' name='QIP' maxlength='31' value='$qossettings{'QIP'}' />
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>$Lang::tr{'destination ip'}:
		    <td width='33%' align='left'><input type='text' name='DIP' maxlength='31' value='$qossettings{'DIP'}' />
		    <td width='33%' align='center'><input type='hidden' name='CLASS' value='$qossettings{'CLASS'}' /><input type='submit' name='DOLEVEL7' value='$Lang::tr{'save'}' />
		<tr><td colspan="3" align='center'><font color="red"><em>$Lang::tr{'qos warning'}</em></font>
		</table></form>
END
;
	&Header::closebox();
}

sub portrule {
	&Header::openbox('100%', 'center', $Lang::tr{'Add Port Rule'});
	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='66%'>
		<tr><td width='100%' colspan='3'>$Lang::tr{'enter data'}
		<tr><td width='33%' align='right'>$Lang::tr{'protocol'}:
		    <td width='33%' align='left'><select name='PPROT'>
END
;
			open( FILE, "< /etc/protocols" );
			@proto = <FILE>;
			close FILE;
			foreach $direntry (sort @proto)
			{
				@tmpline = split( /\ /, $direntry );
				next if $tmpline[0] =~ "#";
				if ( $tmpline[0] eq $qossettings{'PPROT'} ) {
					print "<option value='$tmpline[0]' selected>$tmpline[0]</option>\n";
				} else {
					print "<option value='$tmpline[0]'>$tmpline[0]</option>\n";
				}
			}
	print <<END
		    </select><td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>$Lang::tr{'source port'}:
		    <td width='33%' align='left'><input type='text' name='QPORT' maxlength='11' value='$qossettings{'QPORT'}' />
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>$Lang::tr{'destination port'}:
		    <td width='33%' align='left'><input type='text' name='DPORT' maxlength='11' value='$qossettings{'DPORT'}' />
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>$Lang::tr{'source ip'}:
		    <td width='33%' align='left'><input type='text' name='QIP' maxlength='31' value='$qossettings{'QIP'}' />
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>$Lang::tr{'destination ip'}:
		    <td width='33%' align='left'><input type='text' name='DIP' maxlength='31' value='$qossettings{'DIP'}' />
		    <td width='33%' align='center'><input type='hidden' name='CLASS' value='$qossettings{'CLASS'}' /><input type='submit' name='DOPORT' value='$Lang::tr{'save'}' />
		</table></form>
END
;
	&Header::closebox();
}

sub tosrule {
	&Header::openbox('100%', 'center', $Lang::tr{'TOS Rule'});
	if ($qossettings{'TOS'}) {
		$checked{$qossettings{'TOS'}} = "checked";
	}
	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='66%'>
END
;
	if ( $message ne "" ) {
		print "<tr><td colspan='3' align='center'><font color='red'>$message</font>";
	}
	print <<END
		<tr><td colspan='2' width='100%'>$Lang::tr{'current class'}: $qossettings{'CLASS'}
		<tr><td width='100%' colspan='2'>$Lang::tr{'Enter TOS'}
		<tr><td width='50%' align='left'>$Lang::tr{'min delay'} (8)		<td width='50%'><input type="radio" name="TOS" value="8" $checked[8] />
		<tr><td width='50%' align='left'>$Lang::tr{'max throughput'} (4)		<td width='50%'><input type="radio" name="TOS" value="4" $checked[4] />
		<tr><td width='50%' align='left'>$Lang::tr{'max reliability'} (2)	<td width='50%'><input type="radio" name="TOS" value="2" $checked[2] />
		<tr><td width='50%' align='left'>$Lang::tr{'min costs'} (1)			<td width='50%'><input type="radio" name="TOS" value="1" $checked[1] />
		<tr><td width='100%' align='right' colspan='2'><input type='hidden' name='CLASS' value='$qossettings{'CLASS'}' /><input type='submit' name='DOTOS' value='$Lang::tr{'save'}' />
		</table></form>
END
;
	&Header::closebox();
}

sub showclasses {
	$qossettings{'DEV'} = shift;
	open( FILE, "< $classfile" ) or die "Unable to read $classfile";
	@classes = <FILE>;
	close FILE;
	if (@classes) {
		open( FILE, "< $subclassfile" ) or die "Unable to read $subclassfile";
		@subclasses = <FILE>;
		close FILE;
		open( FILE, "< $level7file" ) or die "Unable to read $level7file";
		@l7rules = <FILE>;
		close FILE;
		open( FILE, "< $tosfile" ) or die "Unable to read $tosfile";
		@tosrules = <FILE>;
		close FILE;
		open( FILE, "< $portfile" ) or die "Unable to read $portfile";
		@portrules = <FILE>;
		close FILE;
	  	foreach $classentry (sort @classes)
	  	{
	  		@classline = split( /\;/, $classentry );
	  		if ( $classline[0] eq $qossettings{'DEV'} )
	  		{
	  		  &Header::openbox('100%', 'center', "$Lang::tr{'Class'}: $classline[1] $classline[8]");
	  			print <<END
				<table border='0' width='100%' cellspacing='0'>
				<tr><td bgcolor='$color{'color20'}' width='10%' align='center'><b>$Lang::tr{'interface'}</b>
				    <td bgcolor='$color{'color20'}' width='10%' align='center'><b>$Lang::tr{'Class'}</b>
				    <td bgcolor='$color{'color20'}' width='10%' align='center'>$Lang::tr{'priority'}
				    <td bgcolor='$color{'color20'}' width='10%' align='center'>$Lang::tr{'guaranteed bandwith'}
				    <td bgcolor='$color{'color20'}' width='10%' align='center'>$Lang::tr{'max bandwith'}
				    <td bgcolor='$color{'color20'}' width='10%' align='center'>Burst
				    <td bgcolor='$color{'color20'}' width='10%' align='center'>Ceil Burst
				    <td bgcolor='$color{'color20'}' width='10%' align='center'>TOS
				    <td bgcolor='$color{'color20'}' width='20%' align='center'>$Lang::tr{'action'}
				<tr><td align='center' bgcolor='$color{'color22'}'>$classline[0]</td>
				    <td align='center' bgcolor='$color{'color22'}'>$classline[1]</td>
				    <td align='center' bgcolor='$color{'color22'}'>$classline[2]</td>
				    <td align='center' bgcolor='$color{'color22'}'>$classline[3]</td>
				    <td align='center' bgcolor='$color{'color22'}'>$classline[4]</td>
				    <td align='center' bgcolor='$color{'color22'}'>$classline[5]</td>
				    <td align='center' bgcolor='$color{'color22'}'>$classline[6]</td>
				    <td align='center' bgcolor='$color{'color22'}'>$classline[7]</td>
				    <td align='right'  bgcolor='$color{'color22'}'>
					<table border='0'><tr>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$classline[1]' />
						<input type='hidden' name='ACTION' value='$Lang::tr{'qos add subclass'}' />
						<input type='image' alt='$Lang::tr{'add subclass'}' title='$Lang::tr{'add subclass'}' src='/images/addblue.gif' />
					</form>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$classline[1]' />
						<input type='hidden' name='ACTION' value='$Lang::tr{'Add Rule'}' />
						<input type='image' alt='$Lang::tr{'Add Rule'}' title='$Lang::tr{'Add Rule'}' src='/images/addgreen.gif' />
					</form>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$classline[1]' />
						<input type='hidden' name='DOCLASS' value='$Lang::tr{'edit'}' />
						<input type='image' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' src='/images/edit.gif' />
					</form>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$classline[1]' />
						<input type='hidden' name='DOCLASS' value='$Lang::tr{'delete'}' />
						<input type='image' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' src='/images/delete.gif' />
					</form>
					</table>
				    </td>
				<tr><td align='right' colspan='2'><b>$Lang::tr{'remark'}:</b>
				    <td align='center' colspan='6'> $classline[8]
				    <td align='right'><b>Queueing:</b> $classline[9]
END
;

				if (@l7rules) {
	  				foreach $l7ruleentry (sort @l7rules)
	  				{
	  					@l7ruleline = split( /\;/, $l7ruleentry );
	  					if ( $l7ruleline[0] eq $classline[1] )
	  					{
	  						print <<END
				<tr><td align='right' colspan='2'><b>$Lang::tr{'Level7 Protocol'}:</b>
				    <td align='center' colspan='6'>$l7ruleline[2]
				    <td align='right' >
					<table border='0'><tr>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$l7ruleline[0]' />
						<input type='hidden' name='L7PROT' value='$l7ruleline[2]' />
						<input type='hidden' name='DOLEVEL7' value='$Lang::tr{'edit'}' />
						<input type='image' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' src='/images/edit.gif' />
					</form>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$l7ruleline[0]' />
						<input type='hidden' name='L7PROT' value='$l7ruleline[2]' />
						<input type='hidden' name='DOLEVEL7' value='$Lang::tr{'delete'}' />
						<input type='image' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' src='/images/delete.gif' />
					</form>
					</table>
END
;
							if (($l7ruleline[3] ne "") || ($l7ruleline[4] ne "")){
								print <<END
				<tr><td align='center'>&nbsp;
				    <td align='right' colspan='3'><b>$Lang::tr{'source ip'}:</b> $l7ruleline[3]
				    <td align='right' colspan='3'><b>$Lang::tr{'destination ip'}:</b> $l7ruleline[4]
END
;
							}


END
;
	  					}
	  				}
				}


				if (@portrules) {
				  	foreach $portruleentry (sort @portrules)
				  	{
				  		@portruleline = split( /\;/, $portruleentry );
				  		if ( $portruleline[0] eq $classline[1] )
				  		{
				  			print <<END
				<tr><td align='right' colspan='2'><b>$Lang::tr{'Port Rule'}:</b>
				    <td align='center'>($portruleline[2])
				    <td align='center' colspan='2'>
END
;
						if ($portruleline[4]) {
							print <<END
				    <i>$Lang::tr{'source port'}:</i> $portruleline[4]
END
;
						}
						print "<td align='center' colspan='2'>";
						if ($portruleline[6]) {
							print <<END
				    <i>$Lang::tr{'destination port'}:</i> $portruleline[6]
END
;
						}
						print <<END
				    <td>&nbsp;
				    <td align='right'>
				    <table border='0'><tr>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$portruleline[0]' />
						<input type='hidden' name='PPROT' value='$portruleline[2]' />
						<input type='hidden' name='QIP' value='$portruleline[3]' />
						<input type='hidden' name='QPORT' value='$portruleline[4]' />
						<input type='hidden' name='DIP' value='$portruleline[5]' />
						<input type='hidden' name='DPORT' value='$portruleline[6]' />
						<input type='hidden' name='DOPORT' value='$Lang::tr{'edit'}' />
						<input type='image' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' src='/images/edit.gif' />
					</form>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$portruleline[0]' />
						<input type='hidden' name='PPROT' value='$portruleline[2]' />
						<input type='hidden' name='QIP' value='$portruleline[3]' />
						<input type='hidden' name='QPORT' value='$portruleline[4]' />
						<input type='hidden' name='DIP' value='$portruleline[5]' />
						<input type='hidden' name='DPORT' value='$portruleline[6]' />
						<input type='hidden' name='DOPORT' value='$Lang::tr{'delete'}' />
						<input type='image' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' src='/images/delete.gif' />
					</form>
				    </table>
END
;
							if (($portruleline[3] ne "") || ($portruleline[5] ne "")){
								print <<END
				<tr><td align='center'>&nbsp;
				    <td align='right' colspan='3'><b>$Lang::tr{'source ip'}:</b> $portruleline[3]
				    <td align='right' colspan='3'><b>$Lang::tr{'destination ip'}:</b> $portruleline[5]
END
;
							}
				  		}
				  	}
				}

				if (@tosrules) {
				  	foreach $tosruleentry (sort @tosrules)
				  	{
				  		@tosruleline = split( /\;/, $tosruleentry );
				  		if ( $tosruleline[0] eq $classline[1] )
				  		{
							print <<END
					<tr><td align='right' colspan='2'>
						<b>TOS Bit matches:</b>
					    <td colspan='6' align='center'>
END
;
							if ( $tosruleline[2] eq "8") {
								print "$Lang::tr{'min delay'}\n";
							} elsif ( $tosruleline[2] eq "4") {
								print "$Lang::tr{'max throughput'}\n";
							} elsif ( $tosruleline[2] eq "2") {
								print "$Lang::tr{'max reliability'}\n";
							} elsif ( $tosruleline[2] eq "1") {
								print "$Lang::tr{'min costs'}\n";
							} else { print "&nbsp;\n"; }

							print <<END
						($tosruleline[2])
					    <td align='right'>
				  		  <table border='0'><tr>
							<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
								<input type='hidden' name='CLASS' value='$tosruleline[0]' />
								<input type='hidden' name='DEV' value='$tosruleline[1]' />
								<input type='hidden' name='TOS' value='$tosruleline[2]' />
								<input type='hidden' name='DOTOS' value='$Lang::tr{'edit'}' />
								<input type='image' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' src='/images/edit.gif' />
							</form>
							<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
								<input type='hidden' name='CLASS' value='$tosruleline[0]' />
								<input type='hidden' name='DEV' value='$tosruleline[1]' />
								<input type='hidden' name='TOS' value='$tosruleline[2]' />
								<input type='hidden' name='DOTOS' value='$Lang::tr{'delete'}' />
								<input type='image' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' src='/images/delete.gif' />
							</form>
				    		</table>
END
;
	  					}
	  				}
				}
END
;
			  	foreach $subclassentry (sort @subclasses)
	  			{
	  				@subclassline = split( /\;/, $subclassentry );
		  			if ( $subclassline[1] eq $classline[1] ) {
						print <<END
							<tr><td align='center' bgcolor='#FAFAFA'>$Lang::tr{'Subclass'}:
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[2]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[3]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[4]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[5]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[6]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[7]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[8]
							    <td align='right'  bgcolor='#FAFAFA'>
						<table border='0'><tr>
						<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='CLASS' value='$subclassline[2]' />
							<input type='hidden' name='ACTION' value='$Lang::tr{'Add Rule'}' />
							<input type='image' alt='$Lang::tr{'Add Rule'}' title='$Lang::tr{'Add Rule'}' src='/images/addgreen.gif' />
						</form>
						<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='CLASS' value='$subclassline[2]' />
							<input type='hidden' name='DOSCLASS' value='$Lang::tr{'edit'}' />
							<input type='image' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' src='/images/edit.gif' />
						</form>
						<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='CLASS' value='$subclassline[2]' />
							<input type='hidden' name='DOSCLASS' value='$Lang::tr{'delete'}' />
							<input type='image' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' src='/images/delete.gif' />
						</form>
						</table>
END
;
					}
				}
			print <<END
			</table>
END
;
	          &Header::closebox();
	  		}
			}
  	}
	}
sub validminbwdth {
	if ( $qossettings{'VALID'} eq 'yes' ) {
		if ( $qossettings{'DEVICE'} eq $qossettings{'RED_DEV'} ) {
			$qossettings{'SPD'} = $qossettings{'OUT_SPD'};
		} elsif ( $qossettings{'DEVICE'} eq $qossettings{'IMQ_DEV'} ) {
			$qossettings{'SPD'} = $qossettings{'INC_SPD'};
		}
		unless ( ( $qossettings{'MINBWDTH'} >= 1 ) && ( $qossettings{'MINBWDTH'} <= $qossettings{'SPD'} ) ) {
			$qossettings{'VALID'} = 'no';
			$message = "$Lang::tr{'false min bandwith'}";
		}
		$qossettings{'SPD'} = '';
	}
}

sub validmaxbwdth {
	if ( $qossettings{'VALID'} eq 'yes' ) {
		if ( $qossettings{'DEVICE'} eq $qossettings{'RED_DEV'} ) {
			$qossettings{'SPD'} = $qossettings{'OUT_SPD'};
		} elsif ( $qossettings{'DEVICE'} eq $qossettings{'IMQ_DEV'} ) {
			$qossettings{'SPD'} = $qossettings{'INC_SPD'};
		}
		unless ( ( $qossettings{'MAXBDWTH'} >= 0 ) && ($qossettings{'MAXBDWTH'} >= $qossettings{'MINBDWTH'}) &&( $qossettings{'MAXBDWTH'} <= $qossettings{'SPD'} ) ) {
			$qossettings{'VALID'} = 'no';
			$message = "$Lang::tr{'false max bandwith'}";
		}
		$qossettings{'SPD'} = '';
	}
}

sub validclass {
	if ( $qossettings{'VALID'} eq 'yes' ) {
		if ( $qossettings{'DEVICE'} eq $qossettings{'RED_DEV'} ) {
			if ($qossettings{'CLASS'} lt 100 || $qossettings{'CLASS'} ge 121) {
				$qossettings{'VALID'} = 'no';
				$message = "$Lang::tr{'false classnumber'}";
			}
		} elsif ( $qossettings{'DEVICE'} eq $qossettings{'IMQ_DEV'} ) {
			if ($qossettings{'CLASS'} lt 200 || $qossettings{'CLASS'} ge 221) {
				$qossettings{'VALID'} = 'no';
				$message = "$Lang::tr{'The class number does not match the specified interface.'}";
			}
		}
		open( FILE, "< $classfile" ) or die "Unable to read $classfile";
		@tmp = <FILE>;
		close FILE;
		foreach $classentry (sort @tmp)
	  	{
	  		@tmpline = split( /\;/, $classentry );
	  		if ( $tmpline[1] eq $qossettings{'CLASS'} )
  			{
				$qossettings{'VALID'} = 'no';
				$message = "$Lang::tr{'false classnumber'}";
				last
			}
		}
	}
}

sub validsubclass {
	if ( $qossettings{'VALID'} eq 'yes' ) {
		open( FILE, "< $subclassfile" ) or die "Unable to read $subclassfile";
		@tmp = <FILE>;
		close FILE;
		foreach $subclassentry (sort @tmp)
	  	{
	  		@tmpline = split( /\;/, $subclassentry );
	  		if ( $tmpline[2] eq $qossettings{'SCLASS'} )
  			{
				$qossettings{'VALID'} = 'no';
				$message = "$Lang::tr{'class in use'}";
				last
			}
		}
	}
}
