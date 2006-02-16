/*
 * PCMCIA bridge device probe
 *
 * This file is part of the IPCop Firewall.
 *
 * IPCop is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * IPCop is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with IPCop; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
 *
 * The initial developer of the original code is David A. Hinds
 * <dahinds@users.sourceforge.net>.  Portions created by David A. Hinds
 * are Copyright (C) 1999 David A. Hinds.  All Rights Reserved.
 *
 * $Id: pcmcia.c,v 1.6.2.4 2005/12/08 02:12:28 franck78 Exp $
 *
 */

#include "install.h"
#include "pcmcia.h"

#ifdef __GLIBC__
#include <sys/io.h>
#else
#include <asm/io.h>
#endif

extern FILE *flog;
extern int modprobe(char *);

/*====================================================================*/

typedef struct {
    u_short	vendor, device;
    char	*modname;
    char	*name;
} pci_id_t;

pci_id_t pci_id[] = {
    { 0x1013, 0x1100, "i82365", "Cirrus Logic CL 6729" },
    { 0x1013, 0x1110, "yenta_socket", "Cirrus Logic PD 6832" },
    { 0x10b3, 0xb106, "yenta_socket", "SMC 34C90" },
    { 0x1180, 0x0465, "yenta_socket", "Ricoh RL5C465" },
    { 0x1180, 0x0466, "yenta_socket", "Ricoh RL5C466" },
    { 0x1180, 0x0475, "yenta_socket", "Ricoh RL5C475" },
    { 0x1180, 0x0476, "yenta_socket", "Ricoh RL5C476" },
    { 0x1180, 0x0477, "yenta_socket", "Ricoh RL5C477" },
    { 0x1180, 0x0478, "yenta_socket", "Ricoh RL5C478" },
    { 0x104c, 0xac12, "yenta_socket", "Texas Instruments PCI1130" }, 
    { 0x104c, 0xac13, "yenta_socket", "Texas Instruments PCI1031" }, 
    { 0x104c, 0xac15, "yenta_socket", "Texas Instruments PCI1131" }, 
    { 0x104c, 0xac1a, "yenta_socket", "Texas Instruments PCI1210" }, 
    { 0x104c, 0xac1e, "yenta_socket", "Texas Instruments PCI1211" }, 
    { 0x104c, 0xac17, "yenta_socket", "Texas Instruments PCI1220" }, 
    { 0x104c, 0xac19, "yenta_socket", "Texas Instruments PCI1221" }, 
    { 0x104c, 0xac1c, "yenta_socket", "Texas Instruments PCI1225" }, 
    { 0x104c, 0xac16, "yenta_socket", "Texas Instruments PCI1250" }, 
    { 0x104c, 0xac1d, "yenta_socket", "Texas Instruments PCI1251A" }, 
    { 0x104c, 0xac1f, "yenta_socket", "Texas Instruments PCI1251B" }, 
    { 0x104c, 0xac50, "yenta_socket", "Texas Instruments PCI1410" }, 
    { 0x104c, 0xac51, "yenta_socket", "Texas Instruments PCI1420" }, 
    { 0x104c, 0xac1b, "yenta_socket", "Texas Instruments PCI1450" }, 
    { 0x104c, 0xac52, "yenta_socket", "Texas Instruments PCI1451" }, 
    { 0x104c, 0xac56, "yenta_socket", "Texas Instruments PCI1510" }, 
    { 0x104c, 0xac55, "yenta_socket", "Texas Instruments PCI1520" }, 
    { 0x104c, 0xac54, "yenta_socket", "Texas Instruments PCI1620" }, 
    { 0x104c, 0xac41, "yenta_socket", "Texas Instruments PCI4410" }, 
    { 0x104c, 0xac40, "yenta_socket", "Texas Instruments PCI4450" }, 
    { 0x104c, 0xac42, "yenta_socket", "Texas Instruments PCI4451" }, 
    { 0x104c, 0xac44, "yenta_socket", "Texas Instruments PCI4510" }, 
    { 0x104c, 0xac46, "yenta_socket", "Texas Instruments PCI4520" }, 
    { 0x104c, 0xac49, "yenta_socket", "Texas Instruments PCI7410" }, 
    { 0x104c, 0xac47, "yenta_socket", "Texas Instruments PCI7510" }, 
    { 0x104c, 0xac48, "yenta_socket", "Texas Instruments PCI7610" }, 
    { 0x1217, 0x6729, "i82365", "O2 Micro 6729" }, 
    { 0x1217, 0x673a, "i82365", "O2 Micro 6730" }, 
    { 0x1217, 0x6832, "yenta_socket", "O2 Micro 6832/6833" }, 
    { 0x1217, 0x6836, "yenta_socket", "O2 Micro 6836/6860" }, 
    { 0x1217, 0x6872, "yenta_socket", "O2 Micro 6812" }, 
    { 0x1217, 0x6925, "yenta_socket", "O2 Micro 6922" }, 
    { 0x1217, 0x6933, "yenta_socket", "O2 Micro 6933" }, 
    { 0x1217, 0x6972, "yenta_socket", "O2 Micro 6912" }, 
    { 0x1179, 0x0603, "i82365", "Toshiba ToPIC95-A" }, 
    { 0x1179, 0x060a, "yenta_socket", "Toshiba ToPIC95-B" }, 
    { 0x1179, 0x060f, "yenta_socket", "Toshiba ToPIC97" }, 
    { 0x1179, 0x0617, "yenta_socket", "Toshiba ToPIC100" }, 
    { 0x119b, 0x1221, "i82365", "Omega Micro 82C092G" }, 
    { 0x8086, 0x1221, "i82092", "Intel 82092AA_0" }, 
    { 0x8086, 0x1222, "i82092", "Intel 82092AA_1" }, 
    { 0x1524, 0x1211, "yenta_socket", "ENE 1211" },
    { 0x1524, 0x1225, "yenta_socket", "ENE 1225" },
    { 0x1524, 0x1410, "yenta_socket", "ENE 1410" },
    { 0x1524, 0x1420, "yenta_socket", "ENE 1420" },
};
#define PCI_COUNT (sizeof(pci_id)/sizeof(pci_id_t))

