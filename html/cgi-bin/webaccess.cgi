#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007  Michael Tremer & Christian Schmidt                      #
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

#usable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';
use CGI;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";


my $swroot = "/var/ipfire";
my $apdir  = "$swroot/proxy/advanced";
my $group_def_file = "$apdir/cre/classrooms";
my $svhosts_file = "$apdir/cre/supervisors";
my $acl_src_noaccess_ips = "$apdir/acls/src_noaccess_ip.acl";
my $acl_src_noaccess_mac = "$apdir/acls/src_noaccess_mac.acl";

my $banner = "A D V A N C E D &nbsp; P R O X Y &nbsp; - &nbsp; W E B &nbsp; A C C E S S &nbsp; M A N A G E R";
my %cgiparams;
my %proxysettings;
my %temp;

my %acl=();
my @group_defs=();
my @groups=();

### Initialize environment
&readhash("${swroot}/proxy/advanced/settings", \%proxysettings);

### Initialize language
require "${swroot}/lang.pl";

&getcgihash(\%cgiparams);

&read_all_groups;
&read_acl_groups;

foreach (@groups)
{
       if ($cgiparams{$_} eq $Lang::tr{'advproxy mode deny'}) { $acl{$_}='on'; }
       if ($cgiparams{$_} eq $Lang::tr{'advproxy mode allow'}) { $acl{$_}='off'; }
}

&read_all_groups;

my $is_supervisor=0;

if ((-e $svhosts_file) && (!-z $svhosts_file))
{
	open (FILE, $svhosts_file);
	while (<FILE>)
	{
		chomp;
		if ($ENV{'REMOTE_ADDR'} eq $_) { $is_supervisor=1; }
	}
	close (FILE);

} else { $is_supervisor=1; }

if (($cgiparams{'ACTION'} eq 'submit') && ($is_supervisor))
{
	if (	($cgiparams{'PASSWORD'} eq $proxysettings{'SUPERVISOR_PASSWORD'}) && (!($proxysettings{'SUPERVISOR_PASSWORD'} eq '')) || 
		((defined($proxysettings{'SUPERVISOR_PASSWORD'})) && ($proxysettings{'SUPERVISOR_PASSWORD'} eq '')))
	{
		&write_acl;
		system("/usr/local/bin/squidctrl restart >/dev/null 2>&1");
	}
}

&read_acl_groups;

#undef(%cgiparams);

# -------------------------------------------------------------------

print <<END
Pragma: no-cache
Cache-control: no-cache
Connection: close
Content-type: text/html

