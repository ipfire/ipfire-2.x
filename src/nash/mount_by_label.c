/*
 * taken from util-linux 2.11g and hacked into nash
 *
 * mount_by_label.c - aeb
 *
 * 1999-02-22 Arkadiusz Mi¶kiewicz <misiek@pld.ORG.PL>
 * - added Native Language Support
 * 2000-01-20 James Antill <james@and.org>
 * - Added error message if /proc/partitions cannot be opened
 * 2000-05-09 Erik Troan <ewt@redhat.com>
 * - Added cache for UUID and disk labels
 * 2000-11-07 Nathan Scott <nathans@sgi.com>
 * - Added XFS support
 */

#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/stat.h>
#include "linux_fs.h"
#include "mount_by_label.h"

#define PROC_PARTITIONS "/proc/partitions"
#define DEVLABELDIR	"/dev"

#define _(str) (str)

static struct uuidCache_s {
	struct uuidCache_s *next;
	char uuid[16];
	char *device;
	char *label;
	int major, minor;
} *uuidCache = NULL;

/* for now, only ext2, ext3 and xfs are supported */
static int
get_label_uuid(const char *device, char **label, char *uuid) {

	/* start with ext2/3 and xfs tests, taken from mount_guess_fstype */
	/* should merge these later */
	int fd;
	int rv = 1;
	size_t namesize;
	struct ext2_super_block e2sb;
	struct xfs_super_block xfsb;

	fd = open(device, O_RDONLY);
	if (fd < 0)
		return rv;

	if (lseek(fd, 1024, SEEK_SET) == 1024
	    && read(fd, (char *) &e2sb, sizeof(e2sb)) == sizeof(e2sb)
	    && (ext2magic(e2sb) == EXT2_SUPER_MAGIC)) {
		memcpy(uuid, e2sb.s_uuid, sizeof(e2sb.s_uuid));
		namesize = sizeof(e2sb.s_volume_name);
		if ((*label = calloc(namesize + 1, 1)) != NULL)
			memcpy(*label, e2sb.s_volume_name, namesize);
		rv = 0;
	}
	else if (lseek(fd, 0, SEEK_SET) == 0
	    && read(fd, (char *) &xfsb, sizeof(xfsb)) == sizeof(xfsb)
	    && (strncmp((char *)xfsb.s_magic, XFS_SUPER_MAGIC, 4) == 0)) {
		memcpy(uuid, xfsb.s_uuid, sizeof(xfsb.s_uuid));
		namesize = sizeof(xfsb.s_fname);
		if ((*label = calloc(namesize + 1, 1)) != NULL)
			memcpy(*label, xfsb.s_fname, namesize);
		rv = 0;
	}

	close(fd);
	return rv;
}

static void
uuidcache_addentry(char * device, int major, int minor, char *label, char *uuid) {
	struct uuidCache_s *last;
    
	if (!uuidCache) {
		last = uuidCache = malloc(sizeof(*uuidCache));
	} else {
		for (last = uuidCache; last->next; last = last->next) ;
		last->next = malloc(sizeof(*uuidCache));
		last = last->next;
	}
	last->next = NULL;
	last->label = label;
	last->device = device;
	last->major = major;
	last->minor = minor;
	memcpy(last->uuid, uuid, sizeof(last->uuid));
}

