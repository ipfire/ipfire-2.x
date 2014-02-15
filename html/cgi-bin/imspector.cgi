#!/usr/bin/perl
#
# IMSpector real-time log viewer
# (c) SmoothWall Ltd 2008
#
# Released under the GPL v2.

use POSIX qw(strftime);

# Common configuration parameters.

my $logbase = "/var/log/imspector/";
my $oururl = '/cgi-bin/imspector.cgi';

# Colours

my $protocol_colour     = '#06264d';
my $local_colour        = '#1d398b';
my $remote_colour       = '#2149c1';
my $conversation_colour = '#335ebe';

my $local_user_colour   = 'blue';
my $remote_user_colour  = 'green';

# No need to change anything from this point

# Page declaration, The following code should parse the CGI headers, and render the page
# accordingly... How you do this depends what environment you're in.

my %cgiparams;

print "Content-type: text/html\n";
print "\n";

if ($ENV{'QUERY_STRING'})
{
	my @vars = split('\&', $ENV{'QUERY_STRING'});
	foreach $_ (@vars)
	{
		my ($var, $val) = split(/\=/);
		$cgiparams{$var} = $val;
	}
}

# Act in Tail mode (as in just generate the raw logs and pass back to the other CGI

if ( defined $cgiparams{'mode'} and $cgiparams{'mode'} eq "render" ){
	&parser( $cgiparams{'section'}, $cgiparams{'offset'}, $cgiparams{'conversation'}, $cgiparams{'skimhtml'} );
	exit;
}

# Start rendering the Page using Express' rendering functions

my $script = &scriptheader();

# Print Some header information 

print qq|
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
	<title>IMSpector real-time log viewer</title>
	$script
</head>
<body>
|;

print &pagebody();

# and now finish off the HTML page.

print qq|
</body>
</html>
|;

exit;

# -----------------------------------------------------------------------------
# ---------------------- IMSPector Log Viewer Code ----------------------------
# -----------------------------------------------------------------------------
#           ^"^                                                 ^"^

# Scriptheader
# ------------
# Return the bulk of the page, which should reside in the pages <head> field

