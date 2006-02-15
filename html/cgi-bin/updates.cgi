#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: updates.cgi,v 1.9.2.22 2005/12/01 20:41:53 franck78 Exp $
#

use LWP::UserAgent;
use File::Copy;
use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require 'CONFIG_ROOT/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

#workaround to suppress a warning when a variable is used only once
my @dummy = ( $General::version );
undef (@dummy);
my $warnmessage='';
my $errormessage='';
my @av=('');
my @pf=('');

&Header::showhttpheaders();

my %uploadsettings=();
$uploadsettings{'ACTION'} = '';

&Header::getcgihash(\%uploadsettings, {'wantfile' => 1, 'filevar' => 'FH'});

if ($uploadsettings{'ACTION'} eq $Lang::tr{'upload'}) {
# This code do not serve a lot because $General::version cannot change while the module is loaded. So no change
# can appear. More, this call should be called 'after' update is done !
#	my $return = &downloadlist();
#	if ($return && $return->is_success) {
#		if (open(LIST, ">${General::swroot}/patches/available")){
#			flock LIST, 2;
#			my @this = split(/----START LIST----\n/,$return->content);
#			print LIST $this[1];
#			close(LIST);
#		} else {
#			$errormessage = $Lang::tr{'could not open available updates file'};
#		}
#	} else {
#		if (open(LIST, "<${General::swroot}/patches/available")) {
#			my @list = <LIST>;
#			close(LIST);
#		}
#		$warnmessage = $Lang::tr{'could not download the available updates list'};
#	}


	if (copy ($uploadsettings{'FH'}, "/var/patches/patch-$$.tar.gz.gpg") != 1) {
		$errormessage = $!;
	} else {
		my $exitcode = system("/usr/local/bin/installpackage $$ > /dev/null") >> 8;
		if ($exitcode == 0) {
			#Hack to get correct version displayed after update
			open (XX,"perl -e \"require'${General::swroot}/general-functions.pl';print \\\$General::version\"|");
			$General::version=<XX>;
			close (XX);
			&General::log("$Lang::tr{'the following update was successfully installed'} ($General::version)");
		}
		elsif($exitcode == 2) {
			$errormessage = "$Lang::tr{'could not create directory'}";
		}
		elsif($exitcode == 3) {
			$errormessage = "$Lang::tr{'this is not an authorised update'}";
		}
		elsif($exitcode == 4) {
			$errormessage = "$Lang::tr{'this is not a valid archive'}";
		}
		elsif($exitcode == 5) {
			$errormessage = "$Lang::tr{'could not open update information file'}";
		}
		elsif($exitcode == 6) {
			$errormessage = "$Lang::tr{'could not open installed updates file'}";
		}
		elsif($exitcode == 7) {
			$errormessage = "$Lang::tr{'this update is already installed'}";
		}
		elsif($exitcode == 11) {
			$errormessage = "$Lang::tr{'not enough disk space'}";
		} else {
			$errormessage = "$Lang::tr{'package failed to install'}";
		}
	}
}
elsif ($uploadsettings{'ACTION'} eq $Lang::tr{'refresh update list'}) {
	my $return = &downloadlist();
	if ($return && $return->is_success) {
		if (open(LIST, ">${General::swroot}/patches/available")) {
			flock LIST, 2;
			my @this = split(/----START LIST----\n/,$return->content);
			print LIST $this[1];
			close(LIST);
			&General::log($Lang::tr{'successfully refreshed updates list'});
		} else {
			$errormessage = $Lang::tr{'could not open available updates file'};
		}
	} else {
		$errormessage = $Lang::tr{'could not download the available updates list'}; 
	}
}
elsif ($uploadsettings{'ACTION'} eq "$Lang::tr{'clear cache'} (squid)") {
        system('/usr/local/bin/restartsquid','-f');
}
		
if (!open(AV, "<${General::swroot}/patches/available")) {
    $errormessage = $Lang::tr{'could not open available updates file'};
} else {
    @av = <AV>;
    close(AV);
}
if (!open (PF, "<${General::swroot}/patches/installed")) {
    $errormessage = $Lang::tr{'could not open installed updates file'};
} else {
    @pf = <PF>;
    close (PF);
    #substract installed patch from list displayed (AV list may not be updated)
    foreach my $P (@pf) {
	$P =~ /^(...)/;
	my $order=$1;
	my $idx=0;
	foreach my $A (@av) {
	    $A =~ /^(...)/;
	    if ($1 eq $order) { # match
		splice (@av,$idx,1);
		last;
	    }
	    $idx++;
	}	
    }
}

