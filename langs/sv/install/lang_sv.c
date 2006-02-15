/*
 * Swedish (sv) Data File
 *
 * This file is part of the IPCop Firewall.
 * 
 * IPCop is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * IPCop is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with IPCop; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
 * 
 * (c) The SmoothWall Team
 * 
 * IPCop translation
 * (c) 2003 Anders Johansson, Christer Jonson
 *  
 */
 
#include "libsmooth.h"

char *sv_tr[] = {

/* TR_ADDRESS_SETTINGS */
"Adressinställningar",
/* TR_ADMIN_PASSWORD */
"Admin lösenord",
/* TR_AGAIN_PROMPT */
"En gång till:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Alla kort har allokerats på ett korrekt sätt.",
/* TR_AUTODETECT */
"* AUTODETECT *",
/* TR_BUILDING_INITRD */
"Bygger INITRD....",
/* TR_CANCEL */
"Avbryt",
/* TR_CARD_ASSIGNMENT */
"Korttilldelning",
/* TR_CHECKING */
"Kontrollerar URL...",
/* TR_CHECKING_FOR */
"Letar efter: %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Välj det ISDN kort du har installerat i den här datorn.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Välj det ISDN protokoll du vill använda.",
/* TR_CONFIGURE_DHCP */
"Konfigurera DHCP-servern genom att skriva in konfigurationsinformationen.",
/* TR_CONFIGURE_NETWORKING */
"Konfigurera nätverket",
/* TR_CONFIGURE_NETWORKING_LONG */
"Nu skall du konfigurera nätverket genom att först ladda den rätta drivrutinen för det GRÖNA gränssnittet. Du kan göra det antingen genom att söka efter ett kort, eller genom att välja rätt drivrutin från en lista. Om du har mer än ett nätverkskort installerat så kommer du att kunna konfigurera dessa senare under installationen. Om du har mer än ett kort av samma typ som ditt GRÖNA gränssnitt och dessa behöver speciella parametrar till modulen så skall du välja parametrarna både för ditt GRÖNA kort och de andra på ett sådant sätt att alla  kort kan vara aktiva samtidigt.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Konfigurera nätverksdrivrutiner och vilket gränssnitt som respektive kort är tilldelat till. Den nuvarande konfigurationen är som följer:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"Konfigurera CDROM-läsaren genom att välja lämplig IO-adress och/eller IRQ.",
/* TR_CONGRATULATIONS */
"Gratulerar!",
/* TR_CONGRATULATIONS_LONG */
"%s installerade korrekt. Tag ut eventuella disketter eller CDROM från datorn. Installationsprogrammet kommer nu fortsätta med konfigurering av ISDN, nätverkskort och systemlösenord. När installationsprogrammet har avslutat så skall du peka din webläsare mot http://%s:81 eller https://%s:445 (eller vad du nu namngett din %s), och konfigurera uppringt nätverk (om det behövs) och yttre tillgång. Kom ihåg att sätta ett lösenord för %s \"dial\" användare om du vill att andra än %s 'admin' användare skall kunna koppla upp och koppla ner modemkopplingen.",
/* TR_CONTINUE_NO_SWAP */
"Din hårddisk är mycket liten men du kan fortsätta utan \"swap\". (används med försiktighet)",
/* TR_CURRENT_CONFIG */
"Nuvarande konfiguration: %s%s",
/* TR_DEFAULT_GATEWAY */
"Standard-Gateway:",
/* TR_DEFAULT_GATEWAY_CR */
"Standard-Gateway\n",
/* TR_DEFAULT_LEASE */
"Standard lånetid (minuter):",
/* TR_DEFAULT_LEASE_CR */
"Standard lånetid\n",
/* TR_DETECTED */
"Hittade en/ett: %s",
/* TR_DHCP_HOSTNAME */
"Dynamisk-IP datornamn:",
/* TR_DHCP_HOSTNAME_CR */
"Dynamisk-IP datornamn\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"Dynamisk-IP server konfiguration",
/* TR_DISABLED */
"Inaktiverad",
/* TR_DISABLE_ISDN */
"Inaktivera ISDN",
/* TR_DISK_TOO_SMALL */
"Din hårddisk är för liten.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"DNS och Gateway inställningar",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Skriv in DNS och gateway informationen. Dessa inställningar används endast om Dynamisk-IP är inaktiverad på det RÖDA gränssnittet.",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Din konfiguration använder sig inte av ett nätverkskort för det RÖDA gränssnittet.  DNS och Gateway information för uppringda användare konfigureras automatiskt vid uppringning.",
/* TR_DOMAINNAME */
"Domännamn",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Domännamnet kan inte utelämnas.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"Domännamn kan inte innehålla mellanslag",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Domännamnet får bara innehålla bokstäver, nummer, minus och punkt.",
/* TR_DOMAIN_NAME_SUFFIX */
"Domännamns suffix:",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Domännamns suffix\n",
/* TR_DONE */
"Klar",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\nVill du ändra de här inställningarna?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Drivrutiner och tilldelning av kort",
/* TR_ENABLED */
"Aktiverad",
/* TR_ENABLE_ISDN */
"Aktivera ISDN",
/* TR_END_ADDRESS */
"Slutadress:",
/* TR_END_ADDRESS_CR */
"Slutadress\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Vissa ISDN kort (speciellt ISA) kan behöva extra modulparametrar för att sätta IRQ och IO-adress information. Om du har ett sådant ISDN kort så kan du skriva in de parametrarna här. Till exempel: \"io=0x280 irq=9\". De kommer i så fall att användas vid detektering av kortet.",
/* TR_ENTER_ADMIN_PASSWORD */
"Skriv in lösenordet för %s admin.  Det här är användaren som används för att logga in på  %s web administrationssidor.",
/* TR_ENTER_DOMAINNAME */
"Ange domännamn",
/* TR_ENTER_HOSTNAME */
"Skriv in datorns namn.",
/* TR_ENTER_IP_ADDRESS_INFO */
"Skriv in IP-adressen",
/* TR_ENTER_NETWORK_DRIVER */
"Misslyckades att detektera nätverkskortet. Skriv in nätverkskortets drivrutin och dess eventuella parametrar.",
/* TR_ENTER_ROOT_PASSWORD */
"Skriv in lösenordet för 'root'. Logga in som 'root' för kommandoradsaccess.",
/* TR_ENTER_SETUP_PASSWORD */
"Skriv in lösenordet för 'setup'. Logga in som 'setup' för att komma åt installations programmet.",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Skriv in IP-adressen för %s gränssnittet.",
/* TR_ENTER_THE_LOCAL_MSN */
"Skriv in det lokala telefonnummret (MSN/EAZ).",
/* TR_ENTER_URL */
"Ange sökväg till ipcop-<version>.tgz och images/scsidrv-<version>.img. Obs, översättning av domännamn ej tillgängligt. Använd IP-adress (http://X.X.X.X/<directory>)",
/* TR_ERROR */
"Fel",
/* TR_ERROR_WRITING_CONFIG */
"Misslyckades skriva konfigurationsinformation.",
/* TR_EURO_EDSS1 */
"Euro (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Extraherar moduler...",
/* TR_FAILED_TO_FIND */
"Lyckades inte hitta en URL-fil.",
/* TR_FOUND_NIC */
"%s har detekterat följande nätverksgränssnitt i din maskin: %s",
/* TR_GERMAN_1TR6 */
"Tyskland 1TR6",
/* TR_HELPLINE */
"              <Tab>/<Alt-Tab> mellan element   |  <Mellanslag> väljer",
/* TR_HOSTNAME */
"Datornamn",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Datorns namn kan inte vara tomt.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"Datorns namn kan inte innehålla mellanslag.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"Namnet (\"Hostname\") får bara innehålla bokstäver, siffror och bindestreck",
/* TR_INITIALISING_ISDN */
"Initierar ISDN...",
/* TR_INSERT_CDROM */
"Sätt in %s CDn i CDROM-läsaren.",
/* TR_INSERT_FLOPPY */
"Sätt in %s drivrutinsdisketten floppy-läsaren.",
/* TR_INSTALLATION_CANCELED */
"Installationen avbruten.",
/* TR_INSTALLING_FILES */
"Installerar filer...",
/* TR_INSTALLING_GRUB */
"Installerar GRUB...",
/* TR_INTERFACE */
"%s gränssnittet",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"Gränssnittett startade inte.",
/* TR_INVALID_FIELDS */
"Följande fält är ogiltiga:\n\n",
/* TR_INVALID_IO */
"Vald IO-adress är inte giltig. ",
/* TR_INVALID_IRQ */
"Vald IRQ är inte giltig.",
/* TR_IP_ADDRESS_CR */
"IP-adress\n",
/* TR_IP_ADDRESS_PROMPT */
"IP-adress:",
/* TR_ISDN_CARD */
"ISDN kort",
/* TR_ISDN_CARD_NOT_DETECTED */
"ISDN kort kunde inte hittas. Du kan behöva ytterligare parameterar för att konfigurera modulen om kortet är av ISA typ eller har speciella behov.",
/* TR_ISDN_CARD_SELECTION */
"Val av ISDN kort",
/* TR_ISDN_CONFIGURATION */
"ISDN Konfiguration",
/* TR_ISDN_CONFIGURATION_MENU */
"ISDN konfigurations meny",
/* TR_ISDN_NOT_SETUP */
"ISDN är inte konfigurerad. Några delar har inte valts.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"ISDN har inte konfigurerats ännu. Välj vad du vill konfigurera.",
/* TR_ISDN_PROTOCOL_SELECTION */
"ISDN val av protokoll",
/* TR_ISDN_STATUS */
"ISDN är för tillfället %s.\n\n   Protokoll: %s\n   Kort: %s\n   Lokalt telefonnummer: %s\n\nVälj vad du vill omkonfigurera eller välj att använda nuvarande inställningar.",
/* TR_KEYBOARD_MAPPING */
"Tangentbordsinställning",
/* TR_KEYBOARD_MAPPING_LONG */
"Välj typen av tangentbord du har från listan nedan.",
/* TR_LEASED_LINE */
"Hyrd lina",
/* TR_LOADING_MODULE */
"Laddar modulen...",
/* TR_LOADING_PCMCIA */
"Laddar PCMCIA (PC-card) moduler...",
/* TR_LOOKING_FOR_NIC */
"Söker efter: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Skapar boot filsystemet...",
/* TR_MAKING_LOG_FILESYSTEM */
"Skapar log filsystemet...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Skapar root filsystemet...",
/* TR_MAKING_SWAPSPACE */
"Skapar swap utrymme...",
/* TR_MANUAL */
"* MANUELLT *",
/* TR_MAX_LEASE */
"Maximal lånetid (minuter):",
/* TR_MAX_LEASE_CR */
"Maximal lånetid\n",
/* TR_MISSING_BLUE_IP */
"IP-information saknas för BLÅTT interface.",
/* TR_MISSING_ORANGE_IP */
"Saknar IP information om det ORANGA gränsnittet.",
/* TR_MISSING_RED_IP */
"Saknar IP information om det RÖDA gränsnittet.",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"Modulnamn kan inte vara tomt.",
/* TR_MODULE_PARAMETERS */
"Skriv in modulens namn och de parametrar som den behöver.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Monterar boot filsystemet...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Monterar log filsystemet...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Monterar root filsystemet...",
/* TR_MOUNTING_SWAP_PARTITION */
"Monterar swap partitionen...",
/* TR_MSN_CONFIGURATION */
"Lokalt telefonnummer(MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Nätmask:",
/* TR_NETWORKING */
"Nätverk",
/* TR_NETWORK_ADDRESS_CR */
"Nätverksadress\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Nätverksadress:",
/* TR_NETWORK_CONFIGURATION_MENU */
"Nätverkskonfigurations meny",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Typ av nätverkskonfiguration",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Välj nätverkskonfigurering för %s.  Följande konfigurationstyper visar de gränssnitt som har ethernet inkopplat. Om du ändrar den här inställningen så kommer nätverkskommunikationen att behöva startas om, och du kommer behöva omkonfigurera nätverksdrivrutinstilldelningen.",
/* TR_NETWORK_MASK_CR */
"Nätmask\n",
/* TR_NETWORK_SETUP_FAILED */
"Nätverksinställningarna misslyckades.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"Det har inte allokerats tillräckligt många kort.",
/* TR_NO_BLUE_INTERFACE */
"Inget BLÅTT gränssnitt definierat.",
/* TR_NO_CDROM */
"Ingen CD-ROM funnen.",
/* TR_NO_HARDDISK */
"Ingen hårddisk funnen.",
/* TR_NO_IPCOP_TARBALL_FOUND */
"IpCop TAR-arkiv saknas på Web-server.",
/* TR_NO_ORANGE_INTERFACE */
"Inget ORANGE gränssnitt är tilldelat.",
/* TR_NO_RED_INTERFACE */
"Inget RÖTT gränssnitt är tilldelat.",
/* TR_NO_SCSI_IMAGE_FOUND */
"SCSI-image saknas på Web-server.",
/* TR_NO_UNALLOCATED_CARDS */
"Inga oallokerade kort återstår och det behövs flera. Du kan försöka söka efter flera eller välja en drivrutin från en lista.",
/* TR_OK */
"Ok",
/* TR_PARTITIONING_DISK */
"Partitionerar disken...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"Lösenorden är olika.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"Lösenordet kan inte vara tomt.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"Lösenordet får inte innehålla mellanslag.",
/* TR_PASSWORD_PROMPT */
"Lösenord:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Telefonnummret kan inte vara tomt.",
/* TR_PREPARE_HARDDISK */
"Installationsprogrammet kommmer nu att förbereda hårddisken på %s. Först kommer disken att partitioneras och sedan kommer filsystem skapas på partitionerna.",
/* TR_PRESS_OK_TO_REBOOT */
"Tryck på OK för att starta om.",
/* TR_PRIMARY_DNS */
"Primär DNS:",
/* TR_PRIMARY_DNS_CR */
"Primär DNS\n",
/* TR_PROBE */
"Sök",
/* TR_PROBE_FAILED */
"Automatisk detektering misslyckades.",
/* TR_PROBING_SCSI */
"Söker SCSI-enheter...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"Problem att sätta lösenordet för %s admin.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"Problem att sätta lösenordet för 'root'.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"Problem att sätta lösenordet för 'setup'.",
/* TR_PROTOCOL_COUNTRY */
"Protokoll/Land",
/* TR_PULLING_NETWORK_UP */
"Tar upp nätverket...",
/* TR_PUSHING_NETWORK_DOWN */
"Tar ner nätverket...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Tar ner det lokala nätverket...",
/* TR_QUIT */
"Avsluta",
/* TR_RED_IN_USE */
"ISDN (eller annan extern uppkoppling) används redan.  Du kan inte konfigurera ISDN medans det RÖDA gränssnittet är aktivt.",
/* TR_RESTART_REQUIRED */
"\n\nNär konfigurationen är färdig så kommer nätverket i datorn att behöva startas om.",
/* TR_RESTORE */
"Återställ",
/* TR_RESTORE_CONFIGURATION */
"Om du har en diskett med en %s systemkonfiguration på så skall du sätta in den i diskettdriven och trycka på återställknappen",
/* TR_ROOT_PASSWORD */
"'root' lösenord",
/* TR_SECONDARY_DNS */
"Sekundär DNS:",
/* TR_SECONDARY_DNS_CR */
"Sekundär DNS\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"Sekundär DNS specificerad utan någon Primär DNS",
/* TR_SECTION_MENU */
"Sektions menu",
/* TR_SELECT */
"Välj",
/* TR_SELECT_CDROM_TYPE */
"Välj typ av CDROM läsare",
/* TR_SELECT_CDROM_TYPE_LONG */
"Kunde inte hittade någon CDROM.  Välj vilken av följande drivrutiner som skall användas så att %s kan komma åt CDROM-läsaren.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Välj installations media",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s kan installeras från olika källor.  Det är enklast att använda datorns CDROM läsare. Om datorn saknar en CDROM så kan du installera från en annan dator på nätverket som har installationsfilerna tillgängliga via HTTP. I så fall så kommer disketten med nätverksdrivrutiner att behövas.",
/* TR_SELECT_NETWORK_DRIVER */
"Välj nätverksdrivrutin",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Välj den nätverksdrivrutin som matchar det kort som är installerat. Om du väljer MANUELLT, så kommer du få möjligheten att skriva in modulens namn och parametrar som hör till drivrutiner som har speciella behov, till exempel ISA kort.",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Välj det gränssnitt som du vill konfigurera om.",
/* TR_SELECT_THE_ITEM */
"Välj det du vill konfigurera.",
/* TR_SETTING_ADMIN_PASSWORD */
"Sätter lösenordet för %s admin....",
/* TR_SETTING_ROOT_PASSWORD */
"Sätter lösenordet för 'root'....",
/* TR_SETTING_SETUP_PASSWORD */
"Sätter lösenordet för 'setup'....",
/* TR_SETUP_FINISHED */
"Installationen är komplett.  Tryck på Ok för att starta om.",
/* TR_SETUP_NOT_COMPLETE */
"Grundinstalltionen är inte helt komplett. Du måste se till att installtionen genomförs fullständigt genom att köra setup igen från prompten.",
/* TR_SETUP_PASSWORD */
"'setup' lösenord",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Sätt eventuella extra modulparametrar",
/* TR_SINGLE_GREEN */
"Din konfiguration är satt till att endast ha ett GRÖNT gränssnitt.",
/* TR_SKIP */
"Hoppa över",
/* TR_START_ADDRESS */
"Start adress:",
/* TR_START_ADDRESS_CR */
"Start adress\n",
/* TR_STATIC */
"Statisk",
/* TR_SUGGEST_IO */
"(föreslår %x)",
/* TR_SUGGEST_IRQ */
"(föreslår %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"Den här modulen är redan inladdad.",
/* TR_TIMEZONE */
"Tidszon",
/* TR_TIMEZONE_LONG */
"Välj den tidszon du befinner dig i från listan nedan.",
/* TR_UNABLE_TO_EJECT_CDROM */
"Misslyckades att mata ut CDROM.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Misslyckades att extrahera moduler.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Kunde inte hitta några fler drivrutiner.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"ISDN kort kunde inte hittas i den här datorn. Du kan behöva ytterligare parameterar för att konfigurera modulen om kortet är av ISA typ eller har speciella behov.",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"Misslyckades med initieringen av ISDN.",
/* TR_UNABLE_TO_INSTALL_FILES */
"Misslyckades att installera filer.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"Misslyckades att installera GRUB.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Kunde inte ladda modulen.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Misslyckades att skapa boot filsystemet.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Misslyckades att skapa log filsystemet.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Misslyckades att skapa root filsystemet.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Misslyckades att skapa swap utrymme.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Misslyckades att skapa symbolisk länk /dev/harddisk.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Misslyckades att skapa symbolisk länk /dev/harddisk1.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Misslyckades att skapa symbolisk länk /dev/harddisk2.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Misslyckades att skapa symbolisk länk /dev/harddisk3.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Misslyckades att skapa symbolisk länk /dev/harddisk4.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Omöjligt att skapa symbolisk länk /dev/root.",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Misslyckades att montera boot filsystemet.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Misslyckades att montera log filsystemet.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Omöjligt att montera proc-filsystemet.",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Misslyckades att montera root filsystemet.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Misslyckades att montera swap partitionen.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Det gick inte att öppna filen \"hosts\".",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Kan inte öppna inställningsfil",
/* TR_UNABLE_TO_PARTITION */
"Misslyckades att partitionera disken.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"Kunde inte ta bort temporära filer.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"Kan inte sätta datornamn.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"Misslyckades att avmontera  CDROM/disketten.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"Misslyckader att avmontera hårddisken.",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"Misslyckades att skriva till /etc/fstab",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"Misslyckades att skriva till /etc/hostname",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"Kan inte skriva till /etc/hosts.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"Kan inte skriva till /etc/hosts.allow.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"Kan inte skriva till /etc/hosts.deny.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"Misslyckades att skriva %s/ethernet/settings.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"Kan inte skriva till %s/main/hostname.conf",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"Misslyckades att skriva %s/main/settings.",
/* TR_UNCLAIMED_DRIVER */
"Det finns ett oanvänt ethernetkort av typen:\n%s\n\nDu kan tilldela det här till:",
/* TR_UNKNOWN */
"OKÄND",
/* TR_UNSET */
"OANVÄNT",
/* TR_USB_KEY_VFAT_ERR */
"Denna USB-nyckel är ogiltig (ingen vfat-partition kunde hittas).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"VARNING",
/* TR_WARNING_LONG */
"Om du ändrar den här IP-adressen och är inloggad från annnan plats, som kommer din uppkoppling mot %s att brytas och du måste koppla upp dig igen med den nya IP-adressen. Detta är en riskfull operation och skall bara göras om du har fysisk tillgång till maskinen ifall något går fel.",
/* TR_WELCOME */
"Välkommen till %s installationsprogram. Om du väljer avbryt på någon av de följande sidorna så kommer datorn att startas om.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Din konfiguration är vald att ha ett enda GRÖNT gränssnitt och har redan tilldelats en drivrutin.",
}; 
  
