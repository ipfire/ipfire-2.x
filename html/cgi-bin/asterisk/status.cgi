#!/usr/bin/perl

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

&Header::showhttpheaders();

#use warnings;
#use CGI::Carp 'fatalsToBrowser';

my %asterisksettings;

&Header::getcgihash(\%asterisksettings);

&Header::openpage('asterisk', 1, '');

&Header::openbigbox('100%', 'LEFT');

if ($asterisksettings{'ACTION'} eq 'Start')
{
	system("/etc/init.d/asterisk start >/dev/null 2>&1");
	sleep 5;
}
if ($asterisksettings{'ACTION'} eq $Lang::tr{'stop'})
{
        system("/etc/init.d/asterisk stop >/dev/null 2>&1");
        sleep 5;
}
if ($asterisksettings{'ACTION'} eq $Lang::tr{'reboot'})
{
        system("/etc/init.d/asterisk restart >/dev/null 2>&1");
        sleep 5;
}
if ($asterisksettings{'ACTION'} eq "$Lang::tr{'reload'} EXT")
{
        system("/etc/init.d/asterisk remod ext >/dev/null 2>&1");
}
if ($asterisksettings{'ACTION'} eq "$Lang::tr{'reload'} SIP")
{
        system("/etc/init.d/asterisk remod sip >/dev/null 2>&1");
}
if ($asterisksettings{'ACTION'} eq "$Lang::tr{'reload'} IAX")
{
        system("/etc/init.d/asterisk remod iax >/dev/null 2>&1");
}

	my $pid = '';
	my $testcmd = '';
	my $exename;
	my @memory;

	if (open(FILE, "/var/run/asterisk.pid")){
		$pid = <FILE>; chomp $pid;
		close FILE;
		if (open(FILE, "/proc/${pid}/status")){
			while (<FILE>){
				if (/^Name:\W+(.*)/) {$testcmd = $1;}
			}
			close FILE;
		}
		}

if ($testcmd !~ /asterisk/) {
	$checked{'ENABLE_AST'}{'status_s'}="<font style=\"color:white;background-color:red;\"> $Lang::tr{'not running'}</font>";
	$checked{'ENABLE_AST'}{'status_b'}="<INPUT TYPE='submit' NAME='ACTION' VALUE='Start'>";
} else {
	$checked{'ENABLE_AST'}{'status_s'}="<font style=\"color:white;background-color:green;\"> $Lang::tr{'running'}</font>";
	$checked{'ENABLE_AST'}{'status_b'}="<INPUT TYPE='submit' NAME='ACTION' VALUE='$Lang::tr{'reboot'}'><INPUT TYPE='submit' NAME='ACTION' VALUE='$Lang::tr{'stop'}'>";
}

if ($errormessage) {
	&Header::openbox('100%', 'LEFT', $tr{'error messages'});
	print "<FONT CLASS='base'>$errormessage&nbsp;</FONT>\n";
	&Header::closebox();
}

if ($message) {
	&Header::openbox('100%', 'LEFT', 'Message');
	print "<FONT CLASS='base'>$message&nbsp;</FONT>\n";
	&Header::closebox();
}

print "<FORM METHOD='POST'>\n";

&Header::openbox('100%', 'LEFT', 'Status:');
	print <<END
  		<center>
<TABLE WIDTH='100%'>
<TR>
	<TD WIDTH='33%' CLASS='base' ALIGN='RIGHT'>Asterisk</TD>
	<TD WIDTH='33%' ALIGN='RIGHT'>$checked{'ENABLE_AST'}{'status_s'}</TD>
	<TD WIDTH='33%' ALIGN='LEFT'>$checked{'ENABLE_AST'}{'status_b'}</TD>
</TR>
<TR>
	<TD WIDTH='33%' CLASS='base' ALIGN='RIGHT'>Dialplan</TD>
	<TD WIDTH='33%' ALIGN='RIGHT'></TD>
	<TD WIDTH='33%' ALIGN='LEFT'> <INPUT TYPE='submit' NAME='ACTION' VALUE='$Lang::tr{'reload'} EXT'></TD>
</TR>
<TR>
        <TD WIDTH='33%' CLASS='base' ALIGN='RIGHT'>SIP</TD>
        <TD WIDTH='33%' ALIGN='RIGHT'></TD>
        <TD WIDTH='33%' ALIGN='LEFT'> <INPUT TYPE='submit' NAME='ACTION' VALUE='$Lang::tr{'reload'} SIP'></TD>
</TR>
<TR>
        <TD WIDTH='33%' CLASS='base' ALIGN='RIGHT'>IAX</TD>
        <TD WIDTH='33%' ALIGN='RIGHT'></TD>
        <TD WIDTH='33%' ALIGN='LEFT'> <INPUT TYPE='submit' NAME='ACTION' VALUE='$Lang::tr{'reload'} IAX'></TD>
</TR>

</TABLE>
END
;

&Header::closebox();

&Header::closebigbox();

&Header::closepage();