&Header::openpage($Lang::tr{'updates'}, 1, '');

&Header::openbigbox('100%', 'left', 'download.png', $errormessage);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print $errormessage;
	print "&nbsp;";
	&Header::closebox();
}

if ($warnmessage) {
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'warning messages'}:");
	print "<CLASS NAME='base'>$warnmessage \n";
	print "&nbsp;</CLASS>\n";
	&Header::closebox();
}


&Header::openbox('100%', 'left', $Lang::tr{'available updates'});

if ( defined $av[0] ) {
	print $Lang::tr{'there are updates available'};
	print qq|<table width='100%' border='0' cellpadding='2' cellspacing='0'>
<tr>
<td width='5%'><b>$Lang::tr{'id'}</b></td>
<td width='15%'><b>$Lang::tr{'title'}</b></td>
<td width='50%'><b>$Lang::tr{'description'}</b></td>
<td width='15%'><b>$Lang::tr{'released'}</b></td>
<td width='15%'>&nbsp;</td>
</tr>
|;
	foreach (@av) {
		my @temp = split(/\|/,$_);
		print "<tr><td valign='top'>$temp[0]</td><td valign='top'>$temp[1]</td><td valign='top'>$temp[2]</td><td valign='top'>$temp[3]</td><td valign='top'><a href='$temp[4]' target='_new'>$Lang::tr{'info'}</a></td></tr>";
	}
	print "</table>";


} else {
	print $Lang::tr{'all updates installed'};
}

print qq|<hr /><br>
$Lang::tr{'to install an update'}
<br />
<form method='post' action='/cgi-bin/updates.cgi' enctype='multipart/form-data'>
<table>
<tr>
<td align='right' class='base'>
<b>$Lang::tr{'upload update file'}</b></td>
<td><input type="file" size='40' name="FH" /> <input type='submit' name='ACTION' value='$Lang::tr{'upload'}' />
</td></tr>
</table>|;

print "<b>$Lang::tr{'disk usage'}</b>";
open (XX,'df -h / /var/log|');
my @df=<XX>;
close (XX);
print "<table cellpadding='2'>";
map ( $_ =~ s/ +/<td>/g,@df);	# tablify each line!
print "<tr><td>$df[0]</tr>";
print "<tr><td>$df[1]</tr>";
print "<tr><td>$df[2]<td><input type='submit' name='ACTION' value='$Lang::tr{'clear cache'} (squid)' /></tr>";
print "</table>";

print "\n<hr />";
print "\n<table width='100%'>\n<tr>";
print "\n\t<td width='50%'>&nbsp;</td>";
print "\n\t<td width='50%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'refresh update list'}' /></td></tr>";
print "\n</table>\n";
print "</form>";

&Header::closebox();

&Header::openbox('100%', 'LEFT', $Lang::tr{'installed updates'});

print qq|<table width='100%' border='0' cellpadding='2' cellspacing='0'>
<tr>
<td width='5%'><b>$Lang::tr{'id'}</b></td>
<td width='15%'><b>$Lang::tr{'title'}</b></td>
<td width='50%'><b>$Lang::tr{'description'}</b></td>
<td width='15%'><b>$Lang::tr{'released'}</b></td>
<td width='15%'><b>$Lang::tr{'installed'}</b></td>
</tr>
|;

foreach my $pf (@pf) {
	next if $pf =~ m/^#/;
	my @temp = split(/\|/,$pf);
#???	@av = grep(!/^$temp[0]/, @av);
	print "<tr><td valign='top'>" . join("</td><td valign='top'>",@temp) . "</td></tr>";
}
close(PF);

print "</table>";

&Header::closebox();

&Header::closebigbox();

&Header::closepage();

sub downloadlist {
	unless (-e "${General::swroot}/red/active") {
		return 0;
	}

	my $downloader = LWP::UserAgent->new;
	$downloader->timeout(5);

	my %proxysettings=();
	&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);

	if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
		my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
		if ($proxysettings{'UPSTREAM_USER'}) {
			$downloader->proxy("http","http://$proxysettings{'UPSTREAM_USER'}:$proxysettings{'UPSTREAM_PASSWORD'}@"."$peer:$peerport/");
		} else {
			$downloader->proxy("http","http://$peer:$peerport/");
		}
	}

	return $downloader->get("http://www.ipcop.org/patches/${General::version}", 'Cache-Control', 'no-cache');

}
