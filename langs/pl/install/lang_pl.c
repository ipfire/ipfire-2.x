/*
 * Polish (pl) Data File
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
 */
 
#include "libsmooth.h"

char *pl_tr[] = {

/* TR_ISDN */
"ISDN",
/* TR_ERROR_PROBING_ISDN */
"Nie można przeprowadzić wyszukiwania urządzeń ISDN.",
/* TR_PROBING_ISDN */
"Wyszukiwanie i konfiguracja urządzeń ISDN.",
/* TR_MISSING_GREEN_IP */
"Brak adresu IP interfejsu Green!",
/* TR_CHOOSE_FILESYSTEM */
"Proszę wybrać system plików:",
/* TR_NOT_ENOUGH_INTERFACES */
"Brak wystarczającej liczby urządzeń sieciowych.\n\nPotrzebne: %d - Dostępne: %d\n",
/* TR_INTERFACE_CHANGE */
"Proszę wybrać interfejs dla którego chcesz wprowadzić zmiany.\n\n",
/* TR_NETCARD_COLOR */
"Przypisane karty",
/* TR_REMOVE */
"Usuń",
/* TR_MISSING_DNS */
"Brakujący DNS.\n",
/* TR_MISSING_DEFAULT */
"Brak bramy domyślnej.\n",
/* TR_JOURNAL_EXT3 */
"Tworzenie dziennika dla Ext3...",
/* TR_CHOOSE_NETCARD */
"Proszę wybrać urządzenie sieciowe dla interfejsu - %s.",
/* TR_NETCARDMENU2 */
"Rozszerzone menu sieci",
/* TR_ERROR_INTERFACES */
"W twoim systemie nie ma wolnych interfejsów.",
/* TR_REMOVE_CARD */
"Czy usunąć przydział dla tej karty sieciowej? - %s",
/* TR_JOURNAL_ERROR */
"Nie można utworzyć dziennika, nastąpi powrót do ext2.",
/* TR_FILESYSTEM */
"Wybierz system plików",
/* TR_ADDRESS_SETTINGS */
"Ustawienia adresów",
/* TR_ADMIN_PASSWORD */
"hasło 'admina' ",
/* TR_AGAIN_PROMPT */
"Powtórz:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Wszystkie karty przypisano poprawnie.",
/* TR_AUTODETECT */
"* AUTODETECT *",
/* TR_BUILDING_INITRD */
"Tworzenie ramdisk...",
/* TR_CANCEL */
"Anuluj",
/* TR_CARD_ASSIGNMENT */
"Przypisywanie kart",
/* TR_CHECKING */
"Sprawdzanie URL...",
/* TR_CHECKING_FOR */
"Sprawdzanie dla: %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Wybierz kartę ISDN zainstalowaną w tym komputerze.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Wybierz wymagany protokół ISDN.",
/* TR_CONFIGURE_DHCP */
"Skonfiguruj serwer DHCP wprowadzając odpowiednie ustawienia.",
/* TR_CONFIGURE_NETWORKING */
"Konfiguruj sieć",
/* TR_CONFIGURE_NETWORKING_LONG */
"Teraz powinieneś skonfigurować sieć poprzez załadowanie odpowiedniego sterownika dla interfejsu GREEN. Możesz skorzystać z automatycznego wykrywania kart sieciowych lub wybrać odpowiedni sterownik z listy. Pamiętaj - jeżeli posiadasz zainstalowaną więcej niż jedną kartę sieciową ich konfigurację będzie można przeprowadzić w dalszej części procesu instalacji. Pamiętaj także, że jeżeli posiadasz więcej niż jedną kartę sieciową takiego samego typu jak GREEN i każda z nich wymaga specjalnych parametrów modułu należy wprowadzić parametry dla wszystkich kart tego typu tak aby możliwe było aktywowanie interfejsu GREEN po jego konfiguracji.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Konfiguracja sterowników oraz przydział kart sieciowych do interfejsów. Aktualna konfiguracja wygląda następująco:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"Skonfiguruj CDROM wybierając odpowiedni adres IO i/lub IRQ.",
/* TR_CONGRATULATIONS */
"Gratulacje!",
/* TR_CONGRATULATIONS_LONG */
"%s został prawidłowo zainstalowany. Proszę usunąć płytę CD z komputera. Uruchomiony zostanie program konfiguracyjny umożliwiający ustawienie połączenia ISDN, kart sieciowych oraz haseł. Po wprowadzeniu ustawień powinieneś otworzyć w przeglądare adres https://%s:444 (lub wprowadzoną nazwę %s) aby przejść do panelu zarządzania systemem.",
/* TR_CONTINUE_NO_SWAP */
"Twój dysk twardy jest bardzo mały. Możesz kontynuować, ale utworzona zostanie bardzo mała przestrzeń swap. (Używaj ostrożnie).",
/* TR_CURRENT_CONFIG */
"Aktualna konfiguracja: %s%s",
/* TR_DEFAULT_GATEWAY */
"Brama domyślna:",
/* TR_DEFAULT_GATEWAY_CR */
"Brama domyślna\n",
/* TR_DEFAULT_LEASE */
"Domyślny czas dzierżawy (minut):",
/* TR_DEFAULT_LEASE_CR */
"Domyślny czas dzierżawy\n",
/* TR_DETECTED */
"Wykryto: %s",
/* TR_DHCP_HOSTNAME */
"Nazwa hosta DHCP:",
/* TR_DHCP_HOSTNAME_CR */
"Nazwa hosta DHCP\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"Konfiguracja serwera DHCP",
/* TR_DISABLED */
"Wyłączone",
/* TR_DISABLE_ISDN */
"Wyłącz ISDN",
/* TR_DISK_TOO_SMALL */
"Twój dysk jest za mały.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"Ustawienia DNS i bramy",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Wprowadź informacje o DNS i bramie. Te ustawienie są używane tylko dla statycznego IP (i DHCP jeżeli ustawiono DNS) na interfejsie RED.",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Twoja konfiguracja nie wykorzystuje karty ethernet jako interfejsu RED.  Informacje o DNS i bramie są wprowadzane automatycznie dla połączeń typu dialup przy połączeniu.",
/* TR_DOMAINNAME */
"Nazwa domeny",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Nazwa domeny nie może być pusta.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"Nazwa domeny nie może zawierać spacji.",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Domain name may only contain letters, numbers, hyphens and periods.",
/* TR_DOMAIN_NAME_SUFFIX */
"Sufix nazwy domeny:",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Sufix nazwy domeny\n",
/* TR_DONE */
"Gotowe",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\nCzy chcesz zmienić te ustawienia?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Przypisywanie sterowników i kart",
/* TR_ENABLED */
"Włączone",
/* TR_ENABLE_ISDN */
"Włącz ISDN",
/* TR_END_ADDRESS */
"Adres końcowy:",
/* TR_END_ADDRESS_CR */
"Adres końcowy\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Niektóre karty ISDN (w szczególności ISA) mogą wymagać dodatkowych parametrów modułu w celu ustawienia IRQ i adresu IO. Jeżeli posiadasz tego typu kartę wprowadź te dodatkowe parametry tutaj. Na przykład: \"io=0x280 irq=9\". Zostaną one użyte podczas wykrywania kart.",
/* TR_ENTER_ADMIN_PASSWORD */
"Podaj hasło użytkownika 'admin' dla %s .  Jest to użytkownik na którego będziesz logował się do interfejsu WWW aby zarządzać %s .",
/* TR_ENTER_DOMAINNAME */
"Wprowadź nazwę domeny",
/* TR_ENTER_HOSTNAME */
"Podaj nazwę hosta dla maszyny.",
/* TR_ENTER_IP_ADDRESS_INFO */
"Wprowadź informacje o adresie IP",
/* TR_ENTER_NETWORK_DRIVER */
"Nie można wykryć kart sieciowych automatycznie. Wprowadź sterownik oraz dodatkowe parametry dla karty sieciowej.",
/* TR_ENTER_ROOT_PASSWORD */
"Podaj hasło użytkownika 'root' . Jest to użytkownik wykorzystywany do logowania do linii poleceń.",
/* TR_ENTER_SETUP_PASSWORD */
"TO BE REMOVED",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Wprowadź informacje o adresie IP dla interfejsu %s .",
/* TR_ENTER_THE_LOCAL_MSN */
"Wprowadź lokalny numer telefonu (MSN/EAZ).",
/* TR_ENTER_URL */
"Wprowadź adres URL do ipcop-<version>.tgz i plików images/scsidrv-<version>.img . UWAGA: DNS niedostępny! URL powinien wyglądać następująco http://X.X.X.X/<katalog>",
/* TR_ERROR */
"Błąd",
/* TR_ERROR_PROBING_CDROM */
"Nie znaleziono napędu CDROM.",
/* TR_ERROR_WRITING_CONFIG */
"Błąd zapisywania informacji o konfiguracji.",
/* TR_EURO_EDSS1 */
"Euro (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Wypakowywanie modułów...",
/* TR_FAILED_TO_FIND */
"Nie można odnaleźć pliku URL.",
/* TR_FOUND_NIC */
"%s wykrył następujące urządzenia NIC w twojej maszynie: %s",
/* TR_GERMAN_1TR6 */
"German 1TR6",
/* TR_HELPLINE */
"              <Tab>/<Alt-Tab> pomiędzy pozycjami   |  <Space> wybór",
/* TR_HOSTNAME */
"Nazwa hosta",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Nazwa hosta nie może być pusta.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"Nazwa hosta nie może zawierać spacji.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"Nazwa hosta może zawierać tylko listery, cyfry i łączniki.",
/* TR_INITIALISING_ISDN */
"Inicjalizacja ISDN...",
/* TR_INSERT_CDROM */
"Proszę włożyć %s CD do napędu CDROM.",
/* TR_INSERT_FLOPPY */
"Proszę włożyć dyskietkę ze sterownikami %s do napędu.",
/* TR_INSTALLATION_CANCELED */
"Instalacja anulowana.",
/* TR_INSTALLING_FILES */
"Instalowanie plików...",
/* TR_INSTALLING_GRUB */
"Instalowanie GRUB...",
/* TR_INSTALLING_LANG_CACHE */
"Instalowanie plików językowych...",
/* TR_INTERFACE */
"Interfejs - %s",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"Nie można uruchomić interfejsu.",
/* TR_INVALID_FIELDS */
"Poniższe pola są niepoprawne:\n\n",
/* TR_INVALID_IO */
"Szczegóły portu IO są nieprawidłowe. ",
/* TR_INVALID_IRQ */
"Wprowadzone dane IRQ są niepoprawne.",
/* TR_IP_ADDRESS_CR */
"Adres IP\n",
/* TR_IP_ADDRESS_PROMPT */
"Adres IP:",
/* TR_ISDN_CARD */
"Karta ISDN",
/* TR_ISDN_CARD_NOT_DETECTED */
"Nie wykryto karty ISDN. Możesz wprowadzić dodatkowe parametry modułu jeżeli posiadasz kartę ISA lub twoja karta ma specyficzne wymagania.",
/* TR_ISDN_CARD_SELECTION */
"Wybór karty ISDN",
/* TR_ISDN_CONFIGURATION */
"Konfiguracja ISDN",
/* TR_ISDN_CONFIGURATION_MENU */
"Menu konfiguracji ISDN",
/* TR_ISDN_NOT_SETUP */
"Nie skonfigurowano ISDN. Pewne pozycje nie zostały wybrane.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"ISDN nie został jeszcze skonfigurowany. Wybierz tą pozycję aby skonfigurować.",
/* TR_ISDN_PROTOCOL_SELECTION */
"Wybór protokołu ISDN",
/* TR_ISDN_STATUS */
"ISDN jest obecnie %s.\n\n   Protokół: %s\n   Karta: %s\n   Lokalny numer telefonu: %s\n\nWybierz pozycję którą chcesz zmienić lub pozostaw obecną konfigurację.",
/* TR_KEYBOARD_MAPPING */
"Układ klawiatury",
/* TR_KEYBOARD_MAPPING_LONG */
"Z poniższej listy wybierz układ klawiatury którego chcesz używać.",
/* TR_LEASED_LINE */
"Linia dzierżawiona",
/* TR_LOADING_MODULE */
"Ładowanie modułu...",
/* TR_LOADING_PCMCIA */
"Ładowanie modułów PCMCIA...",
/* TR_LOOKING_FOR_NIC */
"Wyszukiwanie: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Tworzenie systemu plików boot...",
/* TR_MAKING_LOG_FILESYSTEM */
"Tworzenie systemu plików log...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Tworzenie systemu plików root...",
/* TR_MAKING_SWAPSPACE */
"Tworzenie przestrzeni swap...",
/* TR_MANUAL */
"* RĘCZNIE *",
/* TR_MAX_LEASE */
"Maks czas dzierżawy (minut):",
/* TR_MAX_LEASE_CR */
"Maks czas dzierżawy\n",
/* TR_MISSING_BLUE_IP */
"Brak informacji o IP dla interfejsu BLUE.",
/* TR_MISSING_ORANGE_IP */
"Brak informacji o IP dla interfejsu ORANGE.",
/* TR_MISSING_RED_IP */
"Brak informacji o IP dla interfejsu RED.",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"Nazwa modułu nie może być pusta.",
/* TR_MODULE_PARAMETERS */
"Wprowadź nazwę modułu i parametry dla sterownika.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Montowanie systemu plików boot...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Montowanie systemu plików log...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Montowanie systemu plików root...",
/* TR_MOUNTING_SWAP_PARTITION */
"Montowanie przestrzeni wymiany swap...",
/* TR_MSN_CONFIGURATION */
"Lokalny numer telefonu (MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Maska sieci:",
/* TR_NETWORKING */
"Sieć",
/* TR_NETWORK_ADDRESS_CR */
"Adres sieci\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Adres sieci:",
/* TR_NETWORK_CONFIGURATION_MENU */
"Menu konfiguracji sieci",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Typ konfiguracji sieci",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Wybierz typ konfiguracji sieci dla %s.  Poniższe typy konfiguracji uwzględniają podłączone interfejsy typu ethernet. Jeżeli zmienisz te ustawienia sieć zostanie uruchomiona ponownie i koniecznie będzie ponowne przypisanie sterowników kart.",
/* TR_NETWORK_MASK_CR */
"Maska sieci\n",
/* TR_NETWORK_SETUP_FAILED */
"Błąd konfiguracji sieci.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"Nie można przydzielić wymaganej liczby kart.",
/* TR_NO_BLUE_INTERFACE */
"Nie przypisano interfejsu BLUE.",
/* TR_NO_CDROM */
"Nie znaleziono CD-ROM'u.",
/* TR_NO_GREEN_INTERFACE */
"Nie przypisano interfejsu GREEN.",
/* TR_NO_HARDDISK */
"Nie znaleziono dysku twardego.",
/* TR_DISK_SELECTION */
"Disk Selection",
/* TR_DISK_SELECTION_MSG */
"Select the disk(s) you want to install IPFire on. First those will be partitioned, and then the partitions will have a filesystem put on them.\n\nALL DATA ON THE DISK WILL BE DESTROYED.",
/* TR_NO_DISK_SELECTED */
"No disk has been selected.\n\nPlease select one or more disks you want to install IPFire on.",
/* TR_DISK_SETUP */
"Disk Setup",
/* TR_DISK_SETUP_DESC */
"The installation program will now prepare the chosen harddisk:\n\n  %s\n\nDo you agree to continue?",
/* TR_RAID_SETUP */
"RAID Setup",
/* TR_RAID_SETUP_DESC */
"The installation program will now set up a RAID configuration on the selected harddisks:\n\n  %s\n  %s\n\nDo you agree to continue?",
/* TR_DELETE_ALL_DATA */
"Delete all data",
/* TR_DISK_CONFIGURATION_NOT_SUPPORTED */
"You disk configuration is currently not supported.",
/* TR_CREATING_FILESYSTEMS */
"Creating filesystems...",
/* TR_UNABLE_TO_CREATE_FILESYSTEMS */
"Unable to create filesystems.",
/* TR_MOUNTING_FILESYSTEMS */
"Mounting filesystems...",
/* TR_UNABLE_TO_MOUNT_FILESYSTEMS */
"Unable to mount filesystems.",
/* TR_BUILDING_RAID */
"Building RAID...",
/* TR_UNABLE_TO_BUILD_RAID */
"Unable to build RAID.",
/* TR_NO_IPCOP_TARBALL_FOUND */
"Nie znaleziono archiwum tar ipcop na serwerze Web.",
/* TR_NO_ORANGE_INTERFACE */
"Nie przypisano interfejsu ORANGE.",
/* TR_NO_RED_INTERFACE */
"Nie przypisano interfejsu RED.",
/* TR_NO_SCSI_IMAGE_FOUND */
"Nie znaleziono obrazu SCSI na serwerze Web.",
/* TR_NO_UNALLOCATED_CARDS */
"Nie pozostało więcej nieprzypisanych kart. Możesz wykorzystać automatyczne wykrywanie aby poszukać więcej kart, lub ręcznie wybrać sterownik z listy.",
/* TR_OK */
"Ok",
/* TR_PARTITIONING_DISK */
"Partycjonowanie dysku...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"Hasła nie są identyczne.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"Hasło nie może być puste.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"Hasło nie może zawierać spacji.",
/* TR_PASSWORD_PROMPT */
"Hasło:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Numer telefonu nie może być pusty.",
/* TR_PREPARE_HARDDISK */
"Program instalacyjny przygotuje dysk na %s. Nastąpi partycjonowanie dysku, a następnie utworzone zostaną systemy plików na partycjach.",
/* TR_PRESS_OK_TO_REBOOT */
"Naciśnij OK aby uruchomić ponownie.",
/* TR_PRIMARY_DNS */
"Podstawowy DNS:",
/* TR_PRIMARY_DNS_CR */
"Podstawowy DNS\n",
/* TR_PROBE */
"Sprawdź",
/* TR_PROBE_FAILED */
"Błąd automatycznego wykrywania.",
/* TR_PROBING_HARDWARE */
"Sprawdzanie sprzętu...",
/* TR_PROBING_FOR_NICS */
"Sprawdzanie interfejsów NIC...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"Problem podczas ustawiania hasła dla użytkownika %s 'admin' .",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"Problem podczas ustawiania hasła dla użytkownika 'root' .",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"TO BE REMOVED",
/* TR_PROTOCOL_COUNTRY */
"Protokół/Kraj",
/* TR_PULLING_NETWORK_UP */
"Uruchamianie sieci...",
/* TR_PUSHING_NETWORK_DOWN */
"Wyłączanie sieci...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Wyłączanie sieci innych niż lokalna...",
/* TR_QUIT */
"Wyjście",
/* TR_RED_IN_USE */
"ISDN (lub inne zewnętrzne połączenie) jest aktualnie w użyciu.  Nie możesz skonfigurować ISDN kiedy interfejs RED jest aktywny.",
/* TR_RESTART_REQUIRED */
"\n\nPo zakończeniu konfiguracji wymagane będzie ponowne uruchomienie sieci.",
/* TR_RESTORE */
"Przywróć",
/* TR_RESTORE_CONFIGURATION */
"Jeżeli posiadasz dyskietkę zawierającą konfigurację systemu %s , umieść ją w napędzie dyskietek i naciśnij przycisk Przywróć.",
/* TR_ROOT_PASSWORD */
"hasło 'root'",
/* TR_SECONDARY_DNS */
"Drugi DNS:",
/* TR_SECONDARY_DNS_CR */
"Drugi DNS\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"Zdefiniowano drugi DNS bez podania podstawowego",
/* TR_SECTION_MENU */
"Section menu",
/* TR_SELECT */
"Wybierz",
/* TR_SELECT_CDROM_TYPE */
"Wybierz typ CDROM",
/* TR_SELECT_CDROM_TYPE_LONG */
"Nie wykryto CD-ROM'u w tym komputerze. Proszę wybrać sterowniki których chcesz użyć aby %s mógł uzyskać dostęp do CD-ROM.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Wybierz nośnik instalacji",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s może być zainstalowany z wielu źródeł. Najprostszym sposobem jest instalacja z napędu CDROM. Jeżeli ten komputer nie posiada takiego napędu możesz przeprowadzić instalację z innego komputera w sieci LAN udostępniającego pliki przez HTTP lub FTP.",
/* TR_SELECT_NETWORK_DRIVER */
"Wybierz sterownik karty sieciowej",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Wybierz sterownik dla karty sieciowej zainstalowanej w komputerze. Jeżeli wybierzesz ręczne przypisywanie sterowników będziesz miał możliwość wprowadzenie modułu sterownika i dodatkowych parametrów wymaganych przez niektóre karty (np. ISA).",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Wybierz interfejs którego konfigurację chcesz zmienić.",
/* TR_SELECT_THE_ITEM */
"Wybierz pozycję którą chcesz konfigurować.",
/* TR_SETTING_ADMIN_PASSWORD */
"Ustawianie hasła dla użytkownika 'admin' %s ...",
/* TR_SETTING_ROOT_PASSWORD */
"Ustawianie hasła użytkownika 'root' ....",
/* TR_SETTING_SETUP_PASSWORD */
"TO BE REMOVED",
/* TR_SETUP_FINISHED */
"Zakończono konfigurowanie.  Naciśnij Ok.",
/* TR_SETUP_NOT_COMPLETE */
"Początkowo konfiguracja nie jest kompletna. Należy upewnić się, że ustawienia są poprawne przez uruchomienie programu konfiguracyjnego (polecenia setup z linii poleceń).",
/* TR_SETUP_PASSWORD */
"TO BE REMOVED",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Ustaw dodatkowe parametry modułu",
/* TR_SINGLE_GREEN */
"Twoja konfiguracja zezwala tylko na 1 interfejs GREEN.",
/* TR_SKIP */
"Pomiń",
/* TR_START_ADDRESS */
"Adres początkowy:",
/* TR_START_ADDRESS_CR */
"Adres początkowy\n",
/* TR_STATIC */
"Statycznie",
/* TR_SUGGEST_IO */
"(sugerowane %x)",
/* TR_SUGGEST_IRQ */
"(sugerowane %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"Moduł sterownika jest już załadowany.",
/* TR_TIMEZONE */
"Strefa czasowa",
/* TR_TIMEZONE_LONG */
"Wybierz strefę czasową z poniższej listy.",
/* TR_UNABLE_TO_EJECT_CDROM */
"Nie można wysunąć CDROM'u.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Nie można wypakować modułów.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Nie można odnaleźć dodatkowych sterowników.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Nie można odnaleźć karty ISDN w tym komputerze. Może być konieczne zdefiniowanie dodatkowych parametrów modułu jeżeli karta jest typu ISA lub ma specyficzne wymagania.",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"Nie można zainicjować ISDN.",
/* TR_UNABLE_TO_INSTALL_FILES */
"Nie można zainstalować plików.",
/* TR_UNABLE_TO_INSTALL_LANG_CACHE */
"Nie można zainstalować plików językowych.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"Nie można zainstalować GRUB'a.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Nie można zainstalować modułu sterownika.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Nie można utowrzyć systemu plików boot.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Nie można utowrzyć systemu plików log.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Nie można utowrzyć systemu plików root.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Nie można utworzyć przestrzeni swap.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Nie można utworzyć linku symbolicznego /dev/harddisk.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Nie można utworzyć linku symbolicznego /dev/harddisk1.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Nie można utworzyć linku symbolicznego /dev/harddisk2.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Nie można utworzyć linku symbolicznego /dev/harddisk3.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Nie można utworzyć linku symbolicznego /dev/harddisk4.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Nie można utworzyć linku symbolicznego /dev/root.",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Nie można zamontować systemu plików boot.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Nie można zamontować systemu plików log.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Nie można zamontować systemu plików proc.",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Nie można zamontować systemu plików root.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Nie można zamontować partycji swap.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Nie można otworzyć głównego plików z hostami.",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Nie można utworzyć pliku ustawień",
/* TR_UNABLE_TO_PARTITION */
"Nie można utworzyć partycji na dysku.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"Nie można usunąć pobranych plików tymczasowych.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"Nie można ustawić nazwy hosta.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"Nie można odmontować CDROM'u lub dyskietki.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"Nie można odmontować harddisk.",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"Nie można zapisać /etc/fstab",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"Nie można zapisać /etc/hostname",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"Nie można zapisać /etc/hosts.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"Nie można zapisać /etc/hosts.allow.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"Nie można zapisać /etc/hosts.deny.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"Nie można zapisać %s/ethernet/settings.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"Nie można zapisać %s/main/hostname.conf",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"Nie można zapisać %s/main/settings.",
/* TR_UNCLAIMED_DRIVER */
"Istnieje nieprzydzielona karta ethernet typu:\n%s\n\nMożesz ją przypisać do:",
/* TR_UNKNOWN */
"NIEZNANY",
/* TR_UNSET */
"UNSET",
/* TR_USB_KEY_VFAT_ERR */
"Ten nośnik USB jest nieprawidłowy (nie znaleziono partycji vfat).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"UWAGA",
/* TR_WARNING_LONG */
"Jeżeli zmienisz ten adres IP i jesteś zdalnie zalogowany twoje połączenie z %s zostnie przerwane i konieczne będzie ponowne zalogowanie na nowy adres IP. Jest to ryzykowna operacja i powinna być wykonywana tylko w sytuacji kiedy możliwy jest fizyczny dostęp do maszyny gdyby coś poszło nie tak.",
/* TR_WELCOME */
"Witaj w programie instalacyjnym %s . Wybranie przycisku Anuluj na kolejnych ekranach spowoduje ponowne uruchomienie komputera.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Twoja konfiguracja zezwala na jeden interfejs GREEN, który posiada już przypisany sterownik.",
/* TR_YES */
"Tak",
/* TR_NO */
"Nie",
/* TR_AS */
"jako",
/* TR_IGNORE */
"Ignoruj",
/* TR_PPP_DIALUP */
"PPP DIALUP (PPPoE, modem, ATM ...)",
/* TR_DHCP */
"DHCP",
/* TR_DHCP_STARTSERVER */
"Uruchamianie serwera DHCP ...",
/* TR_DHCP_STOPSERVER */
"Zatrzymywanie serwera DHCP ...",
/* TR_LICENSE_ACCEPT */
"Akceptuję licencję.",
/* TR_LICENSE_NOT_ACCEPTED */
"Nie zaakceptowano licencji.Wyjście!",
/* TR_EXT4FS */
"EXT4 - Filesystem",
/* TR_EXT4FS_WO_JOURNAL */
"EXT4 - Filesystem without journal",
/* TR_REISERFS */
"ReiserFS - Filesystem",
/* TR_NO_LOCAL_SOURCE */
"Brak lokalnego źródła. Rozpoczynanie pobierania.",
/* TR_DOWNLOADING_ISO */
"Pobieranie obrazu instalacyjnego ...",
/* TR_DOWNLOAD_ERROR */
"Błąd podczas pobierania!",
/* TR_DHCP_FORCE_MTU */
"Wymuś mtu DHCP:",
/* TR_IDENTIFY */
"Identify",
/* TR_IDENTIFY_SHOULD_BLINK */
"Selected port should blink now ...",
/* TR_IDENTIFY_NOT_SUPPORTED */
"Function is not supported by this port.",
};
