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
&General::readhash("/srv/web/ipfire/html/themes/ipfire/include/colors.txt", \%color);

my %sensorsettings = ();

my @sensorsgraphs = ();

# Main directory where rrdlog puts the sensor data.
my $sensorsdir = "$mainsettings{'RRDLOG'}/collectd/localhost";

# Open sensors directory.
opendir(SENSORS, "$sensorsdir") or die "Could not opendir $sensorsdir: $!\n";

# Read-in all sensors.
my @sensor_dirs = readdir(SENSORS);

# Close directory handle.
closedir(SENSORS);

# Loop through the grabbed sensors.
foreach my $sensor_dir (@sensor_dirs) {
	# Skip everything which does not start with "sensors-".
	next unless $sensor_dir =~ /^sensors-/;

	# Check if the omitet element is a directory.
	next unless (-d "$sensorsdir/$sensor_dir");

	# Open sensor directory and lookup for sensors.
	opendir(SENSOR_DIR, "$sensorsdir/$sensor_dir") or die "Could not opendir $sensorsdir/$sensor_dir: $!\n";

	# Grab single sensors from the directory.
	my @sensors = readdir(SENSOR_DIR);

	# Close directory handle.
	closedir(SENSOR_DIR);

	# Loop through the omited sensors.
	foreach my $sensor (@sensors) {
		# Skip everything which is not a regular file.
		next unless (-f "$sensorsdir/$sensor_dir/$sensor");

		# Add sensor to the array of sensorsgrapghs.
		push(@sensorsgraphs, "$sensorsdir/$sensor_dir/$sensor");
	}
}

# Look for ACPI Thermal Zone sensors.
my @thermal_zone_sensors = grep(/thermal-thermal_zone/, @sensor_dirs);

# If a thermal zone sensor has been found add it to the sensorsgraphs array.
if (@thermal_zone_sensors) {
	# Loop through the array of thermal zone sensors.
	foreach my $thermal_zone_sensor (@thermal_zone_sensors) {
		# Add the sensor to the array.
		push(@sensorsgraphs, "$sensorsdir/$thermal_zone_sensor");
	}
}

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

# This should be save, because no user given content will be processed.
#my @disks = `ls -1 /sys/block | grep -E '^sd|^nvme' | sort | uniq`;
my @disks = &get_disks();

foreach (@disks){
	my $disk = $_;
	chomp $disk;
	my @array = split(/\//,$disk);

	&Header::openbox('100%', 'center', "$array[$#array] $Lang::tr{'graph'}");
	&Graphs::makegraphbox("hardwaregraphs.cgi",$array[$#array],"day");
	&Header::closebox();
}

if ( grep(/thermal-thermal_zone/, @sensorsgraphs) ) {
	&Header::openbox('100%', 'center', "ACPI Thermal-Zone Temp $Lang::tr{'graph'}");
	&Graphs::makegraphbox("hardwaregraphs.cgi","thermaltemp","day");
	&Header::closebox();
}

if ( grep(/temperature-/, @sensorsgraphs) ) {
	&Header::openbox('100%', 'center', "hwtemp $Lang::tr{'graph'}");
	&Graphs::makegraphbox("hardwaregraphs.cgi","hwtemp","day");
	Header::closebox();
}

if ( grep(/fanspeed-/, @sensorsgraphs) ) {
	&Header::openbox('100%', 'center', "hwfan $Lang::tr{'graph'}");
	&Graphs::makegraphbox("hardwaregraphs.cgi","hwfan","day");
	&Header::closebox();
}

if ( grep(/voltage-/, @sensorsgraphs) ) {
	&Header::openbox('100%', 'center', "hwvolt $Lang::tr{'graph'}");
	&Graphs::makegraphbox("hardwaregraphs.cgi","hwvolt","day");
	&Header::closebox();
}

if ( @sensorsgraphs ) {
	sensorsbox();
}
&Header::closebigbox();
&Header::closepage();

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
	<td align='center' colspan='2' ><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
</tr>
</table>
</form>
END
;
	&Header::closebox();
}

sub get_disks () {
	my @disks;

	# Open virtal sys FS and grab block devices.
	opendir(SYS, "/sys/block") or die "Could not opendir /sys/block/: $!\n";

	# Grab all available block devices.
	my @blockdevs = readdir(SYS);

	# Close directory handle.
	closedir(SYS);

	# Loop through the array of blockdevs.
	foreach my $dev (@blockdevs) {
		# Skip all devices which does not start with "sd" or "nvme".
		next unless (( $dev =~ /^sd/) || ($dev =~ /^nvme/));

		# Add the device to the array of disks.
		push(@disks, $dev);
	}

	# Remove duplicates.
	my @disks = &uniq(@disks);

	# Sort the array.
	my @disks = sort(@disks);

	# Return the array.
	return @disks;
}

# Tiny code snipped to get a uniq() like function.
sub uniq {
	my %seen;
	return grep { !$seen{$_}++ } @_;
}
