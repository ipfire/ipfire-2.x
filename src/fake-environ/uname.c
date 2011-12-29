

#include <stdio.h>
#include <string.h>
#include <dlfcn.h>
#include <stdlib.h>		/* for EXIT_FAILURE */
#include <unistd.h>		/* for _exit() */
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/syslog.h>
#include <sys/utsname.h>

#ifndef RTLD_NEXT
#define RTLD_NEXT      ((void *) -1l)
#endif

typedef int (*uname_t)(struct utsname * buf);

static void *get_libc_func(const char *funcname) {
	char *error;

	void *func = dlsym(RTLD_NEXT, funcname);
	if ((error = dlerror()) != NULL) {
		fprintf(stderr, "I can't locate libc function `%s' error: %s", funcname, error);
		_exit(EXIT_FAILURE);
	}

	return func;
}

int uname(struct utsname *buf) {
	char *env = NULL;

	/* Call real uname to get the information we need. */
	uname_t real_uname = (uname_t)get_libc_func("uname");
	int ret = real_uname((struct utsname *) buf);

	/* Replace release if requested. */
	if ((env = getenv("UTS_RELEASE")) != NULL) {
		strncpy(buf->release, env, _UTSNAME_RELEASE_LENGTH);
	}

	/* Replace machine type if requested. */
	if ((env = getenv("UTS_MACHINE")) != NULL) {
		strncpy(buf->machine, env, _UTSNAME_MACHINE_LENGTH);
	}

	return ret;
}
