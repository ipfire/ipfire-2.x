#!/usr/bin/perl -w
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2022   IPFire Team   <info@ipfire.org>                   #
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
use URI;

use Switch;

package Pakfire;

my @VALID_KEY_FINGERPRINTS = (
	# 2018
	"3ECA8AA4478208B924BB96206FEF7A8ED713594B",
	# 2007
	"179740DC4D8C47DC63C099C74BDE364C64D96617",
);

# A small color-hash :D
our %color;
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

# Make version
$Conf::version = &make_version();

# Pakfire lock file.
our $lockfile = "/tmp/pakfire_lock";

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
  &Pakfire::message("               <list> [installed/notinstalled/upgrade] - Outputs a list with all, installed, available or upgradeable paks.");
  &Pakfire::message("               <status> - Outputs a summary about available core upgrades, updates and a required reboot");
  &Pakfire::message("");
  &Pakfire::message("       Global options:");
  &Pakfire::message("               --non-interactive --> Enables the non-interactive mode.");
  &Pakfire::message("                                     You won't see any question here.");
  &Pakfire::message("                              -y --> Short for --non-interactive.");
  &Pakfire::message("                     --no-colors --> Turns off the wonderful colors.");
  &Pakfire::message("");
  exit 1;
}

sub fetchfile {
	my $getfile = shift;
	my $gethost = shift;
	my (@server, $host, $proto, $file, $i);
	my $allok = 0;

	use File::Basename;
	$bfile = basename("$getfile");

	logger("DOWNLOAD STARTED: $getfile");

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

		$proto = "HTTPS" unless $proto;

		logger("DOWNLOAD INFO: Host: $host ($proto) - File: $file");

		# Init LWP::UserAgent, request SSL hostname verification
		# and specify CA file.
		my $ua = LWP::UserAgent->new(
			ssl_opts => {
				SSL_ca_file     => '/etc/ssl/cert.pem',
				verify_hostname => 1,
			}
		);
		$ua->agent("Pakfire/$Conf::version");
		$ua->timeout(20);

		my %proxysettings=();
		&General::readhash("${General::swroot}/proxy/advanced/settings", \%proxysettings);

		if ($proxysettings{'UPSTREAM_PROXY'}) {
			logger("DOWNLOAD INFO: Upstream proxy: \"$proxysettings{'UPSTREAM_PROXY'}\"");
			if ($proxysettings{'UPSTREAM_USER'}) {
				$ua->proxy(["http", "https"], "http://$proxysettings{'UPSTREAM_USER'}:$proxysettings{'UPSTREAM_PASSWORD'}@"."$proxysettings{'UPSTREAM_PROXY'}/");
				logger("DOWNLOAD INFO: Logging in with \"$proxysettings{'UPSTREAM_USER'}\" against \"$proxysettings{'UPSTREAM_PROXY'}\"");
			} else {
				$ua->proxy(["http", "https"], "http://$proxysettings{'UPSTREAM_PROXY'}/");
			}
		}

		$final_data = undef;

		my $url;
		switch ($proto) {
			case "HTTP" { $url = "http://$host/$file"; }
			case "HTTPS" { $url = "https://$host/$file"; }
			else {
				# skip all lines with unknown protocols
				logger("DOWNLOAD WARNING: Skipping Host: $host due to unknown protocol ($proto) in mirror database");
				next;
			}
		}

		my $result = $ua->head($url);
		my $remote_headers = $result->headers;
		$total_size = $remote_headers->content_length;
		logger("DOWNLOAD INFO: $file has size of $total_size bytes");

		my $response = $ua->get($url, ':content_cb' => \&callback );
		message("");

		my $code = $response->code();
		my $log = $response->status_line;
		logger("DOWNLOAD INFO: HTTP-Status-Code: $code - $log");

		if ( $code eq "500" ) {
			message("Giving up: There was no chance to get the file \"$getfile\" from any available server.\nThere was an error on the way. Please fix it.");
			return 0;
		}

		if ($response->is_success) {
			if (open(FILE, ">$Conf::tmpdir/$bfile")) {
				print FILE $final_data;
				close(FILE);
				logger("DOWNLOAD INFO: File received. Start checking signature...");
				if (&valid_signature("$Conf::tmpdir/$bfile")) {
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
				return 1;
			} else {
				logger("DOWNLOAD ERROR: Could not open $Conf::tmpdir/$bfile for writing.");
			}
		} else {
			logger("DOWNLOAD ERROR: $log");
		}
	}
	message("DOWNLOAD ERROR: There was no chance to get the file \"$getfile\" from any available server.\nMay be you should run \"pakfire update\" to get some new servers.");
	return 0;
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
		if (fetchfile("$Conf::version/lists/server-list.db", "$Conf::mainserver")) {
			move("$Conf::cachedir/server-list.db", "$Conf::dbdir/lists/server-list.db");
		} elsif (! -e "$Conf::dbdir/lists/server-list.db" ) {
			# if we end up with no server-list at all, return failure
			return 0;
		}
	}
	return 1;
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
		if (fetchfile("lists/core-list.db", "")) {
			move("$Conf::cachedir/core-list.db", "$Conf::dbdir/lists/core-list.db");
		}
	}
}

