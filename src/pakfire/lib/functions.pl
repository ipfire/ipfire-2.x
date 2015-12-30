#!/usr/bin/perl -w
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2015   IPFire Team   <info@ipfire.org>                   #
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

require "/opt/pakfire/etc/pakfire.conf";
require "/var/ipfire/general-functions.pl";

use File::Basename;
use File::Copy;
use LWP::UserAgent;
use HTTP::Response;
use HTTP::Headers;
use HTTP::Message;
use HTTP::Request;
use Net::Ping;

package Pakfire;

# GPG Keys
my $myid = "64D96617";			# Our own gpg-key paks@ipfire.org
my $trustid = "65D0FD58";		# gpg-key of CaCert

# A small color-hash :D
my %color;
	$color{'normal'}      = "\033[0m"; 
	$color{'black'}       = "\033[0;30m";
	$color{'darkgrey'}    = "\033[1;30m";
	$color{'blue'}        = "\033[0;34m";
	$color{'lightblue'}   = "\033[1;34m";
	$color{'green'}       = "\033[0;32m";
	$color{'lightgreen'}  = "\033[1;32m";
	$color{'cyan'}        = "\033[0;36m";
	$color{'lightcyan'}   = "\033[1;36m";
	$color{'red'}         = "\033[0;31m";
	$color{'lightred'}    = "\033[1;31m";
	$color{'purple'}      = "\033[0;35m";
	$color{'lightpurple'} = "\033[1;35m";
	$color{'brown'}       = "\033[0;33m";
	$color{'lightgrey'}   = "\033[0;37m";
	$color{'yellow'}      = "\033[1;33m";
	$color{'white'}       = "\033[1;37m";
our $enable_colors = 1;

my $final_data;
my $total_size;
my $bfile;

my %pakfiresettings = ();
&General::readhash("${General::swroot}/pakfire/settings", \%pakfiresettings);

sub message {
	my $message = shift;
		
	logger("$message");
	if ( $enable_colors == 1 ) {
		if ("$message" =~ /ERROR/) {
			$message = "$color{'red'}$message$color{'normal'}";
		} elsif ("$message" =~ /INFO/) {
			$message = "$color{'cyan'}$message$color{'normal'}";
		} elsif ("$message" =~ /WARN/) {
			$message = "$color{'yellow'}$message$color{'normal'}";
		} elsif ("$message" =~ /RESV/) {
			$message = "$color{'purple'}$message$color{'normal'}";
		} elsif ("$message" =~ /INST/) {
			$message = "$color{'green'}$message$color{'normal'}";
		} elsif ("$message" =~ /REMV/) {
			$message = "$color{'lightred'}$message$color{'normal'}";
		} elsif ("$message" =~ /UPGR/) {
			$message = "$color{'lightblue'}$message$color{'normal'}";
		}
	}
	print "$message\n";
	
}

sub logger {
	my $log = shift;
	if ($log) {
		#system("echo \"`date`: $log\" >> /var/log/pakfire.log");
		system("logger -t pakfire \"$log\"");
	}
}

sub usage {
  &Pakfire::message("Usage: pakfire <install|remove> [options] <pak(s)>");
  &Pakfire::message("               <update> - Contacts the servers for new lists of paks.");
  &Pakfire::message("               <upgrade> - Installs the latest version of all paks.");
  &Pakfire::message("               <list> - Outputs a short list with all available paks.");
  &Pakfire::message("");
  &Pakfire::message("       Global options:");
  &Pakfire::message("               --non-interactive --> Enables the non-interactive mode.");
  &Pakfire::message("                                     You won't see any question here.");
  &Pakfire::message("                              -y --> Short for --non-interactive.");
  &Pakfire::message("                     --no-colors --> Turns off the wonderful colors.");
  &Pakfire::message("");
  exit 1;
}

