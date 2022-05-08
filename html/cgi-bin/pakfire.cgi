#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2022  IPFire Team  <info@ipfire.org>                     #
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
use List::Util qw(any);

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "/opt/pakfire/lib/functions.pl";

my %cgiparams=();
my $errormessage = '';
my %color = ();
my %pakfiresettings = ();
my %mainsettings = ();

# Load general settings
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("${General::swroot}/pakfire/settings", \%pakfiresettings);
&General::readhash("/srv/web/ipfire/html/themes/ipfire/include/colors.txt", \%color);

# Get CGI request data
$cgiparams{'ACTION'} = '';
$cgiparams{'FORCE'} = '';

$cgiparams{'INSPAKS'} = '';
$cgiparams{'DELPAKS'} = '';

&Header::getcgihash(\%cgiparams);

### Process AJAX/JSON request ###
if($cgiparams{'ACTION'} eq 'json-getstatus') {
	# Send HTTP headers
	_start_json_output();

	# Read /var/log/messages backwards until a "Pakfire started" header is found,
	# to capture all messages of the last (i.e. current) Pakfire run
	my @messages = `tac /var/log/messages | sed -n '/pakfire:/{p;/Pakfire.*started/q}'`;

	# Test if the log contains an error message (fastest implementation, stops at first match)
	my $failure = any{ index($_, 'ERROR') != -1 } @messages;

	# Collect Pakfire status
	my %status = (
		'running' => &_is_pakfire_busy() || "0",
		'running_since' => &General::age("$Pakfire::lockfile") || "0s",
		'reboot' => (-e "/var/run/need_reboot") || "0",
		'failure' => $failure || "0"
	);

	# Start JSON file
	print "{\n";

	foreach my $key (keys %status) {
		my $value = $status{$key};
		print qq{\t"$key": "$value",\n};
	}

	# Print sanitized messages in reverse order to undo previous "tac"
	print qq{\t"messages": [\n};
	for my $index (reverse (0 .. $#messages)) {
		my $line = $messages[$index];
		$line =~ s/[[:cntrl:]<>&\\]+//g;

		print qq{\t\t"$line"};
		print ",\n" unless $index < 1;
	}
	print "\n\t]\n";

	# Finalize JSON file & stop
	print "}";
	exit;
}

### Process Pakfire install/update commands ###
if(($cgiparams{'ACTION'} ne '') && (! &_is_pakfire_busy())) {
	if(($cgiparams{'ACTION'} eq 'install') && ($cgiparams{'FORCE'} eq 'on')) {
		my @pkgs = split(/\|/, $cgiparams{'INSPAKS'});
		&General::system_background("/usr/local/bin/pakfire", "install", "--non-interactive", "--no-colors", @pkgs);
	} elsif(($cgiparams{'ACTION'} eq 'remove') && ($cgiparams{'FORCE'} eq 'on')) {
		my @pkgs = split(/\|/, $cgiparams{'DELPAKS'});
		&General::system_background("/usr/local/bin/pakfire", "remove", "--non-interactive", "--no-colors", @pkgs);
	} elsif($cgiparams{'ACTION'} eq 'update') {
		&General::system_background("/usr/local/bin/pakfire", "update", "--force", "--no-colors");
	} elsif($cgiparams{'ACTION'} eq 'upgrade') {
		&General::system_background("/usr/local/bin/pakfire", "upgrade", "-y", "--no-colors");
	} elsif($cgiparams{'ACTION'} eq $Lang::tr{'save'}) {
		$pakfiresettings{"TREE"} = $cgiparams{"TREE"};

		# Check for valid input
		if ($pakfiresettings{"TREE"} !~ m/^(stable|testing|unstable)$/) {
			$errormessage .= $Lang::tr{'pakfire invalid tree'};
		}

		unless ($errormessage) {
			&General::writehash("${General::swroot}/pakfire/settings", \%pakfiresettings);

			# Update lists
			&General::system_background("/usr/local/bin/pakfire", "update", "--force", "--no-colors");
		}
	}
}

### Start pakfire page ###
&Header::showhttpheaders();

###--- HTML HEAD ---###
my $extraHead = <<END
<style>
	/* Main screen */
	table#pfmain {
		width: 100%;
		border-style: hidden;
		table-layout: fixed;
	}

	#pfmain td {
		padding: 5px 20px 0;
		text-align: center;
	}
	#pfmain tr:not(:last-child) > td {
		padding-bottom: 1.5em;
	}
	#pfmain tr > td.heading {
		padding: 0;
		font-weight: bold;
		background-color: $color{'color20'};
	}

	.pflist {
		width: 100%;
		text-align: left;
		margin-bottom: 0.8em;
	}

	/* Pakfire log viewer */
	section#pflog-header {
		width: 100%;
		display: flex;
		text-align: left;
		align-items: center;
		column-gap: 20px;
	}
	#pflog-header > div:last-child {
		margin-left: auto;
		margin-right: 20px;
	}
	#pflog-header span {
		line-height: 1.3em;
	}
	#pflog-header span:empty::before {
		content: "\\200b"; /* zero width space */
	}

	pre#pflog-messages {
		margin-top: 0.7em;
		padding-top: 0.7em;
		border-top: 0.5px solid $Header::bordercolour;

		text-align: left;
		min-height: 15em;
		overflow-x: auto;
	}
