#!/usr/bin/perl

##########################################
##
## NAME
##
## DESCRIPTION
##
##   Which is part of the ADSL-optimizer.
##
## USAGE / FUNCTIONS
##   
##   
##   
##    
##
## REQUIRES
##
##
## AUTHOR
##   Jesper Dangaard Brouer <hawk@diku.dk>, d.21/4-2004
##
## CHANGELOG
##   2004-04-21:  Initial version.
##
##########################################

sub update_event_file($$$) {
    my $filename    = $_[0];
    my $information = $_[1];
    my $timestamp   = $_[2];

    if ("$information" ne "") {
	# Append to file
	open( OUTPUT, ">>$filename") 
	    or print "ERROR: Opening/updating event file $filename\n";
	print OUTPUT "$timestamp $information\n";
	close(OUTPUT);
    }
}

sub update_info_file($$$) {
    my $filename    = $_[0];
    my $information = $_[1];
    my $timestamp   = $_[2];
    # Truncate file
    open( OUTPUT, ">$filename") 
	or print "ERROR: Opening/updating info event file $filename\n";
    print OUTPUT "$timestamp $information\n";
    close(OUTPUT);
    
}

sub process_events {

    my @test = keys %classes_info;
    if ( $#test < 0) {	
	print  time, " [process_events] WARNING: classes_info empty!\n";
	return "classes_info empty";
    }

    my @bandwidth_items = ( "type", "prio", "rate", "ceil" );

    my $event_reduced = "";
    my $last_update;

    # Find the class_device (keys) in %classes_info
    for my $class_device ( sort keys %classes_info ) {

	if ("$class_device" eq "last_update") {next}

	my $event_class    = "";
	my $bandwidth_info = "";

	# Tests if something has changed
	if ((not exists $classes_info{$class_device}{file_update}) ||
	    ($classes_info{$class_device}{last_update} >
	     $classes_info{$class_device}{file_update})) {
	    
	    $last_update = $classes_info{$class_device}{last_update};	

	    $event_class   .= "($class_device)";
	    if ( "$event_reduced" eq "" ) {$event_reduced="Class changed:"}
	    $event_reduced .= " ($class_device)";
	    # The list of changed keys
	    while( $changed_key = 
		   shift @{ $classes_info{$class_device}{changed} }) 
	    {
		my $value = $classes_info{$class_device}{$changed_key};
		$event_class .= " $changed_key=$value";
	    }

	    # When something changed always update all the bandwidth info
	    foreach my $item (@bandwidth_items) {
		if (exists $classes_info{$class_device}{$item}) {
		    my $value = $classes_info{$class_device}{$item};
		    if (defined $value) {
			$bandwidth_info .= "  $item:$value";
		    }
		}		
	    }
	    
	    print time . "($class_device) changes... ($last_update) \"$bandwidth_info\" \n";

	    $classes_info{$class_device}{file_update}=$last_update;
	    
	    my $event_file = get_filename_event($class_device);
	    update_event_file($event_file    , $event_class,   $last_update);

	    my $info_file = get_filename_bandwidth_info($class_device);
	    update_info_file($info_file, $bandwidth_info, $last_update);
	}
	
    }
    # Only one line per process_events call
    # (notice $last_update is the latest timestamp assignment) 
    if (defined $last_update) {
	update_event_file($event_file_all, $event_reduced, $last_update);
    }
}


1;
