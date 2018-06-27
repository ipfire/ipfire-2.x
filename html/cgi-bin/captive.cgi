#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2016  IPFire Team  <alexander.marx@ipfire.org>                #
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

#use strict;
use Encode;
use HTML::Entities();
use File::Basename;
use PDF::API2;
use constant mm => 25.4 / 72;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %session_times = (
	3600		=> $Lang::tr{'one hour'},
	14400		=> $Lang::tr{'four hours'},
	28800		=> $Lang::tr{'eight hours'},
	43200		=> $Lang::tr{'twelve hours'},
	86400		=> $Lang::tr{'24 hours'},
	604800		=> $Lang::tr{'one week'},
	1209600		=> $Lang::tr{'two weeks'},
	2592000 	=> $Lang::tr{'one month'},
	31536000	=> $Lang::tr{'one year'},
	0		=> "- $Lang::tr{'unlimited'} -",
);

my %selected = ();

my $coupons = "${General::swroot}/captive/coupons";
my %couponhash = ();

my $logo = "${General::swroot}/captive/logo.dat";

my %settings=();
my %mainsettings;
my %color;
my %cgiparams=();
my %netsettings=();
my %checked=();
my $errormessage='';
my $clients="${General::swroot}/captive/clients";
my %clientshash=();
my $settingsfile="${General::swroot}/captive/settings";
unless (-e $settingsfile)	{ system("touch $settingsfile"); }

&Header::getcgihash(\%cgiparams);

&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);
&General::readhash("$settingsfile", \%settings) if(-f $settingsfile);
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

if ($cgiparams{'ACTION'} eq "export-coupons") {
	my $pdf = &generate_pdf();

	print "Content-Type: application/pdf\n";
	print "Content-Disposition: attachment; filename=captive-portal-coupons.pdf\n";
	print "\n"; # end headers

	# Send PDF
	print $pdf;

	exit(0);
}


&Header::showhttpheaders();

if ($cgiparams{'ACTION'} eq $Lang::tr{'save'}) {
	my $file = $cgiparams{'logo'};
	if ($file) {
		# Check if the file extension is PNG/JPEG
		chomp $file;

		my ($name, $path, $ext) = fileparse($file, qr/\.[^.]*$/);
		if ($ext ne ".png" && $ext ne ".jpg" && $ext ne ".jpeg") {
			$errormessage = $Lang::tr{'Captive wrong ext'};
		}
	}

	$settings{'ENABLE_GREEN'}		= $cgiparams{'ENABLE_GREEN'};
	$settings{'ENABLE_BLUE'}		= $cgiparams{'ENABLE_BLUE'};
	$settings{'AUTH'}				= $cgiparams{'AUTH'};
	$settings{'TITLE'}				= $cgiparams{'TITLE'};
	$settings{'COLOR'}			= $cgiparams{'COLOR'};
	$settings{'SESSION_TIME'}		= $cgiparams{'SESSION_TIME'};

	if (!$errormessage){
		#Check if we need to upload a new logo
		if ($file) {
			# Save logo
			my ($filehandle) = CGI::upload("logo");

			# XXX check filesize

			open(FILE, ">$logo");
			binmode $filehandle;
			while (<$filehandle>) {
				print FILE;
			}
			close(FILE);
		}

		&General::writehash("$settingsfile", \%settings);

		# Save terms
		$cgiparams{'TERMS'} = &Header::escape($cgiparams{'TERMS'});
		open(FH, ">:utf8", "/var/ipfire/captive/terms.txt") or die("$!");
		print FH $cgiparams{'TERMS'};
		close(FH);
		$cgiparams{'TERMS'} = "";

		#execute binary to reload firewall rules
		system("/usr/local/bin/captivectrl");

		if ($cgiparams{'ENABLE_BLUE'} eq 'on'){
				system("/usr/local/bin/wirelessctrl");
		}
	}
}

