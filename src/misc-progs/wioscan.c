/*
 *	wioscan
 *
 *	This program is free software; you can redistribute it and/or
 *	modify it under the terms of the GNU General Public License
 *	version 2 as published by the Free Software Foundation.
 */

#define _GNU_SOURCE
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <poll.h>
#include <errno.h>
#include <err.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <netpacket/packet.h>
#include <net/ethernet.h>
#include <net/if.h>
#include <net/if_arp.h>
#include <netinet/ether.h>
#include <arpa/inet.h>
#include <stdint.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/mman.h>

#define _STR(S) #S
#define STR(S) _STR(S)

#define ARP htons(ETHERTYPE_ARP)
#define IP htons(ETHERTYPE_IP)

typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;

#include "list.h"
#define elemof(T) (sizeof T/sizeof*T)
#define endof(T) (T+elemof(T))
#ifndef offsetof
#define offsetof(T,M) ((int)(long)&((T*)0)->M)
#endif

#define HWMAX 8

union addr {
	struct sockaddr sa;
	struct sockaddr_in in;
	struct sockaddr_ll ll;
};

int sock; /* packet socket */
union addr bcast;

struct opts {
	unsigned sort:1;
	unsigned noown:1;
	unsigned noethn:1;
	unsigned proui:1;
	unsigned isrange:1;
	unsigned passive:1;
	unsigned nsend;
	unsigned wait;
} opts = {nsend:8, wait:250};

void print_oui(int sp, u8 a[6]);

struct he;
void print_he(struct he *he);

struct hwaddr {
	u8 len, addr[HWMAX];
};

static inline hw_eq(struct hwaddr *h, int hl, u8 *ha)
{
	return h->len == hl && memcmp(h->addr, ha, hl) == 0;
}

static inline void hw_set(struct hwaddr *h, int hl, u8 *ha)
{
	memcpy(h->addr, ha, (h->len = hl));
}

struct ifinfo {
	int index;
	char *name;
	u32 ip, net, mask, bcast;
	u16 hw_type;
	struct hwaddr hw;
} ifinfo;

static inline u32 ip_from_sa(struct sockaddr *sa)
{
	return ntohl(((struct sockaddr_in*)sa)->sin_addr.s_addr);
}

/* TABLE */

struct list hashtbl[128];
struct he {
	struct list hash;
	u32 ip;
	struct hwaddr hw;
	struct hwaddr from;
};

static void init_hash() __attribute__((constructor));
static void init_hash()
{
	int i;
	for(i=0;i<elemof(hashtbl);i++) list_init(&hashtbl[i]);
}

int he_for(u32 ip, struct he **ret, int alloc)
{
	struct list *h, *l;
	struct he *he;
	int v = 1;
	h = &hashtbl[ip & elemof(hashtbl)-1];
	for(l=h->next; l!=h; l=l->next) {
		he = list_entry(l, struct he, hash);
		if(he->ip == ip)
			goto ret;
		if(he->ip > ip)
			break;
	}
	v = 0;
	if(alloc) {
		he = (struct he*)malloc(sizeof *he);
		he->ip = ip;
		list_add(l->prev, &he->hash);
ret:
		if(ret) *ret = he;
	}
	return v;
}

/* INTERFACE */

static int net;

static void my__ioctl(int i, struct ifreq *r, char *t)
{
	if(ioctl(net, i, r) < 0)
		err(1, "ioctl(%s,%s)", t, r->ifr_name);
}
#define my_ioctl(I,R) my__ioctl(I,R,#I)

