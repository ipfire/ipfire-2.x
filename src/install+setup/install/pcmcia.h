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
 * $Id: pcmcia.h,v 1.1 2004/01/25 09:34:59 riddles Exp $
 *
 */

#define TCIC_BASE		0x240

/* offsets of registers from TCIC_BASE */
#define TCIC_DATA		0x00
#define TCIC_ADDR		0x02
#define TCIC_SCTRL		0x06
#define TCIC_SSTAT		0x07
#define TCIC_MODE		0x08
#define TCIC_PWR		0x09
#define TCIC_EDC		0x0A
#define TCIC_ICSR		0x0C
#define TCIC_IENA		0x0D
#define TCIC_AUX		0x0E

#define TCIC_SS_SHFT		12
#define TCIC_SS_MASK		0x7000

/* Flags for TCIC_ADDR */
#define TCIC_ADR2_REG		0x8000
#define TCIC_ADR2_INDREG	0x0800

#define TCIC_ADDR_REG		0x80000000
#define TCIC_ADDR_SS_SHFT	(TCIC_SS_SHFT+16)
#define TCIC_ADDR_SS_MASK	(TCIC_SS_MASK<<16)
#define TCIC_ADDR_INDREG	0x08000000
#define TCIC_ADDR_IO		0x04000000
#define TCIC_ADDR_MASK		0x03ffffff

/* Flags for TCIC_SCTRL */
#define TCIC_SCTRL_ENA		0x01
#define TCIC_SCTRL_INCMODE	0x18
#define TCIC_SCTRL_INCMODE_HOLD	0x00
#define TCIC_SCTRL_INCMODE_WORD	0x08
#define TCIC_SCTRL_INCMODE_REG	0x10
#define TCIC_SCTRL_INCMODE_AUTO	0x18
#define TCIC_SCTRL_EDCSUM	0x20
#define TCIC_SCTRL_RESET	0x80

/* Flags for TCIC_SSTAT */
#define TCIC_SSTAT_6US		0x01
#define TCIC_SSTAT_10US		0x02
#define TCIC_SSTAT_PROGTIME	0x04
#define TCIC_SSTAT_LBAT1	0x08
#define TCIC_SSTAT_LBAT2	0x10
#define TCIC_SSTAT_RDY		0x20	/* Inverted */
#define TCIC_SSTAT_WP		0x40
#define TCIC_SSTAT_CD		0x80	/* Card detect */

/* Flags for TCIC_MODE */
#define TCIC_MODE_PGMMASK	0x1f
#define TCIC_MODE_NORMAL	0x00
#define TCIC_MODE_PGMWR		0x01
#define TCIC_MODE_PGMRD		0x02
#define TCIC_MODE_PGMCE		0x04
#define TCIC_MODE_PGMDBW	0x08
#define TCIC_MODE_PGMWORD	0x10
#define TCIC_MODE_AUXSEL_MASK	0xe0

/* Registers accessed through TCIC_AUX, by setting TCIC_MODE */
#define TCIC_AUX_TCTL		(0<<5)
#define TCIC_AUX_PCTL		(1<<5)
#define TCIC_AUX_WCTL		(2<<5)
#define TCIC_AUX_EXTERN		(3<<5)
#define TCIC_AUX_PDATA		(4<<5)
#define TCIC_AUX_SYSCFG		(5<<5)
#define TCIC_AUX_ILOCK		(6<<5)
#define TCIC_AUX_TEST		(7<<5)

/* Flags for TCIC_PWR */
#define TCIC_PWR_VCC(sock)	(0x01<<(sock))
#define TCIC_PWR_VCC_MASK	0x03
#define TCIC_PWR_VPP(sock)	(0x08<<(sock))
#define TCIC_PWR_VPP_MASK	0x18
#define TCIC_PWR_CLIMENA	0x40
#define TCIC_PWR_CLIMSTAT	0x80

/* Flags for TCIC_ICSR */
#define TCIC_ICSR_CLEAR		0x01
#define TCIC_ICSR_SET		0x02
#define TCIC_ICSR_JAM		(TCIC_ICSR_CLEAR|TCIC_ICSR_SET)
#define TCIC_ICSR_STOPCPU	0x04
#define TCIC_ICSR_ILOCK		0x08
#define TCIC_ICSR_PROGTIME	0x10
#define TCIC_ICSR_ERR		0x20
#define TCIC_ICSR_CDCHG		0x40
#define TCIC_ICSR_IOCHK		0x80