</style>

<script src="/include/pakfire.js"></script>
<script>
	// Translations
	pakfire.i18n.load({
		'working': '$Lang::tr{'pakfire working'}',
		'finished': '$Lang::tr{'pakfire finished'}',
		'finished error': '$Lang::tr{'pakfire finished error'}',
		'since': '$Lang::tr{'since'}',

		'link_return': '<a href="$ENV{'SCRIPT_NAME'}">$Lang::tr{'pakfire return'}</a>',
		'link_reboot': '<a href="/cgi-bin/shutdown.cgi">$Lang::tr{'needreboot'}</a>'
	});

	// AJAX auto refresh interval (in ms, default: 1000)
	//pakfire.refreshInterval = 1000;

	// Enable returning to main screen (delay in ms)
	pakfire.setupPageReload(true, 3000);
</script>
END
;
###--- END HTML HEAD ---###

&Header::openpage($Lang::tr{'pakfire configuration'}, 1, $extraHead);
&Header::openbigbox('100%', 'left', '', $errormessage);

# Show error message
if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<font class='base'>$errormessage&nbsp;</font>\n";
	&Header::closebox();
}

# Show log output while Pakfire is running
if(&_is_pakfire_busy()) {
	&Header::openbox("100%", "center", "Pakfire");

	print <<END
<section id="pflog-header">
	<div><img src="/images/indicator.gif" alt="$Lang::tr{'active'}" title="$Lang::tr{'pagerefresh'}"></div>
	<div>
		<span id="pflog-status">$Lang::tr{'pakfire working'}</span><br>
		<span id="pflog-time"></span><br>
		<span id="pflog-action"></span>
	</div>
	<div><a href="$ENV{'SCRIPT_NAME'}"><img src="/images/view-refresh.png" alt="$Lang::tr{'refresh'}" title="$Lang::tr{'refresh'}"></a></div>
</section>

<!-- Pakfire log messages -->
<pre id="pflog-messages"></pre>
<script>
	// Start automatic log refresh
	pakfire.running = true;
</script>

END
;

	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit;
}

