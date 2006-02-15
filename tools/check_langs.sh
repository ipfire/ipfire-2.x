#!/bin/bash

if [ ! -d ./langs/ ]; then
	echo "Script can only be started from IPCop Source base directory"
	exit 1
fi

cat ./langs/en/cgi-bin/en.pl | grep \'.*\' | awk -F\' '{print $2}'| sort > /tmp/en_cgi-bin.$$
cat ./langs/en/install/lang_en.c | grep TR_ | awk -F\  '{print $2}' > /tmp/en_install.$$

for i in ./langs/[a-z]*; do
    if [ "$i" == "./langs/CVS" ] ; then continue; fi
    language=`echo "$i" | awk -F/  '{ print $3 }'`

    echo "############################################################################"
    echo "# Checking install/setup translations for language: ${language}                     #"
    echo "############################################################################"
    cat ./langs/${language}/install/lang_${language}.c | grep TR_ | awk -F\  '{print $2}' | \
        diff /tmp/en_install.$$ - |  grep \<

    echo "############################################################################"
    echo "# Checking cgi-bin translations for language: ${language}                           #"
    echo "############################################################################"
    cat ./langs/${language}/cgi-bin/${language}.pl | grep \'.*\' | awk -F\' '{print $2}' | sort | \
        diff /tmp/en_cgi-bin.$$ - | grep \<
done

rm -f /tmp/en_cgi-bin.$$
rm -f /tmp/en_install.$$

exit 0

