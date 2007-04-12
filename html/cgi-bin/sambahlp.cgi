#!/usr/bin/perl
#
# IPFire CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The IPFire Team

use strict;
# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

&Header::showhttpheaders();
&Header::openpage('Samba', 1, '');
&Header::openbigbox('100%', 'left', '', 'BigBox');
&Header::openbox('100%', 'left', '', 'Sambahelp');

	print <<END
	<br />
	<table width='95%' cellspacing='0'>
	<tr><td><b>$Lang::tr{'caption'}</b></td></tr>
	<tr><td><u>$Lang::tr{'options'}</u></td><td><u>$Lang::tr{'meaning'}</u> / <u>$Lang::tr{'exampel'}</u></td></tr>
	<tr><td>comment</td><td>$Lang::tr{'comment'}</td></tr>
	<tr><td></td><td>comment = $Lang::tr{'my new share'}</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>path</td><td>$Lang::tr{'path to directory'}</td></tr>
	<tr><td></td><td>path = /tmp</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>writeable</td><td>$Lang::tr{'directory writeable'}</td></tr>
	<tr><td></td><td>writeable = yes</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>browseable</td><td>sichtbar in Verzeichnisliste</td></tr>
	<tr><td></td><td>browsable = yes</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>user</td><td>Besitzer der Freigabe</td></tr>
	<tr><td></td><td>user = samba</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>valid users</td><td>Liste der Zugriffsberechtigten</td></tr>
	<tr><td></td><td>valid users = samba, user1</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>write list</td><td>$Lang::tr{'visible in browselist'}</td></tr>
	<tr><td></td><td>write list = samba</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>hosts allow</td><td>$Lang::tr{'host allow'}</td></tr>
	<tr><td></td><td>hosts allow = localhost 192.168.1.1 192.168.2.0/24</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>hosts deny</td><td>$Lang::tr{'host deny'}</td></tr>
	<tr><td></td><td>hosts deny = 192.168.1.2 192.168.3.0/24</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>read list</td><td>$Lang::tr{'read list'}</td></tr>
	<tr><td></td><td>read list = user1</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>admin users</td><td>$Lang::tr{'admin users'}</td></tr>
	<tr><td></td><td>admin users = user1</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>invalid users</td><td>$Lang::tr{'invalid users'}</td></tr>
	<tr><td></td><td>invalid users = user2</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>force user</td><td>$Lang::tr{'force user'}</td></tr>
	<tr><td></td><td>force user = samba</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>directory mask</td><td>$Lang::tr{'directory mask'}</td></tr>
	<tr><td></td><td>directory mask = 0777</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>create mask</td><td>U$Lang::tr{'create mask'}</td></tr>
	<tr><td></td><td>create mask = 0777</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>guest ok</td><td>$Lang::tr{'guest ok'}</td></tr>
	<tr><td></td><td>guest ok = yes</td></tr>
	</table>
END
;

&Header::closebox();
&Header::closebigbox();
&Header::closepage();
