/*
 * nash.c
 * 
 * Simple code to load modules, mount root, and get things going. Uses
 * dietlibc to keep things small.
 *
 * Erik Troan (ewt@redhat.com)
 *
 * Copyright 2002 Red Hat Software 
 *
 * This software may be freely redistributed under the terms of the GNU
 * public license.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 *
 */

/* We internalize losetup, mount, raidautorun, and echo commands. Other
   commands are run from the filesystem. Comments and blank lines work as 
   well, argument parsing is screwy. */

#include <ctype.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <net/if.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mount.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/un.h>
#include <sys/wait.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/reboot.h>
#include <termios.h>

#include <asm/unistd.h>

#include "mount_by_label.h"

/* Need to tell loop.h what the actual dev_t type is. */
#undef dev_t
#if defined(__alpha) || (defined(__sparc__) && defined(__arch64__))
#define dev_t unsigned int
#else
#define dev_t unsigned short
#endif
#include <linux/loop.h>
#undef dev_t
#define dev_t dev_t

#define syslog klogctl

#include <linux/cdrom.h>
#define MD_MAJOR 9
#include <linux/raid/md_u.h>

#ifndef RAID_AUTORUN
#define RAID_AUTORUN           _IO (MD_MAJOR, 0x14)
#endif

#ifndef MS_REMOUNT
#define MS_REMOUNT      32
#endif

#ifdef USE_DIET
static inline _syscall2(int,pivot_root,const char *,one,const char *,two)
#endif

#define MAX(a, b) ((a) > (b) ? a : b)

int testing = 0, quiet = 0;

#define PATH "/usr/bin:/bin:/sbin:/usr/sbin"

char * env[] = {
    "PATH=" PATH,
    NULL
};

int smartmknod(char * device, mode_t mode, dev_t dev) {
    char buf[256];
    char * end;

    strcpy(buf, device);

    end = buf;
    while (*end) {
	if (*end == '/') {
	    *end = '\0';
	    if (access(buf, F_OK) && errno == ENOENT) 
		mkdir(buf, 0700);
	    *end = '/';
	}

	end++;
    }

    return mknod(device, mode, dev);
}

char * getArg(char * cmd, char * end, char ** arg) {
    char quote = '\0';

    if (cmd >= end) return NULL;

    while (isspace(*cmd) && cmd < end) cmd++;
    if (cmd >= end) return NULL;

    if (*cmd == '"')
	cmd++, quote = '"';
    else if (*cmd == '\'')
	cmd++, quote = '\'';

    if (quote) {
	*arg = cmd;

	/* This doesn't support \ escapes */
	while (cmd < end && *cmd != quote) cmd++;

	if (cmd == end) {
	    printf("error: quote mismatch for %s\n", *arg);
	    return NULL;
	}

	*cmd = '\0';
	cmd++;
    } else {
	*arg = cmd;
	while (!isspace(*cmd) && cmd < end) cmd++;
	*cmd = '\0';
    }

    cmd++;

    while (isspace(*cmd)) cmd++;

    return cmd;
}

