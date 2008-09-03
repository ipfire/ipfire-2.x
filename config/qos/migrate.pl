#!/usr/bin/perl

my $rrddir = "/var/log/rrd";
my @files = `cd $rrddir && ls class_* `;

if ( -e "$rrddir/migrated" ){print "Already migrated rrd files -> exit.\n";exit 1;}

system("/etc/init.d/collectd stop");
system("/usr/local/bin/qosctrl stop");

foreach (@files){
		chomp($_);
		my @lines = `rrdtool dump $rrddir/$_`;
		
		my $fromhere = 0;
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
						if ( $_ =~ /\<database\>/ ){
							$fromhere = 1;next;
						}
						if ( $_ =~ /\<\/database\>/ ){
							$fromhere = 0;next;
						}
						if ( $fromhere eq "0" ){
								next;
						}else{
								my @t = split(/<v>/,$_);
								push(@newlines,$t[0]."<v>".$t[1]."</row>\n");
						}
		}
push(@newlines,"		</database>
	</rra>
</rrd>");
open(DATEI, ">/tmp/rrd.xml") || die "Unable to create temp file";
print DATEI @newlines;
close(DATEI);

system("rm -f $rrddir/$_");
system("rrdtool restore -f /tmp/rrd.xml $rrddir/$_");
print "$_ ... resized\n";
}

system("/etc/init.d/collectd start");
system("/usr/local/bin/qosctrl start");
system("touch $rrddir/migrated");
exit 0;
