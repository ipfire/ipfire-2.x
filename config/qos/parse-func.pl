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
##   Jesper Dangaard Brouer <hawk@diku.dk>, d.15/4-2004
##
## CHANGELOG
##   2004-04-15:  Initial version.
##   2005-04-18:  Remove some warnings.
##
##########################################

#use Data::Dumper;

#our %classes_data;
#our %classes_info;
#our $tc_command="/sbin/tc";

my @input_htb = (<<"END_OF_HERE_HTB" =~ m/^\s*(.+)/gm);
class tbf 4220:1 parent 4220: 
class htb 1:1 root rate 400Kbit ceil 400Kbit burst 2111b cburst 2111b 
 Sent 12369084336 bytes 80967118 pkts (dropped 0, overlimits 0) 
 rate 45020bps 258pps 
 lended: 23353805 borrowed: 0 giants: 0
 tokens: 30210 ctokens: 30210

class htb 1:10 parent 1:1 prio 0 rate 80Kbit ceil 320Kbit burst 1701b cburst 2008b 
 Sent 80640087 bytes 247988 pkts (dropped 0, overlimits 0) 
 backlog 42p 
 lended: 230876 borrowed: 17112 giants: 0
 tokens: 127200 ctokens: 37940

class htb 1:20 parent 1:1 leaf 4220: prio 1 rate 100Kbit ceil 200Kbit burst 1727b cburst 1855b 
 Sent 2495181573 bytes 44034303 pkts (dropped 5837, overlimits 0) 
 lended: 43825585 borrowed: 208718 giants: 0
 tokens: 103424 ctokens: 55808

class htb 1:30 parent 1:1 leaf 4230: prio 3 rate 80Kbit ceil 400Kbit burst 1701b cburst 2111b 
 Sent 2060213567 bytes 5465574 pkts (dropped 121, overlimits 0) 
 rate 16851bps 35pps 
 lended: 4556992 borrowed: 908582 giants: 0
 tokens: -25364 ctokens: 32897

class htb 1:50 parent 1:1 leaf 4250: prio 5 rate 40Kbit ceil 120Kbit burst 1650b cburst 1752b 
 Sent 6071486687 bytes 24448436 pkts (dropped 8086739, overlimits 0) 
 rate 15801bps 85pps backlog 126p 
 lended: 8324530 borrowed: 16123780 giants: 0
 tokens: -202717 ctokens: -172499

class htb 1:666 parent 1:1 leaf 666: prio 7 rate 4Kbit ceil 40Kbit burst 1604b cburst 1650b 
 Sent 2148626078 bytes 6771069 pkts (dropped 2078536, overlimits 0) 
 rate 5221bps 17pps backlog 125p 
 lended: 675330 borrowed: 6095613 giants: 0
 tokens: -1149121 ctokens: -293386

END_OF_HERE_HTB

sub parse_class($) {
    my $device = "$_[0]";
    my $return_val = 1;

    my $timestamp = time;
    my @tc_output = `$tc_command -statistics class show dev $device`;
#    my @tc_output = @input_hfsc;
#    my @tc_output = @input_htb;
    my $result = $?;
    if ( $result != 0 ) {
	print "Error executing $tc_command\n";
	return $result;
    }

    $classes_data{last_update}{$device} = $timestamp;
    $classes_info{last_update}{$device} = $timestamp;

    #for my $line (@tc_output) {
    for my $i (0 .. $#tc_output) {

	my $line=$tc_output[$i];
	# Parsing HTB:
	# ------------
	if ( $line =~ m/class htb (\d+):(\d+)( root| parent )?(\d+:\d+)?( leaf )?(\d+)?:?( prio )?(\d+)? rate (.*) ceil (.*) burst (.*) cburst (.*)/ ) {
	    my $type  = "htb";
	    my $major = $1;
	    my $minor = $2;
	    my $class = "${major}-${minor}";
	    #my $hash  = "${class}_${device}";
	    my $parent= $4;
	    my $leaf  = $6;
	    my $prio  = $8;
	    my $rate  = $9;
	    my $ceil  = $10;
	    my $burst = $11;
	    my $cburst= $12;

	    #print "class: $class\n"."parent: $parent\n"."leaf: $leaf\n"."prio: $prio\n";
	    #print "rate: $rate\n"."ceil: $ceil\n"."burst: $burst\n"."cburst: $cburst\n";
	    
	    my ($bytes, $pkts, $dropped, $overlimits);
	    if ($tc_output[$i + 1] =~ m/Sent (\d+) bytes (\d+) pkt \(dropped (\d+), overlimits (\d+) requeues (\d+)\)/ ) {
		$bytes      = $1;
  	#print "bytes: $bytes\n";
	    } else { 
		print "$timestamp: ERROR(+1) - Unable to parse (class ${class}_$device): ";
		print "\"$tc_output[$i + 1]\"\n";
		$return_val="";
		next;
	    }

	    # Update the hash tables	 
	    my $hash="${class}_$device";

	    # Tests if previous data have been updated to file
	    if ( (exists $classes_data{$hash}{last_update}) &&
		 (exists $classes_data{$hash}{file_update})) {
		if ( $classes_data{$hash}{last_update} >
		     $classes_data{$hash}{file_update}   ){
		    print "Warning: old data from $hash has not been updated to file!\n";
		}
	    }

	    # Update the statistics data
	    # (need a function call for error checking)
	    $classes_data{$hash}{last_update} = $timestamp;
	    update_counter( $hash, $timestamp, "bytes"     , $bytes);
	    #(yes I know its bad/redundant, but it makes in easier elsewhere)
	    #print "\n";	  
	}

	# Parsing XXX:
	# ------------
	if ( $line =~ m/class XXX/ ) {
	    print "Matching class XXX\n";
	}

    }
    return $return_val;
}

