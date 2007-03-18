#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>
#include <stdio.h>
#include <fcntl.h>

static dev_t try_name(char *name, int part)
{
	char path[64];
	char buf[32];
	int range;
	dev_t res;
	char *s;
	int len;
	int fd;
	unsigned int maj, min;

	/* read device number from .../dev */

	sprintf(path, "/sys/block/%s/dev", name);
	fd = open(path, O_RDONLY);
	if (fd < 0)
		goto fail;
	len = read(fd, buf, 32);
	close(fd);
	if (len <= 0 || len == 32 || buf[len - 1] != '\n')
		goto fail;
	buf[len - 1] = '\0';
	if (sscanf(buf, "%u:%u", &maj, &min) != 2)
		goto fail;
	res = makedev(maj, min);
	if (maj != major(res) || min != minor(res))
		goto fail;

	/* if it's there and we are not looking for a partition - that's it */
	if (!part)
		return res;

	/* otherwise read range from .../range */
	snprintf(path, 64, "/sys/block/%s/range", name);
	fd = open(path, O_RDONLY);
	if (fd < 0)
		goto fail;
	len = read(fd, buf, 32);
	close(fd);
	if (len <= 0 || len == 32 || buf[len - 1] != '\n')
		goto fail;
	buf[len - 1] = '\0';
	range = strtoul(buf, &s, 10);
	if (*s)
		goto fail;

	/* if partition is within range - we got it */
	if (part < range)
		return res + part;
fail:
	return 0;
}

/*
 *	Convert a name into device number.  We accept the following variants:
 *
 *	1) device number in hexadecimal	represents itself
 *	2) /dev/nfs represents Root_NFS (0xff)
 *	3) /dev/<disk_name> represents the device number of disk
 *	4) /dev/<disk_name><decimal> represents the device number
 *         of partition - device number of disk plus the partition number
 *	5) /dev/<disk_name>p<decimal> - same as the above, that form is
 *	   used when disk name of partitioned disk ends on a digit.
 *
 *	If name doesn't have fall into the categories above, we return 0.
 *	sysfs is used to check if something is a disk name - it has
 *	all known disks under bus/block/devices.  If the disk name
 *	contains slashes, name of driverfs node has them replaced with
 *	bangs.  try_name() does the actual checks, assuming that sysfs
 *	is mounted on /sys.
 *
 *	Note that cases (1) and (2) are already handled by the kernel,
 *	so we can ifdef them out, provided that we check real-root-dev
 *	first.
 */

dev_t name_to_dev_t(char *name)
{
	char s[32];
	char *p;
	dev_t res = 0;
	int part;

	if (strncmp(name, "/dev/", 5) != 0) {
#if 1 /* kernel used to do this */
		unsigned maj, min;

		if (sscanf(name, "%u:%u", &maj, &min) == 2) {
			res = makedev(maj, min);
			if (maj != major(res) || min != minor(res))
				return 0;
		} else {
			res = strtoul(name, &p, 16);
			if (*p)
				return 0;
		}
#endif
		return res;
	}

	name += 5;

#if 1 /* kernel used to do this */
	if (strcmp(name, "nfs") == 0)
		return makedev(0, 255);
#endif

	if (strlen(name) > 31)
		return 0;
	strcpy(s, name);
	for (p = s; *p; p++)
		if (*p == '/')
			*p = '!';
	res = try_name(s, 0);
	if (res)
		return res;

	while (p > s && isdigit(p[-1]))
		p--;
	if (p == s || !*p || *p == '0')
		return 0;
	part = strtoul(p, NULL, 10);
	*p = '\0';
	res = try_name(s, part);
	if (res)
		return res;

	if (p < s + 2 || !isdigit(p[-2]) || p[-1] != 'p')
		return 0;
	p[-1] = '\0';
	return try_name(s, part);
}
