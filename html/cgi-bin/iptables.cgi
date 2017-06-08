#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2010  IPFire Team                                             #
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

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

#use warnings;
#use CGI::Carp 'fatalsToBrowser';

my $debug = 0;
my @iplines;
my $string = "";
my $lines = 0;
my @ipmanlines;
my $manlines = 0;
my @ipnatlines;
my $natlines = 0;
my %chains;
my %chainsman;
my %chainsnat;
my $chainname;
my $selectedchain;
my %netsettings = ();
my %cgiparams=();

&Header::getcgihash(\%cgiparams);

system('/usr/local/bin/getipstat');

&Header::showhttpheaders();
&Header::openpage($Lang::tr{'ipts'}, 1, '');
&Header::openbigbox('100%', 'LEFT');

# This debug is used to see what inputs are done via the cgi and
# what parameters are to be executed

if ( $debug ){
	&Header::openbox('100%', 'center', 'DEBUG');
	my $debugCount = 0;
	foreach my $line (sort keys %cgiparams) {
		print "$line = '$cgiparams{$line}'<br />\n";
		$debugCount++;
	}
	print "&nbsp;Count: $debugCount\n";
	&Header::closebox();
}

&Header::openbox('100%', 'LEFT', $Lang::tr{'ipts'}.':');

# If the cgi is called the first time the default chain is
# used, otherwise if user selected a chains in the selectboxes
# those one are displayed, it is possible to change all 3 at
# the same time

if ( $cgiparams{'selectedchain'} ne "" ){
	my @multi = split(/\|/,$cgiparams{'selectedchain'});
	$selectedchain = $multi[0];
} else {
	$selectedchain = "INPUT";
}

print <<END

<div align='left'>
END
;

# We´ll open the txt files and extract each line, if the line
# start with an Chain the the name, start- and endline of the
# chain is extracted into a hash

	open (FILE, '/var/tmp/iptables.txt');
	while (<FILE>){

		$iplines[$lines] = $_;

		if ( $_ =~ /^Chain/  ){

			my @chainstring = split(/ /,$_);

			if ( $chainname ne "" ){
				$chains{$chainname."end"} = $lines-2;
			}

			$chainname = $chainstring[1];
			$chains{$chainname."start"} = $lines; 
		}

		$lines++;

	}
	$chains{$chainname."end"} = $lines-1;
	close (FILE);

# now the chain hash is extracted to get the correct name of the chain
# all chains are displayed as a select box and can be choosen for display
# after this all corresponding lines for the chain are extraced and seperated
# into table rows, sometimes we need to handle leading blank so the offset is
# needed, some lines need to chomp trailing seperators. The interfaces and
# network addresses should be colorized by an extra function to make a nice
# colored gui

	print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n<select name='selectedchain' style='width: 250px'>\n";
	foreach (sort(keys(%chains))){

		if ( $_ =~ /end$/ ){
			next;
		} else {
			$_ =~ s/start$//gi;
		}

		print "   <option value='".$_;
		if ( $_ eq $selectedchain ){
			print "' selected='selected' >".$_."</option>\n";
		} else {
			print "'>".$_."</option>\n";
		}
	}
	print "</select><input type='submit' name='ACTION' value='$Lang::tr{'update'}' /><form><br /><br />\n\n";

	$string = $iplines[$chains{$selectedchain."start"}];
	$string =~ s/\s$//gi;

	print "<strong>".$string."</strong><br />\n\n";
	print "<table width='100%' cellspacing='1'>\n<tr>\n";
	foreach (split(/ +/,$iplines[$chains{$selectedchain."start"}+1])){
		if ( $_  =~ /[^a-zA-Z]/ ){chomp($_);}
		print "   <th align='left'><strong>".$_."</strong></th>\n";
	}

	print "</tr>\n";

	print "<tr>\n";
	print "   <td width='0'></td>\n   <td width='60'></td>\n   <td width='60'></td>\n";
	print "   <td width='150'></td>\n   <td width='30'></td>\n";
	print "   <td width='30'></td>\n   <td width='40'></td>\n";
	print "   <td width='40'></td>\n   <td width='95'></td>\n";
	print "   <td width='95'></td>\n   <td width='260'></td>\n";
	print "</tr>\n";


	for(my $i = $chains{$selectedchain."start"}+2; $i <= $chains{$selectedchain."end"}; $i++) {
		print "<tr>\n";

		my @iptablesline = split(/ +/,$iplines[$i]);
		my $offset=0;

		 if ( $iptablesline[0] eq "" ){
			$offset=1;
		 }

		print "   <td></td>\n   <td>".$iptablesline[0+$offset]."</td>\n   <td>".$iptablesline[1+$offset]."</td>\n";
		print "   <td>".$iptablesline[2+$offset]."</td>\n   <td>".$iptablesline[3+$offset]."</td>\n";
		print "   <td>".$iptablesline[4+$offset]."</td>\n   <td>".&Header::colorize($iptablesline[5+$offset])."</td>\n";
		print "   <td>".&Header::colorize($iptablesline[6+$offset])."</td>\n";
		print "   <td>".&Header::colorize($iptablesline[7+$offset])."</td>\n";
		print "   <td>".&Header::colorize($iptablesline[8+$offset])."</td>\n   <td>";

		for (my $i=9+$offset; $i <= $#iptablesline; $i++){
			$string = $iptablesline[$i];
			$string =~ s/\s$//gi;
			print " ".$string;
		}
		print "</td>\n</tr>\n";
	}