/* Flags for TCIC_IENA */
#define TCIC_IENA_CFG_MASK	0x03
#define TCIC_IENA_CFG_OFF	0x00	/* disabled */
#define TCIC_IENA_CFG_OD	0x01	/* active low, open drain */
#define TCIC_IENA_CFG_LOW	0x02	/* active low, totem pole */
#define TCIC_IENA_CFG_HIGH	0x03	/* active high, totem pole */
#define TCIC_IENA_ILOCK		0x08
#define TCIC_IENA_PROGTIME	0x10
#define TCIC_IENA_ERR		0x20	/* overcurrent or iochk */
#define TCIC_IENA_CDCHG		0x40

/* Flags for TCIC_AUX_WCTL */
#define TCIC_WAIT_COUNT_MASK	0x001f
#define TCIC_WAIT_ASYNC		0x0020
#define TCIC_WAIT_SENSE		0x0040
#define TCIC_WAIT_SRC		0x0080
#define TCIC_WCTL_WR		0x0100
#define TCIC_WCTL_RD		0x0200
#define TCIC_WCTL_CE		0x0400
#define TCIC_WCTL_LLBAT1	0x0800
#define TCIC_WCTL_LLBAT2	0x1000
#define TCIC_WCTL_LRDY		0x2000
#define TCIC_WCTL_LWP		0x4000
#define TCIC_WCTL_LCD		0x8000

/* Flags for TCIC_AUX_SYSCFG */
#define TCIC_SYSCFG_IRQ_MASK	0x000f
#define TCIC_SYSCFG_MCSFULL	0x0010
#define TCIC_SYSCFG_IO1723	0x0020
#define TCIC_SYSCFG_MCSXB	0x0040
#define TCIC_SYSCFG_ICSXB	0x0080
#define TCIC_SYSCFG_NOPDN	0x0100
#define TCIC_SYSCFG_MPSEL_SHFT	9
#define TCIC_SYSCFG_MPSEL_MASK	0x0e00
#define TCIC_SYSCFG_MPSENSE	0x2000
#define TCIC_SYSCFG_AUTOBUSY	0x4000
#define TCIC_SYSCFG_ACC		0x8000

#define TCIC_ILOCK_OUT		0x01
#define TCIC_ILOCK_SENSE	0x02
#define TCIC_ILOCK_CRESET	0x04
#define TCIC_ILOCK_CRESENA	0x08
#define TCIC_ILOCK_CWAIT	0x10
#define TCIC_ILOCK_CWAITSNS	0x20
#define TCIC_ILOCK_HOLD_MASK	0xc0
#define TCIC_ILOCK_HOLD_CCLK	0xc0

#define TCIC_ILOCKTEST_ID_SH	8
#define TCIC_ILOCKTEST_ID_MASK	0x7f00
#define TCIC_ILOCKTEST_MCIC_1	0x8000

#define TCIC_ID_DB86082		0x02
#define TCIC_ID_DB86082A	0x03
#define TCIC_ID_DB86084		0x04
#define TCIC_ID_DB86084A	0x08
#define TCIC_ID_DB86072		0x15
#define TCIC_ID_DB86184		0x14
#define TCIC_ID_DB86082B	0x17

#define TCIC_TEST_DIAG		0x8000

/*
 * Indirectly addressed registers
 */

#define TCIC_SCF1(sock)	((sock)<<3)
#define TCIC_SCF2(sock) (((sock)<<3)+2)

/* Flags for SCF1 */
#define TCIC_SCF1_IRQ_MASK	0x000f
#define TCIC_SCF1_IRQ_OFF	0x0000
#define TCIC_SCF1_IRQOC		0x0010
#define TCIC_SCF1_PCVT		0x0020
#define TCIC_SCF1_IRDY		0x0040
#define TCIC_SCF1_ATA		0x0080
#define TCIC_SCF1_DMA_SHIFT	8
#define TCIC_SCF1_DMA_MASK	0x0700
#define TCIC_SCF1_DMA_OFF	0
#define TCIC_SCF1_DREQ2		2
#define TCIC_SCF1_IOSTS		0x0800
#define TCIC_SCF1_SPKR		0x1000
#define TCIC_SCF1_FINPACK	0x2000
#define TCIC_SCF1_DELWR		0x4000
#define TCIC_SCF1_HD7IDE	0x8000