sub pinghost {
	my $host = shift;
	
	$p = Net::Ping->new("icmp");
  if ($p->ping($host)) {
 	 logger("PING INFO: $host is alive");
  	return 1;
  } else {
		logger("PING INFO: $host is unreachable");
		return 0;
	}
  $p->close();
}

sub fetchfile {
	my $getfile = shift;
	my $gethost = shift;
	my (@server, $host, $proto, $file, $i);
	my $allok = 0;
	
	use File::Basename;
	$bfile = basename("$getfile");
	
	logger("DOWNLOAD STARTED: $getfile") unless ($bfile =~ /^counter\?.*/);

	$i = 0;	
	while (($allok == 0) && $i < 5) {
		$i++;
		
		if ("$gethost" eq "") {
			@server = selectmirror();
			$proto = $server[0];
			$host = $server[1];
			$file = "$server[2]/$getfile";
		} else {
			$host = $gethost;
			$file = $getfile;
		}
		
		$proto = "HTTP" unless $proto;
		
		unless ($bfile =~ /^counter\?.*/) {
			logger("DOWNLOAD INFO: Host: $host ($proto) - File: $file");
		}

		my $ua = LWP::UserAgent->new;
		$ua->agent("Pakfire/$Conf::version");
		$ua->timeout(20);
		
		my %proxysettings=();
		&General::readhash("${General::swroot}/proxy/advanced/settings", \%proxysettings);

		if ($proxysettings{'UPSTREAM_PROXY'}) {
			logger("DOWNLOAD INFO: Upstream proxy: \"$proxysettings{'UPSTREAM_PROXY'}\"") unless ($bfile =~ /^counter.py\?.*/); 
			if ($proxysettings{'UPSTREAM_USER'}) {
				$ua->proxy("http","http://$proxysettings{'UPSTREAM_USER'}:$proxysettings{'UPSTREAM_PASSWORD'}@"."$proxysettings{'UPSTREAM_PROXY'}/");
				logger("DOWNLOAD INFO: Logging in with: \"$proxysettings{'UPSTREAM_USER'}\" - \"$proxysettings{'UPSTREAM_PASSWORD'}\"") unless ($bfile =~ /^counter.py\?.*/);
			} else {
				$ua->proxy("http","http://$proxysettings{'UPSTREAM_PROXY'}/");
			}
		}

		$final_data = undef;
	 	my $url = "http://$host/$file";
		my $response;
		
		unless ($bfile =~ /^counter.py\?.*/) {
			my $result = $ua->head($url);
			my $remote_headers = $result->headers;
			$total_size = $remote_headers->content_length;
			logger("DOWNLOAD INFO: $file has size of $total_size bytes");
			
			$response = $ua->get($url, ':content_cb' => \&callback );
			message("");
		} else {
			$response = $ua->get($url);
		}
		
		my $code = $response->code();
		my $log = $response->status_line;
		logger("DOWNLOAD INFO: HTTP-Status-Code: $code - $log");
		
		if ( $code eq "500" ) {
			message("Giving up: There was no chance to get the file \"$getfile\" from any available server.\nThere was an error on the way. Please fix it.");
			return 1;
		}
		
		if ($response->is_success) {
			unless ($bfile =~ /^counter.py\?.*/) {
				if (open(FILE, ">$Conf::tmpdir/$bfile")) {
					print FILE $final_data;
					close(FILE);
					logger("DOWNLOAD INFO: File received. Start checking signature...");
					if (system("gpg --verify \"$Conf::tmpdir/$bfile\" &>/dev/null") eq 0) {
						logger("DOWNLOAD INFO: Signature of $bfile is fine.");
						move("$Conf::tmpdir/$bfile","$Conf::cachedir/$bfile");
					} else {
						message("DOWNLOAD ERROR: The downloaded file ($file) wasn't verified by IPFire.org. Sorry - Exiting...");
						my $ntp = `ntpdate -q -t 10 pool.ntp.org 2>/dev/null | tail -1`;
						if ( $ntp !~ /time\ server(.*)offset(.*)/ ){message("TIME ERROR: Unable to get the nettime, this may lead to the verification error.");}
						else { $ntp =~ /time\ server(.*)offset(.*)/; message("TIME INFO: Time Server$1has$2 offset to localtime.");}
						exit 1;
					}
					logger("DOWNLOAD FINISHED: $file");
					$allok = 1;
					return 0;
				} else {
					logger("DOWNLOAD ERROR: Could not open $Conf::tmpdir/$bfile for writing.");
				}
			} else {
				return 0;
			}
		}	else {
			logger("DOWNLOAD ERROR: $log");
		}
	}
	message("DOWNLOAD ERROR: There was no chance to get the file \"$getfile\" from any available server.\nMay be you should run \"pakfire update\" to get some new servers.");
	return 1;
}

