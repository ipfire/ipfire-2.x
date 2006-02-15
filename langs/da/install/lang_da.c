/*
 * Danish (da) Data File
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
 * (c) 2003 Michael Rasmussen
 *  
 */
 
#include "libsmooth.h"

char *da_tr[] = {

/* TR_ADDRESS_SETTINGS */
"Adresseindstilling",
/* TR_ADMIN_PASSWORD */
"Admin password",
/* TR_AGAIN_PROMPT */
"Igen:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Alle kort fik korrekt tildelt driver.",
/* TR_AUTODETECT */
"* AUTOSØGNING *",
/* TR_BUILDING_INITRD */
"Bygger INITRD...",
/* TR_CANCEL */
"Afbryd",
/* TR_CARD_ASSIGNMENT */
"Tildel kort",
/* TR_CHECKING */
"Undersøger URL...",
/* TR_CHECKING_FOR */
"Undersøger for: %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Vælg ISDN kort installeret i denne computer.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Vælg den ISDN protokol du bruger.",
/* TR_CONFIGURE_DHCP */
"Konfigurer DHCP serveren ved at indtaste information om indstilling.",
/* TR_CONFIGURE_NETWORKING */
"Konfigurer netværket",
/* TR_CONFIGURE_NETWORKING_LONG */
"Du skal nu konfigurere netværketet ved først at indlæse korrekt driver for det GRØNNE interface. Du kan gøre dette enten ved autosøgning for et netkort, eller ved at vælge korrekt driver fra en liste. Bemærk, hvis du har mere end et netkort installeret, er det muligt senere i installationen at konfigurere de øvrige netkort. Bemærk også, hvis du har flere end et kort af samme type som det GRØNNE, og hvert netkort kræver særlige parametre, skal du indtaste parametre for alle kort samtidigt, så alle netkort kan aktiveres, når du skal konfigurere det GRØNNE interface.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Konfigurer netværksdriver og hvilket interface, hvert kort skal tildeles.  Nuværende konfiguration ser ud på følgende måde:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"Konfigurer CDROM drevet ved at vælge korrekt IO adresse og/eller IRQ.",
/* TR_CONGRATULATIONS */
"Tillykke!",
/* TR_CONGRATULATIONS_LONG */
"Installering af %s gik godt. Fjern venligst enhver diskette eller CDROM fra maskinen. Setup vil nu blive afviklet, så du kan konfigurere ISDN,  netværkskort og system password. Efter gennemførelse af Setup skal du kalde adressen http://%s:81 eller https://%s:445 (eller det navn du gav din %s) fra din browser, og konfigurere din modemforbindelse (hvis det er krævet) og fjernadgang. Husk at angive et password for %s 'dial' brugeren, hvis du vil have, at ingen %s 'admin' brugere skal kunne kontrollere forbindelsen.",
/* TR_CONTINUE_NO_SWAP */
"Din harddisk er meget lille, du kan dog forsætte uden aktivering af swap. (Kan ikke anbefales).",
/* TR_CURRENT_CONFIG */
"Nuværende konfiguration: %s%s",
/* TR_DEFAULT_GATEWAY */
"Forvalgt Gateway:",
/* TR_DEFAULT_GATEWAY_CR */
"Forvalgt Gateway\n",
/* TR_DEFAULT_LEASE */
"Forvalgt udløb (min):",
/* TR_DEFAULT_LEASE_CR */
"Forvalgt udløbstid\n",
/* TR_DETECTED */
"Fundet et: %s",
/* TR_DHCP_HOSTNAME */
"DHCP hostnavn:",
/* TR_DHCP_HOSTNAME_CR */
"DHCP hostnavn\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"DHCP server konfiguration",
/* TR_DISABLED */
"Deaktiveret",
/* TR_DISABLE_ISDN */
"Deaktiver ISDN",
/* TR_DISK_TOO_SMALL */
"Din harddisk er for lille.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"DNS og Gateway indstillinger",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Indtast DNS og gateway information.  Disse indstillinger bliver kun brugt, hvis DHCP er deaktiveret på det RØDE interface.",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Din konfiguration indeholder ikke opsætning af et ethernet kort for det RØDE interface.  DNS og Gateway information for ring op brugere vil blive konfigureret automatisk på opringningstidspunktet.",
/* TR_DOMAINNAME */
"Domænenavn",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Domænenavn skal være udfyldt.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"Domænenavn må ikke indeholde mellemrum.",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Domænenavn må kun indeholde bogstaver, numre, bindestreger og punkttummer.",
/* TR_DOMAIN_NAME_SUFFIX */
"Domænenavn suffix:",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Domænenavn suffix\n",
/* TR_DONE */
"Udført",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\nØnsker du at ændre disse indstillinger?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Driver og kort indstillinger",
/* TR_ENABLED */
"Aktiveret",
/* TR_ENABLE_ISDN */
"Aktiver ISDN",
/* TR_END_ADDRESS */
"Slut adresse:",
/* TR_END_ADDRESS_CR */
"Slut adresse\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Nogle ISDN kort (specielt ISA kort) kræver muligvis ekstra modulparametre for at indstille IRQ og IO adresse information. Hvis du har et sådan ISDN kort, skal du indtaste disse parametre her. For eksempel: \"io=0x280 irq=9\". De bliver brugt ved søgning af kort.",
/* TR_ENTER_ADMIN_PASSWORD */
"Indtast %s admin password.  Det er denne bruger, der skal benyttes, når du skal have adgang til %s web administrationsiderne.",
/* TR_ENTER_DOMAINNAME */
"Indtast domænenavn",
/* TR_ENTER_HOSTNAME */
"Indtast hostnavn for maskinen.",
/* TR_ENTER_IP_ADDRESS_INFO */
"Indtast IP adresse information",
/* TR_ENTER_NETWORK_DRIVER */
"Automatisk detektering af netkort fejlede. Indtast driver og valgfrie parametre for netkortet.",
/* TR_ENTER_ROOT_PASSWORD */
"Indtast 'root' brugerens password. Login som denne bruger giver kommandolinje adgang.",
/* TR_ENTER_SETUP_PASSWORD */
"Indtast 'setup' brugerens password. Login som denne bruger for at få adgang til setup programmet.",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Indtast IP adresse information for %s interfacet.",
/* TR_ENTER_THE_LOCAL_MSN */
"Indtast det lokale telefonnummer (MSN/EAZ).",
/* TR_ENTER_URL */
"Indtast URL til ipcop-<version>.tgz og images/scsidrv-<version>.img filer. ADVARSEL: DNS er ikke tilgængelig! Derfor skal dette kun være http://X.X.X.X/<katalog>",
/* TR_ERROR */
"Fejl",
/* TR_ERROR_WRITING_CONFIG */
"Fejl ved skrivning af konfigurationsinformation.",
/* TR_EURO_EDSS1 */
"Euro (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Udpakker moduler...",
/* TR_FAILED_TO_FIND */
"Kunne ikke finde URL fil.",
/* TR_FOUND_NIC */
"%s har fundet det følgende NIC i din maskine: %s",
/* TR_GERMAN_1TR6 */
"Tysk 1TR6",
/* TR_HELPLINE */
"              <Tab>/<Alt-Tab> Imellem elementer   |  <Mellemrum> vælger",
/* TR_HOSTNAME */
"Hostnavn",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Hostnavn skal være udfyldt.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"Hostnavn må ikke indeholde blanktegn.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"Hostnavnet må kun indeholde bogstaver, numre og bindestreger.",
/* TR_INITIALISING_ISDN */
"Initialiserer ISDN...",
/* TR_INSERT_CDROM */
"Indsæt venligst %s CD i CDROM drevet.",
/* TR_INSERT_FLOPPY */
"Indsæt venligst disketten med %s drivere til netværk i diskette drevet.",
/* TR_INSTALLATION_CANCELED */
"Installation er afbrudt.",
/* TR_INSTALLING_FILES */
"Installerer filer...",
/* TR_INSTALLING_GRUB */
"Installerer GRUB...",
/* TR_INTERFACE */
"%s interface",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"Interface kunne ikke aktiveres.",
/* TR_INVALID_FIELDS */
"De følgende felter er ulovlige:\n\n",
/* TR_INVALID_IO */
"Den valgte IO adresse er ulovlig. ",
/* TR_INVALID_IRQ */
"Det valgte IRQ nummer er ulovlig.",
/* TR_IP_ADDRESS_CR */
"IP adresse\n",
/* TR_IP_ADDRESS_PROMPT */
"IP adresse:",
/* TR_ISDN_CARD */
"ISDN kort",
/* TR_ISDN_CARD_NOT_DETECTED */
"ISDN kort er ikke blevet fundet. Du skal angive ekstra modulparametre, hvis kortet er af typen ISA, eller det har andre specielle krav.",
/* TR_ISDN_CARD_SELECTION */
"ISDN kortvalg",
/* TR_ISDN_CONFIGURATION */
"ISDN konfiguration",
/* TR_ISDN_CONFIGURATION_MENU */
"ISDN cknfigurationsmenu",
/* TR_ISDN_NOT_SETUP */
"ISDN er ikke sat op. Nogle emner er ikke valgt.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"ISDN er ikke blevet konfigureret endnu. Vælg det emne du ønsker at konfigurere.",
/* TR_ISDN_PROTOCOL_SELECTION */
"ISDN protokol udvælgelse",
/* TR_ISDN_STATUS */
"ISDN er i øjeblikket %s.\n\n   Protokol: %s\n   Kort: %s\n   Lokalt telefonnummer: %s\n\nVælg det emne du ønsker at rekonfigurere, eller vælg nuværende opsætning.",
/* TR_KEYBOARD_MAPPING */
"Tastaturudlægning",
/* TR_KEYBOARD_MAPPING_LONG */
"Vælg den type af tastatur, du benytter, fra listen nedenfor.",
/* TR_LEASED_LINE */
"Leased line",
/* TR_LOADING_MODULE */
"Indlæser modul...",
/* TR_LOADING_PCMCIA */
"Indlæser PCMCIA moduler...",
/* TR_LOOKING_FOR_NIC */
"Leder efter: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Opretter boot filsystemet...",
/* TR_MAKING_LOG_FILESYSTEM */
"Opretter log filsystemet...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Laver root filsystemet...",
/* TR_MAKING_SWAPSPACE */
"Opretter swapfilen...",
/* TR_MANUAL */
"* MANUEL *",
/* TR_MAX_LEASE */
"Maksimal udløb (min):",
/* TR_MAX_LEASE_CR */
"Maksimal udløbstid\n",
/* TR_MISSING_BLUE_IP */
"Mangler IP information for det BLÅ interface.",
/* TR_MISSING_ORANGE_IP */
"Mangler IP information for det ORANGE interface.",
/* TR_MISSING_RED_IP */
"Mangler IP information for det RØDE interface.",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"Modulnavn kan ikke være blank.",
/* TR_MODULE_PARAMETERS */
"Indtast modulnavn og parametre for den ønskede driver.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Monterer boot filsystemet...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Monterer log filsystemet...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Monterer root filsystemet...",
/* TR_MOUNTING_SWAP_PARTITION */
"Monterer swap partitionen...",
/* TR_MSN_CONFIGURATION */
"Lokalt telefonnummer (MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Netværksmaske:",
/* TR_NETWORKING */
"Netværk",
/* TR_NETWORK_ADDRESS_CR */
"Netværksadresse\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Netværksadresse:",
/* TR_NETWORK_CONFIGURATION_MENU */
"Netværk konfigurationsmenu",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Network konfigurationstype",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Vælg netværkskonfiguration for %s. De følgende konfigurationstyper har interfaces med tildelt ethernet. Ændrer du disse indstillinger, skal netværket genstartes, og du må samtidigt rekonfigurere indstillingerne for netværksdriverne.",
/* TR_NETWORK_MASK_CR */
"Netværksmaske\n",
/* TR_NETWORK_SETUP_FAILED */
"Opsætning af netværk fejlede.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"Du har ikke tildelt et tilstrækkeligt antal kort.",
/* TR_NO_BLUE_INTERFACE */
"Intet BLÅT interface tilsluttet.",
/* TR_NO_CDROM */
"Kunne ikke finde CD-ROM.",
/* TR_NO_HARDDISK */
"Kunne ikke finde en harddisk.",
/* TR_NO_IPCOP_TARBALL_FOUND */
"Ingen ipcop tar-pakke fundet på webserveren.",
/* TR_NO_ORANGE_INTERFACE */
"Intet ORANGE interface tildelt.",
/* TR_NO_RED_INTERFACE */
"Intet RØDT interface tildelt.",
/* TR_NO_SCSI_IMAGE_FOUND */
"Intet SCSI image fundet på webserveren.",
/* TR_NO_UNALLOCATED_CARDS */
"Der findes ikke flere utildelte kort, flere kort kræves. Du kan bruge autosøgning og lede efter flere kort, eller vælge en driver fra listen.",
/* TR_OK */
"Ok",
/* TR_PARTITIONING_DISK */
"Partitionere harddisken...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"Passwords er forskellige.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"Password må ikke være blankt.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"Password må ikke indeholde blanktegn.",
/* TR_PASSWORD_PROMPT */
"Password:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Telefonnummer skal angives.",
/* TR_PREPARE_HARDDISK */
"Installationsprogrammet vil nu forberede harddisken på %s. Først bliver disken partitioneret, og bagefter bliver der skrevet et filsystem på partitionerne.",
/* TR_PRESS_OK_TO_REBOOT */
"Tryk Ok for at genstarte.",
/* TR_PRIMARY_DNS */
"Primær DNS:",
/* TR_PRIMARY_DNS_CR */
"Primær DNS\n",
/* TR_PROBE */
"Søg",
/* TR_PROBE_FAILED */
"Automatisk undersøgelse fejlede.",
/* TR_PROBING_SCSI */
"Søger efter SCSI enheder...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"Fejl ved skrivning af %s admin password.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"Fejl under skrivning af 'root' password.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"Fejl under skrivning af 'setup' password.",
/* TR_PROTOCOL_COUNTRY */
"Protokol/land",
/* TR_PULLING_NETWORK_UP */
"Åbner for netværk...",
/* TR_PUSHING_NETWORK_DOWN */
"Lukker for netværk...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Lukker eksternt nedværk ned...",
/* TR_QUIT */
"Slut",
/* TR_RED_IN_USE */
"ISDN (eller en anden ekstern forbindelse) er aktiv i øjeblikket.  Du kan ikke konfigurere ISDN mens det RØDE interface er aktivt.",
/* TR_RESTART_REQUIRED */
"\n\nNår konfiguration er gennemført, skal netværket genstartes.",
/* TR_RESTORE */
"Genskab",
/* TR_RESTORE_CONFIGURATION */
"Hvis du har en diskette med en konfigurationsfil for %s, skal du indsætte den i diskettedrevet, og trykke på knappen for genskab.",
/* TR_ROOT_PASSWORD */
"'root' password",
/* TR_SECONDARY_DNS */
"Sekondær DNS:",
/* TR_SECONDARY_DNS_CR */
"Sekondær DNS\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"Sekondær DNS er angivet uden en Primær DNS",
/* TR_SECTION_MENU */
"Menu sektion",
/* TR_SELECT */
"Vælg",
/* TR_SELECT_CDROM_TYPE */
"Vælg CDROM type",
/* TR_SELECT_CDROM_TYPE_LONG */
"Ingen CDROM blev fundet i denne maskine.  Vælg venligst en af følgende drivere, du vil benytte, så %s kan tilgå CDROM drevet.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Vælg installationsmedie",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s kan installeres fra flere kilder.  Det enkleste er at benytte maskinens CDROM drev. Findes der ikke CDROM drev på maskinen, kan du installere via en anden maskine på netværket, der har installationsfiler tilgængelig via HTTP. I dette tilfælde er disketten med drivere til netværk påkrævet.",
/* TR_SELECT_NETWORK_DRIVER */
"Vælg netværksdriver",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Vælg netværksdriver for det installerede kort i denne maskine. Valgte du MANUEL, får du mulighed for at indtaste moduldriver navn og parametre for driveren, dersom den kræver specielle indstillinger, såsom et ISA kort.",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Vælg det interface du vil rekonfigurere.",
/* TR_SELECT_THE_ITEM */
"Vælg det emne du ønsker at konfigurere.",
/* TR_SETTING_ADMIN_PASSWORD */
"Skriver %s admin password....",
/* TR_SETTING_ROOT_PASSWORD */
"Skriver 'root' password....",
/* TR_SETTING_SETUP_PASSWORD */
"Skriver 'setup' password....",
/* TR_SETUP_FINISHED */
"Setup er færdig.  Pres Ok for at genstarte.",
/* TR_SETUP_NOT_COMPLETE */
"Initial setup blev ikke fuldt gennemført.  Du skal sikre dig, at Setup er korrekt afsluttet ved at afvikle setup igen fra en shell.",
/* TR_SETUP_PASSWORD */
"'setup' password",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Tilføj ekstra modulparametre",
/* TR_SINGLE_GREEN */
"Din konfiguration er indstillet til et enkelt GRØNT interface.",
/* TR_SKIP */
"Spring over",
/* TR_START_ADDRESS */
"Start adresse:",
/* TR_START_ADDRESS_CR */
"Start adresse\n",
/* TR_STATIC */
"Statisk",
/* TR_SUGGEST_IO */
"(prøv %x)",
/* TR_SUGGEST_IRQ */
"(prøv %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"Dette driver modul er allerede indlæst.",
/* TR_TIMEZONE */
"Tidszone",
/* TR_TIMEZONE_LONG */
"Vælg din tidszone fra nedenstående liste.",
/* TR_UNABLE_TO_EJECT_CDROM */
"Kunne ikke åbne CDROM drevet.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Det var ikke muligt at udpakke modulerne.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Kunne ikke finde ekstra drivere.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Det var ikke muligt at finde et ISDN kort i denne computer. Du skal angive ekstra modulparametre, hvis kortet er af typen ISA, eller det har andre specielle krav.",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"Initialisering af ISDN var ikke mulig.",
/* TR_UNABLE_TO_INSTALL_FILES */
"Installering af filer var ikke mulig.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"Installering af GRUB var ikke mulig.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Driver modul kunne ikke indlæses.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Oprettelse af boot filsystemet var ikke mulig.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Oprettelse af log filsystemet var ikke mulig.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Oprettelse af root filsystemet var ikke mulig.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Oprettelse af swapfilen var ikke mulig.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Kunne ikke oprette symbolsk link til /dev/harddisk.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Kunne ikke oprette symbolsk link til /dev/harddisk1.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Kunne ikke oprette symbolsk link til /dev/harddisk2.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Kunne ikke oprette symbolsk link til /dev/harddisk3.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Kunne ikke oprette symbolsk link til /dev/harddisk4.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Kunne ikke lave symbolsk link til /dev/root",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Montering af boot filsystemet var ikke mulig.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Montering af log filsystemet var ikke mulig.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Montering af proc filsystemet var ikke mulig.",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Montering af root filsystemet var ikke mulig.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Montering af swap partitionen var ikke mulig.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Kunne ikke åbne hosts-filen.",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Ikke muligt at åbne indstillingsfilen",
/* TR_UNABLE_TO_PARTITION */
"Partitionering af harddisken var ikke mulig.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"Kunne ikke fjerne de midlertidigt hentede filer.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"Kunne ikke sætte hostnavn.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"Afmontering af CDROM/diskettedrev var ikke mulig.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"Afmontering af harddisk var ikke mulig.",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"Kunne ikke skrive /etc/fstab",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"Kunne ikke skrive /etc/hostname",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"Kunne ikke oprette /etc/hosts.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"Kunne ikke oprette /etc/hosts.allow.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"Kunne ikke oprette /etc/hosts.deny.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"Kunne ikke oprette %s/ethernet/settings.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"Kunne ikke oprette %s/main/hostname.conf",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"Kunne ikke oprette %s/main/settings.",
/* TR_UNCLAIMED_DRIVER */
"Der findes et ethernet kort af type:\n%s, der ikke har tildelt nogen driver\n\nDu kan tildele det til:",
/* TR_UNKNOWN */
"UKENDT",
/* TR_UNSET */
"NULSTIL",
/* TR_USB_KEY_VFAT_ERR */
"Denne USB nøgle kan ikke anvendes (ingen vfat partitioner fundet).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"ADVARSEL",
/* TR_WARNING_LONG */
"Hvis du ændrer denne IP adresse, og du er logget på via fjernopkobling, bliver din forbindelse til denne %s maskine afbrudt, og du vil derfor skulle oprette forbindelse til den nye IP adresse. Dette er en risikabel operation, og bør kun gennemføres, hvis du har fysisk adgang til maskinen, i tilfælde af at noget går galt.",
/* TR_WELCOME */
"Velkommen til %ss installationsprogram. Hvis du vælger afbryd på nogen af de følgende skærmbilleder, vil få maskinen til at genstarte.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Du har kun konfigureret for et enkelt GRØNT interface, der allerede har tildelt en driver.",
}; 
  