int mountCommand(char * cmd, char * end) {
    char * fsType = NULL;
    char * device;
    char * mntPoint;
    char * deviceDir;
    char * options = NULL;
    int mustRemove = 0;
    int mustRemoveDir = 0;
    int rc;
    int flags = MS_MGC_VAL;
    char * newOpts;

    cmd = getArg(cmd, end, &device);
    if (!cmd) {
	printf("usage: mount [--ro] [-o <opts>] -t <type> <device> <mntpoint>\n");
	return 1;
    }

    while (cmd && *device == '-') {
	if (!strcmp(device, "--ro")) {
	    flags |= MS_RDONLY;
	} else if (!strcmp(device, "-o")) {
	    cmd = getArg(cmd, end, &options);
	    if (!cmd) {
		printf("mount: -o requires arguments\n");
		return 1;
	    }
	} else if (!strcmp(device, "-t")) {
	    if (!(cmd = getArg(cmd, end, &fsType))) {
		printf("mount: missing filesystem type\n");
		return 1;
	    }
	}

	cmd = getArg(cmd, end, &device);
    }

    if (!cmd) {
	printf("mount: missing device\n");
	return 1;
    }

    if (!(cmd = getArg(cmd, end, &mntPoint))) {
	printf("mount: missing mount point\n");
	return 1;
    }

    if (!fsType) {
	printf("mount: filesystem type expected\n");
	return 1;
    }

    if (cmd < end) {
	printf("mount: unexpected arguments\n");
	return 1;
    }

    /* need to deal with options */ 
    if (options) {
	char * end;
	char * start = options;

	newOpts = alloca(strlen(options) + 1);
	*newOpts = '\0';

	while (*start) {
	    end = strchr(start, ',');
	    if (!end) {
		end = start + strlen(start);
	    } else {
		*end = '\0';
		end++;
	    }

	    if (!strcmp(start, "ro"))
		flags |= MS_RDONLY;
	    else if (!strcmp(start, "rw"))
		flags &= ~MS_RDONLY;
	    else if (!strcmp(start, "nosuid"))
		flags |= MS_NOSUID;
	    else if (!strcmp(start, "suid"))
		flags &= ~MS_NOSUID;
	    else if (!strcmp(start, "nodev"))
		flags |= MS_NODEV;
	    else if (!strcmp(start, "dev"))
		flags &= ~MS_NODEV;
	    else if (!strcmp(start, "noexec"))
		flags |= MS_NOEXEC;
	    else if (!strcmp(start, "exec"))
		flags &= ~MS_NOEXEC;
	    else if (!strcmp(start, "sync"))
		flags |= MS_SYNCHRONOUS;
	    else if (!strcmp(start, "async"))
		flags &= ~MS_SYNCHRONOUS;
	    else if (!strcmp(start, "nodiratime"))
		flags |= MS_NODIRATIME;
	    else if (!strcmp(start, "diratime"))
		flags &= ~MS_NODIRATIME;
	    else if (!strcmp(start, "noatime"))
		flags |= MS_NOATIME;
	    else if (!strcmp(start, "atime"))
		flags &= ~MS_NOATIME;
	    else if (!strcmp(start, "remount"))
		flags |= MS_REMOUNT;
	    else if (!strcmp(start, "defaults"))
		;
	    else {
		if (*newOpts)
		    strcat(newOpts, ",");
		strcat(newOpts, start);
	    }

	    start = end;
	}

	options = newOpts;
    }

    if (!strncmp("LABEL=", device, 6)) {
	int major, minor;
	char * devName;
	char * ptr;
	int i;

	devName = get_spec_by_volume_label(device + 6, &major, &minor);

	if (devName) {
	    device = devName;
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
		      printf("mkdir: cannot create directory %s\n", deviceDir);
		    } else {
		      mustRemoveDir = 1;
		    }
		}
		if (smartmknod(device, S_IFBLK | 0600, makedev(major, minor))) {
		    printf("mount: cannot create device %s (%d,%d)\n",
			   device, major, minor);
		    return 1;
		}
		mustRemove = 1;
	    }
	}
    }

    if (testing) {
	printf("mount %s%s%s-t '%s' '%s' '%s' (%s%s%s%s%s%s%s)\n", 
		options ? "-o '" : "",	
		options ? options : "",	
		options ? "\' " : "",	
		fsType, device, mntPoint,
		(flags & MS_RDONLY) ? "ro " : "",
		(flags & MS_NOSUID) ? "nosuid " : "",
		(flags & MS_NODEV) ? "nodev " : "",
		(flags & MS_NOEXEC) ? "noexec " : "",
		(flags & MS_SYNCHRONOUS) ? "sync " : "",
		(flags & MS_REMOUNT) ? "remount " : "",
		(flags & MS_NOATIME) ? "noatime " : ""
	    );
    } else {
	if (mount(device, mntPoint, fsType, flags, options)) {
	    printf("mount: error %d mounting %s\n", errno, fsType);
	    rc = 1;
	}
    }

    if (mustRemove) unlink(device);
    if (mustRemoveDir) rmdir(deviceDir);

    return rc;
}

