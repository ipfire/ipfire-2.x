#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: setddns.pl,v 1.4.2.32 2006/02/07 01:29:47 franck78 Exp $
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
my $cachefile = "${General::swroot}/ddns/ipcache";
my $ipcache = 0;
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

my $ip = &General::GetDyndnsRedIP();

if ($ip eq "unavailable") {
	&General::log("Dynamic DNS error: RED/Public IP is unavailable");
	exit(0);
}

&General::log("Dynamic DNS public router IP is: $ip");

if ($ARGV[0] eq '-f') {
	unlink ($cachefile);	# next regular calls will try again if this force update fails.
} else {
	open(IPCACHE, "$cachefile");
	$ipcache = <IPCACHE>;
	close(IPCACHE);
	chomp $ipcache;
}

if ($ip ne $ipcache) {
	my $id = 0;
	my $success = 0;
	my $line;
	my $lines = @current;

	foreach $line (@current) {
		$id++;
		chomp($line);
		my @temp = split(/\,/,$line);
		unless ($temp[7] ne "on") {
			$settings{'SERVICE'} = $temp[0];
			$settings{'HOSTNAME'} = $temp[1];
			$settings{'DOMAIN'} = $temp[2];
			$settings{'PROXY'} = $temp[3];
			$settings{'WILDCARDS'} = $temp[4];
			$settings{'LOGIN'} = $temp[5];
			$settings{'PASSWORD'} = $temp[6];
			$settings{'ENABLED'} = $temp[7];

			#Some connection are very stable (more than 40 days). Finally force
			#one update / month to avoid account lost
			#cron call once/week with -f & once/month with -f -m options
			#minimize update ?
			if ( ($settings{'MINIMIZEUPDATES'} eq 'on') && ($ARGV[1] ne '-m') ) {
			    if (General::DyndnsServiceSync($ip, $settings{'HOSTNAME'},$settings{'DOMAIN'})) {
				&General::log ("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} is uptodate [$ip]");
				$success++;
				next;		# do not update, go to test next service
			    }
			}
			if ($settings{'SERVICE'} ne "dns.lightningwirelabs.com") {
				my @service = split(/\./, "$settings{'SERVICE'}");
				$settings{'SERVICE'} = "$service[0]";
			}
			if ($settings{'SERVICE'} eq 'no-ip') {
				open(F, ">${General::swroot}/ddns/noipsettings");
				flock F, 2;
				print F "PROXY=" . ($settings{'PROXY'} eq 'on' ? "Y\n" : "N\n");
				print F "PASSWORD=$settings{'PASSWORD'}\n";
				print F "NAT=N\n";
				print F "LOGIN=$settings{'LOGIN'}\n";
				print F "INTERVAL=1\n";
				if ($settings{'HOSTNAME'} !~ s/$General::noipprefix//) {
	    			    print F "HOSTNAME=$settings{'HOSTNAME'}\n";
				    print F "GROUP=\n";
				} else {
    				    print F "HOSTNAME=\n";
				    print F "GROUP=$settings{'HOSTNAME'}\n";
				}
				print F "DOMAIN=$settings{'DOMAIN'}\n";
				print F "DEVICE=\n";
				print F "DAEMON=N\n";
				close(F);

				my @ddnscommand = ('/usr/bin/noip','-c',"${General::swroot}/ddns/noipsettings",'-i',"$ip");

				my $result = system(@ddnscommand);
				if ( $result != 0) { 
					&General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : failure");
				} else {
					&General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : success");
					$success++;
				}
			}

			elsif ($settings{'SERVICE'} eq 'all-inkl') {
			    my %proxysettings;
			    &General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
			    if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
				my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
				Net::SSLeay::set_proxy($peer,$peerport,$proxysettings{'UPSTREAM_USER'},$proxysettings{'UPSTREAM_PASSWORD'} );
			    }

			    my ($out, $response) = Net::SSLeay::get_https("dyndns.kasserver.com", 443, "/", Net::SSLeay::make_headers(
					'User-Agent' => 'IPFire', 'Authorization' => 'Basic ' . encode_base64("$settings{'LOGIN'}:$settings{'PASSWORD'}")
			    ));

			    # Valid response are 'ok'   'nochange'
			    if ($response =~ m%HTTP/1\.. 200 OK%) {
				&General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : success");
				$success++;
			    } else {
			        &General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : failure (could not connect to server, check your credentials)");
			    }
			}

			elsif ($settings{'SERVICE'} eq 'cjb') {
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
	                						    Net::SSLeay::make_headers('User-Agent' => 'IPFire' )
									 );

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
			elsif ($settings{'SERVICE'} eq 'selfhost') {
			    # use proxy ?
			    my %proxysettings;
			    &General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
			    if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
				my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
				Net::SSLeay::set_proxy($peer,$peerport,$proxysettings{'UPSTREAM_USER'},$proxysettings{'UPSTREAM_PASSWORD'} );
			    }

			    my ($out, $response) = Net::SSLeay::get_https(  'carol.selfhost.de',
									    443,
									    "/update?username=$settings{'LOGIN'}&password=$settings{'PASSWORD'}&textmodi=1",
	                						    Net::SSLeay::make_headers('User-Agent' => 'IPFire' )
									 );

			    if ($response =~ m%HTTP/1\.. 200 OK%) {
				if ( $out !~ m/status=(200|204)/ ) {
				    $out =~ s/\n/ /g;
				    &General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : failure ($out)");
				} else {
				    &General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : success");
				    $success++;
				}
			    } else {
			        &General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : failure (could not connect to server)");
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
	                						    Net::SSLeay::make_headers('User-Agent' => 'IPFire',
												      'Authorization' => 'Basic ' . encode_base64("$settings{'LOGIN'}:$settings{'PASSWORD'}")
									     )
									 );
			    # Valid response are 'ok'   'nochange'
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
			elsif ($settings{'SERVICE'} eq 'dns.lightningwirelabs.com') {
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

			    my $authstring;
			    if ($settings{'LOGIN'} eq "token") {
			        $authstring = "token=$settings{'PASSWORD'}";
			    } else {
			        $authstring = "username=$settings{'LOGIN'}&password=$settings{'PASSWORD'}";
			    }

			    my $user_agent = &General::MakeUserAgent();
			    my ($out, $response) = Net::SSLeay::get_https("dns.lightningwirelabs.com", 443,
				"/update?hostname=$settings{'HOSTDOMAIN'}&address4=$ip&$authstring",
				Net::SSLeay::make_headers('User-Agent' => $user_agent)
			    );

			    # Valid response are 'ok'   'nochange'
			    if ($response =~ m%HTTP/1\.. 200 OK%) {
				&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : success");
				$success++;
			    } else {
			        &General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure (could not connect to server, check your credentials)");
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
									    "/interface.asp?Command=SetDNSHost&Zone=$settings{'DOMAIN'}&DomainPassword=$settings{'PASSWORD'}&Address=$ip",
	                						    Net::SSLeay::make_headers('User-Agent' => 'IPFire' )
									 );

			    if ($response =~ m%HTTP/1\.. 200 OK%) {
            			#Valid responses from update => ErrCount=0
				if ( $out !~ m/ErrCount=0/ ) {
                                    $out =~ s/(\n|\x0D)/ /g;
				    $out =~ /Err1=([\w ]+)  /;
				    &General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : failure ($1)");
				} else {
				    &General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : success");
				    $success++;
				}
			    } else {
			        &General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : failure (could not connect to server)");
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
	                						    Net::SSLeay::make_headers('User-Agent' => 'IPFire' )
									 );
			    #Valid responses from service are:
                            #Updated n host(s) <domain>
                            #ERROR: <ip> has not changed.
			    if ($response =~ m%HTTP/1\.. 200 OK%) {
            			#Valid responses from update => ErrCount=0
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
                        elsif ($settings{'SERVICE'} eq 'spdns.de') {
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
                            
                            my ($out, $response) = Net::SSLeay::get_https( 'www.spdns.de', 443,
                                                                            "/nic/update?&hostname=$settings{'HOSTDOMAIN'}&myip=$ip",
                                                                            Net::SSLeay::make_headers('User-Agent' => 'IPFire' ,
                                                                                                      'Authorization' => 'Basic ' . encode_base64("$settings{'LOGIN'}:$settings{'PASSWORD'}"))
                                                                         );
                            
                            #Valid responses from service are:
                            # good xxx.xxx.xxx.xxx
                            # nochg  xxx.xxx.xxx.xxx
                            if ($response =~ m%HTTP/1\.. 200 OK%) {
                                if ($out !~ m/good |nochg /ig) {
                                    &General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure ($out)");
                                } else {
                                    &General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : success");
                                    $success++;
                                }
                            } else {
                                &General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure (could not connect to server)");
                            }
                        }
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

				my ($out, $response) = Net::SSLeay::get_https(  'dyndns.strato.com',
									    443,
									    "/nic/update?hostname=$settings{'HOSTDOMAIN'}&myip=$ip",
	                						    Net::SSLeay::make_headers('User-Agent' => 'IPFire',
									     'Authorization' => 'Basic ' . encode_base64("$settings{'LOGIN'}:$settings{'PASSWORD'}") )
									 );

				if ($response =~ m%HTTP/1\.. 200 OK%) {
					#Valid responses from update => ErrCount=0
					if ( $out =~ m/good |nochg /ig) {
						&General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : success");
						$success++;
					} else {
						&General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : failure1 ($out)");
						$success++;
					}
				} elsif ( $out =~ m/<title>(.*)<\/title>/ig ) {
					&General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : failure2 ($1)");
				} else {
					&General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : failure3 ($response)");
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
			    #success|100|update succeeded!
			    #success|101|no update needed at this time..
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
			elsif ($settings{'SERVICE'} eq 'ovh') {
				my %proxysettings;
				&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);

				my $peer = 'www.ovh.com';
				my $peerport = 80;

				if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
					($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
				}

				my $sock;
				unless($sock = new IO::Socket::INET (PeerAddr => $peer, PeerPort => $peerport, Proto => 'tcp', Timeout => 5)) {
					&General::log("Dynamic DNS failure : could not connect to $peer:$peerport: $@");
					next;
				}

				if ($settings{'HOSTNAME'} eq '') {
					$settings{'HOSTDOMAIN'} = $settings{'DOMAIN'};
				} else {
					$settings{'HOSTDOMAIN'} = "$settings{'HOSTNAME'}.$settings{'DOMAIN'}";
				}

				my ($GET_CMD, $code64);
				$GET_CMD  = "GET http://www.ovh.com/nic/update?system=dyndns&hostname=$settings{'HOSTDOMAIN'}&myip=$ip HTTP/1.1\r\n";
				$GET_CMD .= "Host: www.ovh.com\r\n";
				chomp($code64 = encode_base64("$settings{'LOGIN'}:$settings{'PASSWORD'}"));
				$GET_CMD .= "Authorization: Basic $code64\r\n";
			        $GET_CMD .= "User-Agent: ipfire\r\n";
			       #$GET_CMD .= "Content-Type: application/x-www-form-urlencoded\r\n";
				$GET_CMD .= "\r\n";
				print $sock "$GET_CMD";
																												
				my $out = '';
				while(<$sock>) {
					$out .= $_;
				}
				close($sock);

                                #HTTP response => error (in  Title tag) else text response
			        #Valid responses from service:good,nochg  (ez-ipupdate like)
				#Should use ez-ipdate but "system=dyndns" is not present
				if ( $out =~ m/<Title>(.*)<\/Title>/ig ) {
					&General::log("Dynamic DNS ovh.com : failure ($1)");
				}
				elsif ($out !~ m/good |nochg /ig) {
					$out =~ s/.+?\015?\012\015?\012//s;    # header HTTP
					my @out = split("\r", $out);
					&General::log("Dynamic DNS ip-update for $settings{'DOMAIN'} : failure ($out[1])");
				} else {
				        &General::log("Dynamic DNS ip-update for $settings{'DOMAIN'} : success");
					$success++;
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
	                						    Net::SSLeay::make_headers('User-Agent' => 'IPFire' )
									 );
			    #Valid responses from service are:
			    #   now points to
			    #
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
			#namecheap test
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
								Net::SSLeay::make_headers('User-Agent' => 'IPFire' )
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
			#end namecheap test
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
									    "/dyn/dynengine.cgi?func=set&name=$settings{'LOGIN'}&pass=$settings{'PASSWORD'}&ip=$ip&domain=$settings{'DOMAIN'}",
	                						    Net::SSLeay::make_headers('User-Agent' => 'IPFire' )
									 );
			    #Valid responses from service are:
			    # 02 == Domain already exists, refreshing data for ... => xxx.xxx.xxx.xxx
			    #
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
			elsif ($settings{'SERVICE'} eq 'udmedia.de') {
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

			    my ($out, $response) = Net::SSLeay::get_https( 'www.udmedia.de',
									    443,
									    "/nic/update?myip=$ip&username=$settings{'HOSTDOMAIN'}&password=$settings{'PASSWORD'}",
									    Net::SSLeay::make_headers('User-Agent' => 'IPFire',
												      'Authorization' => 'Basic ' . encode_base64("$settings{'LOGIN'}:$settings{'PASSWORD'}")) );

			    # Valid response are 'ok'   'nochange'
			    if ($response =~ m%HTTP/1\.. 200 OK%) {
				if ( $out !~ m/^(ok|nochg)/ ) {
				    $out =~ s/\n/ /g;
				    &General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure ($out)");
				} else {
				    &General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : success");
				    $success++;
				}
			    } else {
				&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure (could not connect to server, check your credentials---$out-$response--)");
			    }
			}
                        elsif ($settings{'SERVICE'} eq 'twodns.de') {
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

                            my ($out, $response) = Net::SSLeay::get_https( 'update.twodns.de',
                                                                            443,
									    "/update?hostname=$settings{'HOSTDOMAIN'}&ip=$ip",
                                                                            Net::SSLeay::make_headers('User-Agent' => 'IPFire',
                                                                                                      'Authorization' => 'Basic ' . encode_base64("$settings{'LOGIN'}:$settings{'PASSWORD'}")) );

                            # Valid response are 'ok'   'nochange'
                            if ($response =~ m%HTTP/1\.. 200 OK%) {
                                if ( $out !~ m/^(good|nochg)/ ) {
                                    $out =~ s/\n/ /g;
                                    &General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure ($out)");
                                } else {
                                    &General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : success");
                                    $success++;
                                }
                            } else {
                                &General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure (could not connect to server, check your credentials---$out-$response--)");
                            }
                        }
			elsif ($settings{'SERVICE'} eq 'variomedia') { 
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
 
 			    my ($out, $response) = Net::SSLeay::get_https( 'dyndns.variomedia.de',
 									    443,
 									    "/nic/update?hostname=$settings{'HOSTDOMAIN'}&myip=$ip",
 									    Net::SSLeay::make_headers('User-Agent' => 'IPFire',
 												      'Authorization' => 'Basic ' . encode_base64("$settings{'LOGIN'}:$settings{'PASSWORD'}")) );
 
 			    # Valid response is 'good $ip'
 			    if ($response =~ m%HTTP/1\.. 200 OK%) {
 				if ( $out !~ m/^good $ip/ ) {
 				    &General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} ($ip) : failure ($out)");
 				} else {
 				    &General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} ($ip) : success");
 				    $success++;
 				}
 			    } else {
 				&General::log("Dynamic DNS ip-update for $settings{'HOSTDOMAIN'} : failure (could not connect to server, check your credentials---$out-$response--)");
 			    }
 			}
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
		} else {
			# If a line is disabled, then we should discount it
			$lines--;
		}
	}

	if ($lines == $success) {
		open(IPCACHE, ">$cachefile");
		flock IPCACHE, 2;
		print IPCACHE $ip;
		close(IPCACHE);
		exit 1;
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



__END__
old code for selfhost.de

				my %proxysettings;
				&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);

				my $peer = 'carol.selfhost.de';
				my $peerport = 80;

				if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
				    ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
				}

				my $sock;
				unless($sock = new IO::Socket::INET (PeerAddr => $peer, PeerPort => $peerport, Proto => 'tcp', Timeout => 5)) {
				    die "Could not connect to $peer:$peerport: $@";
				    return 1;
				}

			        my $GET_CMD;
				$GET_CMD  = "GET https://carol.selfhost.de/update?username=$settings{'LOGIN'}&password=$settings{'PASSWORD'}&myip=$ip&textmodi=1 HTTP/1.1\r\n";
				$GET_CMD .= "Host: carol.selfhost.de\r\n";
			        $GET_CMD .= "User-Agent: ipfire\r\n";
				$GET_CMD .= "Connection: close\r\n\r\n";
				print $sock "$GET_CMD";

				my $out = '';
				while(<$sock>) {
					$out .= $_;
				}
				close($sock);

				if ( $out !~ m/status=(200|204)/ ) {
					#cleanup http response...
					$out =~ s/.+?\015?\012\015?\012//s;    # header HTTP
					my @out = split("\r", $out);
					&General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : failure ($out[1])");
				} else {
					&General::log("Dynamic DNS ip-update for $settings{'HOSTNAME'}.$settings{'DOMAIN'} : success");
					$success++;
				}


			
