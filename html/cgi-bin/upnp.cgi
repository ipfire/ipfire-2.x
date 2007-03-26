#!/usr/bin/perl
#
# IPFire CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The IPFire Team
#

use strict;
# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %upnpsettings = ();
my %checked = ();
my %netsettings = ();
my $message = "";
my $errormessage = "";
my %selected= () ;
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

my %servicenames =
(
        'UPnP Daemon' => 'upnpd',
);

&Header::showhttpheaders();
############################################################################################################################
############################################### Setzen von Standartwerten ##################################################

$upnpsettings{'DEBUGMODE'} = '3';
$upnpsettings{'FORWARDRULES'} = 'yes';
$upnpsettings{'FORWARDCHAIN'} = 'FORWARD';
$upnpsettings{'PREROUTINGCHAIN'} = 'PORTFW';
$upnpsettings{'DOWNSTREAM'} = '900000';
$upnpsettings{'UPSTREAM'} = '16000000';
$upnpsettings{'DESCRIPTION'} = 'gatedesc.xml';
$upnpsettings{'XML'} = '/etc/linuxigd';
$upnpsettings{'ENABLED'} = 'off';
$upnpsettings{'GREENi'} = 'on';
$upnpsettings{'BLUEi'} = 'off';
$upnpsettings{'REDi'} = 'off';
$upnpsettings{'ORANGEi'} = 'off';
$upnpsettings{'GREENe'} = 'off';
$upnpsettings{'BLUEe'} = 'off';
$upnpsettings{'REDe'} = 'on';
$upnpsettings{'ORANGEe'} = 'off';
### Values that have to be initialized
$upnpsettings{'ACTION'} = '';

&General::readhash("${General::swroot}/upnp/settings", \%upnpsettings);
&Header::getcgihash(\%upnpsettings);