print "</table></div><br />";
&Header::closebox();

## MANGLE
&Header::openbox('100%', 'LEFT', $Lang::tr{'iptmangles'}.':');

# If the cgi is called the first time the default chain is
# used, otherwise if user selected a chains in the selectboxes
# those one are displayed, it is possible to change all 3 at
# the same time

if ( $cgiparams{'selectedchain'} ne "" ){
	my @multi = split(/\|/,$cgiparams{'selectedchain'});
	$selectedchain = $multi[1];
} else {
	$selectedchain = "PREROUTING";
}

print <<END

<div align='left'>
END
;

# We´ll open the txt files and extract each line, if the line
# start with an Chain the the name, start- and endline of the
# chain is extracted into a hash

	open (FILE, '/var/tmp/iptablesmangle.txt');
	while (<FILE>){

		$ipmlines[$manlines] = $_;

		if ( $_ =~ /^Chain/  ){

			my @chainstring = split(/ /,$_);

			if ( $chainname ne "" ){
				$chainsman{$chainname."end"} = $manlines-2;
			}

			$chainname = $chainstring[1];
			$chainsman{$chainname."start"} = $manlines; 
		}

		$manlines++;
	   
	}
	$chainsman{$chainname."end"} = $manlines-1;
	close (FILE);

# now the chain hash is extracted to get the correct name of the chain
# all chains are displayed as a select box and can be choosen for display
# after this all corresponding lines for the chain are extraced and seperated
# into table rows, sometimes we need to handle leading blank so the offset is
# needed, some lines need to chomp trailing seperators. The interfaces and
# network addresses should be colorized by an extra function to make a nice
# colored gui

	print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n<select name='selectedchain' style='width: 250px'>\n";
	foreach (sort(keys(%chainsman))){

		if ( $_ =~ /end$/ ){
			next;
		} else {
			$_ =~ s/start$//gi;
		}

		print "   <option value='".$_;
		if ( $_ eq $selectedchain ){
			print "' selected='selected' >".$_."</option>\n";
		} else {
			print "'>".$_."</option>\n";
		}
	}
	print "</select><input type='submit' name='ACTION' value='$Lang::tr{'update'}' /><form><br /><br />\n\n";

	$string = $ipmanlines[$chainsman{$selectedchain."start"}];
	$string =~ s/\s$//gi;

	print "<strong>".$string."</strong><br />\n\n";
	print "<table width='100%' cellspacing='1'>\n<tr>\n";
	foreach (split(/ +/,$ipmlines[$chainsman{$selectedchain."start"}+1])){
		if ( $_  =~ /[^a-zA-Z]/ ){chomp($_);}
		print "   <th align='left'><strong>".$_."</strong></th>\n";
	}

	print "</tr>\n";

	print "<tr>\n";
	print "   <td width='0'></td>\n   <td width='60'></td>\n   <td width='60'></td>\n";
	print "   <td width='150'></td>\n   <td width='30'></td>\n";
	print "   <td width='30'></td>\n   <td width='40'></td>\n";
	print "   <td width='40'></td>\n   <td width='95'></td>\n";
	print "   <td width='95'></td>\n   <td width='260'></td>\n";
	print "</tr>\n";

	for(my $i = $chainsman{$selectedchain."start"}+2; $i <= $chainsman{$selectedchain."end"}; $i++) {
		print "<tr>\n";
		my @iptablesline = split(/ +/,$ipmlines[$i]);
		my $offset=0;

		 if ( $iptablesline[0] eq "" ){
			$offset=1;
		}

		print "   <td></td>\n   <td>".$iptablesline[0+$offset]."</td>\n   <td>".$iptablesline[1+$offset]."</td>\n";
		print "   <td>".$iptablesline[2+$offset]."</td>\n   <td>".$iptablesline[3+$offset]."</td>\n";
		print "   <td>".$iptablesline[4+$offset]."</td>\n   <td>".&Header::colorize($iptablesline[5+$offset])."</td>\n";
		print "   <td>".&Header::colorize($iptablesline[6+$offset])."</td>\n";
		print "   <td>".&Header::colorize($iptablesline[7+$offset])."</td>\n";
		print "   <td>".&Header::colorize($iptablesline[8+$offset])."</td>\n   <td>";

		for (my $i=9+$offset; $i <= $#iptablesline; $i++){
			$string = $iptablesline[$i];
			$string =~ s/\s$//gi;

# mangles with marks need to be converted from hex to number to show the correct qos class

			if ( $string =~ /^0x/){
				$string = hex($string);
			}

			print " ".$string;
		}
		print "</td>\n</tr>\n";
	}
