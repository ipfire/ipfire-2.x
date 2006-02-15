/*
 * Dutch (nl) Data File
 *
 * Dit bestand is een deel van de IPCop Firewall
 * 
 * IPCop is vrije software; het staat u vrij het de her-distribueren of
 * aan te passen onder de voorwaarden van de GNU General Public License
 * zoals deze gepubliceerd is door de Free Software Foundation; of
 * versie 2 van deze licentie, of (naar uw keuze) een latere versie.
 * 
 * IPCop wordt gedistribueerd in de hoop dat het nuttig is, maar
 * ZONDER ENIGE GARANTIE; zonder zelfs een impliciete garantie door
 * WEDERVERKOOPBAARHEID of geschikbaarheid voor een bepaalde
 * toepassing. Zie de GNU General Public License voor meer details.
 * 
 * U zou een kopie van de GNU General Public License bij IPCop
 * ontvangen moeten hebben. Mocht dit niet het geval zijn, schrijf
 * een brief naar:
 * 
 * Free Software Foundation, Inc.
 * 59 Temple Place
 * Suite 330
 * Boston
 * MA 02111-1307 USA
 * 
 * (c) The SmoothWall Team
 * 
 * IPCop translation
 * (c) 2003 Gerard Zwart, Berdt van der Lingen, Tony Vroon, Mark Wormgoor
 * (c) 2005 Jacques Hylkema, Maikel Punie 
 */
 
#include "libsmooth.h"