sub scriptheader
{
	my ( $sec, $min, $hour, $mday, $mon, $year, $wday, $yday ) = localtime( time() );
	$year += 1900; $mon++;
	my $conversation = sprintf( "%.4d-%.2d-%.2d", $year, $mon, $mday );

	my $script = qq {
<script type="text/javascript">
var section	     ='none';
var moveit   	     = 1;
var skimhtml 	     = 1;
var the_timeout;
var offset   	     = 0;
var fragment 	     = "";
var conversationdate = "$conversation";

function xmlhttpPost()
{
	var self = this;
	
	if (window.XMLHttpRequest) {
		// Mozilla/Safari
		self.xmlHttpReq = new XMLHttpRequest();
	} else if (window.ActiveXObject) {
		// IE
		self.xmlHttpReq = new ActiveXObject("Microsoft.XMLHTTP");
	}

	var url = "$url" + "?mode=render&section=" + section + "&skimhtml=" + skimhtml + "&offset=" + offset + "&conversation=" + conversationdate;
    	self.xmlHttpReq.open('POST', url, true);
	self.xmlHttpReq.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

	self.xmlHttpReq.onreadystatechange = function() {
		if ( self.xmlHttpReq && self.xmlHttpReq.readyState == 4) {
			updatepage(self.xmlHttpReq.responseText);
		}
	}

	document.getElementById('status').style.display = "inline";

	self.xmlHttpReq.send( url );
	delete self;
}

function updatepage(str){
	/* update the list of conversations ( if we need to ) */

	var parts = str.split( "--END--\\n" );

	var lines = parts[0].split( "\\n" );

	for ( var line = 0 ; line < lines.length ; line ++ ){
		var a = lines[line].split("|");

		if ( !a[1] || !a[2] || !a[3] ){
			continue;
		}

		/* convert the modification stamp into something sensible */
		a[5] = parseInt( a[5] * 24 * 60 * 60 );

		/* create titling information if needed */
		if ( !document.getElementById( a[1] ) ){
			document.getElementById('conversations').innerHTML += "<div id='" + a[1] + "_t' style='width: 100%; background-color: #d9d9f3; color: $protocol_colour;'>" + a[1] + "</div><div id='" + a[1] + "' style='width: 100%; background-color: #e5e5f3;'></div>";
		}

		if ( !document.getElementById( a[1] + "_" + a[2] ) ){
			document.getElementById( a[1] ).innerHTML += "<div id='" + a[1] + "_" + a[2] + "_t' style='width: 100%; color: $local_colour; padding-left: 5px;'>" + a[2] + "</div><div id='" + a[1] + "_" + a[2] + "' style='width: 100%; background-color: #efeffa; border-bottom: solid 1px #d9d9f3;'></div>";
		}

		if ( !document.getElementById( a[1] + "_" + a[2] + "_" + a[3] ) ){
			document.getElementById( a[1] + "_" + a[2] ).innerHTML += "<div id='" + a[1] + "_" + a[2] + "_" + a[3] + "_t' style='width: 100%; color: $remote_colour; padding-left: 10px; cursor: pointer;' onClick=" + '"' + "setsection('" + a[1] + "|" + a[2] + "|" + a[3] + "|" + a[4] + "');" + '"' + "' + >&raquo;&nbsp;" + a[3] + "</div><div id='" + a[1] + "_" + a[2] + "_" + a[3] + "' style='width: 1%; display: none;'></div>";
		}

		if ( document.getElementById( a[1] + "_" + a[2] + "_" + a[3] ) && a[5] <= 60 ){
			/* modified within the last minute! */
			document.getElementById( a[1] + "_" + a[2] + "_" + a[3] + "_t" ).style.fontWeight = "bold";
		} else {
			document.getElementById( a[1] + "_" + a[2] + "_" + a[3] + "_t" ).style.fontWeight = "normal";
		}
		delete a;
	}

	delete lines;

	/* rework the list of active conversation dates ... */

	var lines = parts[1].split( "\\n" );

	var the_select = document.getElementById('conversationdates');
	the_select.options.length = 0;
		
	for ( var line = 0 ; line < lines.length ; line ++ ){
		if ( lines[ line ] != "" ){
			the_select.options.length ++;
			the_select.options[ line ].text  = lines[line];
			the_select.options[ line ].value = lines[line];
			if ( lines[line] == conversationdate ){
				the_select.selectedIndex = line;
			}
		}
	}

	delete the_select;
	delete lines;

	/* determine the title of this conversation */
	if ( parts[2] ){
		var details = parts[2].split(",");
		var title = details[0] + " conversation between <span style='color: $local_user_colour;'>" + details[ 1 ] + "</span> and <span style='color: $remote_user_colour;'>" + details[2] + "</span>";
		if ( !details[1] ){
			title = "&nbsp;";
		}

		document.getElementById('status').style.display = "none";
	
		var bottom  = parseInt( document.getElementById('content').scrollTop );
		var bottom2 = parseInt( document.getElementById('content').style.height );
		var absheight = parseInt( bottom + bottom2 );

		if ( absheight == document.getElementById('content').scrollHeight ){	
			moveit = 1;
		}

		fragment += parts[4];
		document.getElementById('content').innerHTML = "<table style='width: 100%'>" + fragment + "</table>";
		if (moveit == 1 ){
			document.getElementById('content').scrollTop = 0;
			document.getElementById('content').scrollTop = document.getElementById('content').scrollHeight;
		}

		document.getElementById('content_title').innerHTML = title;
		delete details;
		delete title;
		delete bottom;
		delete bottom2;
		delete absheight;
	}

	/* set the file offset */
	offset = parts[3];

	if ( moveit == 1 ){
		document.getElementById('scrlck').style.color = 'green';
	} else {
		document.getElementById('scrlck').style.color = '#202020';
	}

	if ( skimhtml == 1 ){
		document.getElementById('skimhtml').style.color = 'green';
	} else {
		document.getElementById('skimhtml').style.color = '#202020';
	}

	delete parts;

	the_timeout = setTimeout( "xmlhttpPost();", 5000 );
}

function setsection( value )
{
	section = value;
	offset = 0;
	fragment = "";
	moveit = 1;
	clearTimeout(the_timeout);
	xmlhttpPost();
	document.getElementById('content').scrollTop = 0;
	document.getElementById('content').scrollTop = document.getElementById('content').scrollHeight;
}

function togglescrlck()
{
	if ( moveit == 1 ){
		moveit = 0;
		document.getElementById('scrlck').style.color = '#202020';
	} else {
		moveit = 1;
		document.getElementById('scrlck').style.color = 'green';
	}
}

function toggleskimhtml()
{
	if ( skimhtml == 1 ){
		skimhtml = 0;
		document.getElementById('skimhtml').style.color = '#202020';
	} else {
		skimhtml = 1;
		document.getElementById('skimhtml').style.color = 'green';
	}
	clearTimeout(the_timeout);
	xmlhttpPost();
}

function setDate()
{
	var the_select = document.getElementById('conversationdates');
	conversationdate = the_select.options[ the_select.selectedIndex ].value;
	document.getElementById('conversations').innerHTML = "";
	fragment = "";
	offset = 0;
	section = "";
	clearTimeout(the_timeout);
	xmlhttpPost();
}

</script>
	};

	return $script;
}