sub getmirrors {
	my $force = shift;
	my $age;
	
	use File::Copy;
	
	if ( -e "$Conf::dbdir/lists/server-list.db" ) {
		my @stat = stat("$Conf::dbdir/lists/server-list.db");
		my $time = time();
		$age = $time - $stat[9];
		$force = "force" if ("$age" >= "3600");
		logger("MIRROR INFO: server-list.db is $age seconds old. - DEBUG: $force");
	} else {
		# Force an update.
		$force = "force";
	}
	
	if ("$force" eq "force") {
		fetchfile("$Conf::version/lists/server-list.db", "$Conf::mainserver");
		move("$Conf::cachedir/server-list.db", "$Conf::dbdir/lists/server-list.db");
	}
}

sub getcoredb {
	my $force = shift;
	my $age;
	
	use File::Copy;
	
	if ( -e "$Conf::dbdir/lists/core-list.db" ) {
		my @stat = stat("$Conf::dbdir/lists/core-list.db");
		my $time = time();
		$age = $time - $stat[9];
		$force = "force" if ("$age" >= "3600");
		logger("CORE INFO: core-list.db is $age seconds old. - DEBUG: $force");
	} else {
		# Force an update.
		$force = "force";
	}
	
	if ("$force" eq "force") {
		fetchfile("lists/core-list.db", "");
		move("$Conf::cachedir/core-list.db", "$Conf::dbdir/lists/core-list.db");
	}
}


sub selectmirror {
	### Check if there is a current server list and read it.
	#   If there is no list try to get one.
	my $count = 0;
	while (!(open(FILE, "<$Conf::dbdir/lists/server-list.db")) && ($count lt 5)) {
		$count++;
		getmirrors("noforce");
	}
	if ($count == 5) {
		message("MIRROR ERROR: Could not find or download a server list");
		exit 1;
	}
	my @lines = <FILE>;
	close(FILE);

	### Count the number of the servers in the list
	my $scount = 0;
	my @newlines;
	foreach (@lines) {
		if ("$_" =~ /.*;.*;.*;/ ) {
			push(@newlines,$_);
			$scount++;
		}
	}
	logger("MIRROR INFO: $scount servers found in list");

	if ($scount eq 0) {
		logger("MIRROR INFO: Could not find any servers. Falling back to main server $Conf::mainserver");
		return ("HTTP", $Conf::mainserver, "/$Conf::version");
	}

	### Choose a random server and test if it is online
	#   If the check fails try a new server.
	#   This will never give up.
	my $found = 0;
	my $servers = 0;
	my $pingdelay = 1;
	while ($found == 0) {
		$server = int(rand($scount) + 1);
		$servers = 0;
		my ($line, $proto, $path, $host);
		my @templine;
		foreach $line (@newlines) {
			$servers++;
			if ($servers eq $server) {
				@templine = split(/\;/, $line);
				$proto = $templine[0];
				$host = $templine[1];
				$path = $templine[2];
				if ($pakfiresettings{'HEALTHCHECK'} eq "off") {
				 	logger("PING INFO: Healthcheck is disabled");
					$found = 1;
					return ($proto, $host, $path);
				}
				elsif (pinghost("$host")) {
					$found = 1;
					return ($proto, $host, $path);
				}
				if ($found == 0) {
					sleep($pingdelay);
					$pingdelay=$pingdelay*2;
					if ($pingdelay>1200) {
						$pingdelay=1200;
					}
				}
			}
		}
	}
}