int otherCommand(char * bin, char * cmd, char * end, int doFork) {
    char * args[128];
    char ** nextArg;
    int pid;
    int status;
    char fullPath[255];
    const static char * sysPath = PATH;
    const char * pathStart;
    const char * pathEnd;
    char * stdoutFile = NULL;
    int stdoutFd = 0;

    nextArg = args;

    if (!strchr(bin, '/')) {
	pathStart = sysPath;
	while (*pathStart) {
	    pathEnd = strchr(pathStart, ':');

	    if (!pathEnd) pathEnd = pathStart + strlen(pathStart);

	    strncpy(fullPath, pathStart, pathEnd - pathStart);
	    fullPath[pathEnd - pathStart] = '/';
	    strcpy(fullPath + (pathEnd - pathStart + 1), bin); 

	    pathStart = pathEnd;
	    if (*pathStart) pathStart++;

	    if (!access(fullPath, X_OK)) {
		bin = fullPath;
		break;
	    }
	}
    }

    *nextArg = bin;

    while (cmd && cmd < end) {
	nextArg++;
	cmd = getArg(cmd, end, nextArg);
    }
	
    if (cmd) nextArg++;
    *nextArg = NULL;

    /* if the next-to-last arg is a >, redirect the output properly */
    if (((nextArg - args) >= 2) && !strcmp(*(nextArg - 2), ">")) {
	stdoutFile = *(nextArg - 1);
	*(nextArg - 2) = NULL;

	stdoutFd = open(stdoutFile, O_CREAT | O_RDWR | O_TRUNC, 0600);
	if (stdoutFd < 0) {
	    printf("nash: failed to open %s: %d\n", stdoutFile, errno);
	    return 1;
	}
    }

    if (testing) {
	printf("%s ", bin);
	nextArg = args + 1;
	while (*nextArg)
	    printf(" '%s'", *nextArg++);
	if (stdoutFile)
	    printf(" (> %s)", stdoutFile);
	printf("\n");
    } else {
	if (!doFork || !(pid = fork())) {
	    /* child */
	    dup2(stdoutFd, 1);
	    execve(args[0], args, env);
	    printf("ERROR: failed in exec of %s\n", args[0]);
	    return 1;
	}

	close(stdoutFd);

	wait4(-1, &status, 0, NULL);
	if (!WIFEXITED(status) || WEXITSTATUS(status)) {
	    printf("ERROR: %s exited abnormally!\n", args[0]);
	    return 1;
	}
    }

    return 0;
}

int execCommand(char * cmd, char * end) {
    char * bin;

    if (!(cmd = getArg(cmd, end, &bin))) {
	printf("exec: argument expected\n");
	return 1;
    }

    return otherCommand(bin, cmd, end, 0);
}

int losetupCommand(char * cmd, char * end) {
    char * device;
    char * file;
    int fd;
    struct loop_info loopInfo;
    int dev;

    if (!(cmd = getArg(cmd, end, &device))) {
	printf("losetup: missing device\n");
	return 1;
    }

    if (!(cmd = getArg(cmd, end, &file))) {
	printf("losetup: missing file\n");
	return 1;
    }

    if (cmd < end) {
	printf("losetup: unexpected arguments\n");
	return 1;
    }

    if (testing) {
	printf("losetup '%s' '%s'\n", device, file);
    } else {
	dev = open(device, O_RDWR, 0);
	if (dev < 0) {
	    printf("losetup: failed to open %s: %d\n", device, errno);
	    return 1;
	}

	fd = open(file, O_RDWR, 0);
	if (fd < 0) {
	    printf("losetup: failed to open %s: %d\n", file, errno);
	    close(dev);
	    return 1;
	}

	if (ioctl(dev, LOOP_SET_FD, (long) fd)) {
	    printf("losetup: LOOP_SET_FD failed: %d\n", errno);
	    close(dev);
	    close(fd);
	    return 1;
	}

	close(fd);

	memset(&loopInfo, 0, sizeof(loopInfo));
	strcpy(loopInfo.lo_name, file);

	if (ioctl(dev, LOOP_SET_STATUS, &loopInfo)) 
	    printf("losetup: LOOP_SET_STATUS failed: %d\n", errno);

	close(dev);
    }

    return 0;
}

