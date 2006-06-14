#!/usr/bin/perl
#
# IPFire CGIs
#
# This code is distributed under the terms of the GPL
#

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my @iplines;
my $lines = 0;
my @ipmanlines;
my $manlines = 0;
my @ipnatlines;
my $natlines = 0;

system('/usr/local/bin/getipstat');

&Header::showhttpheaders();
&Header::openpage($Lang::tr{'ipts'}, 1, '');
&Header::openbigbox('100%', 'LEFT');
&Header::openbox('100%', 'LEFT', $Lang::tr{'ipts'}.':');
print <<END

    <DIV align='left'>
    <PRE>
END
;
	open (FILE, '/home/httpd/html/iptables.txt');
	while (<FILE>)
       {
         	$iplines[$lines] = $_;
		$lines++;
       }
	close (FILE);
	foreach $_ (@iplines) {
		print "$_"; }

print <<END
    </PRE>
    </DIV>
    <BR> 

END
;
&Header::closebox();

## MANGLE
&Header::openbox('100%', 'LEFT', $Lang::tr{'iptmangles'}.':');
print <<END

    <DIV align='left'>
    <PRE>
END
;
	open (FILEMAN, '/home/httpd/html/iptablesmangle.txt');
	while (<FILEMAN>)
       {
         	$ipmanlines[$manlines] = $_;
		$manlines++;
       }
	close (FILEMAN);
	foreach $_ (@ipmanlines) {
		print "$_"; }

print <<END
    </PRE>
    </DIV>
    <BR> 

END
;
&Header::closebox();

## NAT
&Header::openbox('100%', 'LEFT', $Lang::tr{'iptnats'}.':');
print <<END

    <DIV align='left'>
    <PRE>
END
;
	open (FILENAT, '/home/httpd/html/iptablesnat.txt');
	while (<FILENAT>)
       {
         	$ipnatlines[$natlines] = $_;
		$natlines++;
       }
	close (FILENAT);
	foreach $_ (@ipnatlines) {
		print "$_"; }

print <<END
    </PRE>
    </DIV>
    <BR> 

END
;
&Header::closebox();
&Header::closebigbox();
&Header::closepage();

unlink /home/httpd/html/iptables.txt;
unlink /home/httpd/html/iptablesmangle.txt;
unlink /home/httpd/html/iptablesnat.txt;