# Show Pakfire install/remove dependencies and confirm form
if (($cgiparams{'ACTION'} eq 'install') && (! &_is_pakfire_busy())) {
	&Header::openbox("100%", "center", $Lang::tr{'request'});

	my @pkgs = split(/\|/, $cgiparams{'INSPAKS'});
	my @output = &General::system_output("/usr/local/bin/pakfire", "resolvedeps", "--no-colors", @pkgs);
	print <<END;
	<table><tr><td colspan='2'>$Lang::tr{'pakfire install package'} @pkgs $Lang::tr{'pakfire possible dependency'}
		<pre>
END
	foreach (@output) {
		$_ =~ s/\\[[0-1]\;[0-9]+m//g;
		print "$_\n";
	}
	print <<END;
		</pre></td></tr>
		<tr><td colspan='2'>$Lang::tr{'pakfire accept all'}</td></tr>
		<tr><td colspan='2'>&nbsp;</td></tr>
		<tr><td align='right'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='hidden' name='INSPAKS' value='$cgiparams{'INSPAKS'}' />
					<input type='hidden' name='FORCE' value='on' />
					<input type='hidden' name='ACTION' value='install' />
					<input type='image' alt='$Lang::tr{'install'}' title='$Lang::tr{'install'}' src='/images/go-next.png' />
				</form>
			</td>
			<td align='left'>
				<form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='hidden' name='ACTION' value='' />
					<input type='image' alt='$Lang::tr{'abort'}' title='$Lang::tr{'abort'}' src='/images/dialog-error.png' />
				</form>
			</td>
		</tr>
	</table>
END
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit;

} elsif (($cgiparams{'ACTION'} eq 'remove') && (! &_is_pakfire_busy())) {
	&Header::openbox("100%", "center", $Lang::tr{'request'});

	my @pkgs = split(/\|/, $cgiparams{'DELPAKS'});
	my @output = &General::system_output("/usr/local/bin/pakfire", "resolvedeps", "--no-colors", @pkgs);
	print <<END;
	<table><tr><td colspan='2'>$Lang::tr{'pakfire uninstall package'} @pkgs $Lang::tr{'pakfire possible dependency'}
		<pre>
END
	foreach (@output) {
		$_ =~ s/\\[[0-1]\;[0-9]+m//g;
		print "$_\n";
	}
	print <<END;
		</pre></td></tr>
		<tr><td colspan='2'>$Lang::tr{'pakfire uninstall all'}</td></tr>
		<tr><td colspan='2'>&nbsp;</td></tr>
		<tr><td align='right'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='hidden' name='DELPAKS' value='$cgiparams{'DELPAKS'}' />
					<input type='hidden' name='FORCE' value='on' />
					<input type='hidden' name='ACTION' value='remove' />
					<input type='image' alt='$Lang::tr{'uninstall'}' title='$Lang::tr{'uninstall'}' src='/images/go-next.png' />
				</form>
			</td>
			<td align='left'>
				<form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='hidden' name='ACTION' value='' />
					<input type='image' alt='$Lang::tr{'abort'}' title='$Lang::tr{'abort'}' src='/images/dialog-error.png' />
				</form>
			</td>
		</tr>
	</table>
END
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit;
}

# Show Pakfire main page
my %selected=();
my %checked=();

$selected{"TREE"} = ();
$selected{"TREE"}{"stable"} = "";
$selected{"TREE"}{"testing"} = "";
$selected{"TREE"}{"unstable"} = "";
$selected{"TREE"}{$pakfiresettings{"TREE"}} = "selected";

my $core_release = `cat /opt/pakfire/db/core/mine 2>/dev/null`;
chomp($core_release);
my $core_update_age = &General::age("/opt/pakfire/db/core/mine");
my $corelist_update_age = &General::age("/opt/pakfire/db/lists/core-list.db");
my $server_update_age = &General::age("/opt/pakfire/db/lists/server-list.db");
my $packages_update_age = &General::age("/opt/pakfire/db/lists/packages_list.db");

&Header::openbox("100%", "center", "Pakfire");

print <<END;
	<table id="pfmain">
END
if ( -e "/var/run/need_reboot") {
	print "\t\t<tr><td colspan='2'><a href='/cgi-bin/shutdown.cgi'>$Lang::tr{'needreboot'}!</a></td></tr>\n";
}
print <<END;
		<tr><td class="heading">$Lang::tr{'pakfire system state'}:</td>
			<td class="heading">$Lang::tr{'available updates'}:</td></tr>

		<tr><td><strong>$Lang::tr{'pakfire core update level'}: $core_release</strong>
				<hr>
				<div class="pflist">
					$Lang::tr{'pakfire last update'} $core_update_age $Lang::tr{'pakfire ago'}<br>
					$Lang::tr{'pakfire last serverlist update'} $server_update_age $Lang::tr{'pakfire ago'}<br>
					$Lang::tr{'pakfire last core list update'} $corelist_update_age $Lang::tr{'pakfire ago'}<br>
					$Lang::tr{'pakfire last package update'} $packages_update_age $Lang::tr{'pakfire ago'}
				</div>
				<form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='hidden' name='ACTION' value='update' />
					<input type='submit' value='$Lang::tr{'calamaris refresh list'}' />
				</form>
			</td>
			<td>
				<form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<select name="UPDPAKS" class="pflist" size="5" disabled>
END

	&Pakfire::dblist("upgrade", "forweb");
	print <<END;
					</select>
					<input type='hidden' name='ACTION' value='upgrade' />
					<input type='image' alt='$Lang::tr{'upgrade'}' title='$Lang::tr{'upgrade'}' src='/images/document-save.png' />
				 </form>
			</td>
		</tr>
		<tr><td class="heading">$Lang::tr{'pakfire available addons'}</td>
			<td class="heading">$Lang::tr{'pakfire installed addons'}</td></tr>

		<tr><td style="padding:5px 10px 20px 20px" align="center"><p>$Lang::tr{'pakfire install description'}</p>
				<form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<select name="INSPAKS" class="pflist" size="10" multiple>
END

	&Pakfire::dblist("notinstalled", "forweb");
	print <<END;
					</select>
					<input type='hidden' name='ACTION' value='install' />
					<input type='image' alt='$Lang::tr{'install'}' title='$Lang::tr{'install'}' src='/images/list-add.png' />
				</form>
			</td>
			<td style="padding:5px 10px 20px 20px" align="center"><p>$Lang::tr{'pakfire uninstall description'}</p>
				<form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<select name="DELPAKS" class="pflist" size="10" multiple>
END

	&Pakfire::dblist("installed", "forweb");
	print <<END;
					</select>
					<input type='hidden' name='ACTION' value='remove' />
					<input type='image' alt='$Lang::tr{'remove'}' title='$Lang::tr{'remove'}' src='/images/list-remove.png' />
				</form>
			</td>
		</tr>
	</table>
END

&Header::closebox();
&Header::openbox("100%", "center", "$Lang::tr{'settings'}");

print <<END;
	<form method='POST' action='$ENV{'SCRIPT_NAME'}'>
		<table width='95%'>
			<tr>
				<td align='left' width='45%'>$Lang::tr{'pakfire tree'}</td>
				<td width="55%" align="left">
					<select name="TREE">
						<option value="stable" $selected{"TREE"}{"stable"}>$Lang::tr{'pakfire tree stable'}</option>
						<option value="testing" $selected{"TREE"}{"testing"}>$Lang::tr{'pakfire tree testing'}</option>
						<option value="unstable" $selected{"TREE"}{"unstable"}>$Lang::tr{'pakfire tree unstable'}</option>
					</select>
				</td>
			</tr>
			<tr>
				<td colspan="2">&nbsp;</td>
			</tr>
			<tr>
				<td colspan="2" align="center">
					<input type="submit" name="ACTION" value="$Lang::tr{'save'}" />
				</td>
			</tr>
		</table>
	</form>
END

&Header::closebox();
&Header::closebigbox();
&Header::closepage();

###--- Internal functions ---###

# Check if pakfire is already running (extend test here if necessary)
sub _is_pakfire_busy {
	# Return immediately if lockfile is present
	if(-e "$Pakfire::lockfile") {
		return 1;
	}

	# Check if a PID of a running pakfire instance is found
	# (The system backpipe command is safe, because no user input is computed.)
	my $pakfire_pid = `pidof -s /usr/local/bin/pakfire`;
	chomp($pakfire_pid);

	if($pakfire_pid) {
		return 1;
	}

	# Pakfire isn't running
	return 0;
}

# Send HTTP headers
sub _start_json_output {
	print "Cache-Control: no-cache, no-store\n";
	print "Content-Type: application/json\n";
	print "\n"; # End of HTTP headers
}