int raidautorunCommand(char * cmd, char * end) {
    char * device;
    int fd;

    if (!(cmd = getArg(cmd, end, &device))) {
	printf("raidautorun: raid device expected as first argument\n");
	return 1;
    }

    if (cmd < end) {
	printf("raidautorun: unexpected arguments\n");
	return 1;
    }

    fd = open(device, O_RDWR, 0);
    if (fd < 0) {
	printf("raidautorun: failed to open %s: %d\n", device, errno);
	return 1;
    }

    if (ioctl(fd, RAID_AUTORUN, 0)) {
	printf("raidautorun: RAID_AUTORUN failed: %d\n", errno);
	close(fd);
	return 1;
    }

    close(fd);
    return 0;
}

static int my_pivot_root(char * one, char * two) {
#ifdef USE_DIET
    return pivot_root(one, two);
#else
    return syscall(__NR_pivot_root, one, two);
#endif
}

int pivotrootCommand(char * cmd, char * end) {
    char * new;
    char * old;

    if (!(cmd = getArg(cmd, end, &new))) {
	printf("pivotroot: new root mount point expected\n");
	return 1;
    }

    if (!(cmd = getArg(cmd, end, &old))) {
	printf("pivotroot: old root mount point expected\n");
	return 1;
    }

    if (cmd < end) {
	printf("pivotroot: unexpected arguments\n");
	return 1;
    }

    if (my_pivot_root(new, old)) {
	printf("pivotroot: pivot_root(%s,%s) failed: %d\n", new, old, errno);
	return 1;
    }

    return 0;
}

int echoCommand(char * cmd, char * end) {
    char * args[256];
    char ** nextArg = args;
    int outFd = 1;
    int num = 0;
    int i;

    if (testing && !quiet) {
	printf("(echo) ");
	fflush(stdout);
    }

    while ((cmd = getArg(cmd, end, nextArg)))
	nextArg++, num++;

    if ((nextArg - args >= 2) && !strcmp(*(nextArg - 2), ">")) {
	outFd = open(*(nextArg - 1), O_RDWR | O_CREAT | O_TRUNC, 0644);
	if (outFd < 0) {
	    printf("echo: cannot open %s for write: %d\n", 
		    *(nextArg - 1), errno);
	    return 1;
	}

	num -= 2;
    }

    for (i = 0; i < num;i ++) {
	if (i)
	    write(outFd, " ", 1);
	write(outFd, args[i], strlen(args[i]));
    }

    write(outFd, "\n", 1);

    if (outFd != 1) close(outFd);

    return 0;
}

int umountCommand(char * cmd, char * end) {
    char * path;

    if (!(cmd = getArg(cmd, end, &path))) {
	printf("umount: path expected\n");
	return 1;
    }

    if (cmd < end) {
	printf("umount: unexpected arguments\n");
	return 1;
    }

    if (umount(path)) {
	printf("umount %s failed: %d\n", path, errno);
	return 1;
    }

    return 0;
}