sub valid_signature($) {
	my $filename = shift;

	open(my $cmd, "gpg --verify --status-fd 1 \"$filename\" 2>/dev/null |");
	while (<$cmd>) {
		# Process valid signature lines
		if (/VALIDSIG ([A-Z0-9]+)/) {
			# Check if we know the key
			foreach my $key (@VALID_KEY_FINGERPRINTS) {
				# Signature is valid
				return 1 if ($key eq $1);
			}
		}
	}
	close($cmd);

	# Signature is invalid
	return 0;
}

sub selectmirror {
	if (defined ${Conf::mirror}) {
		my $uri = URI->new("${Conf::mirror}");

		# Only accept HTTPS mirrors
		if ($uri->scheme eq "https") {
			return ("HTTPS", $uri->host, $uri->path . "/" . ${Conf::version});
		} else {
			message("MIRROR ERROR: Unsupported mirror: " . ${Conf::mirror});
		}
	}

	### Check if there is a current server list and read it.
	#   If there is no list try to get one.
	unless (open(FILE, "<$Conf::dbdir/lists/server-list.db")) {
		unless (getmirrors("noforce")) {
			message("MIRROR ERROR: Could not find or download a server list");
			exit 1;
		}
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
		return ("HTTPS", $Conf::mainserver, "/$Conf::version");
	}

	### Choose a random server and test if it is online
	#   If the check fails try a new server.
	#   This will never give up.
	my $servers = 0;
	while (1) {
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

				return ($proto, $host, $path);
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
		if (fetchfile("lists/packages_list.db", "")) {
			move("$Conf::cachedir/packages_list.db", "$Conf::dbdir/lists/packages_list.db");
		} elsif ( -e "$Conf::dbdir/lists/packages_list.db" ) {
			# If we end up with no db file after download error there
			# is nothing more we can do here.
			return 0;
		}
	}

	# Update the meta database if new packages was in the package list
	my $file;
	my $line;
	my $prog;
	my %metadata;
	my @templine;

    my %paklist = &Pakfire::dblist("all");

	opendir(DIR,"$Conf::dbdir/meta");
	my @files = readdir(DIR);
	closedir(DIR);
	foreach $file (@files) {
		next if ( $file eq "." );
		next if ( $file eq ".." );
		next if ( $file eq "meta-" );
		next if ( $file =~ /^old/ );
		%metadata = parsemetafile("$Conf::dbdir/meta/$file");

		if ((defined $paklist{"$metadata{'Name'}"}) && (
			("$paklist{\"$metadata{'Name'}\"}{'Release'}" ne "$metadata{'Release'}") ||
			(defined $paklist{"$metadata{'Name'}"}{'AvailableRelease'}))
		   ) {
			move("$Conf::dbdir/meta/meta-$metadata{'Name'}","$Conf::dbdir/meta/old_meta-$metadata{'Name'}");
			getmetafile($metadata{'Name'});
		}
	}
}

sub coredbinfo {
	### This subroutine returns core db version information in a hash.
	# Usage is without arguments

	eval(`grep "core_" $Conf::dbdir/lists/core-list.db`);

	my %coredb = (
		CoreVersion => $Conf::version,
		Release => $Conf::core_mine,
	);

	$coredb{'AvailableRelease'} = $core_release if ("$Conf::core_mine" < "$core_release");

	return %coredb;
}

