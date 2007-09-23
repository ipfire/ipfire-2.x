<?php
/* Created by setup.php (1.0.0) on Sun, 23 Sep 2007 16:44:38 +0200 */
$cfg['user_ignore']		= array('cyrus');
$cfg['passwd']['strategy']	= 'PasswordPlaintext';

// repeat these lines for every server or virtual domain
$cfg['Servers']['verbose'][] = 'my database';
$cfg['Servers']['number'][] = $i++;
$cfg['Servers']['DB'][] = array(
	'DSN'		=> 'mysql://root:mysqlfire@localhost/mail',
	'PREFIX'	=> '',
);
$cfg['Servers']['IMAP'][] = array(
	'TYPE'	=> 'cyrus',
	'HOST'	=> 'localhost',
	'PORT'	=> 143,
	'ADMIN'	=> 'cyrus',
	'PASS'	=> 'ipfire',
	'VDOM'	=> ''
);
?>