int mkrootdevCommand(char * cmd, char * end) {
    char * path;
    char * start, * chptr;
    unsigned int devNum = 0;
    int fd;
    int i;
    char buf[1024];
    int major, minor;

    if (!(cmd = getArg(cmd, end, &path))) {
	printf("mkrootdev: path expected\n");
	return 1;
    }

    if (cmd < end) {
	printf("mkrootdev: unexpected arguments\n");
	return 1;
    }

    fd = open("/proc/cmdline", O_RDONLY, 0);
    if (fd < 0) {
	printf("mkrootdev: failed to open /proc/cmdline: %d\n", errno);
	return 1;
    }

    i = read(fd, buf, sizeof(buf));
    if (i < 0) {
	printf("mkrootdev: failed to read /proc/cmdline: %d\n", errno);
	close(fd);
	return 1;
    }

    close(fd);
    buf[i - 1] = '\0';

    start = buf;
    while (*start && isspace(*start)) start++;
    while (*start && strncmp(start, "root=", 5)) {
	while (*start && !isspace(*start)) start++;
	while (*start && isspace(*start)) start++;
    }

    start += 5;
    chptr = start;
    while (*chptr && !isspace(*chptr)) chptr++;
    *chptr = '\0';

    if (!strncmp(start, "LABEL=", 6)) {
	if (get_spec_by_volume_label(start + 6, &major, &minor)) {
	    if (smartmknod(path, S_IFBLK | 0600, makedev(major, minor))) {
		printf("mount: cannot create device %s (%d,%d)\n",
		       path, major, minor);
		return 1;
	    }

	    return 0;
	}

	printf("mkrootdev: label %s not found\n", start + 6);

	return 1;
    }

    fd = open("/proc/sys/kernel/real-root-dev", O_RDONLY, 0);
    if (fd < 0) {
	printf("mkrootdev: failed to open /proc/sys/kernel/real-root-dev: %d\n", errno);
	return 1;
    }

    i = read(fd, buf, sizeof(buf));
    if (i < 0) {
	printf("mkrootdev: failed to read real-root-dev: %d\n", errno);
	close(fd);
	return 1;
    }

    close(fd);
    buf[i - 1] = '\0';

    devNum = atoi(buf);
    if (devNum < 0) {
	printf("mkrootdev: bad device %s\n", buf);
	return 1;
    }

    if (smartmknod(path, S_IFBLK | 0700, devNum)) {
	printf("mkrootdev: mknod failed: %d\n", errno);
	return 1;
    }

    return 0;
}

int mkdirCommand(char * cmd, char * end) {
    char * dir;
    int ignoreExists = 0;

    cmd = getArg(cmd, end, &dir);

    if (cmd && !strcmp(dir, "-p")) {
	ignoreExists = 1;
	cmd = getArg(cmd, end, &dir);
    }

    if (!cmd) {
	printf("mkdir: directory expected\n");
	return 1;
    }

    if (mkdir(dir, 0755)) {
	if (!ignoreExists && errno == EEXIST) {
	    printf("mkdir: failed to create %s: %d\n", dir, errno);
	    return 1;
	}
    }

    return 0;
}

int accessCommand(char * cmd, char * end) {
    char * permStr;
    int perms = 0;
    char * file;

    cmd = getArg(cmd, end, &permStr);
    if (cmd) cmd = getArg(cmd, end, &file);

    if (!cmd || *permStr != '-') {
	printf("usage: access -[perm] file\n");
	return 1;
    }

    permStr++;
    while (*permStr) {
	switch (*permStr) {
	  case 'r': perms |= R_OK; break;
	  case 'w': perms |= W_OK; break;
	  case 'x': perms |= X_OK; break;
	  case 'f': perms |= F_OK; break;
	  default:
	    printf("perms must be -[r][w][x][f]\n");
	    return 1;
	}

	permStr++;
    }

    if (access(file, perms))
	return 1;

    return 0;
}

int sleepCommand(char * cmd, char * end) {
    char *delaystr;
    int delay;

    if (!(cmd = getArg(cmd, end, &delaystr))) {
	printf("sleep: delay expected\n");
	return 1;
    }

    delay = atoi(delaystr);
    sleep(delay);

    return 0;
}

