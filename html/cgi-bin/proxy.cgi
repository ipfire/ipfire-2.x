#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: proxy.cgi,v 1.13.2.23 2006/01/29 09:29:47 eoberlander Exp $
#

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require 'CONFIG_ROOT/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %proxysettings=();
my %netsettings=();
my %mainsettings=();
my $errormessage = '';
my $NeedDoHTML = 1;

&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/main/settings", \%mainsettings);

&Header::showhttpheaders();

$proxysettings{'ACTION'} = '';
$proxysettings{'VALID'} = '';

$proxysettings{'UPSTREAM_PROXY'} = '';
$proxysettings{'UPSTREAM_USER'} = '';
$proxysettings{'UPSTREAM_PASSWORD'} = '';
$proxysettings{'ENABLE'} = 'off';
$proxysettings{'ENABLE_BLUE'} = 'off';
$proxysettings{'CACHE_SIZE'} = '50';
$proxysettings{'TRANSPARENT'} = 'off';
$proxysettings{'TRANSPARENT_BLUE'} = 'off';
$proxysettings{'MAX_SIZE'} = '4096';
$proxysettings{'MIN_SIZE'} = '0';
$proxysettings{'MAX_OUTGOING_SIZE'} = '0';
$proxysettings{'MAX_INCOMING_SIZE'} = '0';
$proxysettings{'LOGGING'} = 'off';
$proxysettings{'PROXY_PORT'} = '800';
$proxysettings{'EXTENSION_METHODS'} = '';

&Header::getcgihash(\%proxysettings);

my $needhup = 0;
my $cachemem = '';

