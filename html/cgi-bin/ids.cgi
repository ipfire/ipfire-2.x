#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: ids.cgi,v 1.8.2.18 2005/07/27 21:35:22 franck78 Exp $
#

use LWP::UserAgent;
use File::Copy;
use File::Temp qw/ tempfile tempdir /;
use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require 'CONFIG_ROOT/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %snortsettings=();
my %checked=();
my %netsettings=();
our $errormessage = '';
our $md5 = '0';# not '' to avoid displaying the wrong message when INSTALLMD5 not set
our $realmd5 = '';
our $results = '';
our $tempdir = '';
our $url='';
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

&Header::showhttpheaders();

$snortsettings{'ENABLE_SNORT'} = 'off';
$snortsettings{'ENABLE_SNORT_GREEN'} = 'off';
$snortsettings{'ENABLE_SNORT_BLUE'} = 'off';
$snortsettings{'ENABLE_SNORT_ORANGE'} = 'off';
$snortsettings{'ACTION'} = '';
$snortsettings{'RULESTYPE'} = '';
$snortsettings{'OINKCODE'} = '';
$snortsettings{'INSTALLDATE'} = '';
$snortsettings{'INSTALLMD5'} = '';

&Header::getcgihash(\%snortsettings, {'wantfile' => 1, 'filevar' => 'FH'});

if ($snortsettings{'RULESTYPE'} eq 'subscripted') {
	$url="http://www.snort.org/pub-bin/oinkmaster.cgi/$snortsettings{'OINKCODE'}/snortrules-snapshot-2.3_s.tar.gz";
} else {
	$url="http://www.snort.org/pub-bin/oinkmaster.cgi/$snortsettings{'OINKCODE'}/snortrules-snapshot-2.3.tar.gz";
}

if ($snortsettings{'ACTION'} eq $Lang::tr{'save'})
{
	$errormessage = $Lang::tr{'invalid input for oink code'} unless (
	    ($snortsettings{'OINKCODE'} =~ /^[a-z0-9]+$/)  ||
	    ($snortsettings{'RULESTYPE'} eq 'nothing' )       );

	&General::writehash("${General::swroot}/snort/settings", \%snortsettings);
	if ($snortsettings{'ENABLE_SNORT'} eq 'on')
	{
		system ('/bin/touch', "${General::swroot}/snort/enable");
	} else {
		unlink "${General::swroot}/snort/enable";
	} 
	if ($snortsettings{'ENABLE_SNORT_GREEN'} eq 'on')
	{
		system ('/bin/touch', "${General::swroot}/snort/enable_green");
	} else {
		unlink "${General::swroot}/snort/enable_green";
	} 
	if ($snortsettings{'ENABLE_SNORT_BLUE'} eq 'on')
	{
		system ('/bin/touch', "${General::swroot}/snort/enable_blue");
	} else {
		unlink "${General::swroot}/snort/enable_blue";
	} 
	if ($snortsettings{'ENABLE_SNORT_ORANGE'} eq 'on')
	{
		system ('/bin/touch', "${General::swroot}/snort/enable_orange");
	} else {
		unlink "${General::swroot}/snort/enable_orange";
	}

	system('/usr/local/bin/restartsnort','red','orange','blue','green');
} else {
	 # INSTALLMD5 is not in the form, so not retrieved by getcgihash
	&General::readhash("${General::swroot}/snort/settings", \%snortsettings);
}

if ($snortsettings{'ACTION'} eq $Lang::tr{'download new ruleset'}) {
	$md5 = &getmd5;
	if (($snortsettings{'INSTALLMD5'} ne $md5) && defined $md5 ) {
		chomp($md5);
		my $filename = &downloadrulesfile();
		if (defined $filename) {
			# Check MD5sum
			$realmd5 = `/usr/bin/md5sum $filename`;
			chomp ($realmd5);
			$realmd5 =~ s/^(\w+)\s.*$/$1/;
			if ($md5 ne $realmd5) {
				$errormessage = "$Lang::tr{'invalid md5sum'}";
			} else {
				$results = "<b>$Lang::tr{'installed updates'}</b>\n<pre>";
				$results .=`/usr/local/bin/oinkmaster.pl -s -u file://$filename -C /var/ipcop/snort/oinkmaster.conf -o /etc/snort 2>&1`;
				$results .= "</pre>";
			}
			unlink ($filename);
		}
	}
}

$checked{'ENABLE_SNORT'}{'off'} = '';
$checked{'ENABLE_SNORT'}{'on'} = '';
$checked{'ENABLE_SNORT'}{$snortsettings{'ENABLE_SNORT'}} = "checked='checked'";
$checked{'ENABLE_SNORT_GREEN'}{'off'} = '';
$checked{'ENABLE_SNORT_GREEN'}{'on'} = '';
$checked{'ENABLE_SNORT_GREEN'}{$snortsettings{'ENABLE_SNORT_GREEN'}} = "checked='checked'";
$checked{'ENABLE_SNORT_BLUE'}{'off'} = '';
$checked{'ENABLE_SNORT_BLUE'}{'on'} = '';
$checked{'ENABLE_SNORT_BLUE'}{$snortsettings{'ENABLE_SNORT_BLUE'}} = "checked='checked'";
$checked{'ENABLE_SNORT_ORANGE'}{'off'} = '';
$checked{'ENABLE_SNORT_ORANGE'}{'on'} = '';
$checked{'ENABLE_SNORT_ORANGE'}{$snortsettings{'ENABLE_SNORT_ORANGE'}} = "checked='checked'";
$checked{'RULESTYPE'}{'nothing'} = '';
$checked{'RULESTYPE'}{'registered'} = '';
$checked{'RULESTYPE'}{'subscripted'} = '';
$checked{'RULESTYPE'}{$snortsettings{'RULESTYPE'}} = "checked='checked'";

