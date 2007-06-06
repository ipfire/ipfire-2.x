#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
#

use strict;

# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/graphs.pl";

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::colourred} );
undef (@dummy);

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

&overviewgraph($qossettings{'RED_DEV'});
&overviewgraph($qossettings{'IMQ_DEV'});

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

my %cgiparams=();
# Maps a nice printable name to the changing part of the pid file, which
# is also the name of the program


# Generate Graphs from rrd Data
&Graphs::updatecpugraph ("day");
&Graphs::updateloadgraph ("day");

&Header::showhttpheaders();
&Header::getcgihash(\%cgiparams);
&Header::openpage($Lang::tr{'status information'}, 1, '');
&Header::openbigbox('100%', 'left');

	open( FILE, "< $classfile" ) or die "Unable to read $classfile";
	@classes = <FILE>;
	close FILE;
	open( FILE, "< $subclassfile" ) or die "Unable to read $subclassfile";
	@subclasses = <FILE>;
	close FILE;
	&Header::openbox('100%', 'left', 'QoS Graphen');
	print <<END
	<table width='100%'>	<tr><td align='center'><font color='red'>Diese Seite braucht je nach Geschwindigkeit des Computers laenger zum Laden.</font>
				<tr><td align='center'><b>Klasse:</b> 
END
;
  	foreach $classentry (sort @classes)
  	{
  		@classline = split( /\;/, $classentry );
		$qossettings{'CLASS'}=$classline[1];
		print <<END
		<input type="button" onClick="swapVisibility('$qossettings{'CLASS'}')" value='$qossettings{'CLASS'}' />
END
;
	}
	print <<END
	</table>
END
;
	&Header::closebox();
  	foreach $classentry (sort @classes)
  	{
  		@classline = split( /\;/, $classentry );
		$qossettings{'DEV'}=$classline[0];
		$qossettings{'CLASS'}=$classline[1];
		&gengraph($qossettings{'DEV'},$qossettings{'CLASS'});
		print "<div id='$qossettings{'CLASS'}' style='display: none'>";
		&Header::openbox('100%', 'center', "$qossettings{'CLASS'} ($qossettings{'DEV'})");
		print <<END
		<table>
		<tr><td colspan='2' align='center'><img src='/graphs/class_$qossettings{'CLASSPRFX'}-$qossettings{'CLASS'}_$qossettings{'DEV'}-packets.png' />
		<tr><td colspan='2' align='center'><img src='/graphs/class_$qossettings{'CLASSPRFX'}-$qossettings{'CLASS'}_$qossettings{'DEV'}-borrowed.png' />
		<tr><td colspan='2' align='center'><img src='/graphs/class_$qossettings{'CLASSPRFX'}-$qossettings{'CLASS'}_$qossettings{'DEV'}-bytes.png' />
END
;
	  	foreach $subclassentry (sort @subclasses)
  		{
	  		@subclassline = split( /\;/, $subclassentry );
			if ($subclassline[1] eq $classline[1]) {
				$qossettings{'DEV'}=$subclassline[0];
				$qossettings{'SCLASS'}=$subclassline[2];
				&gengraph($qossettings{'DEV'},$qossettings{'SCLASS'});
				print <<END
				<tr><td colspan='2' align='center'><img src='/graphs/class_$qossettings{'CLASSPRFX'}-$qossettings{'SCLASS'}_$qossettings{'DEV'}-packets.png' />
				<tr><td colspan='2' align='center'><img src='/graphs/class_$qossettings{'CLASSPRFX'}-$qossettings{'SCLASS'}_$qossettings{'DEV'}-borrowed.png' />
				<tr><td colspan='2' align='center'><img src='/graphs/class_$qossettings{'CLASSPRFX'}-$qossettings{'SCLASS'}_$qossettings{'DEV'}-bytes.png' />
END
;
			}
		}
		print "\t\t</table>";
		&Header::closebox();	
		print "</div>\n";
	}
print <<END
	</table>
END
;

if (( -e "/srv/web/ipfire/html/graphs/qos-graph-$qossettings{'RED_DEV'}.png") && ( -e "/srv/web/ipfire/html/graphs/qos-graph-$qossettings{'IMQ_DEV'}.png")) {
	print <<END
		<tr><td colspan='9' align='center'><img alt="" src="/graphs/qos-graph-$qossettings{'RED_DEV'}.png" />
		<tr><td colspan='9' align='center'><img alt="" src="/graphs/qos-graph-$qossettings{'IMQ_DEV'}.png" />
END
;}


