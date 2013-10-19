/* SmoothWall setup program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Contains main entry point, and misc functions.
 *
 */

#include "setup.h"

FILE *flog = NULL;
char *mylog;

char **ctr = NULL;

int automode = 0;

struct  nic  nics[20] = { { "" , "" , "" , "" } };
struct knic knics[20] = { { "" , "" , "" , "" } };

extern char *en_tr[];
extern char *de_tr[];
extern char *fr_tr[];
extern char *es_tr[];
extern char *pl_tr[];
extern char *ru_tr[];
extern char *nl_tr[];
extern char *tr_tr[];

int main(int argc, char *argv[])
{
#ifdef  LANG_EN_ONLY
	char *shortlangnames[] = { "en", NULL };
	char **langtrs[] = { en_tr, NULL };
#else
	char *shortlangnames[] = { "de", "en", "fr", "es", "nl", "pl", "ru", "tr", NULL };
	char **langtrs[] = { de_tr, en_tr, fr_tr, es_tr, nl_tr, pl_tr, ru_tr, tr_tr, NULL };
#endif
	int choice;
	char *sections[11]; /* need to fill this out AFTER knowning lang */
	int rc;
	struct keyvalue *kv;
	char selectedshortlang[STRING_SIZE] = "en";
	char title[STRING_SIZE];
	int langcounter;
	int autook = 0;

	/* Log file/terminal stuff. */
	if (argc >= 2)
		mylog = argv[1];
	else
		mylog = strdup("/var/log/setup.log");

	if (!(flog = fopen(mylog, "w+")))
	{
		printf("Couldn't open log terminal\n");
		return 1;
	}

	if (argc >= 3)
		automode = 1;

	fprintf(flog, "Setup program started.\n");

	if (!setlocale(LC_CTYPE,""))
		fprintf(flog, "Locale not spezified. Check LANG, LC_CTYPE, RC_ALL.");

	kv = initkeyvalues();
	if (!(readkeyvalues(kv, CONFIG_ROOT "/main/settings")))
	{
		printf("%s is not properly installed.\n", NAME);
		return 1;
	}
	findkey(kv, "LANGUAGE", selectedshortlang);

	for (langcounter = 0; langtrs[langcounter]; langcounter++)
	{
		if (strcmp(selectedshortlang, shortlangnames[langcounter]) == 0)
		{
			ctr = langtrs[langcounter];
			break;
		}
	}

	if (!ctr)
	{
		for (choice = 0; shortlangnames[choice]; choice++)
		{
			if (strcmp(shortlangnames[choice], "en") == 0)
				break;
		}
		if (!shortlangnames[choice])
			goto EXIT;
		ctr = langtrs[choice];
	}

	sections[0] = ctr[TR_KEYBOARD_MAPPING];
	sections[1] = ctr[TR_TIMEZONE];
	sections[2] = ctr[TR_HOSTNAME];
	sections[3] = ctr[TR_DOMAINNAME];
	sections[4] = ctr[TR_NETWORKING];
	sections[5] = ctr[TR_ISDN];
	sections[6] = ctr[TR_ROOT_PASSWORD];
	sections[7] = ctr[TR_ADMIN_PASSWORD];
	sections[8] = NULL;

	newtInit();
	newtCls();
	FILE *f_title;
	if ((f_title = fopen ("/etc/issue", "r")))
	{
	    fgets (title, STRING_SIZE, f_title);
	    if (title[strlen(title) - 1] == '\n')
		title[strlen(title) - 1] = '\0';
	    fclose (f_title);
	} else {
	    sprintf (title, "%s %s - %s", NAME, VERSION, SLOGAN);
	}
	newtDrawRootText(14, 0, title);
	newtPushHelpLine(ctr[TR_HELPLINE]);		

	if (automode == 0)
	{
		choice = 0;
		for (;;)
		{
			rc = newtWinMenu(ctr[TR_SECTION_MENU],
				ctr[TR_SELECT_THE_ITEM], 50, 5, 5, 11,
				sections, &choice, ctr[TR_OK], ctr[TR_QUIT], NULL);

			if (rc == 2)
				break;

			switch (choice)
			{
				case 0:
					handlekeymap();
					break;

				case 1:
					handletimezone();
					break;

				case 2:
					handlehostname();
					break;

				case 3:
					handledomainname();
					break;

				case 4:
					handlenetworking();
					break;
				
				case 5:
					handleisdn();
					break;

				case 6:
					handlerootpassword();
					break;
					
				case 7:
					handleadminpassword();
					break;
		
				default:
					break;
			}
		}
	}
	else
	{
		if (!(handlekeymap()))
			goto EXIT;
		if (!(handletimezone()))
			goto EXIT;
		if (!(handlehostname()))
			goto EXIT;
		if (!(handledomainname()))
			goto EXIT;
		if (!(handlerootpassword()))
			goto EXIT;
		if (!(handleadminpassword()))
			goto EXIT;
		if (!(handleisdn()))
			goto EXIT;
		if (!(handlenetworking()))
			goto EXIT;
		if (!(handledhcp()))
			goto EXIT;

		autook = 1;
	}

EXIT:	
	if (automode != 0)
	{
		sprintf (title, "%s %s - %s", NAME, VERSION, SLOGAN);
		if (autook)
			newtWinMessage(title, ctr[TR_OK], ctr[TR_SETUP_FINISHED]);
		else
		{
			newtWinMessage(ctr[TR_WARNING], ctr[TR_OK], ctr[TR_SETUP_NOT_COMPLETE]);

			fprintf(flog, "Setup program has not finished.\n");
			fflush(flog);
			fclose(flog);

			newtFinished();

			return 1;
		}
	}

	fprintf(flog, "Setup program ended.\n");
	fflush(flog);
	fclose(flog);

	newtFinished();

	return 0;
}
