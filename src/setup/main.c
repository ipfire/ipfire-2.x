/* SmoothWall setup program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Contains main entry point, and misc functions.
 *
 */

// Translation
#include <libintl.h>
#define _(x) dgettext("setup", x)

#include "setup.h"

FILE *flog = NULL;
char *mylog;

int automode = 0;

struct  nic  nics[20] = { { "" , "" , "" , "" } };
struct knic knics[20] = { { "" , "" , "" , "" } };

int main(int argc, char *argv[])
{
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

#if 0
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
#endif

	sections[0] = _("Keyboard mapping");
	sections[1] = _("Timezone");
	sections[2] = _("Hostname");
	sections[3] = _("Domain name");
	sections[4] = _("Networking");
	sections[5] = _("ISDN");
	sections[6] = _("'root' password");
	sections[7] = _("'admin' password");
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
	    sprintf (title, "%s - %s", NAME, SLOGAN);
	}
	newtDrawRootText(14, 0, title);
	newtPushHelpLine(_("              <Tab>/<Alt-Tab> between elements   |  <Space> selects"));		

	if (automode == 0)
	{
		choice = 0;
		for (;;)
		{
			rc = newtWinMenu(_("Section menu"),
				_("Select the item you wish to configure."), 50, 5, 5, 11,
				sections, &choice, _("OK"), _("Quit"), NULL);

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
		sprintf (title, "%s - %s", NAME, SLOGAN);
		if (autook)
			newtWinMessage(title, _("OK"), _("Setup is complete."));
		else {
			newtWinMessage(_("Warning"), _("OK"),
				_("Initial setup was not entirely complete. "
				"You must ensure that Setup is properly finished by running "
				"setup again at the shell."));

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