&Header::closebox();
&Header::closebigbox();
&Header::closepage();

sub gengraph {
	$qossettings{'DEV'} = shift;
	$qossettings{'CLASS'} = shift;
	my $ERROR="";
	if ( $qossettings{'DEV'} eq $qossettings{'RED_DEV'} ) { 
		$qossettings{'CLASSPRFX'} = '1';
	} else { 
		$qossettings{'CLASSPRFX'} = '2';
	}
	my $color=random_hex_color(6);

	RRDs::graph ("/srv/web/ipfire/html/graphs/class_$qossettings{'CLASSPRFX'}-$qossettings{'CLASS'}_$qossettings{'DEV'}-packets.png",
		"--start", "-3240", "-aPNG", "-i", "-z",
		"--alt-y-grid", "-w 600", "-h 150", "-r",
		"--color", "SHADEA#EAE9EE",
		"--color", "SHADEB#EAE9EE",
		"--color", "BACK#FFFFFF",
		"-t $qossettings{'CLASS'} ($qossettings{'DEV'})",
		"DEF:pkts=/var/log/rrd/class_$qossettings{'CLASSPRFX'}-$qossettings{'CLASS'}_$qossettings{'DEV'}.rrd:pkts:AVERAGE",
		"DEF:dropped=/var/log/rrd/class_$qossettings{'CLASSPRFX'}-$qossettings{'CLASS'}_$qossettings{'DEV'}.rrd:dropped:AVERAGE",
		"DEF:overlimits=/var/log/rrd/class_$qossettings{'CLASSPRFX'}-$qossettings{'CLASS'}_$qossettings{'DEV'}.rrd:overlimits:AVERAGE",
		"AREA:pkts$color:packets",
		"GPRINT:pkts:LAST:total packets\\:%8.3lf %s packets\\j",
		"LINE3:dropped#FF0000:dropped",
		"GPRINT:dropped:LAST:dropped packets\\:%8.3lf %s packets\\j",
		"LINE3:overlimits#0000FF:overlimits",
		"GPRINT:overlimits:LAST:overlimits\\:%8.3lf %s packets\\j",
	);
}


sub overviewgraph {
	$qossettings{'DEV'} = shift;
	if ( $qossettings{'DEV'} eq $qossettings{'RED_DEV'} ) { 
		$qossettings{'CLASSPRFX'} = '1';
	} else { 
		$qossettings{'CLASSPRFX'} = '2';
	}
	my $ERROR="";
	my $count="1";
	my $color="#000000";
	my @command=("/srv/web/ipfire/html/graphs/qos-graph-$qossettings{'DEV'}.png",
		"--start", "-3240", "-aPNG", "-i", "-z",
		"--alt-y-grid", "-w 600", "-h 150", "-r",
		"--color", "SHADEA#EAE9EE",
		"--color", "SHADEB#EAE9EE",
		"--color", "BACK#FFFFFF",
		"-t Auslastung auf ($qossettings{'DEV'})"
	);
	open( FILE, "< $classfile" ) or die "Unable to read $classfile";
	@classes = <FILE>;
	close FILE;
  	foreach $classentry (sort @classes)
  	{
  		@classline = split( /\;/, $classentry );
  		if ( $classline[0] eq $qossettings{'DEV'} )
  		{
			$color=random_hex_color(6);
			push(@command, "DEF:$classline[1]=/var/log/rrd/class_$qossettings{'CLASSPRFX'}-$classline[1]_$qossettings{'DEV'}.rrd:bits:AVERAGE");

			if ($count eq "1") {
				push(@command, "AREA:$classline[1]$color:Klasse $classline[1] - $classline[8]\\j");
			} else {
				push(@command, "STACK:$classline[1]$color:Klasse $classline[1] - $classline[8]\\j");
			}
			$count++;
		}
	}
	RRDs::graph (@command);
}

sub random_hex_color {
    my $size = shift;
    $size = 6 if $size !~ /^3|6$/;
    my @hex = ( 0 .. 9, 'a' .. 'f' );
    my @color;
    push @color, @hex[rand(@hex)] for 1 .. $size;
    return join('', '#', @color);
}
