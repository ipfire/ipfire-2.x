#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007  Michael Tremer & Christian Schmidt                      #
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
