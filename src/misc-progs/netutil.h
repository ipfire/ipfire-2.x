
#ifndef NETUTIL_H
#define NETUTIL_H 1

#include <stdlib.h>

#define LETTERS "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
#define NUMBERS "0123456789"
#define LETTERS_NUMBERS LETTERS NUMBERS
#define IP_NUMBERS "./" NUMBERS
#define PORT_NUMBERS ":-" NUMBERS
#define VALID_FQDN LETTERS_NUMBERS ".-"

#define VALID_IP(ip) (strlen(ip) > 6 \
		&& strlen(ip) < 16 \
		&& strspn(ip, NUMBERS ".") == strlen(ip))

#define VALID_IP_AND_MASK(ip) (strlen(ip) > 6 \
		&& strlen(ip) < 32 \
		&& strspn(ip, IP_NUMBERS) == strlen(ip))

#define VALID_PORT(port) (strlen(port) \
		&& strlen(port) < 6 \
		&& strspn(port, NUMBERS) == strlen(port))

#define VALID_PORT_RANGE(port) (strlen(port) \
		&& strlen(port) < 12 \
		&& strspn(port, PORT_NUMBERS) == strlen(port))

#define VALID_SHORT_MASK(ip) (strlen(ip) > 1 \
		&& strlen(ip) < 3 \
		&& strspn(ip, NUMBERS) == strlen(ip))

/* Can't find any info on valid characters/length hopefully these are
 * reasonable guesses */
#define VALID_DEVICE(dev) (strlen(dev) \
		&& strlen(dev) < 16 \
		&& strspn(dev, LETTERS_NUMBERS ":.") == strlen(dev))

/* Again, can't find any hard and fast rules for protocol names, these
 * restrictions are based on the keywords currently listed in
 * <http://www.iana.org/assignments/protocol-numbers>
 * though currently the ipcop cgis will only pass tcp, udp or gre anyway */
#define VALID_PROTOCOL(prot) (strlen(prot) \
		&&  strlen(prot) <16 \
		&&  strspn(prot, LETTERS_NUMBERS "-") == strlen(prot))

#endif