/* Flags for SCF2 */
#define TCIC_SCF2_RI		0x0001
#define TCIC_SCF2_IDBR		0x0002
#define TCIC_SCF2_MDBR		0x0004
#define TCIC_SCF2_MLBAT1	0x0008
#define TCIC_SCF2_MLBAT2	0x0010
#define TCIC_SCF2_MRDY		0x0020
#define TCIC_SCF2_MWP		0x0040
#define TCIC_SCF2_MCD		0x0080
#define TCIC_SCF2_MALL		0x00f8

/* Indirect addresses for memory window registers */
#define TCIC_MWIN(sock,map)	(0x100+(((map)+((sock)<<2))<<3))
#define TCIC_MBASE_X		2
#define TCIC_MMAP_X		4
#define TCIC_MCTL_X		6

#define TCIC_MBASE_4K_BIT	0x4000
#define TCIC_MBASE_HA_SHFT	12
#define TCIC_MBASE_HA_MASK	0x0fff

#define TCIC_MMAP_REG		0x8000
#define TCIC_MMAP_CA_SHFT	12
#define TCIC_MMAP_CA_MASK	0x3fff

#define TCIC_MCTL_WSCNT_MASK	0x001f
#define TCIC_MCTL_WCLK		0x0020
#define TCIC_MCTL_WCLK_CCLK	0x0000
#define TCIC_MCTL_WCLK_BCLK	0x0020
#define TCIC_MCTL_QUIET		0x0040
#define TCIC_MCTL_WP		0x0080
#define TCIC_MCTL_ACC		0x0100
#define TCIC_MCTL_KE		0x0200
#define TCIC_MCTL_EDC		0x0400
#define TCIC_MCTL_B8		0x0800
#define TCIC_MCTL_SS_SHFT	TCIC_SS_SHFT
#define TCIC_MCTL_SS_MASK	TCIC_SS_MASK
#define TCIC_MCTL_ENA		0x8000

/* Indirect addresses for I/O window registers */
#define TCIC_IWIN(sock,map)	(0x200+(((map)+((sock)<<1))<<2))
#define TCIC_IBASE_X		0
#define TCIC_ICTL_X		2

#define TCIC_ICTL_WSCNT_MASK	TCIC_MCTL_WSCNT_MASK
#define TCIC_ICTL_QUIET		TCIC_MCTL_QUIET
#define TCIC_ICTL_1K		0x0080
#define TCIC_ICTL_PASS16	0x0100
#define TCIC_ICTL_ACC		TCIC_MCTL_ACC
#define TCIC_ICTL_TINY		0x0200
#define TCIC_ICTL_B16		0x0400
#define TCIC_ICTL_B8		TCIC_MCTL_B8
#define TCIC_ICTL_BW_MASK	(TCIC_ICTL_B16|TCIC_ICTL_B8)
#define TCIC_ICTL_BW_DYN	0
#define TCIC_ICTL_BW_8		TCIC_ICTL_B8
#define TCIC_ICTL_BW_16		TCIC_ICTL_B16
#define TCIC_ICTL_BW_ATA	(TCIC_ICTL_B16|TCIC_ICTL_B8)
#define TCIC_ICTL_SS_SHFT	TCIC_SS_SHFT
#define TCIC_ICTL_SS_MASK	TCIC_SS_MASK
#define TCIC_ICTL_ENA		TCIC_MCTL_ENA

/* register definitions for the Intel 82365SL PCMCIA controller */

/* Offsets for PCIC registers */
#define I365_IDENT	0x00	/* Identification and revision */
#define I365_STATUS	0x01	/* Interface status */
#define I365_POWER	0x02	/* Power and RESETDRV control */
#define I365_INTCTL	0x03	/* Interrupt and general control */
#define I365_CSC	0x04	/* Card status change */
#define I365_CSCINT	0x05	/* Card status change interrupt control */
#define I365_ADDRWIN	0x06	/* Address window enable */
#define I365_IOCTL	0x07	/* I/O control */
#define I365_GENCTL	0x16	/* Card detect and general control */
#define I365_GBLCTL	0x1E	/* Global control register */

/* Offsets for I/O and memory window registers */
#define I365_IO(map)	(0x08+((map)<<2))
#define I365_MEM(map)	(0x10+((map)<<3))
#define I365_W_START	0
#define I365_W_STOP	2
#define I365_W_OFF	4

