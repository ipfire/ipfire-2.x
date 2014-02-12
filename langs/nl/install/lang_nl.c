/*
 * Dutch (nl) Data File
 *
 * This file is part of the IPFire.
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
 * (c) IPFire Team  <info@ipfire.org>
 *
 * based on work of SmoothWall and IPCop
 *
 * (c) The SmoothWall Team
 *  
 */
 
#include "libsmooth.h"

char *nl_tr[] = {

/* TR_ISDN */
"ISDN",
/* TR_ERROR_PROBING_ISDN */
"Kan ISDN-apparaten niet detecteren.",
/* TR_PROBING_ISDN */
"Detecteren en configureren van ISDN-apparaten.",
/* TR_MISSING_GREEN_IP */
"Groen IP-adres ontbreekt!",
/* TR_CHOOSE_FILESYSTEM */
"Kies uw bestandssysteem:",
/* TR_NOT_ENOUGH_INTERFACES */
"Onvoldoende netwerkkaarten voor uw keuze.\n\nNodig: %d - Beschikbaar: %d\n",
/* TR_INTERFACE_CHANGE */
"Kies de interface die u wilt wijzigen.\n\n",
/* TR_NETCARD_COLOR */
"Toegewezen kaarten",
/* TR_REMOVE */
"Verwijder",
/* TR_MISSING_DNS */
"DNS ontbreekt.\n",
/* TR_MISSING_DEFAULT */
"Standaard gateway ontbreekt.\n",
/* TR_JOURNAL_EXT3 */
"Aanmaken journal voor Ext3...",
/* TR_CHOOSE_NETCARD */
"Kies een netwerkkaart voor de volgende interface - %s.",
/* TR_NETCARDMENU2 */
"Uitgebreide Netwerkmenu",
/* TR_ERROR_INTERFACES */
"Er zijn geen vrije interfaces op uw systeem.",
/* TR_REMOVE_CARD */
"Moet de toewijzing voor de netwerkkaart worden verwijderd? - %s",
/* TR_JOURNAL_ERROR */
"Kon het journaalboek niet aanmaken, valt terug op gebruik van ext2.",
/* TR_FILESYSTEM */
"Kies uw bestandssysteem",
/* TR_ADDRESS_SETTINGS */
"Adresinstellingen",
/* TR_ADMIN_PASSWORD */
"'admin' wachtwoord",
/* TR_AGAIN_PROMPT */
"Nogmaals:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Alle kaarten zijn succesvol toegewezen.",
/* TR_AUTODETECT */
"* AUTOMATISCH DETECTEREN *",
/* TR_BUILDING_INITRD */
"Aanmaken ramdisk...",
/* TR_CANCEL */
"Annuleren",
/* TR_CARD_ASSIGNMENT */
"Kaart toewijzing",
/* TR_CHECKING */
"Controleert URL...",
/* TR_CHECKING_FOR */
"Controleert voor: %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Kies de ISDN-kaart die geïnstalleerd is op deze computer.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Kies het ISDN-protocol dat u nodig heeft.",
/* TR_CONFIGURE_DHCP */
"Configureer de DHCP server door de instellingen in te voeren.",
/* TR_CONFIGURE_NETWORKING */
"Configureer het netwerk",
/* TR_CONFIGURE_NETWORKING_LONG */
"U moet nu het netwerk configureren door eerst de juiste driver te laden voor de GROENE interface. U kunt dit doen door ofwel automatisch te zoeken naar een netwerkkaart, of door de juiste driver te kiezen uit een lijst. Als u meer dan een kaart in uw machine heeft, dan kunt u die later in het installatieproces configureren. Mocht u meer dan een kaart van hetzelfde type als GROEN gebruiken en iedere kaart vereist speciale moduleparameters, dan moet u de parameters voor alle kaarten van dit type invoeren zodat alle kaarten actief kunnen worden waneer u de GROENE interface configureert.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Configureer netwerkdrivers en bepaal welke interface iedere kaart krijgt toegewezen.\nDe huidige configuratie is als volgt:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"Configureer de CDROM door het juiste IO-adres en/of IRQ te kiezen.",
/* TR_CONGRATULATIONS */
"Gefeliciteerd!",
/* TR_CONGRATULATIONS_LONG */
"%s is succesvol geïnstalleerd. Verwijder a.u.b. de CDROM's in uw computer. U kunt nu de netwerkkaarten en ISDN configureren en de systeemwachtwoorden instellen. Nadat de setup is afgerond, kunt u met de webbrowser naar https://%s:444 (of hoe u %s ook genoemd heeft) en het inbelnetwerk configureren (als nodig) en de remote toegang.", 
/* TR_CONTINUE_NO_SWAP */
"Uw vaste schijf is erg klein, maar u kunt verder gaan met een zeer kleine swap. (Wees hier voorzichtig mee).",
/* TR_CURRENT_CONFIG */
"Huidige configuratie: %s%s",
/* TR_DEFAULT_GATEWAY */
"Standaard Gateway:",
/* TR_DEFAULT_GATEWAY_CR */
"Standaard Gateway\n",
/* TR_DEFAULT_LEASE */
"Standaard lease (min.):",
/* TR_DEFAULT_LEASE_CR */
"Standaard leasetijd\n",
/* TR_DETECTED */
"Gedetecteerd: %s",
/* TR_DHCP_HOSTNAME */
"DHCP Hostnaam:",
/* TR_DHCP_HOSTNAME_CR */
"DHCP Hostnaam\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"DHCP serverconfiguratie",
/* TR_DISABLED */
"Uitgeschakeld",
/* TR_DISABLE_ISDN */
"ISDN uitschakelen",
/* TR_DISK_TOO_SMALL */
"Uw vaste schijf is te klein.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"DNS en Gateway instellingen",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Voer de DNS en gateway informatie in. Deze instellingen worden alleen gebruikt met statische IP-adressen (en DHCP als DNS is ingesteld) op de RODE interface.",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Uw configuratie gebruikt geen ethernetadapter voor z'n RODE interface. DNS en gateway voor inbelgebruikers worden automatisch geconfigureerd tijdens inbellen.",
/* TR_DOMAINNAME */
"Domeinnaam",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Domeinnaam mag niet leeg zijn.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"Domeinnaam mag geen spaties bevatten.",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Domeinnaam mag alleen letters, getallen, koppeltekens en punten bevatten.",
/* TR_DOMAIN_NAME_SUFFIX */
"Domeinnaam toevoeging:",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Domeinnaam toevoeging\n",
/* TR_DONE */
"Klaar",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\nWilt u deze instellingen wijzigen?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Drivers en kaarttoewijzingen",
/* TR_ENABLED */
"Ingeschakeld",
/* TR_ENABLE_ISDN */
"Inschakelen ISDN",
/* TR_END_ADDRESS */
"Eindadres:",
/* TR_END_ADDRESS_CR */
"Eindadres\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Bepaalde ISDN-kaarten (met name de ISA-kaarten) kunnen extra moduleparameters vereisen voor het instellen van IRQ- en IO-adressen. Als u zo'n ISDN-kaart heeft, voer deze parameters dan hier in. Bijvoorbeeld: \"io=0x280 irq=9\". Deze gegevens worden gebruikt tijdens de kaartdetectie.",
/* TR_ENTER_ADMIN_PASSWORD */
"Voer het %s 'admin' wachtwoord in. Dit is de gebruikersnaam die gebruikt wordt om in te loggen op de %s webbeheerpagina's.",
/* TR_ENTER_DOMAINNAME */
"Voer de domeinnaam in",
/* TR_ENTER_HOSTNAME */
"Voer de machinehostnaam in",
/* TR_ENTER_IP_ADDRESS_INFO */
"Voer de IP-adres informatie in",
/* TR_ENTER_NETWORK_DRIVER */
"Automatisch detecteren van netwerkkaart is mislukt. Voer de drivernaam en optionele parameters in voor de netwerkkaart.",
/* TR_ENTER_ROOT_PASSWORD */
"Voer het 'root' wachtwoord in. Log in als deze gebruiker voor commandoregel toegang.",
/* TR_ENTER_SETUP_PASSWORD */
"WORDT VERWIJDERD",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Voer de IP-adres informatie in voor de %s interface.",
/* TR_ENTER_THE_LOCAL_MSN */
"Voer lokaal telefoonnummer in (MSN/EAZ).",
/* TR_ENTER_URL */
"Voer het URL-pad in naar de ipcop-<versie>.tgz en images/scsidrv-<versie>.img bestanden. WAARSCHUWING: DNS is niet beschikbaar! Dit zou http://X.X.X.X/<directory> moeten zijn",
/* TR_ERROR */
"Fout",
/* TR_ERROR_PROBING_CDROM */
"Geen CDROM-speler gevonden.",
/* TR_ERROR_WRITING_CONFIG */
"Fout bij wegschrijven van configuratie informatie.",
/* TR_EURO_EDSS1 */
"Euro (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Uitpakken modules...",
/* TR_FAILED_TO_FIND */
"URL-bestand niet gevonden.",
/* TR_FOUND_NIC */
"%s heeft de volgende NIC in uw machine gedetecteerd: %s",
/* TR_GERMAN_1TR6 */
"German 1TR6",
/* TR_HELPLINE */
"        <Tab>/<Alt-Tab> schakel tussen elementen   |  <Spatie> selecteer",
/* TR_HOSTNAME */
"Hostnaam",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Hostnaam mag niet leeg zijn.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"Hostnaam mag geen spaties bevatten.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"Hostnaam mag alleen letters, getallen en koppeltekens bevatten.",
/* TR_INITIALISING_ISDN */
"Initialiseert ISDN...",
/* TR_INSERT_CDROM */
"Plaats de %s CD in the CDROM-speler a.u.b.",
/* TR_INSERT_FLOPPY */
"Plaats de %s driver-diskette in het station a.u.b.",
/* TR_INSTALLATION_CANCELED */
"Installatie afgebroken.",
/* TR_INSTALLING_FILES */
"Installeert bestanden...",
/* TR_INSTALLING_GRUB */
"Installeert GRUB...",
/* TR_INSTALLING_LANG_CACHE */
"Installeert taalbestanden...",
/* TR_INTERFACE */
"Interface - %s",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"Interface kwam niet op.",
/* TR_INVALID_FIELDS */
"De volgende velden zijn ongeldig:\n\n",
/* TR_INVALID_IO */
"De ingevoerde IO-poortgegevens zijn ongeldig. ",
/* TR_INVALID_IRQ */
"De ingevoerde IRQ gegevens zijn ongeldig.",
/* TR_IP_ADDRESS_CR */
"IP-adres\n",
/* TR_IP_ADDRESS_PROMPT */
"IP-adres:",
/* TR_ISDN_CARD */
"ISDN-kaart",
/* TR_ISDN_CARD_NOT_DETECTED */
"ISDN-kaart niet gedetecteerd. Mogelijk dient u extra moduleparameters op te geven als het een ISA type betreft of heeft het speciale eisen.",
/* TR_ISDN_CARD_SELECTION */
"ISDN kaartselectie",
/* TR_ISDN_CONFIGURATION */
"ISDN configuratie",
/* TR_ISDN_CONFIGURATION_MENU */
"ISDN configuratiemenu",
/* TR_ISDN_NOT_SETUP */
"ISDN niet ingesteld. Sommige items zijn niet geselecteerd.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"ISDN is nog niet geconfigureerd. Selecteer het item dat u wilt configureren.",
/* TR_ISDN_PROTOCOL_SELECTION */
"ISDN protocolselectie",
/* TR_ISDN_STATUS */
"ISDN is momenteel %s.\n\n   Protocol: %s\n   Kaart: %s\n   Lokaal telefoonnummer: %s\n\nSelecteer het item dat u wilt herconfigureren, of kies voor de huidige instellingen.",
/* TR_KEYBOARD_MAPPING */
"Toetsenbordindeling",
/* TR_KEYBOARD_MAPPING_LONG */
"Kies het type toetsenbord dat u gebruikt uit de lijst hieronder.",
/* TR_LEASED_LINE */
"Vaste verbinding",
/* TR_LOADING_MODULE */
"Laadt module...",
/* TR_LOADING_PCMCIA */
"Laadt PCMCIA modules...",
/* TR_LOOKING_FOR_NIC */
"Zoekt naar: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Aanmaken boot bestandssysteem...",
/* TR_MAKING_LOG_FILESYSTEM */
"Aanmaken log bestandssysteem...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Aanmaken root bestandssysteem...",
/* TR_MAKING_SWAPSPACE */
"Aanmaken swap...",
/* TR_MANUAL */
"* HANDMATIG *",
/* TR_MAX_LEASE */
"Max. lease (min.):",
/* TR_MAX_LEASE_CR */
"Max. leasetijd\n",
/* TR_MISSING_BLUE_IP */
"Ontbrekende IP-informatie op de BLAUWE interface.",
/* TR_MISSING_ORANGE_IP */
"Ontbrekende IP-informatie op de ORANJE interface.",
/* TR_MISSING_RED_IP */
"Ontbrekende IP-informatie op de RODE interface.",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"Modulenaam mag niet leeg zijn.",
/* TR_MODULE_PARAMETERS */
"Voer de modulenaam en parameters in voor de driver die u nodig hebt.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Koppelen van het boot bestandssysteem...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Koppelen van het log bestandssysteem...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Koppelen van het root bestandssysteem...",
/* TR_MOUNTING_SWAP_PARTITION */
"Koppelen van de swap partitie...",
/* TR_MSN_CONFIGURATION */
"Lokaal telefoonnummer (MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Netwerkmasker:",
/* TR_NETWORKING */
"Netwerk",
/* TR_NETWORK_ADDRESS_CR */
"Netwerkadres\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Netwerkadres:",
/* TR_NETWORK_CONFIGURATION_MENU */
"Netwerk configuratiemenu",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Netwerk configuratietype",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Selecteer de netwerkconfiguratie voor %s. De volgende configuratiesoorten vermelden welke interfaces op ethernet aangesloten zijn. Als u deze instellingen wijzigt, dan is een netwerk herstart nodig en u moet de netwerkdriver toewijzingen opnieuw maken.",
/* TR_NETWORK_MASK_CR */
"Netwerkmasker\n",
/* TR_NETWORK_SETUP_FAILED */
"Netwerkinstelling mislukt.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"Er zijn onvoldoende kaarten toegewezen.",
/* TR_NO_BLUE_INTERFACE */
"Er is geen BLAUWE interface toegewezen.",
/* TR_NO_CDROM */
"Geen CD-ROM gevonden.",
/* TR_NO_GREEN_INTERFACE */
"Er is geen GROENE interface toegewezen.",
/* TR_NO_HARDDISK */
"Geen vaste schijf gevonden.",
/* TR_NO_IPCOP_TARBALL_FOUND */
"Er is geen ipcop tarball gevonden op de webserver.",
/* TR_NO_ORANGE_INTERFACE */
"Er is geen ORANJE interface toegewezen.",
/* TR_NO_RED_INTERFACE */
"Er is geen RODE interface toegewezen.",
/* TR_NO_SCSI_IMAGE_FOUND */
"Er is geen SCSI image gevonden op de webserver.",
/* TR_NO_UNALLOCATED_CARDS */
"Er zijn geen vrije kaarten over, er zijn er meer vereist. U kunt automatisch detecteren proberen en op zoek gaan naar meer kaarten, of u kiest een driver uit de lijst.",
/* TR_OK */
"Ok",
/* TR_PARTITIONING_DISK */
"Partitioneert schijf...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"Wachtwoorden komen niet overeen.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"Wachtwoord mag niet leeg zijn.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"Wachtwoord mag geen spaties bevatten.",
/* TR_PASSWORD_PROMPT */
"Wachtwoord:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Telefoonnummer mag niet leeg zijn.",
/* TR_PREPARE_HARDDISK */
"Het installatieprogramma zal nu de vaste schijf voorbereiden op %s. Eerst wordt de schijf gepartitioneerd, daarna zullen de bestandssystemen erop worden gezet.\n\nALLE DATA OP DE SCHIJF ZAL WORDEN GEWIST. Wilt u hiermee doorgaan?",
/* TR_PRESS_OK_TO_REBOOT */
"Druk Ok om te herstarten.",
/* TR_PRIMARY_DNS */
"Primaire DNS:",
/* TR_PRIMARY_DNS_CR */
"Primaire DNS\n",
/* TR_PROBE */
"Opsporen",
/* TR_PROBE_FAILED */
"Automatisch detecteren mislukt.",
/* TR_PROBING_HARDWARE */
"Opsporen van hardware...",
/* TR_PROBING_FOR_NICS */
"Zoeken naar NIC's...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"Er is een probleem met het instellen van %s 'admin' gebruikerswachtwoord.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"Er is een probleem met het instellen van %s 'root' gebruikerswachtwoord.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"WORDT VERWIJDERD",
/* TR_PROTOCOL_COUNTRY */
"Protocol/Land",
/* TR_PULLING_NETWORK_UP */
"Netwerk opbrengen...",
/* TR_PUSHING_NETWORK_DOWN */
"Netwerk stoppen...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Niet-lokaal netwerk stoppen...",
/* TR_QUIT */
"Stoppen",
/* TR_RED_IN_USE */
"ISDN (of een andere externe verbinding) is momenteel in gebruik. U kunt ISDN niet configureren zolang de RODE interface actief is.",
/* TR_RESTART_REQUIRED */
"\n\nAls de configuratie gereed is moet het netwerk herstart worden.",
/* TR_RESTORE */
"Terugzetten",
/* TR_RESTORE_CONFIGURATION */
"Als u een diskette heeft met een %s systeemconfiguratie daarop, plaats dan de diskette in het station en druk op de terugzetten-knop.",
/* TR_ROOT_PASSWORD */
"'root' wachtwoord",
/* TR_SECONDARY_DNS */
"Secundaire DNS:",
/* TR_SECONDARY_DNS_CR */
"Secundaire DNS\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"Secundaire DNS opgegeven zonder een primaire DNS",
/* TR_SECTION_MENU */
"Sectiemenu",
/* TR_SELECT */
"Selecteer",
/* TR_SELECT_CDROM_TYPE */
"Selecteer CDROM type",
/* TR_SELECT_CDROM_TYPE_LONG */
"Er is geen CD-ROM gedetecteerd in deze machine. Maak een keuze uit de volgende drivers waarmee %s de CD-ROM kan benaderen.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Selecteer installatiemedium",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s kan worden geïnstalleerd vanuit verschillende bronnen. De eenvoudigste manier is om de CDROM-speler van de machine te gebruiken. Als de computer geen CDROM-speler heeft, dan kunt vanaf een andere machine installeren die de installatiebestanden beschikbaar kan maken over het netwerk via HTTP of FTP.",
/* TR_SELECT_NETWORK_DRIVER */
"Selecteer netwerkdriver",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Selecteer de netwerkdriver voor de aanwezige kaart in deze machine. Als u HANDMATIG selecteert, krijgt u de mogelijkheid om de driver modulenaam en parameters op te geven voor drivers met speciale eisen, zoals voor ISA-kaarten.",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Selecteer de interface die u wilt herconfigureren.",
/* TR_SELECT_THE_ITEM */
"Selecteer het item dat u wilt configureren.",
/* TR_SETTING_ADMIN_PASSWORD */
"Instellen van %s 'admin' gebruikerswachtwoord...",
/* TR_SETTING_ROOT_PASSWORD */
"Instellen van 'root' wachtwoord....",
/* TR_SETTING_SETUP_PASSWORD */
"WORDT VERWIJDERD",
/* TR_SETUP_FINISHED */
"Setup is afgerond. Druk Ok.",
/* TR_SETUP_NOT_COMPLETE */
"Initiële setup was niet volledig afgerond. Verzeker u ervan dat de setup goed is afgerond door het setup programma nogmaals vanaf de commandoregel te starten.",
/* TR_SETUP_PASSWORD */
"WORDT VERWIJDERD",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Instellen additionele moduleparameters",
/* TR_SINGLE_GREEN */
"Uw configuratie is ingesteld voor een enkele GROENE interface.",
/* TR_SKIP */
"Overslaan",
/* TR_START_ADDRESS */
"Beginadres:",
/* TR_START_ADDRESS_CR */
"Beginadres\n",
/* TR_STATIC */
"Statisch",
/* TR_SUGGEST_IO */
"(voorstel %x)",
/* TR_SUGGEST_IRQ */
"(voorstel %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"Deze drivermodule is al geladen.",
/* TR_TIMEZONE */
"Tijdzone",
/* TR_TIMEZONE_LONG */
"Kies de tijdzone waar u zich bevindt uit de lijst hieronder.",
/* TR_UNABLE_TO_EJECT_CDROM */
"Kan de CDROM niet uitwerpen.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Kan de modules niet uitpakken.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Kan geen additionele drivers vinden.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Kan geen ISDN-kaart vinden in deze computer. U kunt extra module parameters opgeven als het een ISA-kaart betreft of als het speciale eisen heeft.",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"Kan de ISDN-kaart niet initialiseren.",
/* TR_UNABLE_TO_INSTALL_FILES */
"Kan de bestanden niet installeren.",
/* TR_UNABLE_TO_INSTALL_LANG_CACHE */
"Kan de taalbestanden niet installeren.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"Kan GRUB niet installeren.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Kan de drivermodule niet laden.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Kan het boot bestandssysteem niet aanmaken.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Kan het log bestandssysteem niet aanmaken.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Kan het root bestandssysteem niet aanmaken.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Kan het swap bestandssysteem niet aanmaken.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Kan de symlink /dev/harddisk niet aanmaken.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Kan de symlink /dev/harddisk1 niet aanmaken.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Kan de symlink /dev/harddisk2 niet aanmaken.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Kan de symlink /dev/harddisk3 niet aanmaken.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Kan de symlink /dev/harddisk4 niet aanmaken.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Kan de symlink /dev/root niet aanmaken.",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Kan het boot bestandssysteem niet koppelen.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Kan het log bestandssysteem niet koppelen.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Kan het proc bestandssysteem niet koppelen.",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Kan het root bestandssysteem niet koppelen.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Kan de swap partitie niet koppelen.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Kan het hosts-bestand niet openen.",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Kan het instellingenbestand niet openen",
/* TR_UNABLE_TO_PARTITION */
"Kan de schijf niet partitioneren.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"Kan de tijdelijke gedownloade bestanden niet verwijderen.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"Kan de hostnaam niet instellen.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"Kan het CDROM-/diskettestation niet ontkoppelen.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"Kan de vaste schijf niet ontkoppelen.",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"Kan /etc/fstab niet wegschrijven",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"Kan /etc/hostname niet wegschrijven",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"Kan /etc/hosts niet wegschrijven.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"Kan /etc/hosts.allow niet wegschrijven.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"Kan /etc/hosts.deny niet wegschrijven.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"Kan %s/ethernet/settings niet wegschrijven.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"Kan %s/main/hostname.conf niet wegschrijven.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"Kan %s/main/settings niet wegschrijven.",
/* TR_UNCLAIMED_DRIVER */
"Er is een ongebruikte ethernetkaart van het type:\n%s\n\nU kunt deze toewijzen aan:",
/* TR_UNKNOWN */
"ONBEKEND",
/* TR_UNSET */
"NIET INGESTELD",
/* TR_USB_KEY_VFAT_ERR */
"Deze USB-sleutel is ongeldig (geen vfat partitie gevonden).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"WAARSCHUWING",
/* TR_WARNING_LONG */
"Als u dit IP-adres wijzigt, en u bent op afstand ingelogd, dan zal de verbinding naar de %s machine worden verbroken en u zult opnieuw moeten verbinden naar het nieuwe IP-adres. Dit is een riskante handeling en moet alleen geprobeerd worden als u fysieke toegang tot de machine hebt, in het geval er iets fout gaat.",
/* TR_WELCOME */
"Welkom bij het %s installatieprogramma. Als u 'annuleren' kiest op een van de volgende schermen selecteert zal de computer herstarten.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Uw configuratie is ingesteld voor een enkele GROENE interface, welke al een driver toegewezen heeft.",
/* TR_YES */
"Ja",
/* TR_NO */
"Nee",
/* TR_AS */
"als",
/* TR_IGNORE */
"Negeer",
/* TR_PPP_DIALUP */
"PPP DIALUP (PPPoE, modem, ATM ...)",
/* TR_DHCP */
"DHCP",
/* TR_DHCP_STARTSERVER */
"Start DHCP-server ...",
/* TR_DHCP_STOPSERVER */
"Stopt DHCP-server ...",
/* TR_LICENSE_ACCEPT */
"Ik accepteer deze licentie.",
/* TR_LICENSE_NOT_ACCEPTED */
"Licentie niet geaccepteerd. Stopt!",
/* TR_EXT2FS_DESCR */
"Ext2 - Bestandssysteem zonder journal (geschikt voor flashdrives)",
/* TR_EXT3FS_DESCR */
"Ext3 - Bestandssysteem met journal",
/* TR_EXT4FS_DESCR */
"Ext4 - Bestandssysteem met journal",
/* TR_REISERFS_DESCR */
"ReiserFS - Bestandssysteem met journal",
/* TR_NO_LOCAL_SOURCE */
"Geen lokale bronmedia gevonden. Start download.",
/* TR_DOWNLOADING_ISO */
"Downloaden van installatie-image ...",
/* TR_DOWNLOAD_ERROR */
"Fout tijdens downloaden!",
/* TR_DHCP_FORCE_MTU */
"Forceer DHCP mtu:",
/* TR_IDENTIFY */
"Identify",
/* TR_IDENTIFY_SHOULD_BLINK */
"Selected port should blink now ...",
/* TR_IDENTIFY_NOT_SUPPORTED */
"Function is not supported by this port.",
};