sub dblist {
	### This subroutine returns the packages from the packages_list db in a hash.
	#   It uses the currently cached version of packages_list. To ensure latest 
	#   data, run Pakfire::dbgetlist first.
	#   You may also pass a filter: &Pakfire::dblist(filter) 
	#   Usage is always with one argument.
	#   filter may be: 
	#		- "all": list all known paks,
	#		- "notinstalled": list only not installed paks,
	#		- "installed": list only installed paks
	#		- "upgrade": list only upgradable paks
	#
	#   Returned hash format:
    #   ( "<pak name>" => (
	#       "Installed" => "Yes" or "No" wether the pak is installed,
	#       "ProgVersion" => Installed program version when "Installed" => "Yes" or
    #                        Available version when "Installed" => No,
	#       "Release" => Installed pak release number when "Installed" => "Yes" or
    #                    Available pak release number when "Installed" => No,
	#       "AvailableProgVersion" => Available program version. 
	#                                 Only defined if an upgrade to a higher version is available,
	#       "AvailableRelease" => Available pak release version. 
	#                             Only defined if an upgrade to a higher version is available
	#	  ),
	#	  ...	
	#   )
	
	my $filter = shift;
	my %paklist = ();
	my $file;
	my $line;
	my %metadata;
	my @templine;
	
	open(FILE, "<$Conf::dbdir/lists/packages_list.db");
	my @db = <FILE>;
	close(FILE);

	if ("$filter" ne "notinstalled") {
		opendir(DIR,"$Conf::dbdir/installed");
		my @files = readdir(DIR);
		closedir(DIR);

		foreach $file (@files) {
			next if ( $file eq "." );
			next if ( $file eq ".." );
			next if ( $file =~ /^old/ );
			%metadata = parsemetafile("$Conf::dbdir/installed/$file");

			foreach $line (@db) {
				next unless ($line =~ /.*;.*;.*;/ );
				@templine = split(/\;/,$line);
				if (("$metadata{'Name'}" eq "$templine[0]") && ("$metadata{'Release'}" < "$templine[2]")) {
					# Add all upgradable paks to list
					$paklist{"$metadata{'Name'}"} = {
						ProgVersion => $metadata{'ProgVersion'},
						Release => $metadata{'Release'},
						AvailableProgVersion => $templine[1],
						AvailableRelease => $templine[2],
						Installed => "yes"
					};
					last;
				} elsif (("$metadata{'Name'}" eq "$templine[0]") && ("$filter" ne "upgrade")) {
					# Add installed paks without an upgrade available to list
					$paklist{"$metadata{'Name'}"} = {
						ProgVersion => $metadata{'ProgVersion'},
						Release => $metadata{'Release'},
						Installed => "yes"
					};
					last;
				}
			}
		}
	}

	# Add all not installed paks to list
	if (("$filter" ne "upgrade") && ("$filter" ne "installed")) {
		foreach $line (@db) {
			next unless ($line =~ /.*;.*;.*;/ );
			@templine = split(/\;/,$line);
			next if ((defined $paklist{"$templine[0]"}) || (&isinstalled($templine[0]) == 0));

			$paklist{"$templine[0]"} = {
				ProgVersion => "$templine[1]",
				Release => "$templine[2]",
				Installed => "no"
			};
		}
	}

	return %paklist;
}

sub resolvedeps_one {
	my $pak = shift;
	
	message("PAKFIRE RESV: $pak: Resolving dependencies...");

	unless (getmetafile("$pak")) {
		message("PAKFIRE ERROR: Error retrieving dependency information on $pak. Unable to resolve dependencies.");
		exit 1;
	};
	
	my %metadata = parsemetafile("$Conf::dbdir/meta/meta-$pak");
	my @all;
	my @deps = split(/ /, $metadata{'Dependencies'});
	chomp (@deps);
	foreach (@deps) {
		if ($_) {
		  my $return = &isinstalled($_);
		  if ($return eq 0) {
		  	message("PAKFIRE RESV: $pak: Dependency is already installed: $_");
		  } else {
		  	message("PAKFIRE RESV: $pak: Need to install dependency: $_");
				push(@all,$_);
			}
		}
	}

	return @all;
}

