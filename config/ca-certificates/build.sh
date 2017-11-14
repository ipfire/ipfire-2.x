#!/bin/bash

set -e

# Create file layout.
mkdir -pv certs certs/legacy-default certs/legacy-disable
cp certdata.txt certs
cd certs

python ../certdata2pem.py

cd ..
cat <<EOF > ca-bundle.crt
# This is a bundle of X.509 certificates of public Certificate
# Authorities.  It was generated from the Mozilla root CA list.
# 
# Source: mozilla/security/nss/lib/ckfw/builtins/certdata.txt
#
EOF

cat <<EOF > ca-bundle.trust.crt
# This is a bundle of X.509 certificates of public Certificate
# Authorities.  It was generated from the Mozilla root CA list.
# These certificates are in the OpenSSL "TRUSTED CERTIFICATE"
# format and have trust bits set accordingly.
#
# Source: mozilla/security/nss/lib/ckfw/builtins/certdata.txt
#
EOF

for f in certs/*.crt; do 
	[ -z "${f}" ] && continue

	tbits=$(sed -n '/^# openssl-trust/{s/^.*=//;p;}' ${f})
	case "${tbits}" in
		*serverAuth*)
			openssl x509 -text -in "${f}" >> ca-bundle.crt
			;;
	esac

	if [ -n "$tbits" ]; then
		targs=""
		for t in ${tbits}; do
			targs="${targs} -addtrust ${t}"
		done

		openssl x509 -text -in "${f}" -trustout $targs >> ca-bundle.trust.crt
	fi
done

exit 0