sub dbgetlist {
	### Update the database if the file is older than one day.
	#   If you pass &Pakfire::dbgetlist(force) the list will be downloaded.
	#   Usage is always with an argument.
	my $force = shift;
	my $age;
	
	use File::Copy;
	
	if ( -e "$Conf::dbdir/lists/packages_list.db" ) {
		my @stat = stat("$Conf::dbdir/lists/packages_list.db");
		my $time = time();
		$age = $time - $stat[9];
		$force = "force" if ("$age" >= "3600");
		logger("DB INFO: packages_list.db is $age seconds old. - DEBUG: $force");
	} else {
		# Force an update.
		$force = "force";
	}
	
	if ("$force" eq "force") {
		fetchfile("lists/packages_list.db", "");
		move("$Conf::cachedir/packages_list.db", "$Conf::dbdir/lists/packages_list.db");
	}

	# Update the meta database if new packages was in the package list
	my @meta;
	my $file;
	my $line;
	my $prog;
	my ($name, $version, $release);
	my @templine;

	open(FILE, "<$Conf::dbdir/lists/packages_list.db");
	my @db = <FILE>;
	close(FILE);

	opendir(DIR,"$Conf::dbdir/meta");
	my @files = readdir(DIR);
	closedir(DIR);
	foreach $file (@files) {
		next if ( $file eq "." );
		next if ( $file eq ".." );
		next if ( $file eq "meta-" );
		next if ( $file =~ /^old/ );
		open(FILE, "<$Conf::dbdir/meta/$file");
		@meta = <FILE>;
		close(FILE);
		foreach $line (@meta) {
			@templine = split(/\: /,$line);
			if ("$templine[0]" eq "Name") {
				$name = $templine[1];
				chomp($name);
			} elsif ("$templine[0]" eq "ProgVersion") {
				$version = $templine[1];
				chomp($version);
			} elsif ("$templine[0]" eq "Release") {
				$release = $templine[1];
				chomp($release);
			}
		}
		foreach $prog (@db) {
			@templine = split(/\;/,$prog);
			if (("$name" eq "$templine[0]") && ("$release" ne "$templine[2]")) {
				move("$Conf::dbdir/meta/meta-$name","$Conf::dbdir/meta/old_meta-$name");
				fetchfile("meta/meta-$name", "");
				move("$Conf::cachedir/meta-$name", "$Conf::dbdir/meta/meta-$name");
			}
		}
	}
}

