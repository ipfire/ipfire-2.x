#! /usr/bin/perl -w
use strict;
use Digest::MD5  qw(md5 md5_hex md5_base64);
#Same as HS_UAMSECRET in config file
my $uamsecret = "xxUAMSECRETxx";
my $js_header = "Content-type: text/javascript\n\n";
# Make sure that the get query parameters are clean
my $OK_CHARS='-a-zA-Z0-9_.@&=%!';
$_ = my $query=$ENV{QUERY_STRING};
s/[^$OK_CHARS]/_/go;
$query = $_;

my $return = '';
my ($username,$password,$challenge);

#Read query parameters which we care about
my @array = split('&',$query);
foreach my $var ( @array )
{
    my @array2 = split('=',$var);
    if ($array2[0] =~ /^username$/i) { $username = $array2[1]; }
    if ($array2[0] =~ /^password$/i) { $password = $array2[1]; }
    if ($array2[0] =~ /^challenge$/) { $challenge = $array2[1]; }
}
$password =~ s/\+/ /g;
$password =~s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/seg;
my $hexchal  = pack "H32", $challenge;
my $newchal  = md5($hexchal, $uamsecret);
my $pappassword = unpack "H32", ($password ^ $newchal);
# my $pappassword = $password;
print $js_header;
print "chilliJSON.reply({'response':'".$pappassword."'})";

