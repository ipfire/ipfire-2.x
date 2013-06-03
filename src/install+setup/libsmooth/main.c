/* SmoothWall libsmooth.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Contains library functions.
 * 
 * $Id: main.c,v 1.6.2.9 2005/12/09 22:31:41 franck78 Exp $
 * 
 */
 
#include "libsmooth.h"

extern FILE *flog;
extern char *mylog;

extern char **ctr;
  
/* reboot().  reboots. */
void reboot(void)
{
	mysystem("/etc/halt");
}

/* stripnl().  Replaces \n with \0 */
void stripnl(char *s)
{
	char *t = strchr(s, '\n');
	if (t) *t = '\0';
}

/* Little wrapper. */
int mysystem(char *command)
{
	char mycommand[STRING_SIZE];
	
	snprintf(mycommand, STRING_SIZE, "%s >>%s 2>>%s", command, mylog, mylog);
	fprintf(flog, "Running command: %s\n", command);
	return system(mycommand);
}

void errorbox(char *message)
{
	newtWinMessage(ctr[TR_ERROR], ctr[TR_OK], message);
}

int scrollmsgbox(int width, int height, char *title, char *text, ...)
{
	int rc = 0;
	newtComponent t, f, b, c;
	char *buf = NULL;
	char checkbox;
	int size = 0;
	int i = 0;
	va_list args;

	va_start(args, text);

	do {
		size += 40000;
		if (buf) free(buf);
		buf = malloc(size);
		i = vsnprintf(buf, size, text, args);
	} while (i == size);

	va_end(args);

	newtCenteredWindow(width, height, title);

	b = newtCompactButton(width - 15 ,height - 2, ctr[TR_OK]);
	c = newtCheckbox(3, height - 2, ctr[TR_LICENSE_ACCEPT], ' ', " *", &checkbox);

	t = newtTextbox(1, 1, width - 2, height - 4, NEWT_TEXTBOX_WRAP+NEWT_TEXTBOX_SCROLL);
	newtTextboxSetText(t, buf);

	f = newtForm(NULL, NULL, 0);
	free(buf);

	newtFormAddComponent(f, c);
	newtFormAddComponent(f, b);
	newtFormAddComponent(f, t);

	newtRunForm(f);
	if (checkbox=='*') rc=1;
	newtFormDestroy(f);
	return rc;
}

int disclaimerbox(char *message)
{
	int rc;
	char title[STRING_SIZE];
	
	sprintf (title, "%s v%s - %s", NAME, VERSION, SLOGAN);
	rc = scrollmsgbox(75, 20, title, message);
	newtPopWindow();
	
	return rc;
}


void statuswindow(int width, int height, char *title, char *text, ...)
{
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

int runcommandwithstatus(char *command, char *message)
{
	int rc;
	char title[STRING_SIZE];
	
	sprintf (title, "%s v%s - %s", NAME, VERSION, SLOGAN);
	statuswindow(60, 4, title, message);
	rc = mysystem(command);
	newtPopWindow();
	
	return rc;
}

int runhiddencommandwithstatus(char *command, char *message)
{
	int rc;
	char title[STRING_SIZE];
	char mycommand[STRING_SIZE];
	
	sprintf (title, "%s v%s - %s", NAME, VERSION, SLOGAN);
	statuswindow(60, 4, title, message);
	snprintf(mycommand, STRING_SIZE, "%s >>%s 2>>%s", command, mylog, mylog);
	fprintf(flog, "Running command: ***** HIDDEN *****\n");
	rc = system(mycommand);
	newtPopWindow();
	
	return rc;
}

/* This one borrowed from redhat installer. */
int runcommandwithprogress(int width, int height, char *title, char *command,
	int lines, char *text, ...)
{
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
	
	snprintf(mycommand, STRING_SIZE, "%s 2>>%s", command, mylog);
	fprintf(flog, "Running command: %s\n", command);
	
	if (!(p = popen(command, "r")))
	{
		rc = 1;
		goto EXIT;
	}
	setvbuf(p, NULL, _IOLBF, 255);
	
	while (fgets(buffer, STRING_SIZE, p))
	{
		newtScaleSet(s, ++progress);
		newtRefresh();	
		fprintf(flog, "%s", buffer);
	}
		
	rc = pclose(p);
	
EXIT:
	newtFormDestroy(f);
	newtPopWindow();
		
	return rc;
}

int checkformodule(char *module)
{
	FILE *file;
	char buffer[STRING_SIZE];
	int result = 0;
	
	if (!(file = fopen("/proc/modules", "r")))
	{
		fprintf(flog, "Unable to open /proc/modules in checkformodule()\n");
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

int replace(char filename1[], char *from, char *to)
{
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

/* Include enabled languages */
#ifdef  LANG_EN_ONLY
        #include "lang_en.c"
#else
	#include "lang_de.c"
	#include "lang_en.c"
	#include "lang_es.c"
	#include "lang_fr.c"
	#include "lang_pl.c"
	#include "lang_ru.c"
	#include "lang_nl.c"
	#include "lang_tr.c"
#endif

// returns a pointer to the actual running version number of IPFire.
// Successive updates increase effective version but not VERSION !
char g_title[STRING_SIZE] = "";
char* get_version(void) {
	FILE *f_title;
	if ((f_title = fopen ("/etc/issue", "r"))) {
		fgets (g_title, STRING_SIZE, f_title);
		fclose (f_title);
		if (g_title[strlen(g_title) - 1] == '\n') g_title[strlen(g_title) - 1] = '\0';
	} else {
	        sprintf (g_title, "%s %s - %s", NAME, VERSION, SLOGAN);
	}
	return g_title;
}