sub dblist {
	### This subroutine lists the packages.
	#   You may also pass a filter: &Pakfire::dblist(filter) 
	#   Usage is always with two arguments.
	#   filter may be: all, notinstalled, installed
	my $filter = shift;
	my $forweb = shift;
	my @meta;
	my @updatepaks;
	my $file;
	my $line;
	my $prog;
	my ($name, $version, $release);
	my @templine;
	
	### Make sure that the list is not outdated. 
	#dbgetlist("noforce");

	open(FILE, "<$Conf::dbdir/lists/packages_list.db");
	my @db = <FILE>;
	close(FILE);

	if ("$filter" eq "upgrade") {
		if ("$forweb" ne "forweb" && "$forweb" ne "notice" ) {getcoredb("noforce");}
		eval(`grep "core_" $Conf::dbdir/lists/core-list.db`);
		if ("$core_release" > "$Conf::core_mine") {
			if ("$forweb" eq "forweb") {
				print "<option value=\"core\">Core-Update -- $Conf::version -- Release: $Conf::core_mine -> $core_release</option>\n";
			}
			elsif ("$forweb" eq "notice") {
				print "<br /><br /><br /><a href='pakfire.cgi'>$Lang::tr{'core notice 1'} $Conf::core_mine $Lang::tr{'core notice 2'} $core_release $Lang::tr{'core notice 3'}</a>";
			} else {
				my $command = "Core-Update $Conf::version\nRelease: $Conf::core_mine -> $core_release\n";
				if ("$Pakfire::enable_colors" eq "1") {
					print "$color{'lila'}$command$color{'normal'}\n";
				} else {
					print "$command\n";
				}
			}
		}
	
		opendir(DIR,"$Conf::dbdir/installed");
		my @files = readdir(DIR);
		closedir(DIR);
		foreach $file (@files) {
			next if ( $file eq "." );
			next if ( $file eq ".." );
			next if ( $file =~ /^old/ );
			open(FILE, "<$Conf::dbdir/installed/$file");
			@meta = <FILE>;
			close(FILE);
			foreach $line (@meta) {
				@templine = split(/\: /,$line);
				if ("$templine[0]" eq "Name") {
					$name = $templine[1];
					chomp($name);
				} elsif ("$templine[0]" eq "ProgVersion") {
					$version = $templine[1];
					chomp($version);
				} elsif ("$templine[0]" eq "Release") {
					$release = $templine[1];
					chomp($release);
				}
			}
			foreach $prog (@db) {
				@templine = split(/\;/,$prog);
				if (("$name" eq "$templine[0]") && ("$release" < "$templine[2]" && "$forweb" ne "notice")) {
					push(@updatepaks,$name);
					if ("$forweb" eq "forweb") {
						print "<option value=\"$name\">Update: $name -- Version: $version -> $templine[1] -- Release: $release -> $templine[2]</option>\n";
					} else {
						my $command = "Update: $name\nVersion: $version -> $templine[1]\nRelease: $release -> $templine[2]\n";
						if ("$Pakfire::enable_colors" eq "1") {
							print "$color{'lila'}$command$color{'normal'}\n";
						} else {
							print "$command\n";
						}
					}
				}
			}
		}
		return @updatepaks;
	} else {
		my $line;
		my $use_color;
		my @templine;
		my $count;
		foreach $line (sort @db) {
			next unless ($line =~ /.*;.*;.*;/ );
			$use_color = "";
			$count++;
			@templine = split(/\;/,$line);
			if ("$filter" eq "notinstalled") {
				next if ( -e "$Conf::dbdir/installed/meta-$templine[0]" );
			} elsif ("$filter" eq "installed") {
				next unless ( -e "$Conf::dbdir/installed/meta-$templine[0]" );
			}
			if ("$forweb" eq "forweb")
			 {
				if ("$filter" eq "notinstalled") {
					print "<option value=\"$templine[0]\">$templine[0]-$templine[1]-$templine[2]</option>\n";
				} else {
					print "<option value=\"$templine[0]\">$templine[0]</option>\n";
				}
			} else {
				if ("$Pakfire::enable_colors" eq "1") {
					if (&isinstalled("$templine[0]")) {
						$use_color = "$color{'red'}" 
					} else {
						$use_color = "$color{'green'}"
					}
				}
				print "${use_color}Name: $templine[0]\nProgVersion: $templine[1]\nRelease: $templine[2]$color{'normal'}\n\n";
			}
		}
		print "$count packages total.\n" unless ("$forweb" eq "forweb");
	}
}

