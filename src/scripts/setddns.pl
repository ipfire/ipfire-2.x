#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: setddns.pl,v 1.4.2.55 2009/05/29 21:49:37 owes Exp $
#

#close(STDIN);
#close(STDOUT);
#close(STDERR);

use strict;
use IO::Socket;
use Net::SSLeay;

require '/var/ipfire/general-functions.pl';

#Prototypes functions
sub encode_base64 ($;$);

my %settings;
my $filename = "${General::swroot}/ddns/config";
my $logDirName = "/var/log/dyndns";
my @current = ();

if (open(FILE, "$filename")) {
	@current = <FILE>;
	close(FILE);
	unless(@current) {
		exit 0;
	}
} else {
	&General::log('Dynamic DNS failure : unable to open config file.');
	exit 0;
}

&General::readhash("${General::swroot}/ddns/settings", \%settings);

# ignore monthly update if not in minimize update mode
exit 0 if (($settings{'MINIMIZEUPDATES'} ne 'on') && ($ARGV[1] eq '-m'));

my $ip;
if (open(IP, "${General::swroot}/red/local-ipaddress")) {
	$ip = <IP>;
	close(IP);
	chomp $ip;
} else {
	&General::log('Dynamic DNS failure : unable to open local-ipaddress file.');
	exit 0;
}

# Do delete the the logdir before fetching IP (and write fetch IP state into logdir)
# On delete the fetch IP state is deleted too, but it gets rewritten on -force anyway
if ($ARGV[0] eq '-f') {
	# delete all cache files.
	# next regular calls will try again if this force update fails.
	system("/bin/rm -f $logDirName/*");
}

#If IP is reserved network, we are behind a router. May we ask for our real public IP ?
if ( &General::IpInSubnet ($ip,'10.0.0.0','255.0.0.0') ||
	&General::IpInSubnet ($ip,'172.16.0.0','255.240.0.0') ||
	&General::IpInSubnet ($ip,'192.168.0.0','255.255.0.0')) {
	# We can, but are we authorized by GUI ?
	if ($settings{'BEHINDROUTER'} eq 'FETCH_IP') {

		my %fetchIpState = ();
		$fetchIpState{'FETCHED_IP'} = "";
		$fetchIpState{'BEHINDROUTERWAITLOOP'} = -1;
		&General::readhash("$logDirName/fetchIpState", \%fetchIpState) if(-e "$logDirName/fetchIpState");

		if ($ARGV[0] eq '-f'){
			$fetchIpState{'BEHINDROUTERWAITLOOP'} = -1; # When forced option, fectch PublicIP now
		}

		# Increment counter modulo 4. When it is zero, fetch ip else exit
		# This divides by 4 the requests to the dyndns server.
		$fetchIpState{'BEHINDROUTERWAITLOOP'} = ($fetchIpState{'BEHINDROUTERWAITLOOP'}+1) %4;
		&General::writehash("$logDirName/fetchIpState", \%fetchIpState);

		exit 0 if ( $fetchIpState{'BEHINDROUTERWAITLOOP'} ne 0 );
		my $RealIP = &General::FetchPublicIp;
		$ip = (&General::validip ($RealIP) ?  $RealIP : 'unavailable');
		$fetchIpState{'FETCHED_IP'} = $ip;
		&General::writehash("$logDirName/fetchIpState", \%fetchIpState);
		&General::log ("Dynamic DNS public router IP is: $ip");
	}
}


