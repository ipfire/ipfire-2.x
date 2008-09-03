
##########################################
##
## DESCRIPTION
##
##   RRD function for tc-graph.
##   Which is part of the ADSL-optimizer.
##
## REQUIRES
##
##
## AUTHOR
##   Jesper Dangaard Brouer <hawk@diku.dk>, d.15/4-2004
##
## CHANGELOG
##   2004-04-15:  Initial version.
##
##########################################

use RRDs;

if (not defined $STEP) {
    my $STEP=10;
}

my $heartbeat=$STEP*2;

# Update script samples every 10 seconds.
#  24*60*60  = 86400 seconds (== one day) 
#   8640 *10 = 86400 seconds (== one day)
#   8640 * 5days = 43200 seconds with 10 sec samples
#
my @rrd_data_sources = 
    ("-s", $STEP,
     "DS:bytes:COUNTER:$heartbeat:0:U",
     "RRA:AVERAGE:0.5:1:43200",
     "RRA:AVERAGE:0.5:7:8640",
     "RRA:AVERAGE:0.5:31:8640",
     "RRA:AVERAGE:0.5:372:8640",
     "RRA:MAX:0.5:7:8640",
     "RRA:MAX:0.5:31:8640",
     "RRA:MAX:0.5:372:8640"
     );


sub get_filename_rrd($) {
    my $class_device = "$_[0]";
    my $filename = "${rrd_datadir}class_${class_device}.rrd";
    return $filename;
}

sub create_rrdfile($) {
    my $class_device = "$_[0]";
    my $filename = get_filename_rrd($class_device);
    RRDs::create $filename, @rrd_data_sources;
    my $ERROR = RRDs::error;
    if ($ERROR) {
	my $timestamp = time;
	die "$timestamp: ERROR - Unable to create RRDfile \"$filename\": $ERROR\n";
    }
}

sub format_class_data($) {
    my $class = $_[0];
    my ($rrd_template, $rrd_data);
    my (@array_template, @array_data);
    #print "Ref:". ref($class) ."\n";

    # Select and correct undef values and key
    while ( (my $key, my $value) = each %{$class}) {
	# Skip timestamps
	if ( ($key eq "last_update") ||
	     ($key eq "file_update") ||
	     ($key =~ /hfsc_/ )) {next}

	push @array_template, $key; 

	if ( (not defined $value) ||
	     ("$value" eq "") ) { 
	    $value = "U";
	}
	push @array_data, $value; 
    }
    
    # Makes a RRD suitable input format
    $rrd_template = join(":",@array_template);
    $rrd_data     = join(":",@array_data);

    return ($rrd_template, $rrd_data);
}

sub update_rrds {

    my $res=0;

    # Find the class_device (keys) in %classes_data
    for my $class_device ( keys %classes_data ) {

	if ("last_update" eq "$class_device") {next}

	# Verify file exist (else create it) 
	my $filename = get_filename_rrd($class_device);
	if ( ! -f $filename ) {
	    print "Creating RRDfile: $filename\n";
	    create_rrdfile($class_device);
	}
	#print "$class_device\n";

	# Make a RRD suitable input format
	my ($rrd_template, $rrd_data) = format_class_data($classes_data{$class_device});
	#print "rrd_template: $rrd_template\n";
	#print "rrd_data: $rrd_data\n";


       # WHAT ABOUT:
	# $classes_data{$device}{last_update} ????
	my ($tmp, $device) = split /_/, $class_device;
	#print "device: $device $classes_data{last_update}{$device} \n";
	if ( (exists $classes_data{last_update}{$device}) ) {
	    if ((($classes_data{$class_device}{last_update} + $heartbeat) < 
		 $classes_data{last_update}{$device})) {
		print "WARNING: the class $class_device was";
		print "not updated in lastrun + heartbeat...\n";
		print "Assuming $class_device is removed,";
		print " thus deleteing from hash table.";
#	    # ??? MAYBE DELETE THE OLD HASH ???
		$res="Deleting class $class_device";
		for my $key ( keys %{ $classes_data{$class_device} } ) {
		    delete( $classes_data{$class_device}{$key});
		    print " Deleting key: $key from: $class_device \n";
		}
		delete $classes_data{$class_device};
		next;
	    }
	}

	# Verifies that it is new data, 
	#  and not old data which already have been updated
	# FIXME
#	print "$0 FIXME update_rrds \n";
	if ( exists $classes_data{$class_device}{file_update} ) {
	    if (($classes_data{$class_device}{file_update} >= 
		 $classes_data{$class_device}{last_update})) {
		print "Warning ($class_device):";
		print " data already updated... old data or deleted class?\n";
		$res="Old data or deleted class";
		# ??? MAYBE DELETE THE OLD HASH ???
		next;
	    }
	}


	# Update the RRD file
	my $update_time = $classes_data{$class_device}{last_update};
#	print "Updates: $filename time:$update_time\n";
#	print " --template=$rrd_template\n";
#	print " $update_time:$rrd_data\n";
	
#	`rrdtool update $filename --template=$rrd_template $update_time:$rrd_data`;
	RRDs::update ($filename, "--template=$rrd_template", 
		      "N:$rrd_data");

	my $ERROR = RRDs::error;
	if ($ERROR) {
	    my $timestamp = time;
	    print "$timestamp: WARNING - ";
	    print "Unable to update RRDfile \"$filename\": $ERROR\n";	    
	    $res="Unable to update RRDfile \"$filename\"";
	} else {
	    $classes_data{$class_device}{file_update} = time;
	}
    }
    return $res;
}


return 1;