if ($cgiparams{'ACTION'} eq "$Lang::tr{'Captive generate coupons'}") {
	#check valid remark
	if ($cgiparams{'REMARK'} ne '' && !&validremark($cgiparams{'REMARK'})){
		$errormessage=$Lang::tr{'fwhost err remark'};
	}

	if (!$errormessage) {
		# Remember selected values
		foreach my $val (("SESSION_TIME", "COUNT", "REMARK")) {
			$settings{$val} = $cgiparams{$val};
		}
		&General::writehash($settingsfile, \%settings);

		&General::readhasharray($coupons, \%couponhash) if (-e $coupons);
		my $now = time();

		# Expiry time in seconds
		my $expires = $settings{'SESSION_TIME'};

		my $count = $settings{'COUNT'} || 1;
		while($count-- > 0) {
			# Generate a new code
			my $code = &gencode();

			# Check if the coupon code already exists
			foreach my $key (keys %couponhash) {
				if($couponhash{$key}[1] eq $code) {
					# Code already exists, so try again
					$code = "";
					$count++;
					last;
				}
			}

			next if ($code eq "");

			# Get a new key from hash
			my $key = &General::findhasharraykey(\%couponhash);

			# Initialize all fields
			foreach my $i (0 .. 3) { $couponhash{$key}[$i] = ""; }

			$couponhash{$key}[0] = $now;
			$couponhash{$key}[1] = $code;
			$couponhash{$key}[2] = $expires;
			$couponhash{$key}[3] = $settings{'REMARK'};
		}

		# Save everything to disk
		&General::writehasharray($coupons, \%couponhash);
	}
}

if ($cgiparams{'ACTION'} eq 'delete-coupon') {
	#deletes an already generated but unused voucher

	#read all generated vouchers
	&General::readhasharray($coupons, \%couponhash) if (-e $coupons);
	foreach my $key (keys %couponhash) {
		if($cgiparams{'key'} eq $couponhash{$key}[0]){
			#write logenty with decoded remark
			my $rem=HTML::Entities::decode_entities($couponhash{$key}[4]);
			&General::log("Captive", "Delete unused coupon $couponhash{$key}[1] $couponhash{$key}[2] hours valid expires on $couponhash{$key}[3] remark $rem");
			#delete line from hash
			delete $couponhash{$key};
			last;
		}
	}
	#write back hash
	&General::writehasharray($coupons, \%couponhash);
}

if ($cgiparams{'ACTION'} eq 'delete-client') {
	#delete voucher and connection in use

	#read all active clients
	&General::readhasharray($clients, \%clientshash) if (-e $clients);
	foreach my $key (keys %clientshash) {
		if($cgiparams{'key'} eq $clientshash{$key}[0]){
			#prepare log entry with decoded remark
			my $rem=HTML::Entities::decode_entities($clientshash{$key}[7]);
			#write logentry
			&General::log("Captive", "Deleted client in use $clientshash{$key}[1] $clientshash{$key}[2] hours valid expires on $clientshash{$key}[3] remark $rem - Connection will be terminated");
			#delete line from hash
			delete $clientshash{$key};
			last;
		}
	}
	#write back hash
	&General::writehasharray("$clients", \%clientshash);
	#reload firewallrules to kill connection of client
	system("/usr/local/bin/captivectrl");
}

#open webpage, print header and open box
&Header::openpage($Lang::tr{'Captive'}, 1, '');
&Header::openbigbox();

# If an error message exists, show a box with the error message
if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print $errormessage;
	&Header::closebox();
}

# Prints the config box on the website
&Header::openbox('100%', 'left', $Lang::tr{'Captive config'});
print <<END
	<form method='post' action='$ENV{'SCRIPT_NAME'}' enctype="multipart/form-data">\n
		<table width='100%' border="0">
END
;

#check which parameters have to be enabled (from settings file)
$checked{'ENABLE_GREEN'}{'off'} = '';
$checked{'ENABLE_GREEN'}{'on'} = '';
$checked{'ENABLE_GREEN'}{$settings{'ENABLE_GREEN'}} = "checked='checked'";

$checked{'ENABLE_BLUE'}{'off'} = '';
$checked{'ENABLE_BLUE'}{'on'} = '';
$checked{'ENABLE_BLUE'}{$settings{'ENABLE_BLUE'}} = "checked='checked'";