/* Flags for I365_STATUS */
#define I365_CS_BVD1	0x01
#define I365_CS_STSCHG	0x01
#define I365_CS_BVD2	0x02
#define I365_CS_SPKR	0x02
#define I365_CS_DETECT	0x0C
#define I365_CS_WRPROT	0x10
#define I365_CS_READY	0x20	/* Inverted */
#define I365_CS_POWERON	0x40
#define I365_CS_GPI	0x80

/* Flags for I365_POWER */
#define I365_PWR_OFF	0x00	/* Turn off the socket */
#define I365_PWR_OUT	0x80	/* Output enable */
#define I365_PWR_NORESET 0x40	/* Disable RESETDRV on resume */
#define I365_PWR_AUTO	0x20	/* Auto pwr switch enable */
#define I365_VCC_MASK	0x18	/* Mask for turning off Vcc */
/* There are different layouts for B-step and DF-step chips: the B
   step has independent Vpp1/Vpp2 control, and the DF step has only
   Vpp1 control, plus 3V control */
#define I365_VCC_5V	0x10	/* Vcc = 5.0v */
#define I365_VCC_3V	0x18	/* Vcc = 3.3v */
#define I365_VPP2_MASK	0x0c	/* Mask for turning off Vpp2 */
#define I365_VPP2_5V	0x04	/* Vpp2 = 5.0v */
#define I365_VPP2_12V	0x08	/* Vpp2 = 12.0v */
#define I365_VPP1_MASK	0x03	/* Mask for turning off Vpp1 */
#define I365_VPP1_5V	0x01	/* Vpp2 = 5.0v */
#define I365_VPP1_12V	0x02	/* Vpp2 = 12.0v */

/* Flags for I365_INTCTL */
#define I365_RING_ENA	0x80
#define I365_PC_RESET	0x40
#define I365_PC_IOCARD	0x20
#define I365_INTR_ENA	0x10
#define I365_IRQ_MASK	0x0F

/* Flags for I365_CSC and I365_CSCINT*/
#define I365_CSC_BVD1	0x01
#define I365_CSC_STSCHG	0x01
#define I365_CSC_BVD2	0x02
#define I365_CSC_READY	0x04
#define I365_CSC_DETECT	0x08
#define I365_CSC_ANY	0x0F
#define I365_CSC_GPI	0x10

/* Flags for I365_ADDRWIN */
#define I365_ADDR_MEMCS16	0x20
#define I365_ENA_IO(map)	(0x40 << (map))
#define I365_ENA_MEM(map)	(0x01 << (map))

/* Flags for I365_IOCTL */
#define I365_IOCTL_MASK(map)	(0x0F << (map<<2))
#define I365_IOCTL_WAIT(map)	(0x08 << (map<<2))
#define I365_IOCTL_0WS(map)	(0x04 << (map<<2))
#define I365_IOCTL_IOCS16(map)	(0x02 << (map<<2))
#define I365_IOCTL_16BIT(map)	(0x01 << (map<<2))

/* Flags for I365_GENCTL */
#define I365_CTL_16DELAY	0x01
#define I365_CTL_RESET		0x02
#define I365_CTL_GPI_ENA	0x04
#define I365_CTL_GPI_CTL	0x08
#define I365_CTL_RESUME		0x10
#define I365_CTL_SW_IRQ		0x20

/* Flags for I365_GBLCTL */
#define I365_GBL_PWRDOWN	0x01
#define I365_GBL_CSC_LEV	0x02
#define I365_GBL_WRBACK		0x04
#define I365_GBL_IRQ_0_LEV	0x08
#define I365_GBL_IRQ_1_LEV	0x10

/* Flags for memory window registers */
#define I365_MEM_16BIT	0x8000	/* In memory start high byte */
#define I365_MEM_0WS	0x4000
#define I365_MEM_WS1	0x8000	/* In memory stop high byte */
#define I365_MEM_WS0	0x4000
#define I365_MEM_WRPROT	0x8000	/* In offset high byte */
#define I365_MEM_REG	0x4000

#define I365_REG(slot, reg)	(((slot) << 6) | (reg))

/* Default ISA interrupt mask */
#define I365_ISA_IRQ_MASK	0xdeb8	/* irq's 3-5,7,9-12,14,15 */