static void
uuidcache_init(void) {
	char line[100];
	char *s;
	int ma, mi, sz;
	static char ptname[100];
	FILE *procpt;
	char uuid[16], *label;
	char device[110];
	int firstPass;
	int handleOnFirst;
	char * chptr, * endptr;

	if (uuidCache)
		return;

	procpt = fopen(PROC_PARTITIONS, "r");
	if (!procpt) {
		static int warn = 0;
		if (!warn++)
		    fprintf (stderr, _("mount: could not open %s, so UUID and LABEL "
			     "conversion cannot be done.\n"),
		       PROC_PARTITIONS);
		return;
	}

	for (firstPass = 1; firstPass >= 0; firstPass--) {
	    fseek(procpt, 0, SEEK_SET);

	    while (fgets(line, sizeof(line), procpt)) {
		/* The original version of this code used sscanf, but
		   diet's sscanf is quite limited */
		chptr = line;
		if (*chptr++ != ' ') continue;

		ma = strtol(chptr, &endptr, 0);
		if (endptr == chptr) continue;
		while (isspace(*endptr)) endptr++;
		chptr = endptr;

		mi = strtol(chptr, &endptr, 0);
		if (endptr == chptr) continue;
		while (isspace(*endptr)) endptr++;
		chptr = endptr;

		sz = strtol(chptr, &endptr, 0);
		if (endptr == chptr) continue;
		while (isspace(*endptr)) endptr++;
		chptr = endptr;

		while (!isspace(*endptr) && *endptr != '\n') endptr++;
		if (chptr == endptr) continue;
		strncpy(ptname, chptr, endptr - chptr);
		ptname[endptr - chptr] = '\0';

		/* skip extended partitions (heuristic: size 1) */
		if (sz == 1)
			continue;

		/* look only at md devices on first pass */
		handleOnFirst = !strncmp(ptname, "md", 2);
		if (firstPass != handleOnFirst)
			continue;

		/* skip entire disk (minor 0, 64, ... on ide;
		   0, 16, ... on sd) */
		/* heuristic: partition name ends in a digit */

		for(s = ptname; *s; s++);

		if (isdigit(s[-1])) {
			char * ptr;
			char * deviceDir = NULL;
			int mustRemove = 0;
			int mustRemoveDir = 0;
			int i;

			sprintf(device, "%s/%s", DEVLABELDIR, ptname);
			if (access(device, F_OK)) {
			    ptr = device;
			    i = 0;
			    while (*ptr)
				if (*ptr++ == '/')
				    i++;
			    if (i > 2) {
				deviceDir = alloca(strlen(device) + 1);
				strcpy(deviceDir, device);
				ptr = deviceDir + (strlen(device) - 1);
				while (*ptr != '/')
				    *ptr-- = '\0';
				if (mkdir(deviceDir, 0644)) {
				    printf("mkdir: cannot create directory %s: %d\n", deviceDir, errno);
				} else {
				    mustRemoveDir = 1;
				}
			    }

			    mknod(device, S_IFBLK | 0600, makedev(ma, mi));
			    mustRemove = 1;
			}
			if (!get_label_uuid(device, &label, uuid))
				uuidcache_addentry(strdup(device), ma, mi, 
						   label, uuid);

			if (mustRemove) unlink(device);
			if (mustRemoveDir) rmdir(deviceDir);
		}
	    }
	}

	fclose(procpt);
}

#define UUID   1
#define VOL    2

static char *
get_spec_by_x(int n, const char *t, int * majorPtr, int * minorPtr) {
	struct uuidCache_s *uc;

	uuidcache_init();
	uc = uuidCache;

	while(uc) {
		switch (n) {
		case UUID:
			if (!memcmp(t, uc->uuid, sizeof(uc->uuid))) {
				*majorPtr = uc->major;
				*minorPtr = uc->minor;
				return uc->device;
			}
			break;
		case VOL:
			if (!strcmp(t, uc->label)) {
				*majorPtr = uc->major;
				*minorPtr = uc->minor;
				return uc->device;
			}
			break;
		}
		uc = uc->next;
	}
	return NULL;
}

static unsigned char
fromhex(char c) {
	if (isdigit(c))
		return (c - '0');
	else if (islower(c))
		return (c - 'a' + 10);
	else
		return (c - 'A' + 10);
}

char *
get_spec_by_uuid(const char *s, int * major, int * minor) {
	unsigned char uuid[16];
	int i;

	if (strlen(s) != 36 ||
	    s[8] != '-' || s[13] != '-' || s[18] != '-' || s[23] != '-')
		goto bad_uuid;
	for (i=0; i<16; i++) {
	    if (*s == '-') s++;
	    if (!isxdigit(s[0]) || !isxdigit(s[1]))
		    goto bad_uuid;
	    uuid[i] = ((fromhex(s[0])<<4) | fromhex(s[1]));
	    s += 2;
	}
	return get_spec_by_x(UUID, (char *)uuid, major, minor);

 bad_uuid:
	fprintf(stderr, _("mount: bad UUID"));
	return 0;
}

char *
get_spec_by_volume_label(const char *s, int * major, int * minor) {
	return get_spec_by_x(VOL, s, major, minor);
}

int display_uuid_cache(void) {
	struct uuidCache_s * u;
	size_t i;

	uuidcache_init();

	u = uuidCache;
	while (u) {
	    printf("%s %s ", u->device, u->label);
	    for (i = 0; i < sizeof(u->uuid); i++) {
		if (i == 4 || i == 6 || i == 8 || i == 10)
		    printf("-");
		printf("%x", u->uuid[i] & 0xff);
	    }
	    printf("\n");
	    u = u->next;
	}

	return 0;
}

