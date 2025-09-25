#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2025  IPFire Team  <info@ipfire.org>                     #
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
use Scalar::Util qw(looks_like_number);

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

require "${General::swroot}/ids-functions.pl";

my @squidversion = &General::system_output("/usr/sbin/squid", "-v");
my $http_port='81';
my $https_port='444';

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/ipfire/include/colors.txt", \%color);

my %proxysettings=();
my %netsettings=();
my %filtersettings=();
my %xlratorsettings=();
my %stdproxysettings=();
my %mainsettings=();

my %checked=();
my %selected=();

my @throttle_limits=(64,128,256,512,1024,1536,2048,3072,4096,5120,6144,7168,8192,10240,16384,20480,51200,102400);

my $def_ports_safe="80 # http\n21 # ftp\n443 # https\n563 # snews\n70 # gopher\n210 # wais\n1025-65535 # unregistered ports\n280 # http-mgmt\n488 # gss-http\n591 # filemaker\n777 # multiling http\n800 # Squids port (for icons)\n";
my $def_ports_ssl="443 # https\n563 # snews\n";

my $hintcolour='#FFFFCC';
my $ncsa_buttontext='';
my $language='';
my $i=0;
my $n=0;
my $id=0;
my $line='';
my $user='';
my @userlist=();
my @grouplist=();
my @temp=();
my @templist=();

my $cachemem=0;
my $proxy1='';
my $proxy2='';
my $browser_regexp='';
my $needhup = 0;
my $errormessage='';

my $acldir   = "${General::swroot}/proxy/advanced/acls";
my $ncsadir  = "${General::swroot}/proxy/advanced/ncsa";
my $raddir   = "${General::swroot}/proxy/advanced/radius";
my $identdir = "${General::swroot}/proxy/advanced/ident";
my $credir   = "${General::swroot}/proxy/advanced/cre";

my $userdb = "$ncsadir/passwd";
my $stdgrp = "$ncsadir/standard.grp";
my $extgrp = "$ncsadir/extended.grp";
my $disgrp = "$ncsadir/disabled.grp";

my $mimetypes = "${General::swroot}/proxy/advanced/mimetypes";
my $throttled_urls = "${General::swroot}/proxy/advanced/throttle";

my $cre_enabled = "${General::swroot}/proxy/advanced/cre/enable";
my $cre_groups  = "${General::swroot}/proxy/advanced/cre/classrooms";
my $cre_svhosts = "${General::swroot}/proxy/advanced/cre/supervisors";

my $identhosts = "$identdir/hosts";

my $authdir  = "/usr/lib/squid";
my $errordir = "/usr/lib/squid/errors";

my $acl_src_subnets = "$acldir/src_subnets.acl";
my $acl_src_banned_ip  = "$acldir/src_banned_ip.acl";
my $acl_src_banned_mac = "$acldir/src_banned_mac.acl";
my $acl_src_unrestricted_ip  = "$acldir/src_unrestricted_ip.acl";
my $acl_src_unrestricted_mac = "$acldir/src_unrestricted_mac.acl";
my $acl_src_noaccess_ip  = "$acldir/src_noaccess_ip.acl";
my $acl_src_noaccess_mac = "$acldir/src_noaccess_mac.acl";
my $acl_dst_noauth   = "$acldir/dst_noauth.acl";
my $acl_dst_noauth_dom = "$acldir/dst_noauth_dom.acl";
my $acl_dst_noauth_net = "$acldir/dst_noauth_net.acl";
my $acl_dst_noauth_url = "$acldir/dst_noauth_url.acl";
my $acl_dst_nocache  = "$acldir/dst_nocache.acl";
my $acl_dst_nocache_dom = "$acldir/dst_nocache_dom.acl";
my $acl_dst_nocache_net = "$acldir/dst_nocache_net.acl";
my $acl_dst_nocache_url = "$acldir/dst_nocache_url.acl";
my $acl_dst_throttle = "$acldir/dst_throttle.acl";
my $acl_ports_safe = "$acldir/ports_safe.acl";
my $acl_ports_ssl  = "$acldir/ports_ssl.acl";
my $acl_include = "$acldir/include.acl";

my $acl_dst_noproxy_url = "$acldir/dst_noproxy_url.acl";
my $acl_dst_noproxy_ip = "$acldir/dst_noproxy_ip.acl";

my $updaccelversion  = 'n/a';
my $urlfilterversion = 'n/a';

unless (-d "$acldir")   { mkdir("$acldir"); }
unless (-d "$ncsadir")  { mkdir("$ncsadir"); }
unless (-d "$raddir")   { mkdir("$raddir"); }
unless (-d "$identdir") { mkdir("$identdir"); }
unless (-d "$credir")   { mkdir("$credir"); }

unless (-e $cre_groups)  { &General::system("touch", "$cre_groups"); }
unless (-e $cre_svhosts) { &General::system("touch $cre_svhosts"); }

unless (-e $userdb) { &General::system("touch", "$userdb"); }
unless (-e $stdgrp) { &General::system("touch", "$stdgrp"); }
unless (-e $extgrp) { &General::system("touch", "$extgrp"); }
unless (-e $disgrp) { &General::system("touch", "$disgrp"); }

unless (-e $acl_src_subnets)    { &General::system("touch", "$acl_src_subnets"); }
unless (-e $acl_src_banned_ip)  { &General::system("touch", "$acl_src_banned_ip"); }
unless (-e $acl_src_banned_mac) { &General::system("touch", "$acl_src_banned_mac"); }
unless (-e $acl_src_unrestricted_ip)  { &General::system("touch", "$acl_src_unrestricted_ip"); }
unless (-e $acl_src_unrestricted_mac) { &General::system("touch", "$acl_src_unrestricted_mac"); }
unless (-e $acl_src_noaccess_ip)  { &General::system("touch", "$acl_src_noaccess_ip"); }
unless (-e $acl_src_noaccess_mac) { &General::system("touch", "$acl_src_noaccess_mac"); }
unless (-e $acl_dst_noauth)     { &General::system("touch", "$acl_dst_noauth"); }
unless (-e $acl_dst_noauth_dom) { &General::system("touch", "$acl_dst_noauth_dom"); }
unless (-e $acl_dst_noauth_net) { &General::system("touch", "$acl_dst_noauth_net"); }
unless (-e $acl_dst_noauth_url) { &General::system("touch", "$acl_dst_noauth_url"); }
unless (-e $acl_dst_nocache)     { &General::system("touch", "$acl_dst_nocache"); }
unless (-e $acl_dst_nocache_dom) { &General::system("touch", "$acl_dst_nocache_dom"); }
unless (-e $acl_dst_nocache_net) { &General::system("touch", "$acl_dst_nocache_net"); }
unless (-e $acl_dst_nocache_url) { &General::system("touch", "$acl_dst_nocache_url"); }
unless (-e $acl_dst_throttle)  { &General::system("touch", "$acl_dst_throttle"); }
unless (-e $acl_ports_safe) { &General::system("touch", "$acl_ports_safe"); }
unless (-e $acl_ports_ssl)  { &General::system("touch", "$acl_ports_ssl"); }
unless (-e $acl_include) { &General::system("touch", "$acl_include"); }

unless (-e $mimetypes) { &General::system("touch", "$mimetypes"); }

my $HAVE_NTLM_AUTH = (-e "/usr/bin/ntlm_auth");

&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/main/settings", \%mainsettings);

my $green_cidr = "";
if (&Header::green_used() && $netsettings{'GREEN_DEV'}) {
	$green_cidr = &General::ipcidr("$netsettings{'GREEN_NETADDRESS'}\/$netsettings{'GREEN_NETMASK'}");
}

my $blue_cidr = "";
if (&Header::blue_used() && $netsettings{'BLUE_DEV'}) {
	$blue_cidr = &General::ipcidr("$netsettings{'BLUE_NETADDRESS'}\/$netsettings{'BLUE_NETMASK'}");
}

&Header::showhttpheaders();

$proxysettings{'ACTION'} = '';
$proxysettings{'VALID'} = '';

$proxysettings{'ENABLE'} = 'off';
$proxysettings{'ENABLE_BLUE'} = 'off';
$proxysettings{'TRANSPARENT'} = 'off';
$proxysettings{'TRANSPARENT_BLUE'} = 'off';
$proxysettings{'PROXY_PORT'} = '800';
$proxysettings{'TRANSPARENT_PORT'} = '3128';
$proxysettings{'VISIBLE_HOSTNAME'} = '';
$proxysettings{'ADMIN_MAIL_ADDRESS'} = '';
$proxysettings{'ADMIN_PASSWORD'} = '';
$proxysettings{'ERR_LANGUAGE'} = 'en';
$proxysettings{'ERR_DESIGN'} = 'ipfire';
$proxysettings{'FORWARD_VIA'} = 'off';
$proxysettings{'FORWARD_IPADDRESS'} = 'off';
$proxysettings{'FORWARD_USERNAME'} = 'off';
$proxysettings{'NO_CONNECTION_AUTH'} = 'off';
$proxysettings{'UPSTREAM_PROXY'} = '';
$proxysettings{'UPSTREAM_USER'} = '';
$proxysettings{'UPSTREAM_PASSWORD'} = '';
$proxysettings{'LOGGING'} = 'off';
$proxysettings{'CACHEMGR'} = 'off';
$proxysettings{'LOGQUERY'} = 'off';
$proxysettings{'LOGUSERAGENT'} = 'off';
$proxysettings{'FILEDESCRIPTORS'} = '16384';
$proxysettings{'CACHE_MEM'} = '128';
$proxysettings{'CACHE_SIZE'} = '0';
$proxysettings{'MAX_SIZE'} = '4096';
$proxysettings{'MIN_SIZE'} = '0';
$proxysettings{'MEM_POLICY'} = 'LRU';
$proxysettings{'CACHE_POLICY'} = 'LRU';
$proxysettings{'L1_DIRS'} = '16';
$proxysettings{'OFFLINE_MODE'} = 'off';
$proxysettings{'CACHE_DIGESTS'} = 'off';
$proxysettings{'CLASSROOM_EXT'} = 'off';
$proxysettings{'SUPERVISOR_PASSWORD'} = '';
$proxysettings{'NO_PROXY_LOCAL'} = 'off';
$proxysettings{'NO_PROXY_LOCAL_BLUE'} = 'off';
$proxysettings{'TIME_ACCESS_MODE'} = 'allow';
$proxysettings{'TIME_FROM_HOUR'} = '00';
$proxysettings{'TIME_FROM_MINUTE'} = '00';
$proxysettings{'TIME_TO_HOUR'} = '24';
$proxysettings{'TIME_TO_MINUTE'} = '00';
$proxysettings{'MAX_OUTGOING_SIZE'} = '0';
$proxysettings{'MAX_INCOMING_SIZE'} = '0';
$proxysettings{'THROTTLING_GREEN_TOTAL'} = 'unlimited';
$proxysettings{'THROTTLING_GREEN_HOST'} = 'unlimited';
$proxysettings{'THROTTLING_BLUE_TOTAL'} = 'unlimited';
$proxysettings{'THROTTLING_BLUE_HOST'} = 'unlimited';
$proxysettings{'ASNBL_FASTFLUX_DETECTION'} = 'off';
$proxysettings{'ASNBL_FASTFLUX_THRESHOLD'} = '5';
$proxysettings{'ASNBL_SELECANN_DETECTION'} = 'off';
$proxysettings{'ENABLE_MIME_FILTER'} = 'off';
$proxysettings{'AUTH_METHOD'} = 'none';
$proxysettings{'AUTH_REALM'} = '';
$proxysettings{'AUTH_MAX_USERIP'} = '';
$proxysettings{'AUTH_CACHE_TTL'} = '60';
$proxysettings{'AUTH_IPCACHE_TTL'} = '0';
$proxysettings{'AUTH_CHILDREN'} = '5';
$proxysettings{'NCSA_MIN_PASS_LEN'} = '6';
$proxysettings{'NCSA_BYPASS_REDIR'} = 'off';
$proxysettings{'NCSA_USERNAME'} = '';
$proxysettings{'NCSA_GROUP'} = '';
$proxysettings{'NCSA_PASS'} = '';
$proxysettings{'NCSA_PASS_CONFIRM'} = '';
$proxysettings{'LDAP_BASEDN'} = '';
$proxysettings{'LDAP_TYPE'} = 'ADS';
$proxysettings{'LDAP_SERVER'} = '';
$proxysettings{'LDAP_PORT'} = '389';
$proxysettings{'LDAP_BINDDN_USER'} = '';
$proxysettings{'LDAP_BINDDN_PASS'} = '';
$proxysettings{'LDAP_GROUP'} = '';
$proxysettings{'NTLM_AUTH_GROUP'} = '';
$proxysettings{'NTLM_AUTH_BASIC'} = 'off';
$proxysettings{'NTLM_DOMAIN'} = '';
$proxysettings{'NTLM_PDC'} = '';
$proxysettings{'NTLM_BDC'} = '';
$proxysettings{'NTLM_ENABLE_ACL'} = 'off';
$proxysettings{'NTLM_USER_ACL'} = 'positive';
$proxysettings{'RADIUS_SERVER'} = '';
$proxysettings{'RADIUS_PORT'} = '1812';
$proxysettings{'RADIUS_IDENTIFIER'} = '';
$proxysettings{'RADIUS_SECRET'} = '';
$proxysettings{'RADIUS_ENABLE_ACL'} = 'off';
$proxysettings{'RADIUS_USER_ACL'} = 'positive';
$proxysettings{'IDENT_REQUIRED'} = 'off';
$proxysettings{'IDENT_TIMEOUT'} = '10';
$proxysettings{'IDENT_ENABLE_ACL'} = 'off';
$proxysettings{'IDENT_USER_ACL'} = 'positive';
$proxysettings{'ENABLE_FILTER'} = 'off';
$proxysettings{'ENABLE_UPDXLRATOR'} = 'off';
$proxysettings{'ENABLE_CLAMAV'} = 'off';

$ncsa_buttontext = $Lang::tr{'advproxy NCSA create user'};

&Header::getcgihash(\%proxysettings);

if ($proxysettings{'THROTTLING_GREEN_TOTAL'} eq 0) {$proxysettings{'THROTTLING_GREEN_TOTAL'} = 'unlimited';}
if ($proxysettings{'THROTTLING_GREEN_HOST'}  eq 0) {$proxysettings{'THROTTLING_GREEN_HOST'}  = 'unlimited';}
if ($proxysettings{'THROTTLING_BLUE_TOTAL'}  eq 0) {$proxysettings{'THROTTLING_BLUE_TOTAL'}  = 'unlimited';}
if ($proxysettings{'THROTTLING_BLUE_HOST'}   eq 0) {$proxysettings{'THROTTLING_BLUE_HOST'}   = 'unlimited';}

if ($proxysettings{'ACTION'} eq $Lang::tr{'advproxy NCSA user management'})
{
	$proxysettings{'NCSA_EDIT_MODE'} = 'yes';
}

if ($proxysettings{'ACTION'} eq $Lang::tr{'add'})
{
	$proxysettings{'NCSA_EDIT_MODE'} = 'yes';
	if (length($proxysettings{'NCSA_PASS'}) < $proxysettings{'NCSA_MIN_PASS_LEN'}) {
		$errormessage = $Lang::tr{'advproxy errmsg password length 1'}.$proxysettings{'NCSA_MIN_PASS_LEN'}.$Lang::tr{'advproxy errmsg password length 2'};
	}
	if (!($proxysettings{'NCSA_PASS'} eq $proxysettings{'NCSA_PASS_CONFIRM'})) {
		$errormessage = $Lang::tr{'advproxy errmsg passwords different'};
	}
	if ($proxysettings{'NCSA_USERNAME'} eq '') {
		$errormessage = $Lang::tr{'advproxy errmsg no username'};
	}
	if (!$errormessage) {
		$proxysettings{'NCSA_USERNAME'} =~ tr/A-Z/a-z/;
		&adduser($proxysettings{'NCSA_USERNAME'}, $proxysettings{'NCSA_PASS'}, $proxysettings{'NCSA_GROUP'});
	}
	$proxysettings{'NCSA_USERNAME'} = '';
	$proxysettings{'NCSA_GROUP'} = '';
	$proxysettings{'NCSA_PASS'} = '';
	$proxysettings{'NCSA_PASS_CONFIRM'} = '';
}

if ($proxysettings{'ACTION'} eq $Lang::tr{'remove'})
{
	$proxysettings{'NCSA_EDIT_MODE'} = 'yes';
	&deluser($proxysettings{'ID'});
}

$checked{'ENABLE_UPDXLRATOR'}{'off'} = '';
$checked{'ENABLE_UPDXLRATOR'}{'on'} = '';
$checked{'ENABLE_UPDXLRATOR'}{$proxysettings{'ENABLE_UPDXLRATOR'}} = "checked='checked'";

if ($proxysettings{'ACTION'} eq $Lang::tr{'edit'})
{
	$proxysettings{'NCSA_EDIT_MODE'} = 'yes';
	$ncsa_buttontext = $Lang::tr{'advproxy NCSA update user'};
	@temp = split(/:/,$proxysettings{'ID'});
	$proxysettings{'NCSA_USERNAME'} = $temp[0];
	$proxysettings{'NCSA_GROUP'} = $temp[1];
	$proxysettings{'NCSA_PASS'} = "lEaVeAlOnE";
	$proxysettings{'NCSA_PASS_CONFIRM'} = $proxysettings{'NCSA_PASS'};
}

