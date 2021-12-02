#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2011  Michael Tremer & Christian Schmidt                 #
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
&General::readhash("/srv/web/ipfire/html/themes/ipfire/include/colors.txt", \%color);

# Get CGI request data
$cgiparams{'ACTION'} = '';
$cgiparams{'VALID'} = '';

$cgiparams{'INSPAKS'} = '';
$cgiparams{'DELPAKS'} = '';

&Header::getcgihash(\%cgiparams);

### Process AJAX/JSON request ###
if($cgiparams{'ACTION'} eq 'json-getstatus') {
	# Send HTTP headers
	_start_json_output();

	# Collect Pakfire status and log messages
	my %status = (
		'running' => &_is_pakfire_busy() || "0",
		'running_since' => &General::age("$Pakfire::lockfile") || "0s",
		'reboot' => (-e "/var/run/need_reboot") || "0"
	);
	my @messages = `tac /var/log/messages | sed -n '/pakfire:/{p;/Pakfire.*started/q}'`;

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

### Start pakfire page ###
&Header::showhttpheaders();

###--- HTML HEAD ---###
my $extraHead = <<END
<style>
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
		'finished': 'Pakfire is finished! Please check the log output.',
		'since': '$Lang::tr{'since'} ', //(space is intentional)

		'link_return': '<a href="$ENV{'SCRIPT_NAME'}">Return to Pakfire</a>',
		'link_reboot': '<a href="/cgi-bin/shutdown.cgi">$Lang::tr{'needreboot'}</a>'
	});
	
	// AJAX auto refresh interval
	pakfire.refreshInterval = 1000;
</script>
END
;
###--- END HTML HEAD ---###

&Header::openpage($Lang::tr{'pakfire configuration'}, 1, $extraHead);
&Header::openbigbox('100%', 'left', '', $errormessage);

# Process Pakfire commands
if (($cgiparams{'ACTION'} eq 'install') && (! &_is_pakfire_busy())) {
	my @pkgs = split(/\|/, $cgiparams{'INSPAKS'});
	if ("$cgiparams{'FORCE'}" eq "on") {
		&General::system_background("/usr/local/bin/pakfire", "install", "--non-interactive", "--no-colors", @pkgs);
		sleep(1);
	} else {
		&Header::openbox("100%", "center", $Lang::tr{'request'});
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
		</pre>
		<tr><td colspan='2'>$Lang::tr{'pakfire accept all'}
		<tr><td colspan='2'>&nbsp;
		<tr><td align='right'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='INSPAKS' value='$cgiparams{'INSPAKS'}' />
							<input type='hidden' name='FORCE' value='on' />
							<input type='hidden' name='ACTION' value='install' />
							<input type='image' alt='$Lang::tr{'install'}' title='$Lang::tr{'install'}' src='/images/go-next.png' />
						</form>
				<td align='left'>
						<form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='ACTION' value='' />
							<input type='image' alt='$Lang::tr{'abort'}' title='$Lang::tr{'abort'}' src='/images/dialog-error.png' />
						</form>
		</table>
END
		&Header::closebox();
		&Header::closebigbox();
		&Header::closepage();
		exit;
	}
} elsif (($cgiparams{'ACTION'} eq 'remove') && (! &_is_pakfire_busy())) {
	my @pkgs = split(/\|/, $cgiparams{'DELPAKS'});
	if ("$cgiparams{'FORCE'}" eq "on") {
		&General::system_background("/usr/local/bin/pakfire", "remove", "--non-interactive", "--no-colors", @pkgs);
		sleep(1);
	} else {
		&Header::openbox("100%", "center", $Lang::tr{'request'});
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
		</pre>
		<tr><td colspan='2'>$Lang::tr{'pakfire uninstall all'}
		<tr><td colspan='2'>&nbsp;
		<tr><td align='right'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='DELPAKS' value='$cgiparams{'DELPAKS'}' />
							<input type='hidden' name='FORCE' value='on' />
							<input type='hidden' name='ACTION' value='remove' />
							<input type='image' alt='$Lang::tr{'uninstall'}' title='$Lang::tr{'uninstall'}' src='/images/go-next.png' />
						</form>
				<td align='left'>
						<form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='ACTION' value='' />
							<input type='image' alt='$Lang::tr{'abort'}' title='$Lang::tr{'abort'}' src='/images/dialog-error.png' />
						</form>
		</table>
END
		&Header::closebox();
		&Header::closebigbox();
		&Header::closepage();
		exit;
	}

} elsif (($cgiparams{'ACTION'} eq 'update') && (! &_is_pakfire_busy())) {
	&General::system_background("/usr/local/bin/pakfire", "update", "--force", "--no-colors");
	sleep(1);
} elsif (($cgiparams{'ACTION'} eq 'upgrade') && (! &_is_pakfire_busy())) {
	&General::system_background("/usr/local/bin/pakfire", "upgrade", "-y", "--no-colors");
	sleep(1);
} elsif ($cgiparams{'ACTION'} eq "$Lang::tr{'save'}") {
	$pakfiresettings{"TREE"} = $cgiparams{"TREE"};

	# Check for valid input
	if ($pakfiresettings{"TREE"} !~ m/^(stable|testing|unstable)$/) {
		$errormessage .= $Lang::tr{'pakfire invalid tree'};
	}

	unless ($errormessage) {
		&General::writehash("${General::swroot}/pakfire/settings", \%pakfiresettings);

		# Update lists
		&General::system_background("/usr/local/bin/pakfire", "update", "--force", "--no-colors");
		sleep(1);
	}
}