&Header::openpage('UPnP', 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
################################################### Speichern der Config ###################################################

if ($upnpsettings{'ACTION'} eq $Lang::tr{'save'})
{
&General::writehash("${General::swroot}/upnp/settings", \%upnpsettings);

	open (FILE, ">${General::swroot}/upnp/upnpd.conf") or die "Can't save the upnp config: $!";
	flock (FILE, 2);
	
print FILE <<END

# UPnP Config by Ipfire Project

debug_mode = $upnpsettings{'DEBUGMODE'}
insert_forward_rules = $upnpsettings{'FORWARDRULES'}
forward_chain_name = $upnpsettings{'FORWARDCHAIN'}
prerouting_chain_name = $upnpsettings{'PREROUTINGCHAIN'}
upstream_bitrate = $upnpsettings{'DOWNSTREAM'}
downstream_bitrate = $upnpsettings{'UPSTREAM'}
description_document_name = $upnpsettings{'DESCRIPTION'}
xml_document_path = $upnpsettings{'XML'}

END
;
close FILE;
}
elsif ($upnpsettings{'ACTION'} eq 'Start')
{
        $upnpsettings{'ENABLED'} = 'on';
        &General::writehash("${General::swroot}/upnp/settings", \%upnpsettings);
        system("/usr/local/bin/upnpctrl upnpdstart $netsettings{'RED_DEV'} $netsettings{'GREEN_DEV'}");
} 
elsif ($upnpsettings{'ACTION'} eq 'Stop')
{
        $upnpsettings{'ENABLED'} = 'off';
        &General::writehash("${General::swroot}/upnp/settings", \%upnpsettings);
        system("/usr/local/bin/upnpctrl stop");
} 
elsif ($upnpsettings{'ACTION'} eq $Lang::tr{'restart'})
{
        &General::writehash("${General::swroot}/upnp/settings", \%upnpsettings);
        system("/usr/local/bin/upnpctrl stop");
        system("/usr/local/bin/upnpctrl start $netsettings{'RED_DEV'} $netsettings{'GREEN_DEV'}");
}

&General::readhash("${General::swroot}/upnp/settings", \%upnpsettings);

if ($errormessage) {
        &Header::openbox('100%', 'left', $Lang::tr{'error messages'});
        print "<class name='base'>$errormessage\n";
        print "&nbsp;</class>\n";
        &Header::closebox();
}

$checked{'GREENi'}{'on'} = '';
$checked{'GREENi'}{'off'} = '';
$checked{'GREENi'}{"$upnpsettings{'GREENi'}"} = 'checked';
$checked{'BLUEi'}{'on'} = '';
$checked{'BLUEi'}{'off'} = '';
$checked{'BLUEi'}{"$upnpsettings{'BLUEi'}"} = 'checked';
$checked{'REDi'}{'on'} = '';
$checked{'REDi'}{'off'} = '';
$checked{'REDi'}{"$upnpsettings{'REDi'}"} = 'checked';
$checked{'ORANGEi'}{'on'} = '';
$checked{'ORANGEi'}{'off'} = '';
$checked{'ORANGEi'}{"$upnpsettings{'ORANGEi'}"} = 'checked';
$checked{'GREENe'}{'on'} = '';
$checked{'GREENe'}{'off'} = '';
$checked{'GREENe'}{"$upnpsettings{'GREENe'}"} = 'checked';
$checked{'BLUEe'}{'on'} = '';
$checked{'BLUEe'}{'off'} = '';
$checked{'BLUEe'}{"$upnpsettings{'BLUEe'}"} = 'checked';
$checked{'REDe'}{'on'} = '';
$checked{'REDe'}{'off'} = '';
$checked{'REDe'}{"$upnpsettings{'REDe'}"} = 'checked';
$checked{'ORANGEe'}{'on'} = '';
$checked{'ORANGEe'}{'off'} = '';
$checked{'ORANGEe'}{"$upnpsettings{'ORANGEe'}"} = 'checked';

############################################################################################################################
############################################################################################################################

&Header::openbox('100%', 'center', 'UPnP');
print <<END
        <form method='post' action='$ENV{'SCRIPT_NAME'}'>
        <table width='95%' cellspacing='0'>
END
;
        if ( $message ne "" ) {
                print "<tr><td colspan='3' align='center'><font color='red'>$message</font>";
        }

        my $lines = 0;
        my $key = '';
        foreach $key (sort keys %servicenames)
        {
                if ($lines % 2) {
                        print "<tr bgcolor='${Header::table1colour}'>\n"; }
                else {
                        print "<tr bgcolor='${Header::table2colour}'>\n"; }
                print "<td align='left'>$key\n";
                my $shortname = $servicenames{$key};
                my $status = &isrunning($shortname);
                print "$status\n";
                $lines++;
        }
        print <<END
                <tr><td><b>Alle Dienste:</b></td><td colspan='2'>
                <input type='submit' name='ACTION' value='Start' /> 
                <input type='submit' name='ACTION' value='Stop' /> 
                <input type='submit' name='ACTION' value='$Lang::tr{'restart'}' />
        </table>
END
;
#print <<END
#        <br></br>
#        <hr />
#        <br></br>
#        
#        <table width='95%'>
#        <tr><td colspan='2' align='left' bgcolor='${Header::table1colour}'><b>External Interface</b></td></tr>
#        <tr><td align='left'>&nbsp;</td><td><input type='radio' name='External' value='$netsettings{'RED_DEV'}' $checked{'REDe'}{'on'}><font size='2' color='$Header::colourred'><b>RED - $netsettings{'RED_DEV'}</b></font><br></br>
#                                            <input type='radio' name='External' value='$netsettings{'GREEN_DEV'}' $checked{'GREENe'}{'on'}><font size='2' color='$Header::colourgreen'><b>$Lang::tr{'green'} - $netsettings{'GREEN_DEV'}</b></font><br></br>
#END
#;
#         if (&Header::blue_used()){
#         print <<END
#                                             <input type='radio' name='External' value='$netsettings{'BLUE_DEV'}' $checked{'BLUEe'}{'on'}><font size='2' color='$Header::colourblue'><b>$Lang::tr{'wireless'} - $netsettings{'BLUE_DEV'}</b></font><br></br>
#END
#;
#                                    }
#         if (&Header::orange_used()){
#         print <<END
#                                             <input type='radio' name='External' value='$netsettings{'ORANGE_DEV'}' $checked{'ORANGEe'}{'on'}><font size='2' color='$Header::colourorange'><b>$Lang::tr{'dmz'} - $netsettings{'ORANGE_DEV'}</b></font><br></br>
#END
#;
#                                    }
#        print <<END
#        </td></tr>
#        <tr><td colspan='2' align='left'><br></br></td></tr>
#        <tr><td colspan='2' align='left' bgcolor='${Header::table1colour}'><b>Internal Interface</b></td></tr>
#        <tr><td align='left'>&nbsp;</td><td><input type='radio' name='Internal' value='$netsettings{'RED_DEV'}' $checked{'REDi'}{'on'}><font size='2' color='$Header::colourred'><b>RED - $netsettings{'RED_DEV'}</b></font><br></br>
#                                            <input type='radio' name='Internal' value='$netsettings{'GREEN_DEV'}' $checked{'GREENi'}{'on'}><font size='2' color='$Header::colourgreen'><b>$Lang::tr{'green'} - $netsettings{'GREEN_DEV'}</b></font><br></br>
#END
#;
#         if (&Header::blue_used()){
#         print <<END
#                                            <input type='radio' name='Internal' value='$netsettings{'BLUE_DEV'}' $checked{'BLUEi'}{'on'}><font size='2' color='$Header::colourblue'><b>$Lang::tr{'wireless'} - $netsettings{'BLUE_DEV'}</b></font><br></br>
#END
#;
#                                    }
#         if (&Header::orange_used()){
#         print <<END
#                                            <input type='radio' name='Internal' value='$netsettings{'ORANGE_DEV'}' $checked{'ORANGEi'}{'on'}><font size='2' color='$Header::colourorange'><b>$Lang::tr{'dmz'} - $netsettings{'ORANGE_DEV'}</b></font><br></br>
#END
#;
#                                    }
#        print <<END
#        </td></tr></table>
print <<END
</form>
<br></br>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
<tr><td colspan='2' align='left' bgcolor='${Header::table1colour}'><b>$Lang::tr{'options'}</b></td></tr>
<tr><td colspan='2' align='left'><br></br></td></tr>
<tr><td align='left'>Debug Mode:</td><td><input type='text' name='DEBUGMODE' value='$upnpsettings{'DEBUGMODE'}' size="30"></input></td></tr>
<tr><td align='left'>Forward Rules:</td><td><input type='text' name='FORWARDRULES' value='$upnpsettings{'FORWARDRULES'}' size="30"></input></td></tr>
<tr><td align='left'>Forward Chain:</td><td><input type='text' name='FORWARDCHAIN' value='$upnpsettings{'FORWARDCHAIN'}' size="30"></input></td></tr>
<tr><td align='left'>Prerouting Chain:</td><td><input type='text' name='PREROUTINGCHAIN' value='$upnpsettings{'PREROUTINGCHAIN'}' size="30"></input></td></tr>
<tr><td align='left'>Down Stream:</td><td><input type='text' name='DOWNSTREAM' value='$upnpsettings{'DOWNSTREAM'}' size="30"></input></td></tr>
<tr><td align='left'>Up Strean:</td><td><input type='text' name='UPSTREAM' value='$upnpsettings{'UPSTREAM'}' size="30"></input></td></tr>
<tr><td align='left'>Description Document:</td><td><input type='text' name='DESCRIPTION' value='$upnpsettings{'DESCRIPTION'}' size="30"></input></td></tr>
<tr><td align='left'>XML Document:</td><td><input type='text' name='XML' value='$upnpsettings{'XML'}' size="30"></input></td></tr>
<tr><td colspan='2' align='left'><br></br></td></tr>
<tr><td colspan='2' align='center'><input type='submit' name='ACTION' value=$Lang::tr{'save'} />
</table></form>
<br></br>
<hr></hr>
END
;
&Header::closebox();

&Header::closebigbox();
&Header::closepage();

############################################################################################################################
############################################################################################################################

sub isrunning
{
        my $cmd = $_[0];
        my $status = "<td bgcolor='${Header::colourred}'><font color='white'><b>$Lang::tr{'stopped'}</b></font></td>";
        my $pid = '';
        my $testcmd = '';
        my $exename;

        $cmd =~ /(^[a-z]+)/;
        $exename = $1;

        if (open(FILE, "/var/run/${cmd}.pid"))
        {
                $pid = <FILE>; chomp $pid;
                close FILE;
                if (open(FILE, "/proc/${pid}/status"))
                {
                        while (<FILE>)
                        {
                                if (/^Name:\W+(.*)/) {
                                        $testcmd = $1; }
                        }
                        close FILE;
                        if ($testcmd =~ /$exename/)
                        {
                                $status = "<td bgcolor='${Header::colourgreen}'><font color='white'><b>$Lang::tr{'running'}</b></font></td>";
                        }
                }
        }

        return $status;
}