void fill_ifinfo(char *name)
{
	struct ifreq ir;
	int flags;

	ifinfo.index = if_nametoindex(name);
	if(!ifinfo.index) errx(1, "No such interface: %s", name);
	ifinfo.name = name;

	net = socket(PF_INET, SOCK_DGRAM, 0);
	if(net<0) err(1, "socket(PF_INET)");
	strcpy(ir.ifr_name, ifinfo.name);
	my_ioctl(SIOCGIFFLAGS, &ir);
	flags = ir.ifr_flags;
	if(flags & IFF_NOARP) errx(1, "%s: ARP not supported.", name);
	my_ioctl(SIOCGIFADDR, &ir);
	ifinfo.ip = ip_from_sa(&ir.ifr_addr);
	if(flags & IFF_POINTOPOINT) {
		my_ioctl(SIOCGIFDSTADDR, &ir);
		ifinfo.net = ip_from_sa(&ir.ifr_dstaddr);
		ifinfo.mask = (u32)~0;
		ifinfo.bcast = 0; /* none */
	} else {
		my_ioctl(SIOCGIFNETMASK, &ir);
		ifinfo.mask = ip_from_sa(&ir.ifr_netmask);
		my_ioctl(SIOCGIFBRDADDR, &ir);
		ifinfo.bcast = ip_from_sa(&ir.ifr_broadaddr);
		ifinfo.net = ifinfo.ip & ifinfo.mask;
	}
	close(net);
}

static inline char *str_ip(u32 ip)
{
	struct in_addr n;
	n.s_addr = htonl(ip);
	return inet_ntoa(n);
}

char *str_hw(u8 *a, int l)
{
	static char buf[3*HWMAX];
	char *d = buf;
	if(!l) return "*";
	if(l>HWMAX) l=HWMAX;
	for(;;) {
		d += sprintf(d, "%02X", *a++);
		if(--l <= 0) break;
		*d++ = ':';
	}
	*d = 0;
	return buf;
}

static char *str_addr(union addr *addr)
{
	switch(addr->sa.sa_family) {
		case AF_INET: return inet_ntoa(addr->in.sin_addr);
		case AF_PACKET: return str_hw(addr->ll.sll_addr, addr->ll.sll_halen);
		default: return "???";
	}
}

static inline void setup_socket()
{
	union addr addr;
	socklen_t l;

	sock = socket(PF_PACKET, SOCK_DGRAM, 0);
	if(sock < 0) err(1, "socket(PF_PACKET)");

	memset(&addr.ll, 0, sizeof addr.ll);
	addr.sa.sa_family = AF_PACKET;
	addr.ll.sll_protocol = ARP;
	addr.ll.sll_ifindex = ifinfo.index;

	if(bind(sock, &addr.sa, sizeof addr.ll)<0)
		err(1, "bind");
	l = sizeof addr.ll;
	if(getsockname(sock, &addr.sa, &l)<0)
		err(1, "getsockname");

	if(addr.ll.sll_halen > HWMAX)
		errx(1, "hardware address too long (%d)", addr.ll.sll_halen);
	ifinfo.hw.len = addr.ll.sll_halen;
	memcpy(ifinfo.hw.addr, addr.ll.sll_addr, sizeof ifinfo.hw.addr);
	ifinfo.hw_type = addr.ll.sll_hatype;
}

/* SCAN */

struct arppkt {
	u16 hrd, pro;
	u8 hln, pln;
	u16 op;
	u8 a[2*HWMAX+2*4];
/*	u8 sha[6];
	u8 sip[4];
	u8 tha[6];
	u8 tip[4];*/
};

static inline u8 *get_sha(struct arppkt *pkt) {return pkt->a;}
static inline u8 *get_tha(struct arppkt *pkt) {return pkt->a+pkt->hln+4;}
static inline u32 get_sip(struct arppkt *pkt) {return ntohl(*(u32*)(pkt->a+pkt->hln));}
static inline u32 get_tip(struct arppkt *pkt) {return ntohl(*(u32*)(pkt->a+2*pkt->hln+4));}

#if 0
void print_arp(struct arppkt *arp)
{
	u8 *p = arp->a;
	printf("hrd:%04X pro:%04X ", ntohs(arp->hrd), ntohs(arp->pro));
	printf("hln:%d pln:%d op:%d ", arp->hln, arp->pln, ntohs(arp->op));
	printf("sha:%s ", str_hw(p, arp->hln)); p+=arp->hln;
	printf("sip:%s ", str_ip(ntohl(*(u32*)p))); p+=arp->pln;
	printf("tha:%s ", str_hw(p, arp->hln)); p+=arp->hln;
	printf("tip:%s\n", str_ip(ntohl(*(u32*)p)));
}
#endif