# pagebody function 
# -----------------
# Return the HTML fragment which includes the page body.

sub pagebody
{
	my $body = qq {
	<div style='width: 100%; text-align: right;'><span id='status' style='background-color: #fef1b5; display: none;'>Updating</span>&nbsp;</div>
	<style>
	
.powerbutton {
	color:  #202020;
	font-size: 9pt;
	cursor: pointer;
}

.remoteuser {
	color: $remote_user_colour;
	font-size: 9pt;
}

.localuser {
	color: $local_user_colour;
	font-size: 9pt;
}

	</style>
	<table style='width: 100%;'>
		<tr>
			<td style='width: 170px; text-align: left; vertical-align: top; overflow: auto; font-size: 8pt; border: solid 1px #c0c0c0;'><div id='conversations' style='height: 400px; overflow: auto; font-size: 10px; overflow-x: hidden;'></div></td>
			<td style='border: solid 1px #c0c0c0;'>
				<div id='content_title' style='height: 20px; overflow: auto; vertical-align: top; background-color: #E6E8FA; border-bottom: solid 1px #c0c0c0;'></div>
				<div id='content' style='height: 376px; overflow: auto; vertical-align: bottom; border-bottom: solid 1px #c0c0c0; overflow-x: hidden;'></div>
				<div id='content_subtitle' style='height: 24px; overflow: auto; vertical-align: top; background-color: #E6E8FA; width: 100%; padding: 2px;'>
					<div style='width: 60%; float: left;' id='statuswindow'>
						For conversations on:&nbsp;
						<select id='conversationdates' onChange='setDate()';>
						</select>
					</div>
					<div style='width: 40%; text-align: right; float: right;'>
						<span class='powerbutton' id='skimhtml' onClick='toggleskimhtml();'>[HTML]</span>
						<span class='powerbutton' id='scrlck' onClick='togglescrlck();'>[SCROLL LOCK]</span>
					</div>
				</div>
			</td>
		</tr>
	</table>
	<script>xmlhttpPost();</script>
	};
	return $body;
}

# Parser function ...
# ---------------
# Retrieves the IMspector logs from their nestling place and displays them accordingly.

