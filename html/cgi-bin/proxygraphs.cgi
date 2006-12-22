#!/usr/bin/perl
#
# (c) 2002 Robert Wood <rob@empathymp3.co.uk>
#
# $Id: proxygraphs.cgi,v 1.2.2.5 2005/02/22 22:21:56 gespinasse Exp $
#

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %cgiparams=();
my %pppsettings=();
my %netsettings=();
my @graphs=();

&Header::showhttpheaders();

my $dir = "/srv/web/ipfire/html/sgraph";
$cgiparams{'ACTION'} = '';
&Header::getcgihash(\%cgiparams);
my $sgraphdir = "/srv/web/ipfire/html/sgraph";

&Header::openpage($Lang::tr{'proxy access graphs'}, 1, '');

&Header::openbigbox('100%', 'left');

&Header::openbox('100%', 'left', $Lang::tr{'proxy access graphs'} . ":" );

if (open(IPACHTML, "$sgraphdir/index.html"))
{
	my $skip = 1;
	while (<IPACHTML>)
	{
		$skip = 1 if /^<HR>$/;
		if ($skip)
		{
			$skip = 0 if /<H1>/;
			next;
		}
		s/<IMG SRC=([^"'>]+)>/<img src='\/sgraph\/$1' alt='Graph' \/>/;
		s/<HR>/<hr \/>/g;
		s/<BR>/<br \/>/g;
		s/<([^>]*)>/\L<$1>\E/g;
		s/(size|align|border|color)=([^'"> ]+)/$1='$2'/g;
		print;
	}
	close(IPACHTML);
}
else {
	print $Lang::tr{'no information available'}; }

&Header::closebox();

&Header::closebigbox();

&Header::closepage();