static struct scan {
	u32 ip, start, end;
} scan;

#define IN_RANGE(I) ((I) >= scan.start && (I) <= (u32)(scan.end-1))

int sendscan()
{
	struct arppkt arp;
	int ns;
	u8 *p;

	arp.hrd = htons(ifinfo.hw_type);
	arp.pro = IP;
	arp.hln = ifinfo.hw.len;
	arp.pln = 4;
	arp.op = htons(1);
	p = arp.a;
	memcpy(p, ifinfo.hw.addr, ifinfo.hw.len); p += ifinfo.hw.len;
	*(u32*)p = htonl(ifinfo.ip); p += 4;
	memset(p, 0, ifinfo.hw.len); p += ifinfo.hw.len;

	ns = 0;
	while(scan.ip != scan.end) {
		int v;
		if(scan.ip == ifinfo.bcast || he_for(scan.ip, 0, 0)) {
			scan.ip++;
			continue;
		}
		*(u32*)p = htonl(scan.ip);
		v = sendto(sock, &arp, p+4-(u8*)&arp, 0, &bcast.sa, sizeof bcast.ll);
		if(v<0) {
			if(errno != ENOBUFS || opts.nsend <= 1)
				err(1, "send(%s)", str_addr(&bcast));
			opts.nsend--;
			return -1;
		}
		scan.ip++;
		if(++ns >= opts.nsend) break;
	}
	return ns;
}

void compare_resp(struct he *he, union addr *src, int hln, u8 *sha)
{
	if(hw_eq(&he->hw, hln, sha)
	 && hw_eq(&he->from, src->ll.sll_halen, src->ll.sll_addr))
	 	return;

	fprintf(stderr, "%s: ", str_ip(he->ip));
	fprintf(stderr, "inconsistency: %s", str_hw(sha, hln));
	if(src->ll.sll_halen != hln || memcmp(src->ll.sll_addr, sha, hln))
		fprintf(stderr, " from %s",
		 str_hw(src->ll.sll_addr, src->ll.sll_halen));
	fprintf(stderr, ", was %s\n", str_hw(he->hw.addr, he->hw.len));
	if(!hw_eq(&he->hw, he->from.len, he->from.addr))
		fprintf(stderr, " from %s",
		 str_hw(he->from.addr, he->from.len));
}

int arp_recv(struct arppkt *pkt, union addr *src)
{
	socklen_t l = sizeof *src;
	int v = recvfrom(sock, pkt, sizeof *pkt, 0, &src->sa, &l);
	if(v < 0) err(1, "recvfrom");
	if(v < offsetof(struct arppkt, a))
		return 0;
	if(pkt->pro != IP)
		return 0;
	if(pkt->hrd != htons(ifinfo.hw_type) || pkt->hln != ifinfo.hw.len)
		return 0;
	if(v < offsetof(struct arppkt, a) + 2*pkt->hln + 2*4)
		return 0;
	return 1;
}

void receive()
{
	union addr addr;
	struct arppkt arp;
	struct he *he;
	u32 ip;

	if(!arp_recv(&arp, &addr))
		return;
	if(arp.op != htons(2)) /* only responses */
		return;

	ip = get_sip(&arp);

	if(!he_for(ip, &he, 1)) {
		hw_set(&he->hw, arp.hln, get_sha(&arp));
		hw_set(&he->from, addr.ll.sll_halen, addr.ll.sll_addr);
		if(opts.sort) return;
		if(opts.isrange && !IN_RANGE(ip)) return;
		print_he(he);
	} else
		compare_resp(he, &addr, arp.hln, get_sha(&arp));
}

/**/