if ($proxysettings{'ACTION'} eq $Lang::tr{'save'})
{
	
	#assume error
	my $configerror = 1;

	if ($proxysettings{'ENABLE'} !~ /^(on|off)$/ || 
	    $proxysettings{'TRANSPARENT'} !~ /^(on|off)$/ || 
	    $proxysettings{'ENABLE_BLUE'} !~ /^(on|off)$/ || 
	    $proxysettings{'TRANSPARENT_BLUE'} !~ /^(on|off)$/ ) {
		$errormessage = $Lang::tr{'invalid input'};
		goto ERROR;
	} 
	if (!($proxysettings{'CACHE_SIZE'} =~ /^\d+/) ||
		($proxysettings{'CACHE_SIZE'} < 10))
	{
		$errormessage = $Lang::tr{'invalid cache size'};
		goto ERROR;
	}		
	if (!($proxysettings{'MAX_SIZE'} =~ /^\d+/))
	{
		$errormessage = $Lang::tr{'invalid maximum object size'};
		goto ERROR;
	}
	if (!($proxysettings{'MIN_SIZE'} =~ /^\d+/))
	{
		$errormessage = $Lang::tr{'invalid minimum object size'};
		goto ERROR;
	}
	if (!($proxysettings{'MAX_OUTGOING_SIZE'} =~ /^\d+/))
	{
		$errormessage = $Lang::tr{'invalid maximum outgoing size'};
		goto ERROR;
	}
	if (!($proxysettings{'MAX_INCOMING_SIZE'} =~ /^\d+/))
	{
		$errormessage = $Lang::tr{'invalid maximum incoming size'};
		goto ERROR;
	}

	if (!($proxysettings{'EXTENSION_METHODS'} =~ /^(|[A-Z0-9 _-]+)$/))
	{
		$errormessage = $Lang::tr{'squid extension methods invalid'};
		goto ERROR;
	}

        # Quick parent proxy error checking of username and password info. If username password don't both exist give an error.
        my $proxy1 = 'YES';
        my $proxy2 = 'YES';
        if (($proxysettings{'UPSTREAM_USER'} eq '')) {$proxy1 = '';}
        if (($proxysettings{'UPSTREAM_PASSWORD'} eq '')) {$proxy2 = '';}
        if (($proxy1 ne $proxy2))
        {
                $errormessage = $Lang::tr{'invalid upstream proxy username or password setting'};
                goto ERROR;
        }

	$_ = $proxysettings{'UPSTREAM_PROXY'};
	my ($remotehost, $remoteport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
	$remoteport = 80 if ($remoteport eq '');

      	$proxysettings{'VALID'} = 'yes';
	&General::writehash("${General::swroot}/proxy/settings", \%proxysettings);

	#
	# NAH, 03-Jan-2004
	#
	my @free = `/usr/bin/free`;
	$free[1] =~ m/(\d+)/;
	$cachemem = int $1 / 10;
	if ($cachemem < 4096) {
		$cachemem = 4096;
	}
	if ($cachemem > $proxysettings{'CACHE_SIZE'} * 40) {
		$cachemem = ( $proxysettings{'CACHE_SIZE'} * 40 );
	}

	open(FILE, ">/${General::swroot}/proxy/squid.conf") or die "Unable to write squid.conf file";
	flock(FILE, 2);
	print FILE <<END
shutdown_lifetime 5 seconds
icp_port 0

http_port $netsettings{'GREEN_ADDRESS'}:$proxysettings{'PROXY_PORT'}
END
	;
	print FILE "\nextension_methods $proxysettings{'EXTENSION_METHODS'}\n" if ($proxysettings{'EXTENSION_METHODS'} ne '');

	if ($netsettings{'BLUE_DEV'} && $proxysettings{'ENABLE_BLUE'} eq 'on') {
		print FILE "http_port $netsettings{'BLUE_ADDRESS'}:$proxysettings{'PROXY_PORT'}\n";
	}
	print FILE <<END

acl QUERY urlpath_regex cgi-bin \\?
no_cache deny QUERY

cache_effective_user squid
cache_effective_group squid

pid_filename /var/run/squid.pid

END
	;

	if ($proxysettings{'LOGGING'} eq 'on')
	{
                print FILE <<END
cache_access_log /var/log/squid/access.log
cache_log /var/log/squid/cache.log
cache_store_log none

END
	;} else {
		print FILE <<END
cache_access_log /dev/null
cache_log /dev/null
cache_store_log none

END
	;}
	print FILE <<END
log_mime_hdrs off
forwarded_for off

END
	;

        #Insert acl file and replace __VAR__ with correct values
        my $blue_net = ''; #BLUE empty by default
	my $blue_ip = '';
	if ($netsettings{'BLUE_DEV'} && $proxysettings{'ENABLE_BLUE'} eq 'on') {
	    $blue_net = "$netsettings{'BLUE_NETADDRESS'}/$netsettings{'BLUE_NETMASK'}";
	    $blue_ip  = "$netsettings{'BLUE_ADDRESS'}";
	}
	open (ACL, "${General::swroot}/proxy/acl") or die "Unable to open ACL list file";
	while (<ACL>) {
		$_ =~ s/__GREEN_IP__/$netsettings{'GREEN_ADDRESS'}/;
		$_ =~ s/__GREEN_NET__/$netsettings{'GREEN_NETADDRESS'}\/$netsettings{'GREEN_NETMASK'}/;
		$_ =~ s/__BLUE_IP__/$blue_ip/;
		$_ =~ s/__BLUE_NET__/$blue_net/;
		$_ =~ s/__PROXY_PORT__/$proxysettings{'PROXY_PORT'}/;
		print FILE $_;
	}
	close (ACL);

	# This value is in bytes, so we must turn it from KB into bytes
	my $max_incoming_size = $proxysettings{'MAX_INCOMING_SIZE'} * 1024;

	print FILE <<END

maximum_object_size $proxysettings{'MAX_SIZE'} KB
minimum_object_size $proxysettings{'MIN_SIZE'} KB

cache_mem $cachemem KB
cache_dir aufs /var/log/cache $proxysettings{'CACHE_SIZE'} 16 256

request_body_max_size $proxysettings{'MAX_OUTGOING_SIZE'} KB
reply_body_max_size $max_incoming_size allow all

visible_hostname $mainsettings{'HOSTNAME'}.$mainsettings{'DOMAINNAME'}

END
	;

	# Write the parent proxy info, if needed.
	if ($remotehost ne '')
	{
		# Enter authentication for the parent cache (format is login=user:password)
		if ($proxy1 eq 'YES') {
		print FILE <<END
cache_peer $remotehost parent $remoteport 3130 login=$proxysettings{'UPSTREAM_USER'}:$proxysettings{'UPSTREAM_PASSWORD'} default no-query

END
		; 
		} else {
		# Not using authentication with the parent cache
		print FILE <<END
cache_peer $remotehost parent $remoteport 3130 default no-query

END
		;
		}
		print FILE "never_direct allow all\n";
	}
	if (($proxysettings{'TRANSPARENT'} eq 'on') ||
	    ($proxysettings{'TRANSPARENT_BLUE'} eq 'on'))
	{
		print FILE <<END
httpd_accel_host virtual 
httpd_accel_port 80 
httpd_accel_with_proxy on
httpd_accel_uses_host_header on 
END
		;
	}
	close FILE;
	$configerror = 0;  ## a good config!

ERROR:
	unlink "${General::swroot}/proxy/enable";
	unlink "${General::swroot}/proxy/transparent";
	unlink "${General::swroot}/proxy/enable_blue";
	unlink "${General::swroot}/proxy/transparent_blue";
	&DoHTML;

	if (!$configerror)
	{
		if ($proxysettings{'ENABLE'} eq 'on') {
			system ('/bin/touch', "${General::swroot}/proxy/enable"); }
		if ($proxysettings{'TRANSPARENT'} eq 'on') {
			system ('/bin/touch', "${General::swroot}/proxy/transparent"); }
		if ($proxysettings{'ENABLE_BLUE'} eq 'on') {
			system ('/bin/touch', "${General::swroot}/proxy/enable_blue"); }
		if ($proxysettings{'TRANSPARENT_BLUE'} eq 'on') {
			system ('/bin/touch', "${General::swroot}/proxy/transparent_blue"); }
		system('/usr/local/bin/restartsquid');
	}
}

if ($proxysettings{'ACTION'} eq $Lang::tr{'clear cache'})
{
	&DoHTML;
	system('/usr/local/bin/restartsquid','-f');
}

&DoHTML if $NeedDoHTML;


sub DoHTML	{

$NeedDoHTML = 0;
&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);

my %checked=();

$checked{'ENABLE'}{'off'} = '';
$checked{'ENABLE'}{'on'} = '';
$checked{'ENABLE'}{$proxysettings{'ENABLE'}} = "checked='checked'";

$checked{'TRANSPARENT'}{'off'} = '';
$checked{'TRANSPARENT'}{'on'} = '';
$checked{'TRANSPARENT'}{$proxysettings{'TRANSPARENT'}} = "checked='checked'";

$checked{'ENABLE_BLUE'}{'off'} = '';
$checked{'ENABLE_BLUE'}{'on'} = '';
$checked{'ENABLE_BLUE'}{$proxysettings{'ENABLE_BLUE'}} = "checked='checked'";

$checked{'TRANSPARENT_BLUE'}{'off'} = '';
$checked{'TRANSPARENT_BLUE'}{'on'} = '';
$checked{'TRANSPARENT_BLUE'}{$proxysettings{'TRANSPARENT_BLUE'}} = "checked='checked'";

$checked{'LOGGING'}{'off'} = '';
$checked{'LOGGING'}{'on'} = '';
$checked{'LOGGING'}{$proxysettings{'LOGGING'}} = "checked='checked'";

&Header::openpage($Lang::tr{'web proxy configuration'}, 1, '');

&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<font class='base'>$errormessage&nbsp;</font>\n";
	&Header::closebox();
}

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

