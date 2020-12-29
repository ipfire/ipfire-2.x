#!/usr/bin/perl

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

&Header::showhttpheaders();

my %cgiparams;

&Header::getcgihash(\%cgiparams);

&Header::openpage('asterisk', 1, '');

&Header::openbigbox('100%', 'LEFT');

if ($cgiparams{'ACTION'} eq $Lang::tr{'save'})
  {
        $conf_file = $cgiparams{'save_path'};
        open (FILE, ">$conf_file") or die "Kann die Datei nicht speichern: $!";
        flock (FILE, 2);
        print FILE "$cgiparams{'textarea'}";
        close FILE;
        &Header::openbox('100%', 'LEFT', 'info');
        print "$conf_file wurde gespeichert";
        &Header::closebox();
  }

if ($cgiparams{'ACTION'} eq Bearbeiten)
  {
        $conf_file = $cgiparams{'conf_file'};
  }

if ($conf_file eq '') {
	$conf_file='/var/ipfire/asterisk/extensions.conf';
  }

if ($cgiparams{'ACTION'} eq extensions)
  {
       $conf_file='/var/ipfire/asterisk/extensions.conf';
  }

if ($cgiparams{'ACTION'} eq sip)
  {
	$conf_file='/var/ipfire/asterisk/sip.conf';
  }

if ($cgiparams{'ACTION'} eq iax)
  {
	$conf_file='/var/ipfire/asterisk/iax.conf';
  }




if ($errormessage) {
	&Header::openbox('100%', 'LEFT', $tr{'error messages'});
	print "<FONT CLASS='base'>$errormessage&nbsp;</FONT>\n";
	&Header::closebox();
}

$cgiparams{'ACTION'} = '';

print "<FORM METHOD='POST'>\n";

if ($conf_file ne '') {

&Header::openbox('100%', 'LEFT', $conf_file);
	print <<END
  		<center><table border=0> 
			<tr><td><textarea name="textarea" cols="80" rows="20" wrap="VIRTUAL">
END
;
system("cat $conf_file");
print <<END
</textarea>\n 

	<tr><td align=center>
	<p><input type=text name=save_path value=$conf_file size=25>
	<p><input type=submit name=ACTION value='$Lang::tr{'save'}'>
	</table>

END
;

&Header::closebox();
}

&Header::openbox('100%', 'LEFT', 'Dateiauswahl');

my $dir = '/var/ipfire/asterisk/';
my @dateien;

listFiles ($dir);

print <<END
<table width=100% border=0>
<tr><td width=33% align=right>
    <!-- Buttons -->
	<input type=submit name=ACTION value=extensions><input type=submit name=ACTION value=sip><input type=submit name=ACTION value=iax>
    <td width=33% align=right>
	<center><select name=conf_file>
END
;
foreach $line (sort (@dateien)) {
$op_name =  $line;
$op_name =~ s/$dir//g;
print "<option value='$line'>$op_name</option>\n";
}

my $dir2 = '/home/httpd/cgi-bin/asterisk/conf/';
my @dateien2;

listFiles2 ($dir2);

foreach $line2 (sort (@dateien2)) {
$op_name2 =  $line2;
$op_name2 =~ s/$dir2//g;
print "<option value='$line2'>$op_name2</option>\n";
}

print "</select><input type=submit name=ACTION value=Bearbeiten></center><td width=33% align=right>&nbsp</table>";

sub listFiles {
local *DH;
my ($item, $pfad);
my $dir = shift;

opendir (DH, $dir) or return;
while ($item = readdir (DH)) {
next if ( $item =~ /^\./ );
$pfad = ( ($dir =~ /\/$/) ? ($dir . $item) : ($dir . '/'.$item) );
push (@dateien, $pfad) if (-f $pfad);
listFiles ($pfad) if (-d $pfad);
}
closedir (DH);
}

sub listFiles2 {
local *DH2;
my ($item2, $pfad2);
my $dir2 = shift;

opendir (DH2, $dir2) or return;
while ($item2 = readdir (DH2)) {
next if ( $item2 =~ /^\./ );
$pfad2 = ( ($dir2 =~ /\/$/) ? ($dir2 . $item2) : ($dir2 . '/'.$item2) );
push (@dateien2, $pfad2) if (-f $pfad2);
listFiles2 ($pfad2) if (-d $pfad2);
}
closedir (DH2);
}


&Header::closebox();

print "</FORM>\n";

&Header::closebigbox();

&Header::closepage();
