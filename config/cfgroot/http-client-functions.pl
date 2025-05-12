#!/usr/bin/perl -w
############################################################################
#                                                                          #
# This file is part of the IPFire Firewall.                                #
#                                                                          #
# IPFire is free software; you can redistribute it and/or modify           #
# it under the terms of the GNU General Public License as published by     #
# the Free Software Foundation; either version 2 of the License, or        #
# (at your option) any later version.                                      #
#                                                                          #
# IPFire is distributed in the hope that it will be useful,                #
# but WITHOUT ANY WARRANTY; without even the implied warranty of           #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
# GNU General Public License for more details.                             #
#                                                                          #
# You should have received a copy of the GNU General Public License        #
# along with IPFire; if not, write to the Free Software                    #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA #
#                                                                          #
# Copyright (C) 2025 IPFire Team <info@ipfire.org>                         #
#                                                                          #
############################################################################

package HTTPClient;

require '/var/ipfire/general-functions.pl';

use strict;

# Load module to move files.
use File::Copy;

# Load module to get file stats.
use File::stat;

# Load module to deal with temporary files.
use File::Temp;

# Load module to deal with the date formats used by the HTTP protocol.
use HTTP::Date;

# Load the libwwwperl User Agent module.
use LWP::UserAgent;

# Function to grab a given URL content or to download and store it on disk.
#
# The function requires a configuration hash to be passed.
#
# The following options (hash keys) are supported:
#
# URL -> The URL to the content or file. REQUIRED!
# FILE -> The filename as fullpath where the content/file should be stored on disk.
# ETAGSFILE -> A filename again as fullpath where Etags should be stored and read.
# ETAGPREFIX -> In case a custom etag name should be used, otherwise it defaults to the given URL.
# MAXSIZE -> In bytes until the downloader will abort downloading. (example: 10_485_760 for 10MB)
#
# If a file is given an If-Modified-Since header will be generated from the last modified timestamp
# of an already stored file. In case an Etag file is specified an If-None-Match header will be added to
# the request - Both can be used at the same time.
#
# In case no FILE option has been passed to the function, the content of the requested URL will be returned.
#
# Return codes (if FILE is used):
#
# nothing - On success
# no url - If no URL has been specified.
# not_modified - In case the servers responds with "Not modified" (304)
# dl_error - If the requested URL cannot be accessed.
# incomplete download - In case the size of the local file does not match the remote content_lenght.
#
sub downloader (%) {
	my (%args) = @_;

	# Remap args hash and convert all keys into upper case format.
	%args = map { uc $_ => $args{$_} } keys %args;

	# The amount of download attempts before giving up and
	# logging an error.
	my $max_dl_attempts = 3;

	# Temporary directory to download the files.
	my $tmp_dl_directory = "/var/tmp";

	# Assign hash values.
	my $url = $args{"URL"} if (exists($args{"URL"}));
	my $file = $args{"FILE"} if (exists($args{"FILE"}));
	my $etags_file = $args{"ETAGSFILE"} if (exists($args{"ETAGSFILE"}));
	my $etagprefix = $url;
	$etagprefix = $args{"ETAGPREFIX"} if (exists($args{"ETAGPREFIX"}));
	my $max_size = $args{"MAXSIZE"} if (exists($args{"MAXSIZE"}));

	# Timeout defaults to 60 Seconds if not set.
	my $timeout = 60;
	$timeout = $args{"TIMEOUT"} if (exists($args{"TIMEOUT"}));

	# Abort with error "no url", if no URL has been given.
	die "downloader: No URL has been given." unless ($url);

	my %etags = ();
	my $tmpfile;

	# Read-in proxysettings.
	my %proxysettings=();
	&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);

	# Create a user agent instance.
	#
	# Request SSL hostname verification and specify path
	# to the CA file.
	my $ua = LWP::UserAgent->new(
		ssl_opts => {
			SSL_ca_file     => '/etc/ssl/cert.pem',
			verify_hostname => 1,
		},
	);

	# Set the timeout to the configured value.
	# Defaults to 60 seconds if not set.
	$ua->timeout($timeout);

	# Assign maximum download size if set.
	$ua->max_size($max_size) if ($max_size);

	# Generate UserAgent.
	my $agent = &General::MakeUserAgent();

	# Set the generated UserAgent.
	$ua->agent($agent);

	# Check if an upstream proxy is configured.
	if ($proxysettings{'UPSTREAM_PROXY'}) {
		# Start generating proxy url.
		my $proxy_url = "http://";

		# Check if the proxy requires authentication.
		if (($proxysettings{'UPSTREAM_USER'}) && ($proxysettings{'UPSTREAM_PASSWORD'})) {
			# Add proxy auth details.
			$proxy_url .= "$proxysettings{'UPSTREAM_USER'}\:$proxysettings{'UPSTREAM_PASSWORD'}\@";
		}

		# Add proxy server address and port.
		$proxy_url .= $proxysettings{'UPSTREAM_PROXY'};

		# Append proxy settings.
		$ua->proxy(['http', 'https'], $proxy_url);
	}

	# Create a HTTP request element and pass the given URL to it.
	my $request = HTTP::Request->new(GET => $url);

	# Check if a file to store the output has been provided.
	if ($file) {
		# Check if the given file already exits, because it has been downloaded in the past.
		#
		# In this case we are requesting the server if the remote file has been changed or not.
		# This will be done by sending the modification time in a special HTTP header.
		if (-f $file) {
			# Call stat on the file.
			my $stat = stat($file);

			# Omit the mtime of the existing file.
			my $mtime = $stat->mtime;

			# Convert the timestamp into right format.
			my $http_date = time2str($mtime);

			# Add the If-Modified-Since header to the request to ask the server if the
			# file has been modified.
			$request->header( 'If-Modified-Since' => "$http_date" );
		}

		# Generate a temporary file name, located in the tempoary download directory and with a suffix of ".tmp".
		# The downloaded file will be stored there until some sanity checks are performed.
		my $tmp = File::Temp->new( SUFFIX => ".tmp", DIR => "$tmp_dl_directory/", UNLINK => 0 );
		$tmpfile = $tmp->filename();
	}

	# Check if an file for etags has been given.
	if ($etags_file) {
		# Read-in Etags file for known Etags if the file is present.
		&readhash("$etags_file", \%etags) if (-f $etags_file);

		# Check if an Etag for the requested file is stored.
		if ($etags{$etagprefix}) {
			# Grab the stored tag.
			my $etag = $etags{$etagprefix};

			# Add an "If-None-Match header to the request to ask the server if the
			# file has been modified.
			$request->header( 'If-None-Match' => $etag );
		}
	}

	my $dl_attempt = 1;
	my $response;

	# Download and retry on failure.
	while ($dl_attempt <= $max_dl_attempts) {
		# Perform the request and save the output into the tmpfile if requested.
		$response = $ua->request($request, $tmpfile);

		# Check if the download was successfull.
		if($response->is_success) {
			# Break loop.
			last;

		# Check if the server responds with 304 (Not Modified).
		} elsif ($response->code == 304) {
			# Remove temporary file, if one exists.
			unlink("$tmpfile") if (-e "$tmpfile");

			# Return "not modified".
			return "not modified";

		# Check if we ran out of download re-tries.
		} elsif ($dl_attempt eq $max_dl_attempts) {
			# Obtain error.
			my $error = $response->content;

			# Remove temporary file, if one exists.
			unlink("$tmpfile") if (-e "$tmpfile");

			# Return the error message from response..
			return "$error";
		}

		# Remove temporary file, if one exists.
		unlink("$tmpfile") if (-e "$tmpfile");

		# Increase download attempt counter.
		$dl_attempt++;
	}

	# Obtain the connection headers.
	my $headers = $response->headers;

	# Check if an Etag file has been provided.
	if ($etags_file) {
		# Grab the Etag from the response if the server provides one.
		if ($response->header('Etag')) {
			# Add the provided Etag to the hash of tags.
			$etags{$etagprefix} = $response->header('Etag');

			# Write the etags file.
			&General::writehash($etags_file, \%etags);
		}
	}

	# Check if the response should be stored on disk.
	if ($file) {
		# Get the remote size of the content.
		my $remote_size = $response->header('Content-Length');

		# Perform a stat on the temporary file.
		my $stat = stat($tmpfile);

		# Grab the size of the stored temporary file.
		my $local_size = $stat->size;

		# Check if both sizes are equal.
		if(($remote_size) && ($remote_size ne $local_size)) {
			# Delete the temporary file.
			unlink("$tmpfile");

			# Abort and return "incomplete download" as error.
			return "incomplete download";
		}

		# Move the temporaray file to the desired file by overwriting a may
		# existing one.
		move("$tmpfile", "$file");

		# Omit the timestamp from response header, when the file has been modified the
		# last time.
		my $last_modified = $headers->last_modified;

		# Check if we got a last-modified value from the server.
		if ($last_modified) {
			# Assign the last-modified timestamp as mtime to the
			# stored file.
			utime(time(), "$last_modified", "$file");
		}

		# Delete temporary file.
		unlink("$tmpfile");

		# If we got here, everything worked fine. Return nothing.
		return;
	} else {
		# Decode the response content and return it.
		return $response->decoded_content;
	}
}