int readlinkCommand(char * cmd, char * end) {
    char * path;
    char * buf, * respath, * fullpath;
    struct stat sb;

    if (!(cmd = getArg(cmd, end, &path))) {
        printf("readlink: file expected\n");
        return 1;
    }

    if (lstat(path, &sb) == -1) {
        fprintf(stderr, "unable to stat %s: %d\n", path, errno);
        return 1;
    }

    if (!S_ISLNK(sb.st_mode)) {
        printf("%s\n", path);
        return 0;
    }
    
    buf = malloc(512);
    if (readlink(path, buf, 512) == -1) {
	fprintf(stderr, "error readlink %s: %d\n", path, errno);
	return 1;
    }

    /* symlink is absolute */
    if (buf[0] == '/') {
        printf("%s\n", buf);
        return 0;
    } 
   
    /* nope, need to handle the relative symlink case too */
    respath = strrchr(path, '/');
    if (respath) {
        *respath = '\0';
    }

    fullpath = malloc(512);
    /* and normalize it */
    snprintf(fullpath, 512, "%s/%s", path, buf);
    respath = malloc(PATH_MAX);
    if (!(respath = realpath(fullpath, respath))) {
        fprintf(stderr, "error realpath %s: %d\n", fullpath, errno);
        return 1;
    }

    printf("%s\n", respath);
    return 0;
}

int doFind(char * dirName, char * name) {
    struct stat sb;
    DIR * dir;
    struct dirent * d;
    char * strBuf = alloca(strlen(dirName) + 1024);

    if (!(dir = opendir(dirName))) {
	fprintf(stderr, "error opening %s: %d\n", dirName, errno);
	return 0;
    }

    errno = 0;
    while ((d = readdir(dir))) {
	errno = 0;

	strcpy(strBuf, dirName);
	strcat(strBuf, "/");
	strcat(strBuf, d->d_name);

	if (!strcmp(d->d_name, name))
	    printf("%s\n", strBuf);

	if (!strcmp(d->d_name, ".") || !strcmp(d->d_name, "..")) {
	    errno = 0;
	    continue;
	}

	if (lstat(strBuf, &sb)) {
	    fprintf(stderr, "failed to stat %s: %d\n", strBuf, errno);
	    errno = 0;
	    continue;
	}

	if (S_ISDIR(sb.st_mode))
	    doFind(strBuf, name);
    }

    if (errno) {
	closedir(dir);
	printf("error reading from %s: %d\n", dirName, errno);
	return 1;
    }

    closedir(dir);

    return 0;
}

int findCommand(char * cmd, char * end) {
    char * dir;
    char * name;

    cmd = getArg(cmd, end, &dir);
    if (cmd) cmd = getArg(cmd, end, &name);
    if (cmd && strcmp(name, "-name")) {
	printf("usage: find [path] -name [file]\n");
	return 1;
    }

    if (cmd) cmd = getArg(cmd, end, &name);
    if (!cmd) {
	printf("usage: find [path] -name [file]\n");
	return 1;
    }

    return doFind(dir, name);
}

int findlodevCommand(char * cmd, char * end) {
    char devName[20];
    int devNum;
    int fd;
    struct loop_info loopInfo;
    char separator[2] = "";

    if (*end != '\n') {
	printf("usage: findlodev\n");
	return 1;
    }

    if (!access("/dev/.devfsd", X_OK))
	strcpy(separator, "/");

    for (devNum = 0; devNum < 256; devNum++) {
	sprintf(devName, "/dev/loop%s%d", separator, devNum);
	if ((fd = open(devName, O_RDONLY)) < 0) return 0;

	if (ioctl(fd, LOOP_GET_STATUS, &loopInfo)) {
	    close(fd);
	    printf("%s\n", devName);
	    return 0;
	}

	close(fd);
    }

    return 0;
}

