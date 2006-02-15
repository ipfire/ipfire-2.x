/*
 * Czech  (cs) Data File
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
 * (c) 2003 petr, Peter Dvoracek, Jakub Moc 
 */
 
#include "libsmooth.h"

char *cs_tr[] = {

/* TR_ADDRESS_SETTINGS */
"Nastavení adres",
/* TR_ADMIN_PASSWORD */
"Heslo uživatele Admin",
/* TR_AGAIN_PROMPT */
"Znovu:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Všechny karty úspěšně přiděleny.",
/* TR_AUTODETECT */
"* AUTODETEKCE *",
/* TR_BUILDING_INITRD */
"Vytvářím INITRD...",
/* TR_CANCEL */
"Zrušit",
/* TR_CARD_ASSIGNMENT */
"Přidělování karet",
/* TR_CHECKING */
"Kontroluji URL...",
/* TR_CHECKING_FOR */
"Kontrola: %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Vyberte instalovanou ISDN kartu.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Vyberte požadovaný ISDN protokol.",
/* TR_CONFIGURE_DHCP */
"Nastavte DHCP server zadáním požadovaných informací.",
/* TR_CONFIGURE_NETWORKING */
"Nastavení sítě",
/* TR_CONFIGURE_NETWORKING_LONG */
"Nyní je nutno nastavit připojení k síti, a to nejprve zavedením odpovídajícího ovladače pro GREEN rozhraní. To lze učinit buď pomocí automatického vyhledání síťové karty, nebo vybráním tohoto ovladače ze seznamu. Pokud máte více síťových karet, budete moci zbývající nastavit později během instalace. Upozorňujeme rovněž, že pokud máte další karty stejného typu, jako je karta GREEN rozhraní a každá z nich vyžaduje zvláštní parametry modulu, měli byste tyto parametry zadat pro všechny karty příslušného typu tak, aby mohly být po nastavení GREEN rozhraní aktivovány.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Nastavte síťové ovladače a přiřaďte karty příslušným rozhraním. Současná konfigurace je následující:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"Nastavte CDROM výběrem odpovídající IO adresy a/nebo IRQ.",
/* TR_CONGRATULATIONS */
"Gratuluji!",
/* TR_CONGRATULATIONS_LONG */
"Instalace %s byla úspěšně dokončena. Prosím vyjměte všechna média (diskety a CDROM), která jsou v mechanikách počítače. Nyní bude spuštěn Setup a budete moci nastavit ISDN, síťové karty a systémová hesla. Po dokončení této fáze se připojte pomocí prohlížeče na adresu http://%s:81 nebo https://%s:445 (nebo upravte adresu podle zvoleného jména počítače, kde je %s nainstalován) a nastavte vytáčené připojení (je-li třeba) a vzdálený přístup. Pokud chcete uživatelům umožnit ovládat připojení, nezapomeňte nastavit heslo pro uživatele 'dial'.",
/* TR_CONTINUE_NO_SWAP */
"Váš pevný disk je velmi malý, ale lze pokračovat bez swap oddílu. (Totu možnost použít jen s opatrností).",
/* TR_CURRENT_CONFIG */
"Aktuální nastavení: %s%s",
/* TR_DEFAULT_GATEWAY */
"Výchozí brána:",
/* TR_DEFAULT_GATEWAY_CR */
"Výchozí brána\n",
/* TR_DEFAULT_LEASE */
"Výchozí čas zapůjčení (min):",
/* TR_DEFAULT_LEASE_CR */
"Výchozí čas zapůjčení\n",
/* TR_DETECTED */
"Nalezen: %s",
/* TR_DHCP_HOSTNAME */
"Jméno DHCP serveru:",
/* TR_DHCP_HOSTNAME_CR */
"Jméno DHCP serveru\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"Nastavení DHCP serveru",
/* TR_DISABLED */
"Vypnutý",
/* TR_DISABLE_ISDN */
"Zakázat ISDN",
/* TR_DISK_TOO_SMALL */
"Váš pevný disk je příliš malý.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"Nastavení DNS a brány",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Zadejte údaje o DNS a bráně. Tato nastavení se používají pouze pokud je DHCP na RED rozhraní zakázáno.",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Vaše nastavení nevyužívá ethernetový adaptér pro RED rozhraní. Údaje o DNS a bráně pro dialup uživatele se nastavují automaticky v okamžiku vytáčení.",
/* TR_DOMAINNAME */
"Doménové jméno",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Jméno domény nesmí být nevyplněné.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"Doménové jméno nesmí obsahovat mezery.",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Jméno domény smí obsahovat pouze písmena, čísla, pomlčky a tečky.",
/* TR_DOMAIN_NAME_SUFFIX */
"Přípona doménového jména:",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Přípona doménového jména\n",
/* TR_DONE */
"Hotovo",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\nChcete změnit tato nastavení?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Přidělení ovladačů a karet",
/* TR_ENABLED */
"Povoleno",
/* TR_ENABLE_ISDN */
"Povolit ISDN",
/* TR_END_ADDRESS */
"Koncová adresa:",
/* TR_END_ADDRESS_CR */
"Koncová adresa\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Některé ISDN karty (zvláště ISA) mohou vyžadovat upřesňující parametry modulu pro nastavení údajů o IRQ a adrese IO portu. Pokud vlastníte takovou kartu, zadejte příslušné parametry zde. Např.: \"io=0x280 irq=9\". Ty budou použity při detekci karty.",
/* TR_ENTER_ADMIN_PASSWORD */
"Zadejte heslo %s admin uživatele. Tento účet slouží k přihlášení k %s webovému administračnímu rozhraní.",
/* TR_ENTER_DOMAINNAME */
"Zadejte doménové jméno",
/* TR_ENTER_HOSTNAME */
"Zadejte jméno počítače.",
/* TR_ENTER_IP_ADDRESS_INFO */
"Zadejte IP adresu",
/* TR_ENTER_NETWORK_DRIVER */
"Automatická detekce síťové karty se nezdařila. Zadejte ovladač a volitelné parametry pro síťovou kartu.",
/* TR_ENTER_ROOT_PASSWORD */
"Zadejte heslo uživatele 'root'. Přihlašte se jako tento uživatel pro přístup prostřednictvím příkazové řádky.",
/* TR_ENTER_SETUP_PASSWORD */
"Zadejte heslo uživatele 'setup'. Přihlašte se jako tento uživatel pro přístup k programu setup.",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Zadejte IP adresu rozhraní %s.",
/* TR_ENTER_THE_LOCAL_MSN */
"Zadejte své telefonní číslo (MSN/EAZ).",
/* TR_ENTER_URL */
"Zadejte cestu (URL) k souborům ipcop-<version>.tgz a images/scsidrv-<version>.img. POZOR: DNS není k dispozici! Cesta by měla být ve tvaru http://X.X.X.X/<adresář>",
/* TR_ERROR */
"Chyba",
/* TR_ERROR_WRITING_CONFIG */
"Chyba při zápisu údajů o nastavení.",
/* TR_EURO_EDSS1 */
"Euro (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Rozbaluji moduly...",
/* TR_FAILED_TO_FIND */
"Vyhledání souboru v daném URL se nezdařilo.",
/* TR_FOUND_NIC */
"%s nalezl ve vašem počítači následující síťový adaptér: %s",
/* TR_GERMAN_1TR6 */
"German 1TR6",
/* TR_HELPLINE */
"                 <Tab>/<Alt-Tab> pro přepnutí | <Space> pro výběr",
/* TR_HOSTNAME */
"Jméno počítače",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Jméno počítače nesmí být nevyplněné.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"Jméno počítače nesmí obsahovat mezery.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"Jméno počítače smí obsahovat pouze písmena, čísla a pomlčky.",
/* TR_INITIALISING_ISDN */
"Inicializuji ISDN...",
/* TR_INSERT_CDROM */
"Prosím vložte %s CD do CDROM mechaniky.",
/* TR_INSERT_FLOPPY */
"Prosím vložte %s disketu s ovladači do disketové mechaniky.",
/* TR_INSTALLATION_CANCELED */
"Instalace zrušena.",
/* TR_INSTALLING_FILES */
"Instaluji soubory...",
/* TR_INSTALLING_GRUB */
"Instaluji GRUB...",
/* TR_INTERFACE */
"%s rozhraní",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"Spuštění rozhraní se nezdařilo.",
/* TR_INVALID_FIELDS */
"Následující pole jsou chybně vyplněna:\n\n",
/* TR_INVALID_IO */
"Zadané údaje o IO portu jsou neplatné.",
/* TR_INVALID_IRQ */
"Zadané údaje o IRQ jsou neplatné.",
/* TR_IP_ADDRESS_CR */
"IP adresa\n",
/* TR_IP_ADDRESS_PROMPT */
"IP adresa:",
/* TR_ISDN_CARD */
"ISDN adaptér",
/* TR_ISDN_CARD_NOT_DETECTED */
"ISDN karta nenalezena. Jestliže se jedná o kartu typu ISA nebo kartu, která má zvláštní požadavky, bude zřejmě nutno zadat upřesňující parametry modulu.",
/* TR_ISDN_CARD_SELECTION */
"Výběr ISDN adaptéru",
/* TR_ISDN_CONFIGURATION */
"Nastavení ISDN",
/* TR_ISDN_CONFIGURATION_MENU */
"Menu pro nastavení ISDN",
/* TR_ISDN_NOT_SETUP */
"ISDN není nastaveno. Některé položky nebyly vybrány.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"ISDN dosud není nastaveno. Zvolte položku, kterou chcete nastavit.",
/* TR_ISDN_PROTOCOL_SELECTION */
"Výběr ISDN protokolu",
/* TR_ISDN_STATUS */
"Současné nastavení ISDN %s\n\n Protokol: %s\n Karta: %s\n Vaše telefonní číslo: %s\n\nZvolte položku, kterou chcete překonfigurovat, nebo můžete použít stávající nastavení.",
/* TR_KEYBOARD_MAPPING */
"Rozložení klávesnice",
/* TR_KEYBOARD_MAPPING_LONG */
"Vyberte typ klávesnice z níže uvedeného seznamu.",
/* TR_LEASED_LINE */
"Pevná linka",
/* TR_LOADING_MODULE */
"Zavádím modul...",
/* TR_LOADING_PCMCIA */
"Zavádím PCMCIA moduly...",
/* TR_LOOKING_FOR_NIC */
"Vyhledávám: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Vytvářím souborový systém /boot...",
/* TR_MAKING_LOG_FILESYSTEM */
"Vytvářím souborový systém /log...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Vytvářím kořenový souborový systém...",
/* TR_MAKING_SWAPSPACE */
"Vytvářím swap oddíl...",
/* TR_MANUAL */
"* RUČNÍ *",
/* TR_MAX_LEASE */
"Max. čas zapůjčení (minuty):",
/* TR_MAX_LEASE_CR */
"Max. čas zapůjčení\n",
/* TR_MISSING_BLUE_IP */
"Chybí údaj o IP adrese BLUE rozhraní.",
/* TR_MISSING_ORANGE_IP */
"Chybí údaj o IP adrese ORANGE rozhraní.",
/* TR_MISSING_RED_IP */
"Chybí údaj o IP adrese RED rozhraní.",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"Jméno modulu nesmí být prázdné.",
/* TR_MODULE_PARAMETERS */
"Zadejte jméno modulu a požadované parametry ovladače.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Připojuji souborový systém /boot...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Připojuji souborový systém /log...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Připojuji kořenový souborový systém...",
/* TR_MOUNTING_SWAP_PARTITION */
"Připojuji swap oddíl...",
/* TR_MSN_CONFIGURATION */
"Vaše telefonní číslo (MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Maska sítě:",
/* TR_NETWORKING */
"Sítě",
/* TR_NETWORK_ADDRESS_CR */
"Adresa sítě\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Adresa sítě:",
/* TR_NETWORK_CONFIGURATION_MENU */
"Menu pro nastavení sítě",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Typ konfigurace sítě",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Vyberte nastavení sítě pro %s. Následující typy konfigurace obsahují seznam rozhraní připojených k ethernetu. Pokud nastavení změníte, bude třeba síť restartovat a rovněž bude nutno nastavit přiřazení síťových ovladačů.",
/* TR_NETWORK_MASK_CR */
"Maska sítě\n",
/* TR_NETWORK_SETUP_FAILED */
"Nastavení sítě se nezdařilo.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"Nebyl přidělen dostatečný počet karet.",
/* TR_NO_BLUE_INTERFACE */
"Nebylo přiděleno žádné BLUE rozhraní.",
/* TR_NO_CDROM */
"Nenalezena žádná CD-ROM mechanika.",
/* TR_NO_HARDDISK */
"Nenalezen žádný pevný disk.",
/* TR_NO_IPCOP_TARBALL_FOUND */
"Ipcop tarball nebyl na webovém serveru nalezen.",
/* TR_NO_ORANGE_INTERFACE */
"Nebylo přiděleno žádné ORANGE rozhraní.",
/* TR_NO_RED_INTERFACE */
"Nebylo přiděleno žádné RED rozhraní.",
/* TR_NO_SCSI_IMAGE_FOUND */
"SCSI image nebyla na webovém serveru nalezena.",
/* TR_NO_UNALLOCATED_CARDS */
"Nezbývají žádné nepřidělené karty, přičemž jsou vyžadovány další. K jejich vyhledání můžete využít autodetekci, nebo zvolit odpovídající ovladač ze seznamu.",
/* TR_OK */
"Ok",
/* TR_PARTITIONING_DISK */
"Rozděluji disk...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"Hesla nesouhlasí.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"Heslo nesmí být prázdné.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"Heslo nesmí obsahovat mezery.",
/* TR_PASSWORD_PROMPT */
"Heslo:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Telefonní číslo nesmí být nevyplněné.",
/* TR_PREPARE_HARDDISK */
"Instalační program nyní připraví pevný disk na %s. Nejdříve bude disk rozdělen na oddíly, poté bude na těchto oddílech vytvořen systém souborů.",
/* TR_PRESS_OK_TO_REBOOT */
"Pro restartování stiskněte OK",
/* TR_PRIMARY_DNS */
"Primární DNS:",
/* TR_PRIMARY_DNS_CR */
"Primární DNS\n",
/* TR_PROBE */
"Vyhledat",
/* TR_PROBE_FAILED */
"Automatická detekce se nezdařila.",
/* TR_PROBING_SCSI */
"Detekuji SCSI zařízení...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"Při nastavování %s admin hesla nastaly potíže.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"Při nastavování hesla uživatele 'root' nastaly potíže.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"Při nastavování hesla uživatele 'setup' nastaly potíže.",
/* TR_PROTOCOL_COUNTRY */
"Protokol/Země",
/* TR_PULLING_NETWORK_UP */
"Spouštím síť...",
/* TR_PUSHING_NETWORK_DOWN */
"Zastavuji síť...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Zastavuji vzdálenou síť...",
/* TR_QUIT */
"Skončit",
/* TR_RED_IN_USE */
"ISDN (nebo jiné externí připojení) je právě používáno. Nelze konfigurovat ISDN, dokud je RED rozhraní aktivní.",
/* TR_RESTART_REQUIRED */
"\n\nPo dokončení nastavení bude třeba restartovat síť.",
/* TR_RESTORE */
"Obnovit",
/* TR_RESTORE_CONFIGURATION */
"Pokud máte disketu se zálohou systémové konfigurace %s, vložte ji nyní do disketové mechaniky a stiskněte tlačítko Obnovit.",
/* TR_ROOT_PASSWORD */
"'root' heslo",
/* TR_SECONDARY_DNS */
"Sekundární DNS:",
/* TR_SECONDARY_DNS_CR */
"Sekundární DNS\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"Sekundární DNS server uveden bez zadání primárního DNS",
/* TR_SECTION_MENU */
"Menu",
/* TR_SELECT */
"Vybrat",
/* TR_SELECT_CDROM_TYPE */
"Vyberte typ CDROM",
/* TR_SELECT_CDROM_TYPE_LONG */
"V tomto počítači nebyla nalezena žádná mechanika CD-ROM. Vyberte prosím, který z následujících ovladačů chcete použít, aby %s mohl získat přístup k CD-ROM.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Vyberte instalační médium",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s lze nainstalovat z různých zdrojů. Nejjednodušší je využít CDROM mechaniku počítače. Není-li k dispozici, je možno instalovat s pomocí jiného počítače na síti LAN, který poskytuje instalační soubory prostřednictvím HTTP protokolu. V takovém případě je nutno vytvořit síťovou instalační disketu.",
/* TR_SELECT_NETWORK_DRIVER */
"Vyberte síťový ovladač",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Zvolte ovladač síťové karty nainstalované na tomto počítači. Pokud vyberete možnost RUČNÍ, budete moci zadat jméno modulu ovladače a také parametry ovladače pro karty se zvláštními požadavky, např. ISA karty.",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Vyberte rozhraní, které chcete překonfigurovat.",
/* TR_SELECT_THE_ITEM */
"Zvolte položku, kterou chcete nastavit.",
/* TR_SETTING_ADMIN_PASSWORD */
"Nastavuji %s admin heslo...",
/* TR_SETTING_ROOT_PASSWORD */
"Nastavuji heslo uživatele 'root'...",
/* TR_SETTING_SETUP_PASSWORD */
"Nastavuji heslo uživatele 'setup'...",
/* TR_SETUP_FINISHED */
"Instalace dokončena. Stiskněte Ok pro restart počítače.",
/* TR_SETUP_NOT_COMPLETE */
"Počáteční nastavení nebylo zcela dokončeno. Je bezpodmínečně nutné zajistit jeho správné dokončení opětovným spuštěním programu setup z příkazové řádky.",
/* TR_SETUP_PASSWORD */
"'setup' heslo",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Nastavte upřesňující parametry modulu",
/* TR_SINGLE_GREEN */
"Vaše konfigurace je nastavena pro jediné GREEN rozhraní.",
/* TR_SKIP */
"Přeskočit",
/* TR_START_ADDRESS */
"Počáteční adresa:",
/* TR_START_ADDRESS_CR */
"Počáteční adresa\n",
/* TR_STATIC */
"Statická",
/* TR_SUGGEST_IO */
"(navrhuji %x)",
/* TR_SUGGEST_IRQ */
"(navrhuji %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"Tento ovladač je již zaveden.",
/* TR_TIMEZONE */
"Časové pásmo",
/* TR_TIMEZONE_LONG */
"Vyberte časové pásmo, v němž se nacházíte, z následujícího seznamu.",
/* TR_UNABLE_TO_EJECT_CDROM */
"Nelze vysunout CDROM.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Nelze rozbalit moduly.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Nelze nalézt jakékoliv další ovladače.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Nelze nalézt ISDN kartu. Je třeba specifikovat další parametry, pokud je karta typu ISA nebo má zvláštní požadavky.",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"Nelze inicializovat ISDN.",
/* TR_UNABLE_TO_INSTALL_FILES */
"Nelze instalovat soubory.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"Nelze instalovat GRUB.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Nelze načíst modul ovladače.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Nelze vytvořit souborový systém /boot.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Nelze vytvořit souborový systém /log.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Nelze vytvořit kořenový souborový systém.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Nelze vytvořit swap oddíl.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Nelze vytvořit symbolický odkaz /dev/harddisk.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Nelze vytvořit symbolický odkaz /dev/harddisk1.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Nelze vytvořit symbolický odkaz /dev/harddisk2.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Nelze vytvořit symbolický odkaz /dev/harddisk3.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Nelze vytvořit symbolický odkaz /dev/harddisk4.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Nelze vytvořit symbolický odkaz /dev/root.",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Nelze připojit souborový systém /boot.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Nelze připojit souborový systém /log.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Nelze připojit souborový systém /proc.",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Nelze připojit kořenový souborový systém.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Nelze připojit swap oddíl.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Nelze otevřít soubor 'hosts'.",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Nelze otevřit soubor nastavení.",
/* TR_UNABLE_TO_PARTITION */
"Nelze rozdělit disk.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"Nelze odstranit dočasné stažené soubory.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"Nelze nastavit jméno počítače.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"Nelze odpojit CDROM/disketu.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"Nelze odpojit pevný disk.",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"Nelze zapsat do /etc/fstab",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"Nelze zapsat do /etc/hostname",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"Nelze zapsat do /etc/hosts",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"Nelze zapsat do /etc/hosts.allow",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"Nelze zapsat do /etc/hosts.deny",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"Nelze zapsat do %s/ethernet/settings",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"Nelze zapsat do %s/main/hostname.conf",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"Nelze zapsat do %s/main/settings",
/* TR_UNCLAIMED_DRIVER */
"Dosud není přidělen ethernet adaptér typu:\n%s\n\nMůžete jej přidělit rozhraním:",
/* TR_UNKNOWN */
"NEZNÁMÝ",
/* TR_UNSET */
"NENASTAVEN",
/* TR_USB_KEY_VFAT_ERR */
"This USB key is invalid (no vfat partition found).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"VAROVÁNÍ",
/* TR_WARNING_LONG */
"Pokud změníte tuto IP adresu a jste přihlášeni prostřednictvím vzdáleného přístupu, Vaše spojení s %s bude přerušeno a budete se muset znovu připojit k nové IP adrese. Jedná se o riskantní operaci, o kterou byste se měli pokusit pouze tehdy, pokud máte fyzický přístup k počítači, pro případ, že by se operace nezdařila.",
/* TR_WELCOME */
"Instalační program %s Vás vítá. Volbou Zrušit na libovolné následující obrazovce restartujete počítač.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Vaše konfigurace je nastavena pro jediné GREEN rozhraní, které již má přiděleno ovladač.",
}; 
  