$checked{'UNLIMITED'}{'off'} = '';
$checked{'UNLIMITED'}{'on'} = '';
$checked{'UNLIMITED'}{$settings{'UNLIMITED'}} = "checked='checked'";

$selected{'AUTH'} = ();
$selected{'AUTH'}{'COUPON'} = "";
$selected{'AUTH'}{'TERMS'} = "";
$selected{'AUTH'}{$settings{'AUTH'}} = "selected";

if ($netsettings{'GREEN_DEV'}){
	print <<END;
		<tr>
			<td width='30%'>
				$Lang::tr{'Captive active on'}
				<font color='$Header::colourgreen'>$Lang::tr{'green'}</font>
			</td>
			<td>
				<input type='checkbox' name='ENABLE_GREEN' $checked{'ENABLE_GREEN'}{'on'} />
			</td>
		</tr>
END
}

if ($netsettings{'BLUE_DEV'}){
	print <<END;
		<tr>
			<td width='30%'>
				$Lang::tr{'Captive active on'}
				<font color='$Header::colourblue'>$Lang::tr{'blue'}</font>
			</td>
			<td>
				<input type='checkbox' name='ENABLE_BLUE' $checked{'ENABLE_BLUE'}{'on'} />
			</td>
		</tr>
END
}

print<<END
	<tr>
		<td>
			$Lang::tr{'Captive authentication'}
		</td>
		<td>
			<select name='AUTH'>
				<option value="TERMS"  $selected{'AUTH'}{'TERMS'} >$Lang::tr{'Captive terms'}</option>
				<option value="COUPON" $selected{'AUTH'}{'COUPON'}>$Lang::tr{'Captive coupon'}</option>
			</select>
		</td>
	</tr>
END
;

if ($settings{'AUTH'} eq 'TERMS') {
	$selected{'SESSION_TIME'} = ();
	foreach my $session_time (keys %session_times) {
		$selected{'SESSION_TIME'}{$session_time} = "";
	}
	$selected{'SESSION_TIME'}{$settings{'SESSION_TIME'}} = "selected";

	print <<END;
		<tr>
			<td>$Lang::tr{'Captive client session expiry time'}</td>
			<td>
				<select name="SESSION_TIME">
END

	foreach my $session_time (sort { $a <=> $b } keys %session_times) {
		print <<END;
					<option value="$session_time" $selected{'SESSION_TIME'}{$session_time}>
						$session_times{$session_time}
					</option>
END
	}

	print <<END;
				</select>
			</td>
		</tr>
END
}

print<<END;
	<tr>
		<td colspan="2">
			<br>
			<strong>$Lang::tr{'Captive branding'}</strong>
		</td>
	</tr>
	<tr>
		<td>
			$Lang::tr{'Captive title'}
		</td>
		<td>
			<input type='text' name='TITLE' value="$settings{'TITLE'}" size='40'>
		</td>
	</tr>
	<tr>
		<td>$Lang::tr{'Captive brand color'}</td>
		<td>
			<input type="color" name="COLOR" value="$settings{'COLOR'}">
		</td>
	</tr>
	<tr>
		<td>
			$Lang::tr{'Captive upload logo'}
		</td>
		<td>
			<input type="file" name="logo">
			<br>$Lang::tr{'Captive upload logo recommendations'}
		</td>
	</tr>
END

if (-e $logo) {
	print <<END;
		<tr>
			<td>$Lang::tr{'Captive logo uploaded'}</td>
			<td>$Lang::tr{'yes'}</td>
		</tr>
END
}

my $terms = &getterms();
print <<END;
	<tr>
		<td>$Lang::tr{'Captive terms'}</td>
		<td>
			<textarea cols="50" rows="10" name="TERMS">$terms</textarea>
		</td>
	</tr>
	<tr>
		<td></td>
		<td align='right'>
			<input type='submit' name='ACTION' value="$Lang::tr{'save'}"/>
		</td>
	</tr>
	</table></form>
END

&Header::closebox();

#if settings is set to use coupons, the coupon part has to be displayed
if ($settings{'AUTH'} eq 'COUPON') {
	&coupons();
}

# Show active clients
&show_clients();

