#!/usr/bin/perl -w

require "/opt/pakfire/etc/pakfire.conf";
require "/var/ipfire/general-functions.pl";

use File::Basename;
use File::Copy;
use LWP::UserAgent;
use HTTP::Response;
use Net::Ping;

package Pakfire;

my %pakfiresettings = ();
&General::readhash("${General::swroot}/pakfire/settings", \%pakfiresettings);

sub message {
	my $message = shift;
	print "$message\n";
	logger("$message");
}

sub logger {
	my $log = shift;
	system("logger -t pakfire \"$log\"");
}

sub usage {
  &Pakfire::message("Usage: pakfire <install|remove> <pak(s)>");
  &Pakfire::message("               <update> - Contacts the servers for new lists of paks.");
  &Pakfire::message("               <upgrade> - Installs the latest version of all paks.");
  &Pakfire::message("               <list> - Outputs a short list with all available paks.");
  &Pakfire::message("");
  exit 1;
}

sub pinghost {
	my $host = shift;
	
	$p = Net::Ping->new();
  if ($p->ping($host)) {
  	logger("$host is alive.");
  	return 1;
  } else {
		logger("$host is dead.");
		return 0;
	}
  $p->close();
}

sub fetchfile {
	my $getfile = shift;
	my $gethost = shift;
	my (@server, $host, $proto, $file, $allok, $i);
	
	use File::Basename;
	$bfile = basename("$getfile");

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
		
		logger("Trying to get $file from $host ($proto).");

		my $ua = LWP::UserAgent->new;
		$ua->agent("Pakfire/$Conf::version");
		$ua->timeout(5);
		
		my %proxysettings=();
		&General::readhash("${General::swroot}/proxy/advanced/settings", \%proxysettings);

		if ($proxysettings{'UPSTREAM_PROXY'}) {
			if ($proxysettings{'UPSTREAM_USER'}) {
				$ua->proxy("http","http://$proxysettings{'UPSTREAM_USER'}:$proxysettings{'UPSTREAM_PASSWORD'}@"."$proxysettings{'UPSTREAM_PROXY'}/");
			} else {
				$ua->proxy("http","http://$proxysettings{'UPSTREAM_PROXY'}/");
			}
		}
	 
		my $response = $ua->get("http://$host/$file");
		
		my $code = $response->code();
		my $log = $response->status_line;
		logger("HTTP-Status-Code: $code - $log");
		
		if ( $code eq "500" ) {
			message("Giving up: There was no chance to get teh file \"$getfile\" from any available server.\nThere was an error on the way. Please fix it.");
			return 1;
		}
		
		if ($response->is_success) {
			if (open(FILE, ">$Conf::cachedir/$bfile")) {
				print FILE $response->content;
				close(FILE);
				logger("Download successfully done from $host (file: $file).");
				$allok = 1;
				return 0;
			} else {
				logger("Could not open $Conf::cachedir/$bfile for writing.");
			}
		}	else {
			logger("Download $file failed from $host ($proto): $log");
		}
	}
	message("Giving up: There was no chance to get the file \"$getfile\" from any available server.\nMay be you should run \"pakfire update\" to get some new servers.");
	return 1;
}

sub getmirrors {
	use File::Copy;

	logger("Try to get a mirror list.");
	
	fetchfile("lists/$Conf::version-server-list", "$Conf::mainserver");
	move("$Conf::cachedir/$Conf::version-server-list", "$Conf::dbdir/lists/$Conf::version-server-list");
}