&General::readhash("${General::swroot}/pakfire/settings", \%pakfiresettings);

my %selected=();
my %checked=();

$selected{"TREE"} = ();
$selected{"TREE"}{"stable"} = "";
$selected{"TREE"}{"testing"} = "";
$selected{"TREE"}{"unstable"} = "";
$selected{"TREE"}{$pakfiresettings{"TREE"}} = "selected";

# DPC move error message to top so it is seen!
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
	pakfire.running = true;
</script>

END
;

	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit;
}

my $core_release = `cat /opt/pakfire/db/core/mine 2>/dev/null`;
chomp($core_release);
my $core_update_age = &General::age("/opt/pakfire/db/core/mine");
my $corelist_update_age = &General::age("/opt/pakfire/db/lists/core-list.db");
my $server_update_age = &General::age("/opt/pakfire/db/lists/server-list.db");
my $packages_update_age = &General::age("/opt/pakfire/db/lists/packages_list.db");

&Header::openbox("100%", "center", "Pakfire");

print <<END;
	<table width='95%' cellpadding='5'>
END
if ( -e "/var/run/need_reboot") {
	print "<tr><td align='center' colspan='2'><font color='red'>$Lang::tr{'needreboot'}!</font></td></tr>";
	print "<tr><td colspan='2'>&nbsp;</font></td></tr>"
}
print <<END;
		<tr><td width="50%" bgcolor='$color{'color20'}' align="center"><b>$Lang::tr{'pakfire system state'}:</b>

			<td width="50%" bgcolor='$color{'color20'}' align="center"><b>$Lang::tr{'available updates'}:</b></tr>

		<tr><td align="center">$Lang::tr{'pakfire core update level'}: $core_release<hr />
					$Lang::tr{'pakfire last update'} $core_update_age $Lang::tr{'pakfire ago'}<br />
					$Lang::tr{'pakfire last serverlist update'} $server_update_age $Lang::tr{'pakfire ago'}<br />
					$Lang::tr{'pakfire last core list update'} $corelist_update_age $Lang::tr{'pakfire ago'}<br />
					$Lang::tr{'pakfire last package update'} $packages_update_age $Lang::tr{'pakfire ago'}
					<form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='ACTION' value='update' /><br />
						<input type='submit' value='$Lang::tr{'calamaris refresh list'}' /><br />
					</form>
<br />
				<td align="center">
				<form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<select name="UPDPAKS" size="5" disabled>
END
						&Pakfire::dblist("upgrade", "forweb");
	print <<END;
					</select>
					<br />
					<input type='hidden' name='ACTION' value='upgrade' />
					<input type='image' alt='$Lang::tr{'upgrade'}' title='$Lang::tr{'upgrade'}' src='/images/document-save.png' />
				 </form>

		<tr><td colspan="2"><!-- Just an empty line -->&nbsp;
		<tr><td bgcolor='$color{'color20'}' align="center"><b>$Lang::tr{'pakfire available addons'}</b>
				<td bgcolor='$color{'color20'}' align="center"><b>$Lang::tr{'pakfire installed addons'}</b>
		<tr><td style="padding:5px 10px 20px 20px" align="center">
			<p>$Lang::tr{'pakfire install description'}</p>
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
				<select name="INSPAKS" size="10" multiple>
END
			&Pakfire::dblist("notinstalled", "forweb");

print <<END;
				</select>
				<br />
				<input type='hidden' name='ACTION' value='install' />
				<input type='image' alt='$Lang::tr{'install'}' title='$Lang::tr{'install'}' src='/images/list-add.png' />
			</form>

		<td style="padding:5px 10px 20px 20px" align="center">
			<p>$Lang::tr{'pakfire uninstall description'}</p>
		 <form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<select name="DELPAKS" size="10" multiple>
END

			&Pakfire::dblist("installed", "forweb");

print <<END;
			</select>
			<br />
			<input type='hidden' name='ACTION' value='remove' />
			<input type='image' alt='$Lang::tr{'remove'}' title='$Lang::tr{'remove'}' src='/images/list-remove.png' />
		</form>
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
	# Get PID of a running pakfire instance
	# (The system backpipe command is safe, because no user input is computed.)
	my $pakfire_pid = `pidof -s /usr/local/bin/pakfire`;
	chomp($pakfire_pid);

	# Test presence of PID or lockfile
	return (($pakfire_pid) || (-e "$Pakfire::lockfile"));
}

# Send HTTP headers
sub _start_json_output {
	print "Cache-Control: no-cache, no-store\n";
	print "Content-Type: application/json\n";
	print "\n"; # End of HTTP headers
}
