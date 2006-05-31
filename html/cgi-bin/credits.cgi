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
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require 'CONFIG_ROOT/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

&Header::showhttpheaders();

&Header::openpage($Lang::tr{'credits'}, 1, '');

&Header::openbigbox('100%', 'center');

&Header::openbox('100%', 'left', $Lang::tr{'credits'});

print <<END
<br /><center><b>Besuchen sie uns auf <a href='http://www.ipfire.org/'>http://www.ipfire.org/</a></b></center>
<br /><center><b>Visit us on <a href='http://www.ipfire.org/'>http://www.ipfire.org/</a></b></center>
<p>
<br /><center><b>IPFire is based on IPFire and Smoothwall. Many thanks to its developers for this great piece of software.</b></center>

<p><b>Credits:</b><br />
Projektleiter - Michael Tremer
(<a href='mailto:m.s.tremer\@gmail.com'>m.s.tremer\@gmail.com</a>)<br />
Projektmitglied &amp; Sponsor - Detlef Lampart
(<a href='mailto:info\@delaco.de'>info\@delaco.de</a>)<br />
Projektmitglied &amp; Webinterfacedesign - Benedikt Correll
(<a href='mailto:benedikt_correll\@hotmail.com'>benedikt_correll\@hotmail.com</a>)<br />
...to be continued
</p>
END
;

&Header::closebox();

&Header::closebigbox();

&Header::closepage();
