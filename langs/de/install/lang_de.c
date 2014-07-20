/*
 * German (de) Data File
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
 * IPCop translation
 * (c) 2003 Dirk Loss, Ludwig Steininger, Michael Knappe, Michael Linke,
 * Richard Hartmann, Ufuk Altinkaynak, Gerhard Abrahams, Benjamin Kohberg,
 * Samuel Wiktor 
 */
 
#include "libsmooth.h"

char *de_tr[] = {

/* TR_ISDN */
"ISDN",
/* TR_ERROR_PROBING_ISDN */
"Konnte ISDN Scan nicht durchführen.",
/* TR_PROBING_ISDN */
"Suche und konfiguriere ISDN Geräte.",
/* TR_MISSING_GREEN_IP */
"Fehlende IP auf der grünen Schnittstelle!",
/* TR_CHOOSE_FILESYSTEM */
"Bitte wählen Sie ihr Dateisystem aus:",
/* TR_NOT_ENOUGH_INTERFACES */
"Nicht genügend Netzwerkkarten für diese Auswahl gefunden.\n\nBenötigt: %d - Gefunden: %d\n",
/* TR_INTERFACE_CHANGE */
"Bitte wählen Sie das Interface aus das geändert werden soll.\n\n",
/* TR_NETCARD_COLOR */
"Zugewiesene Karten",
/* TR_REMOVE */
"Entfernen",
/* TR_MISSING_DNS */
"Kein DNS eingetragen\n",
/* TR_MISSING_DEFAULT */
"Kein default Gateway eingetragen.\n",
/* TR_JOURNAL_EXT3 */
"Erstelle Journal für Ext3...",
/* TR_CHOOSE_NETCARD */
"Bitte wählen Sie eine der untenstehenden Netzwerkkarten für die folgene Schnittstelle aus - %s.",
/* TR_NETCARDMENU2 */
"Erweitertes Netzwerkmenu",
/* TR_ERROR_INTERFACES */
"Es wurden leider keine freien Netzwerkkarten für die Schnittstelle in ihrem System gefunden.",
/* TR_REMOVE_CARD */
"Soll die Zuordnung der folgende Netzwerkkarte entfernt werden? - %s",
/* TR_JOURNAL_ERROR */
"Konnte das Journal nicht erstelle, verwende ext2 Fallback.",
/* TR_FILESYSTEM */
"Dateisystemauswahl",
/* TR_ADDRESS_SETTINGS */
"Adress-Einstellungen",
/* TR_ADMIN_PASSWORD */
"'admin'-Passwort",
/* TR_AGAIN_PROMPT */
"Wiederholung:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Alle Karten wurden erfolgreich zugeordnet.",
/* TR_AUTODETECT */
"* AUTOMATISCHE ERKENNUNG *",
/* TR_BUILDING_INITRD */
"Erzeuge Ramdisk...",
/* TR_CANCEL */
"Abbrechen",
/* TR_CARD_ASSIGNMENT */
"Karten-Zuordnung",
/* TR_CHECKING */
"Überprüfe URL...",
/* TR_CHECKING_FOR */
"Suche nach: %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Wähle die ISDN-Karte in diesem Computer aus:",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Wählen Sie das benötigte ISDN-Protokoll.",
/* TR_CONFIGURE_DHCP */
"Konfigurieren Sie den DHCP-Server durch Eingabe der Einstellungen:",
/* TR_CONFIGURE_NETWORKING */
"Netzwerk konfigurieren",
/* TR_CONFIGURE_NETWORKING_LONG */
"Sie sollten jetzt das Netzwerk konfigurieren. Laden Sie zunächst den richtigen Treiber für die GRÜNE Schnittstelle, indem Sie die Netzwerkkarte entweder automatisch erkennen lassen oder den richtigen Treiber aus einer Liste auswählen. Wenn Sie mehr als eine Netzwerkkarte installiert haben, können Sie die anderen später konfigurieren. Sollten Sie mehrere Karten vom gleichen Typ wie die an der GRÜNEN Schnittstelle haben und jede Karte spezielle Modulparameter benötigen, sollten Sie jetzt die Parameter für alle diese Karten eingeben, so dass alle Karten aktiv werden, wenn Sie die GRÜNE Schnittstelle konfigurieren.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Konfigurieren Sie die Netzwerktreiber und geben Sie an, welcher Schnittstelle jede Karte zugewiesen ist. Die aktuelle Konfiguration ist wie folgt:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"Konfigurieren Sie das CD-ROM-Laufwerk, indem Sie die richtigen Werte für IO-Adresse und/oder IRQ eingeben.",
/* TR_CONGRATULATIONS */
"Herzlichen Glückwunsch!",
/* TR_CONGRATULATIONS_LONG */
"%s wurde erfolgreich installiert. Entfernen Sie bitte alle eventuellen CDs aus dem Computer. Nun wird das Setup-Programm gestartet, in dem Sie ISDN, Netzwerkkarten und die Systempasswörter konfigurieren können. Wenn dies fertiggestellt ist, rufen Sie in Ihrem Webbrowser die Box mit https://%s:444 (oder welchen Namen Sie Ihrem %s auch immer gegeben haben) auf und konfigurieren die Wählverbindung und (falls nötig) die Fernwartung.",
/* TR_CONTINUE_NO_SWAP */
"Ihre Festplatte ist sehr klein, aber sie können mit einer minimalen Auslagerungspartition weitermachen. (Mit Vorsicht benutzen).",
/* TR_CURRENT_CONFIG */
"Aktuelle Einstellung: %s%s",
/* TR_DEFAULT_GATEWAY */
"Standard-Gateway:",
/* TR_DEFAULT_GATEWAY_CR */
"Standard-Gateway\n",
/* TR_DEFAULT_LEASE */
"Voreingestellte Haltezeit (min):",
/* TR_DEFAULT_LEASE_CR */
"Voreinstellung der Haltezeit\n",
/* TR_DETECTED */
"Gefunden wurde: %s",
/* TR_DHCP_HOSTNAME */
"DHCP-Hostname:",
/* TR_DHCP_HOSTNAME_CR */
"DHCP-Hostname\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"DHCP-Konfiguration",
/* TR_DISABLED */
"Deaktiviert",
/* TR_DISABLE_ISDN */
"ISDN deaktivieren",
/* TR_DISK_TOO_SMALL */
"Ihre Festplatte ist zu klein.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"DNS- und Gateway-Einstellungen",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Geben Sie die DNS- und Gateway-Informationen ein. Diese Einstellungen werden nur bei einer statischen IP an der ROTEN Schnittstelle benutzt (und DHCP, falls DNS eingetragen wurde).",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Ihre Konfiguration benutzt keine Ethernet-Karte für die ROTE Schnittstelle. DNS- und Gateway-Informationen für  Einwahl- verbindungen werden automatisch beim Einwählen konfiguriert.",
/* TR_DOMAINNAME */
"Domainname",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Domain Name darf nicht leer sein.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"Domainname darf keine Leerzeichen enthalten.",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Domain Name darf nur Buchstaben, Ziffern, Bindestriche und Punkte enthalten.",
/* TR_DOMAIN_NAME_SUFFIX */
"Domainnamen-Suffix:",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Domainnamen-Suffix\n",
/* TR_DONE */
"Fertig",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\nMöchten Sie die Einstellungen ändern?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Treiber- und Karten-Zuordnungen",
/* TR_ENABLED */
"aktiviert",
/* TR_ENABLE_ISDN */
"ISDN aktivieren",
/* TR_END_ADDRESS */
"Endadresse:",
/* TR_END_ADDRESS_CR */
"Endadresse\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Einige ISDN-Karten (besonders ISA-Karten) benötigen zusätzliche Modulparameter, um die IRQ- und IO-Adress-Informationen einzustellen. Wenn Sie eine solche ISDN-Karte haben, geben Sie diese Parameter hier ein (z. B. \"io=0x280 irq=9\"). Sie werden dann bei der Erkennung der Karte berücksichtigt.",
/* TR_ENTER_ADMIN_PASSWORD */
"Geben Sie das Passwort für den %s-Administrator 'admin' ein. Das ist der Benutzer, mit dem Sie sich an den %s-Webadministrationsseiten anmelden.",
/* TR_ENTER_DOMAINNAME */
"Bitte geben Sie den Domainnamen ein",
/* TR_ENTER_HOSTNAME */
"Geben Sie den Hostnamen des Rechners an:",
/* TR_ENTER_IP_ADDRESS_INFO */
"Geben Sie die IP-Adressinformationen ein",
/* TR_ENTER_NETWORK_DRIVER */
"Kann die Netzwerkkarte nicht automatisch erkennen. Geben Sie den Modulnamen und eventuelle Parameter für die Netzwerkkarte an.",
/* TR_ENTER_ROOT_PASSWORD */
"Geben Sie das Passwort für den Benutzer 'root' ein. Melden Sie sich als dieser Benutzer an, um Zugriff auf die Befehlszeile zu erhalten.",
/* TR_ENTER_SETUP_PASSWORD */
"Geben Sie das Passwort für den Benutzer 'setup' ein. Melden Sie sich als dieser Benutzer an, um das Setup-Programm zu starten.",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Geben Sie die IP-Adressinformationen für die folgende Schnittstelle ein - %s.",
/* TR_ENTER_THE_LOCAL_MSN */
"Geben Sie Ihre lokale Telefonnummer ein (MSN/EAZ):",
/* TR_ENTER_URL */
"Geben Sie die URL für ipcop-<version>.tgz und die images/scsidrv-<version>.img-Dateien ein. WARNUNG: DNS ist nicht verfügbar! Sie sollten jetzt nur etwas im Format 'http://X.X.X.X/<verzeichnis>' eingeben. ",
/* TR_ERROR */
"Fehler",
/* TR_ERROR_PROBING_CDROM */
"Kein CDROM-Laufwerk gefunden.",
/* TR_ERROR_WRITING_CONFIG */
"Fehler beim Schreiben der Konfigurationsinformationen.",
/* TR_EURO_EDSS1 */
"DSS1 (Euro-ISDN) (meist richtig)",
/* TR_EXTRACTING_MODULES */
"Entpacke die Module...",
/* TR_FAILED_TO_FIND */
"Konnte die URL-Datei nicht finden.",
/* TR_FOUND_NIC */
"%s hat den folgenden NIC in Ihrer Maschine erkannt: %s",
/* TR_GERMAN_1TR6 */
"1TR6",
/* TR_HELPLINE */
"       <Tab>/<Alt-Tab> wechselt zwischen Elementen | <Leertaste> wählt aus",
/* TR_HOSTNAME */
"Hostname",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Der Hostname darf nicht leer sein.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"Der Hostname darf keine Leerzeichen enthalten.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"Hostname darf nur Buchstaben, Ziffern und Bindestriche enthalten.",
/* TR_INITIALISING_ISDN */
"Initialisiere ISDN...",
/* TR_INSERT_CDROM */
"Legen Sie bitte die %s CD in das CD-ROM-Laufwerk ein.",
/* TR_INSERT_FLOPPY */
"Legen Sie bitte die %s-Treiberdiskette in das Diskettenlaufwerk ein.",
/* TR_INSTALLATION_CANCELED */
"Installation abgebrochen.",
/* TR_INSTALLING_FILES */
"Installiere Dateien...",
/* TR_INSTALLING_GRUB */
"Installiere GRUB...",
/* TR_INSTALLING_LANG_CACHE */
"Installiere Sprachunterstützung...",
/* TR_INTERFACE */
"Schnittstelle - %s",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"Schnittstelle konnte nicht aktiviert werden.",
/* TR_INVALID_FIELDS */
"Die folgenden Felder sind ungültig:\n\n",
/* TR_INVALID_IO */
"Die angegebenen Einstellungen für den IO-Port sind ungültig. ",
/* TR_INVALID_IRQ */
"Die eingegebenen IRQ-Einstellungen sind ungültig.",
/* TR_IP_ADDRESS_CR */
"IP-Adresse\n",
/* TR_IP_ADDRESS_PROMPT */
"IP-Adresse:",
/* TR_ISDN_CARD */
"ISDN-Karte",
/* TR_ISDN_CARD_NOT_DETECTED */
"Keine ISDN-Karte gefunden. Möglicherweise müssen Sie zusätzliche Modulparameter angeben, wenn es sich um eine ISA-Karte handelt oder die Karte spezielle Anforderungen hat.",
/* TR_ISDN_CARD_SELECTION */
"Auswahl der ISDN-Karte",
/* TR_ISDN_CONFIGURATION */
"ISDN-Konfiguration",
/* TR_ISDN_CONFIGURATION_MENU */
"ISDN-Konfigurationsmenü",
/* TR_ISDN_NOT_SETUP */
"ISDN nicht eingestellt. Einige Parameter wurden nicht ausgewählt.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"ISDN wurde noch nicht konfiguriert. Wählen Sie aus, was Sie konfigurieren möchten.",
/* TR_ISDN_PROTOCOL_SELECTION */
"Auswahl des ISDN-Protokolls",
/* TR_ISDN_STATUS */
"ISDN ist momentan %s.\n\n   Protokoll: %s\n   Karte: %s\n   Lokale Telefonnummer: %s\n\nWählen Sie aus, was Sie konfigurieren möchten, oder verwerfen Sie die aktuellen Einstellungen.",
/* TR_KEYBOARD_MAPPING */
"Tastatur-Layout",
/* TR_KEYBOARD_MAPPING_LONG */
"Wählen Sie aus dieser Liste den Tastatur-Typ aus, den Sie benutzen.",
/* TR_LEASED_LINE */
"Standleitung (leased line)",
/* TR_LOADING_MODULE */
"Lade Modul...",
/* TR_LOADING_PCMCIA */
"PCMCIA-Module werden geladen...",
/* TR_LOOKING_FOR_NIC */
"Suche nach: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Erstelle das Boot-Dateisystem...",
/* TR_MAKING_LOG_FILESYSTEM */
"Erstelle das Log-Dateisystem...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Erstelle das Root-Dateisystem...",
/* TR_MAKING_SWAPSPACE */
"Erstelle Swap-Partition...",
/* TR_MANUAL */
"* MANUELL *",
/* TR_MAX_LEASE */
"Maximale Haltezeit (min):",
/* TR_MAX_LEASE_CR */
"Maximale Haltezeit\n",
/* TR_MISSING_BLUE_IP */
"Fehlende IP-Information für das BLAUE Interface.",
/* TR_MISSING_ORANGE_IP */
"IP-Informationen für die ORANGE Schnittstelle fehlen.",
/* TR_MISSING_RED_IP */
"IP-Informationen für die ROTE Schnittstelle fehlen.",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"Der Modulname darf nicht leer sein.",
/* TR_MODULE_PARAMETERS */
"Geben Sie den Modulnamen und die Parameter für den benötigten Treiber an.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Mounte das Boot-Dateisystem...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Mounte das Log-Dateisystem...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Mounte das Root-Dateisystem...",
/* TR_MOUNTING_SWAP_PARTITION */
"Mounte die Swap-Partition...",
/* TR_MSN_CONFIGURATION */
"Lokale Telefonnummer (MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Subnetzmaske:",
/* TR_NETWORKING */
"Netzwerk",
/* TR_NETWORK_ADDRESS_CR */
"Netzwerkadresse\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Netzwerkadresse:",
/* TR_NETWORK_CONFIGURATION_MENU */
"Netzwerkkonfiguration",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Typ der Netzwerkkonfiguration",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Wählen Sie die Netzwerkkonfiguration für %s aus. Die folgenden Konfigurationstypen listen diejenigen Schnittstellen auf, die am Ethernet angeschlossen sind. Wenn Sie diese Einstellung ändern, muss das Netzwerk neu gestartet werden und Sie müssen die Netzwerktreiber neu zuweisen.",
/* TR_NETWORK_MASK_CR */
"Subnetzmaske\n",
/* TR_NETWORK_SETUP_FAILED */
"Netzwerk-Setup fehlgeschlagen.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"Nicht genügend Karten wurden zugeordnet.",
/* TR_NO_BLUE_INTERFACE */
"Kein BLAUES Interface zugeordnet.",
/* TR_NO_CDROM */
"Kein CD-ROM gefunden.",
/* TR_NO_GREEN_INTERFACE */
"Keine GRÜNE Schnittstelle zugewiesen.",
/* TR_NO_HARDDISK */
"Keine Festplatte gefunden.",
/* TR_DISK_SELECTION */
"Festplattenauswahl",
/* TR_DISK_SELECTION_MSG */
"Wählen Sie die Festplatte(n), auf die Sie IPFire installieren möchten. Diese wird dann zuerst partitioniert und danach wird ein Dateisystem auf die Partitionen installiert.\n\nALLE DATEN AUF DER FESTPLATTE WERDEN GELÖSCHT.",
/* TR_NO_DISK_SELECTED */
"Es wurde kein Datenträger ausgewählt.\n\nBitte wählen Sie einen oder mehrere Festplatten aus, um mit der Installation fortzufahren.",
/* TR_DISK_SETUP */
"Festplatten-Setup",
/* TR_DISK_SETUP_DESC */
"Das Installationsprogramm wird nun die ausgewählte Festplatte vorbereiten:\n\n  %s\n\nMöchten Sie fortfahren?",
/* TR_RAID_SETUP */
"RAID-Setup",
/* TR_RAID_SETUP_DESC */
"Das Installationsprogramm wird nun eine RAID-Konfiguration auf den ausgewählten Festplatten anlegen:\n\n  %s\n  %s\n\nMöchten Sie fortfahren?",
/* TR_DELETE_ALL_DATA */
"Alle Daten löschen",
/* TR_NO_IPCOP_TARBALL_FOUND */
"Auf dem Webserver wurde kein ipcop-Tarball gefunden.",
/* TR_NO_ORANGE_INTERFACE */
"Keine ORANGE Schnittstelle zugewiesen.",
/* TR_NO_RED_INTERFACE */
"Keine ROTE Schnittstelle zugewiesen.",
/* TR_NO_SCSI_IMAGE_FOUND */
"Auf dem Webserver wurde kein SCSI-Image gefunden.",
/* TR_NO_UNALLOCATED_CARDS */
"Es sind keine nicht zugeteilten Karten übrig; es werden aber noch mehr benötigt. Sie könnten einen Treiber aus der Liste auswählen oder eine automatische Erkennung starten.",
/* TR_OK */
"Ok",
/* TR_PARTITIONING_DISK */
"Partitioniere die Festplatte...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"Die Passwörter stimmen nicht überein.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"Die Passwörter dürfen nicht leer sein.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"Das Passwort darf keine Leerzeichen enthalten.",
/* TR_PASSWORD_PROMPT */
"Passwort:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Die Telefonnummer darf nicht leer sein.",
/* TR_PREPARE_HARDDISK */
"Das Installationsprogramm wird jetzt die Festplatte %s vorbereiten. Zunächst wird die Festplatte partitioniert. Danach wird auf den Partitionen ein Dateisystem erstellt.\n\nALLE DATEN AUF DEM LAUFWERK WERDEN GELÖSCHT. Einverstanden?",
/* TR_PRESS_OK_TO_REBOOT */
"Drücken Sie Ok, um neu zu starten.",
/* TR_PRIMARY_DNS */
"Primärer DNS:",
/* TR_PRIMARY_DNS_CR */
"Primärer DNS\n",
/* TR_PROBE */
"Automatische Erkennung",
/* TR_PROBE_FAILED */
"Automatische Erkennung fehlgeschlagen.",
/* TR_PROBING_HARDWARE */
"Hardwareerkennung läuft...",
/* TR_PROBING_FOR_NICS */
"Netzwerkkartenerkennung läuft...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"Problem beim Setzen des %s Administrator-Passworts.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"Problem beim Setzen des 'root'-Passworts.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"Problem beim Setzen des 'setup'-Passworts.",
/* TR_PROTOCOL_COUNTRY */
"Protokoll/Land",
/* TR_PULLING_NETWORK_UP */
"Starte Netzwerk...",
/* TR_PUSHING_NETWORK_DOWN */
"Fahre Netzwerk herunter...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Fahre nicht-lokales Netzwerk herunter...",
/* TR_QUIT */
"Beenden",
/* TR_RED_IN_USE */
"ISDN (oder eine andere externe Verbindung) wird momentan benutzt. Sie können ISDN nicht konfigurieren, während die ROTE Schnittstelle aktiv ist.",
/* TR_RESTART_REQUIRED */
"\n\nWenn die Konfiguration komplett ist, muss das Netzwerk neu gestartet werden.",
/* TR_RESTORE */
"Wiederherstellen",
/* TR_RESTORE_CONFIGURATION */
"Falls Sie eine Diskette mit %s-Systemeinstellungen haben, legen Sie die Diskette in das Floppylaufwerk und \ndrücken auf <Wiederherstellen>",
/* TR_ROOT_PASSWORD */
"'root'-Passwort",
/* TR_SECONDARY_DNS */
"Sekundärer DNS:",
/* TR_SECONDARY_DNS_CR */
"Sekundärer DNS\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"Sekundären DNS angegeben ohne primären DNS",
/* TR_SECTION_MENU */
"Auswahlmenu",
/* TR_SELECT */
"Auswählen",
/* TR_SELECT_CDROM_TYPE */
"Wählen Sie den Typ des CD-ROM-Laufwerks aus",
/* TR_SELECT_CDROM_TYPE_LONG */
"Es wurde kein CD-ROM-Laufwerk in diesem Rechner gefunden. Bitte wählen Sie aus, welchen der folgenden Treiber Sie benutzen möchten, damit %s das CD-ROM-Laufwerk ansprechen kann.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Wählen Sie das Installationsmedium",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s kann von verschiedenen Programmquellen installiert werden.  Am einfachsten ist, Sie benutzen das eingebaute CD-ROM-Laufwerk. Falls der Computer kein CD-ROM-Laufwerk besitzt, können Sie von einem anderen Rechner im LAN installieren, der die Installationsdateien per HTTP oder FTP zur Verfügung stellt.",
/* TR_SELECT_NETWORK_DRIVER */
"Wählen Sie den Netzwerktreiber aus",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Wählen Sie den Treiber für die in diesem Rechner eingebaute Netzwerkkarte aus. Wenn Sie MANUELL auswählen, können Sie den Modulnamen des Treibers  und die Parameter selbst angeben (z. B. für Treiber mit speziellen Anforderungen, wie bei ISA-Karten).",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Wählen Sie die Schnittstelle aus, die Sie neu konfigurieren möchten.",
/* TR_SELECT_THE_ITEM */
"Wählen Sie den Punkt aus, den Sie konfigurieren möchten:",
/* TR_SETTING_ADMIN_PASSWORD */
"Setze %s-Administrator-Passwort....",
/* TR_SETTING_ROOT_PASSWORD */
"Setze 'root'-Passwort....",
/* TR_SETTING_SETUP_PASSWORD */
"Setze 'setup'-Passwort...",
/* TR_SETUP_FINISHED */
"Das Setup ist vollständig beendet. Drücken Sie Ok.",
/* TR_SETUP_NOT_COMPLETE */
"Das erste Setup wurde nicht vollständig durchgeführt. Sie müssen Setup vollständig beenden; dies können Sie durch Ausführen von Setup in der Shell nachholen.",
/* TR_SETUP_PASSWORD */
"'setup'-Passwort",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Zusätzliche Modulparameter angeben",
/* TR_SINGLE_GREEN */
"In ihrer Konfiguration ist eine GRÜNE Schnittstelle eingestellt.",
/* TR_SKIP */
"Überspringen",
/* TR_START_ADDRESS */
"Anfangsadresse:",
/* TR_START_ADDRESS_CR */
"Anfangsadressen\n",
/* TR_STATIC */
"Statisch",
/* TR_SUGGEST_IO */
"(schlage vor %x)",
/* TR_SUGGEST_IRQ */
"(schlage vor %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"Dieses Treibermodul ist bereits geladen.",
/* TR_TIMEZONE */
"Zeitzone",
/* TR_TIMEZONE_LONG */
"Wählen Sie die Zeitzone aus, in der Sie sich befinden.",
/* TR_UNABLE_TO_EJECT_CDROM */
"Kann die CD-ROM nicht auswerfen.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Module können nicht extrahiert werden.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Kann keine weiteren Treiber finden.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Kann keine ISDN-Karte in diesem Computer finden. Möglicherweise müssen Sie zusätzliche Modulparameter angeben, wenn es sich um eine ISA-Karte handelt oder die Karte spezielle Anforderungen hat.",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"Kann ISDN nicht initialisieren.",
/* TR_UNABLE_TO_INSTALL_FILES */
"Kann die Dateien nicht installieren.",
/* TR_UNABLE_TO_INSTALL_LANG_CACHE */
"Kann Sprachunterstützung nicht installieren.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"Kann GRUB nicht installieren.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Kann Treibermodul nicht laden.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Kann das Boot-Dateisystem nicht erstellen.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Kann das Log-Dateisystem nicht erstellen.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Kann das Root-Dateisystem nicht erstellen.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Kann Swap-Partition nicht erstellen.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Kann symbolischen Link /dev/harddisk nicht anlegen.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Kann symbolischen Link /dev/harddisk1 nicht anlegen.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Kann symbolischen Link /dev/harddisk2 nicht anlegen.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Kann symbolischen Link /dev/harddisk3 nicht anlegen.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Kann symbolischen Link /dev/harddisk4 nicht anlegen.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Symlink /dev/root kann nicht erzeugt werden.",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Kann das Root-Dateisystem nicht mounten.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Kann das Log-Dateisystem nicht mounten.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Das proc-Dateisystem kann nicht gemountet werden.",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Kann das Root-Dateisystem nicht mounten.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Kann die Swap-Partition nicht unmounten.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Kann primäre hosts-Datei nicht öffnen.",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Kann Datei mit Einstellungen nicht öffnen",
/* TR_UNABLE_TO_PARTITION */
"Kann die Festplatte nicht partitionieren.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"Kann temporär heruntergeladene Dateien nicht löschen.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"Kann Hostnamen nicht setzen.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"Kann die CD-ROM bzw. Floppy nicht unmounten.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"Kann die Festplatte nicht unmounten.",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"Kann /etc/fstab nicht schreiben",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"Kann /etc/hostname nicht schreiben",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"Kann /etc/hosts nicht schreiben.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"Kann /etc/hosts.allow nicht schreiben.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"Kann /etc/hosts.deny nicht schreiben.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"Kann %s/ethernet/settings nicht schreiben.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"Kann %s/main/hostname.conf nicht schreiben",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"Kann %s/main/settings nicht schreiben.",
/* TR_UNCLAIMED_DRIVER */
"Es gibt eine nicht zugeordnete Ethernet-Karte des Typs:\n%s\n\nSie können sie zuweisen an:",
/* TR_UNKNOWN */
"UNBEKANNT",
/* TR_UNSET */
"NICHT GESETZT",
/* TR_USB_KEY_VFAT_ERR */
"Dieser USB-Stick ist ungültig (keine VFAT Partiton gefunden).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"WARNUNG",
/* TR_WARNING_LONG */
"Wenn Sie diese IP-Adresse ändern, während Sie über den Fernwartungszugang zugreifen, wird die Verbindung zum %s-Rechner abbrechen. Sie müssen dann eine Verbindung zur neuen IP-Adresse aufbauen. Dies ist ein riskanter Vorgang, der nur versucht werden sollte, wenn Sie physikalischen Zugriff auf den Rechner haben, für den Fall, dass etwas schief geht.",
/* TR_WELCOME */
"Willkommen zum %s Installationsprogramm. Wenn Sie auf irgendeiner der folgenden Seiten 'Abbrechen' auswählen, wird der Computer neu gestartet.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Ihre Konfiguration ist für eine einzelne GRÜNE Schnittstelle eingestellt, der bereits ein Treiber zugewiesen ist.",
/* TR_YES */
"Ja",
/* TR_NO */
"Nein",
/* TR_AS */
"als",
/* TR_IGNORE */
"Ignorieren",
/* TR_PPP_DIALUP */
"PPP Einwahl (PPPoE, Modem, ATM ...)",
/* TR_DHCP */
"DHCP",
/* TR_DHCP_STARTSERVER */
"Starte den DHCP-Server ...",
/* TR_DHCP_STOPSERVER */
"Stoppe den DHCP-Server ...",
/* TR_LICENSE_ACCEPT */
"Ich akzeptiere diese Lizenz.",
/* TR_LICENSE_NOT_ACCEPTED */
"Die Lizenz wurde nicht akzeptiert. Abbruch!",
/* TR_EXT2FS_DESCR */
"Ext2 - Dateisystem ohne Journal (empfohlen für Flash)",
/* TR_EXT3FS_DESCR */
"Ext3 - Dateisystem mit Journal",
/* TR_EXT4FS_DESCR */
"Ext4 - Dateisystem mit Journal",
/* TR_REISERFS_DESCR */
"ReiserFS - Dateisystem mit Journal",
/* TR_NO_LOCAL_SOURCE */
"Kein lokales Quellmedium gefunden. Starte Download.",
/* TR_DOWNLOADING_ISO */
"Lade Installations-Abbild ...",
/* TR_DOWNLOAD_ERROR */
"Beim Herunterladen ist ein Fehler aufgetreten!",
/* TR_DHCP_FORCE_MTU */
"DHCP MTU setzen:",
/* TR_IDENTIFY */
"Identifizieren",
/* TR_IDENTIFY_SHOULD_BLINK */
"Die Leds dieses Netzwerkports sollten jetzt blinken ...",
/* TR_IDENTIFY_NOT_SUPPORTED */
"Dieser Netzwerkport untestützt die Funktion leider nicht.",
};