sub parser
{
	my ( $section, $offset, $conversationdate, $skimhtml ) = @_;
	# render the user list ...

	chomp $offset;	

	unless ( $offset =~ /^([\d]*)$/ ){
		print STDERR "Illegal offset ($offset $1) resetting...\n";
		$offset = 0;
	}

	# browse for the available protocols
	unless ( opendir DIR, $logbase ){
		exit;
	}

	my %conversationaldates;
	my @protocols = grep {!/^\./} readdir(DIR);		

	foreach my $protocol ( @protocols ){
		unless ( opendir LUSER, "$logbase$protocol" ){
			next;
		}
	
		my @localusers = grep {!/^\./} readdir(LUSER);		
		foreach my $localuser ( @localusers ){
			unless ( opendir RUSER, "$logbase$protocol/$localuser/" ){
				next;
			}
			my @remoteusers = grep {!/^\./} readdir( RUSER );
			foreach my $remoteuser ( @remoteusers ){
				unless ( opendir CONVERSATIONS, "$logbase$protocol/$localuser/$remoteuser/" ){
					next;
				}
				my @conversations = grep {!/^\./} readdir( CONVERSATIONS );
				foreach my $conversation ( @conversations ){
					$conversationaldates{ $conversation } = $localuser;
				}

				closedir CONVERSATIONS;

				my ( $sec, $min, $hour, $mday, $mon, $year, $wday, $yday ) = localtime( time() );
				$year += 1900; $mon++;
				my $conversation = sprintf( "%.4d-%.2d-%.2d", $year, $mon, $mday );

				$conversation = $conversationdate if ( defined $conversationdate and $conversationdate ne "" );

				if ( -e "$logbase$protocol/$localuser/$remoteuser/$conversation" ){
					my $modi = -M "$logbase$protocol/$localuser/$remoteuser/$conversation";
					print "|$protocol|$localuser|$remoteuser|$conversation|$modi\n";
				}
			}
			closedir RUSER;
		}
		closedir LUSER;
	}
	closedir DIR;

	print "--END--\n";

	# display a list of conversational dates .. i.e. the dates which we have conversations on.
	foreach my $key ( sort keys %conversationaldates ){
		print "$key\n";
	}
	
	print "--END--\n";


	# now check the log file ...
	
	if ( $section ne "none" ){
		my ( $protocol, $localuser, $remoteuser, $conversation ) = split /\|/, $section;
		
		print "$protocol, $localuser, $remoteuser, $conversation\n";
		print "--END--\n";
		
		my $filename = "$logbase$protocol/$localuser/$remoteuser/$conversation";
		
		unless ( open(FD, "$filename" ) ){
			exit;
		};

		# perform some *reasonably* complicated file hopping and stuff of that ilk.
		# it's not beyond reason that logs *could* be extremely large, so what we
		# should do to speed up their processing is to jump to the end of the file,
		# then backtrack a little (say a meg, which is a reasonably amount of logs)
		# and parse from that point onwards.  This, *post* filtering might of course
		# not leave us with the desired resolution for the tail.  If this is the case,
		# we keep that array and jump back another meg and have another go, concatinating
		# the logs as we go.... <wheh>

		my $jumpback = 100000; # not quite a meg, but hey ho	
		my $goneback = 0;
		my $gonebacklimit = 1000000000;  # don't go back more than 100MB

		# firstly jump to the end of the file.
		seek( FD, 0, 2 );

		my $log_position = tell( FD );
		my $end = $log_position;
		my $end_position = $log_position;

		my $lines;
		my @content;

		my $TAILSIZE = 100;

		do {
			$end_position = $log_position;

			if ( $offset != 0 ){
				# we were given a hint as to where we should have been anyhow ..
				# so we might as well use that to go back to.
				$log_position = $offset;
				$goneback = $end_position - $log_position;
			} else {
				$log_position -= $jumpback;
				$goneback += $jumpback;
			}

			last if ( $goneback > $gonebacklimit );

			if ( $log_position > 0 ){
				seek( FD, $log_position, 0 );
			} else {
				seek( FD, 0, 0 );
			}
	
			my @newcontent;

			while ( my $line = <FD> and ( tell( FD ) <= $end_position ) ){
				chomp $line;
				push @content, $line;
			}
			shift @content if $#content >= $TAILSIZE;
		} while ( $#content < $TAILSIZE and $log_position > 0 and $offset == 0 );

		# trim the content down as we may have more entries than we should.
	
		while ( $#content > $TAILSIZE ){ shift @content; };
		close FD;

		print "$end_position\n--END--\n";

		foreach my $line ( @content ){
			my ( $address, $timestamp, $direction, $type, $filtered, $cat, $data );

			( $address, $timestamp, $direction, $type, $filtered, $cat, $data ) = ( $line =~ /([^,]*),(\d+),(\d+),(\d+),(\d+),([^,]*),(.*)/ );

			# are we using the oldstyle or new style logs ?
			if ( not defined $address and not defined $timestamp ){
				( $address, $timestamp, $type, $data ) = ( $line =~ /([^,]*),([^,]*),([^,]*),(.*)/ );
				if ( $type eq "1" ){
					$direction = 0;
					$type      = 1;
				} elsif ( $type eq "2" ){
					$direction = 1;
					$type      = 1;
				} elsif ( $type eq "3" ){
					$direction = 0;
					$type      = 2;
				} elsif ( $type eq "4" ){
					$direction = 1;
					$type      = 4;
				}
			}
			
			my ( $severity, $classification ) = '0', 'None';
			if ($cat) {
				( $severity, $classification) = split(/ /, $cat, 2); }
			else {
				$cat = 'N/A'; }

			my $red = 255;
			my $green = 255;
			my $blue = 255;

			if ($severity < 0 && $severity >= -5) {
				$red = 0; $green = abs($severity) * (255 / 5); $blue = 0; }
			elsif ($severity > 0 && $severity <= 5) {
				$red = $severity * (255 / 5); $green = 0; $blue = 0; }
			else {
				$red = 0; $green = 0; $blue = 0; }
			
			my $severitycolour = '';
			if ($cat ne 'N/A') {
				$severitycolour = sprintf("background-color: #%02x%02x%02x;", $red, $green, $blue); }

			# some protocols (ICQ, I'm looking in your direction) have a habit of starting 
			# and ending each sentence with HTML (evil program)		

			if ( defined $skimhtml and $skimhtml eq "1" ){	
				$data =~ s/^<HTML><BODY[^>]*><FONT[^>]*>//ig;	
				$data =~ s/<\/FONT><\/BODY><\/HTML>//ig;	
			}

			$data = &htmlescape($data);
			$data =~ s/\r\\n/<br>\n/g;
			my $user = "";

			my $bstyle = "";
			$bstyle = "style='background-color: #FFE4E1;'" if ( $filtered eq "1" );

			if ( $type eq "1" ){
				# a message message (from remote user)
				if ( $direction eq "0" ){
					# incoming
					my $u = $remoteuser;
					$u =~ s/\@.*//g;
					$user = "&lt;<span class='remoteuser'>$u</span>&gt;";
				} else { 
					# outgoing message
					my $u = $localuser;
					$u =~ s/\@.*//g;
					$user = "&lt;<span class='localuser'>$u</span>&gt;";
				}
			} elsif ($type eq "2") {
				if ( $direction eq "0" ){
					# incoming file
					my $u = $remoteuser;
					$u =~ s/\@.*//g;
					$user = "&lt;<span class='remoteuser'><b><i>$u</i></b></span>&gt;";
				} else {
					# outgoing file
					my $u = $localuser;
					$u =~ s/\@.*//g;
					$user = "&lt;<span class='localuser'><b><i>$u</i></b></span>&gt;";
				}
			}

			my $t = strftime "%H:%M:%S", localtime($timestamp);
			if ($type eq "3" or $type eq "4") {
				$data = "<b><i>$data</i></b>";
			}
			print "<tr $bstyle><td style='width: 30px; vertical-align: top;'>[$t]</td><td style='width: 10px; $severitycolour' title='$cat'><td style=' width: 60px; vertical-align: top;'>$user</td><td style='vertical-align: top;'>$data</td></tr>";
		}
	}
	return;
}

sub htmlescape
{
	my ($value) = @_;
	$value =~ s/&/\&amp;/g;
	$value =~ s/</\&lt;/g;
	$value =~ s/>/\&gt;/g;
	$value =~ s/"/\&quot;/g;
	$value =~ s/'/\&#39;/g;
	return $value;
}