foreach my $line (@current) {
	chomp($line);
	my @temp = split(/\,/,$line);
	next if ($temp[7] ne "on");

	$settings{'SERVICE'} = $temp[0];
	$settings{'HOSTNAME'} = $temp[1];
	$settings{'DOMAIN'} = $temp[2];
	$settings{'PROXY'} = $temp[3];
	$settings{'WILDCARDS'} = $temp[4];
	$settings{'LOGIN'} = $temp[5];
	$settings{'PASSWORD'} = $temp[6];
	$settings{'ENABLED'} = $temp[7];

	my $ipcache = 0;
	my $success = 0;
	my $ipCacheFile = "$logDirName/$settings{'SERVICE'}.$settings{'HOSTNAME'}.$settings{'DOMAIN'}";
	if(-e $ipCacheFile) {
		open(IPCACHE, $ipCacheFile);
		$ipcache = <IPCACHE>;
		close(IPCACHE);
		chomp $ipcache;
	}

	next if ($ip eq $ipcache);

	#Some connection are very stable (more than 40 days). Finally force
	#one update / month to avoid account lost
	#cron call once/week with -f & once/month with -f -m options
	#minimize update ?
	if ( ($settings{'MINIMIZEUPDATES'} eq 'on') && ($ARGV[1] ne '-m')) {
		if (General::DyndnsServiceSync($ip, $settings{'HOSTNAME'},$settings{'DOMAIN'})) {
			&General::log ("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} is uptodate [$ip]");

			# write cachefile (in case of -force the file is missing) otherwise the log
			# is filled up with "... is uptodate ..." messages every 5 minutes.
			open(IPCACHE, ">$ipCacheFile");
			flock IPCACHE, 2;
			print IPCACHE $ip;
			close(IPCACHE);

			next;		# do not update, go to test next service
		}
	}
	my @service = split(/\./, "$settings{'SERVICE'}");
	$settings{'SERVICE'} = "$service[0]";
	if ($settings{'SERVICE'} eq 'cjb') {
		# use proxy ?
		my %proxysettings;
		&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
		if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
			my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
			Net::SSLeay::set_proxy($peer,$peerport,$proxysettings{'UPSTREAM_USER'},$proxysettings{'UPSTREAM_PASSWORD'} );
		}

		my ($out, $response) = Net::SSLeay::get_http(  'www.cjb.net',
								80,
								"/cgi-bin/dynip.cgi?username=$settings{'LOGIN'}&password=$settings{'PASSWORD'}&ip=$ip",
								Net::SSLeay::make_headers('User-Agent' => 'Ipcop' )
								);
		#Valid responses from service are:
		# has been updated to point to
		if ($response =~ m%HTTP/1\.. 200 OK%) {
			if ( $out !~ m/has been updated to point to/ ) {
				&General::log("Dynamic DNS ip-update for cjb.net ($settings{'LOGIN'}) : failure (bad password or login)");
			} else {
				&General::log("Dynamic DNS ip-update for cjb.net ($settings{'LOGIN'}) : success");
				$success++;
			}
		} else {
			&General::log("Dynamic DNS ip-update for cjb.net ($settings{'LOGIN'}) : failure (could not connect to server)");
		}
	}
	# dhs.org=>ez-ipupdate
	elsif ($settings{'SERVICE'} eq 'dnsmadeeasy') {
		# use proxy ?
		my %proxysettings;
		&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
		if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
			my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
			Net::SSLeay::set_proxy($peer,$peerport,$proxysettings{'UPSTREAM_USER'},$proxysettings{'UPSTREAM_PASSWORD'} );
		}

		# replace the ';' with ',' because comma is the separator in the config file.
		$settings{'HOSTNAME'} =~ tr /;/,/;
		my ($out, $response) = Net::SSLeay::get_https(  'www.dnsmadeeasy.com',
								443,
								"/servlet/updateip?username=$settings{'LOGIN'}&password=$settings{'PASSWORD'}&id=$settings{'HOSTNAME'}&ip=$ip",
								Net::SSLeay::make_headers('User-Agent' => 'Ipcop' )
								);
		#Valid responses from service are:
		# success
		if ($response =~ m%HTTP/1\.. 200 OK%) {
			if ( $out !~ m/success/ ) {
				$out =~ s/\cM//g;
				&General::log("Dynamic DNS ip-update for dnsmadeeasy ID $settings{'HOSTNAME'} : failure ($out)");
			} else {
				&General::log("Dynamic DNS ip-update for dnsmadeeasy ID $settings{'HOSTNAME'} : success");
				$success++;
			}
		} else {
			&General::log("Dynamic DNS ip-update for dnsmadeeasy ID $settings{'HOSTNAME'} : failure (could not connect to server)");
		}
	}
	elsif ($settings{'SERVICE'} eq 'dnspark') {
		# use proxy ?
		my %proxysettings;
		&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
		if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
			my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
			Net::SSLeay::set_proxy($peer,$peerport,$proxysettings{'UPSTREAM_USER'},$proxysettings{'UPSTREAM_PASSWORD'} );
		}

		if ($settings{'HOSTNAME'} eq '') {
			$settings{'HOSTDOMAIN'} = $settings{'DOMAIN'};
		} else {
			$settings{'HOSTDOMAIN'} = "$settings{'HOSTNAME'}.$settings{'DOMAIN'}";
		}

		my ($out, $response) = Net::SSLeay::get_https(  "www.dnspark.net",
								443,
								"/api/dynamic/update.php?hostname=$settings{'HOSTDOMAIN'}&ip=$ip",
								Net::SSLeay::make_headers('User-Agent' => 'Ipcop',
											'Authorization' => 'Basic ' . encode_base64("$settings{'LOGIN'}:$settings{'PASSWORD'}")
								)
								);
		# Valid response are
		# 'ok'   'nochange'
		if ($response =~ m%HTTP/1\.. 200 OK%) {
			if ( $out !~ m/^(ok|nochange)/ ) {
				$out =~ s/\n/ /g;
				&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure ($out)");
			} else {
				&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : success");
				$success++;
			}
		} else {
			&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure (could not connect to server, check your credentials)");
		}
	}
	elsif ($settings{'SERVICE'} eq 'dtdns') {
		# use proxy ?
		my %proxysettings;
		&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
		if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
			my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
			Net::SSLeay::set_proxy($peer,$peerport,$proxysettings{'UPSTREAM_USER'},$proxysettings{'UPSTREAM_PASSWORD'} );
		}

		if ($settings{'HOSTNAME'} eq '') {
			$settings{'HOSTDOMAIN'} = $settings{'DOMAIN'};
		} else {
			$settings{'HOSTDOMAIN'} = "$settings{'HOSTNAME'}.$settings{'DOMAIN'}";
		}

		my ($out, $response) = Net::SSLeay::get_http(  'www.dtdns.com',
								80,
								"/api/autodns.cfm?id=$settings{'HOSTDOMAIN'}&pw=$settings{'PASSWORD'}",
								Net::SSLeay::make_headers('User-Agent' => 'Ipcop' )
								);
		#Valid responses from service are:
		#   now points to
		if ($response =~ m%HTTP/1\.. 200 OK%) {
			if ( $out !~ m/Host .* now points to/ig ) {
				&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure ($out)");
			} else {
				&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : success");
				$success++;
			}
		} else {
			&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure (could not connect to server)");
		}
	}
	# dyndns-custom,dyndns-static,dyndns.org,dyns.cx => ez-ipupdate
	elsif ($settings{'SERVICE'} eq 'dynu') {
		# use proxy ?
		my %proxysettings;
		&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
		if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
			my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
			Net::SSLeay::set_proxy($peer,$peerport,$proxysettings{'UPSTREAM_USER'},$proxysettings{'UPSTREAM_PASSWORD'} );
		}

		if ($settings{'HOSTNAME'} eq '') {
			$settings{'HOSTDOMAIN'} = $settings{'DOMAIN'};
		} else {
			$settings{'HOSTDOMAIN'} = "$settings{'HOSTNAME'}.$settings{'DOMAIN'}";
		}

		my ($out, $response) = Net::SSLeay::get_http(  'dynserv.ca',
								80,
								"/dyn/dynengine.cgi?func=set&name=$settings{'LOGIN'}&pass=$settings{'PASSWORD'}&ip=$ip&domain=$settings{'HOSTDOMAIN'}",
								Net::SSLeay::make_headers('User-Agent' => 'Ipcop' )
								);
		#Valid responses from service are:
		# 02 == Domain already exists, refreshing data for ... => xxx.xxx.xxx.xxx
		if ($response =~ m%HTTP/1\.. 200 OK%) {
			if ( $out !~ m/Domain already exists, refreshing data for/ig ) {
				&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure ($out)");
			} else {
				&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : success");
				$success++;
			}
		} else {
			&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure (could not connect to server)");
		}
	}
	# easydns => see 'ez-ipupdate'
	elsif ($settings{'SERVICE'} eq 'editdns') {
		# use proxy ?
		my %proxysettings;
		&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
		if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
			my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
			Net::SSLeay::set_proxy($peer,$peerport,$proxysettings{'UPSTREAM_USER'},$proxysettings{'UPSTREAM_PASSWORD'} );
		}
		if ($settings{'HOSTNAME'} eq '') {
			$settings{'HOSTDOMAIN'} = $settings{'DOMAIN'};
		} else {
			$settings{'HOSTDOMAIN'} = "$settings{'HOSTNAME'}.$settings{'DOMAIN'}";
		}

		my ($out, $response) = Net::SSLeay::get_http(  'dyndns.editdns.net',
								80,
								"/api/dynLinux.php?r=$settings{'HOSTDOMAIN'}&p=$settings{'PASSWORD'}",
								Net::SSLeay::make_headers('User-Agent' => 'Ipcop' )
								);
		#Valid responses from service are:
		# Record has been updated
		# Record already exists with the same IP
		if ($response =~ m%HTTP/1\.. 200 OK%) {
			if ( $out !~ m/Record (has been updated|already exists with the same IP)/ ) {
				&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure ($out)");
			} else {
				&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : success");
				$success++;
			}
		} else {
			&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure (could not connect to server)");
		}
	}
	elsif ($settings{'SERVICE'} eq 'enom') {
		# use proxy ?
		my %proxysettings;
		&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
		if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
			my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
			Net::SSLeay::set_proxy($peer,$peerport,$proxysettings{'UPSTREAM_USER'},$proxysettings{'UPSTREAM_PASSWORD'} );
		}
		if ($settings{'HOSTNAME'} eq '') {
			$settings{'HOSTDOMAIN'} = $settings{'DOMAIN'};
		} else {
			$settings{'HOSTDOMAIN'} = "$settings{'HOSTNAME'}.$settings{'DOMAIN'}";
		}

		my ($out, $response) = Net::SSLeay::get_http(  'dynamic.name-services.com',
								80,
								"/interface.asp?Command=SetDNSHost&Zone=$settings{'HOSTDOMAIN'}&DomainPassword=$settings{'PASSWORD'}&Address=$ip",
								Net::SSLeay::make_headers('User-Agent' => 'Ipcop' )
								);
		#Valid responses from service are:
		# ErrCount=0
		if ($response =~ m%HTTP/1\.. 200 OK%) {
			if ( $out !~ m/ErrCount=0/ ) {
				$out =~ s/(\n|\x0D)/ /g;
				$out =~ /Err1=([\w ]+)  /;
				&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure ($1)");
			} else {
				&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : success");
				$success++;
			}
		} else {
			&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure (could not connect to server)");
		}
	}
	elsif ($settings{'SERVICE'} eq 'everydns') {
		# use proxy ?
		my %proxysettings;
		&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
		if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
			my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
			Net::SSLeay::set_proxy($peer,$peerport,$proxysettings{'UPSTREAM_USER'},$proxysettings{'UPSTREAM_PASSWORD'} );
		}

		if ($settings{'HOSTNAME'} eq '') {
			$settings{'HOSTDOMAIN'} = $settings{'DOMAIN'};
		} else {
			$settings{'HOSTDOMAIN'} = "$settings{'HOSTNAME'}.$settings{'DOMAIN'}";
		}
		my $code64 = encode_base64("$settings{'LOGIN'}:$settings{'PASSWORD'}");
		my $version = "0.1"; # developped for this version of dyn server.

		my ($out, $response) = Net::SSLeay::get_http(  'dyn.everydns.net',
								80,
								"/index.php?ver=$version&ip=$ip&domain=$settings{'HOSTDOMAIN'}",
								Net::SSLeay::make_headers('User-Agent' => 'Ipcop',
											'Authorization' => "Basic $code64")
								);
		#Valid responses from service are:
		# "... Exit code: 0"    0:ok else error
		if ($response =~ m%HTTP/1\.. 200 OK%) {
			if ( $out !~ m/Exit code: 0/ig ) {
				&General::log("Dynamic DNS everydns for $settings{'HOSTDOMAIN'} : failure ($out)");
			} else {
				&General::log("Dynamic DNS everydns for $settings{'HOSTDOMAIN'} : success");
				$success++;
			}
		} else {
			&General::log("Dynamic DNS everydns for $settings{'HOSTDOMAIN'} : failure (could not connect to server)");
		}
	}
	elsif ($settings{'SERVICE'} eq 'freedns') {
		# use proxy ?
		my %proxysettings;
		&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
		if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
			my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
			Net::SSLeay::set_proxy($peer,$peerport,$proxysettings{'UPSTREAM_USER'},$proxysettings{'UPSTREAM_PASSWORD'} );
		}

		my ($out, $response) = Net::SSLeay::get_https(  'freedns.afraid.org',
								443,
								"/dynamic/update.php?$settings{'LOGIN'}",
								Net::SSLeay::make_headers('User-Agent' => 'Ipcop' )
								);
		#Valid responses from service are:
		# Updated n host(s) <domain>
		# ERROR: <ip> has not changed.
		if ($response =~ m%HTTP/1\.. 200 OK%) {
			if ( $out !~ m/(^Updated|Address .* has not changed)/ig ) {
				&General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : failure ($out)");
			} else {
				&General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : success");
				$success++;
			}
		} else {
			&General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : failure (could not connect to server)");
		}
	}
	elsif ($settings{'SERVICE'} eq 'namecheap') {
		# use proxy ?
		my %proxysettings;
		&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
		if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
			my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
			Net::SSLeay::set_proxy($peer,$peerport,$proxysettings{'UPSTREAM_USER'},$proxysettings{'UPSTREAM_PASSWORD'} );
		}

		my ($out, $response) = Net::SSLeay::get_https(  'dynamicdns.park-your-domain.com',
								443,
								"/update?host=$settings{'HOSTNAME'}&domain=$settings{'DOMAIN'}&password=$settings{'PASSWORD'}&ip=$ip",
								Net::SSLeay::make_headers('User-Agent' => 'Ipcop' )
								);
		#Valid responses from service are:
		# wait confirmation!!
		if ($response =~ m%HTTP/1\.. 200 OK%) {
			if ( $out !~ m/<ErrCount>0<\/ErrCount>/ ) {
				$out =~ m/<Err1>(.*)<\/Err1>/;
				&General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : failure ($1)");
			} else {
				&General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : success");
				$success++;
			}
		} else {
			&General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : failure (could not connect to server)");
		}
	}
	elsif ($settings{'SERVICE'} eq 'no-ip') {
		# use proxy ?
		my %proxysettings;
		&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
		if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
			my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
			Net::SSLeay::set_proxy($peer,$peerport,$proxysettings{'UPSTREAM_USER'},$proxysettings{'UPSTREAM_PASSWORD'} );
		}
		my $request = "username=$settings{'LOGIN'}&pass=$settings{'PASSWORD'}&ip=$ip";
		my $display;
		if ($settings{'HOSTNAME'} !~ s/$General::noipprefix//) {
			if ($settings{'HOSTNAME'} eq "") {
				$request .= "&h[]=$settings{'DOMAIN'}";
				$display = "$settings{'DOMAIN'}";
			} else {
				$request .= "&h[]=$settings{'HOSTNAME'}.$settings{'DOMAIN'}";
				$display = "$settings{'HOSTNAME'}.$settings{'DOMAIN'}";
			}
		} else {
			$request .= "&groupname=$settings{'HOSTNAME'}";
			$display = "group:$settings{'HOSTNAME'}";
		}
		$request = encode_base64($request,"");

		my ($out, $response) = Net::SSLeay::get_http(  'dynupdate.no-ip.com',
								80,
								"/ducupdate.php?requestL=$request",
								Net::SSLeay::make_headers('User-Agent' => 'IPCop/'.${General::version} )
								);

		if ($response =~ m%HTTP/1\.. 200 OK%) {
			# expected response format: [host].[domain]:[return_code]
			# example: myhost.example.com:0
			if ($out =~ m/:(.*)/) {
        	    if (($1 == 0) || ($1 == 11) || ($1 == 12)) {
					# 0 is success, 11 is success group, 12 is already set group
					&General::log("Dynamic DNS ip-update for $display : success");
					$success++;
        	    } else {
					&General::log("Dynamic DNS ip-update for $display : failure ($1)");
				}
			} else {
				&General::log("Dynamic DNS ip-update for $display : failure ($out)");
			}
		} else {
			&General::log("Dynamic DNS ip-update for $display : failure (could not connect to server)");
		}
	}
	elsif ($settings{'SERVICE'} eq 'nsupdate') {
		# Fetch UI configurable values and assemble the host name.

		my $hostName="$settings{'DOMAIN'}";
		if ($settings{'HOSTNAME'} ne "") {
			$hostName="$settings{'HOSTNAME'}.$hostName";
		}
		my $keyName=$settings{'LOGIN'};
		my $keySecret=$settings{'PASSWORD'};

		# Use a relatively long TTL value to reduce load on DNS.
		# Some public Dynamic DNS servers use values around 4 hours,
		# some use values as low as 60 seconds.
		# XXX Maybe we could fetch the master value from the server
		# (not the timed-down version supplied by DNS cache)

		my $timeToLive="3600";

		# Internal setting that can be used to override the DNS server
		# where the update is applied. It can be of use when testing
		# against a private DNS server.

		my $masterServer="";

		# Prepare the nsupdate command script to remove and re-add the
		# updated A record for the domain.

		my $cmdFile="/tmp/nsupdate-$hostName-commands";
		my $logFile="/tmp/nsupdate-$hostName-result";
		open(TF, ">$cmdFile");
		if ($masterServer ne "") {
			print TF "server $masterServer\n";
		}
		if ($keyName ne "" && $keySecret ne "") {
			print TF "key $keyName $keySecret\n";
		}
		print TF "update delete $hostName A\n";
		print TF "update add $hostName $timeToLive A $ip\n";
		print TF "send\n";
		close(TF);

		# Run nsupdate with -v to use TCP instead of UDP because we're
		# issuing multiple cmds and potentially long keys, and -d to
		# get diagnostic result output.

		my $result = system("/usr/bin/nsupdate -v -d $cmdFile 2>$logFile");
		if ($result != 0) {
			&General::log("Dynamic DNS ip-update for $hostName : failure");
			open(NSLOG, "$logFile");
			my @nsLog = <NSLOG>;
			close(NSLOG);
			my $logLine;
			foreach $logLine (@nsLog) {
				chomp($logLine);
				if ($logLine ne "") {
					&General::log("... $logLine");
				}
			}
		} else {
			&General::log("Dynamic DNS ip-update for $hostName : success");
			$success++;
		}
		unlink $cmdFile, $logFile;
	}
	# ods => ez-ipupdate
	elsif ($settings{'SERVICE'} eq 'opendns') {
		# use proxy ?
		my %proxysettings;
		&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
		if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
			my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
			Net::SSLeay::set_proxy($peer,$peerport,$proxysettings{'UPSTREAM_USER'},$proxysettings{'UPSTREAM_PASSWORD'} );
		}

		if ($settings{'HOSTNAME'} eq '') {
			$settings{'HOSTDOMAIN'} = $settings{'DOMAIN'};
		} else {
			$settings{'HOSTDOMAIN'} = "$settings{'HOSTNAME'}.$settings{'DOMAIN'}";
		}

		my ($out, $response) = Net::SSLeay::get_https(  "updates.opendns.com",
								443,
								"/account/ddns.php?hostname=$settings{'HOSTDOMAIN'}&myip=$ip",
								Net::SSLeay::make_headers('User-Agent' => 'Ipcop',
											'Authorization' => 'Basic ' . encode_base64("$settings{'LOGIN'}:$settings{'PASSWORD'}")
								)
								);
		#Valid responses from service are:
		# 'good ip-address' , 'nochg ip-address'  (ez-ipupdate like)
		if ($response =~ m%HTTP/1\.. 200 OK%)  {
			if ($out =~ m/good |nochg /ig) {
				&General::log("Dynamic DNS ip-update for opendns $settings{'HOSTDOMAIN'} : success");
				$success++;
			} else {
				&General::log("Dynamic DNS ip-update for opendns $settings{'HOSTDOMAIN'} : failure ($out)");
			}
		} elsif ( $out =~ m/<title>(.*)<\/title>/ig ) {
			&General::log("Dynamic DNS ip-update for opendns $settings{'HOSTDOMAIN'} : failure ($1)");
		} else {
			&General::log("Dynamic DNS ip-update for opendns $settings{'HOSTDOMAIN'} : failure ($response)");
		}
	}
	elsif ($settings{'SERVICE'} eq 'ovh') {
		# use proxy ?
		my %proxysettings;
		&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
		if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
			my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
			Net::SSLeay::set_proxy($peer,$peerport,$proxysettings{'UPSTREAM_USER'},$proxysettings{'UPSTREAM_PASSWORD'} );
		}
		if ($settings{'DOMAIN'} eq '') {
			$settings{'HOSTDOMAIN'} = $settings{'HOSTNAME'};
		} else {
			$settings{'HOSTDOMAIN'} = "$settings{'HOSTNAME'}.$settings{'DOMAIN'}";
		}

		my $code64 = encode_base64("$settings{'LOGIN'}:$settings{'PASSWORD'}");
		chomp($code64);
		my ($out, $response) = Net::SSLeay::get_https( 'www.ovh.com',
								443,
								"/nic/update?system=dyndns&hostname=$settings{'HOSTDOMAIN'}&myip=$ip",
								Net::SSLeay::make_headers('User-Agent' => 'Ipcop',
											'Authorization' => "Basic $code64" )
								);
		#Valid responses from service are:
		# 'good ip-address' , 'nochg ip-address'  (ez-ipupdate like)
		if ($response =~ m%HTTP/1\.. 200 OK%)  {
			if ($out =~ m/good |nochg /ig) {
				&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : success");
				$success++;
			} else {
				&General::log("Dynamic DNS ovh.com for $settings{'HOSTDOMAIN'} : failure ($out)");
			}
		} elsif ( $out =~ m/<title>(.*)<\/title>/ig ) {
			&General::log("Dynamic DNS ovh.com for $settings{'HOSTDOMAIN'} : failure ($1)");
		} else {
			&General::log("Dynamic DNS ovh.com for $settings{'HOSTDOMAIN'} : failure ($response)");
		}
	}
	elsif ($settings{'SERVICE'} eq 'regfish') {
		# use proxy ?
		my %proxysettings;
		&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
		if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
			my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
			Net::SSLeay::set_proxy($peer,$peerport,$proxysettings{'UPSTREAM_USER'},$proxysettings{'UPSTREAM_PASSWORD'} );
		}
		my ($out, $response) = Net::SSLeay::get_https(  'dyndns.regfish.de',
								443,
								"/?fqdn=$settings{'DOMAIN'}&ipv4=$ip&forcehost=1&authtype=secure&token=$settings{'LOGIN'}",
								Net::SSLeay::make_headers('User-Agent' => 'Ipfire' )
								);
		#Valid responses from service are:
		# success|100|update succeeded!
		# success|101|no update needed at this time..
		if ($response =~ m%HTTP/1\.. 200 OK%) {
			if ( $out !~ m/(success\|(100|101)\|)/ig ) {
				&General::log("Dynamic DNS ip-update for $settings{'DOMAIN'} : failure ($out)");
			} else {
				&General::log("Dynamic DNS ip-update for $settings{'DOMAIN'} : success");
				$success++;
			}
		} else {
			&General::log("Dynamic DNS ip-update for $settings{'DOMAIN'} : failure (could not connect to server)");
		}
	}
	elsif ($settings{'SERVICE'} eq 'registerfly') {
		# use proxy ?
		my %proxysettings;
		&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
		if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
			my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
			Net::SSLeay::set_proxy($peer,$peerport,$proxysettings{'UPSTREAM_USER'},$proxysettings{'UPSTREAM_PASSWORD'} );
		}

		my ($out, $response) = Net::SSLeay::get_https(  'dynamic.registerfly.com',
								443,
								"?domain=$settings{'DOMAIN'}&password=$settings{'PASSWORD'}&host=$settings{'HOSTNAME'}&ipaddress=$ip",
								Net::SSLeay::make_headers('User-Agent' => 'Ipcop' )
								);
		#Valid responses from service are:
		# <strong><b>Your Dynamic DNS change was accepted by our system</b></strong>
		if ($response =~ m%HTTP/1\.. 200 OK%) {
			if ( $out !~ m/DNS change was accepted/ig ) {
				$out =~ /<strong>(.*)<\/strong>/;
				&General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : failure ($1)");
			} else {
				&General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : success");
				$success++;
			}
		} else {
			&General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : failure (could not connect to server)");
		}
	}
	elsif ($settings{'SERVICE'} eq 'sitelutions') {
		# use proxy ?
		my %proxysettings;
		&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
		if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
			my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
			Net::SSLeay::set_proxy($peer,$peerport,$proxysettings{'UPSTREAM_USER'},$proxysettings{'UPSTREAM_PASSWORD'} );
		}

		my ($out, $response) = Net::SSLeay::get_https(  'www.sitelutions.com',
								443,
								"/dnsup?ttl=60&id=$settings{'HOSTNAME'}&user=$settings{'LOGIN'}&pass=$settings{'PASSWORD'}&ip=$ip",
								Net::SSLeay::make_headers('User-Agent' => 'Ipcop' )
								);
		#Valid responses from service are:
		# success
		if ($response =~ m%HTTP/1\.. 200 OK%) {
			if ( $out !~ m/(success)/ ) {
				$out =~ s/\n/ /g;
				&General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'} : failure ($out)");
			} else {
				&General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'} : success");
				$success++;
			}
		} else {
			&General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'} : failure (could not connect to server)");
		}
	}
	elsif ($settings{'SERVICE'} eq 'selfhost') {
		# use proxy ?
		my %proxysettings;
		&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
		if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
			my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
			Net::SSLeay::set_proxy($peer,$peerport,$proxysettings{'UPSTREAM_USER'},$proxysettings{'UPSTREAM_PASSWORD'} );
		}
		if ($settings{'DOMAIN'} eq '') {
			$settings{'HOSTDOMAIN'} = "selfhost.de ($settings{'LOGIN'})";
		} else {
			$settings{'HOSTDOMAIN'} = $settings{'DOMAIN'};
		}

		my ($out, $response) = Net::SSLeay::get_https(  'carol.selfhost.de',
								443,
								"/update?username=$settings{'LOGIN'}&password=$settings{'PASSWORD'}&textmodi=1",
								Net::SSLeay::make_headers('User-Agent' => 'Ipcop' )
								);
		#Valid responses from service are:
		# status=200  status=204
		if ($response =~ m%HTTP/1\.. 200 OK%) {
			if ( $out !~ m/status=(200|204)/ ) {
				$out =~ s/\n/ /g;
				&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure ($out)");
			} else {
				&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : success");
				$success++;
			}
		} else {
			&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure (could not connect to server)");
		}
	}
	# strato
	elsif ($settings{'SERVICE'} eq 'strato') {
		# use proxy ?
		my %proxysettings;
		&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
		if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
			my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
			Net::SSLeay::set_proxy($peer,$peerport,$proxysettings{'UPSTREAM_USER'},$proxysettings{'UPSTREAM_PASSWORD'} );
		}

		if ($settings{'HOSTNAME'} eq '') {
			$settings{'HOSTDOMAIN'} = $settings{'DOMAIN'};
		} else {
			$settings{'HOSTDOMAIN'} = "$settings{'HOSTNAME'}.$settings{'DOMAIN'}";
		}

		my ($out, $response) = Net::SSLeay::get_https(  "dyndns.strato.com",
								443,
								"/nic/update?hostname=$settings{'HOSTDOMAIN'}&myip=$ip",
											Net::SSLeay::make_headers('User-Agent' => 'Ipcop',
												'Authorization' => 'Basic ' . encode_base64("$settings{'LOGIN'}:$settings{'PASSWORD'}")
											)
							);
		# Valid response are 'ok'   'nochange'
		if ($response =~ m%HTTP/1\.. 200 OK%)  {
			if ($out =~ m/good |nochg /ig) {
				&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : success");
				$success++;
			} else {
				&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure ($out)");
			}
		} elsif ( $out =~ m/<title>(.*)<\/title>/ig ) {
			&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure ($1)");
		} else {
			&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure ($response)");
		}
	}
   elsif ($settings{'SERVICE'} eq 'tiggerswelt') {
      $settings{'HOSTDOMAIN'} = "$settings{'HOSTNAME'}.$settings{'DOMAIN'}";

      my ($out, $response) = Net::SSLeay::get_https(   "ssl.tiggerswelt.net",
                        443,
                        "/nic/update?hostname=$settings{'HOSTDOMAIN'}&myip=$ip",
                                 Net::SSLeay::make_headers('User-Agent' => 'IPCop',
                                    'Authorization' => 'Basic ' . encode_base64("$settings{'LOGIN'}:$settings{'PASSWORD'}")
                                 )
                     );

      if ($response =~ m%HTTP/1\.. 200 OK%) {
         if ($out =~ m/good |nochg /ig) {
            &General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'}: success");
            $success++;
         } else {
            &General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'}: failure ($out)");
         }
      } else {
         &General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'}: failure ($response)");
      }
   }
	# zonedit => see 'ez-ipupdate'
	else {
		if ($settings{'WILDCARDS'} eq 'on') {
			$settings{'WILDCARDS'} = '-w';
		} else {
			$settings{'WILDCARDS'} = '';
		}
		if (($settings{'SERVICE'} eq 'dyndns-custom' ||
			$settings{'SERVICE'} eq 'easydns' ||
			$settings{'SERVICE'} eq 'zoneedit') && $settings{'HOSTNAME'} eq '') {
			$settings{'HOSTDOMAIN'} = $settings{'DOMAIN'};
		} else {
			$settings{'HOSTDOMAIN'} = "$settings{'HOSTNAME'}.$settings{'DOMAIN'}";
		}
		my @ddnscommand = ('/usr/bin/ez-ipupdate', '-a', "$ip", '-S', "$settings{'SERVICE'}", '-u', "$settings{'LOGIN'}:$settings{'PASSWORD'}", '-h', "$settings{'HOSTDOMAIN'}", "$settings{'WILDCARDS'}", '-q');
		my $result = system(@ddnscommand);
		if ( $result != 0) {
			&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'}: failure");
		} else {
			&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'}: success");
			$success++;
		}
	}
	# DEBUG:
	#print "Success: $success, file: $ipCacheFile\n";
	# write current IP to specific cache file
	if ($success == 1) {
		open(IPCACHE, ">$ipCacheFile");
		flock IPCACHE, 2;
		print IPCACHE $ip;
		close(IPCACHE);
	}
}
exit 0;

# Extracted from Base64.pm
sub encode_base64 ($;$) {
	my $res = "";
	my $eol = $_[1];
	$eol = "\n" unless defined $eol;
	pos($_[0]) = 0;                          # ensure start at the beginning
	while ($_[0] =~ /(.{1,45})/gs) {
		$res .= substr(pack('u', $1), 1);
		chop($res);
	}
	$res =~ tr|` -_|AA-Za-z0-9+/|;               # `# help emacs
	# fix padding at the end
	my $padding = (3 - length($_[0]) % 3) % 3;
	$res =~ s/.{$padding}$/'=' x $padding/e if $padding;
	# break encoded string into lines of no more than 76 characters each
	if (length $eol) {
		$res =~ s/(.{1,76})/$1$eol/g;
	}
	$res;
}
