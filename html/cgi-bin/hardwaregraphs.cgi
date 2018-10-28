#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2005-2011  IPFire Team                                        #
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

my %sensorsettings = ();

my @sensorsgraphs = ();
my @sensorsdir = `ls -dA $mainsettings{'RRDLOG'}/collectd/localhost/sensors-*/`;
foreach (@sensorsdir){
	chomp($_);chop($_);
	foreach (`ls $_/*`){
		chomp($_);
		push(@sensorsgraphs,$_);
	}
}

my @querry = split(/\?/,$ENV{'QUERY_STRING'});
$querry[0] = '' unless defined $querry[0];
$querry[1] = 'hour' unless defined $querry[1];

if ( $querry[0] =~ "hwtemp"){
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	&Graphs::updatehwtempgraph($querry[1]);
}elsif ( $querry[0] =~ "hwfan"){
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	&Graphs::updatehwfangraph($querry[1]);
}elsif ( $querry[0] =~ "hwvolt"){
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	&Graphs::updatehwvoltgraph($querry[1]);
}elsif ( $querry[0] =~ "thermaltemp"){
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	&Graphs::updatethermaltempgraph($querry[1]);
}elsif ( $querry[0] =~ "sd?" ){
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	&Graphs::updatehddgraph($querry[0],$querry[1]);
}elsif ( $querry[0] =~ "nvme?" ){
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	&Graphs::updatehddgraph($querry[0],$querry[1]);
}else{
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'hardware graphs'}, 1, '');
	&Header::openbigbox('100%', 'left');

	&Header::getcgihash(\%sensorsettings);

	if ( $sensorsettings{'ACTION'} eq $Lang::tr{'save'} ) {
		foreach(@sensorsgraphs){
			chomp($_);
				$_ =~ /\/(.*)sensors-(.*)\/(.*)\.rrd/;
				my $label = $2.$3;$label=~ s/-//g;
				if ( $sensorsettings{'LINE-'.$label} ne "on" ){
					$sensorsettings{'LINE-'.$label} = 'off';
				} elsif ($sensorsettings{'LINE-'.$label} eq "on" ){
					$sensorsettings{'LINE-'.$label} = 'checked';
				}
				$sensorsettings{'LABEL-'.$label} =~ s/\W//g;
		}
		&General::writehash("${General::swroot}/sensors/settings", \%sensorsettings);
	}

	my @disks = `ls -1 /sys/block | grep -E '^sd|^nvme' | sort | uniq`;

	foreach (@disks){
		my $disk = $_;
		chomp $disk;
		my @array = split(/\//,$disk);

		&Header::openbox('100%', 'center', "$array[$#array] $Lang::tr{'graph'}");
		&Graphs::makegraphbox("hardwaregraphs.cgi",$array[$#array],"day");
		&Header::closebox();
	}

	if ( `ls $mainsettings{'RRDLOG'}/collectd/localhost/thermal-thermal_zone* 2>/dev/null` ) {
		&Header::openbox('100%', 'center', "ACPI Thermal-Zone Temp $Lang::tr{'graph'}");
		&Graphs::makegraphbox("hardwaregraphs.cgi","thermaltemp","day");
		&Header::closebox();
	}

	if ( `ls $mainsettings{'RRDLOG'}/collectd/localhost/sensors-*/temperature-* 2>/dev/null` ) {
		&Header::openbox('100%', 'center', "hwtemp $Lang::tr{'graph'}");
		&Graphs::makegraphbox("hardwaregraphs.cgi","hwtemp","day");
		Header::closebox();
	}

	if ( `ls $mainsettings{'RRDLOG'}/collectd/localhost/sensors-*/fanspeed-* 2>/dev/null` ) {
		&Header::openbox('100%', 'center', "hwfan $Lang::tr{'graph'}");
		&Graphs::makegraphbox("hardwaregraphs.cgi","hwfan","day");
		&Header::closebox();
	}

	if ( `ls $mainsettings{'RRDLOG'}/collectd/localhost/sensors-*/voltage-* 2>/dev/null` ) {
		&Header::openbox('100%', 'center', "hwvolt $Lang::tr{'graph'}");
		&Graphs::makegraphbox("hardwaregraphs.cgi","hwvolt","day");
		&Header::closebox();
	}

	if ( `ls $mainsettings{'RRDLOG'}/collectd/localhost/sensors-* 2>/dev/null` ) {
		sensorsbox();
	}
	&Header::closebigbox();
	&Header::closepage();

}


sub sensorsbox {
	&Header::openbox('100%', 'center', "$Lang::tr{'mbmon settings'}");

	print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='100%' border='0' cellspacing='5' cellpadding='0' align='center'>
<tr>
	<td align='right' width='40%'><b>$Lang::tr{'mbmon display'}</b></td>
	<td align='left'><b>$Lang::tr{'mbmon label'}</b></td>
</tr>
END
;

	foreach (@sensorsgraphs){
			$_ =~ /\/(.*)sensors-(.*)\/(.*)\.rrd/;
			my $label = $2.$3;$label=~ s/-//g;
			$sensorsettings{'LABEL-'.$label}="$label";
			$sensorsettings{'LINE-'.$label}="checked";
			&General::readhash("${General::swroot}/sensors/settings", \%sensorsettings);
			print("<tr><td align='right'><input type='checkbox' name='LINE-$label' $sensorsettings{'LINE-'.$label} /></td>");
	 		print("<td><input type='text' name='LABEL-$label' value='$sensorsettings{'LABEL-'.$label}' size='25' /></td></tr>\n");
	}

	print <<END
<tr>
	<td align='center' colspan='2' ><input type='submit' name='ACTION' value=$Lang::tr{'save'} /></td>
</tr>
</table>
</form>
END
;
	&Header::closebox();
}