# The main purpose of this function is to detect counter resets 
#  and avoid parsing them on to RRDtool which interprets them
#  as counter overflows, thus updating with a very large number.
sub update_counter  ($$$$) {
    my $class_hash = "$_[0]";
    my $timestamp  = "$_[1]";
    my $data_key   = "$_[2]";
    my $new_value;
    if ( defined $_[3]) {
	$new_value = "$_[3]";
    }
    # 
    my $max_allowed_wrap_increase = 100000000;
    my $old_value;
    if (exists $classes_data{$class_hash}{$data_key}) {
	$old_value  =  $classes_data{$class_hash}{$data_key};
        #print "old_value: $old_value\n";
    }

#    # If the new and old value is not defined, nothing is done 
#    if ((not defined $new_value) && (not defined $old_value)) {
#	return "";
#    }

    # Argh... the tc program outputs in unsigned long long (64 bit).
    #  but perls integers should be 32 bit, but some how perl
    #  manages to store numbers larger than 32 bit numbers.
    my $MAX_VALUE=0xFFFFFFFF;

    if ((defined $new_value) && (defined $old_value)) {
	my $delta = $new_value - $old_value;
	if ( $delta < 0 ) {
	    # Counter wrap around...
	    my $real_delta = $delta + $MAX_VALUE + 1;
	    if ($real_delta < 0) {
		print "($class_hash:$data_key): Perl-Magic using numbers bigger than 32bit ";
		print "new:$new_value - old:$old_value = delta:$delta, real_delta:$real_delta.\n";
	    }
	    print time . " ($class_hash:$data_key) Info: Counter wrap around (real delta:$real_delta)\n";
	    if ( ($real_delta > $max_allowed_wrap_increase) ||
		 ($real_delta < 0)) {
		# Properly a counter reset and not a wrap around 
		# A counter reset normally a result of a reload of the classes
		$classes_data{$class_hash}{$data_key}     = undef;
		$classes_info{$class_hash}{counter_reset} = $timestamp; 
		$classes_info{$class_hash}{last_update}   = $timestamp; 
		print time . "Warning: Real_delta too big, assuming Counter reset";
		print        "($class_hash:$data_key)\n";
		return "Counter reset";	      
	    }
	}
    }
   
    $classes_data{$class_hash}{$data_key} = $new_value;
    return 1;
}

sub update_info ($$$$) {
    my $class_hash = "$_[0]";
    my $timestamp  = "$_[1]";
    my $info_key   = "$_[2]";
    my $new_value;
    if ( defined $_[3]) {
	$new_value = "$_[3]";
    }
    my $old_value;
    if (exists $classes_info{$class_hash}{$info_key}) {
	$old_value  =  $classes_info{$class_hash}{$info_key};
        #print "old_value: $old_value\n";
    }

    # If the new and old value is not defined, nothing is done 
    if ((not defined $new_value) && (not defined $old_value)) {
	return "";
    }
    
    # An update is needed
    # - if the old_value is not defined and new_value is defined
    # - if the new_value is not defined and old_value is defined
    # - if the old_value differs from the new, 
    #
    if ( ((not defined $old_value) and (defined $new_value)) ||
	 ((not defined $new_value) and (defined $old_value)) ||
	 ("$old_value" ne "$new_value")) {

	# Special case: If the "type" changes the hash should be cleared
	if ( "$info_key" eq "type") {
	    #print "Type has changed clearing hash \n";
	    for my $key ( keys %{ $classes_info{$class_hash} } ) {
		delete( $classes_info{$class_hash}{$key});
		print " Deleting key: $key from: $class_hash \n";
	    }
	}

	if (defined $new_value) {
	    $classes_info{$class_hash}{$info_key} = $new_value;
	} else {
	    #print "New value undef -> Deleting key: $info_key from: $class_hash\n";
	    delete($classes_info{$class_hash}{$info_key});
	}
	    
	# Mark the class for an info-file update
	$classes_info{$class_hash}{last_update} = $timestamp;
	
	# Update list/array of "changed" keys
	push @{ $classes_info{$class_hash}{changed} }, $info_key; 

	# Print debug info
	#print "Update class:$class_hash $info_key=";
	#if (defined $new_value) {print "$new_value"};
	#print "\n";
	return 1;
    }
    return "";
}

# test
#parse_class(eth1);

#print Dumper(%classes_data);
#print Dumper(%classes_info);

return 1;