sub getterms() {
	my @ret;

	open(FILE, "<:utf8", "/var/ipfire/captive/terms.txt");
	while(<FILE>) {
		push(@ret, HTML::Entities::decode_entities($_));
	}
	close(FILE);

	return join(/\n/, @ret);
}

sub gencode(){
	#generate a random code only letters from A-Z except 'O'  and 0-9
	my @chars = ("A".."N", "P".."Z", "0".."9");
	my $randomstring;
	$randomstring .= $chars[rand @chars] for 1..8;
	return $randomstring;
}

sub coupons() {
	&Header::openbox('100%', 'left', $Lang::tr{'Captive generate coupons'});

	$selected{'SESSION_TIME'} = ();
	foreach my $session_time (keys %session_times) {
		$selected{'SESSION_TIME'}{$session_time} = "";
	}
	$selected{'SESSION_TIME'}{$settings{'SESSION_TIME'}} = "selected";

	print <<END;
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<table border='0' width='100%'>
				<tr>
					<td width='30%'>
						$Lang::tr{'Captive vouchervalid'}
					</td>
					<td width='70%'>
						<select name="SESSION_TIME">
END

	foreach my $session_time (sort { $a <=> $b } keys %session_times) {
		print <<END;
							<option value="$session_time" $selected{'SESSION_TIME'}{$session_time}>
								$session_times{$session_time}
							</option>
END
	}

	print <<END;
						</select>
					</td>
				</tr>
				<tr>
					<td>$Lang::tr{'remark'}</td>
					<td>
						<input type='text' name='REMARK' size=40>
					</td>
				</tr>
				<tr>
					<td>$Lang::tr{'Captive generated coupon no'}</td>
					<td>
						<select name="COUNT">
							<option value="1">1</option>
							<option value="2">2</option>
							<option value="3">3</option>
							<option value="4">4</option>
							<option value="5">5</option>
							<option value="6">6</option>
							<option value="7">7</option>
							<option value="8">8</option>
							<option value="9">9</option>
							<option value="10">10</option>
							<option value="20">20</option>
							<option value="50">50</option>
							<option value="100">100</option>
						</select>
					</td>
				</tr>
			</table>

			<div align="right">
				<input type="submit" name="ACTION" value="$Lang::tr{'Captive generate coupons'}">
			</div>
		</form>
END

	&Header::closebox();

	# Show all coupons if exist
	if (! -z $coupons) {
		&show_coupons();
	}
}

sub show_coupons() {
	&General::readhasharray($coupons, \%couponhash) if (-e $coupons);

	#if there are already generated but unsused coupons, print a table
	&Header::openbox('100%', 'left', $Lang::tr{'Captive issued coupons'});

	print <<END;
		<table class='tbl' border='0'>
			<tr>
				<th align='center' width='15%'>
					$Lang::tr{'Captive coupon'}
				</th>
				<th align='center' width='15%'>$Lang::tr{'Captive expiry time'}</th>
				<th align='center' width='65%'>$Lang::tr{'remark'}</th>
				<th align='center' width='5%'>$Lang::tr{'delete'}</th>
			</tr>
END

	foreach my $key (keys %couponhash) {
		my $expirytime = $Lang::tr{'Captive nolimit'};
		if ($couponhash{$key}[2] > 0) {
			$expirytime = &General::format_time($couponhash{$key}[2]);
		}

		if ($count++ % 2) {
			$col="bgcolor='$color{'color20'}'";
		} else {
			$col="bgcolor='$color{'color22'}'";
		}

		print <<END;
			<tr>
				<td $col align="center">
					<b>$couponhash{$key}[1]</b>
				</td>
				<td $col align="center">
					$expirytime
				</td>
				<td $col align="center">
					$couponhash{$key}[3]
				</td>
				<td $col align="center">
					<form method='post'>
						<input type='image' src='/images/delete.gif' align='middle' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' />
						<input type='hidden' name='ACTION' value='delete-coupon' />
						<input type='hidden' name='key' value='$couponhash{$key}[0]' />
					</form>
				</td>
			</tr>
END
	}

	print "</table>";

	# Download PDF
	print <<END;
		<div align="right">
			<form method="POST">
				<input type="hidden" name="ACTION" value="export-coupons">
				<input type="submit" value="$Lang::tr{'Captive export coupons'}">
			</form>
		</div>
END

	&Header::closebox();
}