sub resolvedeps {
	my $pak = shift;
	my @all;

	# Resolve all not yet installed dependencies of $pak
	my @deps = &resolvedeps_one($pak);
	push(@all, @deps);

	# For each dependency, we check if more dependencies exist
	while (@deps) {
		my $dep = pop(@deps);

		my @subdeps = &resolvedeps_one($dep);
		foreach my $subdep (@subdeps) {
			# Skip the package we are currently resolving for
			next if ($pak eq $subdep);

			# If the package is not already to be installed,
			# we add it to the list (@all) and check if it has
			# more dependencies on its own.
			unless (grep {$_ eq $subdep} @all) {
				push(@deps, $subdep);
				push(@all, $subdep);
			}
		}
	}

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
	
	# Try to download meta-file if we don't have one yet, or it is empty for some reason
	if ((! -e "$Conf::dbdir/meta/meta-$pak" ) || ( -z "$Conf::dbdir/meta/meta-$pak" )) {
		return 0 unless (fetchfile("meta/meta-$pak", ""));
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

	if (my %metadata = parsemetafile("$Conf::dbdir/meta/meta-$pak")) {
		return $metadata{'Size'};
	}
	return 0;
}

sub parsemetafile {
	### This subroutine returns a hash with the contents of a meta- file
	#   Pass path to metafile as argument: Pakfire::parsemetafile("$Conf::dbdir/meta/meta-$pak")
	#   Usage is always with an argument.
	my $metafile = shift;

	my %metadata = ();

	my @templine;
	my @file;

	if (! -e $metafile ) {
		return 0;
	}

	open(FILE, "<$metafile");
	@file = <FILE>;
	close(FILE);

	foreach (@file) {
		@templine = split(/\: /,$_);
		if ($templine[1]) {
			chomp($templine[1]);
			$metadata{"$templine[0]"} = $templine[1];
		}
	}

	return %metadata;
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

	unless (getmetafile("$pak")) {
		message("PAKFIRE ERROR: Unable to retrieve $pak metadata.");
		exit 1;
	}
	
	my %metadata = parsemetafile("$Conf::dbdir/meta/meta-$pak");
	my $file = $metadata{'File'};

	unless ($file) {
		message("No filename given in meta-file.");
		exit 1;
	}

	unless ( "$force" eq "force" ) {
		if ( -e "$Conf::cachedir/$file" ) {
			return $file;
		}
	}
	
	unless (fetchfile("paks/$file", "")) {
		message("PAKFIRE ERROR: Unable to download $pak.");
		exit 1;
	}
	return $file;
}

sub setuppak {
	my $pak = shift;

	message("PAKFIRE INST: $pak: Decrypting...");
	decryptpak("$pak");

	message("PAKFIRE INST: $pak: Copying files and running post-installation scripts...");
	my $return = system("cd $Conf::tmpdir && NAME=$pak ./install.sh >> $Conf::logdir/install-$pak.log 2>&1");
	$return %= 255;
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
	# Safety check for lazy testers:
	# Before we upgrade to the latest release, we re-install the previous release
	# to make sure that the tester has always been on the latest version.
	my $tree = &get_tree();
	$Conf::core_mine-- if ($tree eq "testing" || $tree eq "unstable");

	message("CORE UPGR: Upgrading from release $Conf::core_mine to $core_release");
	
	my @seq = ($Conf::core_mine .. $core_release);
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

sub updates_available {
	# Get packets with updates available
	my %upgradepaks = &Pakfire::dblist("upgrade");

	# Get the length of the returned hash
	my $updatecount = keys %upgradepaks;

	return "$updatecount";
}

sub reboot_required {
	if ( -e "/var/run/need_reboot" ) {
		return "yes";
	}
	else {
		return "no";
	}
}

sub status {
	### This subroutine returns pakfire status information in a hash.
	# Usage is without arguments

	# Add core version info
	my %status = &Pakfire::coredbinfo();

	# Add last update info
	$status{'LastUpdate'} = &General::age("/opt/pakfire/db/core/mine");
	$status{'LastCoreListUpdate'} = &General::age("/opt/pakfire/db/lists/core-list.db");
	$status{'LastServerListUpdate'} = &General::age("/opt/pakfire/db/lists/server-list.db");
	$status{'LastPakListUpdate'} = &General::age("/opt/pakfire/db/lists/packages_list.db");

	# Add number of available package updates
	$status{'CoreUpdateAvailable'} = (defined $status{'AvailableRelease'}) ? "yes" : "no";
	$status{'PakUpdatesAvailable'} = &Pakfire::updates_available();

	# Add if reboot is required
	$status{'RebootRequired'} = &Pakfire::reboot_required();

	return %status;
}

sub get_arch() {
	# Append architecture
	my ($sysname, $nodename, $release, $version, $machine) = POSIX::uname();

	# We only support armv6l for 32 bit arm
	if ($machine =~ m/armv[67]/) {
		return "armv6l";
	}

	return $machine;
}

sub get_tree() {
	# Return stable if nothing is set
	return "stable" unless (defined $pakfiresettings{'TREE'});

	return $pakfiresettings{'TREE'};
}

sub make_version() {
	my $version = "";

	# Open /etc/system-release
	open(RELEASE, "</etc/system-release");
	my $release = <RELEASE>;
	close(RELEASE);

	# Add the main relase
	if ($release =~ m/IPFire ([\d\.]+)/) {
		$version .= $1;
	}

	# Append suffix for tree
	my $tree = &get_tree();
	if ($tree eq "testing") {
		$version .= ".1";
	} elsif ($tree eq "unstable") {
		$version .= ".2";
	}

	# Append architecture
	$version .= "-" . &get_arch();

	return $version;
}

1;