void passive()
{
	for(;;) {
		struct arppkt arp;
		union addr src;
		if(!arp_recv(&arp, &src))
			continue;
		printf("%s: ", str_addr(&src));
		printf("%s %-15s ", str_hw(get_sha(&arp),arp.hln),
			str_ip(get_sip(&arp)));
		switch(htons(arp.op)) {
			case 1:
				printf("Q %s", str_ip(get_tip(&arp)));
				break;
			case 2:
				printf("A %s %s", str_hw(get_tha(&arp),arp.hln),
					str_ip(get_tip(&arp)));
				break;
			default:
				printf("%X", htons(arp.op));
		}
		putchar('\n');
	}
}

/**/

int waitsock(int n)
{
	int v;
	struct pollfd pollfd;
	pollfd.fd = sock;
	pollfd.events = POLLIN;
	v = poll(&pollfd, 1, n);
	if(v < 0) {
		if(errno != EINTR)
			err(1, "poll");
		v = 0;
	}
	return v;
}

void print_he(struct he *he)
{
	int l, w;
	if(opts.noown && he->ip == ifinfo.ip)
		return;
	printf("%s,", str_hw(he->hw.addr, he->hw.len));
	l = 15 - printf("%s", str_ip(he->ip));
	w = 0;
	if(!opts.proui && !hw_eq(&he->from, he->hw.len, he->hw.addr))
		w = 1, l = 1;

	if(opts.proui)
		print_oui(l, he->hw.addr);
	else if(!opts.noethn) {
#if !defined __dietlibc_ && !defined __UCLIBC__
		char nm[1024];
		if(!ether_ntohost(nm, (struct ether_addr*)he->hw.addr))
			printf("%*s%s", l, "", nm);
#endif
	}
	if(w)
		printf(" from %s", str_hw(he->from.addr, he->from.len));
	putchar('\n');
}

static int parse_iprange(char *p)
{
	char *e;
	u32 ip=0;
	int sh;

	for(sh = 24;; sh -= 8) {
		unsigned long v;

		v = strtoul(p, &e, 10);
		if(p == e || v > 255)
			return 0;

		ip |= v << sh;

		p = e + 1;
		if(*e == '/') {
			v = strtoul(p, &e, 10);
			if(p == e || *e || v > 32)
				return 0;
			if(v) {
				v = 32 - v;
				if(sh > v)
					return 0;
mask:
				v = ~0 << v;
			}
			scan.start = ip & v;
			scan.end = scan.start - v;
			return 1;
		}

		if(!sh) break;

		v = sh;
		if(!*e)
			goto mask;

		if(*e != '.')
			return 0;

		if(!*p || *p == '*' && !p[1])
			goto mask;
	}

	scan.start = ip;
	scan.end = ip + 1;

	if(*e == '-') {
		u32 end = 0, m = ~0;

		do {
			unsigned long v = strtoul(p, &e, 10);
			if(p == e || v > 255)
				return 0;
			p = e + 1;
			end = end<<8 | v;
			m <<= 8;
		} while(m && *e);

		if(*e)
			return 0;

		end |= ip & m;
		if(end < ip)
			return 0;

		scan.end = end + 1;
		return 1;
	}
	return *e == 0;
}