static char * pci_probe()
{
    char s[256], *modname = NULL;
    u_int device, vendor, i;
    FILE *f;
    
    if ((f = fopen("/proc/bus/pci/devices", "r")) != NULL) {
	while (fgets(s, 256, f) != NULL) {
	    u_int n = strtoul(s+5, NULL, 16);
	    vendor = (n >> 16); device = (n & 0xffff);
	    for (i = 0; i < PCI_COUNT; i++)
		if ((vendor == pci_id[i].vendor) &&
		    (device == pci_id[i].device)) break;

	    if (i < PCI_COUNT) {
		modname = pci_id[i].modname;
		break;
	    }
	}
    }
    
    return modname;
}

/*====================================================================*/

#ifndef __alpha__
typedef u_short ioaddr_t;

static ioaddr_t i365_base = 0x03e0;

static u_char i365_get(u_short sock, u_short reg)
{
    u_char val = I365_REG(sock, reg);
    outb(val, i365_base); val = inb(i365_base+1);
    return val;
}

#if 0    // the following code do nothing usefull, it ends with return 0 anyway

static void i365_set(u_short sock, u_short reg, u_char data)
{
    u_char val = I365_REG(sock, reg);
    outb(val, i365_base); outb(data, i365_base+1);
}

static void i365_bset(u_short sock, u_short reg, u_char mask)
{
    u_char d = i365_get(sock, reg);
    d |= mask;
    i365_set(sock, reg, d);
}

static void i365_bclr(u_short sock, u_short reg, u_char mask)
{
    u_char d = i365_get(sock, reg);
    d &= ~mask;
    i365_set(sock, reg, d);
}
#endif

