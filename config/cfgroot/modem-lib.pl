#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2014 IPFire Team  <info@ipfire.org>                           #
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

use Device::Modem;

package Modem;

sub new() {
	my $class = shift;

	my $port = shift;
	my $baud = shift;

	my $self = {};
	bless $self, $class;

	# Initialize the connetion to the modem.
	my $ret = $self->_initialize($port, $baud);
	if ($ret) {
		return undef;
	}

	if ($self->_is_working()) {
		return $self;
	}

	return undef;
}

sub DESTROY() {
	my $self = shift;

	# Close connection to modem.
	if ($self->{modem}) {
		$self->{modem}->close();
	}
}

sub _initialize() {
	my ($self, $port, $baud) = @_;

	# Check if the character device actually exists.
	if (! -c $port) {
		return 1;
	}

	# Establish connection to the modem.
	$self->{modem} = new Device::Modem(port => $port);
	$self->{modem}->connect(baudrate => $baud);

	return 0;
}

sub _is_working() {
	my $self = shift;

	# Check if the modem responds to AT commands.
	$self->{modem}->atsend("AT\r\n");

	my $response = $self->{modem}->answer();
	return ($response eq "OK");
}

sub _command() {
	my $self = shift;
	my $cmd  = shift;

	# Terminate the AT command with newline.
	$cmd .= "\r\n";

	$self->{modem}->atsend($cmd);

	my $response = $self->{modem}->answer();
	my @response = split(/\n/, $response);

	# Trim leading and trailing spaces.
	foreach my $line (@response) {
		$line =~ s/^\s+|\s+$//g;
		chomp($line);
	}

	my $last_element = pop(@response);
	unless ($last_element eq "OK") {
		push(@response, $last_element);
	}

	$response = join("\n", @response);

	return $self->_trim($response);
}

sub _trim() {
	my $self = shift;
	my $input = shift;

	my $first_char = substr($input, 0, 1);
	if ($first_char eq "+") {
		my @output = split(/:/, $input);
		if ($#output == 1) {
			return $output[1];
		}
	}

	return $input;
}

sub get_vendor() {
	my $self = shift;

	return $self->_command("AT+GMI");
}

sub get_model() {
	my $self = shift;

	return $self->_command("AT+GMM");
}

sub get_software_version() {
	my $self = shift;

	return $self->_command("AT+GMR");
}

sub get_imei() {
	my $self = shift;

	return $self->_command("AT+GSN");
}

sub get_capabilities() {
	my $self = shift;

	my $output = $self->_command("AT+GCAP");
	return split(/,/, $output);
}

sub is_sim_unlocked() {
	my $self = shift;

	# TODO
	return 1;
}

sub get_sim_imsi() {
	my $self = shift;

	if ($self->is_sim_unlocked()) {
		return $self->_command("AT+CIMI");
	}
}

sub get_network_registration() {
	my $self = shift;

	my @elements;
	foreach my $i ([0, 1]) {
		my $output = $self->_command("AT+CREG?");

		@elements = split(/,/, $output);
		if ($#elements != 2) {
			# Output in wrong format. Resetting.
			$self->_command("AT+CREG=0");
		}
	}

	if ($elements[0] == 0) {
		if ($elements[1] == 0) {
			return "NOT REGISTERED, NOT SEARCHING";
		} elsif ($elements[1] == 1) {
			return "REGISTERED TO HOME NETWORK";
		} elsif ($elements[1] == 2) {
			return "NOT REGISTERED, SEARCHING";
		} elsif ($elements[1] == 3) {
			return "REGISTRATION DENIED";
		} elsif ($elements[1] == 5) {
			return "REGISTERED, ROAMING";
		} else {
			return "UNKNOWN";
		}
	}
}

sub _get_network_operator() {
	my $self = shift;

	my $output = $self->_command("AT+COPS?");
	$output =~ s/\"//g;

	my @elements = split(/,/, $output);
	if ($#elements == 3) {
		return @elements;
	}
}

sub get_network_operator() {
	my $self = shift;

	my ($mode, $format, $operator, $act) = $self->_get_network_operator();

	return $operator;
}

sub get_network_mode() {
	my $self = shift;

	my ($mode, $format, $operator, $act) = $self->_get_network_operator();

	if ($act == 0) {
		return "GSM";
	} elsif ($act == 1) {
		return "Compact GSM";
	} elsif ($act == 2) {
		return "UMTS";
	} elsif ($act == 3) {
		return "GSM WITH EGPRS";
	} elsif ($act == 4) {
		return "UMTS WITH HSDPA";
	} elsif ($act == 5) {
		return "UMTS WITH HSUPA";
	} elsif ($act == 6) {
		return "UMTS WITH HSDPA+HSUPA";
	} elsif ($act == 7) {
		return "LTE";
	} else {
		return "UNKNOWN ($act)";
	}
}

sub _get_signal_quality() {
	my $self = shift;

	my $output = $self->_command("AT+CSQ");

	my @elements = split(/,/, $output);
	if ($#elements == 1) {
		return @elements;
	}
}

sub get_signal_quality() {
	my $self = shift;

	my ($rssi, $ber) = $self->_get_signal_quality();

	# 99 equals unknown.
	unless ($rssi == 99) {
		my $dbm = ($rssi * 2) - 113;
		return $dbm;
	}

	return undef;
}

sub get_bit_error_rate() {
	my $self = shift;

	my ($rssi, $ber) = $self->_get_signal_quality();

	# 99 indicates unknown.
	unless ($ber == 99) {
		return $ber;
	}

	return undef;
}

1;
