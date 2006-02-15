/*
 * Polish  (pl) Data File
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
 * (c) 2004 Jack Korzeniowski, Piotr, Andrzej Zolnierowicz
 * (c) 2005 Remi Schleicher 
 */
 
#include "libsmooth.h"

char *pl_tr[] = {

/* TR_ADDRESS_SETTINGS */
"Ustawienie adresu",
/* TR_ADMIN_PASSWORD */
"Hasło dla użytkownika Admin",
/* TR_AGAIN_PROMPT */
"Ponownie:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Wszystkie karty skutecznie zlokalizowano.",
/* TR_AUTODETECT */
"* AUTOWYKRYWANIE *",
/* TR_BUILDING_INITRD */
"Tworzenie INITRD...",
/* TR_CANCEL */
"Anuluj",
/* TR_CARD_ASSIGNMENT */
"Przypisanie karty",
/* TR_CHECKING */
"Sprawdzanie URL...",
/* TR_CHECKING_FOR */
"Sprawdzanie dla: %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Wybierz kartę ISDN zainstalowaną w tym komputerze.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Wybierz protokół ISDN jaki potrzebujesz.",
/* TR_CONFIGURE_DHCP */
"Konfiguruj serwer DHCP przez wprowadzenie informacji o ustawieniach.",
/* TR_CONFIGURE_NETWORKING */
"Konfiguracja sieci",
/* TR_CONFIGURE_NETWORKING_LONG */
"Powinieneś teraz skonfigurować sieć przez załadowanie właściwego sterownika dla interfejsu GREEN. Możesz to zrobić przez automatyczne rozpoznawanie sprzętu lub przez wybranie właściwego sterownika z listy. Zauważ, że jeśli masz więcej zainstalowanych kart sieciowych niż jedną, będziesz musiał skonfigurować pozostałe później podczas instalacji. Zwróć również uwagę na to, że jeśli masz więcej niż jedną kartę, która jest tego samego typu co GREEN i każda karta wymaga specjalnych parametrów modułu, powinieneś wprowadzić parametry dla wszystkich kart tego typu tak, że wszystkie karty staną się aktywne gdy skonfigurujesz interfejs GREEN.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Konfiguruj sterowniki sieciowe i do którego interfejsu jest przypisana każda karta. Bieżąca konfiguracja jest następująca:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"Skonfiguruj CDROM przez wybranie właściwego adresu IO i/lub IRQ.",
/* TR_CONGRATULATIONS */
"Gratulacje!",
/* TR_CONGRATULATIONS_LONG */
"%s został poprawnie zainstalowany. Usuń dyskietki lub CDROMy z komputera. Setup poprowadzi Cię teraz przez konfigurację ISDN, kart sieciowych, i haseł systemowych. Gdy Setup będzie pomyślnie zakończony powinineś wpisać w swojej ulubionej przeglądarce http://%s:81 lub https://%s:445 (lub jak tam nazwałeś %s), i skonfigurować dialup networking (jeśli wymagane) i zdalny dostęp. Pamiętaj aby wybrać hasło dla %s użytkownika 'dial', jeśli sobie życzysz by nie %s użytkownicy 'admin' mieli możliwość kontrolowania linka.",
/* TR_CONTINUE_NO_SWAP */
"Twój twardy... (dysk) ;-) jest bardzo mały, ale możesz kontynuować bez żadnego swap'a. (Używać ostrożnie).",
/* TR_CURRENT_CONFIG */
"Bieżąca konfiguracja: %s%s",
/* TR_DEFAULT_GATEWAY */
"Domyślna bramka:",
/* TR_DEFAULT_GATEWAY_CR */
"Domyślna bramka\n",
/* TR_DEFAULT_LEASE */
"Dzierżawa domyślna (min.):",
/* TR_DEFAULT_LEASE_CR */
"Domyślny czas dzierżawy\n",
/* TR_DETECTED */
"Wykryto a:%s",
/* TR_DHCP_HOSTNAME */
"DHCP Hostname:",
/* TR_DHCP_HOSTNAME_CR */
"DHCP Hostname\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"Konfiguracja serwera DHCP",
/* TR_DISABLED */
"Nie aktywny",
/* TR_DISABLE_ISDN */
"ISDN nie aktywny",
/* TR_DISK_TOO_SMALL */
"Twój dysk jest za mały.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"Ustawienia DNS i bramy",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Wpisz informacje o DNS i bramie. Ustawienia te używane są tylko przy Statycznym IP (oraz DHCP jeśli ustawiono DNS) dla interfejsu RED.",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Twoja konfiguracja nie używa karty ethernet dla interfejsu RED. Informacje o DNS i bramie dla łącza dial-up są ustawiane automatycznie w czasie łączenia z internetem.",
/* TR_DOMAINNAME */
"Nazwa domeny",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Nazwa Domeny nie może być pusta.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"Nazwa Domeny nie może zawierać spacji.",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Nazwa Domeny może zawierać tylko litery, cyfry,minus,podkreślenie i kropkę.",
/* TR_DOMAIN_NAME_SUFFIX */
"Sufiks nazwy domeny:",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Sufiks nazwy domeny:\n",
/* TR_DONE */
"Zrobione",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\nCzy Chcesz zmienić te ustawienia?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Przypisania sterowników i kart",
/* TR_ENABLED */
"Aktywny",
/* TR_ENABLE_ISDN */
"Włącz ISDN",
/* TR_END_ADDRESS */
"Końcowy adres",
/* TR_END_ADDRESS_CR */
"Adres końcowy\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Niektóre karty ISDN (szczególnie ISA) moga wymagać dodatkowych parametrów do ustawienia przerwania IRQ i adresu portu IO. Jeżeli masz taką kartę ISDN, wpisz tu dodatkowe parametry. Np. \"io=0x280 irq=9\". Będą one używane przy wykrywaniu karty.",
/* TR_ENTER_ADMIN_PASSWORD */
"Wpisz hasło użytkownika admin serwera %s. Użytkownik ten może logować się do stron www administrowania serwerem %s.",
/* TR_ENTER_DOMAINNAME */
"Podaj nazwę Domeny",
/* TR_ENTER_HOSTNAME */
"Podaj nazwę komputera.",
/* TR_ENTER_IP_ADDRESS_INFO */
"Podaj informajcę o adrsie IP",
/* TR_ENTER_NETWORK_DRIVER */
"Nieudane automatyczne wykrycie kart sieciowych. Podaj driver i opcjonalne parametry dla karty sieciowej",
/* TR_ENTER_ROOT_PASSWORD */
"Podaj hasło dla użytkownika 'root'. Logowanie z poziomu powłoki.",
/* TR_ENTER_SETUP_PASSWORD */
"Podaj hasło dla użytkownika 'setup'. Logowanie z poziomu powłoki.",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Podaj adres IP dla interfejsu: %s ",
/* TR_ENTER_THE_LOCAL_MSN */
"Podaj numer telefonu (MSN/EAZ)",
/* TR_ENTER_URL */
"Podaj adres URL do plików: ipcop-<wersja>.tgz i images/scsidrv-<wersja>.img. Ostrzeżenia: DNS nieosiągalny. Powinno być http://X.X.X.X/<katalog>",
/* TR_ERROR */
"Błąd",
/* TR_ERROR_WRITING_CONFIG */
"Błąd przy zapisywaniu konfiguracji",
/* TR_EURO_EDSS1 */
"Euro (EDSSI)",
/* TR_EXTRACTING_MODULES */
"Rozpakowywanie modułów...",
/* TR_FAILED_TO_FIND */
"Błąd przy szukaniu adresu",
/* TR_FOUND_NIC */
"%s odnalazł następujący instefejs NIC w twoim komputerze: %s",
/* TR_GERMAN_1TR6 */
"Niemiecki 1TR6 (nieużywany)",
/* TR_HELPLINE */
"             <Tab>/<Alt-Tab> pomiędzy elementami | <Spacja> wybierz",
/* TR_HOSTNAME */
"Nazwa hosta",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Nazwa hosta nie może być pusta.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"Nazwa hosta nie może zawierać spacji",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"Hostname może zawierać litery, cyfry i niektóre znaki specjalne.",
/* TR_INITIALISING_ISDN */
"Uruchamianie ISDN..",
/* TR_INSERT_CDROM */
"Proszę włożyć %s CD do napędu CDROM",
/* TR_INSERT_FLOPPY */
"Proszę włożyć %s dyskietkę do napędu 3,5\"",
/* TR_INSTALLATION_CANCELED */
"Instalacja została anulowana",
/* TR_INSTALLING_FILES */
"Instalacja plików",
/* TR_INSTALLING_GRUB */
"Instalowanie GRUB-a...",
/* TR_INTERFACE */
"%s interfejs",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"Nieudane uruchamianie intefejsu.",
/* TR_INVALID_FIELDS */
"Następujące pola są nieprawidłowe:\n\n",
/* TR_INVALID_IO */
"Dane o porcie IO są nieprawidłowe",
/* TR_INVALID_IRQ */
"Dane o IRQ są nieprawidłowe",
/* TR_IP_ADDRESS_CR */
"Adres IP\n",
/* TR_IP_ADDRESS_PROMPT */
"Adres IP:",
/* TR_ISDN_CARD */
"Karta ISDN",
/* TR_ISDN_CARD_NOT_DETECTED */
"Karta ISDN nie została wykryta. Należy podać dodatkowe parametry modułu jeśli karta jest typu ISA lub jeśli ma specjalne wymagania.",
/* TR_ISDN_CARD_SELECTION */
"Wybierz kartę ISDN",
/* TR_ISDN_CONFIGURATION */
"Konfiguracja ISDN",
/* TR_ISDN_CONFIGURATION_MENU */
"Menu konfiguracyjne ISDN",
/* TR_ISDN_NOT_SETUP */
"ISDN nie jest skonfigurowany. Niektóre rzeczy nie zostały wybrane.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"ISDN nie został jeszcze skonfigurowany. Wybierz co chcesz skonfigurować",
/* TR_ISDN_PROTOCOL_SELECTION */
"Wybierz protokół ISDN.",
/* TR_ISDN_STATUS */
"ISDN jest obecnie %s.\n\nProtokół: %s\nKarta: %s\nNumer telefonu: %s\nWybierz co chcesz przekonfigurować, albo wybierz aktualne ustawienia.",
/* TR_KEYBOARD_MAPPING */
"Mapowanie klawiatury",
/* TR_KEYBOARD_MAPPING_LONG */
"Wybierz typ klawiatury którą używasz z poniższej listy.",
/* TR_LEASED_LINE */
"Linia dzierżawiona",
/* TR_LOADING_MODULE */
"Ładowanie modułów...",
/* TR_LOADING_PCMCIA */
"Ładowanie modułów PCMCIA...",
/* TR_LOOKING_FOR_NIC */
"Szukanie: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Tworzenie systemu plików dla boot...",
/* TR_MAKING_LOG_FILESYSTEM */
"Tworzenie systemu plików dla log...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Tworzenie systemu plików dla root...",
/* TR_MAKING_SWAPSPACE */
"Tworzenie pliku wymiany...",
/* TR_MANUAL */
"* RĘCZNIE *",
/* TR_MAX_LEASE */
"Maksymalny czas dzierżawy (w min):",
/* TR_MAX_LEASE_CR */
"Maksymalny czas dzierżawy\n",
/* TR_MISSING_BLUE_IP */
"Brakuje adresy IP dla interfejsu BLUE (Niebieskiego).",
/* TR_MISSING_ORANGE_IP */
"Brakuje adresu IP dla interfejsu ORANGE (Pomarańczowego).",
/* TR_MISSING_RED_IP */
"Brakuje adresu IP dla interfejsu RED (Czerwonego).",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"Nazwa modułu nie może być pusta.",
/* TR_MODULE_PARAMETERS */
"Podaj nazwa modułu i parametry dla wymaganego sterownika.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Montowanie systemu plików boot...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Montowanie systemu plików log...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Montowanie systemu plików root...",
/* TR_MOUNTING_SWAP_PARTITION */
"Montowanie partycji swap...",
/* TR_MSN_CONFIGURATION */
"Numer telefonu (MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Maska sieci:",
/* TR_NETWORKING */
"Sieć",
/* TR_NETWORK_ADDRESS_CR */
"Adres sieciowy\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Adres sieciowy:",
/* TR_NETWORK_CONFIGURATION_MENU */
"Menu konfiguracji sieci",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Typ konfiguracji sieci",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Wybierz konfiguracje sieciową dla %s. Konfiguracja typów dla następujących interfejsów siecowych. Jeśli zmienisz ustawienia wymagane będzie ponowne uruchomienie sieci, i będziesz musiał ponownie przekonfigurować zadania sieciowe.",
/* TR_NETWORK_MASK_CR */
"Maska sieci\n",
/* TR_NETWORK_SETUP_FAILED */
"Błąd ustawień sieci.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"Za mała ilość kart.",
/* TR_NO_BLUE_INTERFACE */
"Brak Blue (Niebieskiego) inerfejsu.",
/* TR_NO_CDROM */
"Brak CD-ROM-u",
/* TR_NO_HARDDISK */
"Brak twrdego dysku.",
/* TR_NO_IPCOP_TARBALL_FOUND */
"Brak archiwum ipcop na  serwerze.",
/* TR_NO_ORANGE_INTERFACE */
"Brak Pomarańczowego interfejsu",
/* TR_NO_RED_INTERFACE */
"Brak Czerwonego interfejsu.",
/* TR_NO_SCSI_IMAGE_FOUND */
"Brak obrazu z SCSI na serwerze.",
/* TR_NO_UNALLOCATED_CARDS */
"Nie ma więcej nieprzydzielonych kart sieciowych, potrzeba więcej. Możesz wyszukać automatycznie więcej kart lub wybrać ręcznie z listy.",
/* TR_OK */
"Ok",
/* TR_PARTITIONING_DISK */
"Partycjonowanie dysku.",
/* TR_PASSWORDS_DO_NOT_MATCH */
"Hasła nie pasują do siebie.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"Hasło nie może być puste.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"Hasło nie może zawierać spacji.",
/* TR_PASSWORD_PROMPT */
"Hasło:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Numer telefonu nie może być pusty.",
/* TR_PREPARE_HARDDISK */
"Program instalacyjny przygotuje dysk na %s. Najpierw dysk zostanie podzielony, potem partycje zostaną sformatowane.",
/* TR_PRESS_OK_TO_REBOOT */
"Wciśnij Ok aby ponownie uruchomić komputer.",
/* TR_PRIMARY_DNS */
"Podstawowy DNS:",
/* TR_PRIMARY_DNS_CR */
"Podstawowy DNS\n",
/* TR_PROBE */
"Wykryj.",
/* TR_PROBE_FAILED */
"Automatyczne wykrywanie nieudało się.",
/* TR_PROBING_SCSI */
"Wykrywanie urządzeń SCSI...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"Problem z ustawieniem %s hasła administratora.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"Problem z ustawieniem hasła dla użytkownika 'root'.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"Problem z ustawieniem hasła dla użytkownika 'setup'.",
/* TR_PROTOCOL_COUNTRY */
"Protokół/Kraj",
/* TR_PULLING_NETWORK_UP */
"Rozruch sieci...",
/* TR_PUSHING_NETWORK_DOWN */
"Zamykanie sieci...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Zamykanie połączeń innych niż lokalne... ",
/* TR_QUIT */
"Koniec",
/* TR_RED_IN_USE */
"ISDN (lub inne połączenie zewnętrzne) jest w użyciu. Nie możesz konfigurować jeśli ISDN lub Czerwony interfejs jest aktywny.",
/* TR_RESTART_REQUIRED */
"\n\nKiedy konfiguracja się zakończy, będzie wymagany rozruch ponowny sieci.",
/* TR_RESTORE */
"Odzyskaj.",
/* TR_RESTORE_CONFIGURATION */
"Jesłi masz dyskietke z %s konfiguracją systemu, włóż ją do napędu i wciśnij Odzyskaj.",
/* TR_ROOT_PASSWORD */
"Hasło root-a",
/* TR_SECONDARY_DNS */
"Dodatkowy DNS:",
/* TR_SECONDARY_DNS_CR */
"Dodatkowy DNS\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"Drugorzędny serwer DNS bez Pierwszorzędnego.",
/* TR_SECTION_MENU */
"Sekcja menu",
/* TR_SELECT */
"Wybierz",
/* TR_SELECT_CDROM_TYPE */
"Wybierz typ CD-ROM-u",
/* TR_SELECT_CDROM_TYPE_LONG */
"Nie wykryto CD-ROM-u w tym komputerze. Proszę wybrać  sterownik %s przy pomocy którego chcesz uruchomić CD-ROM.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Wybierz źródło instalacji.",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s może być instalowany z kilku źródeł. Najprościej jest użyć CD-ROM-u.Jeśli instalacja z płyty przebiega powoli, możesz instalować poprzez sieć LAN z instalacją udostępniona poprzez HTTP. W tym wypadku będzie wymagana dyskietka z driverami do kart sieciowych.",
/* TR_SELECT_NETWORK_DRIVER */
"Wybierz sterownik karty sieciowej.",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Wybierz sterownik do karty sieciowej zainstalowanej w twoim komputerze. Jeśli wybierzesz RĘCZNIE, będziesz miał możliwość podania nazwy modułu i parametrów dla driverów które tego wymagają, np. kart ISA.",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Wybierz interfejs do przekonfigurowania.",
/* TR_SELECT_THE_ITEM */
"Wybierz co chcesz skonfigurować.",
/* TR_SETTING_ADMIN_PASSWORD */
"Ustawianie %s hasła dla użytkownika 'admin'...",
/* TR_SETTING_ROOT_PASSWORD */
"Ustawieniem hasła dla użytkownika 'root'...",
/* TR_SETTING_SETUP_PASSWORD */
"Ustawianie %s hasła dla użytkownika 'setup'...",
/* TR_SETUP_FINISHED */
"Konfiguracja jest  skończona. Wciśnij Ok aby wykonać restart.",
/* TR_SETUP_NOT_COMPLETE */
"Uruchamianie instalacji nie zostało zakończone. Musisz się upewnić czy Konfiduracja jest skończona poprawnie poprzez uruchomienie 'setup'  z powłoki.",
/* TR_SETUP_PASSWORD */
"Hasło do 'setup'",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Podaj parametry dodatkowe dla modułu.",
/* TR_SINGLE_GREEN */
"Twoja konfiguracja dla interfejsu GREEN (Zielonego) jest ustawiona.",
/* TR_SKIP */
"Pomiń",
/* TR_START_ADDRESS */
"Adres początkowy:",
/* TR_START_ADDRESS_CR */
"Adres początkowy\n",
/* TR_STATIC */
"Statycznie",
/* TR_SUGGEST_IO */
"(proponowane %x)",
/* TR_SUGGEST_IRQ */
"(proponowane %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"Ten moduł jest już załadowany.",
/* TR_TIMEZONE */
"Strefa czasowa",
/* TR_TIMEZONE_LONG */
"Wybierz strefe czasową w której się znajdujesz.",
/* TR_UNABLE_TO_EJECT_CDROM */
"Nie można otworzyć CD-ROM-u.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Nie można rozpakować modułów.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Nie można znaleźć odpowiednich driverów.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Nie można znaleźć karty ISDN w twoim komputerze. Możesz potrzebować podać dodatkowe parametry jeśli karta jest typu ISDN to wymagane są dodatkowe parametry.",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"Nie można uruchomić ISDN.",
/* TR_UNABLE_TO_INSTALL_FILES */
"Nie można zaisntalować plików.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"Nie można zaisntalować GRUB-a.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Nie można załadować modułów.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Nie można stworzyć systemu plików dla boot.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Nie można stworzyć systemu plików dla log. ",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Nie można stworzyć systemu plików dla root.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Nie można stworzyć systemu plików dla swap.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Nie można stworzyć dowiązania symbolicznego /dev/harddisk",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Nie można stworzyć dowiązania symbolicznego /dev/harddisk1",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Nie można stworzyć dowiązania symbolicznego /dev/harddisk2",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Nie można stworzyć dowiązania symbolicznego /dev/harddisk3",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Nie można stworzyć dowiązania symbolicznego /dev/harddisk4",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Nie można stworzyć dowiązania symbloicznego /dev/root.",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Nie można zamontować boot.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Nie można zamontować log.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Nie można zamontować proc.",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Nie można zamontować root.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Nie można zamontować partycji swap.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Nie można otworzyć pliku hosts.",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Nie można otworzyć pliku z ustawieniami.",
/* TR_UNABLE_TO_PARTITION */
"Nie można spartycjonować dysku.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"Nie można usunąć tymczasowo ściągniętych plików.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"Nie można ustawić nazwy hosta.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"Nie można odmontować CD-ROM-u lub stacji dyskietek.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"Nie można odmontować dysku twardego.",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"Nie można zapisać do /etc/fstab",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"Nie można zapisać do /etc/hostname",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"Nie można zapisać do /etc/hosts",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"Nie można zapisać do /etc/hosts.allow",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"Nie można zapisać do /etc/hosts.deny",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"Nie można zapisać do %s/ethernet/settings.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"Nie można zapisać do %s/main/hostname.conf",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"Nie można zapisać do %s/main/settings",
/* TR_UNCLAIMED_DRIVER */
"Wykryto nieprzypisaną kartę sieciową typu:\n%s\n\nMożna ja użyć do:",
/* TR_UNKNOWN */
"NIEZNANY",
/* TR_UNSET */
"NIEUSTAWIONE",
/* TR_USB_KEY_VFAT_ERR */
"This USB key is invalid (no vfat partition found).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"OSTRZEŻENIE",
/* TR_WARNING_LONG */
"Jeśli zmienisz ten adres IP i jesteś zalogowany zdalnie, twoje połączenie z %s komputerem zostanie zerwane i będziesz musiał ponownie połączyć się na nowy adres IP. To jest ryzykowna operacja, powinna być przeprowadzana tylko wtedy, jeśli masz fizyczny dostęp do komputera, jeśli coś by poszło źle.",
/* TR_WELCOME */
"Witaj w programie instalacyjnym %s. Wybranie Anuluj na którymkolwiek z następnych ekranów zrestartuje komputer.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Twoja konfiguracja została ustawiona dla Zielonego interfejsu, który ma już skonfigurowany sterownik.",
}; 
  