char *nl_tr[] = {

/* TR_ADDRESS_SETTINGS */
"Adres instellingen",
/* TR_ADMIN_PASSWORD */
"Admin wachtwoord",
/* TR_AGAIN_PROMPT */
"Opnieuw:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Alle kaarten successvol toegewezen.",
/* TR_AUTODETECT */
"* AUTOMATISCHE DETECTIE *",
/* TR_BUILDING_INITRD */
"INITRD wordt gebouwd...",
/* TR_CANCEL */
"Annuleren",
/* TR_CARD_ASSIGNMENT */
"Kaart toewijzing",
/* TR_CHECKING */
"Controle URL...",
/* TR_CHECKING_FOR */
"Aan het controleren voor: %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Kies de ISDN kaart die geïnstalleerd is in deze computer.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Kies het benodigde ISDN protocol.",
/* TR_CONFIGURE_DHCP */
"Configureer de DHCP server door de instellingen hieronder op te geven.",
/* TR_CONFIGURE_NETWORKING */
"Configureer netwerk",
/* TR_CONFIGURE_NETWORKING_LONG */
"U kunt nu uw netwerk configureren door allereerst de juiste driver te laden voor de GROENE interface. U kunt dit automatisch laten doen of door de juiste driver uit een lijst te selecteren. Als u meerdere netwerkkaarten heeft geïnstalleerd krijgt u later de mogelijkheid deze te installeren.U zou het netwerk moeten configureren door eerst de juiste driver te laden voor de GROENE interface. U kunt dit doen door zelf een driver uit een lijst te kiezen of dit script automatisch de juiste driver te laten zoeken. Als u meerdere netwerkkaarten heeft, krijgt u later de mogelijkheid deze te configuteren. Als u meerdere kaarten heeft van het zelfde type als de GROENE en elke kaart heeft speciale modules parameters, dan zult u deze voor alle kaarten van dit type moeten opgeven zodat alle kaarten actief kunnen worden als u de GROENE configureert. ",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Configureer netwerk drivers, en welke interface aan welke kaart is toegewezen. De huidige configuratie is de volgende:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"Configureer de CDROM doot het juiste IO adres en/of IRQ op te geven.",
/* TR_CONGRATULATIONS */
"Gefeliciteerd!",
/* TR_CONGRATULATIONS_LONG */
"%s is successvol geinstalleerd. Gelieve alle floppy disks of CDROM's te verwijderen. Setup zal u nu de mogelijkheid geven ISDN, netwerk, en systeem wachtwoorden in te stellen. Na het voltooien van Setup, kunt u met uw webbrowser naar http://%s:81 of https://%s:445 gaan (of hoe u uw %s genoemd heeft), en daar inbelnetwerk instellen(als dit nodig is) en externe toegang. Denk aaneen wachtwoord voor %s 'inbel' gebruiker, als u niet 'admin' gebruikers beheer wilt geven over een externe verbinding.",
/* TR_CONTINUE_NO_SWAP */
"Uw harddisks zijn erg klein, maar u kunt verder gaan zonder swap te gebruiken (Gebruik met voorzichtigheid).",
/* TR_CURRENT_CONFIG */
"Huidige configuratie: %s%s",
/* TR_DEFAULT_GATEWAY */
"Standaard Gateway:",
/* TR_DEFAULT_GATEWAY_CR */
"Standaard Gateway\n",
/* TR_DEFAULT_LEASE */
"Standaard lease (minuten):",
/* TR_DEFAULT_LEASE_CR */
"Standaard lease tijd\n",
/* TR_DETECTED */
"Gedetecteerd: %s",
/* TR_DHCP_HOSTNAME */
"DHCP Machinenaam:",
/* TR_DHCP_HOSTNAME_CR */
"DHCP Machinenaam\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"DHCP server configuratie",
/* TR_DISABLED */
"Uitgeschakeld",
/* TR_DISABLE_ISDN */
"Schakel ISDN uit",
/* TR_DISK_TOO_SMALL */
"Uw harde schijf is te klein.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"DNS en Gateway instellingen",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Geef DNS en gateway informatie op. Deze instellingen worden allen gebruikt als DHCP uit staat op de RODE interface.",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Uw configuratie gebruikt geen ethernet adapter voor de RODE interfaceDNS en Gateway informatie voor inbel gebruikers wordt automatisch ingesteld tijdens het inbellen.",
/* TR_DOMAINNAME */
"Domein naam",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Domein naam mag niet leeg zijn.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"Domein naam mag geen spaties bevatten.",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Domein naam mag alleen letters, cijfers, verbindingsstreepjes en punten bevatten.",
/* TR_DOMAIN_NAME_SUFFIX */
"Domein naam achtervoegsel:",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Domein naam achtervoegsel\n",
/* TR_DONE */
"Voltooid",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\nWilt u deze instellingen wijzigen?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Drivers en kaart toewijzingen",
/* TR_ENABLED */
"Ingeschakeld",
/* TR_ENABLE_ISDN */
"Schakel ISDN in",
/* TR_END_ADDRESS */
"Eind adres:",
/* TR_END_ADDRESS_CR */
"Eind adres\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Sommige ISDN kaarten (vooral ISA uitvoeringen) hebben additionele module parameters nodig om IRQ en IO adres informatie in te stellen. Als u zo eenISDN kaart heeft, vult u deze parameters hier in. Bijvoorbeeld: \"io=0x280 irq=9\". Deze worden gebruikt tijdens de kaart detectie.",
/* TR_ENTER_ADMIN_PASSWORD */
"Geef %s admin wachtwoord.  Dit is het gebruikers account wat u gebruikt om in te loggen via %s web beheers pagina's.",
/* TR_ENTER_DOMAINNAME */
"Geef Domein naam in",
/* TR_ENTER_HOSTNAME */
"Geef de machinenaam voor de machine.",
/* TR_ENTER_IP_ADDRESS_INFO */
"Vul IP adres informatie in",
/* TR_ENTER_NETWORK_DRIVER */
"Automatisch detecteren van de netwerkkaart mislukt. Geef een driver met de optionele parameters voor de netwerkkaart op.",
/* TR_ENTER_ROOT_PASSWORD */
"Geef het 'root' gebruikers wachtwoord. Log in als deze gebruiker voor commandprompt toegang.",
/* TR_ENTER_SETUP_PASSWORD */
"Geef het 'setup' gebruikers wachtwoord. Log in als deze gebruiker om het Setup programma te gebruiken.",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Vul de IP adres informatie in voor %s interface.",
/* TR_ENTER_THE_LOCAL_MSN */
"Geef het lokale telefoon nummer op (MSN/EAZ).",
/* TR_ENTER_URL */
"Geef de URL in voor de ipcop-<versie>.tgz en scsidrv-<versie>.img bestanden.  WAARSCHUWING: DNS is niet beschikbaar.  Dit moet dus zijn: http://X.X.X.X/<directory>/.",
/* TR_ERROR */
"Fout",
/* TR_ERROR_WRITING_CONFIG */
"Er is een fout opgetreden tijdens het schrijven van de configuratie informatie.",
/* TR_EURO_EDSS1 */
"Euro (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Modules uitpakken...",
/* TR_FAILED_TO_FIND */
"Kon het bestand via URL niet vinden.",
/* TR_FOUND_NIC */
"%s heeft de volgende netwerkkaart gevonden: %s",
/* TR_GERMAN_1TR6 */
"Duits 1TR6",
/* TR_HELPLINE */
"              <Tab>/<Alt-Tab> tussen elementen   |  <Space> selecteren",
/* TR_HOSTNAME */
"Machinenaam",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Machinenaam kan niet leeg zijn.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"Machinenaam kan geen spaties bevatten.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"Machinenaam mag alleen letters, cijfers en verbindingsstreepjes bevatten.",
/* TR_INITIALISING_ISDN */
"Initialiseren ISDN...",
/* TR_INSERT_CDROM */
"Gelieve de %s CD in de CDROM speler te plaatsen.",
/* TR_INSERT_FLOPPY */
"Gelieve de %s driver diskette in uw floppy drive te plaatsen.",
/* TR_INSTALLATION_CANCELED */
"Installatie geannuleerd.",
/* TR_INSTALLING_FILES */
"Bestanden aan het installeren...",
/* TR_INSTALLING_GRUB */
"LILO aan het installeren...",
/* TR_INTERFACE */
"%s interface",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"Aktief worden interface mislukt.",
/* TR_INVALID_FIELDS */
"De volgende velden zijn ongeldig:\n\n",
/* TR_INVALID_IO */
"De opgegeven IO poort details zijn ongeldig. ",
/* TR_INVALID_IRQ */
"Het opgegeven IRQ is ongeldig.",
/* TR_IP_ADDRESS_CR */
"IP adres\n",
/* TR_IP_ADDRESS_PROMPT */
"IP adres:",
/* TR_ISDN_CARD */
"ISDN kaart",
/* TR_ISDN_CARD_NOT_DETECTED */
"ISDN kaart niet gedetecteerd. U kunt additionele module parameters opgeven als het om kaart gaat van het ISA type of speciale instellingen vereist.",
/* TR_ISDN_CARD_SELECTION */
"ISDN kaart selectie",
/* TR_ISDN_CONFIGURATION */
"ISDN Configuratie",
/* TR_ISDN_CONFIGURATION_MENU */
"ISDN configuratie menu",
/* TR_ISDN_NOT_SETUP */
"ISDN niet ingesteld. Sommige items zijn niet geselecteerd.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"ISDN is nog niet geconfigureerd. Selecteer het item dat u wilt instellen.",
/* TR_ISDN_PROTOCOL_SELECTION */
"ISDN protocol selectie",
/* TR_ISDN_STATUS */
"ISDN is op dit moment %s.\n\n   Protocol: %s\n   Kaart: %s\n   Lokaal telefoon nummer: %s\n\nSelecteer het item wat u opnieuw wilt configureren, of kies voor de huidige instellingen.",
/* TR_KEYBOARD_MAPPING */
"Toetsenbord layout",
/* TR_KEYBOARD_MAPPING_LONG */
"Kies het type toetsenbord dat u gebruikt in de lijst hieronder.",
/* TR_LEASED_LINE */
"Huurlijn",
/* TR_LOADING_MODULE */
"Laden van module...",
/* TR_LOADING_PCMCIA */
"Laden van PCMCIA modules...",
/* TR_LOOKING_FOR_NIC */
"Zoekt naar: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Opstart bestandssysteem aan het maken...",
/* TR_MAKING_LOG_FILESYSTEM */
"log bestandssysteem aan het maken...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Maken van root bestandssysteem...",
/* TR_MAKING_SWAPSPACE */
"SWAP ruimte aan het maken...",
/* TR_MANUAL */
"* HANDMATIG *",
/* TR_MAX_LEASE */
"Max lease (minuten):",
/* TR_MAX_LEASE_CR */
"Max lease tijd\n",
/* TR_MISSING_BLUE_IP */
"Er is geen IP informatie voor de BLAUWE interface.",
/* TR_MISSING_ORANGE_IP */
"Er is geen IP informatie voor de ORANJE interface.",
/* TR_MISSING_RED_IP */
"Er is geen IP informatie voor de RODE interface.",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"Module naam kan niet leeg zijn.",
/* TR_MODULE_PARAMETERS */
"Geef de module naam en parameters voor de benodigde driver.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Koppelen van opstart bestandssysteem...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Koppelen van log bestandssysteem...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Root bestandssysteem aan het koppelen...",
/* TR_MOUNTING_SWAP_PARTITION */
"Swap partitie aan het koppelen...",
/* TR_MSN_CONFIGURATION */
"Lokaal telefoon nummer (MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Netwerk mask:",
/* TR_NETWORKING */
"Netwerk",
/* TR_NETWORK_ADDRESS_CR */
"Netwerk adres\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Netwerk adres:",
/* TR_NETWORK_CONFIGURATION_MENU */
"Netwerk configuratie menu",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Netwerk configuratie type",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Selecteer de netwerkconfiguratie voor %s.  De volgende configuratie types rangschikt de interfaces welke aan ethernet gekoppeld zijn. Als u deze instelling aanpast, is een netwerk herstart nodig en u zult netwerk toewijzingen moeten herconfigureren. ",
/* TR_NETWORK_MASK_CR */
"Netwerk mask\n",
/* TR_NETWORK_SETUP_FAILED */
"Netwerk setup mislukt.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"Er zijn niet genoeg kaarten toegewezen.",
/* TR_NO_BLUE_INTERFACE */
"Er is geen BLAUWE interface aangewezen.",
/* TR_NO_CDROM */
"Geen CD-ROM gevonden.",
/* TR_NO_HARDDISK */
"Geen harddisk gevonden.",
/* TR_NO_IPCOP_TARBALL_FOUND */
"Geen ipcop tarbestand gevonden op de webserver.",
/* TR_NO_ORANGE_INTERFACE */
"Er is geen ORANJE interface toegewezen.",
/* TR_NO_RED_INTERFACE */
"Er is geen RODE interface toegewezen.",
/* TR_NO_SCSI_IMAGE_FOUND */
"Geen SCSI bestand gevonden op de webserver.",
/* TR_NO_UNALLOCATED_CARDS */
"Geen ongebruikte netwerkkaarten meer, u heeft er meer nodig. U kunt autodetectie gebruiken om te zoeken naar meerkaarten of er een selecteren uit de lijst.",
/* TR_OK */
"Ok",
/* TR_PARTITIONING_DISK */
"Indelen schijf...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"De wachtwoorden komen niet overeen.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"Het wachtwoord kan niet leeg zijn.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"Wachtwoord mag geen spaties bevatten.",
/* TR_PASSWORD_PROMPT */
"Wachtwoord:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Het telefoon nummer kan niet leeg zijn",
/* TR_PREPARE_HARDDISK */
"Het installatie programma zal nu uw harde schijf voorbereiden voor %s. Eerst zal de schijf ingedeeld worden, en dan zal er een bestandssysteem op geschreven worden.",
/* TR_PRESS_OK_TO_REBOOT */
"Kies Ok om opnieuw te starten.",
/* TR_PRIMARY_DNS */
"Primaire DNS:",
/* TR_PRIMARY_DNS_CR */
"Primaire DNS\n",
/* TR_PROBE */
"Probeer",
/* TR_PROBE_FAILED */
"Auto detectie mislukt.",
/* TR_PROBING_SCSI */
"Zoeken SCSI apparaten...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"Probleem bij het instellen van het %s admin wachtwoord.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"Probleem bij het instellen van het 'root' wachtwoord.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"Probleem bij het instellen van het 'setup' wachtwoord.",
/* TR_PROTOCOL_COUNTRY */
"Protocol/Land",
/* TR_PULLING_NETWORK_UP */
"Netwerk activeren...",
/* TR_PUSHING_NETWORK_DOWN */
"Netwerk uitschakelen...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Down brengen lokaal netwerk...",
/* TR_QUIT */
"Stop",
/* TR_RED_IN_USE */
"ISDN (of andere externe verbinding) is op dit moment in gebruik.U kan ISDN niet instellen als de RODE interface aktief is.",
/* TR_RESTART_REQUIRED */
"\n\nAls de comfiguratie compleet is, is een netwerk herstart nodig.",
/* TR_RESTORE */
"Terugzetten",
/* TR_RESTORE_CONFIGURATION */
"Als je een floppy met de %s systeemconfiguratie hebt, plaats de floppy in de drive en selecteer Terugzetten.",
/* TR_ROOT_PASSWORD */
"'root' wachtwoord",
/* TR_SECONDARY_DNS */
"Secondaire DNS:",
/* TR_SECONDARY_DNS_CR */
"Secondaire DNS\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"Secondaire DNS opgegeven zonder Primaire DNS",
/* TR_SECTION_MENU */
"Sectie menu",
/* TR_SELECT */
"Selecteer",
/* TR_SELECT_CDROM_TYPE */
"Selecteer CDROM type",
/* TR_SELECT_CDROM_TYPE_LONG */
"Er is geen CD-ROM gedetecteerd.  Geef aan welke van de volgendedrivers u wilt gebruiken om %s toegang te geven tot de CD-ROM.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Selecteer installatie manier",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s kan vanaf meerdere bronnen geinstalleerd worden.  De simpelste is gebruik te maken van de cdrom. Als de computer geen cdrom speler heeft kunt u installeren via een andere computer op het netwerk met via HTTP. In dit geval zult u een netwerkkaart driver diskette nodig hebben.",
/* TR_SELECT_NETWORK_DRIVER */
"Selecteer netwerk driver",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Selecteer de netwerk driver voor de geinstalleerde kaart in deze machine.Als u HANDMATIG selecteert kunt u de driver module naam en parameter opgeven voor drivers die speciale vereisten hebben, zoals ISA kaarten",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Selecteer de interface die u wilt herconfigureren.",
/* TR_SELECT_THE_ITEM */
"Selecteer het item dat u wilt configureren.",
/* TR_SETTING_ADMIN_PASSWORD */
"Instellen %s admin wachtwoord....",
/* TR_SETTING_ROOT_PASSWORD */
"Instellen 'root' wachtwoord....",
/* TR_SETTING_SETUP_PASSWORD */
"Instellen 'setup' wachtwoord....",
/* TR_SETUP_FINISHED */
"Setup is voltooid. Selecteer Ok om opnieuw te start.",
/* TR_SETUP_NOT_COMPLETE */
"De initiële setup is niet helemaal compleet. Controleer dat Setup netjes voltooid is door Setup nogmaals te draaien vanaf de shell.",
/* TR_SETUP_PASSWORD */
"'setup' wachtwoord",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Geef additionele module parameters",
/* TR_SINGLE_GREEN */
"Uw configuratie is ingesteld voor een enkele GROENE interface.",
/* TR_SKIP */
"Overslaan",
/* TR_START_ADDRESS */
"Begin adres:",
/* TR_START_ADDRESS_CR */
"Begin adres\n",
/* TR_STATIC */
"Statisch",
/* TR_SUGGEST_IO */
"(suggestie %x)",
/* TR_SUGGEST_IRQ */
"(suggestie %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"Deze driver module is al geladen.",
/* TR_TIMEZONE */
"Tijdzone",
/* TR_TIMEZONE_LONG */
"Kies de tijdzone waarin u zich bevind in de lijst hieronder.",
/* TR_UNABLE_TO_EJECT_CDROM */
"Kan de CDROM niet uitwerpen.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Kon modules niet uitpakken.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Kan geen additionele drivers vinden.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Kan geen ISDN kaart vinden in deze computer. Misschien moet u additionele module parameters opgeven als het een ISA type is of speciale instellingen vereist.",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"Kan ISDN niet initialiseren.",
/* TR_UNABLE_TO_INSTALL_FILES */
"Installeren bestanden mislukt.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"Het installeren van GRUB is mislukt.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Kan driver module niet laden.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Maken van opstart bestandssysteem mislukt.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Maken van log bestandssysteem mislukt.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Maken van root bestandssysteem mislukt.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Maken van SWAP ruimte mislukt.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Kan geen symbolische link maken naar /dev/harddisk.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Kan geen symbolische link maken naar /dev/harddisk1.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Kan geen symbolische link maken naar /dev/harddisk2.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Kan geen symbolische link maken naar /dev/harddisk3.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Kan geen symbolische link maken naar /dev/harddisk4.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Kan geen symbolische link maken naar /dev/root",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Koppelen van opstart bestandssysteem mislukt.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Koppelen van log bestandssysteem mislukt.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Koppelen van proc bestandssysteem mislukt.",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Koppelen root bestandssysteem mislukt.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Koppelen van de SWAP partitie mislukt.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Kan hosts bestand niet openen.",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Kan instellingen bestand niet openen",
/* TR_UNABLE_TO_PARTITION */
"Het indelen van de schijf is mislukt.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"Het verwijderen van tijdelijke opgehaalde bestanden is mislukt.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"Kan machinenaam niet wegschijven.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"Het loskoppelen van de CDROM/Floppy is mislukt.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"Het loskoppelen van de harde schijf is mislukt",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"Kan /etc/fstab niet wegschrijven",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"Kan /etc/hostname niet wegschrijven",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"Kan niet wegschrijven /etc/hosts.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"Kan niet wegschrijven /etc/hosts.allow.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"Kan niet wegschrijven /etc/hosts.deny.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"Kan %s/ethernet/settings niet wegschrijven.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"Kan niet wegschrijven %s/main/hostname.conf",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"Kan %s/main/settings niet wegschrijven.",
/* TR_UNCLAIMED_DRIVER */
"Dit is een ongebruikte netwerkkaart van het type:\n%s\n\nU kunt deze toewijzen aan:",
/* TR_UNKNOWN */
"ONBEKEND",
/* TR_UNSET */
"ONGEDAAN MAKEN",
/* TR_USB_KEY_VFAT_ERR */
"De USB key is niet inorde (geen vfat partitie gevonden).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"WAARSCHUWING",
/* TR_WARNING_LONG */
"Als u dit IP adres aanpast, en u bent op afstand verbonden, zal u verbinding met de %s machine worden verbroken, en u zult dan opnieuw moeten verbinden, gebruikmakend van het nieuwe IP. Dit is een risicovolle operatie en zou alleen uitgevoerd moeten worden als u fysieke toegang heeft tot de machine voor het geval dat er iets fout gaat.",
/* TR_WELCOME */
"Welkom in het %s installatie programma. Het selecteren van Annuleer op enig van de volgende schermen laat uw computer herstarten.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Uw configuratie is ingesteld voor een enkele GROENE interface, welke al een driver heeft.",
}; 
  