sub resolvedeps {
	my $pak = shift;
	
	getmetafile("$pak");
	
	message("PAKFIRE RESV: $pak: Resolving dependencies...");
	
	open(FILE, "<$Conf::dbdir/meta/meta-$pak");
	my @file = <FILE>;
	close(FILE);
	
	my $line;
	my (@templine, @deps, @tempdeps, @all);
	foreach $line (@file) {
		@templine = split(/\: /,$line);
		if ("$templine[0]" eq "Dependencies") {
			@deps = split(/ /, $templine[1]);
		}
	}
	chomp (@deps);
	foreach (@deps) {
		if ($_) {
		  my $return = &isinstalled($_);
		  if ($return eq 0) {
		  	message("PAKFIRE RESV: $pak: Dependency is already installed: $_");
		  } else {
		  	message("PAKFIRE RESV: $pak: Need to install dependency: $_");
				push(@tempdeps,$_);
				push(@all,$_);
			} 
		}
	}

	foreach (@tempdeps) {
		if ($_) {
			my @newdeps = resolvedeps("$_");
			foreach(@newdeps) {
				unless (($_ eq " ") || ($_ eq "")) {
					my $return = &isinstalled($_);
					if ($return eq 0) {
						message("PAKFIRE RESV: $pak: Dependency is already installed: $_");
					} else {
						message("PAKFIRE RESV: $pak: Need to install dependency: $_");
						push(@all,$_);
					}
				}
			}
		}
	}
	message("");
	chomp (@all);
	return @all;
}

sub resolvedeps_recursive {
	my @packages = @_;
	my @result = ();

	foreach my $pkg (@packages) {
		my @deps = &Pakfire::resolvedeps($pkg);

		foreach my $dep (@deps) {
			push(@result, $dep);
		}
	}

	# Sort the result array and remove dupes
	my %sort = map{ $_, 1 } @result;
	@result = keys %sort;

	return @result;
}

sub cleanup {
	my $dir = shift;
	my $path;
	
	logger("CLEANUP: $dir");
	
	if ( "$dir" eq "meta" ) {
		$path = "$Conf::dbdir/meta";
	} elsif ( "$dir" eq "tmp" ) {
		$path = "$Conf::tmpdir";
	}
	chdir("$path");
	opendir(DIR,".");
	my @files = readdir(DIR);
	closedir(DIR);
	foreach (@files) {
	  unless (($_ eq ".") || ($_ eq "..")) {
		   system("rm -rf $_");
		}
	}
}

sub getmetafile {
	my $pak = shift;
	
	unless ( -e "$Conf::dbdir/meta/meta-$pak" ) {
		fetchfile("meta/meta-$pak", "");
		move("$Conf::cachedir/meta-$pak", "$Conf::dbdir/meta/meta-$pak");
	}
	
	if ( -z "$Conf::dbdir/meta/meta-$pak" ) {
		fetchfile("meta/meta-$pak", "");
		move("$Conf::cachedir/meta-$pak", "$Conf::dbdir/meta/meta-$pak");
	}
	
	open(FILE, "<$Conf::dbdir/meta/meta-$pak");
	my @line = <FILE>;
	close(FILE);
	
	open(FILE, ">$Conf::dbdir/meta/meta-$pak");
	foreach (@line) {
		my $string = $_;
		$string =~ s/\r\n/\n/g;
		print FILE $string;
	}
	close(FILE);
	return 1;
}

sub getsize {
	my $pak = shift;
	
	getmetafile("$pak");
	
	open(FILE, "<$Conf::dbdir/meta/meta-$pak");
	my @file = <FILE>;
	close(FILE);
	
	my $line;
	my @templine;
	foreach $line (@file) {
		@templine = split(/\: /,$line);
		if ("$templine[0]" eq "Size") {
			chomp($templine[1]);
			return $templine[1];
		}
	}
	return 0;
}

sub decryptpak {
	my $pak = shift;
	
	cleanup("tmp");
	
	my $file = getpak("$pak", "noforce");
	
	logger("DECRYPT STARTED: $pak");
	my $return = system("cd $Conf::tmpdir/ && gpg -d --batch --quiet --no-verbose --status-fd 2 --output - < $Conf::cachedir/$file 2>/dev/null | tar x");
	$return %= 255;
	logger("DECRYPT FINISHED: $pak - Status: $return");
	if ($return != 0) { exit 1; }
}

