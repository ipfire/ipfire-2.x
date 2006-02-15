/*
 * Norwegian (no) Data File
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
 * (c) 2003 Morten Grendal, Alexander Dawson, Mounir S. Chermiti, 
 * Runar Skraastad, Alf-Ivar Holm
 * 
 *  
 */
 
#include "libsmooth.h"

char *no_tr[] = {

/* TR_ADDRESS_SETTINGS */
"Adresseinnstillinger",
/* TR_ADMIN_PASSWORD */
"Adminpassord",
/* TR_AGAIN_PROMPT */
"Gjenta:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Alle kort fikk tildelt drivere.",
/* TR_AUTODETECT */
"* AUTOSØK *",
/* TR_BUILDING_INITRD */
"Bygger INITRD...",
/* TR_CANCEL */
"Avbryt",
/* TR_CARD_ASSIGNMENT */
"Tildel kort",
/* TR_CHECKING */
"Sjekker URL...",
/* TR_CHECKING_FOR */
"Søker etter: %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Velg ISDN-kortet som er installert i denne maskinen.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Velg ISDN-protokollen du behøver.",
/* TR_CONFIGURE_DHCP */
"Sett opp DHCP-tjeneren ved å skrive inn innstillingsinformasjonen.",
/* TR_CONFIGURE_NETWORKING */
"Oppsett av nettverket",
/* TR_CONFIGURE_NETWORKING_LONG */
"Du skal nå sette opp nettverket ved først å laste korrekt driver for det GRØNNE grensesnittet. Du kan gjøre dette enten ved autosøking etter nettverkskort, eller ved å velge riktig driver fra en liste. Merk deg at hvis du har mer enn ett nettverkskort vil du kunne sette opp de andre senere i installasjonen. Hvis du har mer enn ett kort av samme type som det GRØNNE og hvert kort krever spesielle modulparametere bør du skrive inn parametere for alle kort samtidig, slik at alle kort kan bli aktivert når du setter opp det GRØNNE grensesnittet.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Sett opp nettverksdrivere og hvilket grensesnitt hvert kort skal tildeles.  Gjeldende oppsett er som følger:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"Konfigurer CDROM ved å velge riktig IO-adresse og/eller IRQ.",
/* TR_CONGRATULATIONS */
"Gratulerer!",
/* TR_CONGRATULATIONS_LONG */
"Installasjonen av %s var vellykket. Fjern evt. diskett eller CDROM fra maskinen. Nå kjøres oppsettet, hvor du kan sette opp ISDN, nettverkskort og systempassordene. Etter at oppsettet er fullført bør du åpne http://%s:81 eller https://%s:445 (eller hva du har kalt din %s) i nettleseren din, og sette opp oppringt forbindelse (hvis nødvendig) og fjerntilgang. Husk å sette et passord for %s modembruker hvis du ønsker at andre enn %s administratorer skal kunne kontrollere forbindelsen.",
/* TR_CONTINUE_NO_SWAP */
"Harddisken din er veldig liten, men du kan fortsette uten vekslefil (brukes med varsomhet).",
/* TR_CURRENT_CONFIG */
"Gjeldende oppsett: %s%s",
/* TR_DEFAULT_GATEWAY */
"Standard gateway:",
/* TR_DEFAULT_GATEWAY_CR */
"Standard gateway\n",
/* TR_DEFAULT_LEASE */
"Standard leietid (min.):",
/* TR_DEFAULT_LEASE_CR */
"Standard leietid\n",
/* TR_DETECTED */
"Fant et: %s",
/* TR_DHCP_HOSTNAME */
"DHCP-vertsnavn:",
/* TR_DHCP_HOSTNAME_CR */
"DHCP-vertsnavn\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"DHCP-tjeneroppsett",
/* TR_DISABLED */
"Deaktivert",
/* TR_DISABLE_ISDN */
"Deaktiver ISDN",
/* TR_DISK_TOO_SMALL */
"Harddisken din er for liten.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"DNS- og gatewayinnstillinger",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Skriv inn DNS- og gatewayinformasjon. Disse innstillingene blir bare brukt hvis DHCP er deaktivert på det RØDE grensesnittet.",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Gjeldende oppsett benytter ikke et ethernetkort for sitt RØDE grensesnitt.  DNS- og gatewayinformasjon for oppringte brukere blir satt opp automatisk når oppringning foretas.",
/* TR_DOMAINNAME */
"Domenenavn",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Domenenavn kan ikke være tomt.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"Domenenavn kan ikke inneholde mellomrom.",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Domenenavn kan bare inneholde bokstaver, tall, bindestrek og punktum.",
/* TR_DOMAIN_NAME_SUFFIX */
"Domenenavnsuffiks:",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Domenenavnsuffiks\n",
/* TR_DONE */
"Ferdig",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\nVil du endre disse innstillingene?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Tildeling av kort og drivere",
/* TR_ENABLED */
"Aktivert",
/* TR_ENABLE_ISDN */
"Aktiver ISDN",
/* TR_END_ADDRESS */
"Sluttadresse:",
/* TR_END_ADDRESS_CR */
"Sluttadresse\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Noen ISDN-kort (spesielt ISA) behøver ekstra modulparametere for å sette IRQ- og IO-adresseinformasjon. Hvis du har et slikt ISDN-kort kan du skrive inn disse ekstra parameterene her. F.eks.: \"io=0x280 irq=9\". Dette vil bli brukt ved søking etter kort.",
/* TR_ENTER_ADMIN_PASSWORD */
"Skriv inn %s 'admin'-passord. Denne brukeren benyttes ved innlogging på %s vevadministrasjonssidene.",
/* TR_ENTER_DOMAINNAME */
"Skriv inn domenenavn",
/* TR_ENTER_HOSTNAME */
"Skriv inn maskinens vertsnavn.",
/* TR_ENTER_IP_ADDRESS_INFO */
"Skriv inn IP-adresseinformasjonen",
/* TR_ENTER_NETWORK_DRIVER */
"Klarte ikke finne nettverkskort automatisk. Skriv inn driveren og eventuelle parametere for nettverkskortet.",
/* TR_ENTER_ROOT_PASSWORD */
"Skriv inn 'root'-passordet. Logg inn som 'root' for kommandolinjetilgang.",
/* TR_ENTER_SETUP_PASSWORD */
"Skriv inn 'setup'-passord. Logg inn som 'setup' for tilgang til oppsettprogrammet.",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Skriv inn IP-adresseinformasjonen for %s grensesnitt.",
/* TR_ENTER_THE_LOCAL_MSN */
"Skriv inn lokalt telefonnummer (MSN/EAZ).",
/* TR_ENTER_URL */
"Skriv inn URL-banen til filene ipcop-<versjon>.tgz og images/scsidrv-<versjon>.img. OBS: DNS er ikke tilgjengelig! Adressen skal være i formatet http://X.X.X.X/<mappe>",
/* TR_ERROR */
"Feil",
/* TR_ERROR_WRITING_CONFIG */
"Feil ved skriving av oppsettinformasjon.",
/* TR_EURO_EDSS1 */
"Euro (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Pakker ut moduler...",
/* TR_FAILED_TO_FIND */
"Klarte ikke finne URL-filen.",
/* TR_FOUND_NIC */
"%s fant følgende nettverkskort i maskinen: %s",
/* TR_GERMAN_1TR6 */
"Tysk 1TR6",
/* TR_HELPLINE */
"             <Tab>/<Alt-Tab> mellom elementer  |  <Mellomrom> velger",
/* TR_HOSTNAME */
"Vertsnavn",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Vertsnavn kan ikke være blankt.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"Vertsnavn kan ikke inneholde mellomrom.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"Vertsnavn kan bare inneholde bokstaver, tall og bindestreker.",
/* TR_INITIALISING_ISDN */
"Starter ISDN...",
/* TR_INSERT_CDROM */
"Sett inn %s CD-en i CDROM-spilleren.",
/* TR_INSERT_FLOPPY */
"Sett inn %s driverdiskett i diskettstasjonen.",
/* TR_INSTALLATION_CANCELED */
"Installasjon avbrutt.",
/* TR_INSTALLING_FILES */
"Installerer filer...",
/* TR_INSTALLING_GRUB */
"Installerer GRUB...",
/* TR_INTERFACE */
"%s grensesnitt",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"Grensesnittet startet ikke.",
/* TR_INVALID_FIELDS */
"Følgende felt er ugyldige:\n\n",
/* TR_INVALID_IO */
"Valgt IO-adresse er ugyldig. ",
/* TR_INVALID_IRQ */
"Valgt IRQ er ugyldig.",
/* TR_IP_ADDRESS_CR */
"IP-adresse\n",
/* TR_IP_ADDRESS_PROMPT */
"IP-adresse:",
/* TR_ISDN_CARD */
"ISDN-kort",
/* TR_ISDN_CARD_NOT_DETECTED */
"ISDN-kort ikke funnet. Du må kanskje angi ekstra modulparametere hvis kortet er av typen ISA eller det har spesielle krav.",
/* TR_ISDN_CARD_SELECTION */
"ISDN-kort valg",
/* TR_ISDN_CONFIGURATION */
"ISDN-oppsett",
/* TR_ISDN_CONFIGURATION_MENU */
"ISDN-oppsettmeny",
/* TR_ISDN_NOT_SETUP */
"ISDN ikke satt opp. Noen punkter har ikke blitt valgt.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"ISDN har ikke blitt satt opp enda. Velg punktet du vil sette opp.",
/* TR_ISDN_PROTOCOL_SELECTION */
"ISDN-protokollvalg",
/* TR_ISDN_STATUS */
"Gjeldende ISDN er %s.\n\n   Protokoll: %s\n   Kort: %s\n   Lokalt telefonnummer: %s\n\nVelg punktet du vil endre, eller bruk gjeldende innstillinger.",
/* TR_KEYBOARD_MAPPING */
"Tastaturoppsett",
/* TR_KEYBOARD_MAPPING_LONG */
"Velg typen tastatur du bruker ved å velge fra listen under.",
/* TR_LEASED_LINE */
"Leid linje",
/* TR_LOADING_MODULE */
"Laster modul...",
/* TR_LOADING_PCMCIA */
"Laster PCMCIA-moduler...",
/* TR_LOOKING_FOR_NIC */
"Søker etter: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Oppretter bootfilsystem...",
/* TR_MAKING_LOG_FILESYSTEM */
"Oppretter loggfilsystem...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Oppretter rootfilsystem...",
/* TR_MAKING_SWAPSPACE */
"Oppretter veksleområde...",
/* TR_MANUAL */
"* MANUELL *",
/* TR_MAX_LEASE */
"Maks leietid (min.):",
/* TR_MAX_LEASE_CR */
"Maks leietid\n",
/* TR_MISSING_BLUE_IP */
"Mangler IP-informasjon for BLÅTT grensesnitt.",
/* TR_MISSING_ORANGE_IP */
"Mangler IP-informasjon for ORANSJE grensesnitt.",
/* TR_MISSING_RED_IP */
"Mangler IP-informasjon for RØDT grensesnitt.",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"Modulnavnet kan ikke være blankt.",
/* TR_MODULE_PARAMETERS */
"Skriv inn modulnavnet og parametere for den ønskede driveren.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Monterer bootfilsystem...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Monterer loggfilsystem...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Monterer rootfilesystem...",
/* TR_MOUNTING_SWAP_PARTITION */
"Monterer swapområde...",
/* TR_MSN_CONFIGURATION */
"Lokalt telefonnummer (MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Nettverksmaske:",
/* TR_NETWORKING */
"Nettverk",
/* TR_NETWORK_ADDRESS_CR */
"Nettverksadresse\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Nettverksadresse:",
/* TR_NETWORK_CONFIGURATION_MENU */
"Nettverksoppsettmeny",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Velg nettverksoppsett",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Velg nettverksoppsett for %s. Følgende typer oppsett viser grensesnittene som har ethernet tilkoblet. Hvis du endrer dette oppsettet må nettverket startes på nytt, og du må sette opp tildelingen av nettverksdriver på nytt.",
/* TR_NETWORK_MASK_CR */
"Nettverksmaske\n",
/* TR_NETWORK_SETUP_FAILED */
"Nettverksoppsett feilet.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"For få kort er tildelt.",
/* TR_NO_BLUE_INTERFACE */
"BLÅTT grensesnitt ikke tildelt.",
/* TR_NO_CDROM */
"Ingen CD-ROM funnet.",
/* TR_NO_HARDDISK */
"Ingen harddisk funnet.",
/* TR_NO_IPCOP_TARBALL_FOUND */
"Fant ikke IPCop-tarball på vevtjeneren.",
/* TR_NO_ORANGE_INTERFACE */
"ORANSJE grensesnitt ikke tildelt.",
/* TR_NO_RED_INTERFACE */
"RØDT grensesnitt ikke tildelt.",
/* TR_NO_SCSI_IMAGE_FOUND */
"Fant ikke SCSI-image på vevtjeneren.",
/* TR_NO_UNALLOCATED_CARDS */
"Det finnes ikke flere ledige kort, men flere er nødvendig. Du kan bruke autosøk for å finne flere kort, eller velge en driver fra listen.",
/* TR_OK */
"Ok",
/* TR_PARTITIONING_DISK */
"Partisjonerer disken...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"Passordene er ikke like.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"Passordet kan ikke være blankt.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"Passordet kan ikke inneholde mellomrom.",
/* TR_PASSWORD_PROMPT */
"Passord:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Telefonnummer kan ikke være blankt.",
/* TR_PREPARE_HARDDISK */
"Installasjonsprogrammet vil nå forberede harddisken på %s. Først vil disken bli partisjonert, og så vil filsystem bli opprettet på partisjonene.",
/* TR_PRESS_OK_TO_REBOOT */
"Trykk Ok for å starte på nytt.",
/* TR_PRIMARY_DNS */
"Primær DNS:",
/* TR_PRIMARY_DNS_CR */
"Primær DNS\n",
/* TR_PROBE */
"Søk",
/* TR_PROBE_FAILED */
"Autosøk feilet.",
/* TR_PROBING_SCSI */
"Søker etter SCSI-enheter...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"Problem ved setting av 'admin'-passord.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"Problem ved setting av 'root'-passord.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"Problem ved setting av 'setup'-passord.",
/* TR_PROTOCOL_COUNTRY */
"Protokoll/Land",
/* TR_PULLING_NETWORK_UP */
"Tar opp nettverket...",
/* TR_PUSHING_NETWORK_DOWN */
"Tar ned nettverket...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Tar ned eksternt nettverk...",
/* TR_QUIT */
"Avslutt",
/* TR_RED_IN_USE */
"ISDN (eller en annen ekstern tilkobling) er i bruk.  Du kan ikke sette opp ISDN mens RØDT grensesnitt er aktivt.",
/* TR_RESTART_REQUIRED */
"\n\nNår oppsettet er fullført må nettverket startes på nytt.",
/* TR_RESTORE */
"Gjenopprett",
/* TR_RESTORE_CONFIGURATION */
"Hvis du har en diskett med %s systemoppsett, sett den i diskettstasjonen og trykk gjenopprett-knappen.",
/* TR_ROOT_PASSWORD */
"'root'-passord",
/* TR_SECONDARY_DNS */
"Sekundær DNS:",
/* TR_SECONDARY_DNS_CR */
"Sekundær DNS\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"Sekundær DNS er angitt uten en primær DNS",
/* TR_SECTION_MENU */
"Seksjonsmeny",
/* TR_SELECT */
"Velg",
/* TR_SELECT_CDROM_TYPE */
"Velg CDROM-type",
/* TR_SELECT_CDROM_TYPE_LONG */
"Ingen CDROM ble funnet i denne maskinen.  Velg hvilken av de følgende driverene du vil bruke slik at %s kan få tilgang til CDROM-en.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Velg installasjonsmedia",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s kan installeres fra flere kilder. Det enkleste er å bruke maskinens CDROM-spiller. Hvis maskinen ikke har CDROM-spiller, kan du installere fra en annen maskin på nettverket som har installasjonsfilene tilgjengelig via HTTP. I så fall behøves disketten med nettverksdrivere.",
/* TR_SELECT_NETWORK_DRIVER */
"Velg nettverksdriver",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Velg nettverksdriver for kortet som er installert i maskinen. Hvis du velger MANUELL vil du få muligheten til å skrive inn driverens modulnavn og evt. parametere dersom driveren krever spesielle innstillinger, slik som ISA-kort.",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Velg grensesnittet du vil endre.",
/* TR_SELECT_THE_ITEM */
"Velg det du vil sette opp.",
/* TR_SETTING_ADMIN_PASSWORD */
"Setter %s 'admin'-passord...",
/* TR_SETTING_ROOT_PASSWORD */
"Setter 'root'-passord...",
/* TR_SETTING_SETUP_PASSWORD */
"Setter 'setup'-passord....",
/* TR_SETUP_FINISHED */
"Oppsettet er fullført. Trykk Ok for å starte maskinen på nytt.",
/* TR_SETUP_NOT_COMPLETE */
"Grunninstallasjonen ble ikke helt fullført. Du må forsikre deg om at oppsettet er fullstendig ved å kjøre oppsettet igjen fra skallet.",
/* TR_SETUP_PASSWORD */
"'setup'-passord",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Sett ekstra modulparametere",
/* TR_SINGLE_GREEN */
"Gjeldende oppsett er for ett enkelt GRØNT grensesnitt.",
/* TR_SKIP */
"Hopp over",
/* TR_START_ADDRESS */
"Startadresse:",
/* TR_START_ADDRESS_CR */
"Startadresse\n",
/* TR_STATIC */
"Statisk",
/* TR_SUGGEST_IO */
"(prøv %x)",
/* TR_SUGGEST_IRQ */
"(prøv %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"Denne drivermodulen er allerede lastet.",
/* TR_TIMEZONE */
"Tidssone",
/* TR_TIMEZONE_LONG */
"Velg tidssonen du befinner deg i fra listen under.",
/* TR_UNABLE_TO_EJECT_CDROM */
"Klarte ikke løse ut CDROM.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Klarte ikke pakke ut moduler.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Klarte ikke finne ekstra drivere.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Klarte ikke finne et ISDN-kort i denne maskinen. Du må kanskje angi ekstra modulparametere hvis kortet er av typen ISA eller det har spesielle krav.",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"Klarte ikke starte ISDN.",
/* TR_UNABLE_TO_INSTALL_FILES */
"Klarte ikke installere filer.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"Klarte ikke installere GRUB.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Klarte ikke laste drivermodulen.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Klarte ikke opprette bootfilsystem.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Klarte ikke opprette loggfilsystem.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Klarte ikke opprette rootfilsystem.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Klarte ikke opprette veksleområde.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Klarte ikke opprette symlenke /dev/harddisk.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Klarte ikke opprette symlenke /dev/harddisk1.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Klarte ikke opprette symlenke /dev/harddisk2.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Klarte ikke opprette symlenke /dev/harddisk3.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Klarte ikke opprette symlenke /dev/harddisk4.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Klarte ikke opprette symlenke /dev/root.",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Klarte ikke montere bootfilsystem.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Klarte ikke montere loggfilsystem.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Klarte ikke montere procfilsystem.",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Klarte ikke montere rootfilsystem.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Klarte ikke montere veksleområde.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Klarte ikke åpne filen hosts.",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Klarte ikke åpne innstillingsfilen",
/* TR_UNABLE_TO_PARTITION */
"Klarte ikke partisjonere disken.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"Klarte ikke fjerne midlertidig nedlastede filer.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"Klarte ikke sette vertsnavn.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"Klarte ikke demontere CDROM/diskett.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"Klarte ikke demontere harddisk.",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"Klarte ikke skrive /etc/fstab",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"Klarte ikke skrive /etc/hostname",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"Klarte ikke skrive /etc/hosts.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"Klarte ikke skrive /etc/hosts.allow.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"Klarte ikke skrive /etc/hosts.deny.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"Klarte ikke skrive %s/ethernet/innstillinger.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"Klarte ikke skrive %s/main/hostname.conf",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"Klarte ikke skrive %s/main/innstillinger.",
/* TR_UNCLAIMED_DRIVER */
"Et ethernetkort av type:\n%s er ikke tildelt noen driver.\n\nDu kan tildele dette til:",
/* TR_UNKNOWN */
"UKJENT",
/* TR_UNSET */
"IKKE SATT",
/* TR_USB_KEY_VFAT_ERR */
"This USB key is invalid (no vfat partition found).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"ADVARSEL",
/* TR_WARNING_LONG */
"Hvis du endrer denne IP-adressen og du er fjerntilkoblet, vil forbindelsen til %s-maskinen bli brutt, og du må koble til på nytt mot den nye IP-adressen. Dette er en risikabel operasjon, og bør kun gjennomføres hvis du har fysisk tilgang til maskinen - i tilfelle noe skulle gå galt!",
/* TR_WELCOME */
"Velkommen til installasjonsprogrammet for %s. Velger du Avbryt i noen av de følgende skjermbildene vil maskinen startes på nytt.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Du har satt opp ett enkelt GRØNT grensesnitt som allerede er tildelt en driver.",
}; 
  
