# Set up i18n variables

if [ -f "/etc/sysconfig/console" ]; then
	. /etc/sysconfig/console
else
	LANG=en_US.UTF-8
fi

unset KEYMAP FONT UNICODE KEYMAP_CORRECTIONS LEGACY_CHARSET
export LANG