int mknodCommand(char * cmd, char * end) {
    char * path, * type;
    char * majorStr, * minorStr;
    int major;
    int minor;
    char * chptr;
    mode_t mode;

    cmd = getArg(cmd, end, &path);
    cmd = getArg(cmd, end, &type);
    cmd = getArg(cmd, end, &majorStr);
    cmd = getArg(cmd, end, &minorStr);
    if (!minorStr) {
	printf("mknod: usage mknod <path> [c|b] <major> <minor>\n");
	return 1;
    }

    if (!strcmp(type, "b")) {
	mode = S_IFBLK;
    } else if (!strcmp(type, "c")) {
	mode = S_IFCHR;
    } else {
	printf("mknod: invalid type\n");
	return 1;
    }

    major = strtol(majorStr, &chptr, 10);
    if (*chptr) {
	printf("invalid major number\n");
	return 1;
    }

    minor = strtol(minorStr, &chptr, 10);
    if (*chptr) {
	printf("invalid minor number\n");
	return 1;
    }

    if (smartmknod(path, mode | 0600, makedev(major, minor))) {
	printf("mknod: failed to create %s: %d\n", path, errno);
	return 1;
    }

    return 0;
}

int mkdevicesCommand(char * cmd, char * end) {
    int fd;
    char buf[32768];
    int i;
    char * start, * chptr;
    int major, minor;
    char old;
    char devName[128];
    char * prefix;

    if (!(cmd = getArg(cmd, end, &prefix))) {
	printf("mkdevices: path expected\n");
	return 1;
    }

    if (cmd < end) {
	printf("mkdevices: unexpected arguments\n");
	return 1;
    }

    if ((fd = open("/proc/partitions", O_RDONLY)) < 0) {
	printf("mkrootdev: failed to open /proc/partitions: %d\n", errno);
	return 1;
    }

    i = read(fd, buf, sizeof(buf));
    if (i < 1) {
	close(fd);
	printf("failed to read /proc/partitions: %d\n", errno);
	return 1;
    }
    buf[i] = '\0';
    close(fd);

    start = strchr(buf, '\n');
    if (start) {
	start++;
	start = strchr(buf, '\n');
    }
    if (!start) return 1;

    start = start + 1;
    while (*start) {
	while (*start && isspace(*start)) start++;
	major = strtol(start, &chptr, 10);

	if (start != chptr) {
	    start = chptr;
	    while (*start && isspace(*start)) start++;
	    minor = strtol(start, &chptr, 10);

	    if (start != chptr) {
		start = chptr;
		while (*start && isspace(*start)) start++;
		while (*start && !isspace(*start)) start++;
		while (*start && isspace(*start)) start++;

		if (*start) {

		    chptr = start;
		    while (!isspace(*chptr)) chptr++;
		    old = *chptr;
		    *chptr = '\0';

		    if (testing) {
			printf("% 3d % 3d %s\n", major, minor, start);
		    } else {
			char * ptr, * deviceDir;
			int i;

			sprintf(devName, "%s/%s", prefix, start);
			unlink(devName);

			ptr = devName;
			i = 0;
			while (*ptr)
			    if (*ptr++ == '/')
				i++;
			if (i > 2) {
			    deviceDir = alloca(strlen(devName) + 1);
			    strcpy(deviceDir, devName);
			    ptr = deviceDir + (strlen(devName) - 1);
			    while (*ptr != '/')
				*ptr-- = '\0';
			    if (access(deviceDir, X_OK) && mkdir(deviceDir, 0644)) {
				printf("mkdir: cannot create directory %s: %d\n", deviceDir, errno);
			    }
			}
			if (smartmknod(devName, S_IFBLK | 0600, 
				  makedev(major, minor))) {
			    printf("failed to create %s\n", devName);
			}
		    }

		    *chptr = old;
		    start = chptr;
		}

	    }
	}

	start = strchr(start, '\n');
	if (!*start) return 1;
	start = start + 1;
    }

    return 0;
}

