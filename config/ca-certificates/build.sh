#!/bin/bash

set -e

# Create file layout.
mkdir -pv certs
mkdir -pv /etc/pki/ca-trust/source
cp certdata.txt certs
cd certs

python3 ../certdata2pem.py

cd ..


cat <<EOF > ca-bundle.trust.p11-kit
# This is a bundle of X.509 certificates of public Certificate
# Authorities.  It was generated from the Mozilla root CA list.
# These certificates and trust/distrust attributes use the file format accepted
# by the p11-kit-trust module.
#
# Source: mozilla/security/nss/lib/ckfw/builtins/certdata.txt
#
EOF


P11FILES=`find certs -name \*.tmp-p11-kit | wc -l`
if [ $P11FILES -ne 0 ]; then
  for p in certs/*.tmp-p11-kit; do 
    cat "$p" >> /etc/pki/ca-trust/source/ca-bundle.trust.p11-kit
  done	
fi

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

trust extract --comment --filter=certificates --format=openssl-bundle --overwrite ca-bundle.trust
cat ca-bundle.trust >> ca-bundle.trust.crt

trust extract --comment --filter=ca-anchors --format=pem-bundle --overwrite --purpose server-auth ca-bundle
cat ca-bundle >> ca-bundle.crt


exit 0