#
# Tiny function to grab the public red IPv4 address using an online service.
#
sub FetchPublicIp {
	# URL to grab the public IP.
	my $url = "https://checkip4.ipfire.org";

	# Call downloader to fetch the public IP.
	my $response = &downloader("URL" => $url);

	# Omit the address from the resonse message.
	if ($response =~ /Your IP address is: (\d+.\d+.\d+.\d+)/) {
		# Return the address.
		return $1;
	}

	# Unable to grab the address - Return nothing.
	return;
}

#
# This sub returns the red IP used to compare in DyndnsServiceSync
#
sub GetDyndnsRedIP {
	my %settings;

	# Read-in ddns settings.
	&General::readhash("${General::swroot}/ddns/settings", \%settings);

	# Try to grab the address from the local-ipaddress file.
	my $ip = &General::grab_address_from_file("${General::swroot}/red/local-ipaddress") or return 'unavailable';

	# 100.64.0.0/10 is reserved for dual-stack lite (http://tools.ietf.org/html/rfc6598).
	if (&General::IpInSubnet ($ip,'10.0.0.0','255.0.0.0') ||
		&General::IpInSubnet ($ip,'172.16.0.0.','255.240.0.0') ||
		&General::IpInSubnet ($ip,'192.168.0.0','255.255.0.0') ||
		&General::IpInSubnet ($ip,'100.64.0.0', '255.192.0.0'))
	{
		if ($settings{'BEHINDROUTER'} eq 'FETCH_IP') {
			# Call function to omit the real address.
			my $RealIP = &FetchPublicIp;

			# Check if the grabbed address is valid.
			$ip = (&General::validip ($RealIP) ?  $RealIP : 'unavailable');
		}
	}

	return $ip;
}

1;