if (($proxysettings{'ACTION'} eq $Lang::tr{'save'}) || ($proxysettings{'ACTION'} eq $Lang::tr{'advproxy save and restart'}) || ($proxysettings{'ACTION'} eq $Lang::tr{'proxy reconfigure'}))
{
	if ($proxysettings{'ENABLE'} !~ /^(on|off)$/ ||
	    $proxysettings{'TRANSPARENT'} !~ /^(on|off)$/ ||
	    $proxysettings{'ENABLE_BLUE'} !~ /^(on|off)$/ ||
	    $proxysettings{'TRANSPARENT_BLUE'} !~ /^(on|off)$/ ) {
		$errormessage = $Lang::tr{'invalid input'};
		goto ERROR;
	}
	if($proxysettings{'CACHE_MEM'} > $proxysettings{'CACHE_SIZE'} && $proxysettings{'CACHE_SIZE'} > 0){
		$errormessage = $Lang::tr{'advproxy errmsg cache'}." ".$proxysettings{'CACHE_MEM'}." > ".$proxysettings{'CACHE_SIZE'};
		goto ERROR;
	}

	if (!(&General::validport($proxysettings{'PROXY_PORT'})))
	{
		$errormessage = $Lang::tr{'advproxy errmsg invalid proxy port'};
		goto ERROR;
	}
	if (!(&General::validport($proxysettings{'TRANSPARENT_PORT'})))
	{
		$errormessage = $Lang::tr{'advproxy errmsg invalid proxy port'};
		goto ERROR;
	}
	if ($proxysettings{'PROXY_PORT'} eq $proxysettings{'TRANSPARENT_PORT'}) {
		$errormessage = $Lang::tr{'advproxy errmsg proxy ports equal'};
		goto ERROR;
	}
	if (!($proxysettings{'UPSTREAM_PROXY'} eq ''))
	{
		my @temp = split(/:/,$proxysettings{'UPSTREAM_PROXY'});
		if (!(&General::validip($temp[0])))
		{
			if (!(&General::validdomainname($temp[0])))
			{
				$errormessage = $Lang::tr{'advproxy errmsg invalid upstream proxy'};
				goto ERROR;
			}
		}
        }
	if (!($proxysettings{'CACHE_SIZE'} =~ /^\d+/) ||
		($proxysettings{'CACHE_SIZE'} < 10))
	{
		if (!($proxysettings{'CACHE_SIZE'} eq '0'))
		{
			$errormessage = $Lang::tr{'advproxy errmsg hdd cache size'};
			goto ERROR;
		}
	}
	if (!($proxysettings{'FILEDESCRIPTORS'} =~ /^\d+/) ||
		($proxysettings{'FILEDESCRIPTORS'} < 1) || ($proxysettings{'FILEDESCRIPTORS'} > 1048576))
	{
		$errormessage = $Lang::tr{'proxy errmsg filedescriptors'};
		goto ERROR;
	}
	if (!($proxysettings{'CACHE_MEM'} =~ /^\d+/))
	{
		$errormessage = $Lang::tr{'advproxy errmsg mem cache size'};
		goto ERROR;
	}
	my @free = &General::system_output("/usr/bin/free");
	$free[1] =~ m/(\d+)/;
	$cachemem = int $1 / 2048;
	if ($proxysettings{'CACHE_MEM'} > $cachemem) {
		$proxysettings{'CACHE_MEM'} = $cachemem;
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
	if (!($proxysettings{'TIME_TO_HOUR'}.$proxysettings{'TIME_TO_MINUTE'} gt $proxysettings{'TIME_FROM_HOUR'}.$proxysettings{'TIME_FROM_MINUTE'}))
	{
		$errormessage = $Lang::tr{'advproxy errmsg time restriction'};
		goto ERROR;
	}
	if (!($proxysettings{'MAX_INCOMING_SIZE'} =~ /^\d+/))
	{
		$errormessage = $Lang::tr{'invalid maximum incoming size'};
		goto ERROR;
	}
	if (($proxysettings{'ASNBL_FASTFLUX_DETECTION'} eq 'on') || ($proxysettings{'ASNBL_SELECANN_DETECTION'} eq 'on'))
	{
		if (-z $proxysettings{'ASNBL_FASTFLUX_THRESHOLD'}) {
			$errormessage = $Lang::tr{'advproxy fastflux no threshold given'};
			goto ERROR;
		}
		if (! looks_like_number($proxysettings{'ASNBL_FASTFLUX_THRESHOLD'})) {
			$errormessage = $Lang::tr{'advproxy fastflux threshold invalid'};
			goto ERROR;
		}
		if (($proxysettings{'ASNBL_FASTFLUX_THRESHOLD'} < 2) || ($proxysettings{'ASNBL_FASTFLUX_THRESHOLD'} > 10)) {
			$errormessage = $Lang::tr{'advproxy fastflux threshold out of bounds'};
			goto ERROR;
		}
	}
	if (!($proxysettings{'AUTH_METHOD'} eq 'none'))
	{
		unless (($proxysettings{'AUTH_METHOD'} eq 'ident') &&
			($proxysettings{'IDENT_REQUIRED'} eq 'off') &&
			($proxysettings{'IDENT_ENABLE_ACL'} eq 'off'))
		{
			if ($netsettings{'BLUE_DEV'})
			{
				if ((($proxysettings{'ENABLE'} eq 'off') || ($proxysettings{'TRANSPARENT'} eq 'on')) &&
					(($proxysettings{'ENABLE_BLUE'} eq 'off') || ($proxysettings{'TRANSPARENT_BLUE'} eq 'on')))
				{
					$errormessage = $Lang::tr{'advproxy errmsg non-transparent proxy required'};
					goto ERROR;
				}
			} else {
				if (($proxysettings{'ENABLE'} eq 'off') || ($proxysettings{'TRANSPARENT'} eq 'on'))
				{
					$errormessage = $Lang::tr{'advproxy errmsg non-transparent proxy required'};
					goto ERROR;
				}
			}
		}
		if ((!($proxysettings{'AUTH_MAX_USERIP'} eq '')) &&
			((!($proxysettings{'AUTH_MAX_USERIP'} =~ /^\d+/)) || ($proxysettings{'AUTH_MAX_USERIP'} < 1) || ($proxysettings{'AUTH_MAX_USERIP'} > 255)))
		{
			$errormessage = $Lang::tr{'advproxy errmsg max userip'};
			goto ERROR;
		}
		if (!($proxysettings{'AUTH_CACHE_TTL'} =~ /^\d+/))
		{
			$errormessage = $Lang::tr{'advproxy errmsg auth cache ttl'};
			goto ERROR;
		}
		if (!($proxysettings{'AUTH_IPCACHE_TTL'} =~ /^\d+/))
		{
			$errormessage = $Lang::tr{'advproxy errmsg auth ipcache ttl'};
			goto ERROR;
		}
		if ((!($proxysettings{'AUTH_MAX_USERIP'} eq '')) && ($proxysettings{'AUTH_IPCACHE_TTL'} eq '0'))
		{
			$errormessage = $Lang::tr{'advproxy errmsg auth ipcache may not be null'};
			goto ERROR;
		}
		if ((!($proxysettings{'AUTH_CHILDREN'} =~ /^\d+/)) || ($proxysettings{'AUTH_CHILDREN'} < 1) || ($proxysettings{'AUTH_CHILDREN'} > 255))
		{
			$errormessage = $Lang::tr{'advproxy errmsg auth children'};
			goto ERROR;
		}
	}
	if ($proxysettings{'AUTH_METHOD'} eq 'ncsa')
	{
		if ((!($proxysettings{'NCSA_MIN_PASS_LEN'} =~ /^\d+/)) || ($proxysettings{'NCSA_MIN_PASS_LEN'} < 1) || ($proxysettings{'NCSA_MIN_PASS_LEN'} > 255))
		{
			$errormessage = $Lang::tr{'advproxy errmsg password length'};
			goto ERROR;
		}
	}
	if ($proxysettings{'AUTH_METHOD'} eq 'ident')
	{
		if ((!($proxysettings{'IDENT_TIMEOUT'} =~ /^\d+/)) || ($proxysettings{'IDENT_TIMEOUT'} < 1))
		{
			$errormessage = $Lang::tr{'advproxy errmsg ident timeout'};
			goto ERROR;
		}
	}
	if ($proxysettings{'AUTH_METHOD'} eq 'ldap')
	{
		if ($proxysettings{'LDAP_BASEDN'} eq '')
		{
			$errormessage = $Lang::tr{'advproxy errmsg ldap base dn'};
			goto ERROR;
		}
		if (!&General::validip($proxysettings{'LDAP_SERVER'}))
		{
			if (!&General::validdomainname($proxysettings{'LDAP_SERVER'}))
			{
				$errormessage = $Lang::tr{'advproxy errmsg ldap server'};
				goto ERROR;
			}
		}
		if (!&General::validport($proxysettings{'LDAP_PORT'}))
		{
			$errormessage = $Lang::tr{'advproxy errmsg ldap port'};
			goto ERROR;
		}
		if (($proxysettings{'LDAP_TYPE'} eq 'ADS') || ($proxysettings{'LDAP_TYPE'} eq 'NDS'))
		{
			if (($proxysettings{'LDAP_BINDDN_USER'} eq '') || ($proxysettings{'LDAP_BINDDN_PASS'} eq ''))
			{
				$errormessage = $Lang::tr{'advproxy errmsg ldap bind dn'};
				goto ERROR;
			}
		}
	}
	if ($proxysettings{'AUTH_METHOD'} eq 'radius')
	{
		if (!&General::validip($proxysettings{'RADIUS_SERVER'}))
		{
			$errormessage = $Lang::tr{'advproxy errmsg radius server'};
			goto ERROR;
		}
		if (!&General::validport($proxysettings{'RADIUS_PORT'}))
		{
			$errormessage = $Lang::tr{'advproxy errmsg radius port'};
			goto ERROR;
		}
		if ($proxysettings{'RADIUS_SECRET'} eq '')
		{
			$errormessage = $Lang::tr{'advproxy errmsg radius secret'};
			goto ERROR;
		}
	}

	# Quick parent proxy error checking of username and password info. If username password don't both exist give an error.
	$proxy1 = 'YES';
	$proxy2 = 'YES';
	if (($proxysettings{'UPSTREAM_USER'} eq '')) {$proxy1 = '';}
	if (($proxysettings{'UPSTREAM_PASSWORD'} eq '')) {$proxy2 = '';}
	if ($proxysettings{'UPSTREAM_USER'} eq 'PASS')  {$proxy1=$proxy2='PASS'; $proxysettings{'UPSTREAM_PASSWORD'} = '';}
	if (($proxy1 ne $proxy2))
	{
		$errormessage = $Lang::tr{'advproxy errmsg invalid upstream proxy username or password setting'};
		goto ERROR;
	}

ERROR:
	&check_acls;

	if ($errormessage) {
		$proxysettings{'VALID'} = 'no'; }
	else {
		$proxysettings{'VALID'} = 'yes'; }

	if ($proxysettings{'VALID'} eq 'yes')
	{
		# Determine if suricata may needs to be restarted.
		my $suricata_proxy_ports_changed;

		# Check if the IDS is running
		if(&IDS::ids_is_running()) {
			my %oldproxysettings;

			# Read-in current proxy settings and store them as oldsettings hash.
			&General::readhash("${General::swroot}/proxy/advanced/settings", \%oldproxysettings);

			# Check if the proxy port has been changed.
			unless ($proxysettings{'PROXY_PORT'} eq $oldproxysettings{'PROXY_PORT'}) {
				# Port has changed, suricata needs to be adjusted.
				$suricata_proxy_ports_changed = 1;
			}

			# Check if the transparent port has been changed.
			unless ($proxysettings{'TRANSPARENT_PORT'} eq $oldproxysettings{'TRANSPARENT_PORT'}) {
				# Transparent port has changed, suricata needs to be adjusted.
				$suricata_proxy_ports_changed = 1;
			}
		}

		&write_acls;

		delete $proxysettings{'SRC_SUBNETS'};
		delete $proxysettings{'SRC_BANNED_IP'};
		delete $proxysettings{'SRC_BANNED_MAC'};
		delete $proxysettings{'SRC_UNRESTRICTED_IP'};
		delete $proxysettings{'SRC_UNRESTRICTED_MAC'};
		delete $proxysettings{'DST_NOCACHE'};
		delete $proxysettings{'DST_NOAUTH'};
		delete $proxysettings{'DST_NOPROXY_IP'};
		delete $proxysettings{'DST_NOPROXY_URL'};
		delete $proxysettings{'PORTS_SAFE'};
		delete $proxysettings{'PORTS_SSL'};
		delete $proxysettings{'MIME_TYPES'};
		delete $proxysettings{'NTLM_ALLOW_USERS'};
		delete $proxysettings{'NTLM_DENY_USERS'};
		delete $proxysettings{'RADIUS_ALLOW_USERS'};
		delete $proxysettings{'RADIUS_DENY_USERS'};
		delete $proxysettings{'IDENT_HOSTS'};
		delete $proxysettings{'IDENT_ALLOW_USERS'};
		delete $proxysettings{'IDENT_DENY_USERS'};

		delete $proxysettings{'CRE_GROUPS'};
		delete $proxysettings{'CRE_SVHOSTS'};

		delete $proxysettings{'NCSA_USERNAME'};
		delete $proxysettings{'NCSA_GROUP'};
		delete $proxysettings{'NCSA_PASS'};
		delete $proxysettings{'NCSA_PASS_CONFIRM'};

		$proxysettings{'TIME_MON'} = 'off' unless exists $proxysettings{'TIME_MON'};
		$proxysettings{'TIME_TUE'} = 'off' unless exists $proxysettings{'TIME_TUE'};
		$proxysettings{'TIME_WED'} = 'off' unless exists $proxysettings{'TIME_WED'};
		$proxysettings{'TIME_THU'} = 'off' unless exists $proxysettings{'TIME_THU'};
		$proxysettings{'TIME_FRI'} = 'off' unless exists $proxysettings{'TIME_FRI'};
		$proxysettings{'TIME_SAT'} = 'off' unless exists $proxysettings{'TIME_SAT'};
		$proxysettings{'TIME_SUN'} = 'off' unless exists $proxysettings{'TIME_SUN'};

		$proxysettings{'AUTH_ALWAYS_REQUIRED'} = 'off' unless exists $proxysettings{'AUTH_ALWAYS_REQUIRED'};
		$proxysettings{'NTLM_ENABLE_INT_AUTH'} = 'off' unless exists $proxysettings{'NTLM_ENABLE_INT_AUTH'};

		&General::writehash("${General::swroot}/proxy/advanced/settings", \%proxysettings);

		if (-e "${General::swroot}/proxy/settings") { &General::readhash("${General::swroot}/proxy/settings", \%stdproxysettings); }
		$stdproxysettings{'PROXY_PORT'} = $proxysettings{'PROXY_PORT'};
		$stdproxysettings{'UPSTREAM_PROXY'}    = $proxysettings{'UPSTREAM_PROXY'};
		$stdproxysettings{'UPSTREAM_USER'}     = $proxysettings{'UPSTREAM_USER'};
		$stdproxysettings{'UPSTREAM_PASSWORD'} = $proxysettings{'UPSTREAM_PASSWORD'};
		$stdproxysettings{'ENABLE_FILTER'} = $proxysettings{'ENABLE_FILTER'};
		$stdproxysettings{'ENABLE_UPDXLRATOR'} = $proxysettings{'ENABLE_UPDXLRATOR'};
		$stdproxysettings{'ENABLE_CLAMAV'} = $proxysettings{'ENABLE_CLAMAV'};
		&General::writehash("${General::swroot}/proxy/settings", \%stdproxysettings);

		&writeconfig;
		&writepacfile;

		if ($proxysettings{'CACHEMGR'} eq 'on'){&writecachemgr;}

		&General::system ('/usr/local/bin/squidctrl', 'disable');
		unlink "${General::swroot}/proxy/enable";
		unlink "${General::swroot}/proxy/transparent";
		unlink "${General::swroot}/proxy/enable_blue";
		unlink "${General::swroot}/proxy/transparent_blue";

		if ($proxysettings{'ENABLE'} eq 'on') {
			&General::system('/usr/bin/touch', "${General::swroot}/proxy/enable");
			&General::system('/usr/local/bin/squidctrl', 'enable'); }
		if ($proxysettings{'TRANSPARENT'} eq 'on' && $proxysettings{'ENABLE'} eq 'on') {
			&General::system('/usr/bin/touch', "${General::swroot}/proxy/transparent"); }
		if ($proxysettings{'ENABLE_BLUE'} eq 'on') {
			&General::system('/usr/bin/touch', "${General::swroot}/proxy/enable_blue");
			&General::system('/usr/local/bin/squidctrl', 'enable'); }
		if ($proxysettings{'TRANSPARENT_BLUE'} eq 'on' && $proxysettings{'ENABLE_BLUE'} eq 'on') {
			&General::system('/usr/bin/touch', "${General::swroot}/proxy/transparent_blue"); }

		if ($proxysettings{'ACTION'} eq $Lang::tr{'advproxy save and restart'}) { &General::system('/usr/local/bin/squidctrl', 'restart'); }
		if ($proxysettings{'ACTION'} eq $Lang::tr{'proxy reconfigure'}) { &General::system('/usr/local/bin/squidctrl', 'reconfigure'); }

		# Check if the suricata_proxy_ports_changed flag has been set.
		if ($suricata_proxy_ports_changed) {
			# Re-generate HTTP ports file.
			&IDS::generate_http_ports_file();

			# Restart suricata.
			&IDS::call_suricatactrl("restart");
		}
  }
}

if ($proxysettings{'ACTION'} eq $Lang::tr{'advproxy clear cache'})
{
	&General::system('/usr/local/bin/squidctrl', 'flush');
}

if (!$errormessage)
{
 	if (-e "${General::swroot}/proxy/advanced/settings") {
		&General::readhash("${General::swroot}/proxy/advanced/settings", \%proxysettings);
	} elsif (-e "${General::swroot}/proxy/settings") {
		&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
	}
	&read_acls;
}

# ------------------------------------------------------------------

# Hook to regenerate the configuration files, if cgi got called from command line.
if ($ENV{"REMOTE_ADDR"} eq "") {
        writeconfig();
        exit(0);
}

# -------------------------------------------------------------------

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

$checked{'FORWARD_IPADDRESS'}{'off'} = '';
$checked{'FORWARD_IPADDRESS'}{'on'} = '';
$checked{'FORWARD_IPADDRESS'}{$proxysettings{'FORWARD_IPADDRESS'}} = "checked='checked'";
$checked{'FORWARD_USERNAME'}{'off'} = '';
$checked{'FORWARD_USERNAME'}{'on'} = '';
$checked{'FORWARD_USERNAME'}{$proxysettings{'FORWARD_USERNAME'}} = "checked='checked'";
$checked{'FORWARD_VIA'}{'off'} = '';
$checked{'FORWARD_VIA'}{'on'} = '';
$checked{'FORWARD_VIA'}{$proxysettings{'FORWARD_VIA'}} = "checked='checked'";
$checked{'NO_CONNECTION_AUTH'}{'off'} = '';
$checked{'NO_CONNECTION_AUTH'}{'on'} = '';
$checked{'NO_CONNECTION_AUTH'}{$proxysettings{'NO_CONNECTION_AUTH'}} = "checked='checked'";

$selected{'MEM_POLICY'}{$proxysettings{'MEM_POLICY'}} = "selected='selected'";
$selected{'CACHE_POLICY'}{$proxysettings{'CACHE_POLICY'}} = "selected='selected'";
$selected{'L1_DIRS'}{$proxysettings{'L1_DIRS'}} = "selected='selected'";
$checked{'OFFLINE_MODE'}{'off'} = '';
$checked{'OFFLINE_MODE'}{'on'} = '';
$checked{'OFFLINE_MODE'}{$proxysettings{'OFFLINE_MODE'}} = "checked='checked'";
$checked{'CACHE_DIGESTS'}{'off'} = '';
$checked{'CACHE_DIGESTS'}{'on'} = '';
$checked{'CACHE_DIGESTS'}{$proxysettings{'CACHE_DIGESTS'}} = "checked='checked'";

$checked{'LOGGING'}{'off'} = '';
$checked{'LOGGING'}{'on'} = '';
$checked{'LOGGING'}{$proxysettings{'LOGGING'}} = "checked='checked'";
$checked{'CACHEMGR'}{'off'} = '';
$checked{'CACHEMGR'}{'on'} = '';
$checked{'CACHEMGR'}{$proxysettings{'CACHEMGR'}} = "checked='checked'";
$checked{'LOGQUERY'}{'off'} = '';
$checked{'LOGQUERY'}{'on'} = '';
$checked{'LOGQUERY'}{$proxysettings{'LOGQUERY'}} = "checked='checked'";
$checked{'LOGUSERAGENT'}{'off'} = '';
$checked{'LOGUSERAGENT'}{'on'} = '';
$checked{'LOGUSERAGENT'}{$proxysettings{'LOGUSERAGENT'}} = "checked='checked'";

$selected{'ERR_LANGUAGE'}{$proxysettings{'ERR_LANGUAGE'}} = "selected='selected'";
$selected{'ERR_DESIGN'}{$proxysettings{'ERR_DESIGN'}} = "selected='selected'";

$checked{'NO_PROXY_LOCAL'}{'off'} = '';
$checked{'NO_PROXY_LOCAL'}{'on'} = '';
$checked{'NO_PROXY_LOCAL'}{$proxysettings{'NO_PROXY_LOCAL'}} = "checked='checked'";
$checked{'NO_PROXY_LOCAL_BLUE'}{'off'} = '';
$checked{'NO_PROXY_LOCAL_BLUE'}{'on'} = '';
$checked{'NO_PROXY_LOCAL_BLUE'}{$proxysettings{'NO_PROXY_LOCAL_BLUE'}} = "checked='checked'";

$checked{'CLASSROOM_EXT'}{'off'} = '';
$checked{'CLASSROOM_EXT'}{'on'} = '';
$checked{'CLASSROOM_EXT'}{$proxysettings{'CLASSROOM_EXT'}} = "checked='checked'";

$selected{'TIME_ACCESS_MODE'}{$proxysettings{'TIME_ACCESS_MODE'}} = "selected='selected'";
$selected{'TIME_FROM_HOUR'}{$proxysettings{'TIME_FROM_HOUR'}} = "selected='selected'";
$selected{'TIME_FROM_MINUTE'}{$proxysettings{'TIME_FROM_MINUTE'}} = "selected='selected'";
$selected{'TIME_TO_HOUR'}{$proxysettings{'TIME_TO_HOUR'}} = "selected='selected'";
$selected{'TIME_TO_MINUTE'}{$proxysettings{'TIME_TO_MINUTE'}} = "selected='selected'";

$proxysettings{'TIME_MON'} = 'on' unless exists $proxysettings{'TIME_MON'};
$proxysettings{'TIME_TUE'} = 'on' unless exists $proxysettings{'TIME_TUE'};
$proxysettings{'TIME_WED'} = 'on' unless exists $proxysettings{'TIME_WED'};
$proxysettings{'TIME_THU'} = 'on' unless exists $proxysettings{'TIME_THU'};
$proxysettings{'TIME_FRI'} = 'on' unless exists $proxysettings{'TIME_FRI'};
$proxysettings{'TIME_SAT'} = 'on' unless exists $proxysettings{'TIME_SAT'};
$proxysettings{'TIME_SUN'} = 'on' unless exists $proxysettings{'TIME_SUN'};

$checked{'TIME_MON'}{'off'} = '';
$checked{'TIME_MON'}{'on'} = '';
$checked{'TIME_MON'}{$proxysettings{'TIME_MON'}} = "checked='checked'";
$checked{'TIME_TUE'}{'off'} = '';
$checked{'TIME_TUE'}{'on'} = '';
$checked{'TIME_TUE'}{$proxysettings{'TIME_TUE'}} = "checked='checked'";
$checked{'TIME_WED'}{'off'} = '';
$checked{'TIME_WED'}{'on'} = '';
$checked{'TIME_WED'}{$proxysettings{'TIME_WED'}} = "checked='checked'";
$checked{'TIME_THU'}{'off'} = '';
$checked{'TIME_THU'}{'on'} = '';
$checked{'TIME_THU'}{$proxysettings{'TIME_THU'}} = "checked='checked'";
$checked{'TIME_FRI'}{'off'} = '';
$checked{'TIME_FRI'}{'on'} = '';
$checked{'TIME_FRI'}{$proxysettings{'TIME_FRI'}} = "checked='checked'";
$checked{'TIME_SAT'}{'off'} = '';
$checked{'TIME_SAT'}{'on'} = '';
$checked{'TIME_SAT'}{$proxysettings{'TIME_SAT'}} = "checked='checked'";
$checked{'TIME_SUN'}{'off'} = '';
$checked{'TIME_SUN'}{'on'} = '';
$checked{'TIME_SUN'}{$proxysettings{'TIME_SUN'}} = "checked='checked'";

$selected{'THROTTLING_GREEN_TOTAL'}{$proxysettings{'THROTTLING_GREEN_TOTAL'}} = "selected='selected'";
$selected{'THROTTLING_GREEN_HOST'}{$proxysettings{'THROTTLING_GREEN_HOST'}} = "selected='selected'";
$selected{'THROTTLING_BLUE_TOTAL'}{$proxysettings{'THROTTLING_BLUE_TOTAL'}} = "selected='selected'";
$selected{'THROTTLING_BLUE_HOST'}{$proxysettings{'THROTTLING_BLUE_HOST'}} = "selected='selected'";

$checked{'ASNBL_FASTFLUX_DETECTION'}{'off'} = '';
$checked{'ASNBL_FASTFLUX_DETECTION'}{'on'} = '';
$checked{'ASNBL_FASTFLUX_DETECTION'}{$proxysettings{'ASNBL_FASTFLUX_DETECTION'}} = "checked='checked'";

$checked{'ASNBL_SELECANN_DETECTION'}{'off'} = '';
$checked{'ASNBL_SELECANN_DETECTION'}{'on'} = '';
$checked{'ASNBL_SELECANN_DETECTION'}{$proxysettings{'ASNBL_SELECANN_DETECTION'}} = "checked='checked'";

$checked{'ENABLE_MIME_FILTER'}{'off'} = '';
$checked{'ENABLE_MIME_FILTER'}{'on'} = '';
$checked{'ENABLE_MIME_FILTER'}{$proxysettings{'ENABLE_MIME_FILTER'}} = "checked='checked'";

$checked{'AUTH_METHOD'}{'none'} = '';
$checked{'AUTH_METHOD'}{'ncsa'} = '';
$checked{'AUTH_METHOD'}{'ident'} = '';
$checked{'AUTH_METHOD'}{'ldap'} = '';
$checked{'AUTH_METHOD'}{'ntlm-auth'} = '';
$checked{'AUTH_METHOD'}{'radius'} = '';
$checked{'AUTH_METHOD'}{$proxysettings{'AUTH_METHOD'}} = "checked='checked'";

$proxysettings{'AUTH_ALWAYS_REQUIRED'} = 'on' unless exists $proxysettings{'AUTH_ALWAYS_REQUIRED'};

$checked{'AUTH_ALWAYS_REQUIRED'}{'off'} = '';
$checked{'AUTH_ALWAYS_REQUIRED'}{'on'} = '';
$checked{'AUTH_ALWAYS_REQUIRED'}{$proxysettings{'AUTH_ALWAYS_REQUIRED'}} = "checked='checked'";

$checked{'NCSA_BYPASS_REDIR'}{'off'} = '';
$checked{'NCSA_BYPASS_REDIR'}{'on'} = '';
$checked{'NCSA_BYPASS_REDIR'}{$proxysettings{'NCSA_BYPASS_REDIR'}} = "checked='checked'";

$selected{'NCSA_GROUP'}{$proxysettings{'NCSA_GROUP'}} = "selected='selected'";

$selected{'LDAP_TYPE'}{$proxysettings{'LDAP_TYPE'}} = "selected='selected'";

$proxysettings{'NTLM_ENABLE_INT_AUTH'} = 'on' unless exists $proxysettings{'NTLM_ENABLE_INT_AUTH'};

$checked{'NTLM_ENABLE_INT_AUTH'}{'off'} = '';
$checked{'NTLM_ENABLE_INT_AUTH'}{'on'} = '';
$checked{'NTLM_ENABLE_INT_AUTH'}{$proxysettings{'NTLM_ENABLE_INT_AUTH'}} = "checked='checked'";

$checked{'NTLM_ENABLE_ACL'}{'off'} = '';
$checked{'NTLM_ENABLE_ACL'}{'on'} = '';
$checked{'NTLM_ENABLE_ACL'}{$proxysettings{'NTLM_ENABLE_ACL'}} = "checked='checked'";

$checked{'NTLM_USER_ACL'}{'positive'} = '';
$checked{'NTLM_USER_ACL'}{'negative'} = '';
$checked{'NTLM_USER_ACL'}{$proxysettings{'NTLM_USER_ACL'}} = "checked='checked'";

$checked{'NTLM_AUTH_BASIC'}{'on'} = '';
$checked{'NTLM_AUTH_BASIC'}{'off'} = '';
$checked{'NTLM_AUTH_BASIC'}{$proxysettings{'NTLM_AUTH_BASIC'}} = "checked='checked'";

$checked{'RADIUS_ENABLE_ACL'}{'off'} = '';
$checked{'RADIUS_ENABLE_ACL'}{'on'} = '';
$checked{'RADIUS_ENABLE_ACL'}{$proxysettings{'RADIUS_ENABLE_ACL'}} = "checked='checked'";

$checked{'RADIUS_USER_ACL'}{'positive'} = '';
$checked{'RADIUS_USER_ACL'}{'negative'} = '';
$checked{'RADIUS_USER_ACL'}{$proxysettings{'RADIUS_USER_ACL'}} = "checked='checked'";

$checked{'IDENT_REQUIRED'}{'off'} = '';
$checked{'IDENT_REQUIRED'}{'on'} = '';
$checked{'IDENT_REQUIRED'}{$proxysettings{'IDENT_REQUIRED'}} = "checked='checked'";

$checked{'IDENT_ENABLE_ACL'}{'off'} = '';
$checked{'IDENT_ENABLE_ACL'}{'on'} = '';
$checked{'IDENT_ENABLE_ACL'}{$proxysettings{'IDENT_ENABLE_ACL'}} = "checked='checked'";

$checked{'IDENT_USER_ACL'}{'positive'} = '';
$checked{'IDENT_USER_ACL'}{'negative'} = '';
$checked{'IDENT_USER_ACL'}{$proxysettings{'IDENT_USER_ACL'}} = "checked='checked'";

$checked{'ENABLE_FILTER'}{'off'} = '';
$checked{'ENABLE_FILTER'}{'on'} = '';
$checked{'ENABLE_FILTER'}{$proxysettings{'ENABLE_FILTER'}} = "checked='checked'";

$checked{'ENABLE_UPDXLRATOR'}{'off'} = '';
$checked{'ENABLE_UPDXLRATOR'}{'on'} = '';
$checked{'ENABLE_UPDXLRATOR'}{$proxysettings{'ENABLE_UPDXLRATOR'}} = "checked='checked'";

$checked{'ENABLE_CLAMAV'}{'off'} = '';
$checked{'ENABLE_CLAMAV'}{'on'} = '';
$checked{'ENABLE_CLAMAV'}{$proxysettings{'ENABLE_CLAMAV'}} = "checked='checked'";

&Header::openpage($Lang::tr{'advproxy advanced web proxy configuration'}, 1, '');

&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<font class='base'>$errormessage&nbsp;</font>\n";
	&Header::closebox();
}