print "</table></div><br />";
&Header::closebox();

## NAT
&Header::openbox('100%', 'LEFT', $Lang::tr{'iptnats'}.':');

# If the cgi is called the first time the default chain is
# used, otherwise if user selected a chains in the selectboxes
# those one are displayed, it is possible to change all 3 at
# the same time

if ( $cgiparams{'selectedchain'} ne "" ){
	my @multi = split(/\|/,$cgiparams{'selectedchain'});
	$selectedchain = $multi[2];
} else {
	$selectedchain = "PREROUTING";
}

print <<END

<div align='left'>
END
;

# We´ll open the txt files and extract each line, if the line
# start with an Chain the the name, start- and endline of the
# chain is extracted into a hash

	open (FILE, '/var/tmp/iptablesnat.txt');
	while (<FILE>){

		$ipnatlines[$natlines] = $_;

		if ( $_ =~ /^Chain/  ){

			my @chainstring = split(/ /,$_);

			if ( $chainname ne "" ){
				$chainsnat{$chainname."end"} = $natlines-2;
			}

			$chainname = $chainstring[1];
			$chainsnat{$chainname."start"} = $natlines; 
		}

		$natlines++;
	   
	}
	$chainsnat{$chainname."end"} = $natlines-1;
	close (FILE);

# now the chain hash is extracted to get the correct name of the chain
# all chains are displayed as a select box and can be choosen for display
# after this all corresponding lines for the chain are extraced and seperated
# into table rows, sometimes we need to handle leading blank so the offset is
# needed, some lines need to chomp trailing seperators. The interfaces and
# network addresses should be colorized by an extra function to make a nice
# colored gui

	print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n<select name='selectedchain' style='width: 250px'>\n";
	foreach (sort(keys(%chainsnat))){

		if ( $_ =~ /end$/ ){
			next;
		} else {
			$_ =~ s/start$//gi;
		}

		print "   <option value='".$_;
		if ( $_ eq $selectedchain ){
			print "' selected='selected' >".$_."</option>\n";
		} else {
			print "'>".$_."</option>\n";
		}
	}
	print "</select><input type='submit' name='ACTION' value='$Lang::tr{'update'}' /><form><br /><br />\n\n";

	$string = $ipnatlines[$chainsnat{$selectedchain."start"}];
	$string =~ s/\s$//gi;

	print "<strong>".$string."</strong><br />\n\n";
	print "<table width='100%' cellspacing='1'>\n<tr>\n";
	foreach (split(/ +/,$ipnatlines[$chainsnat{$selectedchain."start"}+1])){
		if ( $_  =~ /[^a-zA-Z]/ ){chomp($_);}
		print "<th align='left'><strong>".$_."</strong></th>\n";
	}

	print "</tr>\n";

	print "<tr>\n";
	print "   <td width='0'></td>\n   <td width='60'></td>\n   <td width='60'></td>\n";
	print "   <td width='150'></td>\n   <td width='30'></td>\n";
	print "   <td width='30'></td>\n   <td width='40'></td>\n";
	print "   <td width='40'></td>\n   <td width='95'></td>\n";
	print "   <td width='95'></td>\n   <td width='260'></td>\n";
	print "</tr>\n";

	for(my $i = $chainsnat{$selectedchain."start"}+2; $i <= $chainsnat{$selectedchain."end"}; $i++) {
		print "<tr>\n";
		my @iptablesline = split(/ +/,$ipnatlines[$i]);
		my $offset=0;

		 if ( $iptablesline[0] eq "" ){
			$offset=1;
		}

		print "   <td></td>\n<td>".$iptablesline[0+$offset]."</td>\n   <td>".$iptablesline[1+$offset]."</td>\n";
		print "   <td>".$iptablesline[2+$offset]."</td>\n   <td>".$iptablesline[3+$offset]."</td>\n";
		print "   <td>".$iptablesline[4+$offset]."</td>\n   <td>".&Header::colorize($iptablesline[5+$offset])."</td>\n";
		print "   <td>".&Header::colorize($iptablesline[6+$offset])."</td>\n";
		print "   <td>".&Header::colorize($iptablesline[7+$offset])."</td>\n";
		print "   <td>".&Header::colorize($iptablesline[8+$offset])."</td>\n   <td>";

		for (my $i=9+$offset; $i <= $#iptablesline; $i++){
			$string = $iptablesline[$i];
			$string =~ s/\s$//gi;
			print " ".$string;
		}
		print "</td>\n</tr>\n";
	}
print "</table></div><br />";
&Header::closebox();
&Header::closebigbox();
&Header::closepage();

system("rm -f /var/tmp/iptables.txt");
system("rm -f /var/tmp/iptablesmangle.txt");
system("rm -f /var/tmp/iptablesnat.txt");
