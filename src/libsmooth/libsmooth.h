/* SmoothWall libsmooth.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Contains prototypes for library functions.
 *
 */

#ifndef ___LIBSMOOTH_H
#define ___LIBSMOOTH_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <wchar.h>
#include <locale.h>
#include <unistd.h>
#include <sys/file.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <newt.h>
#include <dirent.h>
#include <sys/mount.h>

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include <linux/cdrom.h>
#include <sys/ioctl.h>

#define STRING_SIZE 1024

struct keyvalue {
 	char key[STRING_SIZE];
 	char value[STRING_SIZE];
 	struct keyvalue *next;
};

/* libsmooth.c */
void stripnl(char *s);
int mysystem(const char* output, const char *command);
void errorbox(char *message);
int statuswindowscroll(int width, int height, const char *title, const char *text, ...);
int disclaimerbox(char *message);
void statuswindow(int width, int height, const char *title, const char *text, ...);
int runcommandwithprogress(int width, int height, const char *title, const char *command,
	int lines, char *text, ...);
int runcommandwithstatus(const char *command, const char* title, const char *message, const char* output);
int runhiddencommandwithstatus(const char *command, const char* title, const char *message, const char* output);
int splashWindow(const char* title, const char* message, unsigned int timeout);
int checkformodule(const char *module);
int replace(char filename1[], char *from, char *to);
char* get_version(void);

/* varval.c */
struct keyvalue *initkeyvalues(void);
void freekeyvalues(struct keyvalue *head);
int readkeyvalues(struct keyvalue *head, char *filename);
int writekeyvalues(struct keyvalue *head, char *filename);
int findkey(struct keyvalue *head, char *key, char *value);
void appendkeyvalue(struct keyvalue *head, char *key, char *value);
void replacekeyvalue(struct keyvalue *head, char *key, char *value);

#endif