if ($squidversion[0] =~ /^Squid\sCache:\sVersion\s/i)
{
	$squidversion[0] =~ s/^Squid\sCache:\sVersion//i;
	$squidversion[0] =~ s/^\s+//g;
	$squidversion[0] =~ s/\s+$//g;
} else {
	$squidversion[0] = $Lang::tr{'advproxy unknown'};
}

# ===================================================================
#  Main settings
# ===================================================================

unless ($proxysettings{'NCSA_EDIT_MODE'} eq 'yes') {

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

&Header::openbox('100%', 'left', "$Lang::tr{'advproxy advanced web proxy'}");

print <<END
<table width='100%'>
<tr>
	<td colspan='4' class='base'><b>$Lang::tr{'advproxy common settings'}</b></td>
</tr>
<tr>
	<td width='25%' class='base'>$Lang::tr{'advproxy enabled on'} <font color="$Header::colourgreen">Green</font>:</td>
	<td width='20%'><input type='checkbox' name='ENABLE' $checked{'ENABLE'}{'on'} /></td>
	<td width='25%' class='base'>$Lang::tr{'advproxy proxy port'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td width='30%'><input type='text' name='PROXY_PORT' value='$proxysettings{'PROXY_PORT'}' size='5' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'advproxy transparent on'} <font color="$Header::colourgreen">Green</font>:</td>
	<td><input type='checkbox' name='TRANSPARENT' $checked{'TRANSPARENT'}{'on'} /></td>
	<td width='25%' class='base'>$Lang::tr{'advproxy proxy port transparent'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td width='30%'><input type='text' name='TRANSPARENT_PORT' value='$proxysettings{'TRANSPARENT_PORT'}' size='5' /></td>
</tr>
<tr>
END
;
if ($netsettings{'BLUE_DEV'}) {
	print "<td class='base'>$Lang::tr{'advproxy enabled on'} <font color='$Header::colourblue'>Blue</font>:</td>";
	print "<td><input type='checkbox' name='ENABLE_BLUE' $checked{'ENABLE_BLUE'}{'on'} /></td>";
} else {
	print "<td colspan='2'>&nbsp;</td>";
}
print <<END
	<td class='base'>$Lang::tr{'advproxy visible hostname'}:</td>
	<td><input type='text' name='VISIBLE_HOSTNAME'
		value='@{[ &Header::escape($proxysettings{'VISIBLE_HOSTNAME'}) ]}' /></td>
</tr>
<tr>
END
;
if ($netsettings{'BLUE_DEV'}) {
	print "<td class='base'>$Lang::tr{'advproxy transparent on'} <font color='$Header::colourblue'>Blue</font>:</td>";
	print "<td><input type='checkbox' name='TRANSPARENT_BLUE' $checked{'TRANSPARENT_BLUE'}{'on'} /></td>";
} else {
	print "<td colspan='2'>&nbsp;</td>";
}
print <<END
	<td class='base'>$Lang::tr{'advproxy error language'}:</td>
	<td class='base'>
	<select name='ERR_LANGUAGE'>
END
;
	foreach (<$errordir/*>) {
		if (-d) {
			$language = substr($_,rindex($_,"/")+1);
			print "<option value='$language' $selected{'ERR_LANGUAGE'}{$language}>$language</option>\n";
		}
	}
print <<END
	</select>
	</td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td>&nbsp;</td>
	<td class='base'>$Lang::tr{'advproxy error design'}:</td>
	<td class='base'><select name='ERR_DESIGN'>
		<option value='ipfire' $selected{'ERR_DESIGN'}{'ipfire'}>IPFire</option>
		<option value='squid' $selected{'ERR_DESIGN'}{'squid'}>$Lang::tr{'advproxy standard'}</option>
	</select></td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
END
;
if ( -e "/usr/bin/squidclamav" ) {
	print "<td class='base'><b>".$Lang::tr{'advproxy squidclamav'}."</b><br />";
	if ( ! -e "/var/run/clamav/clamd.pid" ){
		print "<font color='red'>clamav not running</font><br /><br />";
		$proxysettings{'ENABLE_CLAMAV'} = 'off';
		}
	else {
		print $Lang::tr{'advproxy enabled'}."<input type='checkbox' name='ENABLE_CLAMAV' ".$checked{'ENABLE_CLAMAV'}{'on'}." /><br />";
}
	print "</td>";
} else {
	print "<td></td>";
}
print "<td class='base'><a href='/cgi-bin/urlfilter.cgi'><b>".$Lang::tr{'advproxy url filter'}."</a></b><br />";
print $Lang::tr{'advproxy enabled'}."<input type='checkbox' name='ENABLE_FILTER' ".$checked{'ENABLE_FILTER'}{'on'}." /><br />";
print "</td>";
print "<td class='base'><a href='/cgi-bin/updatexlrator.cgi'><b>".$Lang::tr{'advproxy update accelerator'}."</a></b><br />";
print $Lang::tr{'advproxy enabled'}."<input type='checkbox' name='ENABLE_UPDXLRATOR' ".$checked{'ENABLE_UPDXLRATOR'}{'on'}." /><br />";
print "</td></tr>";
print <<END
</table>
<hr size='1'>
<table width='100%'>
<tr>
	<td colspan='4' class='base'><b>$Lang::tr{'advproxy upstream proxy'}</b></td>
</tr>
<tr>
	<td width='25%' class='base'>$Lang::tr{'advproxy via forwarding'}:</td>
	<td width='20%'><input type='checkbox' name='FORWARD_VIA' $checked{'FORWARD_VIA'}{'on'} /></td>
	<td width='25%' class='base'>$Lang::tr{'advproxy upstream proxy host:port'}:</td>
	<td width='30%'><input type='text' name='UPSTREAM_PROXY' value='$proxysettings{'UPSTREAM_PROXY'}' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'advproxy client IP forwarding'}:</td>
	<td><input type='checkbox' name='FORWARD_IPADDRESS' $checked{'FORWARD_IPADDRESS'}{'on'} /></td>
	<td class='base'>$Lang::tr{'advproxy upstream username'}:</td>
	<td><input type='text' name='UPSTREAM_USER' value='$proxysettings{'UPSTREAM_USER'}' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'advproxy username forwarding'}:</td>
	<td><input type='checkbox' name='FORWARD_USERNAME' $checked{'FORWARD_USERNAME'}{'on'} /></td>
	<td class='base'>$Lang::tr{'advproxy upstream password'}:</td>
	<td><input type='password' name='UPSTREAM_PASSWORD' value='$proxysettings{'UPSTREAM_PASSWORD'}' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'advproxy no connection auth'}:</td>
	<td><input type='checkbox' name='NO_CONNECTION_AUTH' $checked{'NO_CONNECTION_AUTH'}{'on'} /></td>
	<td>&nbsp;</td>
	<td>&nbsp;</td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
	<td colspan='4' class='base'><b>$Lang::tr{'advproxy log settings'}</b></td>
</tr>
<tr>
	<td width='25%' class='base'>$Lang::tr{'advproxy log enabled'}:</td>
	<td width='20%'><input type='checkbox' name='LOGGING' $checked{'LOGGING'}{'on'} /></td>
	<td width='25%'class='base'>$Lang::tr{'advproxy log query'}:</td>
	<td width='30%'><input type='checkbox' name='LOGQUERY' $checked{'LOGQUERY'}{'on'} /></td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td>&nbsp;</td>
	<td class='base'>$Lang::tr{'advproxy log useragent'}:</td>
	<td><input type='checkbox' name='LOGUSERAGENT' $checked{'LOGUSERAGENT'}{'on'} /></td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
	<td colspan='4'><b>$Lang::tr{'advproxy cache management'}</b></td>
</tr>
<tr>
	<td class='base'><a href='/cgi-bin/cachemgr.cgi' target='_blank'>$Lang::tr{'proxy cachemgr'}:</td>
	<td><input type='checkbox' name='CACHEMGR' $checked{'CACHEMGR'}{'on'} /></td>
	<td class='base'>$Lang::tr{'advproxy admin mail'}:</td>
	<td><input type='text' name='ADMIN_MAIL_ADDRESS'
		value='@{[ &Header::escape($proxysettings{'ADMIN_MAIL_ADDRESS'}) ]}' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'proxy filedescriptors'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td><input type='text' name='FILEDESCRIPTORS' value='$proxysettings{'FILEDESCRIPTORS'}' size='5' /></td>
	<td class='base'>$Lang::tr{'proxy admin password'}:</td>
	<td><input type='text' name='ADMIN_PASSWORD'
		value='@{[ &Header::escape($proxysettings{'ADMIN_PASSWORD'}) ]}' /></td>
</tr>
<tr>
	<td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='30%'></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'advproxy ram cache size'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td><input type='text' name='CACHE_MEM' value='$proxysettings{'CACHE_MEM'}' size='5' /></td>
	<td class='base'>$Lang::tr{'advproxy hdd cache size'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td><input type='text' name='CACHE_SIZE' value='$proxysettings{'CACHE_SIZE'}' size='5' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'advproxy min size'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td><input type='text' name='MIN_SIZE' value='$proxysettings{'MIN_SIZE'}' size='5' /></td>
	<td class='base'>$Lang::tr{'advproxy max size'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td><input type='text' name='MAX_SIZE' value='$proxysettings{'MAX_SIZE'}' size='5' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'advproxy number of L1 dirs'}:</td>
	<td class='base'><select name='L1_DIRS'>
		<option value='16'  $selected{'L1_DIRS'}{'16'}>16</option>
		<option value='32'  $selected{'L1_DIRS'}{'32'}>32</option>
		<option value='64'  $selected{'L1_DIRS'}{'64'}>64</option>
		<option value='128' $selected{'L1_DIRS'}{'128'}>128</option>
		<option value='256' $selected{'L1_DIRS'}{'256'}>256</option>
	</select></td>
	<td colspan='2' rowspan= '5' valign='top' class='base'>
		<table cellspacing='0' cellpadding='0'>
			<tr>
				<!-- intentionally left empty -->
			</tr>
			<tr>
			<td>$Lang::tr{'advproxy no cache sites'}:</td>
			</tr>
			<tr>
				<!-- intentionally left empty -->
			</tr>
			<tr>
				<!-- intentionally left empty -->
			</tr>
			<tr>
			<td><textarea name='DST_NOCACHE' cols='32' rows='6' wrap='off'>
END
;

print $proxysettings{'DST_NOCACHE'};

print <<END
</textarea></td>
		</tr>
		</table>
	</td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'advproxy memory replacement policy'}:</td>
	<td class='base'><select name='MEM_POLICY'>
		<option value='LRU' $selected{'MEM_POLICY'}{'LRU'}>LRU</option>
		<option value='heap LFUDA' $selected{'MEM_POLICY'}{'heap LFUDA'}>heap LFUDA</option>
		<option value='heap GDSF' $selected{'MEM_POLICY'}{'heap GDSF'}>heap GDSF</option>
		<option value='heap LRU' $selected{'MEM_POLICY'}{'heap LRU'}>heap LRU</option>
	</select></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'advproxy cache replacement policy'}:</td>
	<td class='base'><select name='CACHE_POLICY'>
		<option value='LRU' $selected{'CACHE_POLICY'}{'LRU'}>LRU</option>
		<option value='heap LFUDA' $selected{'CACHE_POLICY'}{'heap LFUDA'}>heap LFUDA</option>
		<option value='heap GDSF' $selected{'CACHE_POLICY'}{'heap GDSF'}>heap GDSF</option>
		<option value='heap LRU' $selected{'CACHE_POLICY'}{'heap LRU'}>heap LRU</option>
	</select></td>
</tr>
<tr>
	<td colspan='2'>&nbsp;</td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'advproxy offline mode'}:</td>
	<td><input type='checkbox' name='OFFLINE_MODE' $checked{'OFFLINE_MODE'}{'on'} /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'advproxy cache-digest'}:</td>
        <td><input type='checkbox' name='CACHE_DIGESTS' $checked{'CACHE_DIGESTS'}{'on'} /></td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
	<td colspan='4'><b>$Lang::tr{'advproxy destination ports'}</b></td>
</tr>
<tr>
	<td width='25%' align='center'></td> <td width='20%' align='center'></td><td width='25%' align='center'></td><td width='30%' align='center'></td>
</tr>
<tr>
	<td colspan='2' class='base'>$Lang::tr{'advproxy standard ports'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td colspan='2' class='base'>$Lang::tr{'advproxy ssl ports'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
</tr>
<tr>
	<td colspan='2'><textarea name='PORTS_SAFE' cols='32' rows='6' wrap='off'>
END
;
	if (!$proxysettings{'PORTS_SAFE'}) { print $def_ports_safe; } else { print $proxysettings{'PORTS_SAFE'}; }

print <<END
</textarea></td>
	<td colspan='2'><textarea name='PORTS_SSL' cols='32' rows='6' wrap='off'>
END
;
	if (!$proxysettings{'PORTS_SSL'}) { print $def_ports_ssl; } else { print $proxysettings{'PORTS_SSL'}; }

print <<END
</textarea></td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
	<td colspan='4'><b>$Lang::tr{'advproxy network based access'}</b></td>
</tr>
<tr>
	<td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='30%'></td>
</tr>
<tr>
	<td colspan='4' class='base'>$Lang::tr{'advproxy allowed subnets'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
</tr>
<tr>
	<td colspan='2' rowspan='4'><textarea name='SRC_SUBNETS' cols='32' rows='3' wrap='off'>
END
;

if (!$proxysettings{'SRC_SUBNETS'})
{
	if (&Header::green_used()) {
		print "$green_cidr\n";
	}

	if (&Header::blue_used()) {
		print "$blue_cidr\n";
	}
} else { print $proxysettings{'SRC_SUBNETS'}; }

print <<END
</textarea></td>
END
;

$line = $Lang::tr{'advproxy no internal proxy on green'};
$line =~ s/Green/<font color="$Header::colourgreen">Green<\/font>/i;
print "<td class='base'>$line:</td>\n";
print <<END
	<td><input type='checkbox' name='NO_PROXY_LOCAL' $checked{'NO_PROXY_LOCAL'}{'on'} /></td>
</tr>
END
;
if ($netsettings{'BLUE_DEV'}) {
	$line = $Lang::tr{'advproxy no internal proxy on blue'};
	$line =~ s/Blue/<font color="$Header::colourblue">Blue<\/font>/i;
	print "<tr>\n";
	print "<td class='base'>$line:</td>\n";
	print <<END
	<td><input type='checkbox' name='NO_PROXY_LOCAL_BLUE' $checked{'NO_PROXY_LOCAL_BLUE'}{'on'} /></td>
</tr>
END
;
}
print <<END
<tr>
	<td colspan='2'>&nbsp;</td>
</tr>
<tr>
	<td colspan='2'>&nbsp;</td>
</tr>
</table>
<table width='100%'>
<tr>
	<td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='30%'></td>
</tr>
<tr>
	<td colspan='2' class='base'>$Lang::tr{'advproxy unrestricted ip clients'}:</td>
	<td colspan='2' class='base'>$Lang::tr{'advproxy unrestricted mac clients'}:</td>
</tr>
<tr>
	<td colspan='2'><textarea name='SRC_UNRESTRICTED_IP' cols='32' rows='3' wrap='off'>
END
;

	print $proxysettings{'SRC_UNRESTRICTED_IP'};

print <<END
</textarea></td>
	<td colspan='2'><textarea name='SRC_UNRESTRICTED_MAC' cols='32' rows='3' wrap='off'>
END
;

print $proxysettings{'SRC_UNRESTRICTED_MAC'};

print <<END
</textarea></td>
</tr>
</table>
<table width='100%'>
<tr>
	<td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='30%'></td>
</tr>
<tr>
	<td colspan='2' class='base'>$Lang::tr{'advproxy banned ip clients'}:</td>
	<td colspan='2' class='base'>$Lang::tr{'advproxy banned mac clients'}:</td>
</tr>
<tr>
	<td colspan='2'><textarea name='SRC_BANNED_IP' cols='32' rows='3' wrap='off'>
END
;

	print $proxysettings{'SRC_BANNED_IP'};

print <<END
</textarea></td>
	<td colspan='2'><textarea name='SRC_BANNED_MAC' cols='32' rows='3' wrap='off'>
END
;

print $proxysettings{'SRC_BANNED_MAC'};

print <<END
</textarea></td>
</tr>
</table>

<hr size='1'>

END
;
# -------------------------------------------------------------------
#  CRE GUI - optional
# -------------------------------------------------------------------

if (-e $cre_enabled) { print <<END
<table width='100%'>

<tr>
	<td colspan='4'><b>$Lang::tr{'advproxy classroom extensions'}</b> $Lang::tr{'advproxy enabled'}:<input type='checkbox' name='CLASSROOM_EXT' $checked{'CLASSROOM_EXT'}{'on'} /></td>
</tr>
<tr>
	<td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='30%'></td>
</tr>
<tr>

END
;
if ($proxysettings{'CLASSROOM_EXT'} eq 'on'){
print <<END
	<td class='base'>$Lang::tr{'advproxy supervisor password'}:</td>
	<td><input type='password' name='SUPERVISOR_PASSWORD' value='$proxysettings{'SUPERVISOR_PASSWORD'}' size='12' /></td>
</tr>
<tr>
	<td colspan='2' class='base'>$Lang::tr{'advproxy cre group definitions'}:</td>
	<td colspan='2' class='base'>$Lang::tr{'advproxy cre supervisors'}:</td>
END
;
}
print "</tr>";
if ($proxysettings{'CLASSROOM_EXT'} eq 'on'){
print <<END
<tr>
	<td colspan='2'><textarea name='CRE_GROUPS' cols='32' rows='6' wrap='off'>
END
;

	print $proxysettings{'CRE_GROUPS'};

print <<END
</textarea></td>
	<td colspan='2'><textarea name='CRE_SVHOSTS' cols='32' rows='6' wrap='off'>
END
;
	print $proxysettings{'CRE_SVHOSTS'};

print <<END
</textarea></td>
</tr>
END
;
}
print "</table><hr size='1'>";

} else {
	print <<END
	<input type='hidden' name='SUPERVISOR_PASSWORD' value='$proxysettings{'SUPERVISOR_PASSWORD'}' />
	<input type='hidden' name='CRE_GROUPS'          value='$proxysettings{'CRE_GROUPS'}' />
	<input type='hidden' name='CRE_SVHOSTS'         value='$proxysettings{'CRE_SVHOSTS'}' />
END
;
}

# ===================================================================
#  WPAD settings
# ===================================================================

print <<END
<table width='100%'>
<tr>
	<td colspan='4'><b>$Lang::tr{'advproxy wpad title'}</b></td>
</tr>
<tr>
	<td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='30%'></td>
</tr>
<tr>
	<td colspan='2' class='base'>$Lang::tr{'advproxy wpad label dst_noproxy_ip'}:</td>
	<td colspan='2' class='base'>$Lang::tr{'advproxy wpad label dst_noproxy_url'}:</td>
</tr>
<tr>
	<td colspan='2'><textarea name='DST_NOPROXY_IP' cols='32' rows='3' wrap='off'>
END
;

	print $proxysettings{'DST_NOPROXY_IP'};

print <<END
</textarea></td>

	<td colspan='2'><textarea name='DST_NOPROXY_URL' cols='32' rows='3' wrap='off'>
END
;

	print $proxysettings{'DST_NOPROXY_URL'};

print <<END
</textarea></td>
</tr>
<tr>
	<td colspan='2' class='base'>$Lang::tr{'advproxy wpad example dst_noproxy_ip'}</td>
	<td colspan='2' class='base'>$Lang::tr{'advproxy wpad example dst_noproxy_url'}</td>
</tr>
<tr>
	<td colspan="4">&nbsp;</td>
</tr>
<tr>
	<td colspan="4">$Lang::tr{'advproxy wpad view pac'}: <a href="http://$ENV{SERVER_ADDR}:81/wpad.dat" target="_blank">http://$ENV{SERVER_ADDR}:81/wpad.dat</a></td>
</tr>
<tr>
	<td colspan="4">&nbsp;</td>
</tr>
</table>

<hr size='1'>

END
;

# -------------------------------------------------------------------

print <<END

<table width='100%'>
<tr>
	<td colspan='4'><b>$Lang::tr{'advproxy time restrictions'}</b></td>
</tr>
<table width='100%'>
<tr>
	<td width='2%'>$Lang::tr{'advproxy access'}</td>
	<td width='1%'>&nbsp;</td>
	<td width='2%' align='center'>$Lang::tr{'advproxy monday'}</td>
	<td width='2%' align='center'>$Lang::tr{'advproxy tuesday'}</td>
	<td width='2%' align='center'>$Lang::tr{'advproxy wednesday'}</td>
	<td width='2%' align='center'>$Lang::tr{'advproxy thursday'}</td>
	<td width='2%' align='center'>$Lang::tr{'advproxy friday'}</td>
	<td width='2%' align='center'>$Lang::tr{'advproxy saturday'}</td>
	<td width='2%' align='center'>$Lang::tr{'advproxy sunday'}</td>
	<td width='1%'>&nbsp;&nbsp;</td>
	<td width='7%' colspan=3>$Lang::tr{'advproxy from'}</td>
	<td width='1%'>&nbsp;</td>
	<td width='7%' colspan=3>$Lang::tr{'advproxy to'}</td>
	<td>&nbsp;</td>
</tr>
<tr>
	<td class='base'>
	<select name='TIME_ACCESS_MODE'>
	<option value='allow' $selected{'TIME_ACCESS_MODE'}{'allow'}>$Lang::tr{'advproxy mode allow'}</option>
	<option value='deny'  $selected{'TIME_ACCESS_MODE'}{'deny'}>$Lang::tr{'advproxy mode deny'}</option>
	</select>
	</td>
	<td>&nbsp;</td>
	<td class='base'><input type='checkbox' name='TIME_MON' $checked{'TIME_MON'}{'on'} /></td>
	<td class='base'><input type='checkbox' name='TIME_TUE' $checked{'TIME_TUE'}{'on'} /></td>
	<td class='base'><input type='checkbox' name='TIME_WED' $checked{'TIME_WED'}{'on'} /></td>
	<td class='base'><input type='checkbox' name='TIME_THU' $checked{'TIME_THU'}{'on'} /></td>
	<td class='base'><input type='checkbox' name='TIME_FRI' $checked{'TIME_FRI'}{'on'} /></td>
	<td class='base'><input type='checkbox' name='TIME_SAT' $checked{'TIME_SAT'}{'on'} /></td>
	<td class='base'><input type='checkbox' name='TIME_SUN' $checked{'TIME_SUN'}{'on'} /></td>
	<td>&nbsp;</td>
	<td class='base'>
	<select name='TIME_FROM_HOUR'>
END
;
for ($i=0;$i<=24;$i++) {
	$_ = sprintf("%02s",$i);
	print "<option $selected{'TIME_FROM_HOUR'}{$_}>$_</option>\n";
}
print <<END
	</select>
	</td>
	<td>:</td>
	<td class='base'>
	<select name='TIME_FROM_MINUTE'>
END
;
for ($i=0;$i<=45;$i+=15) {
	$_ = sprintf("%02s",$i);
	print "<option $selected{'TIME_FROM_MINUTE'}{$_}>$_</option>\n";
}
print <<END
	</select>
	<td> - </td>
	</td>
	<td class='base'>
	<select name='TIME_TO_HOUR'>
END
;
for ($i=0;$i<=24;$i++) {
	$_ = sprintf("%02s",$i);
	print "<option $selected{'TIME_TO_HOUR'}{$_}>$_</option>\n";
}
print <<END
	</select>
	</td>
	<td>:</td>
	<td class='base'>
	<select name='TIME_TO_MINUTE'>
END
;
for ($i=0;$i<=45;$i+=15) {
	$_ = sprintf("%02s",$i);
	print "<option $selected{'TIME_TO_MINUTE'}{$_}>$_</option>\n";
}
print <<END
	</select>
	</td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
	<td colspan='4'><b>$Lang::tr{'advproxy transfer limits'}</b></td>
</tr>
<tr>
	<td width='25%' class='base'>$Lang::tr{'advproxy max download size'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td width='20%'><input type='text' name='MAX_INCOMING_SIZE' value='$proxysettings{'MAX_INCOMING_SIZE'}' size='5' /></td>
	<td width='25%' class='base'>$Lang::tr{'advproxy max upload size'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td width='30%'><input type='text' name='MAX_OUTGOING_SIZE' value='$proxysettings{'MAX_OUTGOING_SIZE'}' size='5' /></td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
	<td colspan='4'><b>$Lang::tr{'advproxy download throttling'}</b></td>
</tr>
<tr>
	<td width='25%' class='base'>$Lang::tr{'advproxy throttling total on'} <font color="$Header::colourgreen">Green</font>:</td>
	<td width='20%' class='base'>
	<select name='THROTTLING_GREEN_TOTAL'>
END
;

foreach (@throttle_limits) {
	my $val = $_;
	my $unit = "kbit/s";

	if ($val >= 1024) {
		$unit = "Mbit/s";
		$val /= 1024;
	}

	print "\t<option value='$_' $selected{'THROTTLING_GREEN_TOTAL'}{$_}>$val $unit</option>\n";
}

print <<END
	<option value='0' $selected{'THROTTLING_GREEN_TOTAL'}{'unlimited'}>$Lang::tr{'advproxy throttling unlimited'}</option>\n";
	</select>
	</td>
	<td width='25%' class='base'>$Lang::tr{'advproxy throttling per host on'} <font color="$Header::colourgreen">Green</font>:</td>
	<td width='30%' class='base'>
	<select name='THROTTLING_GREEN_HOST'>
END
;

foreach (@throttle_limits) {
	print "\t<option value='$_' $selected{'THROTTLING_GREEN_HOST'}{$_}>$_ kbit/s</option>\n";
}

print <<END
	<option value='0' $selected{'THROTTLING_GREEN_HOST'}{'unlimited'}>$Lang::tr{'advproxy throttling unlimited'}</option>\n";
	</select>
	</td>
</tr>
END
;

if ($netsettings{'BLUE_DEV'}) {
	print <<END
<tr>
	<td class='base'>$Lang::tr{'advproxy throttling total on'} <font color="$Header::colourblue">Blue</font>:</td>
	<td class='base'>
	<select name='THROTTLING_BLUE_TOTAL'>
END
;

foreach (@throttle_limits) {
	print "\t<option value='$_' $selected{'THROTTLING_BLUE_TOTAL'}{$_}>$_ kbit/s</option>\n";
}

print <<END
	<option value='0' $selected{'THROTTLING_BLUE_TOTAL'}{'unlimited'}>$Lang::tr{'advproxy throttling unlimited'}</option>\n";
	</select>
	</td>
	<td class='base'>$Lang::tr{'advproxy throttling per host on'} <font color="$Header::colourblue">Blue</font>:</td>
	<td class='base'>
	<select name='THROTTLING_BLUE_HOST'>
END
;

foreach (@throttle_limits) {
	print "\t<option value='$_' $selected{'THROTTLING_BLUE_HOST'}{$_}>$_ kbit/s</option>\n";
}

print <<END
	<option value='0' $selected{'THROTTLING_BLUE_HOST'}{'unlimited'}>$Lang::tr{'advproxy throttling unlimited'}</option>\n";
	</select>
	</td>
</tr>
END
;
}

print <<END
</table>
<hr size='1'>
<table width='100%'>
<tr>
	<td colspan='4'><b>$Lang::tr{'advproxy MIME filter'}</b> $Lang::tr{'advproxy enabled'}:<input type='checkbox' name='ENABLE_MIME_FILTER' $checked{'ENABLE_MIME_FILTER'}{'on'} /></td>
</tr>
END
;
if ( $proxysettings{'ENABLE_MIME_FILTER'} eq 'on' ){
print <<END
<tr>
	<td  colspan='2' class='base'>$Lang::tr{'advproxy MIME block types'}:</td>
	<td>&nbsp;</td>
	<td>&nbsp;</td>
</tr>
<tr>
	<td colspan='2'><textarea name='MIME_TYPES' cols='32' rows='6' wrap='off'>
END
;

print $proxysettings{'MIME_TYPES'};

print <<END
</textarea></td>
	<td>&nbsp;</td>
	<td>&nbsp;</td>
</tr>
END
;
}
print <<END
</table>

<hr size='1'>

<table width='100%'>
<tr>
       <td><b>$Lang::tr{'advproxy asbased anomaly detection'}</b></td>
</tr>
<tr>
       <td class='base'>$Lang::tr{'advproxy fastflux detection'}:</td>
       <td><input type='checkbox' name='ASNBL_FASTFLUX_DETECTION' $checked{'ASNBL_FASTFLUX_DETECTION'}{'on'} /></td>
       <td class='base'>$Lang::tr{'advproxy fastflux detection threshold'}:</td>
       <td><input type='text' name='ASNBL_FASTFLUX_THRESHOLD' value='$proxysettings{'ASNBL_FASTFLUX_THRESHOLD'}' size=2 /></td>
</tr>
<tr>
       <td class='base'>$Lang::tr{'advproxy selectively announcements detection'}:</td>
       <td colspan='3'><input type='checkbox' name='ASNBL_SELECANN_DETECTION' $checked{'ASNBL_SELECANN_DETECTION'}{'on'} /></td>
</tr>
</table>

<hr size='1'>
END
;

my $auth_columns = 5;
if ($HAVE_NTLM_AUTH) {
	$auth_columns++;
}
my $auth_column_width = 100 / $auth_columns;

print <<END;
<table width='100%'>
<tr>
	<td colspan='$auth_columns'><b>$Lang::tr{'advproxy AUTH method'}</b></td>
</tr>
<tr>
	<td width='$auth_column_width%' class='base'><input type='radio' name='AUTH_METHOD' value='none' $checked{'AUTH_METHOD'}{'none'} />$Lang::tr{'advproxy AUTH method none'}</td>
	<td width='$auth_column_width%' class='base'><input type='radio' name='AUTH_METHOD' value='ncsa' $checked{'AUTH_METHOD'}{'ncsa'} />$Lang::tr{'advproxy AUTH method ncsa'}</td>
	<td width='$auth_column_width%' class='base'><input type='radio' name='AUTH_METHOD' value='ident' $checked{'AUTH_METHOD'}{'ident'} />$Lang::tr{'advproxy AUTH method ident'}</td>
	<td width='$auth_column_width%' class='base'><input type='radio' name='AUTH_METHOD' value='ldap' $checked{'AUTH_METHOD'}{'ldap'} />$Lang::tr{'advproxy AUTH method ldap'}</td>
END

if ($HAVE_NTLM_AUTH) {
	print <<END;
	<td width='$auth_column_width%' class='base'><input type='radio' name='AUTH_METHOD' value='ntlm-auth' $checked{'AUTH_METHOD'}{'ntlm-auth'} />$Lang::tr{'advproxy AUTH method ntlm auth'}</td>
END
}

print <<END
	<td width='$auth_column_width%' class='base'><input type='radio' name='AUTH_METHOD' value='radius' $checked{'AUTH_METHOD'}{'radius'} />$Lang::tr{'advproxy AUTH method radius'}</td>
</tr>
</table>
END
;

if (!($proxysettings{'AUTH_METHOD'} eq 'none')) { if (!($proxysettings{'AUTH_METHOD'} eq 'ident')) { print <<END
<hr size='1'>
<table width='100%'>
<tr>
	<td colspan='4'><b>$Lang::tr{'advproxy AUTH global settings'}</b></td>
</tr>
<tr>
	<td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='30%'></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'advproxy AUTH number of auth processes'}:</td>
	<td><input type='text' name='AUTH_CHILDREN' value='$proxysettings{'AUTH_CHILDREN'}' size='5' /></td>
	<td colspan='2' rowspan= '6' valign='top' class='base'>
		<table cellpadding='0' cellspacing='0'>
			<tr>
			<td class='base'>$Lang::tr{'advproxy AUTH realm'}:</td>
			</tr>
			<tr>
				<!-- intentionally left empty -->
			</tr>
			<tr>
				<!-- intentionally left empty -->
			</tr>
			<tr>
			<td><input type='text' name='AUTH_REALM' value='$proxysettings{'AUTH_REALM'}' size='40' /></td>
			</tr>
			<tr>
				<!-- intentionally left empty -->
			</tr>
			<tr>
				<!-- intentionally left empty -->
			</tr>
			<tr>
			<td>$Lang::tr{'advproxy AUTH no auth'}:</td>
			</tr>
			<tr>
				<!-- intentionally left empty -->
			</tr>
			<tr>
				<!-- intentionally left empty -->
			</tr>
			<tr>
			<td><textarea name='DST_NOAUTH' cols='32' rows='6' wrap='off'>
END
;

print $proxysettings{'DST_NOAUTH'};

print <<END
</textarea></td>
		</tr>
		</table>
	</td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'advproxy AUTH auth cache TTL'}:</td>
	<td><input type='text' name='AUTH_CACHE_TTL' value='$proxysettings{'AUTH_CACHE_TTL'}' size='5' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'advproxy AUTH limit of IP addresses'}:</td>
	<td><input type='text' name='AUTH_MAX_USERIP' value='$proxysettings{'AUTH_MAX_USERIP'}' size='5' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'advproxy AUTH user IP cache TTL'}:</td>
	<td><input type='text' name='AUTH_IPCACHE_TTL' value='$proxysettings{'AUTH_IPCACHE_TTL'}' size='5' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'advproxy AUTH always required'}:</td>
	<td><input type='checkbox' name='AUTH_ALWAYS_REQUIRED' $checked{'AUTH_ALWAYS_REQUIRED'}{'on'} /></td>
</tr>
<tr>
	<td colspan='2'>&nbsp;</td>
</tr>
</table>
END
;
}

# ===================================================================
#  NCSA auth settings
# ===================================================================

if ($proxysettings{'AUTH_METHOD'} eq 'ncsa') {
print <<END
<hr size='1'>
<table width='100%'>
<tr>
	<td colspan='4'><b>$Lang::tr{'advproxy NCSA auth'}</b></td>
</tr>
<tr>
	<td width='25%' class='base'>$Lang::tr{'advproxy NCSA min password length'}:</td>
	<td width='20%'><input type='text' name='NCSA_MIN_PASS_LEN' value='$proxysettings{'NCSA_MIN_PASS_LEN'}' size='5' /></td>
	<td width='25%' class='base'>$Lang::tr{'advproxy NCSA redirector bypass'} \'$Lang::tr{'advproxy NCSA grp extended'}\':</td>
	<td width='20%'><input type='checkbox' name='NCSA_BYPASS_REDIR' $checked{'NCSA_BYPASS_REDIR'}{'on'} /></td>
</tr>
<tr>
	<td colspan='2'><br>&nbsp;<input type='submit' name='ACTION' value='$Lang::tr{'advproxy NCSA user management'}'></td>
	<td>&nbsp;</td>
	<td>&nbsp;</td>
</tr>
</table>
END
; }

# ===================================================================
#  IDENTD auth settings
# ===================================================================

if ($proxysettings{'AUTH_METHOD'} eq 'ident') {
print <<END
<hr size ='1'>
<table width='100%'>
<tr>
	<td colspan='4'><b>$Lang::tr{'advproxy IDENT identd settings'}</b></td>
</tr>
<tr>
	<td width='25%' class='base'>$Lang::tr{'advproxy IDENT required'}:</td>
	<td width='20%'><input type='checkbox' name='IDENT_REQUIRED' $checked{'IDENT_REQUIRED'}{'on'} /></td>
	<td width='25%' class='base'>$Lang::tr{'advproxy AUTH always required'}:</td>
	<td width='30%'><input type='checkbox' name='AUTH_ALWAYS_REQUIRED' $checked{'AUTH_ALWAYS_REQUIRED'}{'on'} /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'advproxy IDENT timeout'}:</td>
	<td><input type='text' name='IDENT_TIMEOUT' value='$proxysettings{'IDENT_TIMEOUT'}' size='5' /></td>
	<td>&nbsp;</td>
	<td>&nbsp;</td>
</tr>
<tr>
	<td colspan='2' class='base'>$Lang::tr{'advproxy IDENT aware hosts'}:</td>
	<td colspan='2' class='base'>$Lang::tr{'advproxy AUTH no auth'}:</td>
</tr>
<tr>
	<td colspan='2'><textarea name='IDENT_HOSTS' cols='32' rows='6' wrap='off'>
END
;
if (!$proxysettings{'IDENT_HOSTS'}) {
	if (&Header::green_used()) {
		print "$green_cidr\n";
	}

	if (&Header::blue_used()) {
		print "$blue_cidr\n";
	}
} else {
	print $proxysettings{'IDENT_HOSTS'};
}

print <<END
</textarea></td>
			<td colspan='2'><textarea name='DST_NOAUTH' cols='32' rows='6' wrap='off'>
END
;

print $proxysettings{'DST_NOAUTH'};

print <<END
</textarea></td>
</tr>
</table>
<hr size ='1'>
<table width='100%'>
<tr>
	<td colspan='4'><b>$Lang::tr{'advproxy IDENT user based access restrictions'}</b></td>
</tr>
<tr>
	<td width='25%' class='base'>$Lang::tr{'advproxy enabled'}:</td>
	<td width='20%'><input type='checkbox' name='IDENT_ENABLE_ACL' $checked{'IDENT_ENABLE_ACL'}{'on'} /></td>
	<td width='25%'>&nbsp;</td>
	<td width='30%'>&nbsp;</td>
</tr>
<tr>
	<td colspan='2'><input type='radio' name='IDENT_USER_ACL' value='positive' $checked{'IDENT_USER_ACL'}{'positive'} />
	$Lang::tr{'advproxy IDENT use positive access list'}:</td>
	<td colspan='2'><input type='radio' name='IDENT_USER_ACL' value='negative' $checked{'IDENT_USER_ACL'}{'negative'} />
	$Lang::tr{'advproxy IDENT use negative access list'}:</td>
</tr>
<tr>
	<td colspan='2'>$Lang::tr{'advproxy IDENT authorized users'}</td>
	<td colspan='2'>$Lang::tr{'advproxy IDENT unauthorized users'}</td>
</tr>
<tr>
	<td colspan='2'><textarea name='IDENT_ALLOW_USERS' cols='32' rows='6' wrap='off'>
END
; }

if ($proxysettings{'AUTH_METHOD'} eq 'ident') { print $proxysettings{'IDENT_ALLOW_USERS'}; }

if ($proxysettings{'AUTH_METHOD'} eq 'ident') { print <<END
</textarea></td>
	<td colspan='2'><textarea name='IDENT_DENY_USERS' cols='32' rows='6' wrap='off'>
END
; }

if ($proxysettings{'AUTH_METHOD'} eq 'ident') { print $proxysettings{'IDENT_DENY_USERS'}; }

if ($proxysettings{'AUTH_METHOD'} eq 'ident') { print <<END
</textarea></td>
</tr>
</table>
END
; }

# ===================================================================
#  NTLM-AUTH settings
# ===================================================================

if ($proxysettings{'AUTH_METHOD'} eq 'ntlm-auth') {
	print <<END;
		<hr size ='1'>
		<table width='100%'>
			<td width='20%' class='base'>$Lang::tr{'advproxy basic authentication'}:</td>
			<td width='40%'><input type='checkbox' name='NTLM_AUTH_BASIC' $checked{'NTLM_AUTH_BASIC'}{'on'} /></td>
			<td colspan='2'>&nbsp;</td>
		</table>

		<hr size='1' />

		<table width='100%'>
			<tr>
				<td colspan='4'><b>$Lang::tr{'advproxy group access control'}</b></td>
			</tr>
			<tr>
				<td width='20%' class='base'>$Lang::tr{'advproxy group required'}:</td>
				<td width='40%'><input type='text' name='NTLM_AUTH_GROUP' value='$proxysettings{'NTLM_AUTH_GROUP'}' size='37' /></td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
			</tr>
	</table>
END
}

# ===================================================================
#  LDAP auth settings
# ===================================================================

if ($proxysettings{'AUTH_METHOD'} eq 'ldap') {
print <<END
<hr size='1'>
<table width='100%'>
<tr>
	<td colspan='4'><b>$Lang::tr{'advproxy LDAP common settings'}</b></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'advproxy LDAP basedn'}:</td>
	<td><input type='text' name='LDAP_BASEDN' value='$proxysettings{'LDAP_BASEDN'}' size='37' /></td>
	<td class='base'>$Lang::tr{'advproxy LDAP type'}:</td>
	<td class='base'><select name='LDAP_TYPE'>
		<option value='ADS' $selected{'LDAP_TYPE'}{'ADS'}>$Lang::tr{'advproxy LDAP ADS'}</option>
		<option value='NDS' $selected{'LDAP_TYPE'}{'NDS'}>$Lang::tr{'advproxy LDAP NDS'}</option>
		<option value='V2' $selected{'LDAP_TYPE'}{'V2'}>$Lang::tr{'advproxy LDAP V2'}</option>
		<option value='V3' $selected{'LDAP_TYPE'}{'V3'}>$Lang::tr{'advproxy LDAP V3'}</option>
	</select></td>
</tr>
<tr>
	<td width='20%' class='base'>$Lang::tr{'advproxy LDAP server'}:</td>
	<td width='40%'><input type='text' name='LDAP_SERVER' value='$proxysettings{'LDAP_SERVER'}' size='14' /></td>
	<td width='20%' class='base'>$Lang::tr{'advproxy LDAP port'}:</td>
	<td><input type='text' name='LDAP_PORT' value='$proxysettings{'LDAP_PORT'}' size='3' /></td>
</tr>
</table>
<hr size ='1'>
<table width='100%'>
<tr>
	<td colspan='4'><b>$Lang::tr{'advproxy LDAP binddn settings'}</b></td>
</tr>
<tr>
	<td width='20%' class='base'>$Lang::tr{'advproxy LDAP binddn username'}:</td>
	<td width='40%'><input type='text' name='LDAP_BINDDN_USER' value='$proxysettings{'LDAP_BINDDN_USER'}' size='37' /></td>
	<td width='20%' class='base'>$Lang::tr{'advproxy LDAP binddn password'}:</td>
	<td><input type='password' name='LDAP_BINDDN_PASS' value='$proxysettings{'LDAP_BINDDN_PASS'}' size='14' /></td>
</tr>
</table>
<hr size ='1'>
<table width='100%'>
<tr>
	<td colspan='4'><b>$Lang::tr{'advproxy LDAP group access control'}</b></td>
</tr>
<tr>
	<td width='20%' class='base'>$Lang::tr{'advproxy LDAP group required'}:</td>
	<td width='40%'><input type='text' name='LDAP_GROUP' value='$proxysettings{'LDAP_GROUP'}' size='37' /></td>
	<td>&nbsp;</td>
	<td>&nbsp;</td>
</tr>
</table>
END
; }

# ===================================================================
#  RADIUS auth settings
# ===================================================================

if ($proxysettings{'AUTH_METHOD'} eq 'radius') {
print <<END
<hr size='1'>
<table width='100%'>
<tr>
	<td colspan='4'><b>$Lang::tr{'advproxy RADIUS radius settings'}</b></td>
</tr>
<tr>
	<td width='25%' class='base'>$Lang::tr{'advproxy RADIUS server'}:</td>
	<td width='20%'><input type='text' name='RADIUS_SERVER' value='$proxysettings{'RADIUS_SERVER'}' size='14' /></td>
	<td width='25%' class='base'>$Lang::tr{'advproxy RADIUS port'}:</td>
	<td width='30%'><input type='text' name='RADIUS_PORT' value='$proxysettings{'RADIUS_PORT'}' size='3' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'advproxy RADIUS identifier'}:</td>
	<td><input type='text' name='RADIUS_IDENTIFIER' value='$proxysettings{'RADIUS_IDENTIFIER'}' size='14' /></td>
	<td class='base'>$Lang::tr{'advproxy RADIUS secret'}:</td>
	<td><input type='password' name='RADIUS_SECRET' value='$proxysettings{'RADIUS_SECRET'}' size='14' /></td>
</tr>
</table>
<hr size ='1'>
<table width='100%'>
<tr>
	<td colspan='4'><b>$Lang::tr{'advproxy RADIUS user based access restrictions'}</b></td>
</tr>
<tr>
	<td width='25%' class='base'>$Lang::tr{'advproxy enabled'}:</td>
	<td width='20%'><input type='checkbox' name='RADIUS_ENABLE_ACL' $checked{'RADIUS_ENABLE_ACL'}{'on'} /></td>
	<td width='25%'>&nbsp;</td>
	<td width='30%'>&nbsp;</td>
</tr>
<tr>
	<td colspan='2'><input type='radio' name='RADIUS_USER_ACL' value='positive' $checked{'RADIUS_USER_ACL'}{'positive'} />
	$Lang::tr{'advproxy RADIUS use positive access list'}:</td>
	<td colspan='2'><input type='radio' name='RADIUS_USER_ACL' value='negative' $checked{'RADIUS_USER_ACL'}{'negative'} />
	$Lang::tr{'advproxy RADIUS use negative access list'}:</td>
</tr>
<tr>
	<td colspan='2'>$Lang::tr{'advproxy RADIUS authorized users'}</td>
	<td colspan='2'>$Lang::tr{'advproxy RADIUS unauthorized users'}</td>
</tr>
<tr>
	<td colspan='2'><textarea name='RADIUS_ALLOW_USERS' cols='32' rows='6' wrap='off'>
END
; }

if ($proxysettings{'AUTH_METHOD'} eq 'radius') { print $proxysettings{'RADIUS_ALLOW_USERS'}; }

if ($proxysettings{'AUTH_METHOD'} eq 'radius') { print <<END
</textarea></td>
	<td colspan='2'><textarea name='RADIUS_DENY_USERS' cols='32' rows='6' wrap='off'>
END
; }

if ($proxysettings{'AUTH_METHOD'} eq 'radius') { print $proxysettings{'RADIUS_DENY_USERS'}; }

if ($proxysettings{'AUTH_METHOD'} eq 'radius') { print <<END
</textarea></td>
</tr>
</table>
END
; }

# ===================================================================

}

print "<table>\n";

if ($proxysettings{'AUTH_METHOD'} eq 'none') {
print <<END
<td><input type='hidden' name='AUTH_CHILDREN'        value='$proxysettings{'AUTH_CHILDREN'}'></td>
<td><input type='hidden' name='AUTH_CACHE_TTL'       value='$proxysettings{'AUTH_CACHE_TTL'}' size='5' /></td>
<td><input type='hidden' name='AUTH_MAX_USERIP'      value='$proxysettings{'AUTH_MAX_USERIP'}' size='5' /></td>
<td><input type='hidden' name='AUTH_IPCACHE_TTL'     value='$proxysettings{'AUTH_IPCACHE_TTL'}' size='5' /></td>
<td><input type='hidden' name='AUTH_ALWAYS_REQUIRED' value='$proxysettings{'AUTH_ALWAYS_REQUIRED'}'></td>
<td><input type='hidden' name='AUTH_REALM'           value='$proxysettings{'AUTH_REALM'}'></td>
<td><input type='hidden' name='DST_NOAUTH'           value='$proxysettings{'DST_NOAUTH'}'></td>
END
; }

if ($proxysettings{'AUTH_METHOD'} eq 'ident') {
print <<END
<td><input type='hidden' name='AUTH_CHILDREN'        value='$proxysettings{'AUTH_CHILDREN'}'></td>
<td><input type='hidden' name='AUTH_CACHE_TTL'       value='$proxysettings{'AUTH_CACHE_TTL'}' size='5' /></td>
<td><input type='hidden' name='AUTH_MAX_USERIP'      value='$proxysettings{'AUTH_MAX_USERIP'}' size='5' /></td>
<td><input type='hidden' name='AUTH_IPCACHE_TTL'     value='$proxysettings{'AUTH_IPCACHE_TTL'}' size='5' /></td>
<td><input type='hidden' name='AUTH_REALM'           value='$proxysettings{'AUTH_REALM'}'></td>
END
; }

if (!($proxysettings{'AUTH_METHOD'} eq 'ncsa')) {
print <<END
<td><input type='hidden' name='NCSA_MIN_PASS_LEN' value='$proxysettings{'NCSA_MIN_PASS_LEN'}'></td>
<td><input type='hidden' name='NCSA_BYPASS_REDIR' value='$proxysettings{'NCSA_BYPASS_REDIR'}'></td>
END
; }

if (!($proxysettings{'AUTH_METHOD'} eq 'ident')) {
print <<END
<td><input type='hidden' name='IDENT_REQUIRED'    value='$proxysettings{'IDENT_REQUIRED'}'></td>
<td><input type='hidden' name='IDENT_TIMEOUT'     value='$proxysettings{'IDENT_TIMEOUT'}'></td>
<td><input type='hidden' name='IDENT_HOSTS'       value='$proxysettings{'IDENT_HOSTS'}'></td>
<td><input type='hidden' name='IDENT_ENABLE_ACL'  value='$proxysettings{'IDENT_ENABLE_ACL'}'></td>
<td><input type='hidden' name='IDENT_USER_ACL'    value='$proxysettings{'IDENT_USER_ACL'}'></td>
<td><input type='hidden' name='IDENT_ALLOW_USERS' value='$proxysettings{'IDENT_ALLOW_USERS'}'></td>
<td><input type='hidden' name='IDENT_DENY_USERS'  value='$proxysettings{'IDENT_DENY_USERS'}'></td>
END
; }

if (!($proxysettings{'AUTH_METHOD'} eq 'ldap')) {
print <<END
<td><input type='hidden' name='LDAP_BASEDN'      value='$proxysettings{'LDAP_BASEDN'}'></td>
<td><input type='hidden' name='LDAP_TYPE'        value='$proxysettings{'LDAP_TYPE'}'></td>
<td><input type='hidden' name='LDAP_SERVER'      value='$proxysettings{'LDAP_SERVER'}'></td>
<td><input type='hidden' name='LDAP_PORT'        value='$proxysettings{'LDAP_PORT'}'></td>
<td><input type='hidden' name='LDAP_BINDDN_USER' value='$proxysettings{'LDAP_BINDDN_USER'}'></td>
<td><input type='hidden' name='LDAP_BINDDN_PASS' value='$proxysettings{'LDAP_BINDDN_PASS'}'></td>
<td><input type='hidden' name='LDAP_GROUP'       value='$proxysettings{'LDAP_GROUP'}'></td>
END
; }

if (!($proxysettings{'AUTH_METHOD'} eq 'radius')) {
print <<END
<td><input type='hidden' name='RADIUS_SERVER'      value='$proxysettings{'RADIUS_SERVER'}'></td>
<td><input type='hidden' name='RADIUS_PORT'        value='$proxysettings{'RADIUS_PORT'}'></td>
<td><input type='hidden' name='RADIUS_IDENTIFIER'  value='$proxysettings{'RADIUS_IDENTIFIER'}'></td>
<td><input type='hidden' name='RADIUS_SECRET'      value='$proxysettings{'RADIUS_SECRET'}'></td>
<td><input type='hidden' name='RADIUS_ENABLE_ACL'  value='$proxysettings{'RADIUS_ENABLE_ACL'}'></td>
<td><input type='hidden' name='RADIUS_USER_ACL'    value='$proxysettings{'RADIUS_USER_ACL'}'></td>
<td><input type='hidden' name='RADIUS_ALLOW_USERS' value='$proxysettings{'RADIUS_ALLOW_USERS'}'></td>
<td><input type='hidden' name='RADIUS_DENY_USERS'  value='$proxysettings{'RADIUS_DENY_USERS'}'></td>
END
; }

print "</table>\n";

print <<END
<hr size='1'>
END
;

print <<END
<table width='100%'>
<tr>
	<td>&nbsp;</td>
	<td align='center'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
	<td align='center'><input type='submit' name='ACTION' value='$Lang::tr{'proxy reconfigure'}' /></td>
	<td align='center'><input type='submit' name='ACTION' value='$Lang::tr{'advproxy save and restart'}' /></td>
	<td align='center'><input type='submit' name='ACTION' value='$Lang::tr{'advproxy clear cache'}' /></td>
	<td>&nbsp;</td>
</tr>

</table>
<br />
<table width='100%'>
<tr>
	<td><img src='/blob.gif' align='top' alt='*' />&nbsp;<font class='base'>$Lang::tr{'required field'}</font></td>
	<td align='right'>&nbsp;</td>
</tr>
</table>
</form>
END
;

&Header::closebox();

} else {

# ===================================================================
#  NCSA user management
# ===================================================================

&Header::openbox('100%', 'left', "$Lang::tr{'advproxy NCSA auth'}");
print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='100%'>
<tr>
	<td colspan='4'><b>$Lang::tr{'advproxy NCSA user management'}</b></td>
</tr>
<tr>
	<td width='25%' class='base'>$Lang::tr{'advproxy NCSA username'}:</td>
	<td width='25%'><input type='text' name='NCSA_USERNAME' value='$proxysettings{'NCSA_USERNAME'}' size='12'
END
;
	if ($proxysettings{'ACTION'} eq $Lang::tr{'edit'}) { print " readonly='readonly' "; }
	print <<END
	 /></td>
	<td width='25%' class='base'>$Lang::tr{'advproxy NCSA group'}:</td>
	<td class='base'>
		<select name='NCSA_GROUP'>
		<option value='standard' $selected{'NCSA_GROUP'}{'standard'}>$Lang::tr{'advproxy NCSA grp standard'}</option>
		<option value='extended' $selected{'NCSA_GROUP'}{'extended'}>$Lang::tr{'advproxy NCSA grp extended'}</option>
		<option value='disabled' $selected{'NCSA_GROUP'}{'disabled'}>$Lang::tr{'advproxy NCSA grp disabled'}</option>
		</select>
	</td>

</tr>
<tr>
	<td class='base'>$Lang::tr{'advproxy NCSA password'}:</td>
	<td><input type='password' name='NCSA_PASS' value='$proxysettings{'NCSA_PASS'}' size='14' /></td>
	<td class='base'>$Lang::tr{'advproxy NCSA password confirm'}:</td>
	<td><input type='password' name='NCSA_PASS_CONFIRM' value='$proxysettings{'NCSA_PASS_CONFIRM'}' size='14' /></td>
</tr>
</table>
<br>
<table>
<tr>
	<td>&nbsp;</td>
	<td><input type='submit' name='SUBMIT' value='$ncsa_buttontext' /></td>
	<td><input type='hidden' name='ACTION' value='$Lang::tr{'add'}' /></td>
	<td><input type='hidden' name='NCSA_MIN_PASS_LEN' value='$proxysettings{'NCSA_MIN_PASS_LEN'}'></td>
END
;
	if ($proxysettings{'ACTION'} eq $Lang::tr{'edit'}) {
		print "<td><input type='reset' name='ACTION' value='$Lang::tr{'advproxy reset'}' /></td>\n";
	}

print <<END
	<td>&nbsp;</td>
	<td>&nbsp;</td>
	<td><input type='button' name='return2main' value='$Lang::tr{'advproxy back to main page'}' onClick='self.location.href="$ENV{'SCRIPT_NAME'}"'></td>
</tr>
</table>
</form>
<hr size='1'>
<table width='100%'>
<tr>
	<td><b>$Lang::tr{'advproxy NCSA user accounts'}:</b></td>
</tr>
</table>
<table width='100%' align='center'>
END
;

if (-e $extgrp)
{
	open(FILE, $extgrp); @grouplist = <FILE>; close(FILE);
	foreach $user (@grouplist) { chomp($user); push(@userlist,$user.":extended"); }
}
if (-e $stdgrp)
{
	open(FILE, $stdgrp); @grouplist = <FILE>; close(FILE);
	foreach $user (@grouplist) { chomp($user); push(@userlist,$user.":standard"); }
}
if (-e $disgrp)
{
	open(FILE, $disgrp); @grouplist = <FILE>; close(FILE);
	foreach $user (@grouplist) { chomp($user); push(@userlist,$user.":disabled"); }
}

@userlist = sort(@userlist);

# If the password file contains entries, print entries and action icons

if ( ! -z "$userdb" ) {
	print <<END
	<tr>
		<td width='30%' class='boldbase' align='center'><b><i>$Lang::tr{'advproxy NCSA username'}</i></b></td>
		<td width='30%' class='boldbase' align='center'><b><i>$Lang::tr{'advproxy NCSA group membership'}</i></b></td>
		<td class='boldbase' colspan='2' align='center'>&nbsp;</td>
	</tr>
END
;
	$id = 0;
	foreach $line (@userlist)
	{
		$id++;
		chomp($line);
		@temp = split(/:/,$line);
		if($proxysettings{'ACTION'} eq $Lang::tr{'edit'} && $proxysettings{'ID'} eq $line) {
			print "<tr bgcolor='$Header::colouryellow'>\n"; }
		elsif ($id % 2) {
			print "<tr bgcolor='$color{'color20'}'>\n"; }
		else {
			print "<tr bgcolor='$color{'color22'}'>\n"; }

		print <<END
		<td align='center'>$temp[0]</td>
		<td align='center'>
END
;
		if ($temp[1] eq 'standard') {
			print $Lang::tr{'advproxy NCSA grp standard'};
		} elsif ($temp[1] eq 'extended') {
			print $Lang::tr{'advproxy NCSA grp extended'};
		} elsif ($temp[1] eq 'disabled') {
			print $Lang::tr{'advproxy NCSA grp disabled'}; }
		print <<END
		</td>
		<td width='8%' align='center'>
		<form method='post' name='frma$id' action='$ENV{'SCRIPT_NAME'}'>
		<input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' title='$Lang::tr{'edit'}' alt='$Lang::tr{'edit'}' />
		<input type='hidden' name='ID' value='$line' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
		</form>
		</td>

		<td width='8%' align='center'>
		<form method='post' name='frmb$id' action='$ENV{'SCRIPT_NAME'}'>
		<input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' title='$Lang::tr{'remove'}' alt='$Lang::tr{'remove'}' />
		<input type='hidden' name='ID' value='$temp[0]' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'remove'}' />
		</form>
		</td>
	</tr>
END
;
	}

print <<END
</table>
<br>
<table>
<tr>
	<td class='boldbase'>&nbsp; <b>$Lang::tr{'legend'}:</b></td>
	<td>&nbsp; &nbsp; <img src='/images/edit.gif' alt='$Lang::tr{'edit'}' /></td>
	<td class='base'>$Lang::tr{'edit'}</td>
	<td>&nbsp; &nbsp; <img src='/images/delete.gif' alt='$Lang::tr{'remove'}' /></td>
	<td class='base'>$Lang::tr{'remove'}</td>
</tr>
END
;
} else {
	print <<END
	<tr>
		<td><i>$Lang::tr{'advproxy NCSA no accounts'}</i></td>
	</tr>
END
;
}

print <<END
</table>
END
;

&Header::closebox();

}

# ===================================================================

&Header::closebigbox();

&Header::closepage();

# -------------------------------------------------------------------

sub read_acls
{
	if (-e "$acl_src_subnets") {
		open(FILE,"$acl_src_subnets");
		delete $proxysettings{'SRC_SUBNETS'};
		while (<FILE>) { $proxysettings{'SRC_SUBNETS'} .= $_ };
		close(FILE);
	}
	if (-e "$acl_src_banned_ip") {
		open(FILE,"$acl_src_banned_ip");
		delete $proxysettings{'SRC_BANNED_IP'};
		while (<FILE>) { $proxysettings{'SRC_BANNED_IP'} .= $_ };
		close(FILE);
	}
	if (-e "$acl_src_banned_mac") {
		open(FILE,"$acl_src_banned_mac");
		delete $proxysettings{'SRC_BANNED_MAC'};
		while (<FILE>) { $proxysettings{'SRC_BANNED_MAC'} .= $_ };
		close(FILE);
	}
	if (-e "$acl_src_unrestricted_ip") {
		open(FILE,"$acl_src_unrestricted_ip");
		delete $proxysettings{'SRC_UNRESTRICTED_IP'};
		while (<FILE>) { $proxysettings{'SRC_UNRESTRICTED_IP'} .= $_ };
		close(FILE);
	}
	if (-e "$acl_src_unrestricted_mac") {
		open(FILE,"$acl_src_unrestricted_mac");
		delete $proxysettings{'SRC_UNRESTRICTED_MAC'};
		while (<FILE>) { $proxysettings{'SRC_UNRESTRICTED_MAC'} .= $_ };
		close(FILE);
	}
	if (-e "$acl_dst_nocache") {
		open(FILE,"$acl_dst_nocache");
		delete $proxysettings{'DST_NOCACHE'};
		while (<FILE>) { $proxysettings{'DST_NOCACHE'} .= $_ };
		close(FILE);
	}
	if (-e "$acl_dst_noauth") {
		open(FILE,"$acl_dst_noauth");
		delete $proxysettings{'DST_NOAUTH'};
		while (<FILE>) { $proxysettings{'DST_NOAUTH'} .= $_ };
		close(FILE);
	}
	if (-e "$acl_dst_noproxy_ip") {
		open(FILE,"$acl_dst_noproxy_ip");
		delete $proxysettings{'DST_NOPROXY_IP'};
		while (<FILE>) { $proxysettings{'DST_NOPROXY_IP'} .= $_ };
		close(FILE);
	}
	if (-e "$acl_dst_noproxy_url") {
		open(FILE,"$acl_dst_noproxy_url");
		delete $proxysettings{'DST_NOPROXY_URL'};
		while (<FILE>) { $proxysettings{'DST_NOPROXY_URL'} .= $_ };
		close(FILE);
	}
	if (-e "$acl_ports_safe") {
		open(FILE,"$acl_ports_safe");
		delete $proxysettings{'PORTS_SAFE'};
		while (<FILE>) { $proxysettings{'PORTS_SAFE'} .= $_ };
		close(FILE);
	}
	if (-e "$acl_ports_ssl") {
		open(FILE,"$acl_ports_ssl");
		delete $proxysettings{'PORTS_SSL'};
		while (<FILE>) { $proxysettings{'PORTS_SSL'} .= $_ };
		close(FILE);
	}
	if (-e "$mimetypes") {
		open(FILE,"$mimetypes");
		delete $proxysettings{'MIME_TYPES'};
		while (<FILE>) { $proxysettings{'MIME_TYPES'} .= $_ };
		close(FILE);
	}
	if (-e "$raddir/radauth.allowusers") {
		open(FILE,"$raddir/radauth.allowusers");
		delete $proxysettings{'RADIUS_ALLOW_USERS'};
		while (<FILE>) { $proxysettings{'RADIUS_ALLOW_USERS'} .= $_ };
		close(FILE);
	}
	if (-e "$raddir/radauth.denyusers") {
		open(FILE,"$raddir/radauth.denyusers");
		delete $proxysettings{'RADIUS_DENY_USERS'};
		while (<FILE>) { $proxysettings{'RADIUS_DENY_USERS'} .= $_ };
		close(FILE);
	}
	if (-e "$identdir/identauth.allowusers") {
		open(FILE,"$identdir/identauth.allowusers");
		delete $proxysettings{'IDENT_ALLOW_USERS'};
		while (<FILE>) { $proxysettings{'IDENT_ALLOW_USERS'} .= $_ };
		close(FILE);
	}
	if (-e "$identdir/identauth.denyusers") {
		open(FILE,"$identdir/identauth.denyusers");
		delete $proxysettings{'IDENT_DENY_USERS'};
		while (<FILE>) { $proxysettings{'IDENT_DENY_USERS'} .= $_ };
		close(FILE);
	}
	if (-e "$identhosts") {
		open(FILE,"$identhosts");
		delete $proxysettings{'IDENT_HOSTS'};
		while (<FILE>) { $proxysettings{'IDENT_HOSTS'} .= $_ };
		close(FILE);
	}
	if (-e "$cre_groups") {
		open(FILE,"$cre_groups");
		delete $proxysettings{'CRE_GROUPS'};
		while (<FILE>) { $proxysettings{'CRE_GROUPS'} .= $_ };
		close(FILE);
	}
	if (-e "$cre_svhosts") {
		open(FILE,"$cre_svhosts");
		delete $proxysettings{'CRE_SVHOSTS'};
		while (<FILE>) { $proxysettings{'CRE_SVHOSTS'} .= $_ };
		close(FILE);
	}
}

# -------------------------------------------------------------------

sub check_acls
{
	@temp = split(/\n/,$proxysettings{'PORTS_SAFE'});
	undef $proxysettings{'PORTS_SAFE'};
	foreach (@temp)
	{
		s/^\s+//g; s/\s+$//g;
		if ($_)
		{
			$line = $_;
			if (/^[^#]+\s+#\sSquids\sport/) { s/(^[^#]+)(\s+#\sSquids\sport)/$proxysettings{'PROXY_PORT'}\2/; $line=$_; }
			s/#.*//g; s/\s+//g;
			if (/.*-.*-.*/) { $errormessage = $Lang::tr{'advproxy errmsg invalid destination port'}; }
			@templist = split(/-/);
			foreach (@templist) { unless (&General::validport($_)) { $errormessage = $Lang::tr{'advproxy errmsg invalid destination port'}; } }
			$proxysettings{'PORTS_SAFE'} .= $line."\n";
		}
	}

	@temp = split(/\n/,$proxysettings{'PORTS_SSL'});
	undef $proxysettings{'PORTS_SSL'};
	foreach (@temp)
	{
		s/^\s+//g; s/\s+$//g;
		if ($_)
		{
			$line = $_;
			s/#.*//g; s/\s+//g;
			if (/.*-.*-.*/) { $errormessage = $Lang::tr{'advproxy errmsg invalid destination port'}; }
			@templist = split(/-/);
			foreach (@templist) { unless (&General::validport($_)) { $errormessage = $Lang::tr{'advproxy errmsg invalid destination port'}; } }
			$proxysettings{'PORTS_SSL'} .= $line."\n";
		}
	}

	@temp = split(/\n/,$proxysettings{'DST_NOCACHE'});
	undef $proxysettings{'DST_NOCACHE'};
	foreach (@temp)
	{
		s/^\s+//g;
		unless (/^#/) { s/\s+//g; }
		if ($_)
		{
			if (/^\./) { $_ = '*'.$_; }
			unless (&General::validwildcarddomainname($_)) { $errormessage = $Lang::tr{'advproxy errmsg invalid url'} . ": " . &Header::escape($_); }
			$proxysettings{'DST_NOCACHE'} .= $_."\n";
		}
	}

	@temp = split(/\n/,$proxysettings{'SRC_SUBNETS'});
	undef $proxysettings{'SRC_SUBNETS'};
	foreach (@temp)
	{
		s/^\s+//g; s/\s+$//g;
		if ($_)
		{
			unless (&Network::check_subnet($_)) { $errormessage = $Lang::tr{'advproxy errmsg invalid ip or mask'} . ": $_"; }
			$proxysettings{'SRC_SUBNETS'} .= $_."\n";
		}
	}

	@temp = split(/\n/,$proxysettings{'SRC_BANNED_IP'});
	undef $proxysettings{'SRC_BANNED_IP'};
	foreach (@temp)
	{
		s/^\s+//g; s/\s+$//g;
		if ($_)
		{
			unless (&General::validipormask($_)) { $errormessage = $Lang::tr{'advproxy errmsg invalid ip or mask'}; }
			$proxysettings{'SRC_BANNED_IP'} .= $_."\n";
		}
	}

	@temp = split(/\n/,$proxysettings{'SRC_BANNED_MAC'});
	undef $proxysettings{'SRC_BANNED_MAC'};
	foreach (@temp)
	{
		s/^\s+//g; s/\s+$//g; s/-/:/g;
		if ($_)
		{
			unless (&General::validmac($_)) { $errormessage = $Lang::tr{'advproxy errmsg invalid mac'}; }
			$proxysettings{'SRC_BANNED_MAC'} .= $_."\n";
		}
	}

	@temp = split(/\n/,$proxysettings{'SRC_UNRESTRICTED_IP'});
	undef $proxysettings{'SRC_UNRESTRICTED_IP'};
	foreach (@temp)
	{
		s/^\s+//g; s/\s+$//g;
		if ($_)
		{
			unless (&General::validipormask($_)) { $errormessage = $Lang::tr{'advproxy errmsg invalid ip or mask'}; }
			$proxysettings{'SRC_UNRESTRICTED_IP'} .= $_."\n";
		}
	}

	@temp = split(/\n/,$proxysettings{'SRC_UNRESTRICTED_MAC'});
	undef $proxysettings{'SRC_UNRESTRICTED_MAC'};
	foreach (@temp)
	{
		s/^\s+//g; s/\s+$//g; s/-/:/g;
		if ($_)
		{
			unless (&General::validmac($_)) { $errormessage = $Lang::tr{'advproxy errmsg invalid mac'}; }
			$proxysettings{'SRC_UNRESTRICTED_MAC'} .= $_."\n";
		}
	}

	@temp = split(/\n/,$proxysettings{'DST_NOAUTH'});
	undef $proxysettings{'DST_NOAUTH'};
	foreach (@temp)
	{
		s/^\s+//g;
		unless (/^#/) { s/\s+//g; }
		if ($_)
		{
			if (/^\./) { $_ = '*'.$_; }
			$proxysettings{'DST_NOAUTH'} .= $_."\n";
		}
	}

	@temp = split(/\n/,$proxysettings{'DST_NOPROXY_IP'});
	undef $proxysettings{'DST_NOPROXY_IP'};
	foreach (@temp)
	{
			s/^\s+//g; s/\s+$//g;
			if ($_)
			{
					unless (&General::validipormask($_)) { $errormessage = $Lang::tr{'advproxy errmsg wpad invalid ip or mask'}; }
					$proxysettings{'DST_NOPROXY_IP'} .= $_."\n";
			}
	}

	@temp = split(/\n/,$proxysettings{'DST_NOPROXY_URL'});
	undef $proxysettings{'DST_NOPROXY_URL'};
	foreach (@temp)
	{
			s/^\s+//g;
			unless (/^#/) { s/\s+//g; }
			if ($_)
			{
					if (/^\./) { $_ = '*'.$_; }
					unless (&General::validwildcarddomainname($_)) { $errormessage = $Lang::tr{'advproxy errmsg invalid url'} . ": " . &Header::escape($_); }
					$proxysettings{'DST_NOPROXY_URL'} .= $_."\n";
			}
	}

	if (($proxysettings{'NTLM_ENABLE_ACL'} eq 'on') && ($proxysettings{'NTLM_USER_ACL'} eq 'positive'))
	{
		@temp = split(/\n/,$proxysettings{'NTLM_ALLOW_USERS'});
		undef $proxysettings{'NTLM_ALLOW_USERS'};
		foreach (@temp)
		{
			s/^\s+//g; s/\s+$//g;
			if ($_) { $proxysettings{'NTLM_ALLOW_USERS'} .= $_."\n"; }
		}
		if ($proxysettings{'NTLM_ALLOW_USERS'} eq '') { $errormessage = $Lang::tr{'advproxy errmsg acl cannot be empty'}; }
	}

	if (($proxysettings{'NTLM_ENABLE_ACL'} eq 'on') && ($proxysettings{'NTLM_USER_ACL'} eq 'negative'))
	{
		@temp = split(/\n/,$proxysettings{'NTLM_DENY_USERS'});
		undef $proxysettings{'NTLM_DENY_USERS'};
		foreach (@temp)
		{
			s/^\s+//g; s/\s+$//g;
			if ($_) { $proxysettings{'NTLM_DENY_USERS'} .= $_."\n"; }
		}
		if ($proxysettings{'NTLM_DENY_USERS'} eq '') { $errormessage = $Lang::tr{'advproxy errmsg acl cannot be empty'}; }
	}

	if (($proxysettings{'IDENT_ENABLE_ACL'} eq 'on') && ($proxysettings{'IDENT_USER_ACL'} eq 'positive'))
	{
		@temp = split(/\n/,$proxysettings{'IDENT_ALLOW_USERS'});
		undef $proxysettings{'IDENT_ALLOW_USERS'};
		foreach (@temp)
		{
			s/^\s+//g; s/\s+$//g;
			if ($_) { $proxysettings{'IDENT_ALLOW_USERS'} .= $_."\n"; }
		}
		if ($proxysettings{'IDENT_ALLOW_USERS'} eq '') { $errormessage = $Lang::tr{'advproxy errmsg acl cannot be empty'}; }
	}

	if (($proxysettings{'IDENT_ENABLE_ACL'} eq 'on') && ($proxysettings{'IDENT_USER_ACL'} eq 'negative'))
	{
		@temp = split(/\n/,$proxysettings{'IDENT_DENY_USERS'});
		undef $proxysettings{'IDENT_DENY_USERS'};
		foreach (@temp)
		{
			s/^\s+//g; s/\s+$//g;
			if ($_) { $proxysettings{'IDENT_DENY_USERS'} .= $_."\n"; }
		}
		if ($proxysettings{'IDENT_DENY_USERS'} eq '') { $errormessage = $Lang::tr{'advproxy errmsg acl cannot be empty'}; }
	}

	if (($proxysettings{'RADIUS_ENABLE_ACL'} eq 'on') && ($proxysettings{'RADIUS_USER_ACL'} eq 'positive'))
	{
		@temp = split(/\n/,$proxysettings{'RADIUS_ALLOW_USERS'});
		undef $proxysettings{'RADIUS_ALLOW_USERS'};
		foreach (@temp)
		{
			s/^\s+//g; s/\s+$//g;
			if ($_) { $proxysettings{'RADIUS_ALLOW_USERS'} .= $_."\n"; }
		}
		if ($proxysettings{'RADIUS_ALLOW_USERS'} eq '') { $errormessage = $Lang::tr{'advproxy errmsg acl cannot be empty'}; }
	}

	if (($proxysettings{'RADIUS_ENABLE_ACL'} eq 'on') && ($proxysettings{'RADIUS_USER_ACL'} eq 'negative'))
	{
		@temp = split(/\n/,$proxysettings{'RADIUS_DENY_USERS'});
		undef $proxysettings{'RADIUS_DENY_USERS'};
		foreach (@temp)
		{
			s/^\s+//g; s/\s+$//g;
			if ($_) { $proxysettings{'RADIUS_DENY_USERS'} .= $_."\n"; }
		}
		if ($proxysettings{'RADIUS_DENY_USERS'} eq '') { $errormessage = $Lang::tr{'advproxy errmsg acl cannot be empty'}; }
	}

	@temp = split(/\n/,$proxysettings{'IDENT_HOSTS'});
	undef $proxysettings{'IDENT_HOSTS'};
	foreach (@temp)
	{
		s/^\s+//g; s/\s+$//g;
		if ($_)
		{
			unless (&General::validipormask($_)) { $errormessage = $Lang::tr{'advproxy errmsg invalid ip or mask'}; }
			$proxysettings{'IDENT_HOSTS'} .= $_."\n";
		}
	}

	@temp = split(/\n/,$proxysettings{'CRE_SVHOSTS'});
	undef $proxysettings{'CRE_SVHOSTS'};
	foreach (@temp)
	{
		s/^\s+//g; s/\s+$//g;
		if ($_)
		{
			unless (&General::validipormask($_)) { $errormessage = $Lang::tr{'advproxy errmsg invalid ip or mask'}; }
			$proxysettings{'CRE_SVHOSTS'} .= $_."\n";
		}
	}
}

# -------------------------------------------------------------------

sub write_acls
{
	open(FILE, ">$acl_src_subnets");
	flock(FILE, 2);
	if (!$proxysettings{'SRC_SUBNETS'})
	{
		if (&Header::green_used()) {
			print FILE "$green_cidr\n";
		}

		if (&Header::blue_used()) {
			print FILE "$blue_cidr\n";
		}
	} else { print FILE $proxysettings{'SRC_SUBNETS'}; }
	close(FILE);

	open(FILE, ">$acl_src_banned_ip");
	flock(FILE, 2);
	print FILE $proxysettings{'SRC_BANNED_IP'};
	close(FILE);

	open(FILE, ">$acl_src_banned_mac");
	flock(FILE, 2);
	print FILE $proxysettings{'SRC_BANNED_MAC'};
	close(FILE);

	open(FILE, ">$acl_src_unrestricted_ip");
	flock(FILE, 2);
	print FILE $proxysettings{'SRC_UNRESTRICTED_IP'};
	close(FILE);

	open(FILE, ">$acl_src_unrestricted_mac");
	flock(FILE, 2);
	print FILE $proxysettings{'SRC_UNRESTRICTED_MAC'};
	close(FILE);

	open(FILE, ">$acl_dst_noauth");
	flock(FILE, 2);
	print FILE $proxysettings{'DST_NOAUTH'};
	close(FILE);

	open(FILE, ">$acl_dst_noproxy_ip");
	flock(FILE, 2);
	print FILE $proxysettings{'DST_NOPROXY_IP'};
	close(FILE);

	open(FILE, ">$acl_dst_noproxy_url");
	flock(FILE, 2);
	print FILE $proxysettings{'DST_NOPROXY_URL'};
	close(FILE);

	open(FILE, ">$acl_dst_noauth_net");
	close(FILE);
	open(FILE, ">$acl_dst_noauth_dom");
	close(FILE);
	open(FILE, ">$acl_dst_noauth_url");
	close(FILE);

	@temp = split(/\n/,$proxysettings{'DST_NOAUTH'});
	foreach(@temp)
	{
		unless (/^#/)
		{
			if (/^\*\.\w/)
			{
				s/^\*//;
				open(FILE, ">>$acl_dst_noauth_dom");
				flock(FILE, 2);
				print FILE "$_\n";
				close(FILE);
			}
			elsif (&General::validipormask($_))
			{
				open(FILE, ">>$acl_dst_noauth_net");
				flock(FILE, 2);
				print FILE "$_\n";
				close(FILE);
			}
			elsif (/\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?-\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?/)
			{
				open(FILE, ">>$acl_dst_noauth_net");
				flock(FILE, 2);
				print FILE "$_\n";
				close(FILE);
			}
			else
			{
				open(FILE, ">>$acl_dst_noauth_url");
				flock(FILE, 2);
				if (/^[fh]tt?ps?:\/\//) { print FILE "$_\n"; } else { print FILE "^[fh]tt?ps?://$_\n"; }
				close(FILE);
			}
		}
	}

	open(FILE, ">$acl_dst_nocache");
	flock(FILE, 2);
	print FILE $proxysettings{'DST_NOCACHE'};
	close(FILE);

	open(FILE, ">$acl_dst_nocache_net");
	close(FILE);
	open(FILE, ">$acl_dst_nocache_dom");
	close(FILE);
	open(FILE, ">$acl_dst_nocache_url");
	close(FILE);

	@temp = split(/\n/,$proxysettings{'DST_NOCACHE'});
	foreach(@temp)
	{
		unless (/^#/)
		{
			if (/^\*\.\w/)
			{
				s/^\*//;
				open(FILE, ">>$acl_dst_nocache_dom");
				flock(FILE, 2);
				print FILE "$_\n";
				close(FILE);
			}
			elsif (&General::validipormask($_))
			{
				open(FILE, ">>$acl_dst_nocache_net");
				flock(FILE, 2);
				print FILE "$_\n";
				close(FILE);
			}
			elsif (/\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?-\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?/)
			{
				open(FILE, ">>$acl_dst_nocache_net");
				flock(FILE, 2);
				print FILE "$_\n";
				close(FILE);
			}
			else
			{
				open(FILE, ">>$acl_dst_nocache_url");
				flock(FILE, 2);
				if (/^[fh]tt?ps?:\/\//) { print FILE "$_\n"; } else { print FILE "^[fh]tt?ps?://$_\n"; }
				close(FILE);
			}
		}
	}

	open(FILE, ">$acl_ports_safe");
	flock(FILE, 2);
	if (!$proxysettings{'PORTS_SAFE'}) { print FILE $def_ports_safe; } else { print FILE $proxysettings{'PORTS_SAFE'}; }
	close(FILE);

	open(FILE, ">$acl_ports_ssl");
	flock(FILE, 2);
	if (!$proxysettings{'PORTS_SSL'}) { print FILE $def_ports_ssl; } else { print FILE $proxysettings{'PORTS_SSL'}; }
	close(FILE);

	if (-s $throttled_urls)
	{
		open(URLFILE, $throttled_urls);
		@temp = <URLFILE>;
		close(URLFILE);
		foreach (@temp) { print FILE; }
	}
	close(FILE);

	open(FILE, ">$mimetypes");
	flock(FILE, 2);
	print FILE $proxysettings{'MIME_TYPES'};
	close(FILE);

	open(FILE, ">$raddir/radauth.allowusers");
	flock(FILE, 2);
	print FILE $proxysettings{'RADIUS_ALLOW_USERS'};
	close(FILE);

	open(FILE, ">$raddir/radauth.denyusers");
	flock(FILE, 2);
	print FILE $proxysettings{'RADIUS_DENY_USERS'};
	close(FILE);

	open(FILE, ">$identdir/identauth.allowusers");
	flock(FILE, 2);
	print FILE $proxysettings{'IDENT_ALLOW_USERS'};
	close(FILE);

	open(FILE, ">$identdir/identauth.denyusers");
	flock(FILE, 2);
	print FILE $proxysettings{'IDENT_DENY_USERS'};
	close(FILE);

	open(FILE, ">$identhosts");
	flock(FILE, 2);
	print FILE $proxysettings{'IDENT_HOSTS'};
	close(FILE);

	open(FILE, ">$cre_groups");
	flock(FILE, 2);
	print FILE $proxysettings{'CRE_GROUPS'};
	close(FILE);

	open(FILE, ">$cre_svhosts");
	flock(FILE, 2);
	print FILE $proxysettings{'CRE_SVHOSTS'};
	close(FILE);
}

# -------------------------------------------------------------------

sub writepacfile
{
	my %vpnconfig=();
	my %ovpnconfig=();
	&General::readhasharray("${General::swroot}/vpn/config", \%vpnconfig);
	&General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%ovpnconfig);
	open(FILE, ">/srv/web/ipfire/html/proxy.pac");
	flock(FILE, 2);
	print FILE "function FindProxyForURL(url, host)\n";
	print FILE "{\n";
	if (($proxysettings{'ENABLE'} eq 'on') || ($proxysettings{'ENABLE_BLUE'} eq 'on'))
	{
		print FILE <<END
if (
     (isPlainHostName(host)) ||
     (isInNet(host, "127.0.0.1", "255.0.0.0")) ||
END
;

	if ($netsettings{'GREEN_DEV'}) {
		print FILE "     (isInNet(host, \"$netsettings{'GREEN_NETADDRESS'}\", \"$netsettings{'GREEN_NETMASK'}\")) ||\n";
	}

	if (&Header::blue_used() && $netsettings{'BLUE_DEV'}) {
		print FILE "     (isInNet(host, \"$netsettings{'BLUE_NETADDRESS'}\", \"$netsettings{'BLUE_NETMASK'}\")) ||\n";
	}

	if (&Header::orange_used() && $netsettings{'ORANGE_DEV'}) {
		print FILE "     (isInNet(host, \"$netsettings{'ORANGE_NETADDRESS'}\", \"$netsettings{'ORANGE_NETMASK'}\")) ||\n";
	}

	# Additional exceptions for URLs
	# The file has to be created by the user and should contain one entry per line
	# Line-Format: <URL incl. wildcards>
	# e.g. *.ipfire.org*
	if (-s "$acl_dst_noproxy_url") {
		undef @templist;

		open(NOPROXY,"$acl_dst_noproxy_url");
		@templist = <NOPROXY>;
		close(NOPROXY);
		chomp (@templist);

		foreach (@templist)
		{
			print FILE "     (shExpMatch(url, \"$_\")) ||\n";
		}
	}

	# Additional exceptions for Subnets
	# The file has to be created by the user and should contain one entry per line
	# Line-Format: <IP>/<SUBNET MASK>
	# e.g. 192.168.0.0/255.255.255.0
	if (-s "$acl_dst_noproxy_ip") {
		undef @templist;

		open(NOPROXY,"$acl_dst_noproxy_ip");
		@templist = <NOPROXY>;
		close(NOPROXY);
		chomp (@templist);

		foreach (@templist)
		{
			@temp = split(/\//);
			print FILE "     (isInNet(host, \"$temp[0]\", \"$temp[1]\")) ||\n";
		}
	}

	foreach my $key (sort { uc($vpnconfig{$a}[1]) cmp uc($vpnconfig{$b}[1]) } keys %vpnconfig) {
		if ($vpnconfig{$key}[0] eq 'on' && $vpnconfig{$key}[3] ne 'host') {
			my @networks = split(/\|/, $vpnconfig{$key}[11]);
			foreach my $network (@networks) {
				my ($vpnip, $vpnsub) = split("/", $network);
				$vpnsub = &Network::convert_prefix2netmask($vpnsub) || $vpnsub;
				next if ($vpnip eq "0.0.0.0" || $vpnsub eq "0.0.0.0");
				print FILE "     (isInNet(host, \"$vpnip\", \"$vpnsub\")) ||\n";
			}
		}
	}

	foreach my $key (sort { uc($ovpnconfig{$a}[1]) cmp uc($ovpnconfig{$b}[1]) } keys %ovpnconfig) {
		if ($ovpnconfig{$key}[0] eq 'on' && $ovpnconfig{$key}[3] ne 'host') {
			my @networks = split(/\|/, $ovpnconfig{$key}[11]);
			foreach my $network (@networks) {
				my ($vpnip, $vpnsub) = split("/", $network);
				$vpnsub = &Network::convert_prefix2netmask($vpnsub) || $vpnsub;
				next if ($vpnip eq "0.0.0.0" || $vpnsub eq "0.0.0.0");
				print FILE "     (isInNet(host, \"$vpnip\", \"$vpnsub\")) ||\n";
			}
		}
	}

	print FILE <<END
     (isInNet(host, "169.254.0.0", "255.255.0.0"))
   )
     return "DIRECT";

 else

END
;
		if ($proxysettings{'ENABLE'} eq 'on')
		{
			print FILE "if (\n";
			print FILE "     (isInNet(myIpAddress(), \"$netsettings{'GREEN_NETADDRESS'}\", \"$netsettings{'GREEN_NETMASK'}\"))";

			undef @templist;
			if (-e "$acl_src_subnets") {
				open(SUBNETS,"$acl_src_subnets");
				@templist = <SUBNETS>;
				close(SUBNETS);
			}

			foreach (@templist)
			{
				@temp = split(/\//);
				if (
					($temp[0] ne $netsettings{'GREEN_NETADDRESS'}) && ($temp[1] ne $netsettings{'GREEN_NETMASK'}) &&
					($temp[0] ne $netsettings{'BLUE_NETADDRESS'}) && ($temp[1] ne $netsettings{'BLUE_NETMASK'})
					)
				{
					chomp $temp[1];
					my $tempmask = &Network::convert_prefix2netmask($temp[1]);
					print FILE " ||\n     (isInNet(myIpAddress(), \"$temp[0]\", \"$tempmask\"))";
				}
			}

			print FILE "\n";

			print FILE <<END
   )
     return "PROXY $netsettings{'GREEN_ADDRESS'}:$proxysettings{'PROXY_PORT'}";
END
;
		}
		if (($proxysettings{'ENABLE'} eq 'on') && ($proxysettings{'ENABLE_BLUE'} eq 'on') && ($netsettings{'BLUE_DEV'}))
		{
			print FILE "\n else\n\n";
		}
		if (($netsettings{'BLUE_DEV'}) && ($proxysettings{'ENABLE_BLUE'} eq 'on'))
		{
			print FILE <<END
if (
     (isInNet(myIpAddress(), "$netsettings{'BLUE_NETADDRESS'}", "$netsettings{'BLUE_NETMASK'}"))
   )
     return "PROXY $netsettings{'BLUE_ADDRESS'}:$proxysettings{'PROXY_PORT'}";
END
;
		}
	}
	print FILE "}\n";
	close(FILE);
}

# -------------------------------------------------------------------

sub writeconfig
{
	my $authrealm;
	my $delaypools;

	if ($proxysettings{'THROTTLING_GREEN_TOTAL'} +
	    $proxysettings{'THROTTLING_GREEN_HOST'}  +
	    $proxysettings{'THROTTLING_BLUE_TOTAL'}  +
	    $proxysettings{'THROTTLING_BLUE_HOST'} gt 0)
	{
		$delaypools = 1; } else { $delaypools = 0;
	}

	if ($proxysettings{'AUTH_REALM'} eq '')
	{
		$authrealm = "IPFire Advanced Proxy Server";
	} else {
		$authrealm = $proxysettings{'AUTH_REALM'};
	}

	$_ = $proxysettings{'UPSTREAM_PROXY'};
        my ($remotehost, $remoteport) = split(/:/,$_);

	if ($remoteport eq '') { $remoteport = 80; }

	open(FILE, ">${General::swroot}/proxy/squid.conf");
	flock(FILE, 2);
	print FILE <<END
# Do not modify '${General::swroot}/proxy/squid.conf' directly since any changes
# you make will be overwritten whenever you resave proxy settings using the
# web interface!
#
# Instead, modify the file '$acl_include' and
# then restart the proxy service using the web interface. Changes made to the
# 'include.acl' file will propagate to the 'squid.conf' file at that time.

shutdown_lifetime 5 seconds
icp_port 0
httpd_suppress_version_string on

END
	;

	# Include file with user defined settings.
	if (-e "/etc/squid/squid.conf.pre.local") {
		print FILE "include /etc/squid/squid.conf.pre.local\n\n";
	}

	if (&Header::green_used()) {
		print FILE "http_port $netsettings{'GREEN_ADDRESS'}:$proxysettings{'PROXY_PORT'}";
	} else {
		print FILE "http_port 0.0.0.0:$proxysettings{'PROXY_PORT'}";
	}
	if ($proxysettings{'NO_CONNECTION_AUTH'} eq 'on') { print FILE " no-connection-auth" }
	print FILE "\n";

	if (&Header::green_used() && $proxysettings{'TRANSPARENT'} eq 'on') {
		print FILE "http_port $netsettings{'GREEN_ADDRESS'}:$proxysettings{'TRANSPARENT_PORT'} intercept";
		if ($proxysettings{'NO_CONNECTION_AUTH'} eq 'on') { print FILE " no-connection-auth" }
		print FILE "\n";
	}

	if ($netsettings{'BLUE_DEV'} && $proxysettings{'ENABLE_BLUE'} eq 'on') {
		print FILE "http_port $netsettings{'BLUE_ADDRESS'}:$proxysettings{'PROXY_PORT'}";
		if ($proxysettings{'NO_CONNECTION_AUTH'} eq 'on') { print FILE " no-connection-auth" }
		print FILE "\n";

		if ($proxysettings{'TRANSPARENT_BLUE'} eq 'on') {
			print FILE "http_port $netsettings{'BLUE_ADDRESS'}:$proxysettings{'TRANSPARENT_PORT'} intercept";
			if ($proxysettings{'NO_CONNECTION_AUTH'} eq 'on') { print FILE " no-connection-auth" }
			print FILE "\n";
		}
	}

	if (($proxysettings{'CACHE_SIZE'} > 0) || ($proxysettings{'CACHE_MEM'} > 0))
	{
		print FILE "\n";

		if (!-z $acl_dst_nocache_dom) {
			print FILE "acl no_cache_domains dstdomain \"$acl_dst_nocache_dom\"\n";
			print FILE "cache deny no_cache_domains\n";
		}
		if (!-z $acl_dst_nocache_net) {
			print FILE "acl no_cache_ipaddr dst \"$acl_dst_nocache_net\"\n";
			print FILE "cache deny no_cache_ipaddr\n";
		}
		if (!-z $acl_dst_nocache_url) {
			print FILE "acl no_cache_hosts url_regex -i \"$acl_dst_nocache_url\"\n";
			print FILE "cache deny no_cache_hosts\n";
		}
	}

	print FILE <<END

cache_effective_user squid
umask 022

pid_filename /var/run/squid.pid

cache_mem $proxysettings{'CACHE_MEM'} MB
END
	;
	print FILE "error_directory $errordir/$proxysettings{'ERR_LANGUAGE'}\n\n";

	if ($proxysettings{'OFFLINE_MODE'} eq 'on') {  print FILE "offline_mode on\n\n"; }
	if ($proxysettings{'CACHE_DIGESTS'} eq 'on') {  print FILE "digest_generation on\n\n"; } else {  print FILE "digest_generation off\n\n"; }

	if ((!($proxysettings{'MEM_POLICY'} eq 'LRU')) || (!($proxysettings{'CACHE_POLICY'} eq 'LRU')))
	{
		if (!($proxysettings{'MEM_POLICY'} eq 'LRU'))
		{
			print FILE "memory_replacement_policy $proxysettings{'MEM_POLICY'}\n";
		}
		if (!($proxysettings{'CACHE_POLICY'} eq 'LRU'))
		{
			print FILE "cache_replacement_policy $proxysettings{'CACHE_POLICY'}\n";
		}
		print FILE "\n";
	}

	open (PORTS,"$acl_ports_ssl");
	my @ssl_ports = <PORTS>;
	close PORTS;

	if (@ssl_ports) {
		foreach (@ssl_ports) {
			print FILE "acl SSL_ports port $_";
		}
	}

	open (PORTS,"$acl_ports_safe");
	my @safe_ports = <PORTS>;
	close PORTS;

	if (@safe_ports) {
		foreach (@safe_ports) {
			print FILE "acl Safe_ports port $_";
		}
	}

	print FILE <<END;
acl IPFire_ips dst 127.0.0.1
acl IPFire_http  port $http_port
acl IPFire_https port $https_port
acl IPFire_networks         src "$acl_src_subnets"
acl IPFire_servers          dst "$acl_src_subnets"
END
	if (&Header::green_used()) {
		print FILE <<END;
acl IPFire_ips              dst $netsettings{'GREEN_ADDRESS'}
acl IPFire_green_network    src $green_cidr
acl IPFire_green_servers    dst $green_cidr
END
	}
	if ($netsettings{'BLUE_DEV'}) { print FILE "acl IPFire_blue_network     src $blue_cidr\n"; }
	if ($netsettings{'BLUE_DEV'}) { print FILE "acl IPFire_blue_servers     dst $blue_cidr\n"; }
	if (!-z $acl_src_banned_ip) { print FILE "acl IPFire_banned_ips       src \"$acl_src_banned_ip\"\n"; }
	if (!-z $acl_src_banned_mac) { print FILE "acl IPFire_banned_mac       arp \"$acl_src_banned_mac\"\n"; }
	if (!-z $acl_src_unrestricted_ip) { print FILE "acl IPFire_unrestricted_ips src \"$acl_src_unrestricted_ip\"\n"; }
	if (!-z $acl_src_unrestricted_mac) { print FILE "acl IPFire_unrestricted_mac arp \"$acl_src_unrestricted_mac\"\n"; }
	print FILE <<END
acl CONNECT method CONNECT
END
	;

	if ($proxysettings{'CACHE_SIZE'} > 0) {
		print FILE <<END
maximum_object_size $proxysettings{'MAX_SIZE'} KB
minimum_object_size $proxysettings{'MIN_SIZE'} KB

cache_dir aufs /var/log/cache $proxysettings{'CACHE_SIZE'} $proxysettings{'L1_DIRS'} 256
END
		;
	} else {
		if ($proxysettings{'CACHE_MEM'} > 0) {
			# always 2% of CACHE_MEM defined as max object size
			print FILE "maximum_object_size_in_memory " . int($proxysettings{'CACHE_MEM'} * 1024 * 0.02) . " KB\n\n";
		} else {
			print FILE "cache deny all\n\n";
	    }
	}

	print FILE <<END
request_body_max_size $proxysettings{'MAX_OUTGOING_SIZE'} KB
END
	;

	if ($proxysettings{'MAX_INCOMING_SIZE'} > 0) {
		if (!-z $acl_src_unrestricted_ip) { print FILE "reply_body_max_size none IPFire_unrestricted_ips\n"; }
		if (!-z $acl_src_unrestricted_mac) { print FILE "reply_body_max_size none IPFire_unrestricted_mac\n"; }
		if ($proxysettings{'AUTH_METHOD'} eq 'ncsa')
		{
			if (!-z $extgrp) { print FILE "reply_body_max_size none for_extended_users\n"; }
		}
	}

	if ( $proxysettings{'MAX_INCOMING_SIZE'} != '0' )
	{
		print FILE "reply_body_max_size $proxysettings{'MAX_INCOMING_SIZE'} KB all\n\n";
	}

	if ($proxysettings{'LOGGING'} eq 'on')
	{
		print FILE <<END
access_log stdio:/var/log/squid/access.log
cache_log /var/log/squid/cache.log
cache_store_log none
END
	;
		if ($proxysettings{'LOGUSERAGENT'} eq 'on') { print FILE "access_log stdio:\/var\/log\/squid\/user_agent.log useragent\n"; }
		if ($proxysettings{'LOGQUERY'} eq 'on') { print FILE "\nstrip_query_terms off\n"; }
	} else {
		print FILE <<END
access_log /dev/null
cache_log /dev/null
cache_store_log none
END
	;}
	print FILE <<END

log_mime_hdrs off
END
	;

	if ($proxysettings{'FORWARD_IPADDRESS'} eq 'on')
	{
		print FILE "forwarded_for on\n";
	} else {
		print FILE "forwarded_for off\n";
	}
	if ($proxysettings{'FORWARD_VIA'} eq 'on')
	{
		print FILE "via on\n";
	} else {
		print FILE "via off\n";
	}
	print FILE "\n";

	if ((!($proxysettings{'AUTH_METHOD'} eq 'none')) && (!($proxysettings{'AUTH_METHOD'} eq 'ident')))
	{
		if ($proxysettings{'AUTH_METHOD'} eq 'ncsa')
		{
			print FILE "auth_param basic program $authdir/basic_ncsa_auth $userdb\n";
			print FILE "auth_param basic children $proxysettings{'AUTH_CHILDREN'}\n";
			print FILE "auth_param basic realm $authrealm\n";
			print FILE "auth_param basic credentialsttl $proxysettings{'AUTH_CACHE_TTL'} minutes\n";
			if (!($proxysettings{'AUTH_IPCACHE_TTL'} eq '0')) { print FILE "\nauthenticate_ip_ttl $proxysettings{'AUTH_IPCACHE_TTL'} minutes\n"; }
		}

		if ($proxysettings{'AUTH_METHOD'} eq 'ldap')
		{
			print FILE "auth_param basic utf8 on\n";
			print FILE "auth_param basic program $authdir/basic_ldap_auth -b \"$proxysettings{'LDAP_BASEDN'}\"";
			if (!($proxysettings{'LDAP_BINDDN_USER'} eq '')) { print FILE " -D \"$proxysettings{'LDAP_BINDDN_USER'}\""; }
			if (!($proxysettings{'LDAP_BINDDN_PASS'} eq '')) { print FILE " -w $proxysettings{'LDAP_BINDDN_PASS'}"; }
			if ($proxysettings{'LDAP_TYPE'} eq 'ADS')
			{
				if ($proxysettings{'LDAP_GROUP'} eq '')
				{
					print FILE " -f \"(\&(objectClass=person)(sAMAccountName=\%s))\"";
				} else {
					print FILE " -f \"(\&(\&(objectClass=person)(sAMAccountName=\%s))(memberOf=$proxysettings{'LDAP_GROUP'}))\"";
				}
				print FILE " -u sAMAccountName -P";
			}
			if ($proxysettings{'LDAP_TYPE'} eq 'NDS')
			{
				if ($proxysettings{'LDAP_GROUP'} eq '')
				{
					print FILE " -f \"(\&(objectClass=person)(cn=\%s))\"";
				} else {
					print FILE " -f \"(\&(\&(objectClass=person)(cn=\%s))(groupMembership=$proxysettings{'LDAP_GROUP'}))\"";
				}
				print FILE " -u cn -P";
			}
			if (($proxysettings{'LDAP_TYPE'} eq 'V2') || ($proxysettings{'LDAP_TYPE'} eq 'V3'))
			{
				if ($proxysettings{'LDAP_GROUP'} eq '')
				{
					print FILE " -f \"(\&(objectClass=person)(uid=\%s))\"";
				} else {
					print FILE " -f \"(\&(\&(objectClass=person)(uid=\%s))(memberOf=$proxysettings{'LDAP_GROUP'}))\"";
				}
				if ($proxysettings{'LDAP_TYPE'} eq 'V2') { print FILE " -v 2"; }
				if ($proxysettings{'LDAP_TYPE'} eq 'V3') { print FILE " -v 3"; }
				print FILE " -u uid -P";
			}
			print FILE " $proxysettings{'LDAP_SERVER'}:$proxysettings{'LDAP_PORT'}\n";
			print FILE "auth_param basic children $proxysettings{'AUTH_CHILDREN'}\n";
			print FILE "auth_param basic realm $authrealm\n";
			print FILE "auth_param basic credentialsttl $proxysettings{'AUTH_CACHE_TTL'} minutes\n";
			if (!($proxysettings{'AUTH_IPCACHE_TTL'} eq '0')) { print FILE "\nauthenticate_ip_ttl $proxysettings{'AUTH_IPCACHE_TTL'} minutes\n"; }
		}

		if ($proxysettings{'AUTH_METHOD'} eq 'ntlm-auth')
		{
			print FILE "auth_param ntlm program /usr/bin/ntlm_auth --helper-protocol=squid-2.5-ntlmssp";
			if ($proxysettings{'NTLM_AUTH_GROUP'}) {
				my $ntlm_auth_group = $proxysettings{'NTLM_AUTH_GROUP'};
				$ntlm_auth_group =~ s/\\/\+/;

				print FILE " --require-membership-of=$ntlm_auth_group";
			}
			print FILE "\n";

			print FILE "auth_param ntlm children $proxysettings{'AUTH_CHILDREN'}\n\n";
			print FILE "auth_param ntlm credentialsttl $proxysettings{'AUTH_CACHE_TTL'} minutes\n\n";

			# BASIC authentication
			if ($proxysettings{'NTLM_AUTH_BASIC'} eq "on") {
				print FILE "auth_param basic program /usr/bin/ntlm_auth --helper-protocol=squid-2.5-basic";
				if ($proxysettings{'NTLM_AUTH_GROUP'}) {
					my $ntlm_auth_group = $proxysettings{'NTLM_AUTH_GROUP'};
					$ntlm_auth_group =~ s/\\/\+/;

					print FILE " --require-membership-of=$ntlm_auth_group";
				}
				print FILE "\n";
				print FILE "auth_param basic children $proxysettings{'AUTH_CHILDREN'}\n";
				print FILE "auth_param basic realm $authrealm\n";
				print FILE "auth_param basic credentialsttl $proxysettings{'AUTH_CACHE_TTL'} minutes\n\n";
			}
		}

		if ($proxysettings{'AUTH_METHOD'} eq 'radius')
		{
			print FILE "auth_param basic program $authdir/basic_radius_auth -h $proxysettings{'RADIUS_SERVER'} -p $proxysettings{'RADIUS_PORT'} ";
			if (!($proxysettings{'RADIUS_IDENTIFIER'} eq '')) { print FILE "-i $proxysettings{'RADIUS_IDENTIFIER'} "; }
			print FILE "-w $proxysettings{'RADIUS_SECRET'}\n";
			print FILE "auth_param basic children $proxysettings{'AUTH_CHILDREN'}\n";
			print FILE "auth_param basic realm $authrealm\n";
			print FILE "auth_param basic credentialsttl $proxysettings{'AUTH_CACHE_TTL'} minutes\n";
			if (!($proxysettings{'AUTH_IPCACHE_TTL'} eq '0')) { print FILE "\nauthenticate_ip_ttl $proxysettings{'AUTH_IPCACHE_TTL'} minutes\n"; }
		}

		print FILE "\n";
		print FILE "acl for_inetusers proxy_auth REQUIRED\n";
		if (($proxysettings{'AUTH_METHOD'} eq 'radius') && ($proxysettings{'RADIUS_ENABLE_ACL'} eq 'on'))
		{
			if ((!-z "$raddir/radauth.allowusers") && ($proxysettings{'RADIUS_USER_ACL'} eq 'positive'))
			{
				print FILE "acl for_acl_users proxy_auth \"$raddir/radauth.allowusers\"\n";
			}
			if ((!-z "$raddir/radauth.denyusers") && ($proxysettings{'RADIUS_USER_ACL'} eq 'negative'))
			{
				print FILE "acl for_acl_users proxy_auth \"$raddir/radauth.denyusers\"\n";
			}
		}
		if ($proxysettings{'AUTH_METHOD'} eq 'ncsa')
		{
			print FILE "\n";
			if (!-z $extgrp) { print FILE "acl for_extended_users proxy_auth \"$extgrp\"\n"; }
			if (!-z $disgrp) { print FILE "acl for_disabled_users proxy_auth \"$disgrp\"\n"; }
		}
		if (!($proxysettings{'AUTH_MAX_USERIP'} eq '')) { print FILE "\nacl concurrent max_user_ip -s $proxysettings{'AUTH_MAX_USERIP'}\n"; }
		print FILE "\n";

		if (!-z $acl_dst_noauth_net) { print FILE "acl to_ipaddr_without_auth dst \"$acl_dst_noauth_net\"\n"; }
		if (!-z $acl_dst_noauth_dom) { print FILE "acl to_domains_without_auth dstdomain \"$acl_dst_noauth_dom\"\n"; }
		if (!-z $acl_dst_noauth_url) { print FILE "acl to_hosts_without_auth url_regex -i \"$acl_dst_noauth_url\"\n"; }
		print FILE "\n";

	}

	if ($proxysettings{'AUTH_METHOD'} eq 'ident')
	{
		if ($proxysettings{'IDENT_REQUIRED'} eq 'on')
		{
			print FILE "acl for_inetusers ident REQUIRED\n";
		}
		if ($proxysettings{'IDENT_ENABLE_ACL'} eq 'on')
		{
			if ((!-z "$identdir/identauth.allowusers") && ($proxysettings{'IDENT_USER_ACL'} eq 'positive'))
			{
				print FILE "acl for_acl_users ident_regex -i \"$identdir/identauth.allowusers\"\n\n";
			}
			if ((!-z "$identdir/identauth.denyusers") && ($proxysettings{'IDENT_USER_ACL'} eq 'negative'))
			{
				print FILE "acl for_acl_users ident_regex -i \"$identdir/identauth.denyusers\"\n\n";
			}
		}
		if (!-z $acl_dst_noauth_net) { print FILE "acl to_ipaddr_without_auth dst \"$acl_dst_noauth_net\"\n"; }
		if (!-z $acl_dst_noauth_dom) { print FILE "acl to_domains_without_auth dstdomain \"$acl_dst_noauth_dom\"\n"; }
		if (!-z $acl_dst_noauth_url) { print FILE "acl to_hosts_without_auth url_regex -i \"$acl_dst_noauth_url\"\n"; }
		print FILE "\n";
	}

	if (($delaypools) && (!-z $acl_dst_throttle)) { print FILE "acl for_throttled_urls url_regex -i \"$acl_dst_throttle\"\n\n"; }

	print FILE "acl within_timeframe time ";
	if ($proxysettings{'TIME_MON'} eq 'on') { print FILE "M"; }
	if ($proxysettings{'TIME_TUE'} eq 'on') { print FILE "T"; }
	if ($proxysettings{'TIME_WED'} eq 'on') { print FILE "W"; }
	if ($proxysettings{'TIME_THU'} eq 'on') { print FILE "H"; }
	if ($proxysettings{'TIME_FRI'} eq 'on') { print FILE "F"; }
	if ($proxysettings{'TIME_SAT'} eq 'on') { print FILE "A"; }
	if ($proxysettings{'TIME_SUN'} eq 'on') { print FILE "S"; }
	print FILE " $proxysettings{'TIME_FROM_HOUR'}:";
	print FILE "$proxysettings{'TIME_FROM_MINUTE'}-";
	print FILE "$proxysettings{'TIME_TO_HOUR'}:";
	print FILE "$proxysettings{'TIME_TO_MINUTE'}\n\n";

	if ((!-z $mimetypes) && ($proxysettings{'ENABLE_MIME_FILTER'} eq 'on')) {
		print FILE "acl blocked_mimetypes rep_mime_type \"$mimetypes\"\n\n";
	}

	if ($proxysettings{'CLASSROOM_EXT'} eq 'on') {
		print FILE <<END

#Classroom extensions
acl IPFire_no_access_ips src "$acl_src_noaccess_ip"
acl IPFire_no_access_mac arp "$acl_src_noaccess_mac"
END
		;
		print FILE "deny_info ";
		if (($proxysettings{'ERR_DESIGN'} eq 'squid') && (-e "$errordir/$proxysettings{'ERR_LANGUAGE'}/ERR_ACCESS_DISABLED"))
		{
			print FILE "ERR_ACCESS_DISABLED";
		} else {
			print FILE "ERR_ACCESS_DENIED";
		}
		print FILE " IPFire_no_access_ips\n";
		print FILE "deny_info ";
		if (($proxysettings{'ERR_DESIGN'} eq 'squid') && (-e "$errordir/$proxysettings{'ERR_LANGUAGE'}/ERR_ACCESS_DISABLED"))
		{
			print FILE "ERR_ACCESS_DISABLED";
		} else {
			print FILE "ERR_ACCESS_DENIED";
		}
		print FILE " IPFire_no_access_mac\n";

		print FILE <<END
http_access deny IPFire_no_access_ips
http_access deny IPFire_no_access_mac
END
	;
	}

	#Insert acl file and replace __VAR__ with correct values
	my $blue_net = ''; #BLUE empty by default
	my $blue_ip = '';
	if ($netsettings{'BLUE_DEV'} && $proxysettings{'ENABLE_BLUE'} eq 'on') {
		$blue_net = "$blue_cidr";
		$blue_ip  = "$netsettings{'BLUE_ADDRESS'}";
	}
	if (!-z $acl_include)
	{
		open (ACL, "$acl_include");
		print FILE "\n#Start of custom includes\n\n";
		while (<ACL>) {
			$_ =~ s/__GREEN_IP__/$netsettings{'GREEN_ADDRESS'}/;
			$_ =~ s/__GREEN_NET__/$green_cidr/;
			$_ =~ s/__BLUE_IP__/$blue_ip/;
			$_ =~ s/__BLUE_NET__/$blue_net/;
			$_ =~ s/__PROXY_PORT__/$proxysettings{'PROXY_PORT'}/;
			print FILE $_;
		}
		print FILE "\n#End of custom includes\n";
		close (ACL);
	}
	if ((!-z $extgrp) && ($proxysettings{'AUTH_METHOD'} eq 'ncsa') && ($proxysettings{'NCSA_BYPASS_REDIR'} eq 'on')) { print FILE "\nredirector_access deny for_extended_users\n"; }

	# Check if squidclamav is enabled.
	if ($proxysettings{'ENABLE_CLAMAV'} eq 'on') {
		print FILE "\n#Settings for squidclamav:\n";
		print FILE "http_port 127.0.0.1:$proxysettings{'PROXY_PORT'}\n";
		print FILE "acl purge method PURGE\n";
		print FILE "http_access deny to_localhost\n";
		print FILE "http_access allow localhost\n";
		print FILE "http_access allow purge localhost\n";
		print FILE "http_access deny purge\n";
		print FILE "url_rewrite_access deny localhost\n";
	}
	print FILE <<END;

#Access to squid:
#local machine, no restriction
http_access allow         localhost

#GUI admin if local machine connects
http_access allow         IPFire_ips IPFire_networks IPFire_http
http_access allow CONNECT IPFire_ips IPFire_networks IPFire_https

#Deny not web services
END

if (@safe_ports) {
	print FILE "http_access deny          !Safe_ports\n";
}

if (@ssl_ports) {
	print FILE "http_access deny  CONNECT !SSL_ports\n";
}

	if ((($proxysettings{'ASNBL_FASTFLUX_DETECTION'} eq 'on') && (!-z $proxysettings{'ASNBL_FASTFLUX_THRESHOLD'})) || ($proxysettings{'ASNBL_SELECANN_DETECTION'} eq 'on')) {
		print FILE "external_acl_type asnblhelper children-max=10 children-startup=2 ttl=86400 %DST /usr/bin/asnbl-helper.py ${General::swroot}/proxy/asnbl-helper.conf\n";
		print FILE "acl asnbl external asnblhelper\n";

		# Use the user-defined URL filter whitelist (if present and populated) for the ASNBL helper as well
		# Necessary for destinations such as fedoraproject.org, but we do not want to maintain a dedicated
		# or hardcoded list for such FQDNs.
		if ((-e "${General::swroot}/urlfilter/blacklists/custom/allowed/domains") && (!-z "${General::swroot}/urlfilter/blacklists/custom/allowed/domains")) {
			print FILE "acl asnbl_whitelisted_destinations dstdomain \"${General::swroot}/urlfilter/blacklists/custom/allowed/domains\"\n";
			print FILE "http_access deny asnbl !asnbl_whitelisted_destinations\n\n";
		} else {
			print FILE "http_access deny asnbl\n\n";
		}

		# Write ASNBL helper configuration file...
		open(ASNBLFILE, ">${General::swroot}/proxy/asnbl-helper.conf");
		flock(ASNBLFILE, 2);

		print ASNBLFILE<<END
#
# This file has been automatically generated. Manual changes will be overwritten.
#

[GENERAL]
LOGLEVEL = INFO
ASNDB_PATH = /var/lib/location/database.db
USE_REPLYMAP = no
END
;

		print ASNBLFILE "AS_DIVERSITY_THRESHOLD = $proxysettings{'ASNBL_FASTFLUX_THRESHOLD'}\n";

		if ($proxysettings{'ASNBL_SELECANN_DETECTION'} eq 'on') {
			print ASNBLFILE "BLOCK_SUSPECTED_SELECTIVE_ANNOUNCEMENTS = yes\n";
		} else {
			print ASNBLFILE "BLOCK_SUSPECTED_SELECTIVE_ANNOUNCEMENTS = no\n";
		}

		if ($proxysettings{'ASNBL_FASTFLUX_DETECTION'} eq 'on') {
			print ASNBLFILE "BLOCK_DIVERSITY_EXCEEDING_DESTINATIONS = yes\n";
		} else {
			print ASNBLFILE "BLOCK_DIVERSITY_EXCEEDING_DESTINATIONS = no\n";
		}

		print ASNBLFILE<<END
TESTDATA = (10.0.0.1, 0) (127.0.0.1, 0) (fe80::1, 0)
ACTIVE_ASNBLS =
END
;

		close ASNBLFILE;
    }

if ($proxysettings{'AUTH_METHOD'} eq 'ident')
{
print FILE "#Set ident ACLs\n";
if (!-z $identhosts)
	{
		print FILE "acl on_ident_aware_hosts src \"$identhosts\"\n";
		print FILE "ident_lookup_access allow on_ident_aware_hosts\n";
		print FILE "ident_lookup_access deny all\n";
	} else {
		print FILE "ident_lookup_access allow all\n";
	}
	print FILE "ident_timeout $proxysettings{'IDENT_TIMEOUT'} seconds\n\n";
}

if ($delaypools) {
	print FILE "#Set download throttling\n";

	if ($netsettings{'BLUE_DEV'})
	{
		print FILE "delay_pools 2\n";
	} else {
		print FILE "delay_pools 1\n";
	}

	print FILE "delay_class 1 3\n";
	if ($netsettings{'BLUE_DEV'}) {	print FILE "delay_class 2 3\n"; }

	print FILE "delay_parameters 1 ";
	if ($proxysettings{'THROTTLING_GREEN_TOTAL'} eq 'unlimited')
	{
		print FILE "-1/-1";
	} else {
		print FILE $proxysettings{'THROTTLING_GREEN_TOTAL'} * 125;
		print FILE "/";
		print FILE $proxysettings{'THROTTLING_GREEN_TOTAL'} * 250;
	}

	print FILE " -1/-1 ";
	if ($proxysettings{'THROTTLING_GREEN_HOST'} eq 'unlimited')
	{
		print FILE "-1/-1";
	} else {
		print FILE $proxysettings{'THROTTLING_GREEN_HOST'} * 125;
		print FILE "/";
		print FILE $proxysettings{'THROTTLING_GREEN_HOST'} * 250;
	}
	print FILE "\n";

	if ($netsettings{'BLUE_DEV'})
	{
		print FILE "delay_parameters 2 ";
		if ($proxysettings{'THROTTLING_BLUE_TOTAL'} eq 'unlimited')
		{
			print FILE "-1/-1";
		} else {
			print FILE $proxysettings{'THROTTLING_BLUE_TOTAL'} * 125;
			print FILE "/";
			print FILE $proxysettings{'THROTTLING_BLUE_TOTAL'} * 250;
		}
		print FILE " -1/-1 ";
		if ($proxysettings{'THROTTLING_BLUE_HOST'} eq 'unlimited')
		{
			print FILE "-1/-1";
		} else {
			print FILE $proxysettings{'THROTTLING_BLUE_HOST'} * 125;
			print FILE "/";
			print FILE $proxysettings{'THROTTLING_BLUE_HOST'} * 250;
		}
		print FILE "\n";
	}

	print FILE "delay_access 1 deny  IPFire_ips\n";
	if (!-z $acl_src_unrestricted_ip)  { print FILE "delay_access 1 deny  IPFire_unrestricted_ips\n"; }
	if (!-z $acl_src_unrestricted_mac) { print FILE "delay_access 1 deny  IPFire_unrestricted_mac\n"; }
	if (($proxysettings{'AUTH_METHOD'} eq 'ncsa') && (!-z $extgrp)) { print FILE "delay_access 1 deny  for_extended_users\n"; }

	if ($netsettings{'BLUE_DEV'})
	{
		if (&Header::green_used()) {
			print FILE "delay_access 1 allow IPFire_green_network";
			if (!-z $acl_dst_throttle) { print FILE " for_throttled_urls"; }
			print FILE "\n";
		}
		print FILE "delay_access 1 deny  all\n";
	} else {
		print FILE "delay_access 1 allow all";
		if (!-z $acl_dst_throttle) { print FILE " for_throttled_urls"; }
		print FILE "\n";
	}

	if ($netsettings{'BLUE_DEV'})
	{
		print FILE "delay_access 2 deny  IPFire_ips\n";
		if (!-z $acl_src_unrestricted_ip)  { print FILE "delay_access 2 deny  IPFire_unrestricted_ips\n"; }
		if (!-z $acl_src_unrestricted_mac) { print FILE "delay_access 2 deny  IPFire_unrestricted_mac\n"; }
		if (($proxysettings{'AUTH_METHOD'} eq 'ncsa') && (!-z $extgrp)) { print FILE "delay_access 2 deny  for_extended_users\n"; }
		print FILE "delay_access 2 allow IPFire_blue_network";
		if (!-z $acl_dst_throttle) { print FILE " for_throttled_urls"; }
		print FILE "\n";
		print FILE "delay_access 2 deny  all\n";
	}

	print FILE "delay_initial_bucket_level 100\n";
	print FILE "\n";
}

if (&Header::green_used() && $proxysettings{'NO_PROXY_LOCAL'} eq 'on')
{
	print FILE "#Prevent internal proxy access to Green except IPFire itself\n";
	print FILE "http_access deny IPFire_green_servers !IPFire_ips !IPFire_green_network\n\n";
}

if ($proxysettings{'NO_PROXY_LOCAL_BLUE'} eq 'on')
{
	print FILE "#Prevent internal proxy access from Blue except IPFire itself\n";
	print FILE "http_access allow IPFire_blue_network IPFire_blue_servers\n";
	print FILE "http_access deny  IPFire_blue_network !IPFire_ips IPFire_servers\n\n";
}

	print FILE <<END
#Set custom configured ACLs
END
	;
	if (!-z $acl_src_banned_ip) { print FILE "http_access deny  IPFire_banned_ips\n"; }
	if (!-z $acl_src_banned_mac) { print FILE "http_access deny  IPFire_banned_mac\n"; }

	if ((!-z $acl_dst_noauth) && (!($proxysettings{'AUTH_METHOD'} eq 'none')))
	{
		if (!-z $acl_src_unrestricted_ip)
		{
			if (!-z $acl_dst_noauth_net) { print FILE "http_access allow IPFire_unrestricted_ips to_ipaddr_without_auth\n"; }
			if (!-z $acl_dst_noauth_dom) { print FILE "http_access allow IPFire_unrestricted_ips to_domains_without_auth\n"; }
			if (!-z $acl_dst_noauth_url) { print FILE "http_access allow IPFire_unrestricted_ips to_hosts_without_auth\n"; }
		}
		if (!-z $acl_src_unrestricted_mac)
		{
			if (!-z $acl_dst_noauth_net) { print FILE "http_access allow IPFire_unrestricted_mac to_ipaddr_without_auth\n"; }
			if (!-z $acl_dst_noauth_dom) { print FILE "http_access allow IPFire_unrestricted_mac to_domains_without_auth\n"; }
			if (!-z $acl_dst_noauth_url) { print FILE "http_access allow IPFire_unrestricted_mac to_hosts_without_auth\n"; }
		}
		if (!-z $acl_dst_noauth_net)
		{
			print FILE "http_access allow IPFire_networks";
			if ($proxysettings{'TIME_ACCESS_MODE'} eq 'deny') {
				print FILE " !within_timeframe";
			} else {
				print FILE " within_timeframe"; }
			print FILE " to_ipaddr_without_auth\n";
		}
		if (!-z $acl_dst_noauth_dom)
		{
			print FILE "http_access allow IPFire_networks";
			if ($proxysettings{'TIME_ACCESS_MODE'} eq 'deny') {
				print FILE " !within_timeframe";
			} else {
				print FILE " within_timeframe"; }
			print FILE " to_domains_without_auth\n";
		}
		if (!-z $acl_dst_noauth_url)
		{
			print FILE "http_access allow IPFire_networks";
			if ($proxysettings{'TIME_ACCESS_MODE'} eq 'deny') {
				print FILE " !within_timeframe";
			} else {
				print FILE " within_timeframe"; }
			print FILE " to_hosts_without_auth\n";
		}
	}

	if (($proxysettings{'AUTH_METHOD'} eq 'ident') && ($proxysettings{'IDENT_REQUIRED'} eq 'on') && ($proxysettings{'AUTH_ALWAYS_REQUIRED'} eq 'on'))
	{
		print FILE "http_access deny  !for_inetusers";
		if (!-z $identhosts) { print FILE " on_ident_aware_hosts"; }
		print FILE "\n";
	}

	if (
	     ($proxysettings{'AUTH_METHOD'} eq 'ident') &&
	     ($proxysettings{'AUTH_ALWAYS_REQUIRED'} eq 'on') &&
	     ($proxysettings{'IDENT_ENABLE_ACL'} eq 'on') &&
	     ($proxysettings{'IDENT_USER_ACL'} eq 'negative') &&
	     (!-z "$identdir/identauth.denyusers")
	   )
	{
		print FILE "http_access deny  for_acl_users";
		if (($proxysettings{'AUTH_METHOD'} eq 'ident') && (!-z "$identdir/hosts")) { print FILE " on_ident_aware_hosts"; }
		print FILE "\n";
	}

	if (!-z $acl_src_unrestricted_ip)
	{
		print FILE "http_access allow IPFire_unrestricted_ips";
		if ($proxysettings{'AUTH_ALWAYS_REQUIRED'} eq 'on')
		{
			if ($proxysettings{'AUTH_METHOD'} eq 'ncsa')
			{
				if (!-z $disgrp) { print FILE " !for_disabled_users"; } else { print FILE " for_inetusers"; }
			}
			if (($proxysettings{'AUTH_METHOD'} eq 'ldap') || ($proxysettings{'AUTH_METHOD'} eq 'radius'))
			{
				print FILE " for_inetusers";
			}
			if (($proxysettings{'AUTH_METHOD'} eq 'radius') && ($proxysettings{'RADIUS_ENABLE_ACL'} eq 'on'))
			{
				if ($proxysettings{'RADIUS_ENABLE_ACL'} eq 'on')
				{
					if (($proxysettings{'RADIUS_USER_ACL'} eq 'positive') && (!-z "$raddir/radauth.allowusers"))
					{
						print FILE " for_acl_users";
					}
					if (($proxysettings{'RADIUS_USER_ACL'} eq 'negative') && (!-z "$raddir/radauth.denyusers"))
					{
						print FILE " !for_acl_users";
					}
				} else { print FILE " for_inetusers"; }
			}
		}
		print FILE "\n";
	}

	if (!-z $acl_src_unrestricted_mac)
	{
		print FILE "http_access allow IPFire_unrestricted_mac";
		if ($proxysettings{'AUTH_ALWAYS_REQUIRED'} eq 'on')
		{
			if ($proxysettings{'AUTH_METHOD'} eq 'ncsa')
			{
				if (!-z $disgrp) { print FILE " !for_disabled_users"; } else { print FILE " for_inetusers"; }
			}
			if (($proxysettings{'AUTH_METHOD'} eq 'ldap') || ($proxysettings{'AUTH_METHOD'} eq 'radius'))
			{
				print FILE " for_inetusers";
			}
			if (($proxysettings{'AUTH_METHOD'} eq 'radius') && ($proxysettings{'RADIUS_ENABLE_ACL'} eq 'on'))
			{
				if ($proxysettings{'RADIUS_ENABLE_ACL'} eq 'on')
				{
					if (($proxysettings{'RADIUS_USER_ACL'} eq 'positive') && (!-z "$raddir/radauth.allowusers"))
					{
						print FILE " for_acl_users";
					}
					if (($proxysettings{'RADIUS_USER_ACL'} eq 'negative') && (!-z "$raddir/radauth.denyusers"))
					{
						print FILE " !for_acl_users";
					}
				} else { print FILE " for_inetusers"; }
			}
		}
		print FILE "\n";
	}

	if ($proxysettings{'AUTH_METHOD'} eq 'ncsa')
	{
		if (!-z $disgrp) { print FILE "http_access deny  for_disabled_users\n"; }
		if (!-z $extgrp) { print FILE "http_access allow IPFire_networks for_extended_users\n"; }
	}

	if (
	    (
	     ($proxysettings{'AUTH_METHOD'} eq 'radius') &&
	     ($proxysettings{'RADIUS_ENABLE_ACL'} eq 'on') &&
	     ($proxysettings{'RADIUS_USER_ACL'} eq 'negative') &&
	     (!-z "$raddir/radauth.denyusers")
	    )
		||
	    (
	     ($proxysettings{'AUTH_METHOD'} eq 'ident') &&
	     ($proxysettings{'AUTH_ALWAYS_REQUIRED'} eq 'off') &&
	     ($proxysettings{'IDENT_ENABLE_ACL'} eq 'on') &&
	     ($proxysettings{'IDENT_USER_ACL'} eq 'negative') &&
	     (!-z "$identdir/identauth.denyusers")
	    )
	   )
	{
		print FILE "http_access deny  for_acl_users";
		if (($proxysettings{'AUTH_METHOD'} eq 'ident') && (!-z "$identdir/hosts")) { print FILE " on_ident_aware_hosts"; }
		print FILE "\n";
	}

	if (($proxysettings{'AUTH_METHOD'} eq 'ident') && ($proxysettings{'IDENT_REQUIRED'} eq 'on') && (!-z "$identhosts"))
	{
		print FILE "http_access allow";
		if ($proxysettings{'TIME_ACCESS_MODE'} eq 'deny') {
			print FILE " !within_timeframe";
		} else {
			print FILE " within_timeframe"; }
		print FILE " !on_ident_aware_hosts\n";
	}

	print FILE "http_access allow IPFire_networks";
	if (
	    (
	     ($proxysettings{'AUTH_METHOD'} eq 'radius') &&
	     ($proxysettings{'RADIUS_ENABLE_ACL'} eq 'on') &&
	     ($proxysettings{'RADIUS_USER_ACL'} eq 'positive') &&
	     (!-z "$raddir/radauth.allowusers")
	    )
		||
	    (
	     ($proxysettings{'AUTH_METHOD'} eq 'ident') &&
	     ($proxysettings{'IDENT_REQUIRED'} eq 'on') &&
	     ($proxysettings{'IDENT_ENABLE_ACL'} eq 'on') &&
	     ($proxysettings{'IDENT_USER_ACL'} eq 'positive') &&
	     (!-z "$identdir/identauth.allowusers")
	    )
	   )
	{
		print FILE " for_acl_users";
	} elsif (((!($proxysettings{'AUTH_METHOD'} eq 'none')) && (!($proxysettings{'AUTH_METHOD'} eq 'ident'))) ||
		(($proxysettings{'AUTH_METHOD'} eq 'ident') && ($proxysettings{'IDENT_REQUIRED'} eq 'on'))) {
		print FILE " for_inetusers";
	}
	if ((!($proxysettings{'AUTH_MAX_USERIP'} eq '')) && (!($proxysettings{'AUTH_METHOD'} eq 'none')) && (!($proxysettings{'AUTH_METHOD'} eq 'ident')))
	{
		print FILE " !concurrent";
	}
	if ($proxysettings{'TIME_ACCESS_MODE'} eq 'deny') {
		print FILE " !within_timeframe";
	} else {
		print FILE " within_timeframe"; }
	print FILE "\n";

	print FILE "http_access deny  all\n\n";

	if (($proxysettings{'FORWARD_IPADDRESS'} eq 'off') || ($proxysettings{'FORWARD_VIA'} eq 'off'))
	{
		print FILE "#Strip HTTP Header\n";

		if ($proxysettings{'FORWARD_IPADDRESS'} eq 'off')
		{
			print FILE "request_header_access X-Forwarded-For deny all\n";
			print FILE "reply_header_access X-Forwarded-For deny all\n";
		}
		if ($proxysettings{'FORWARD_VIA'} eq 'off')
		{
			print FILE "request_header_access Via deny all\n";
			print FILE "reply_header_access Via deny all\n";
		}

		print FILE "\n";

	}

	if ((!-z $mimetypes) && ($proxysettings{'ENABLE_MIME_FILTER'} eq 'on')) {
		if (!-z $acl_src_unrestricted_ip)  { print FILE "http_reply_access allow IPFire_unrestricted_ips\n"; }
		if (!-z $acl_src_unrestricted_mac) { print FILE "http_reply_access allow IPFire_unrestricted_mac\n"; }
		if ($proxysettings{'AUTH_METHOD'} eq 'ncsa')
		{
			if (!-z $extgrp) { print FILE "http_reply_access allow for_extended_users\n"; }
		}
		print FILE "http_reply_access deny  blocked_mimetypes\n";
		print FILE "http_reply_access allow all\n\n";
	}

	print FILE "visible_hostname";
	if ($proxysettings{'VISIBLE_HOSTNAME'} eq '')
	{
		print FILE " $mainsettings{'HOSTNAME'}.$mainsettings{'DOMAINNAME'}\n\n";
	} else {
		print FILE " $proxysettings{'VISIBLE_HOSTNAME'}\n\n";
	}

	if (!($proxysettings{'ADMIN_MAIL_ADDRESS'} eq ''))
		{
			print FILE "cache_mgr $proxysettings{'ADMIN_MAIL_ADDRESS'}\n";
		}
	if (!($proxysettings{'ADMIN_PASSWORD'} eq ''))
		{
			print FILE "cachemgr_passwd $proxysettings{'ADMIN_PASSWORD'} all\n";
		}
	print FILE "\n";

	print FILE "max_filedescriptors $proxysettings{'FILEDESCRIPTORS'}\n\n";

	# Write the parent proxy info, if needed.
	if ($remotehost ne '')
	{
		print FILE "cache_peer $remotehost parent $remoteport 3130 default no-query";

		# Enter authentication for the parent cache. Option format is
		# login=user:password   ($proxy1='YES')
		# login=PASS            ($proxy1='PASS')
		# login=*:password      ($proxysettings{'FORWARD_USERNAME'} eq 'on')
		if (($proxy1 eq 'YES') || ($proxy1 eq 'PASS'))
		{
			$proxysettings{'UPSTREAM_USER'} = &Header::escape($proxysettings{'UPSTREAM_USER'});
			print FILE " login=$proxysettings{'UPSTREAM_USER'}";
			if ($proxy1 eq 'YES')
			{
				$proxysettings{'UPSTREAM_PASSWORD'} = &Header::escape($proxysettings{'UPSTREAM_PASSWORD'});
				print FILE ":$proxysettings{'UPSTREAM_PASSWORD'}";
			}
		}
		elsif ($proxysettings{'FORWARD_USERNAME'} eq 'on') { print FILE " login=*:password"; }

		print FILE "\nalways_direct allow IPFire_ips\n";
		print FILE "never_direct  allow all\n\n";
	}
	if (($proxysettings{'ENABLE_FILTER'} eq 'on') || ($proxysettings{'ENABLE_UPDXLRATOR'} eq 'on') || ($proxysettings{'ENABLE_CLAMAV'} eq 'on'))
	{
		print FILE "url_rewrite_program /usr/sbin/redirect_wrapper\n";
		print FILE "url_rewrite_children ", &General::number_cpu_cores();
		print FILE " startup=", &General::number_cpu_cores();
		print FILE " idle=", &General::number_cpu_cores();
		print FILE " queue-size=", &General::number_cpu_cores() * 32, "\n\n";
	}

	# Include file with user defined settings.
	if (-e "/etc/squid/squid.conf.local") {
		print FILE "include /etc/squid/squid.conf.local\n";
	}
	close FILE;

	# Proxy settings for squidclamav - if installed.
	#
	# Check if squidclamav is enabled.
	if ($proxysettings{'ENABLE_CLAMAV'} eq 'on') {

		my $configfile='/etc/squidclamav.conf';

		my $data = &General::read_file_utf8($configfile);
		$data =~ s/squid_port [0-9]+/squid_port $proxysettings{'PROXY_PORT'}/g;
		&General::write_file_utf8($configfile, $data);
	}
}

# -------------------------------------------------------------------

sub adduser
{
	my ($str_user, $str_pass, $str_group) = @_;
	my @groupmembers=();

	if ($str_pass eq 'lEaVeAlOnE')
	{
		open(FILE, "$userdb");
		@groupmembers = <FILE>;
		close(FILE);
		foreach $line (@groupmembers) {	if ($line =~ /^$str_user:/i) { $str_pass = substr($line,index($line,":")); } }
		&deluser($str_user);
		open(FILE, ">>$userdb");
		flock FILE,2;
		print FILE "$str_user$str_pass";
		close(FILE);
	} else {
		&deluser($str_user);
		&General::system("/usr/bin/htpasswd", "-bB", "-C 10", "$userdb", "$str_user", "$str_pass");
	}

	if ($str_group eq 'standard') { open(FILE, ">>$stdgrp");
	} elsif ($str_group eq 'extended') { open(FILE, ">>$extgrp");
	} elsif ($str_group eq 'disabled') { open(FILE, ">>$disgrp"); }
	flock FILE, 2;
	print FILE "$str_user\n";
	close(FILE);

	return;
}

# -------------------------------------------------------------------

sub deluser
{
	my ($str_user) = @_;
	my $groupfile='';
	my @groupmembers=();
	my @templist=();

	foreach $groupfile ($stdgrp, $extgrp, $disgrp)
	{
		undef @templist;
		open(FILE, "$groupfile");
		@groupmembers = <FILE>;
		close(FILE);
		foreach $line (@groupmembers) { if (!($line =~ /^$str_user$/i)) { push(@templist, $line); } }
		open(FILE, ">$groupfile");
		flock FILE, 2;
		print FILE @templist;
		close(FILE);
	}

	undef @templist;
	open(FILE, "$userdb");
	@groupmembers = <FILE>;
	close(FILE);
	foreach $line (@groupmembers) { if (!($line =~ /^$str_user:/i)) { push(@templist, $line); } }
	open(FILE, ">$userdb");
	flock FILE, 2;
	print FILE @templist;
	close(FILE);

	return;
}

# -------------------------------------------------------------------

sub writecachemgr
{
	open(FILE, ">${General::swroot}/proxy/cachemgr.conf");
	flock(FILE, 2);
	if (&Header::green_used()) {
		print FILE "$netsettings{'GREEN_ADDRESS'}:$proxysettings{'PROXY_PORT'}\n";
	}
	print FILE "localhost";
	close(FILE);
  return;
}

# -------------------------------------------------------------------
