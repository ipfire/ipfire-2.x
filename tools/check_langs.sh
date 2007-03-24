#!/bin/bash


if [ ! -d ./langs/ ]; then
	echo "Script can only be started from IPCop Source base directory"
	exit 1
fi

cat ./langs/de/cgi-bin/de.pl | grep \'.*\' | awk -F\' '{print $2}'| sort > /tmp/de_cgi-bin.$$
cat ./langs/de/install/lang_de.c | grep TR_ | awk -F\  '{print $2}' > /tmp/de_install.$$

for i in ./langs/en; do
    if [ "$i" == "./langs/.svn" ] ; then continue; fi
    language=`echo "$i" | awk -F/  '{ print $3 }'`

    echo "############################################################################"
    echo "# Checking install/setup translations for language: ${language}                     #"
    echo "############################################################################"
    cat ./langs/${language}/install/lang_${language}.c | grep TR_ | awk -F\  '{print $2}' | \
        diff /tmp/de_install.$$ - |  grep \<

    echo "############################################################################"
    echo "# Checking cgi-bin translations for language: ${language}                           #"
    echo "############################################################################"
    cat ./langs/${language}/cgi-bin/${language}.pl | grep \'.*\' | awk -F\' '{print $2}' | sort | \
        diff /tmp/de_cgi-bin.$$ - | grep \<
done

rm -f /tmp/de_cgi-bin.$$
rm -f /tmp/de_install.$$

exit 0