int runStartup(int fd) {
    char contents[32768];
    int i;
    char * start, * end;
    char * chptr;
    int rc;

    i = read(fd, contents, sizeof(contents) - 1);
    if (i == (sizeof(contents) - 1)) {
	printf("Failed to read /startup.rc -- file too large.\n");
	return 1;
    }

    contents[i] = '\0';

    start = contents;
    while (*start) {
	while (isspace(*start) && *start && (*start != '\n')) start++;

	if (*start == '#')
	    while (*start && (*start != '\n')) start++;

	if (*start == '\n') {
	    start++;
	    continue;
	}

	if (!*start) {
	    printf("(last line in /startup.rc is empty)\n");
	    continue;
	}

	/* start points to the beginning of the command */
	end = start + 1;
	while (*end && (*end != '\n')) end++;
	if (!*end) {
	    printf("(last line in /startup.rc missing \\n -- skipping)\n");
	    start = end;
	    continue;
	}

	/* end points to the \n at the end of the command */

	chptr = start;
	while (chptr < end && !isspace(*chptr)) chptr++;

	if (!strncmp(start, "mount", MAX(5, chptr - start)))
	    rc = mountCommand(chptr, end);
	else if (!strncmp(start, "losetup", MAX(7, chptr - start)))
	    rc = losetupCommand(chptr, end);
	else if (!strncmp(start, "echo", MAX(4, chptr - start)))
	    rc = echoCommand(chptr, end);
	else if (!strncmp(start, "raidautorun", MAX(11, chptr - start)))
	    rc = raidautorunCommand(chptr, end);
	else if (!strncmp(start, "pivot_root", MAX(10, chptr - start)))
	    rc = pivotrootCommand(chptr, end);
	else if (!strncmp(start, "mkrootdev", MAX(9, chptr - start)))
	    rc = mkrootdevCommand(chptr, end);
	else if (!strncmp(start, "umount", MAX(6, chptr - start)))
	    rc = umountCommand(chptr, end);
	else if (!strncmp(start, "exec", MAX(4, chptr - start)))
	    rc = execCommand(chptr, end);
	else if (!strncmp(start, "mkdir", MAX(5, chptr - start)))
	    rc = mkdirCommand(chptr, end);
	else if (!strncmp(start, "access", MAX(6, chptr - start)))
	    rc = accessCommand(chptr, end);
	else if (!strncmp(start, "find", MAX(4, chptr - start)))
	    rc = findCommand(chptr, end);
	else if (!strncmp(start, "findlodev", MAX(7, chptr - start)))
	    rc = findlodevCommand(chptr, end);
	else if (!strncmp(start, "showlabels", MAX(10, chptr-start)))
	    rc = display_uuid_cache();
	else if (!strncmp(start, "mkdevices", MAX(9, chptr-start)))
	    rc = mkdevicesCommand(chptr, end);
	else if (!strncmp(start, "sleep", MAX(5, chptr-start)))
	    rc = sleepCommand(chptr, end);
	else if (!strncmp(start, "mknod", MAX(5, chptr-start)))
	    rc = mknodCommand(chptr, end);
        else if (!strncmp(start, "readlink", MAX(8, chptr-start)))
            rc = readlinkCommand(chptr, end);
	else {
	    *chptr = '\0';
	    rc = otherCommand(start, chptr + 1, end, 1);
	}

	start = end + 1;
    }

    return rc;
}

int main(int argc, char **argv) {
    int fd = 0;
    char * name;
    int rc;
    int force = 0;

    name = strrchr(argv[0], '/');
    if (!name) 
	name = argv[0];
    else
	name++;

    if (!strcmp(name, "modprobe"))
	exit(0);

    testing = (getppid() != 0) && (getppid() != 1);
    argv++, argc--;

    while (argc && **argv == '-') {
	if (!strcmp(*argv, "--force")) {
	    force = 1;
	    argv++, argc--;
	    testing = 0;
	} else if (!strcmp(*argv, "--quiet")) {
	    quiet = 1;
	    argv++, argc--;
	} else {
	    printf("unknown argument %s\n", *argv);
	    return 1;
	}
    }

    if (force && !quiet)
	printf("(forcing normal run)\n");

    if (testing && !quiet)
	printf("(running in test mode).\n");

    if (!quiet) printf("Red Hat nash version %s starting\n", VERSION);

    if (*argv) {
	fd = open(*argv, O_RDONLY, 0);
	if (fd < 0) {
	    printf("nash: cannot open %s: %d\n", *argv, errno);
	    exit(1);
	}
    }

    rc = runStartup(fd);
    close(fd);

    return rc;
}
