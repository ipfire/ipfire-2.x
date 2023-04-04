#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2008  Michael Tremer & Christian Schmidt                      #
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

# This skript will migrate all old rrd files with ADSL Optimizer Style to a
# custom IPFire one only collecting byte count for the QoS classes

# Fore testing purpose i recommend to copy your rrd files to /tmp and change
# the rrddir, then you are able to test the migration without problems
# Migration will take all classes rrd into count

my $rrddir = "/var/log/rrd";
my @files = `cd $rrddir && ls class_*.rrd`;

# Ff migration was already done we will skip this to avoid errors
if ( -e "$rrddir/migrated" ){print "Already migrated rrd files -> exit.\n";exit 1;}

# Stop collectd and qos to ensure that no one further write to the rrds
system("/etc/init.d/collectd stop");
system("/usr/local/bin/qosctrl stop");

foreach (@files){
		chomp($_);
		
		# Dump the whole rrd file to human readable xml format into an array
		my @lines = `rrdtool dump $rrddir/$_`;
		
		# to ensure only needed raw data is extracted we will use a marker
		my $fromhere = 0;
		
		# because every rrd hase the same header we can use a general one deleting
		# lastupdate and lastvalue they will be set the first time rrd is written
		# after migration
		my @newlines = "<!-- Round Robin Database Dump --><rrd>	<version> 0003 </version>
	<step> 10 </step> <!-- Seconds -->
	<lastupdate> </lastupdate>

	<ds>
		<name> bytes </name>
		<type> COUNTER </type>
		<minimal_heartbeat> 20 </minimal_heartbeat>
		<min> 0.0000000000e+00 </min>
		<max> NaN </max>

		<!-- PDP Status -->
		<last_ds> </last_ds>
		<value> </value>
		<unknown_sec> 0 </unknown_sec>
	</ds>

<!-- Round Robin Archives -->	<rra>
		<cf> AVERAGE </cf>
		<pdp_per_row> 1 </pdp_per_row> <!-- 10 seconds -->

		<params>
		<xff> 5.0000000000e-01 </xff>
		</params>
		<cdp_prep>
			<ds>
			<primary_value> </primary_value>
			<secondary_value> NaN </secondary_value>
			<value> NaN </value>
			<unknown_datapoints> 0 </unknown_datapoints>
			</ds>
		</cdp_prep>
		<database>
";
		foreach (@lines){
		
						# if database content line is found we will start to extract the values
						if ( $_ =~ /\<database\>/ ){
							$fromhere = 1;next;
						}
						# if database content is finished we will stop to extract the values
						if ( $_ =~ /\<\/database\>/ ){
							$fromhere = 0;next;
						}
						# if extraction is not set we will skip this line else we will extract
						# only the first row and drop all the other ones, the new raw line
						# will be written to and array
						if ( $fromhere eq "0" ){
								next;
						}else{
								my @t = split(/<v>/,$_);
								push(@newlines,$t[0]."<v>".$t[1]."</row>\n");
						}
		}
# Add default footer to the array so a valid rrd xml file will be created
push(@newlines,"		</database>
	</rra>
</rrd>");
# Now write the whole array to an xml file
open(DATEI, ">/tmp/rrd.xml") || die "Unable to create temp file";
print DATEI @newlines;
close(DATEI);

# Delete the old rrd file and restore a new one with content from the xml file
system("rm -f $rrddir/$_");
system("rrdtool restore -f /tmp/rrd.xml $rrddir/$_");
print "$_ ... resized\n";
}

# Now we can restart the collection
system("/etc/init.d/collectd start");
system("/usr/local/bin/qosctrl start");

# Finaly we will delete unneeded evt files and touch the migration file
system("rm -f $rrddir/*.evt");
system("touch $rrddir/migrated");
exit 0;
