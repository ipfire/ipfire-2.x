/* SmoothWall setup program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Contains main entry point, and misc functions.
 * 
 * modified 16/11/2002 eoberlander - French language added
 *
 * $Id: main.c,v 1.4.2.7 2005/12/01 20:13:08 eoberlander Exp $
 * 
 */

#include "setup.h"

FILE *flog = NULL;
char *mylog;

char **ctr = NULL;

int automode = 0;

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
extern char *sk_tr[];
extern char *so_tr[];
extern char *sv_tr[];
extern char *no_tr[];
extern char *pl_tr[];
extern char *pt_tr[];
extern char *vi_tr[];

int main(int argc, char *argv[])
{
#ifdef  LANG_EN_ONLY
	char *shortlangnames[] = { "en", NULL };
	char **langtrs[] = { en_tr, NULL };
#elifdef LANG_ALL
	char *shortlangnames[] = { "bz", "cs", "da", "de", "en", "es", "fr", "el", "it", "la", "hu", "nl", "no", "pl", "pt", "sk", "so", "fi", "sv", "tr", "vi", NULL };
	char **langtrs[] = { bz_tr, cs_tr, da_tr, de_tr, en_tr, es_tr, fr_tr, el_tr, it_tr, la_tr, hu_tr, nl_tr, no_tr, pl_tr, pt_tr, sk_tr, so_tr, fi_tr, sv_tr, tr_tr, vi_tr, NULL };
#else
	char *shortlangnames[] = { "de", "en", NULL };
	char **langtrs[] = { de_tr, en_tr, NULL };
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
		mylog = strdup("/root/setup.log");

	if (!(flog = fopen(mylog, "w+")))
	{
		printf("Couldn't open log terminal\n");
		return 1;
	}
	
	if (argc >= 3)
		automode = 1;
	
	fprintf(flog, "Setup program started.\n");
		
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
		/* zh,lt,ro,ru,th languages not available in setup, so use English */
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
	sections[4] = ctr[TR_ISDN_CONFIGURATION];
	sections[5] = ctr[TR_NETWORKING];	
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
	    sprintf (title, "%s v%s - %s", NAME, VERSION, SLOGAN);
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
					handleisdn();
					break;

				case 5:
					handlenetworking();
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
		if (!(handleisdn()))
			goto EXIT;
		if (!(handlenetworking()))
			goto EXIT;
		if (!(handledhcp()))
			goto EXIT;
		if (!(handlerootpassword()))
			goto EXIT;
		if (!(handleadminpassword()))
			goto EXIT;

		autook = 1;
	}

EXIT:	
	if (automode != 0)
	{
		sprintf (title, "%s v%s - %s", NAME, VERSION, SLOGAN);
		if (autook)
			newtWinMessage(title, ctr[TR_OK], ctr[TR_SETUP_FINISHED]);
		else
			newtWinMessage(ctr[TR_WARNING], ctr[TR_OK], ctr[TR_SETUP_NOT_COMPLETE]);
	}
	
	fprintf(flog, "Setup program ended.\n");
	fflush(flog);
	fclose(flog);
		
	newtFinished();

	return 0;
}