/* Device ID's for PCI-to-PCMCIA bridges */

#ifndef PCI_VENDOR_ID_INTEL
#define PCI_VENDOR_ID_INTEL		0x8086
#endif
#ifndef PCI_DEVICE_ID_INTEL_82092AA_0
#define PCI_DEVICE_ID_INTEL_82092AA_0	0x1221
#endif
#ifndef PCI_VENDOR_ID_OMEGA
#define PCI_VENDOR_ID_OMEGA		0x119b
#endif
#ifndef PCI_DEVICE_ID_OMEGA_82C092G
#define PCI_DEVICE_ID_OMEGA_82C092G	0x1221
#endif

#ifndef PCI_VENDOR_ID_CIRRUS
#define PCI_VENDOR_ID_CIRRUS		0x1013
#endif
#ifndef PCI_DEVICE_ID_CIRRUS_6729
#define PCI_DEVICE_ID_CIRRUS_6729	0x1100
#endif
#ifndef PCI_DEVICE_ID_CIRRUS_6832
#define PCI_DEVICE_ID_CIRRUS_6832	0x1110
#endif

#define PD67_MISC_CTL_1		0x16	/* Misc control 1 */
#define PD67_FIFO_CTL		0x17	/* FIFO control */
#define PD67_MISC_CTL_2		0x1E	/* Misc control 2 */
#define PD67_CHIP_INFO		0x1f	/* Chip information */
#define PD67_ATA_CTL		0x026	/* 6730: ATA control */
#define PD67_EXT_INDEX		0x2e	/* Extension index */
#define PD67_EXT_DATA		0x2f	/* Extension data */

#define pd67_ext_get(s, r) \
    (i365_set(s, PD67_EXT_INDEX, r), i365_get(s, PD67_EXT_DATA))
#define pd67_ext_set(s, r, v) \
    (i365_set(s, PD67_EXT_INDEX, r), i365_set(s, PD67_EXT_DATA, v))

/* PD6722 extension registers -- indexed in PD67_EXT_INDEX */
#define PD67_DATA_MASK0		0x01	/* Data mask 0 */
#define PD67_DATA_MASK1		0x02	/* Data mask 1 */
#define PD67_DMA_CTL		0x03	/* DMA control */

/* PD6730 extension registers -- indexed in PD67_EXT_INDEX */
#define PD67_EXT_CTL_1		0x03	/* Extension control 1 */
#define PD67_MEM_PAGE(n)	((n)+5)	/* PCI window bits 31:24 */
#define PD67_EXTERN_DATA	0x0a
#define PD67_EXT_CTL_2		0x0b
#define PD67_MISC_CTL_3		0x25
#define PD67_SMB_PWR_CTL	0x26

/* I/O window address offset */
#define PD67_IO_OFF(w)		(0x36+((w)<<1))

/* Timing register sets */
#define PD67_TIME_SETUP(n)	(0x3a + 3*(n))
#define PD67_TIME_CMD(n)	(0x3b + 3*(n))
#define PD67_TIME_RECOV(n)	(0x3c + 3*(n))

/* Flags for PD67_MISC_CTL_1 */
#define PD67_MC1_5V_DET		0x01	/* 5v detect */
#define PD67_MC1_MEDIA_ENA	0x01	/* 6730: Multimedia enable */
#define PD67_MC1_VCC_3V		0x02	/* 3.3v Vcc */
#define PD67_MC1_PULSE_MGMT	0x04
#define PD67_MC1_PULSE_IRQ	0x08
#define PD67_MC1_SPKR_ENA	0x10
#define PD67_MC1_INPACK_ENA	0x80

/* Flags for PD67_FIFO_CTL */
#define PD67_FIFO_EMPTY		0x80

/* Flags for PD67_MISC_CTL_2 */
#define PD67_MC2_FREQ_BYPASS	0x01
#define PD67_MC2_DYNAMIC_MODE	0x02
#define PD67_MC2_SUSPEND	0x04
#define PD67_MC2_5V_CORE	0x08
#define PD67_MC2_LED_ENA	0x10	/* IRQ 12 is LED enable */
#define PD67_MC2_FAST_PCI	0x10	/* 6729: PCI bus > 25 MHz */
#define PD67_MC2_3STATE_BIT7	0x20	/* Floppy change bit */
#define PD67_MC2_DMA_MODE	0x40
#define PD67_MC2_IRQ15_RI	0x80	/* IRQ 15 is ring enable */