&Header::openbox('100%', 'left', "$Lang::tr{'web proxy'}:");
print <<END
<table width='100%'>
<tr>
	<td width='25%' class='base'>$Lang::tr{'enabled on'} <font color="${Header::colourgreen}">Green</font>:</td>
	<td width='15%'><input type='checkbox' name='ENABLE' $checked{'ENABLE'}{'on'} /></td>
	<td width='30%' class='base'>$Lang::tr{'upstream proxy host:port'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td width='30%'><input type='text' name='UPSTREAM_PROXY' value='$proxysettings{'UPSTREAM_PROXY'}' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'transparent on'} <font color="${Header::colourgreen}">Green</font>:</td>
	<td><input type='checkbox' name='TRANSPARENT' $checked{'TRANSPARENT'}{'on'} /></td>
	<td class='base'>$Lang::tr{'upstream username'}&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td><input type='text' name='UPSTREAM_USER' value='$proxysettings{'UPSTREAM_USER'}' /></td>
</tr>
<tr>
END
;
if ($netsettings{'BLUE_DEV'}) {
	print "<td class='base'>$Lang::tr{'enabled on'} <font color='${Header::colourblue}'>Blue</font>:</td>";
	print "<td><input type='checkbox' name='ENABLE_BLUE' $checked{'ENABLE_BLUE'}{'on'} /></td>";
} else {
	print "<td colspan='2'>&nbsp;</td>";
}
print <<END
	<td class='base'>$Lang::tr{'upstream password'}&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td><input type='password' name='UPSTREAM_PASSWORD' value='$proxysettings{'UPSTREAM_PASSWORD'}' /></td>
