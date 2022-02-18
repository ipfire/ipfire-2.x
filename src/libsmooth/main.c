/* SmoothWall libsmooth.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Contains library functions.
 */

#include "libsmooth.h"

#include <libintl.h>
#define _(x) dgettext("libsmooth", x)

/* stripnl().  Replaces \n with \0 */
void stripnl(char *s) {
	char *t = strchr(s, '\n');
	if (t)
		*t = '\0';
}

/* Little wrapper. */
int mysystem(const char* output, const char *command) {
	char mycommand[STRING_SIZE];

	if (output == NULL)
		output = "/dev/null";

	snprintf(mycommand, sizeof(mycommand), "%s >>%s 2>&1", command, output);

	FILE* f = fopen(output, "w+");
	fprintf(f, "Running command: %s\n", command);
	fclose(f);

	return system(mycommand);
}

void errorbox(char *message) {
	newtWinMessage(_("Error"), _("OK"), message);
}

void statuswindow(int width, int height, const char *title, const char *text, ...) {
	newtComponent t, f;
	char *buf = NULL;
	int size = 0;
	int i = 0;
	va_list args;

	va_start(args, text);

	do {
		size += 1000;
		if (buf) free(buf);
		buf = malloc(size);
		i = vsnprintf(buf, size, text, args);
	} while (i == size);

	va_end(args);

	newtCenteredWindow(width, height, title);

	t = newtTextbox(1, 1, width - 2, height - 2, NEWT_TEXTBOX_WRAP);
	newtTextboxSetText(t, buf);
	f = newtForm(NULL, NULL, 0);

	free(buf);

	newtFormAddComponent(f, t);

	newtDrawForm(f);
	newtRefresh();
	newtFormDestroy(f);
}

int runcommandwithstatus(const char *command, const char* title, const char *message, const char* output) {
	statuswindow(60, 4, title, message);

	int rc = mysystem(output, command);
	newtPopWindow();

	return rc;
}

int runhiddencommandwithstatus(const char *command, const char* title, const char *message, const char* output) {
	statuswindow(60, 4, title, message);

	int rc = mysystem(output, command);
	newtPopWindow();

	return rc;
}

int splashWindow(const char* title, const char* message, unsigned int timeout) {
	statuswindow(60, 4, title, message);

	// Wait so the user can read this message
	sleep(timeout);
	newtPopWindow();

	return 0;
}

/* This one borrowed from redhat installer. */
int runcommandwithprogress(int width, int height, const char *title, const char *command,
	int lines, char *text, ...) {
	newtComponent t, f, s;
	char *buf = NULL;
	int size = 0;
	int i = 0;
	va_list args;
	int rc = 0;
	FILE *p;
	char buffer[STRING_SIZE];
	int progress = 0;
	char mycommand[STRING_SIZE];

	va_start(args, text);

	do {
		size += 1000;
		if (buf) free(buf);
		buf = malloc(size);
		i = vsnprintf(buf, size, text, args);
	} while (i == size);

	va_end(args);

	newtCenteredWindow(width, height, title);

	t = newtTextbox(1, 1, width - 2, height - 2, NEWT_TEXTBOX_WRAP);
	newtTextboxSetText(t, buf);
	f = newtForm(NULL, NULL, 0);

	free(buf);

	newtFormAddComponent(f, t);

	s = newtScale(1, 3, width - 2, lines);
	newtScaleSet(s, progress);

	newtFormAddComponent(f, s);

	newtDrawForm(f);
	newtRefresh();

	if (!(p = popen(command, "r")))
	{
		rc = 1;
		goto EXIT;
	}
	setvbuf(p, NULL, _IOLBF, 255);

	while (fgets(buffer, STRING_SIZE, p)) {
		newtScaleSet(s, ++progress);
		newtRefresh();
	}

	rc = pclose(p);

EXIT:
	newtFormDestroy(f);
	newtPopWindow();

	return rc;
}

int checkformodule(const char *module) {
	FILE *file;
	char buffer[STRING_SIZE];
	int result = 0;

	if (!(file = fopen("/proc/modules", "r")))
	{
		fprintf(stderr, "Unable to open /proc/modules in checkformodule()\n");
		return 0;
	}

	while (fgets(buffer, STRING_SIZE, file))
	{
		if (strncmp(buffer, module, strlen(module)) == 0)
		{
			if (buffer[strlen(module)] == ' ')
			{
				result = 1;
				goto EXIT;
			}
		}
	}

EXIT:
	fclose(file);

	return result;
}

int _replace_string(char string[], char *from, char *to)
{
	int fromlen = strlen(from);
	int tolen = strlen(to);
	char *start, *p1, *p2;
	for(start = string; *start != '\0'; start++)
	{
		p1 = from;
		p2 = start;
		while(*p1 != '\0')
		{
			if(*p1 != *p2)
				break;
			p1++;
			p2++;
		}
		if(*p1 == '\0')
		{
			if(fromlen != tolen)
			{
				memmove(start + tolen, start + fromlen,
					strlen(start + fromlen) + 1);
			}
			for(p1 = to; *p1 != '\0'; p1++)
				*start++ = *p1;
			return 1;
		}
	}
	return 0;
}

int replace(char filename1[], char *from, char *to) {
	FILE *file1, *file2;
	char filename2[1000];
	char temp[1000];
	int ret = 0;

	/* Open the source and destination files */
	strcpy (filename2, filename1);
	strcat (filename2, ".new");
	if (!(file1 = fopen (filename1, "r"))) return 1;
	if (!(file2 = fopen (filename2, "w"))) {
		fclose(file1);
		return -1;
	}

	/* Start reading in lines */
	while (fgets (temp, 1000, file1) != NULL) {
		if (strlen(to) > 0) {
			/* Replace string */
			ret = _replace_string (temp, from, to);

			/* Write string to new file */
			fputs(temp, file2);
		} else {
			/* Remove string when to is NULL */
			if (!strstr(temp, from))
				fputs(temp, file2);
		}
	}

	/* Close source and destination */
	fclose (file1);
	fclose (file2);

	/* Move the file */
	rename (filename2, filename1);

	return (ret);
}

// returns a pointer to the actual running version number of IPFire.
// Successive updates increase effective version but not VERSION !
char g_title[STRING_SIZE] = "";
char* get_version(void) {
	FILE *f_title;
	if ((f_title = fopen ("/etc/issue", "r"))) {
		fgets (g_title, STRING_SIZE, f_title);
		fclose (f_title);
		if (g_title[strlen(g_title) - 1] == '\n') g_title[strlen(g_title) - 1] = '\0';
	}
	return g_title;
}