/* Flags for PD67_CHIP_INFO */
#define PD67_INFO_SLOTS		0x20	/* 0 = 1 slot, 1 = 2 slots */
#define PD67_INFO_CHIP_ID	0xc0
#define PD67_INFO_REV		0x1c

/* Fields in PD67_TIME_* registers */
#define PD67_TIME_SCALE		0xc0
#define PD67_TIME_SCALE_1	0x00
#define PD67_TIME_SCALE_16	0x40
#define PD67_TIME_SCALE_256	0x80
#define PD67_TIME_SCALE_4096	0xc0
#define PD67_TIME_MULT		0x3f

/* Fields in PD67_DMA_CTL */
#define PD67_DMA_MODE		0xc0
#define PD67_DMA_OFF		0x00
#define PD67_DMA_DREQ_INPACK	0x40
#define PD67_DMA_DREQ_WP	0x80
#define PD67_DMA_DREQ_BVD2	0xc0
#define PD67_DMA_PULLUP		0x20	/* Disable socket pullups? */

/* Fields in PD67_EXT_CTL_1 */
#define PD67_EC1_VCC_PWR_LOCK	0x01
#define PD67_EC1_AUTO_PWR_CLEAR	0x02
#define PD67_EC1_LED_ENA	0x04
#define PD67_EC1_INV_CARD_IRQ	0x08
#define PD67_EC1_INV_MGMT_IRQ	0x10
#define PD67_EC1_PULLUP_CTL	0x20

/* Fields in PD67_EXTERN_DATA */
#define PD67_EXD_VS1(s)		(0x01 << ((s)<<1))
#define PD67_EXD_VS2(s)		(0x02 << ((s)<<1))

/* Fields in PD67_EXT_CTL_2 */
#define PD67_EC2_GPSTB_TOTEM	0x04
#define PD67_EC2_GPSTB_IOR	0x08
#define PD67_EC2_GPSTB_IOW	0x10
#define PD67_EC2_GPSTB_HIGH	0x20

/* Fields in PD67_MISC_CTL_3 */
#define PD67_MC3_IRQ_MASK	0x03
#define PD67_MC3_IRQ_PCPCI	0x00
#define PD67_MC3_IRQ_EXTERN	0x01
#define PD67_MC3_IRQ_PCIWAY	0x02
#define PD67_MC3_IRQ_PCI	0x03
#define PD67_MC3_PWR_MASK	0x0c
#define PD67_MC3_PWR_SERIAL	0x00
#define PD67_MC3_PWR_TI2202	0x08
#define PD67_MC3_PWR_SMB	0x0c

/* Register definitions for Cirrus PD6832 PCI-to-CardBus bridge */

/* PD6832 extension registers -- indexed in PD67_EXT_INDEX */
#define PD68_PCI_SPACE			0x22
#define PD68_PCCARD_SPACE		0x23
#define PD68_WINDOW_TYPE		0x24
#define PD68_EXT_CSC			0x2e
#define PD68_MISC_CTL_4			0x2f
#define PD68_MISC_CTL_5			0x30
#define PD68_MISC_CTL_6			0x31

/* Extra flags in PD67_MISC_CTL_3 */
#define PD68_MC3_HW_SUSP		0x10
#define PD68_MC3_MM_EXPAND		0x40
#define PD68_MC3_MM_ARM			0x80

/* Bridge Control Register */
#define  PD6832_BCR_MGMT_IRQ_ENA	0x0800

/* Socket Number Register */
#define PD6832_SOCKET_NUMBER		0x004c	/* 8 bit */

/* Data structure for tracking vendor-specific state */
typedef struct cirrus_state_t {
    u_char		misc1;		/* PD67_MISC_CTL_1 */
    u_char		misc2;		/* PD67_MISC_CTL_2 */
    u_char		ectl1;		/* PD67_EXT_CTL_1 */
    u_char		timer[6];	/* PD67_TIME_* */
} cirrus_state_t;

#define CIRRUS_PCIC_ID \
    IS_PD6729, IS_PD6730, IS_PD6832

#define CIRRUS_PCIC_INFO \
    { "Cirrus PD6729", IS_CIRRUS|IS_PCI, ID(CIRRUS, 6729) },		\
    { "Cirrus PD6730", IS_CIRRUS|IS_PCI, PCI_VENDOR_ID_CIRRUS, -1 },	\
    { "Cirrus PD6832", IS_CIRRUS|IS_CARDBUS, ID(CIRRUS, 6832) }