int i365_probe()
{
    int val, slot, sock, done;
//   char *name = "i82365sl";

    ioperm(i365_base, 4, 1);
    ioperm(0x80, 1, 1);
    for (slot = 0; slot < 2; slot++) {
	for (sock = done = 0; sock < 2; sock++) {
	    val = i365_get(sock, I365_IDENT);
	    switch (val) {
	    case 0x82:
//		name = "i82365sl A step";
//		break;
	    case 0x83:
//		name = "i82365sl B step";
//	    break;
	    case 0x84:
//		name = "VLSI 82C146";
//		break;
	    case 0x88: case 0x89: case 0x8a:
//		name = "IBM Clone";
//	    break;
	    case 0x8b: case 0x8c:
		break;
	    default:
		done = 1;
	    }
	    if (done) break;
	}
	if (done && sock) break;
	i365_base += 2;
    }

    if (sock == 0) {
	return -1;
    }

#if 0    // the following code do nothing usefull, it ends with return 0 anyway
    if ((sock == 2) && (strcmp(name, "VLSI 82C146") == 0))
	name = "i82365sl DF";

    /* Check for Vadem chips */
    outb(0x0e, i365_base);
    outb(0x37, i365_base);
    i365_bset(0, VG468_MISC, VG468_MISC_VADEMREV);
    val = i365_get(0, I365_IDENT);
    if (val & I365_IDENT_VADEM) {
	if ((val & 7) < 4)
	    name = "Vadem VG-468";
	else
	    name = "Vadem VG-469";
	i365_bclr(0, VG468_MISC, VG468_MISC_VADEMREV);
    }
    
    /* Check for Cirrus CL-PD67xx chips */
    i365_set(0, PD67_CHIP_INFO, 0);
    val = i365_get(0, PD67_CHIP_INFO);
    if ((val & PD67_INFO_CHIP_ID) == PD67_INFO_CHIP_ID) {
	val = i365_get(0, PD67_CHIP_INFO);
	if ((val & PD67_INFO_CHIP_ID) == 0) {
	    if (val & PD67_INFO_SLOTS)
		name = "Cirrus CL-PD672x";
	    else {
		name = "Cirrus CL-PD6710";
		sock = 1;
	    }
	    i365_set(0, PD67_EXT_INDEX, 0xe5);
	    if (i365_get(0, PD67_EXT_INDEX) != 0xe5)
		name = "VIA VT83C469";
	}
    }
#endif
    return 0;
    
} /* i365_probe */
#endif

/*====================================================================*/

#ifndef __alpha__
static u_short tcic_getw(ioaddr_t base, u_char reg)
{
    u_short val = inw(base+reg);
    return val;
}

static void tcic_setw(ioaddr_t base, u_char reg, u_short data)
{
    outw(data, base+reg);
}

int tcic_probe_at(ioaddr_t base)
{
    int i;
    u_short old;
    
    /* Anything there?? */
    for (i = 0; i < 0x10; i += 2)
	if (tcic_getw(base, i) == 0xffff)
	    return -1;

    /* Try to reset the chip */
    tcic_setw(base, TCIC_SCTRL, TCIC_SCTRL_RESET);
    tcic_setw(base, TCIC_SCTRL, 0);
    
    /* Can we set the addr register? */
    old = tcic_getw(base, TCIC_ADDR);
    tcic_setw(base, TCIC_ADDR, 0);
    if (tcic_getw(base, TCIC_ADDR) != 0) {
	tcic_setw(base, TCIC_ADDR, old);
	return -2;
    }
    
    tcic_setw(base, TCIC_ADDR, 0xc3a5);
    if (tcic_getw(base, TCIC_ADDR) != 0xc3a5)
	return -3;

    return 2;
}

int tcic_probe(ioaddr_t base)
{
    int sock;

    ioperm(base, 16, 1);
    ioperm(0x80, 1, 1);
    sock = tcic_probe_at(base);
    
    if (sock <= 0) {
	return -1;
    }

    return 0;
    
} /* tcic_probe */
#endif

/*====================================================================*/
char * initialize_pcmcia (void)
{
#ifndef __alpha__
    ioaddr_t tcic_base = TCIC_BASE;
#endif
    char* pcmcia;
    
    if ((pcmcia = pci_probe()))
	return pcmcia; /* we're all done */
#ifndef __alpha__
    else if (i365_probe() == 0)
	return "i82365";
    else if (tcic_probe(tcic_base) == 0)
	return "tcic";
#endif
    else {
    	/* Detect ISAPNP based i82365 controllers */
    	FILE *f;
        modprobe("i82365");
	if ((f = fopen("/proc/bus/pccard/00/info", "r"))) {
		fclose(f);
		return "i82365";
	}
    }

    return NULL;
}