</tr>
<tr>
END
;
if ($netsettings{'BLUE_DEV'}) {
	print "<td class='base'>$Lang::tr{'transparent on'} <font color='${Header::colourblue}'>Blue</font>:</td>";
	print "<td><input type='checkbox' name='TRANSPARENT_BLUE' $checked{'TRANSPARENT_BLUE'}{'on'} /></td>";
} else {
	print "<td colspan='2'>&nbsp;</td>";
}
print <<END
	<td class='base'>$Lang::tr{'proxy port'}:</td>
	<td><input type='text' name='PROXY_PORT' value='$proxysettings{'PROXY_PORT'}' size='5' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'log enabled'}:</td>
	<td><input type='checkbox' name='LOGGING' $checked{'LOGGING'}{'on'} /></td>
	<td>$Lang::tr{'squid extension methods'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td><input type='text' name='EXTENSION_METHODS' value='$proxysettings{'EXTENSION_METHODS'}' /></td>
</tr>
<!--TAG FOR ADDONS-->
<tr>
	<td colspan='4'><hr /><b>$Lang::tr{'cache management'}</b></td>
</tr>
<tr>
	<td width='25%' class='base'>$Lang::tr{'cache size'}</td>
	<td><input type='text' name='CACHE_SIZE' value='$proxysettings{'CACHE_SIZE'}' size='5' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'min size'}</td>
	<td><input type='text' name='MIN_SIZE' value='$proxysettings{'MIN_SIZE'}' size='5' /></td>
	<td class='base'>$Lang::tr{'max size'}</td>
	<td><input type='text' name='MAX_SIZE' value='$proxysettings{'MAX_SIZE'}' size='5' /></td>
</tr>
<tr>
	<td colspan='4'><hr /><b>$Lang::tr{'transfer limits'}</b></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'max incoming size'}</td>
	<td><input type='text' name='MAX_INCOMING_SIZE' value='$proxysettings{'MAX_INCOMING_SIZE'}' size='5' /></td>
	<td class='base'>$Lang::tr{'max outgoing size'}</td>
	<td><input type='text' name='MAX_OUTGOING_SIZE' value='$proxysettings{'MAX_OUTGOING_SIZE'}' size='5' /></td>
</tr>
</table>
<table width='100%'>
<hr />
<tr>
	<td width='28%'>
		<img src='/blob.gif' align='top' alt='*' />&nbsp;
		<font class='base'>$Lang::tr{'this field may be blank'}</font>
	</td>
	<td width='33%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'clear cache'}' /></td>
	<td width=33%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
	<td width='5%' align='right'>
		<a href='${General::adminmanualurl}/services.html#services_webproxy' target='_blank'>
		<img src='/images/web-support.png' title='$Lang::tr{'online help en'}' /></a></td>
</tr>

</table>
END
;
&Header::closebox();

print "</form>\n";

&Header::closebigbox();

&Header::closepage();

} # end sub DoHTML
1
