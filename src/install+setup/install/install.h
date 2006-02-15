/* SmoothWall install program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Main include file.
 * 
 * $Id: install.h,v 1.10.2.4 2006/01/11 01:01:38 franck78 Exp $
 * 
 */

#include "../libsmooth/libsmooth.h"

#define IDE_EMPTY 0
#define IDE_CDROM 1
#define IDE_HD 2
#define IDE_UNKNOWN 3

/* CDROMS and harddisks. */
struct devparams
{
	char devnode_disk[30];		// when single partition is addressed
	char devnode_part[30];		// when the RAID partition is addressed
	char devnode_disk_run[30];	// the same dev but after installation 
	char devnode_part_run[30];
	char modulename[STRING_SIZE];
	char options[STRING_SIZE];
//	int module;
};

/* ide.c */
int checkide(char letter);
char findidetype(int type);

/* cdrom.c */
int ejectcdrom(char *dev);

/* nic.c */
int networkmenu(struct keyvalue *ethernetkv);

/* net.c */
int checktarball(char *);

/* config.c */
int write_disk_configs(struct devparams *dp);
int write_lang_configs( char *lang);
int write_ethernet_configs(struct keyvalue *ethernetkv);

/* pcmcia.c */
char * initialize_pcmcia (void);

/* upgrade_v12_v13.c */
int upgrade_v12_v13();

/* upgrade_v130_v131.c */
int upgrade_v130_v140();

/* usb.c */
int initialize_usb();
int write_usb_modules_conf();
int checkusb (char *partition);

/* scsi.c */
int try_scsi(char *dev);
int get_boot(char *dev);

/*main.c */
int modprobe (char *mod);
int rmmod (char *mod);

extern char *bz_tr[];
extern char *cs_tr[];
extern char *da_tr[];
extern char *en_tr[];
extern char *es_tr[];
extern char *fi_tr[];
extern char *fr_tr[];
extern char *hu_tr[];
extern char *la_tr[];
extern char *nl_tr[];
extern char *de_tr[];
extern char *tr_tr[];
extern char *it_tr[];
extern char *el_tr[];
extern char *pl_tr[];
extern char *pt_tr[];
extern char *sk_tr[];
extern char *so_tr[];
extern char *sv_tr[];
extern char *no_tr[];
extern char *vi_tr[];
