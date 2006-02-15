/*
 * Slovak  (sk) Data File
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
 * (c) 2005 Drlik Zbynek, Miloš Mráz 
 */
 
#include "libsmooth.h"

char *sk_tr[] = {

/* TR_ADDRESS_SETTINGS */
"Nastavenie adries",
/* TR_ADMIN_PASSWORD */
"Heslo užívateľa 'admin'",
/* TR_AGAIN_PROMPT */
"Znovu:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Všetky karty boli úspešne priradené.",
/* TR_AUTODETECT */
"* AUTODETEKCIA *",
/* TR_BUILDING_INITRD */
"Vytváram INITRD ...",
/* TR_CANCEL */
"Zrušiť",
/* TR_CARD_ASSIGNMENT */
"Priraďovanie kariet",
/* TR_CHECKING */
"Kontrolujem URL ...",
/* TR_CHECKING_FOR */
"Kontrola: %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Vyberte v tomto počítači nainštalovanú ISDN kartu.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Vyberte požadovaný ISDN protokol.",
/* TR_CONFIGURE_DHCP */
"Zadajte požadované informácie pre nastavenie DHCP serveru.",
/* TR_CONFIGURE_NETWORKING */
"Nastavenie siete",
/* TR_CONFIGURE_NETWORKING_LONG */
"Teraz je nutné nastaviť pripojenie k sieti a to najprv zavedením odpovedajúceho ovládača pre GREEN rozhranie. Ten je možné určiť pomocou automatického vyhľadania sieťovej karty alebo vybraním tohoto ovládača zo zoznamu. Ak máte nainštalovaných viacej sieťových kariet, tie budete môcť nastaviť neskoršie počas inštalácie. Pokiaľ máte ďalšie karty rovnakého typu ako je karta GREEN rozhrania a každá z nich vyžaduje zvláštne parametre modulu, mali by ste tieto parametre zadať pre všetky karty príslušného typu tak, aby mohli byť aktivované po nastavení GREEN rozhrania.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Nastavte sieťové ovládače a priraďte karty príslušným rozhraniam. Aktuálna konfigurácia je nasledovná:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"Nastavte CD-ROM výberom odpovedajúcej IO adresy a/alebo IRQ.",
/* TR_CONGRATULATIONS */
"Blahoželám!",
/* TR_CONGRATULATIONS_LONG */
"Inštalácia %s-u bola úspešne dokončená. Prosím vyberte všetky diskety a CD-ROM, ktoré sú v mechanikách počítača. Ak systém nenaštartuje správne, prosím skúste naštartovať z DOS diskiet a zadať príkaz 'fdisk /mbr' k znovuvytvoreniu Master Boot Record-u. Bude spustený setup a budete môcť nastaviť IDSN, sieťové karty a systémové heslá. Po úspešnom ukončení setup-u, budete sa môcť pripojiť pomocou prehliadača na adrese http://%s:81 alebo https://%s:445 (alebo meno vašeho %s-u), nastavte vytáčané pripojenie (ak je treba) a vzdialený prístup. Pokiaľ chcete užívateľom umožniť ovládať pripojenie, nezabudnite nastaviť heslo pre užívateľa 'dial'.",
/* TR_CONTINUE_NO_SWAP */
"Váš pevný disk je veľmi malý, ale je možné pokračovať bez swap oddielu. (Túto možnosť použite len s opatrnosťou).",
/* TR_CURRENT_CONFIG */
"Aktuálne nastavenie: %s%s",
/* TR_DEFAULT_GATEWAY */
"Východzia brána:",
/* TR_DEFAULT_GATEWAY_CR */
"Východzia brána\n",
/* TR_DEFAULT_LEASE */
"Východzí čas zapožičania (min):",
/* TR_DEFAULT_LEASE_CR */
"Východzí čas zapožičania\n",
/* TR_DETECTED */
"Nájdený: %s",
/* TR_DHCP_HOSTNAME */
"Meno DHCP serveru:",
/* TR_DHCP_HOSTNAME_CR */
"Meno DHCP serveru\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"Nastavenie DHCP serveru",
/* TR_DISABLED */
"zakázané",
/* TR_DISABLE_ISDN */
"Zakázať ISDN",
/* TR_DISK_TOO_SMALL */
"Váš pevný disk je veľmi malý.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"Nastavenie DNS a brány",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Zadajte údaje o DNS a bráne. Tieto nastavenia sa používajú iba ak je zakázané DHCP na RED rozhraní.",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Vaše nastavenie nepoužíva sieťový adaptér pre RED rozhranie. Údaje o DNS a bráne pre dialup užívateľa sa nastavujú automaticky v okamžiku vytočenia.",
/* TR_DOMAINNAME */
"Meno domény",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Nebolo zadané meno domény.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"Meno domény nesmie obsahovať medzery.",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Meno domény smie obsahovať iba písmená, čísla, pomlčky a bodky.",
/* TR_DOMAIN_NAME_SUFFIX */
"Prípona mena domény:",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Prípona mena domény\n",
/* TR_DONE */
"Hotovo",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\nChcete zmeniť tieto nastavenia?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Priradenie ovládačov a kariet",
/* TR_ENABLED */
"Povoliť",
/* TR_ENABLE_ISDN */
"Povoliť ISDN",
/* TR_END_ADDRESS */
"Koncová adresa:",
/* TR_END_ADDRESS_CR */
"Koncová adresa\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Niektoré ISDN karty (najmä ISA) môžu vyžadovať upresňujúce parametre modulu pre nastavenie údajov o IRQ a adrese IO portu. Ak máte takúto ISDN kartu, zadajte sem príslušné parametre. Napríklad: \"io=0x280 irq=9\". Tie budú použité pri detekcii karty.",
/* TR_ENTER_ADMIN_PASSWORD */
"Zadajte heslo 'admin' užívateľa %s-u. Tento účet slúži na prihlasovanie sa k webovému rozhraniu %s-u.",
/* TR_ENTER_DOMAINNAME */
"Zadajte meno domény.",
/* TR_ENTER_HOSTNAME */
"Zadajte meno počítača.",
/* TR_ENTER_IP_ADDRESS_INFO */
"Zadajte IP adresu",
/* TR_ENTER_NETWORK_DRIVER */
"Nepodarilo sa automaticky detekovať sieťovú kartu. Zadajte ovládač a voliteľné parametre pre sieťovú kartu.",
/* TR_ENTER_ROOT_PASSWORD */
"Zadajte heslo 'root' užívateľa IPCop-u. Tento účet slúži na prihlasovanie sa k príkazovému riadku IPCop-u.",
/* TR_ENTER_SETUP_PASSWORD */
"Zadajte heslo 'setup' užívateľa. Tento účet slúži na prihlasovanie sa k programu setup.",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Zadajte IP adresu %s rozhrania.",
/* TR_ENTER_THE_LOCAL_MSN */
"Zadajte vaše telefónne číslo (MSN/EAZ).",
/* TR_ENTER_URL */
"Zadajte cestu (URL) k súborom ipcop-<verzia>.tgz a images/scsidrv-<verzia>.img. Pozor: DNS nie je dostupná! Cesta má mať tvar http://X.X.X.X/<adresár>",
/* TR_ERROR */
"Chyba",
/* TR_ERROR_WRITING_CONFIG */
"Nastala chyba pri zápise údajov o nastavení.",
/* TR_EURO_EDSS1 */
"Euro (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Rozbaľujem moduly ...",
/* TR_FAILED_TO_FIND */
"Nepodarilo sa nájsť súbor na zadanej URL.",
/* TR_FOUND_NIC */
"%s našiel vo vašom počítači nasledujúcu sieťovú kartu: %s",
/* TR_GERMAN_1TR6 */
"German 1TR6",
/* TR_HELPLINE */
"            <Tab>/<Alt-Tab> pre prepnutie  |  <Medzera> pre výber",
/* TR_HOSTNAME */
"Meno počítača",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Nebolo zadané meno počítača.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"Meno počítača nesmie obsahovať medzery.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"Meno počítača smie obsahovať iba písmená, čísla, pomlčky.",
/* TR_INITIALISING_ISDN */
"Inicializujem ISDN...",
/* TR_INSERT_CDROM */
"Prosím vložte %s CD do CD-ROM mechaniky.",
/* TR_INSERT_FLOPPY */
"Prosím vložte %s disketu s ovládačmi do disketovej mechaniky.",
/* TR_INSTALLATION_CANCELED */
"Inštalácia bola zrušená.",
/* TR_INSTALLING_FILES */
"Inštalujem súbory ...",
/* TR_INSTALLING_GRUB */
"Inštalujem GRUB ...",
/* TR_INTERFACE */
"%s rozhranie",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"Nepodarilo sa spustiť rozhranie.",
/* TR_INVALID_FIELDS */
"Nasledujúce polia sú chybne vyplnené:\n\n",
/* TR_INVALID_IO */
"Zadané údaje o IO porte sú chybné. ",
/* TR_INVALID_IRQ */
"Zadané údaje o IRQ sú chybné.",
/* TR_IP_ADDRESS_CR */
"IP adresa\n",
/* TR_IP_ADDRESS_PROMPT */
"IP adresa:",
/* TR_ISDN_CARD */
"ISDN karta",
/* TR_ISDN_CARD_NOT_DETECTED */
"Nebola detekovaná ISDN karta. Ak sa jedná o kartu typu ISA alebo kartu, ktorá má zvláštne požiadavky, zrejme bude nutné zadať upresňujúce parametre modulu.",
/* TR_ISDN_CARD_SELECTION */
"Výber ISDN karty",
/* TR_ISDN_CONFIGURATION */
"Nastavenie ISDN",
/* TR_ISDN_CONFIGURATION_MENU */
"Menu pre nastavenie ISDN",
/* TR_ISDN_NOT_SETUP */
"ISDN nie je nastavené. Niektoré položky neboli vybrané.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"Zatiaľ nie je ISDN nastavené. Vyberte položku, ktorú chcete nastaviť.",
/* TR_ISDN_PROTOCOL_SELECTION */
"Výber ISDN protokolu",
/* TR_ISDN_STATUS */
"Aktuálne nastavenie ISDN - %s.\n\n Protokol: %s\n Karta: %s\n Vaše telefónne číslo: %s\n\nVyberte položku, ktorú chcete zmeniť, alebo použite aktuálne nastavenie.",
/* TR_KEYBOARD_MAPPING */
"Rozloženie klávesnice",
/* TR_KEYBOARD_MAPPING_LONG */
"Vyberte typ klávesnice z nižšie uvedeného zoznamu.",
/* TR_LEASED_LINE */
"Pevná linka",
/* TR_LOADING_MODULE */
"Zavádzam modul ...",
/* TR_LOADING_PCMCIA */
"Zavádzam PCMCIA moduly ...",
/* TR_LOOKING_FOR_NIC */
"Vyhľadávam: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Vytváram súborový systém /boot ...",
/* TR_MAKING_LOG_FILESYSTEM */
"Vytváram súborový systém /log ...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Vytváram koreňový súborový systém / ...",
/* TR_MAKING_SWAPSPACE */
"Vytváram swap oddiel ...",
/* TR_MANUAL */
"* RUČNE *",
/* TR_MAX_LEASE */
"Maximálny čas zapožičania (min):",
/* TR_MAX_LEASE_CR */
"Max. čas zapožičania\n",
/* TR_MISSING_BLUE_IP */
"Nebola zadaná IP adresa BLUE rozhrania.",
/* TR_MISSING_ORANGE_IP */
"Nebola zadaná IP adresa ORANGE rozhrania.",
/* TR_MISSING_RED_IP */
"Nebola zadaná IP adresa RED rozhrania.",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"Nebolo zadané meno modulu.",
/* TR_MODULE_PARAMETERS */
"Zadajte meno modulu a požadované parametre ovládača.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Pripájam súborový systém /boot ...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Pripájam súborový systém /log ...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Pripájam koreňový súborový systém / ...",
/* TR_MOUNTING_SWAP_PARTITION */
"Pripájam swap oddiel ...",
/* TR_MSN_CONFIGURATION */
"Vaše telefónne číslo (MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Sieťová maska:",
/* TR_NETWORKING */
"Siete",
/* TR_NETWORK_ADDRESS_CR */
"Sieťová adresa\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Sieťová adresa:",
/* TR_NETWORK_CONFIGURATION_MENU */
"Menu pre nastavenie siete",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Typ nastavenia siete",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Z nasledujúceho zoznamu typov nastavení siete vyberte nastavenie pre %s. Pokiaľ nastavenie zmeníte, bude nutné sieť reštartovať a tiež znovu priradiť sieťové ovládače k rozhraniam.",
/* TR_NETWORK_MASK_CR */
"Sieťová maska\n",
/* TR_NETWORK_SETUP_FAILED */
"Nepodarilo sa nastaviť sieť.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"Nebol priradený dostatočný počet kariet.",
/* TR_NO_BLUE_INTERFACE */
"Nebolo priradené žiadne BLUE rozhranie.",
/* TR_NO_CDROM */
"Nebola nájdená žiadna CD-ROM mechanika.",
/* TR_NO_HARDDISK */
"Nebol nájdený žiadny pevný disk.",
/* TR_NO_IPCOP_TARBALL_FOUND */
"Nebol nájdený ipcop tarball na www serveri.",
/* TR_NO_ORANGE_INTERFACE */
"Nebolo priradené žiadne ORANGE rozhranie.",
/* TR_NO_RED_INTERFACE */
"Nebolo priradené žiadne RED rozhranie.",
/* TR_NO_SCSI_IMAGE_FOUND */
"Nebol nájdený SCSI obraz na www serveri.",
/* TR_NO_UNALLOCATED_CARDS */
"Neostávajú žiadne nepriradené karty, pričom sa vyžadujú ďalšie. K ich vyhľadaniu môžete použiť autodetekciu, alebo zvoliť odpovedajúci ovládač zo zoznamu.",
/* TR_OK */
"Ok",
/* TR_PARTITIONING_DISK */
"Rozdeľujem disk ...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"Heslá nesúhlasia.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"Nebolo zadané heslo.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"Heslo nesmie obsahovať medzery.",
/* TR_PASSWORD_PROMPT */
"Heslo:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Nebolo zadané telefónne číslo.",
/* TR_PREPARE_HARDDISK */
"Inštalačný program teraz pripraví pevný disk %s. Disk bude najprv rozdelený na oddiely, na ktorých bude vytvorený súborový systém.",
/* TR_PRESS_OK_TO_REBOOT */
"Na reštartovanie stlačte Ok.",
/* TR_PRIMARY_DNS */
"Primárny DNS server:",
/* TR_PRIMARY_DNS_CR */
"Primárny DNS server\n",
/* TR_PROBE */
"Detekovať",
/* TR_PROBE_FAILED */
"Nepodarila sa automatická detekcia.",
/* TR_PROBING_SCSI */
"Detekujem SCSI zariadenia ...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"Nastal problém pri nastavovaní hesla užívateľa %s 'admin'.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"Nastal problém pri nastavovaní hesla užívateľa 'root'.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"Nastal problém pri nastavovaní hesla užívateľa 'setup'.",
/* TR_PROTOCOL_COUNTRY */
"Protokol/Krajina",
/* TR_PULLING_NETWORK_UP */
"Spúšťam sieť ...",
/* TR_PUSHING_NETWORK_DOWN */
"Zastavujem sieť ...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Zastavujem vzdialenú sieť ...",
/* TR_QUIT */
"Skončiť",
/* TR_RED_IN_USE */
"ISDN (alebo iné externé pripojenie) sa práve používa. Nie je možné nastaviť IDSN pokiaľ je aktívne RED rozhranie.",
/* TR_RESTART_REQUIRED */
"\n\nPo dokončení nastavenia je nutné reštartovať sieť.",
/* TR_RESTORE */
"Obnoviť",
/* TR_RESTORE_CONFIGURATION */
"Ak máte disketu zo zálohou systémového nastavenia %s-u, vložte ju do disketovej mechaniky a stlačte tlačítko Obnoviť.",
/* TR_ROOT_PASSWORD */
"Heslo užívateľa 'root'",
/* TR_SECONDARY_DNS */
"Sekundárny DNS server:",
/* TR_SECONDARY_DNS_CR */
"Sekundárny DNS server\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"Sekundárny DNS server je uvedený bez zadania primárneho DNS serveru.",
/* TR_SECTION_MENU */
"Menu",
/* TR_SELECT */
"Vybrať",
/* TR_SELECT_CDROM_TYPE */
"Vyberte typ CD-ROM",
/* TR_SELECT_CDROM_TYPE_LONG */
"V tomto počítači nebola nájdená žiadna CD-ROM mechanika. Prosím vyberte, ktorý z týchto ovládačov chcete použiť, aby %s mohol získať prístup k CD-ROM.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Vyberte inštalačné médium",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s je možné nainštalovať z rôznych zdrojov. Najjednoduchšie je použiť CD-ROM mechaniku počítača. Ak nie je k dispozícii, je možné inštalovať pomocou iného počítača v sieti LAN, ktorý poskytuje inštalačné súbory prostredníctvom HTTP protokolu. V tomto prípade je nutné vytvoriť sieťovú inštalačnú disketu.",
/* TR_SELECT_NETWORK_DRIVER */
"Vyberte sieťový ovládač",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Zvoľte ovládač sieťovej karty nainštalovanej v tomto počítači. Pokiaľ vyberiete možnosť RUČNE, budete môcť zadať meno ovládača a tiež parametre ovládača pre karty zo zvláštnymi požiadavkami, napr. ISA karty.",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Vyberte rozhranie, ktoré chcete znovu nastaviť.",
/* TR_SELECT_THE_ITEM */
"Vyberte položku, ktorú chcete nastaviť.",
/* TR_SETTING_ADMIN_PASSWORD */
"Nastavujem heslo %s užívateľa 'admin' ...",
/* TR_SETTING_ROOT_PASSWORD */
"Nastavujem heslo užívateľa 'root' ...",
/* TR_SETTING_SETUP_PASSWORD */
"Nastavujem heslo užívateľa 'setup' ...",
/* TR_SETUP_FINISHED */
"Inštalácia bola úspešne dokončená. Stlačení tlačítka Ok reštartujete počítač.",
/* TR_SETUP_NOT_COMPLETE */
"Počiatočné nastavenie nebolo úplne dokončené. Je bezpodmienečne nutné zaistiť jeho správne dokončenie opätovným spustením programu setup z príkazového riadku.",
/* TR_SETUP_PASSWORD */
"Heslo užívateľa 'setup'",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Nastavenie doplňujúcich parametrov modulu",
/* TR_SINGLE_GREEN */
"Vaše nastavenie má iba GREEN rozhranie.",
/* TR_SKIP */
"Preskočiť",
/* TR_START_ADDRESS */
"Počiatočná adresa:",
/* TR_START_ADDRESS_CR */
"Počiatočná adresa\n",
/* TR_STATIC */
"Statická",
/* TR_SUGGEST_IO */
"(navrhujem %x)",
/* TR_SUGGEST_IRQ */
"(navrhujem %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"Tento ovládač je už zavedený.",
/* TR_TIMEZONE */
"Časové pásmo",
/* TR_TIMEZONE_LONG */
"Vyberte časové pásmo, v ktorom sa nachádzate, z nasledujúceho zoznamu.",
/* TR_UNABLE_TO_EJECT_CDROM */
"Nie je možné vysunúť CD-ROM.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Nie je možné rozbaliť moduly.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Nie je možné nájsť akékoľvek ďalšie ovládače.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Nie je možné v tomto počítači nájsť ISDN kartu. Je treba špecifikovať ďalšie parametre, pokiaľ je karta typu ISA alebo má zvláštne požiadavky.",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"Nie je možné inicializovať ISDN.",
/* TR_UNABLE_TO_INSTALL_FILES */
"Nie je možné nainštalovať súbory.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"Nie je možné nainštalovať GRUB.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Nie je možné zaviesť modul ovládača.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Nie je možné vytvoriť súborový systém /boot.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Nie je možné vytvoriť súborový systém /log.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Nie je možné vytvoriť koreňový súborový systém /.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Nie je možné vytvoriť swap oddiel.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Nie je možné vytvoriť symbolický odkaz /dev/harddisk.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Nie je možné vytvoriť symbolický odkaz /dev/harddisk1.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Nie je možné vytvoriť symbolický odkaz /dev/harddisk2.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Nie je možné vytvoriť symbolický odkaz /dev/harddisk3.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Nie je možné vytvoriť symbolický odkaz /dev/harddisk4.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Nie je možné vytvoriť symbolický odkaz /dev/root",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Nie je možné pripojiť súborový systém /boot",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Nie je možné pripojiť súborový systém /log",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Nie je možné pripojiť súborový systém /proc",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Nie je možné pripojiť koreňový súborový systém /.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Nie je možné pripojiť swap oddiel.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Nie je možné otvoriť súbor 'hosts'.",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Nie je možné otvoriť súbor nastavenia",
/* TR_UNABLE_TO_PARTITION */
"Nie je možné rozdeliť disk.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"Nie je možné odstrániť stiahnuté dočasné súbory.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"Nie je možné nastaviť meno počítača.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"Nie je možné odpojiť CD-ROM/disketu.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"Nie je možné odpojiť pevný disk.",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"Nie je možné zapísať do súboru /etc/fstab",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"Nie je možné zapísať do súboru /etc/hostname",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"Nie je možné zapísať do súboru /etc/hosts.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"Nie je možné zapísať do súboru /etc/hosts.allow.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"Nie je možné zapísať do súboru /etc/hosts.deny.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"Nie je možné zapísať do súboru %s/ethernet/settings.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"Nie je možné zapísať do súboru %s/main/hostname.conf",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"Nie je možné zapísať do súboru %s/main/settings.",
/* TR_UNCLAIMED_DRIVER */
"Zatiaľ nie je priradená sieťová karta typu:\n%s\n\nMôžete ju priradiť rozhraniu:",
/* TR_UNKNOWN */
"NEZNÁMY",
/* TR_UNSET */
"NENASTAVENÉ",
/* TR_USB_KEY_VFAT_ERR */
"USB kľúč je poškodený (nebola nájdená vfat partícia).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"Varovanie",
/* TR_WARNING_LONG */
"Ak zmeníte túto IP adresu a ste prihlásení prostredníctvom vzdialeného prístupu, vaše spojenie s %s bude prerušené a budete sa musieť znovu pripojiť k novej IP adrese. Jedná sa o riskantnú operáciu, o ktorú by ste sa mali pokúsiť iba vtedy, pokiaľ máte fyzický prístup k počítaču, pre prípad, že by sa operácia nepodarila.",
/* TR_WELCOME */
"Vítajte v inštalačnom programe %s-u. Voľbou Zrušiť na ľubovoľnej nasledujúcej obrazovke reštartujete počítač.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Vaše nastavenie má iba GREEN rozhranie s už priradeným ovládačom.",
}; 
  