sub selectmirror {
	### Check if there is a current server list and read it.
	#   If there is no list try to get one.
	my $count = 0;
	while (!(open(FILE, "<$Conf::dbdir/lists/$Conf::version-server-list")) && ($count lt 5)) {
		$count++;
		getmirrors();
	}
	if ($count == 5) {
		message("Could not find or download a server list.");
		exit 1;
	}
	my @lines = <FILE>;
	close(FILE);

	### Count the number of the servers in the list
	my $scount = 0;
	foreach (@lines) {
		$scount++;
	}
	logger("$scount servers found in list.");
	
	### Choose a random server and test if it is online
	#   If the check fails try a new server.
	#   This will never give up.
	my $found = 0;
	my $servers = 0;
	while ($found == 0) {
		$server = int(rand($scount) + 1);
		$servers = 0;
		my ($line, $proto, $path, $host);
		my @templine;
		foreach $line (@lines) {
			$servers++;
			if ($servers eq $server) {
				@templine = split(/\;/, $line);
				$proto = $templine[0];
				$host = $templine[1];
				$path = $templine[2];
				if (pinghost("$host")) {
					$found = 1;
					return ($proto, $host, $path);
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
	} else {
		# Force an update.
		$age = "86401";
	}
	
	if (("$age" gt 86400) || ("$force" eq "force")) {
		#cleanup();
		fetchfile("lists/packages_list.db", "");
		move("$Conf::cachedir/packages_list.db", "$Conf::dbdir/lists/packages_list.db");
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
	dbgetlist("noforce");

	open(FILE, "<$Conf::dbdir/lists/packages_list.db");
	my @db = <FILE>;
	close(FILE);

	if ("$filter" eq "upgrade") {
		opendir(DIR,"$Conf::dbdir/meta");
		my @files = readdir(DIR);
		closedir(DIR);
		foreach $file (@files) {
			next if ( $file eq "." );
			next if ( $file eq ".." );
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
				if (("$name" eq "$templine[0]") && ("$release" < "$templine[2]" )) {
					push(@updatepaks,$name);
					if ("$forweb" eq "forweb") {
						print "<option value=\"$name\">Update: $name -- Version: $version -> $templine[1] -- Release: $release -> $templine[2]</option>\n";
					} else {
						print "Update: $name\nVersion: $version -> $templine[1]\nRelease: $release -> $templine[2]\n\n";
					}
				}
			}
		}
		return @updatepaks;
	} else {
		my $line;
		my @templine;
		foreach $line (sort @db) {
			@templine = split(/\;/,$line);
			if ("$filter" eq "notinstalled") {
				next if ( -e "$Conf::dbdir/installed/meta-$templine[0]" );
			} elsif ("$filter" eq "installed") {
				next unless ( -e "$Conf::dbdir/installed/meta-$templine[0]" );
			}
			if ("$forweb" eq "forweb") {
				print "<option value=\"$templine[0]\">$templine[0]-$templine[1]-$templine[2]</option>\n";
			} else {
				print "Name: $templine[0]\nProgVersion: $templine[1]\nRelease: $templine[2]\n\n";
			}
		}
	}
}

sub resolvedeps {
	my $pak = shift;
	
	getmetafile("$pak");
	
	message("\n## Resolving dependencies for $pak...");
	
	open(FILE, "<$Conf::dbdir/meta/meta-$pak");
	my @file = <FILE>;
	close(FILE);
	
	my $line;
	my (@templine, @deps, @tempdeps);
	foreach $line (@file) {
		@templine = split(/\: /,$line);
		if ("$templine[0]" eq "Dependencies") {
			@deps = split(/ /, $templine[1]);
		}
	}
	chomp (@deps);
	foreach (@deps) {
		if ($_) {
		  message("### Found dependency: $_");
		  push(@tempdeps,$_);
		}
	}
	
	#my @tempdeps = @deps;
	foreach (@tempdeps) {
		if ($_) {
			my @newdeps = resolvedeps("$_");
			foreach(@newdeps) {
				unless (($_ eq " ") || ($_ eq "")) {
				  message("### Found dependency: $_");
					push(@deps,$_);
				}
			}
		}
	}
	chomp (@deps);
	return @deps;
}

sub cleanup {
	my $dir = shift;
	my $path;
	
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
	
	logger("Going to download meta-$pak.");
	
	unless ( -e "$Conf::dbdir/meta/meta-$pak") {
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
	
	my $return = system("cd $Conf::tmpdir/ && gpg -d < $Conf::cachedir/$file | tar x >/dev/null 2>&1");
	$return %= 255;
	logger("Decryption process returned the following: $return");
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
		message("No filename given in meta-file. Please phone the developers.");
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
	
	message("We are going to install: $pak");
	
	decryptpak("$pak");
	
	my $return = system("cd $Conf::tmpdir && NAME=$pak ./install.sh >> $Conf::logdir/install-$pak.log 2>&1");
	$return %= 255;
	if ($return == 0) {
	  move("$Conf::tmpdir/ROOTFILES", "$Conf::dbdir/rootfiles/$pak");
	  cleanup("tmp");
	  copy("$Conf::dbdir/meta/meta-$pak","$Conf::dbdir/installed/");
		message("Setup completed. Congratulations!");
	} else {
		message("Setup returned: $return. Sorry. Please search our forum to find a solution for this problem.");
		exit $return;
	}
	return $return;
}

sub upgradepak {
	my $pak = shift;

	message("We are going to upgrade: $pak");

	decryptpak("$pak");

	my $return = system("cd $Conf::tmpdir && NAME=$pak ./update.sh >> $Conf::logdir/update-$pak.log 2>&1");
	$return %= 255;
	if ($return == 0) {
	  move("$Conf::tmpdir/ROOTFILES", "$Conf::dbdir/rootfiles/$pak");
	  cleanup("tmp");
		copy("$Conf::dbdir/meta/meta-$pak","$Conf::dbdir/installed/");
		message("Upgrade completed. Congratulations!");
	} else {
		message("Setup returned: $return. Sorry. Please search our forum to find a solution for this problem.");
		exit $return;
	}
	return $return;
}

sub removepak {
	my $pak = shift;

	message("We are going to uninstall: $pak");

	decryptpak("$pak");

	my $return = system("cd $Conf::tmpdir && NAME=$pak ./uninstall.sh >> $Conf::logdir/uninstall-$pak.log 2>&1");
	$return %= 255;
	if ($return == 0) {
	  open(FILE, "<$Conf::dbdir/rootfiles/$pak");
		my @file = <FILE>;
		close(FILE);
		foreach (@file) {
		  my $line = $_;
		  chomp($line);
			system("echo \"Removing: $line\" >> $Conf::logdir/uninstall-$pak.log 2>&1");
			system("cd / && rm -rf $line >> $Conf::logdir/uninstall-$pak.log 2>&1");
		}
	  unlink("$Conf::dbdir/rootfiles/$pak");
	  cleanup("tmp");
		message("Uninstall completed. Congratulations!");
	} else {
		message("Setup returned: $return. Sorry. Please search our forum to find a solution for this problem.");
		exit $return;
	}
	return $return;
}

sub beautifysize {
	my $size = shift;
	$size = $size / 1024;
	my $unit;
	
	if ($size > 1023) {
	  $size = ($size / 1024);
	  $unit = "MB";
	} else {
	  $unit = "KB";
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
		fetchfile("cgi-bin/counter?ver=$Conf::version&uuid=$Conf::uuid", "$Conf::mainserver");
		system("rm -f $Conf::cachedir/counter* 2>/dev/null");
	}
}

sub lock {
	my $status = shift;
	if ("$status" eq "on") {
		system("touch /opt/pakfire/pakfire.lock");
		system("chmod 777 /opt/pakfire/pakfire.lock");
		logger("Created lock");
	} else {
		if (system("rm -f /opt/pakfire/pakfire.lock >/dev/null 2>&1")) {
			logger("Successfully removed lock.");
		} else {
			logger("Couldn't remove lock.");
		}
	}
	return 0;
}

sub checkcryptodb {
	my $myid = "64D96617"; # Our own gpg-key
	my $trustid = "65D0FD58"; # Id of CaCert
	my $ret = system("gpg --list-keys | grep -q $myid");
	unless ( "$ret" eq "0" ) {
		message("The GnuPG isn't configured corectly. Trying now to fix this.");
		system("gpg --keyserver wwwkeys.de.pgp.net --always-trust --recv-key $myid");
		system("gpg --keyserver wwwkeys.de.pgp.net --always-trust --recv-key $trustid");
	}
}

1;