<!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML 4.01 Transitional//EN' 'http://www.w3.org/TR/html4/loose.dtd'>
<html>
<head>
<meta http-equiv='Content-Type' content='text/html; charset=UTF-8'>
<title>Advanced Proxy - Web Access Manager</title>
<style type='text/css'>
	a:link    { text-decoration:none; font-family:verdana,arial,helvetica; font-weight:bold; color:#ffffff; }
	a:visited { text-decoration:none; font-family:verdana,arial,helvetica; font-weight:bold; color:#ffffff; }
	a:hover   { text-decoration:none; font-family:verdana,arial,helvetica; font-weight:bold; color:#000000; }
	a:active  { text-decoration:none; font-family:verdana,arial,helvetica; font-weight:bold; color:#000000; }
	a:focus   { text-decoration:none; font-family:verdana,arial,helvetica; font-weight:bold; color:#ffffff; }
</style>
</head>
<body bgcolor='#FFFFFF'>

<center>

<form method='post' action='$ENV{'SCRIPT_NAME'}'>

<table width='720' cellspacing='10' cellpadding='5' border='0'>

<tr>
   <td bgcolor='#C0C0C0' height='20'></td>
</tr>

<tr>
   <td bgcolor='#F4F4F4' align='center'>
      <table width='100%' cellspacing='10' cellpadding='10' border='0'>

         <tr>
            <td nowrap bgcolor='#FFFFFF' align='center'>
                <font face='verdana,arial,helvetica' color='#000000' size='3'>$banner</font>
            </td>
         </tr>

END
;
if ($proxysettings{'CLASSROOM_EXT'} eq 'on')
{
if (@groups)
{
print <<END
         <tr>
            <td>
               <table width='70%' cellspacing='2' cellpadding='2' border='0' align='center'>
	<tr><td><input type='hidden' name='ACTION' value='submit'></td></tr>
               <tr>
END
;
if (($is_supervisor) && ((defined($proxysettings{'SUPERVISOR_PASSWORD'})) && (!($proxysettings{'SUPERVISOR_PASSWORD'} eq ''))))
{
print <<END
                  <td align='center'>
                     <font face='verdana,arial,helvetica' color='#000000' size='2'>$Lang::tr{'advproxy supervisor password'}:</font>
                  </td>
                  <td align='center'><input type='password' name='PASSWORD' size='15'></td>
END
;
}
print <<END
               </tr>

               </table>

               <p>

END
;
	foreach (@groups) {
		if ($is_supervisor)
		{
			print"<table width='65%' cellspacing='2' cellpadding='2' border='0' align='center' rules='groups'>";
		} else {
			print"<table width='50%' cellspacing='2' cellpadding='6' border='0' align='center' rules='groups'>";
		}
		print "<tr>\n";
		if ((defined($acl{$_})) && ($acl{$_} eq 'on'))
		{
			print " <td bgcolor='#D00000' align='center'><font face='verdana,arial,helvetica' color='#FFFFFF' size='2'>$_</font>";
		} else { print " <td bgcolor='#00A000' align='center'><font face='verdana,arial,helvetica' color='#FFFFFF' size='2'>$_</font>"; }
		if ($is_supervisor)
		{
			if ((defined($acl{$_})) && ($acl{$_} eq 'on'))
			{
			print "</td><td width='120' align='center'>";
				print "<input type='submit' name='$_' value=' $Lang::tr{'advproxy mode allow'} '>";
			print "</td><td width='16' bgcolor='#D00000'>&nbsp;</td>\n";
			} else {
			print "</td><td width='120' align='center'>";
				print "<input type='submit' name='$_' value=' $Lang::tr{'advproxy mode deny'} '>";
			print "</td><td width='16' bgcolor='#00A000'>&nbsp;</td>\n";
			}
		}
		print "</tr>\n";
		print "</table>\n";
		print"<table width='65%' cellspacing='2' cellpadding='2' border='0' align='center'>";
		print "<tr><td></td></tr>\n";
		print "</table>\n";
	}

print <<END
            </td>
         </tr>
END
;
} else {
            print "      <tr>\n";
            print "         <td align='center'>\n";
            print "            <font face='verdana,arial,helvetica' color='#000000' size='2'>$Lang::tr{'advproxy no cre groups'}</font>\n";
            print "         </td>\n";
            print "      </tr>\n";
}
} else {
            print "      <tr>\n";
            print "         <td align='center'>\n";
            print "            <font face='verdana,arial,helvetica' color='#000000' size='2'>$Lang::tr{'advproxy cre disabled'}</font>\n";
            print "         </td>\n";
            print "      </tr>\n";
}

print <<END

      </table>
   </td>
</tr>


<tr>
   <td bgcolor='#C0C0C0' align='right'>
      <font face='verdana,arial,helvetica' color='#FFFFFF' size='1'>
      <a href='http://www.advproxy.net' target='_blank'>Advanced Proxy</a> running on
      <a href='http://www.ipfire.org' target='_blank'>IPFire</a>
      </font>
   </td>
</tr>

</table>

</form>

</center>

</body>

</html>
END
;

# -------------------------------------------------------------------

sub readhash
{
	my $filename = $_[0];
	my $hash = $_[1];
	my ($var, $val);

	if (-e $filename)
	{
		open(FILE, $filename) or die "Unable to read file $filename";
		while (<FILE>)
		{
			chop;
			($var, $val) = split /=/, $_, 2;
			if ($var)
			{
				$val =~ s/^\'//g;
				$val =~ s/\'$//g;
	
				# Untaint variables read from hash
				$var =~ /([A-Za-z0-9_-]*)/;        $var = $1;
				$val =~ /([\w\W]*)/; $val = $1;
				$hash->{$var} = $val;
			}
		}
		close FILE;
	}
}

# -------------------------------------------------------------------

sub getcgihash
{
	my ($hash, $params) = @_;
	my $cgi = CGI->new ();
	return if ($ENV{'REQUEST_METHOD'} ne 'POST');
	if (!$params->{'wantfile'}) {
		$CGI::DISABLE_UPLOADS = 1;
		$CGI::POST_MAX        = 512 * 1024;
	} else {
		$CGI::POST_MAX = 10 * 1024 * 1024;
	}

	$cgi->referer() =~ m/^https?\:\/\/([^\/]+)/;
	my $referer = $1;
	$cgi->url() =~ m/^https?\:\/\/([^\/]+)/;
	my $servername = $1;
	return if ($referer ne $servername);

	### Modified for getting multi-vars, split by |
	%temp = $cgi->Vars();
	foreach my $key (keys %temp) {
		$hash->{$key} = $temp{$key};
		$hash->{$key} =~ s/\0/|/g;
		$hash->{$key} =~ s/^\s*(.*?)\s*$/$1/;
	}

	if (($params->{'wantfile'})&&($params->{'filevar'})) {
		$hash->{$params->{'filevar'}} = $cgi->upload
					($params->{'filevar'});
	}
	return;
}

# -------------------------------------------------------------------

sub read_acl_groups
{
	undef(%acl);
	open (FILE,"$acl_src_noaccess_ips");
	my @aclgroups = <FILE>;
	close (FILE);
	foreach (@aclgroups)
	{
		chomp;
		if (/^\#/)
		{
			s/^\# //;
			$acl{$_}='on';
		}
	}
}

# -------------------------------------------------------------------

sub read_all_groups
{
	my $grpstr;

	open (FILE,"$group_def_file");
	@group_defs = <FILE>;
	close (FILE);

	undef(@groups);
	foreach (@group_defs)
	{
		chomp;
		if (/^\s*\[.*\]\s*$/)
		{
			$grpstr=$_;
			$grpstr =~ s/^\s*\[\s*//;
			$grpstr =~ s/\s*\]\s*$//;
			push(@groups,$grpstr);
		}
	}
}

# -------------------------------------------------------------------

sub write_acl
{
	my $is_blocked=0;

	open (FILE_IPS,">$acl_src_noaccess_ips");
	open (FILE_MAC,">$acl_src_noaccess_mac");
	flock (FILE_IPS, 2);
	flock (FILE_MAC, 2);
	foreach (@group_defs)
	{
		if (/^\s*\[.*\]\s*$/)
		{
			s/^\s*\[\s*//;
			s/\s*\]\s*$//;
			if ((defined($acl{$_})) && ($acl{$_} eq 'on'))
			{
				print FILE_IPS "# $_\n";
				print FILE_MAC "# $_\n";
				$is_blocked=1;
			} else { $is_blocked=0; }
		} elsif (($is_blocked) && ($_))
		{
			s/^\s+//g; s/\s+$//g;
			/^[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}$/i ? print FILE_MAC "$_\n" : print FILE_IPS "$_\n";
		}
	}

	close (FILE_IPS);
	close (FILE_MAC);
}

# -------------------------------------------------------------------