sub show_clients() {
	# if there are active clients which use coupons show table
	return if ( -z $clients || ! -f $clients );

	my $count=0;
	my $col;

	&Header::openbox('100%', 'left', $Lang::tr{'Captive clients'});

	print <<END;
		<table class='tbl' width='100%'>
			<tr>
				<th align='center' width='15%'>$Lang::tr{'Captive coupon'}</th>
				<th align='center' width='15%'>$Lang::tr{'Captive activated'}</th>
				<th align='center' width='15%'>$Lang::tr{'Captive expiry time'}</th>
				<th align='center' width='10%'>$Lang::tr{'Captive mac'}</th>
				<th align='center' width='43%'>$Lang::tr{'remark'}</th>
				<th align='center' width='5%'>$Lang::tr{'delete'}</th>
			</tr>
END

	&General::readhasharray($clients, \%clientshash) if (-e $clients);
	foreach my $key (keys %clientshash) {
		#calculate time from clientshash (starttime)
		my $starttime = sub{sprintf '%02d.%02d.%04d %02d:%02d', $_[3], $_[4]+1, $_[5]+1900, $_[2], $_[1]  }->(localtime($clientshash{$key}[2]));

		#calculate endtime from clientshash
		my $endtime;
		if ($clientshash{$key}[3] eq '0'){
			$endtime=$Lang::tr{'Captive nolimit'};
		} else {
			$endtime = sub{sprintf '%02d.%02d.%04d %02d:%02d', $_[3], $_[4]+1, $_[5]+1900, $_[2], $_[1]  }->(localtime($clientshash{$key}[2]+$clientshash{$key}[3]));
		}

		if ($count++ % 2) {
			$col="bgcolor='$color{'color20'}'";
		} else {
			$col="bgcolor='$color{'color22'}'";
		}

		my $coupon = ($clientshash{$key}[4] eq "LICENSE") ? $Lang::tr{'Captive terms short'} : $clientshash{$key}[4];

		print <<END;
			<tr>
				<td $col align="center"><b>$coupon</b></td>
				<td $col align="center">$starttime</td>
				<td $col align="center">$endtime</td>
				<td $col align="center">$clientshash{$key}[0]</td>
				<td $col align="center">$clientshash{$key}[5]</td>
				<td $col align="center">
					<form method='post'>
						<input type='image' src='/images/delete.gif' align='middle' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' />
						<input type='hidden' name='ACTION' value='delete-client' />
						<input type='hidden' name='key' value='$clientshash{$key}[0]' />
					</form>
				</td>
			</tr>
END
	}

	print "</table>";

	&Header::closebox();
}

sub validremark
{
	# Checks a hostname against RFC1035
        my $remark = $_[0];
	# Each part should be at least two characters in length
	# but no more than 63 characters
	if (length ($remark) < 1 || length ($remark) > 255) {
		return 0;}
	# Only valid characters are a-z, A-Z, 0-9 and -
	if ($remark !~ /^[a-zäöüA-ZÖÄÜ0-9-.:;\|_()\/\s]*$/) {
		return 0;}
	# First character can only be a letter or a digit
	if (substr ($remark, 0, 1) !~ /^[a-zäöüA-ZÖÄÜ0-9]*$/) {
		return 0;}
	# Last character can only be a letter or a digit
	if (substr ($remark, -1, 1) !~ /^[a-zöäüA-ZÖÄÜ0-9.:;_)]*$/) {
		return 0;}
	return 1;
}