sub getpak {
	my $pak = shift;
	my $force = shift;

	getmetafile("$pak");
	
	open(FILE, "<$Conf::dbdir/meta/meta-$pak");
	my @file = <FILE>;
	close(FILE);
	
	my $line;
	my $file;
	my @templine;
	foreach $line (@file) {
		@templine = split(/\: /,$line);
		if ("$templine[0]" eq "File") {
			chomp($templine[1]);
			$file = $templine[1];
		}
	}
	
	unless ($file) {
		message("No filename given in meta-file.");
		exit 1;
	}
	
	unless ( "$force" eq "force" ) {
		if ( -e "$Conf::cachedir/$file" ) {
			return $file;
		}
	}
	
	fetchfile("paks/$file", "");
	return $file;
}

sub setuppak {
	my $pak = shift;
	
	message("PAKFIRE INST: $pak: Decrypting...");
	decryptpak("$pak");
	
	message("PAKFIRE INST: $pak: Copying files and running post-installation scripts...");
	my $return = system("cd $Conf::tmpdir && NAME=$pak ./install.sh >> $Conf::logdir/install-$pak.log 2>&1");
	$return %= 255;
	if ($pakfiresettings{'UUID'} ne "off") {
		fetchfile("counter.py?ver=$Conf::version&uuid=$Conf::uuid&ipak=$pak&return=$return", "$Conf::mainserver");
	}
	if ($return == 0) {
	  move("$Conf::tmpdir/ROOTFILES", "$Conf::dbdir/rootfiles/$pak");
	  cleanup("tmp");
	  copy("$Conf::dbdir/meta/meta-$pak","$Conf::dbdir/installed/");
		message("PAKFIRE INST: $pak: Finished.");
		message("");
	} else {
		message("PAKFIRE ERROR: Returncode: $return. Sorry. Please search our forum to find a solution for this problem.");
		exit $return;
	}
	return $return;
}

sub upgradecore {
	getcoredb("noforce");
	eval(`grep "core_" $Conf::dbdir/lists/core-list.db`);
	if ("$core_release" > "$Conf::core_mine") {
		message("CORE UPGR: Upgrading from release $Conf::core_mine to $core_release");
		
		my @seq = `seq $Conf::core_mine $core_release`;
		shift @seq;
		my $release;
		foreach $release (@seq) {
			chomp($release);
			getpak("core-upgrade-$release");
		}
		
		foreach $release (@seq) {
			chomp($release);
			upgradepak("core-upgrade-$release");
		}
		
		system("echo $core_release > $Conf::coredir/mine");
		
	} else {
		message("CORE ERROR: No new upgrades available. You are on release $Conf::core_mine.");
	}
}

sub isinstalled {
	my $pak = shift;
	if ( open(FILE,"<$Conf::dbdir/installed/meta-$pak") ) {
		close(FILE);
		return 0;
	} else {
		return 1;
	}
}

sub upgradepak {
	my $pak = shift;

	message("PAKFIRE UPGR: $pak: Decrypting...");
	decryptpak("$pak");

	message("PAKFIRE UPGR: $pak: Upgrading files and running post-upgrading scripts...");
	my $return = system("cd $Conf::tmpdir && NAME=$pak ./update.sh >> $Conf::logdir/update-$pak.log 2>&1");
	$return %= 255;
	if ($pakfiresettings{'UUID'} ne "off") {
		fetchfile("counter.py?ver=$Conf::version&uuid=$Conf::uuid&upak=$pak&return=$return", "$Conf::mainserver");
	}
	if ($return == 0) {
	  move("$Conf::tmpdir/ROOTFILES", "$Conf::dbdir/rootfiles/$pak");
	  cleanup("tmp");
		copy("$Conf::dbdir/meta/meta-$pak", "$Conf::dbdir/installed/");
		message("PAKFIRE UPGR: $pak: Finished.");
		message("");
	} else {
		message("PAKFIRE ERROR: Returncode: $return. Sorry. Please search our forum to find a solution for this problem.");
		exit $return;
	}
	return $return;
}