&Header::openpage($Lang::tr{'intrusion detection system'}, 1, '');

&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
}

&Header::openbox('100%', 'left', $Lang::tr{'intrusion detection system2'});
print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'><table width='100%'>
<tr>
	<td class='base'><input type='checkbox' name='ENABLE_SNORT_GREEN' $checked{'ENABLE_SNORT_GREEN'}{'on'} />
		GREEN Snort</td>
</tr>
END
;
if ($netsettings{'BLUE_DEV'} ne '') {
print <<END
<tr>
	<td class='base'><input type='checkbox' name='ENABLE_SNORT_BLUE' $checked{'ENABLE_SNORT_BLUE'}{'on'} />
		BLUE Snort</td>
</tr>
END
;
}
if ($netsettings{'ORANGE_DEV'} ne '') {
print <<END
<tr>
	<td class='base'><input type='checkbox' name='ENABLE_SNORT_ORANGE' $checked{'ENABLE_SNORT_ORANGE'}{'on'} />
		ORANGE Snort</td>
</tr>
END
;
}
print <<END
<tr>
	<td class='base'><input type='checkbox' name='ENABLE_SNORT' $checked{'ENABLE_SNORT'}{'on'} />
		RED Snort</td>
</tr>
<tr>
	<td><hr /></td>
</tr>
<tr>
	<td><b>$Lang::tr{'ids rules update'}</b></td>
</tr>
<tr>
	<td><input type='radio' name='RULESTYPE' value='nothing' $checked{'RULESTYPE'}{'nothing'} />
		$Lang::tr{'no'}</td>
</tr>
<tr>
	<td><input type='radio' name='RULESTYPE' value='registered' $checked{'RULESTYPE'}{'registered'} />
		$Lang::tr{'registered user rules'}</td>
</tr>
<tr>
	<td><input type='radio' name='RULESTYPE' value='subscripted' $checked{'RULESTYPE'}{'subscripted'} />
		$Lang::tr{'subscripted user rules'}</td>
</tr>
<tr>
	<td><br />
		$Lang::tr{'ids rules license'} <a href='http://www.snort.org/' target='_blank'>http://www.snort.org</a>.<br />
		<br />
		$Lang::tr{'ids rules license2'} <a href='http://www.snort.org/reg-bin/userprefs.cgi' target='_blank'>USER PREFERENCES</a>, $Lang::tr{'ids rules license3'}<br />
	</td>
</tr>
<tr>
	<td nowrap='nowrap'>Oink Code:&nbsp;<input type='text' size='40' name='OINKCODE' value='$snortsettings{'OINKCODE'}' /></td>
</tr>
<tr>
	<td width='30%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'download new ruleset'}' />
END
;

if ($snortsettings{'INSTALLMD5'} eq $md5) {
	print "&nbsp;$Lang::tr{'rules already up to date'}</td>";
} else {
	if ( $snortsettings{'ACTION'} eq $Lang::tr{'download new ruleset'} && $md5 eq $realmd5 ) {
		$snortsettings{'INSTALLMD5'} = $realmd5;
		$snortsettings{'INSTALLDATE'} = `/bin/date +'%Y-%m-%d'`;
		&General::writehash("${General::swroot}/snort/settings", \%snortsettings);
	}
	print "&nbsp;$Lang::tr{'updates installed'}: $snortsettings{'INSTALLDATE'}</td>";
}
print <<END
</tr>
</table>
<hr />
<table width='100%'>
<tr>
	<td width='55%'>&nbsp;</td>
	<td width='40%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
	<td width='5%'>
		&nbsp; <!-- space for future online help link -->
	</td>
</tr>
</table>
</form>
END
;

if ($results ne '') {
	print "$results";
}

&Header::closebox();
&Header::closebigbox();
&Header::closepage();

sub getmd5 {
	# Retrieve MD5 sum from $url.md5 file
	#
	my $md5buf = &geturl("$url.md5");
	return undef unless $md5buf;

	if (0) { # 1 to debug
		my $filename='';
		my $fh='';
		($fh, $filename) = tempfile('/tmp/XXXXXXXX',SUFFIX => '.md5' );
		binmode ($fh);
		syswrite ($fh, $md5buf->content);
		close($fh);
	}
	return $md5buf->content;
}
sub downloadrulesfile {
	my $return = &geturl($url);
	return undef unless $return;

	if (index($return->content, "\037\213") == -1 ) { # \037\213 is .gz beginning
		$errormessage = $Lang::tr{'invalid loaded file'};
		return undef;
	}

	my $filename='';
	my $fh='';
	($fh, $filename) = tempfile('/tmp/XXXXXXXX',SUFFIX => '.tar.gz' );#oinkmaster work only with this extension
	binmode ($fh);
	syswrite ($fh, $return->content);
	close($fh);
	return $filename;
}

sub geturl ($) {
	my $url=$_[0];

	unless (-e "${General::swroot}/red/active") {
		$errormessage = $Lang::tr{'could not download latest updates'};
		return undef;
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

	my $return = $downloader->get($url,'Cache-Control','no-cache');

	if ($return->code == 403) {
		$errormessage = $Lang::tr{'access refused with this oinkcode'};
		return undef;
	} elsif (!$return->is_success()) {
		$errormessage = $Lang::tr{'could not download latest updates'};
		return undef;
	}

	return $return;

}
