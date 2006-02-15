/*
 * Hungarian (hu) Data File
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
 * (c) 2003 Ádám Makovecz, Ferenc Mányi-Szabó
 *  
 */
 
#include "libsmooth.h"

char *hu_tr[] = {

/* TR_ADDRESS_SETTINGS */
"Cím beállítások",
/* TR_ADMIN_PASSWORD */
"Admin jelszó",
/* TR_AGAIN_PROMPT */
"Ismét:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Minden kártya megfelelően lefoglalva.",
/* TR_AUTODETECT */
"* FELISMERÉS *",
/* TR_BUILDING_INITRD */
"INITRD felépítése...",
/* TR_CANCEL */
"Mégsem",
/* TR_CARD_ASSIGNMENT */
"Kártya kijelölés",
/* TR_CHECKING */
"URL ellenőrzése...",
/* TR_CHECKING_FOR */
"Ellenőrzés: %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Válassza ki a számítógépben lévő ISDN kártyát.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Válassza ki a használni kívánt ISDN protokolt.",
/* TR_CONFIGURE_DHCP */
"DHCP server beállítása az adatok megadásával.",
/* TR_CONFIGURE_NETWORKING */
"Hálózat beállítása",
/* TR_CONFIGURE_NETWORKING_LONG */
"Most beállíthatja a hálózatot, mely a GREEN eszköz megfelelő vezérlőjének betöltésével kezdődik. Ezt megteheti automatikus felismeréssel, vagy kiválaszthatja a megfelelőt a listából. Ha több mint egy hálózati kártya van a számítógépben, a többi beállítását megteheti a telepítés későbbi szakaszában. Abban az esetben, ha a többi kártya is ugyanolyan mint a GREEN és mindegyikhez speciális modul paraméterekre van szükség, megadhatja mindegyik számára a paramétereket, így mindegyik aktívvá válik.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Hálózati meghajtók konfigurálása és az interfészek kártyához rendelése. A jelenlegi konfiguráció a következő:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"CDROM beállítása a megfelelő IO cím és/vagy IRQ kiválasztásásval.",
/* TR_CONGRATULATIONS */
"Gratulálunk!",
/* TR_CONGRATULATIONS_LONG */
"Az %s telepítése sikeresen befejeződött. Kérjük távolítson el minden floppy vagy CD lemezt a számítógépből. Ha a rendszer nem tült be megfelelően, akkor probáljon DOS lemezről indítani es futatni a \"FDISK /MBR\"-t a Master Boot Record ujrakészítéséhez. Most elindul a Setup, ahol az ISDN-t, hálózati kártyákat és a rendszer jelszavait állíthatja be. A Setup után a http://%s:81 vagy a https://%s:445 (vagy azon a néven amire elnevezte az %s-t) címen távolról elérheti az adminisztrációs felületet, ahol szükség esetén beállíthatja a behívásos kapcsolatot és a távoli asztal elérést. Ne felejtsen el jelszót adni az %s 'dial' felhasználónak, ha nem az %s 'admin' felhasználójával szeretné vezérelni az oldalt.",
/* TR_CONTINUE_NO_SWAP */
"Az Ön merevlemeze nagyon kicsi, de folytathatja swap terület nélkül.",
/* TR_CURRENT_CONFIG */
"Jelenlegi beállítás: %s%s",
/* TR_DEFAULT_GATEWAY */
"Alapértelmezett Átjáró:",
/* TR_DEFAULT_GATEWAY_CR */
"Alapértelmezett Átjáró\n",
/* TR_DEFAULT_LEASE */
"Alapértelmezett fenntartás (perc):",
/* TR_DEFAULT_LEASE_CR */
"Alapértelmezett fenntartási idő\n",
/* TR_DETECTED */
"Felismerve: %s",
/* TR_DHCP_HOSTNAME */
"DHCP Hostnév:",
/* TR_DHCP_HOSTNAME_CR */
"DHCP Hostnév\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"DHCP szerver beállítás",
/* TR_DISABLED */
"tiltva",
/* TR_DISABLE_ISDN */
"ISDN tiltva",
/* TR_DISK_TOO_SMALL */
"Merevlemez túl kicsi.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"DNS és Átjáró beállítások",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Írja be a DNS és átjáró információkat. Ezeket a beállításokat csak akkor kell alkalmazni, ha a DHCP ki van kapcsolva a RED interfészen.",
/* TR_DNS_GATEWAY_WITH_GREEN */
"A konfigurációban nincs hálózati eszköz beállítva a RED interfész számára. A DNS és átjáró információ automatikusan beállítódik a tárcsázás közben.",
/* TR_DOMAINNAME */
"Domain név",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Domain név nem lehet üres.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"A domain név nem tartalmazhat szünetet.",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Domain név csak betüket, számokat, kötőjelet és alávonást tartalmazhat.",
/* TR_DOMAIN_NAME_SUFFIX */
"Domain név utótag:",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Domain név utótag\n",
/* TR_DONE */
"Rendben",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\nSzeretné megváltoztatni ezeket a beállításokat?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Driver hozzárendelése kártyákhoz",
/* TR_ENABLED */
"Engedélyezve",
/* TR_ENABLE_ISDN */
"ISDN engedélyezve",
/* TR_END_ADDRESS */
"Befejező cím:",
/* TR_END_ADDRESS_CR */
"Befejező cím\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Néhány ISDN kártya (például ISA típusúak) igényelhetnek további modulparamétereket az IRQ és IO cím beállításához. Ha ilyen ISDN kártyája van, itt megadhatja ezeket a paramétereket. Példaul: \"io=0x280 irq=9\". Ezek a felismerés közben lesznek alkalmazva.",
/* TR_ENTER_ADMIN_PASSWORD */
"Adja meg a %s admin jelszavát. Ezt a felhasználót használhatja a %s web adminisztrációs oldalára való belépéshez.",
/* TR_ENTER_DOMAINNAME */
"Írja be a domain nevet",
/* TR_ENTER_HOSTNAME */
"Adja meg a számítógép hostnevét.",
/* TR_ENTER_IP_ADDRESS_INFO */
"Adja meg az IP címet",
/* TR_ENTER_NETWORK_DRIVER */
"A halózati kártya automatikus felismerése nem sikerült. Adja meg a drivert és az opcionális paramétereket a hálózati kártyához.",
/* TR_ENTER_ROOT_PASSWORD */
"Írja be a 'root' felhasználó jelszavát. Parancssori eléréshez lépjen be ezzel a felhasználóval.",
/* TR_ENTER_SETUP_PASSWORD */
"Írja be a 'setup' felhasználó jelszavát. Ha ezzel a felhasználóval lép be, elérheti a setup programot.",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Írja be az IP címet a %s interfészhez.",
/* TR_ENTER_THE_LOCAL_MSN */
"Írja be a helyi telefonszámot (MSN/EAZ).",
/* TR_ENTER_URL */
"Írja be az ipcop-<verzió>.tgz és az images/scsi-<verzió>.img fájlok URL-jét. FIGYELMEZTETÉS: DNS nem elérhető! Csakis hasonló címet adhat meg http://x.x.x.x/<könyvtár>",
/* TR_ERROR */
"Hiba",
/* TR_ERROR_WRITING_CONFIG */
"Hiba történt a konfigurációs információk írása közben.",
/* TR_EURO_EDSS1 */
"Euro (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Modulok kicsomagolása...",
/* TR_FAILED_TO_FIND */
"Az URL fájl nem található.",
/* TR_FOUND_NIC */
"%s a következő NIC-et felismerte a számítógépen: %s",
/* TR_GERMAN_1TR6 */
"German 1TR6",
/* TR_HELPLINE */
"                 <Tab>/<Alt-Tab> léptetés | <Space> kiválasztás",
/* TR_HOSTNAME */
"Hostnév",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Hostnév nem lehet üres.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"A hostnév nem tartalmazhat szóközt.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"A hostnév csak betüket, számokat és kötőjelet tartalmazhat.",
/* TR_INITIALISING_ISDN */
"ISDN telepítése...",
/* TR_INSERT_CDROM */
"Helyezze be az %s CD-t a CD-ROM meghajtóba.",
/* TR_INSERT_FLOPPY */
"Helyezze be a %s driver lemezt a floppy meghajtóba.",
/* TR_INSTALLATION_CANCELED */
"Telepítés megszakítva.",
/* TR_INSTALLING_FILES */
"Fájlok telepítése...",
/* TR_INSTALLING_GRUB */
"GRUB telepítése...",
/* TR_INTERFACE */
"%s interfész",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"Az interfész felállítása sikertelen.",
/* TR_INVALID_FIELDS */
"A következő mezők kitöltése helytelen:\n\n",
/* TR_INVALID_IO */
"A megadott IO port helytelen.",
/* TR_INVALID_IRQ */
"A megadott IRQ helytelen.",
/* TR_IP_ADDRESS_CR */
"IP cím\n",
/* TR_IP_ADDRESS_PROMPT */
"IP cím:",
/* TR_ISDN_CARD */
"ISDN kártya",
/* TR_ISDN_CARD_NOT_DETECTED */
"IDSN kártya felismerése nem sikerült. Lehetséges, hogy szüksége van további speciális modulparaméterekre, ha a kártya ISA típusú vagy speciálisan igényli ezeket.",
/* TR_ISDN_CARD_SELECTION */
"ISDN kártya kiválasztása",
/* TR_ISDN_CONFIGURATION */
"ISDN konfiguráció",
/* TR_ISDN_CONFIGURATION_MENU */
"ISDN konfigurásiós menü",
/* TR_ISDN_NOT_SETUP */
"ISDN nincs beállítva. Néhány elem nincs kiválasztva.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"ISDN még nincs konfigurálva. Válassza ki azt az elemet, amit konfigurálni kíván.",
/* TR_ISDN_PROTOCOL_SELECTION */
"ISDN protokol kiválasztása",
/* TR_ISDN_STATUS */
"ISDN jelenleg %s.\n\n Protokol: %s\n Kártya: %s\n Helyi telefonszám: %s\n\nVálassza ki az elemet, amelyet újra kíván konfigurálni vagy használja a jelenlegi beállításokat.",
/* TR_KEYBOARD_MAPPING */
"Billentyűzet kiosztás",
/* TR_KEYBOARD_MAPPING_LONG */
"Válassza ki a használni kívánt billentyűzet-kiosztást az alábbi listából.",
/* TR_LEASED_LINE */
"Bérelt vonal",
/* TR_LOADING_MODULE */
"Modul betöltése...",
/* TR_LOADING_PCMCIA */
"PCMCIA modulok betöltése...",
/* TR_LOOKING_FOR_NIC */
"Keresés: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Boot partíció létrehozása...",
/* TR_MAKING_LOG_FILESYSTEM */
"Log partíció létrehozása...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Root partíció létrehozása...",
/* TR_MAKING_SWAPSPACE */
"Swap terület létrehozása...",
/* TR_MANUAL */
"* MANUÁLIS *",
/* TR_MAX_LEASE */
"Max fenntartás (perc):",
/* TR_MAX_LEASE_CR */
"Max fenntartási idő\n",
/* TR_MISSING_BLUE_IP */
"Hiányzó IP információk a BLUE interfészen.",
/* TR_MISSING_ORANGE_IP */
"Hiányzó IP információk az ORANGE interfészen.",
/* TR_MISSING_RED_IP */
"Hiányzó IP információk a RED interfészen.",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"Modul neve nem lehet üres.",
/* TR_MODULE_PARAMETERS */
"Adja meg a modul nevét és a paramétereket a driverhez amire szüksége van.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Boot partíció csatlakoztatása...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Log partíció csatlakoztatása...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Root partíció csatlakoztatása...",
/* TR_MOUNTING_SWAP_PARTITION */
"Swap partíció csatlakoztatása..",
/* TR_MSN_CONFIGURATION */
"Helyi telefonszám (MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Hálózati mask:",
/* TR_NETWORKING */
"Hálózat",
/* TR_NETWORK_ADDRESS_CR */
"Hálózati cím\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Hálózati cím:",
/* TR_NETWORK_CONFIGURATION_MENU */
"Halózat beállítási menü",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Hálózati konfigurációs típus",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Válassza a hálózati beállítását a %s-nak. A következő beállítás típusok listája az interfészekhez, amik csatoltak az ethernet-hez. Ha megváltoztatja ezeket a beállításokat, hálózati újraindítás szükséges, és újra be kell állítania a hálózati driverek csatolását.",
/* TR_NETWORK_MASK_CR */
"Hálózati mask\n",
/* TR_NETWORK_SETUP_FAILED */
"Hálózat beállítása sikertelen.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"Nincs elég kártya hozzárendelve.",
/* TR_NO_BLUE_INTERFACE */
"Nincs kijelölt BLUE interfész.",
/* TR_NO_CDROM */
"Nem található CD-ROM.",
/* TR_NO_HARDDISK */
"Nem található merevlemez.",
/* TR_NO_IPCOP_TARBALL_FOUND */
"Nincs ipcop tarball fájl a Web szerveren.",
/* TR_NO_ORANGE_INTERFACE */
"Nincs ORANGE interfész hozzárendelve.",
/* TR_NO_RED_INTERFACE */
"Nincs Red interfész hozzárendelve.",
/* TR_NO_SCSI_IMAGE_FOUND */
"Nincs SCSI kép fájl a Web szerveren.",
/* TR_NO_UNALLOCATED_CARDS */
"Nincs több szabad hálózati kártya, továbbira van szükség. Próbálja az automatikus felismerést a többi kártya kereséséhez vagy válasszon egy drivert a listából.",
/* TR_OK */
"Ok",
/* TR_PARTITIONING_DISK */
"Lemez partícionálása...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"A megadott jelszavak nem egyeznek.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"Jelszó nem lehet üres.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"Jelszó nem tartalmazhat szünetet.",
/* TR_PASSWORD_PROMPT */
"Jelszó:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Telefonszám nem lehet üres.",
/* TR_PREPARE_HARDDISK */
"A telepítő program előkészíti a merevlemezt a %s-en.. Először a meghajtót partícionálja, majd a fájlrendszereket hozza létre.",
/* TR_PRESS_OK_TO_REBOOT */
"Újraindításhoz nyomja meg az Ok-t.",
/* TR_PRIMARY_DNS */
"Elsődleges DNS:",
/* TR_PRIMARY_DNS_CR */
"Elsődleges DNS\n",
/* TR_PROBE */
"Próba",
/* TR_PROBE_FAILED */
"Automatikus felismerés sikertelen.",
/* TR_PROBING_SCSI */
"SCSI eszközök keresése...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"%s 'admin' jelszó beállítási probléma.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"'root' jelszó beállítási probléma.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"'setup' jelszó beállítási probléma.",
/* TR_PROTOCOL_COUNTRY */
"Protokol/Ország",
/* TR_PULLING_NETWORK_UP */
"Hálózat aktíválása...",
/* TR_PUSHING_NETWORK_DOWN */
"A hálózat leállítás alatt...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Nem lokális hálózat leállítás alatt...",
/* TR_QUIT */
"Kilépés",
/* TR_RED_IN_USE */
"ISDN (vagy egy másik külső kapcsolat) használatban. Az ISDN nem konfigurálható, amíg a RED interfész aktív.",
/* TR_RESTART_REQUIRED */
"\n\nA konfiguráció befejezése után a hálózatot újra kell indítani.",
/* TR_RESTORE */
"Visszaállít",
/* TR_RESTORE_CONFIGURATION */
"Ha van elmentett %s konfigurációja, helyezze be a floppy meghajtóba az ezt tartalmazó lemezt és nyomja meg a Visszaállít gombot.",
/* TR_ROOT_PASSWORD */
"'root' jelszó",
/* TR_SECONDARY_DNS */
"Másodlagos DNS:",
/* TR_SECONDARY_DNS_CR */
"Másodlagos DNS\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"Elsődleges DNS nélkül lett megadva a Másodlagos DNS.",
/* TR_SECTION_MENU */
"Szekció menü",
/* TR_SELECT */
"Kiválaszt",
/* TR_SELECT_CDROM_TYPE */
"CDROM típusának kiválasztása",
/* TR_SELECT_CDROM_TYPE_LONG */
"Nem sikerült a CDROM-ot felismerni a számítógépben. Válassza ki az alábbi driverek közül a megfelelőt hogy az %s használni tudja a CDROM-ot.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Telepítő média kiválasztása.",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"Az %s többféle médiáról telepíthető. A legegyszerűbb ha a számítógép CD-ROM meghajtóját használja. Ha nincs ilyen, akkor telepítheti egy másik számítógépről LAN-on keresztül, amin HTTP-n elérhetőek a telepítő fájlok. Ehhez a verzióhoz a hálózati driver lemezre lesz szüksége.",
/* TR_SELECT_NETWORK_DRIVER */
"Hálózati driver kiválasztása",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Hálózati driver kiválasztása a számítógépben található hálózati kártyához. Ha a MANUÁLIS módot választja, meg kell adnia a driver pontos nevét és paramétereit, amelyekre szükség van például egy ISA kártyánál.",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Válassza ki az interfészt, amit újra akar konfigurálni.",
/* TR_SELECT_THE_ITEM */
"Válassza ki a beállítani kívánt elemet.",
/* TR_SETTING_ADMIN_PASSWORD */
"Jelszó beállítása az 'admin' felhaszálóhoz...",
/* TR_SETTING_ROOT_PASSWORD */
"Jelszó beállítása a 'root' felhaszálóhoz...",
/* TR_SETTING_SETUP_PASSWORD */
"Jelszó beállítása a 'setup' felhaszálóhoz...",
/* TR_SETUP_FINISHED */
"Telepítés befejeződött. Nyomja meg az OK-t az újraindításhoz.",
/* TR_SETUP_NOT_COMPLETE */
"Az előtelepítés nem fejeződött be. Kérjük fejezze be a későbbiekben a setup shell-ből futtatásával.",
/* TR_SETUP_PASSWORD */
"'setup' jelszó",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"További modulparaméterek beállítása",
/* TR_SINGLE_GREEN */
"A konfiguráció egyedüli GREEN interfészre van beállítva.",
/* TR_SKIP */
"Kihagy",
/* TR_START_ADDRESS */
"Kezdő cím:",
/* TR_START_ADDRESS_CR */
"Kezdő cím\n",
/* TR_STATIC */
"Statikus",
/* TR_SUGGEST_IO */
"(javasolt %x)",
/* TR_SUGGEST_IRQ */
"(javasolt %x)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"Ez a modul driver már be van töltve.",
/* TR_TIMEZONE */
"Időzóna",
/* TR_TIMEZONE_LONG */
"Válassza ki az időzónáját az alábbi listából.",
/* TR_UNABLE_TO_EJECT_CDROM */
"A CDROM kiadása nem lehetséges.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"A modulok kicsomagolása nem lehetséges.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"További driverek nem találhatók.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Nem található ISDN kártya ebben a számítógépben. Lehetséges, hogy további modulparaméterekre van szüksége (Pl ISA kártya esetén).",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"ISDN telepítése sikertelen.",
/* TR_UNABLE_TO_INSTALL_FILES */
"Fájlok telepítése sikertelen.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"GRUB telepítése sikertelen.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Modul driver nem betölthető.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Boot fájlrendszer létrehozása sikertelen.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Log fájlrendszer létrehozása sikertelen.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Root fájlrendszer létrehozása sikertelen.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Swap terület létrehozása sikertelen.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Hivatkozás létrehozása /dev/harddisk-re nem sikerült.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Hivatkozás létrehozása /dev/harddisk1-re nem sikerült.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Hivatkozás létrehozása /dev/harddisk2-re nem sikerült.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Hivatkozás létrehozása /dev/harddisk3-ra nem sikerült.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Hivatkozás létrehozása /dev/harddisk4-re nem sikerült.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Hivatkozás létrehozása /dev/root-ra nem sikerült.",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Boot fájlrendszer csatlakoztatása sikertelen.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Log fájlrendszer csatlakoztatása sikertelen.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Proc fájlrendszer csatlakoztatása sikertelen.",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"A root fájlrendszert nem lehet csatlakoztatni.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"A swap paríció csatlakoztatása sikertelen.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"A fő host fájlokat nem lehet megnyitni.",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"A beállításokat tartalmazó fájlt nem lehet megnyitni.",
/* TR_UNABLE_TO_PARTITION */
"A lemez particionálása sikertelen.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"A letöltött átmeneti fájlok eltávolítása sikertelen.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"A hostnév nem beállitható.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"CDROM/floppydisk lecsatolása sikertelen.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"A merevlemezt nem lehet lecsatolni.",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"/etc/fstab nem írható",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"/etc/hostname nem írható",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"/etc/hosts nem írható",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"/etc/hosts.allow nem írható",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"/etc/hosts.deny nem írható",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"%s/ethernet/settings nem írható",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"%s/main/hostname.conf nem írható",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"%s/main/settings nem írható",
/* TR_UNCLAIMED_DRIVER */
"Van egy gazdátlan hálózati kártya, aminek a típusa:\n%s\n\nHozzárendelheti ehhez:",
/* TR_UNKNOWN */
"ISMERETLEN",
/* TR_UNSET */
"NEM MEGADOTT",
/* TR_USB_KEY_VFAT_ERR */
"This USB key is invalid (no vfat partition found).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"FIGYELMEZTETÉS",
/* TR_WARNING_LONG */
"Ha megváltoztatja ezt az IP címet és távolról jelentkezett be, a kapcsolat a géppel meg fog szakadni, és újra kell kapcsolódnia az új IP címen. Ez egy kritikus beállítás. Ajánjuk, hogy csak fizikai kapcsolat esetén alkalmazza, mivel problémák adódnának.",
/* TR_WELCOME */
"%s telepítő program üdvözli Önt. Ha bármikor a következőkben a Mégsem gombot választja, a számítógép újraindul.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Egyetlen GREEN interfész van beállítva, amelyhez már tartozik hozzárendelt driver.",
}; 
  