sub removepak {
	my $pak = shift;

	message("PAKFIRE REMV: $pak: Decrypting...");
	decryptpak("$pak");

	message("PAKFIRE REMV: $pak: Removing files and running post-removing scripts...");
	my $return = system("cd $Conf::tmpdir && NAME=$pak ./uninstall.sh >> $Conf::logdir/uninstall-$pak.log 2>&1");
	$return %= 255;
	if ($pakfiresettings{'UUID'} ne "off") {
		fetchfile("counter.py?ver=$Conf::version&uuid=$Conf::uuid&dpak=$pak&return=$return", "$Conf::mainserver");
	}
	if ($return == 0) {
	  unlink("$Conf::dbdir/rootfiles/$pak");
	  unlink("$Conf::dbdir/installed/meta-$pak");
	  cleanup("tmp");
		message("PAKFIRE REMV: $pak: Finished.");
		message("");
	} else {
		message("PAKFIRE ERROR: Returncode: $return. Sorry. Please search our forum to find a solution for this problem.");
		exit $return;
	}
	return $return;
}

sub beautifysize {
	my $size = shift;
	#$size = $size / 1024;
	my $unit;
	
	if ($size > 1023*1024) {
	  $size = ($size / (1024*1024));
	  $unit = "MB";
	} elsif ($size > 1023) {
	  $size = ($size / 1024);
	  $unit = "KB";
	} else {
	  $unit = "B";
	}
	$size = sprintf("%.2f" , $size);
	my $string = "$size $unit";
	return $string;
}

sub makeuuid {
	unless ( -e "$Conf::dbdir/uuid" ) {
		open(FILE, "</proc/sys/kernel/random/uuid");
		my @line = <FILE>;
		close(FILE);
		
		open(FILE, ">$Conf::dbdir/uuid");
		foreach (@line) {
			print FILE $_;
		}
		close(FILE);
	}
}

sub senduuid {
	if ($pakfiresettings{'UUID'} ne "off") {
		unless("$Conf::uuid") {
			$Conf::uuid = `cat $Conf::dbdir/uuid`;
		}
		logger("Sending my uuid: $Conf::uuid");
		fetchfile("counter.py?ver=$Conf::version&uuid=$Conf::uuid", "$Conf::mainserver");
		system("rm -f $Conf::tmpdir/counter* 2>/dev/null");
	}
}

sub checkcryptodb {
	logger("CRYPTO INFO: Checking GnuPG Database");
	my $ret = system("gpg --list-keys | grep -q $myid");
	unless ( "$ret" eq "0" ) {
		message("CRYPTO WARN: The GnuPG isn't configured corectly. Trying now to fix this.");
		message("CRYPTO WARN: It's normal to see this on first execution.");
		message("CRYPTO WARN: If this message is being shown repeatedly, check if time and date are set correctly, and if IPFire can connect via port 11371 TCP.");
		my $command = "gpg --keyserver pgp.ipfire.org --always-trust --status-fd 2";
		system("$command --recv-key $myid >> $Conf::logdir/gnupg-database.log 2>&1");
		system("$command --recv-key $trustid >> $Conf::logdir/gnupg-database.log 2>&1");
	} else {
		logger("CRYPTO INFO: Database is okay");
	}
}

sub callback {
   my ($data, $response, $protocol) = @_;
   $final_data .= $data;
   print progress_bar( length($final_data), $total_size, 30, '=' );
}

sub progress_bar {
    my ( $got, $total, $width, $char ) = @_;
    my $show_bfile;
    $width ||= 30; $char ||= '=';
    my $len_bfile = length $bfile;
    if ("$len_bfile" >= "17") {
			$show_bfile = substr($bfile,0,17)."...";
		} else {
			$show_bfile = $bfile;
		}	
		$progress = sprintf("%.2f%%", 100*$got/+$total);
    sprintf "$color{'lightgreen'}%-20s %7s |%-${width}s| %10s$color{'normal'}\r",$show_bfile, $progress, $char x (($width-1)*$got/$total). '>', beautifysize($got);
}

1;