sub generate_pdf() {
	my $pdf = PDF::API2->new();

	my ($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) = gmtime(time);
	my $timestamp = sprintf("D:%04d%02d%02d%02d%02d%02d+00;00", $year+1900, $mon+1, $mday, $hour, $min, $sec);

	$pdf->info(
		"Creator"      => $Lang::tr{'Captive portal'},
		"Title"        => $Lang::tr{'Captive portal coupons'},
		"CreationDate" => $timestamp,
		"ModDate"      => $timestamp,
	);

	# Set page size
	$pdf->mediabox("A4");
	$pdf->trimbox(28/mm, 27/mm, 182/mm, 270/mm);

	# Set font
	my $font = $pdf->ttfont("/usr/share/fonts/Ubuntu-R.ttf");

	my $page_h_margin = 27/mm;
	my $page_v_margin = 28/mm;

	my $height = 68/mm;
	my $width  = 91/mm;
	my $margin =  2/mm;

	# Tux Image
	my $tux_image = $pdf->image_png("/srv/web/ipfire/html/captive/assets/ipfire.png");
	my $logo_height = 12/mm;
	my $logo_width  = 12/mm;

	my @coupons = ();
	my %coupon_expiry_times = ();

	# Read coupons
	&General::readhasharray($coupons, \%couponhash) if (-e $coupons);
	foreach my $key (keys %couponhash) {
		$coupon_expiry_times{$couponhash{$key}[1]} = $couponhash{$key}[2];
		push @coupons, $couponhash{$key}[1];
	}

	while (@coupons) {
		# Make a new page
		my $page = $pdf->page();

		# Graphics
		$gfx = $page->gfx();

		# Headline font
		my $f_headline = $page->text();
		$f_headline->font($font, 20);

		# Subheadline font
		my $f_subheadline = $page->text();
		$f_subheadline->font($font, 14);

		# Coupon font
		my $f_coupon = $page->text();
		$f_coupon->font($font, 36);

		# Lifetime
		my $f_lifetime = $page->text();
		$f_lifetime->font($font, 14);

		# Watermark font
		my $f_watermark = $page->text();
		$f_watermark->fillcolor("#666666");
		$f_watermark->font($font, 10);

		my $i = 0;
		while (@coupons && $i < 8) {
			my $coupon = shift @coupons;

			# Box corners
			my $x = ($page_v_margin / 2) + (($i % 2) ? $width : 0);
			my $y = ($page_h_margin / 2) + (int($i / 2) * $height);

			# Weidth and height of the box
			my $w = $width - $margin;
			my $h = $height - $margin;

			# Center
			my $cx = $x + ($w / 2);
			my $cy = $y + ($h / 2);

			# Draw border box
			$gfx->strokecolor("#333333");
			$gfx->linedash(1/mm, 1/mm);
			$gfx->rect($x, $y, $w, $h);
			$gfx->stroke();
			$gfx->endpath();

			# Headline
			$f_headline->translate($cx, ($y + $h - $cy) / 1.7 + $cy);
			$f_subheadline->translate($cx, ($y + $h - $cy) / 2.4 + $cy);

			if ($settings{'TITLE'}) {
				$f_headline->text_center(decode("utf8", $settings{'TITLE'}));
				$f_subheadline->text_center(decode("utf8", $Lang::tr{'Captive WiFi coupon'}));
			} else {
				$f_headline->text_center(decode("utf8", $Lang::tr{'Captive WiFi coupon'}));
			}

			# Coupon
			$f_coupon->translate($cx, $cy);
			$f_coupon->text_center(decode("utf8", $coupon));

			# Show lifetime
			my $expiry_time = $coupon_expiry_times{$coupon};
			$f_lifetime->translate($cx, $cy - ($y + $h - $cy) / 4);
			if ($expiry_time > 0) {
				my $lifetime = &General::format_time($expiry_time);
				$f_lifetime->text_center(decode("utf8", $Lang::tr{'Captive valid for'} . " " . $lifetime));
			} else {
				$f_lifetime->text_center(decode("utf8", $Lang::tr{'Captive nolimit'}));
			}

			# Add watermark
			$gfx->image($tux_image, $x + $w - $logo_width - $margin, $y + $margin, $logo_width, $logo_height);
			$f_watermark->translate($x + $w - ($margin * 2) - $logo_width, $y + ($logo_height / 2));
			$f_watermark->text_right("Powered by IPFire");

			$i++;
		}
	}

	# Write out the PDF document
	return $pdf->stringify();
}

&Header::closebigbox();
&Header::closepage();
