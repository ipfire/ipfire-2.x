#include <newt.h>       /* Fenster */
#include <stdio.h>      /* File IO */
#include <stdlib.h>     /* exit() */
#include <string.h>     /* Strings */

#define STRING_SIZE  256

#define KNOWN_NICS   "/var/ipfire/ethernet/known_nics"
#define SCANNED_NICS "/tmp/scanned_nics"

struct nic
{
       char description[256];
       char macaddr[20];
};

struct knic
{
       char macaddr[20];
};

int write_configs_netudev(char *macaddr, char *colour) {
	
	#define UDEV_NET_CONF "/etc/udev/rules.d/30-persistent-network.rules"
	
	FILE *fp;
	char commandstring[STRING_SIZE];
	
	if( (fp = fopen(KNOWN_NICS, "a")) == NULL )
	{
		fprintf(stderr,"Couldn't open "KNOWN_NICS);
		return 1;
	}
	fprintf(fp,"%s;\n", macaddr);
	fclose(fp);

	// Make sure that there is no conflict
	snprintf(commandstring, STRING_SIZE, "/usr/bin/touch "UDEV_NET_CONF" >/dev/null 2>&1");
  system(commandstring);
  snprintf(commandstring, STRING_SIZE, "/bin/cat "UDEV_NET_CONF"| /bin/grep -v \"%s\" > "UDEV_NET_CONF" 2>/dev/null", macaddr);
  system(commandstring);
  snprintf(commandstring, STRING_SIZE, "/bin/cat "UDEV_NET_CONF"| /bin/grep -v \"%s\" > "UDEV_NET_CONF" 2>/dev/null", colour);
	system(commandstring);

	if( (fp = fopen(UDEV_NET_CONF, "a")) == NULL )
	{
		fprintf(stderr,"Couldn't open" UDEV_NET_CONF);
		return 1;
	}
	fprintf(fp,"ACTION==\"add\", SUBSYSTEM==\"net\", SYSFS{address}==\"%s\", NAME=\"%s0\"\n", macaddr, colour);
	fclose(fp);	
	
	return 0;
}

int main(void)
{
			FILE *fp;
			char temp_line[STRING_SIZE];
			struct nic nics[20], *pnics;
			pnics = nics;
			struct knic knics[20], *pknics;
			pknics = knics;
			int rc, choise, count = 0, kcount = 0, i, found;
			char macaddr[STRING_SIZE], description[STRING_SIZE];
			char message[STRING_SIZE];

			char MenuInhalt[20][80];
			char *pMenuInhalt[20];

			newtComponent form;
			
			// Read the nics we already use
			if( (fp = fopen(KNOWN_NICS, "r")) == NULL )
			{
				fprintf(stderr,"Couldn't open " KNOWN_NICS);
				return 1;
			}
			
			while ( fgets(temp_line, STRING_SIZE, fp) != NULL)
			{
				strcpy( knics[kcount].macaddr , strtok(temp_line,";") );
				if (strlen(knics[kcount].macaddr) > 5 ) kcount++;
			}
			fclose(fp);

			// Read our scanned nics
			if( (fp = fopen(SCANNED_NICS, "r")) == NULL )
			{
				fprintf(stderr,"Couldn't open "SCANNED_NICS);
				return 1;
			}
			while ( fgets(temp_line, STRING_SIZE, fp) != NULL)
			{
				strcpy(description, strtok(temp_line,";") );
				strcpy(macaddr,     strtok(NULL,";") );
				found = 0;
				if (strlen(macaddr) > 5 ) {
					for (i=0; i < kcount; i++)
					{
						// Check if the nic is already in use
						if (strcmp(pknics[i].macaddr, macaddr) == NULL )
						{
							found = 1;
						}
					}
					if (!found)
					{
						strcpy( pnics[count].description , description );
						strcpy( pnics[count].macaddr , macaddr );
						count++;
					}
				}
			}
			fclose(fp);
			
			// If new nics are found...
			if (count > 0) {
				newtInit();
				newtCls();
	
				char cMenuInhalt[STRING_SIZE];
				for (i=0 ; i < count ; i++)
				{
					if ( strlen(nics[i].description) < 52 )
						strncpy(MenuInhalt[i], nics[i].description + 1, strlen(nics[i].description)- 2);
					else
					{
						strncpy(cMenuInhalt, nics[i].description + 1, 50);
						strncpy(MenuInhalt[i], cMenuInhalt,(strrchr(cMenuInhalt,' ') - cMenuInhalt));
						strcat (MenuInhalt[i], "...");
					}
					while ( strlen(MenuInhalt[i]) < 50)
						// Fill with space.
						strcat( MenuInhalt[i], " ");
	
					strcat(MenuInhalt[i], " (");
					strcat(MenuInhalt[i], nics[i].macaddr);
					strcat(MenuInhalt[i], ")");
					pMenuInhalt[i] = MenuInhalt[i];
				}
	       
				form = newtForm(NULL, NULL, 0);
				
				sprintf(message, "Es wurde(n) %d Netzwerkkarte(n)\nin Ihrem System gefunden.\nBitte waehlen Sie eine aus:\n", count);
	
				rc = newtWinMenu("NetcardMenu", message, 50, 5, 5, 6, pMenuInhalt, &choise, "OK", "Cancel", NULL);
	
				newtFormDestroy(form);
				newtFinished();
	
				if ( rc == 0 || rc == 1) {
					write_configs_netudev(pnics[choise].macaddr, "green");
	      } else {
					printf("BREAK\n");
					return 1;
				}
				return 0;
		} else {
			printf("Es wurden keine ungenutzen Netzwerkschnittstellen gefunden.\n");
			return 1;
		}
}
