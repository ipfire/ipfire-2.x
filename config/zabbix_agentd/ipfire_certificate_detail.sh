#!/bin/bash
###############################################################################
# ipfire_certificate_detail.sh - Get certificate details and validation results
#                                in JSON format for use by Zabbix agent
#
# Author: robin.roevens (at) disroot.org
# Version: 1.0
#
# Copyright (C) 2007-2024  IPFire Team  <info@ipfire.org> 
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License 
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
###############################################################################

# Required binaries
OPENSSL=/usr/bin/openssl
DATE=/bin/date

# Parameter checking
[[ $1 ]] || { echo "{\"error\":\"No CA certificate file given.\"}"; exit 1; }
[[ -f $1 ]] || { echo "{\"error\":\"CA certificate not found: $1.\"}"; exit 1; }
[[ -r $1 ]] || { echo "{\"error\":\"No read permission on CA certificate: $1.\"}"; exit 1; }
[[ $2 ]] || { echo "{\"error\":\"No certificate file given.\"}"; exit 1; }
[[ -f $2 ]] || { echo "{\"error\":\"Certificate not found: $2.\"}"; exit 1; }
[[ -r $2 ]] || { echo "{\"error\":\"No read permission on certificate $2.\"}"; exit 1; }
[[ -x $OPENSSL ]] || { echo "{\"error\":\"$OPENSSL binary not found or no permission.\"}"; exit 1; }
[[ -x $DATE ]] || { echo "{\"error\":\"$DATE binary not found or no permission.\"}"; exit 1; }

cafile=$1
cert=$2

# Parse certificate details
cert_details=$(${OPENSSL} x509 -in "${cert}" -noout -text -certopt no_header,no_sigdump)
version=$(echo "${cert_details}" | grep "Version:" | sed 's/^ \+Version: \([0-9]\+\) (.\+)$/\1/g')
serial_number=$(echo "${cert_details}" | grep -A1 "Serial Number:" | tr -d '\n' | sed 's/^ \+Serial Number:\(\( \(.*\) ([0-9]\+x[0-9]\+).*\)\|\( \+\(.*\)$\)\)/\3\5/g')
signature_algorithm=$(echo "${cert_details}" | grep "Signature Algorithm:" | sed 's/^ \+Signature Algorithm: //g')
issuer=$(echo "${cert_details}" | grep "Issuer:" | sed 's/^ \+Issuer: //g' | sed 's/"/\\"/g')
not_before_value=$(echo "${cert_details}" | grep "Not Before:" | sed 's/^ \+Not Before: //g')
not_before_timestamp=$(${DATE} -d "${not_before_value}" +%s)
not_after_value=$(echo "${cert_details}" | grep "Not After :" | sed 's/^ \+Not After : //g')
not_after_timestamp=$(${DATE} -d "${not_after_value}" +%s)
subject=$(echo "${cert_details}" | grep "Subject:" | sed 's/^ \+Subject: //g' | sed 's/"/\\"/g')
public_key_algorithm=$(echo "${cert_details}" | grep "Public Key Algorithm:" | sed 's/^ \+Public Key Algorithm: //g')

# Verify certificate
cert_verify=$(${OPENSSL} verify -CAfile "${cafile}" "${cert}" 2>&1)
if [[ $? != 0 ]]; then
	result_value="invalid"
	result_message="failed to verify certificate: x509: $(echo "${cert_verify}" | grep -E "error [0-9]+" | sed 's/^.\+: \(.\+\)/\1/g')"
else
	result_value="valid"
	result_message="certificate verified successfully"
fi

# Generate fingerprints
sha1_fingerprint=$(${OPENSSL} x509 -in "${cert}" -noout -fingerprint -sha1 | cut -d= -f2)
sha256_fingerprint=$(${OPENSSL} x509 -in "${cert}" -noout -fingerprint -sha256 | cut -d= -f2)

# Print certificate details in JSON
echo -n "{\"x509\":{"
echo -n "\"version\":\"${version}\","
echo -n "\"serial_number\":\"${serial_number}\","
echo -n "\"signature_algorithm\":\"${signature_algorithm}\","
echo -n "\"issuer\":\"${issuer}\","
echo -n "\"not_before\":{"
echo -n "\"value\":\"${not_before_value}\","
echo -n "\"timestamp\":\"${not_before_timestamp}\"},"
echo -n "\"not_after\":{"
echo -n "\"value\":\"${not_after_value}\","
echo -n "\"timestamp\":\"${not_after_timestamp}\"},"
echo -n "\"subject\":\"${subject}\","
echo -n "\"public_key_algorithm\":\"${public_key_algorithm}\"},"
echo -n "\"result\":{"
echo -n "\"value\":\"${result_value}\","
echo -n "\"message\":\"${result_message}\"},"
echo -n "\"sha1_fingerprint\":\"${sha1_fingerprint}\","
echo -n "\"sha256_fingerprint\":\"${sha256_fingerprint}\""
echo -n "}"

exit 0