/* Special bit in I365_IDENT used for Vadem chip detection */
#define I365_IDENT_VADEM	0x08

/* Special definitions in I365_POWER */
#define VG468_VPP2_MASK		0x0c
#define VG468_VPP2_5V		0x04
#define VG468_VPP2_12V		0x08

/* Unique Vadem registers */
#define VG469_VSENSE		0x1f	/* Card voltage sense */
#define VG469_VSELECT		0x2f	/* Card voltage select */
#define VG468_CTL		0x38	/* Control register */
#define VG468_TIMER		0x39	/* Timer control */
#define VG468_MISC		0x3a	/* Miscellaneous */
#define VG468_GPIO_CFG		0x3b	/* GPIO configuration */
#define VG469_EXT_MODE		0x3c	/* Extended mode register */
#define VG468_SELECT		0x3d	/* Programmable chip select */
#define VG468_SELECT_CFG	0x3e	/* Chip select configuration */
#define VG468_ATA		0x3f	/* ATA control */

/* Flags for VG469_VSENSE */
#define VG469_VSENSE_A_VS1	0x01
#define VG469_VSENSE_A_VS2	0x02
#define VG469_VSENSE_B_VS1	0x04
#define VG469_VSENSE_B_VS2	0x08

/* Flags for VG469_VSELECT */
#define VG469_VSEL_VCC		0x03
#define VG469_VSEL_5V		0x00
#define VG469_VSEL_3V		0x03
#define VG469_VSEL_MAX		0x0c
#define VG469_VSEL_EXT_STAT	0x10
#define VG469_VSEL_EXT_BUS	0x20
#define VG469_VSEL_MIXED	0x40
#define VG469_VSEL_ISA		0x80

/* Flags for VG468_CTL */
#define VG468_CTL_SLOW		0x01	/* 600ns memory timing */
#define VG468_CTL_ASYNC		0x02	/* Asynchronous bus clocking */
#define VG468_CTL_TSSI		0x08	/* Tri-state some outputs */
#define VG468_CTL_DELAY		0x10	/* Card detect debounce */
#define VG468_CTL_INPACK	0x20	/* Obey INPACK signal? */
#define VG468_CTL_POLARITY	0x40	/* VCCEN polarity */
#define VG468_CTL_COMPAT	0x80	/* Compatibility stuff */

#define VG469_CTL_WS_COMPAT	0x04	/* Wait state compatibility */
#define VG469_CTL_STRETCH	0x10	/* LED stretch */

/* Flags for VG468_TIMER */
#define VG468_TIMER_ZEROPWR	0x10	/* Zero power control */
#define VG468_TIMER_SIGEN	0x20	/* Power up */
#define VG468_TIMER_STATUS	0x40	/* Activity timer status */
#define VG468_TIMER_RES		0x80	/* Timer resolution */
#define VG468_TIMER_MASK	0x0f	/* Activity timer timeout */

/* Flags for VG468_MISC */
#define VG468_MISC_GPIO		0x04	/* General-purpose IO */
#define VG468_MISC_DMAWSB	0x08	/* DMA wait state control */
#define VG469_MISC_LEDENA	0x10	/* LED enable */
#define VG468_MISC_VADEMREV	0x40	/* Vadem revision control */
#define VG468_MISC_UNLOCK	0x80	/* Unique register lock */

/* Flags for VG469_EXT_MODE_A */
#define VG469_MODE_VPPST	0x03	/* Vpp steering control */
#define VG469_MODE_INT_SENSE	0x04	/* Internal voltage sense */
#define VG469_MODE_CABLE	0x08
#define VG469_MODE_COMPAT	0x10	/* i82365sl B or DF step */
#define VG469_MODE_TEST		0x20
#define VG469_MODE_RIO		0x40	/* Steer RIO to INTR? */

/* Flags for VG469_EXT_MODE_B */
#define VG469_MODE_B_3V		0x01	/* 3.3v for socket B */

/* Data structure for tracking vendor-specific state */
typedef struct vg46x_state_t {
    u_char		ctl;		/* VG468_CTL */
    u_char		ema;		/* VG468_EXT_MODE_A */
} vg46x_state_t;