int main(int argc, char **argv)
{
	for(;;) switch(getopt(argc, argv, "fsaepwlh")) {
		case 'f': opts.sort=0; break;
		case 's': opts.sort=1; break;
		case 'a': opts.noown=1; break;
		case 'e': opts.noethn=1; break;
		case 'p': opts.proui=1; break;
		case 'w': opts.nsend=2; opts.wait=1000; break;
		case 'l': opts.passive=1; break;
		case 'h':
			printf(
			"wioscan [-faep] [interface] [ip-range]\n"
			"\t-s  sort responses\n"
			"\t-a  do not list interface's own address\n"
#if !defined __dietlibc_ && !defined __UCLIBC__
			"\t-e  do not include info from /etc/ethers\n"
#endif
			"\t-p  print vendor names\n"
			"\t-w  slow operation\n"
			"\t-l  listen only (not promiscuous)\n"
			"ip-range: ip ip/bits ip-ip\n"
			);
			return 0;
		case EOF:
			goto endopt;
	}
endopt:

	{
		char *dev = "eth0";
		if(optind<argc && (*argv[optind] < '0' || *argv[optind] > '9'))
			dev = argv[optind++];
		fill_ifinfo(dev);
		setup_socket();
	}

	if(optind>=argc) {
		scan.start = ifinfo.net;
		scan.end = (ifinfo.net | ~ifinfo.mask) + 1;
	} else {
		if(!parse_iprange(argv[optind]))
			errx(1, "%s: bad IP range", argv[optind]);
		opts.isrange = 1;
	}

	if(ifinfo.hw_type != ARPHRD_ETHER)
		opts.proui = 0, opts.noethn = 1;

	if(opts.passive)
		passive();

	/* hw broadcast address is Linux's secret, this works with Ethernet */
	bcast.sa.sa_family = AF_PACKET;
	bcast.ll.sll_protocol = ARP;
	bcast.ll.sll_ifindex = ifinfo.index;
	bcast.ll.sll_hatype = ifinfo.hw_type;
	bcast.ll.sll_pkttype = PACKET_BROADCAST; /* unused :-( */
	bcast.ll.sll_halen = ifinfo.hw.len;
	memset(bcast.ll.sll_addr, 0xFF, ifinfo.hw.len);

	if(IN_RANGE(ifinfo.ip)) {
		/* XXX we should add all our arpable addresses on the interface */
		struct he *he;
		he_for(ifinfo.ip, &he, 1);
		hw_set(&he->hw, ifinfo.hw.len, ifinfo.hw.addr);
		hw_set(&he->from, ifinfo.hw.len, ifinfo.hw.addr);
		if(!opts.sort)
			print_he(he);
	}

	/* 1st scan */
	scan.ip = scan.start;
	while(sendscan()) {
		while(waitsock(10))
			receive();
	}
	/* 2nd scan */
	scan.ip = scan.start;
	while(sendscan()) {
		while(waitsock(10))
			receive();
	}
	while(waitsock(opts.wait))
		receive();

	if(opts.sort) for(scan.ip = ifinfo.net; scan.ip != scan.end; scan.ip++) {
		struct he *he;
		if(he_for(scan.ip, &he, 0))
			print_he(he);
	}
	return 0;
}


typedef uint8_t u8;
static int fd = -2;
static char *ouiptr, *ouiend;

static void open_oui()
{
	struct stat st;
	fd = open("oui", O_RDONLY);
	if(fd < 0) {
		fd = open(STR(OUI), O_RDONLY);
		if(fd < 0) goto err;
	}
	if(fstat(fd, &st) < 0 || st.st_size == 0) goto err_cl;
	ouiptr = mmap(0, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
	ouiend = ouiptr + st.st_size;
	if(ouiptr == MAP_FAILED) {
err_cl:
		close(fd); fd=-1;
err:
		warnx("Can't open OUI database");
		return;
	}
#ifdef MADV_SEQUENTIAL
	madvise(ouiptr, st.st_size, MADV_SEQUENTIAL);
#endif
}

void print_oui(int sp, u8 a[6])
{
	char addr[7], *p, *q;
	if(fd < 0) {
		if(fd == -2)
			open_oui();
		if(fd < 0)
			return;
	}
	sprintf(addr, "%02X%02X%02X", a[0], a[1], a[2]);

	for(p=ouiptr; p<ouiend; p=q+1) {
		q = memchr(p, '\n', ouiend-p);
		if(!q) q=ouiend;
		if(q-p < 8 || memcmp(p, addr, 6))
			continue;

		p += 7;
print:
		printf("%*s%.*s", sp, "", (int)(q-p), p);
		return;
	}
	if(a[0]==0 && a[1]==0xFF) {
		p = "(generated)";
		q = p + 11;
		goto print;
	}
}