/*
 * Italian (it) Data File
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
 * You sh ould have received a copy of the GNU General Public License
 * along with IPCop; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
 * 
 * (c) The SmoothWall Team
 * 
 * IPCop translation
 * (c) 2003 Fabio Gava, Antonio Stano, Marco Spreafico, Filippo Carletti 
 */
 
#include "libsmooth.h"

char *it_tr[] = {

/* TR_ADDRESS_SETTINGS */
"Impostazioni indirizzo",
/* TR_ADMIN_PASSWORD */
"Password per Admin",
/* TR_AGAIN_PROMPT */
"Conferma password:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Tutte le schede sono state assegnate.",
/* TR_AUTODETECT */
"* AUTOMATICO *",
/* TR_BUILDING_INITRD */
"Creazione INITRD...",
/* TR_CANCEL */
"Annulla",
/* TR_CARD_ASSIGNMENT */
"Assegnamento schede",
/* TR_CHECKING */
"Controllo URL...",
/* TR_CHECKING_FOR */
"Controllo per: %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Scegliere quale scheda ISDN è installata sul computer.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Selezionare il protocollo ISDN richiesto.",
/* TR_CONFIGURE_DHCP */
"Configurare il server DHCP inserendo le seguenti informazioni.",
/* TR_CONFIGURE_NETWORKING */
"Configurazione della rete",
/* TR_CONFIGURE_NETWORKING_LONG */
"Si dovrebbe configurare la rete caricando un driver corretto per l'interfaccia GREEN. E' possibile utilizzare l'auto-riconoscimento della scheda di rete o selezionare il driver corretto da una lista. Se si hanno più schede installate, le altre saranno configurate successivamente durante l'installazione. Si noti che se si hanno più schede di rete del medesimo tipo della GREEN e tali schede richiedono dei parametri particolari, si dovrebbero inserire i parametri per tali schede in modo da renderle attive al momento della configurazione dell'interfaccia GREEN.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Configurare le schede di rete, e indicare a quale interfaccia ogni scheda è assegnata. L'attuale configurazione è la seguente:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"Configurare il CDROM scegliendo l'indirizzo IO e/o l'IRQ appropriati.",
/* TR_CONGRATULATIONS */
"Congratulazioni!",
/* TR_CONGRATULATIONS_LONG */
"%s è stato correttamente installato. Rimuovere tutti i floppy o i CDROM presenti. L'installazione consentirà ora di configurare ISDN, schede di rete, e le password di sistema. Al termine dell'installazione puntare il proprio browser all'indirizzo http://%s:81 o https://%s:445 (o comunque sia stato chiamato %s), e configurare l'accesso via modem (se richiesto) e l'accesso remoto. Si ricordi di impostare una password per l'utente 'dial' di %s se non si desidera lasciare la possibilità ad 'admin' di controllare la connessione.",
/* TR_CONTINUE_NO_SWAP */
"L'hard disk è molto piccolo, ma è possibile continuare senza area swap. (Usare con cautela).",
/* TR_CURRENT_CONFIG */
"Impostazioni correnti: %s%s",
/* TR_DEFAULT_GATEWAY */
"Gateway di default:",
/* TR_DEFAULT_GATEWAY_CR */
"Gateway di default\n",
/* TR_DEFAULT_LEASE */
"Lease di default (min):",
/* TR_DEFAULT_LEASE_CR */
"Lease di default\n",
/* TR_DETECTED */
"Rilevata come: %s",
/* TR_DHCP_HOSTNAME */
"DHCP Hostname:",
/* TR_DHCP_HOSTNAME_CR */
"DHCP Hostname\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"Configurazione server DHCP",
/* TR_DISABLED */
"Disabilitato",
/* TR_DISABLE_ISDN */
"Disabilita ISDN",
/* TR_DISK_TOO_SMALL */
"L'hard disk è troppo piccolo.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"Impostazioni DNS e Gateway",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Inserire le informazioni per DNS e gateway. Queste informazioni saranno usate nel caso il DHCP sia disabilitato sull'interfaccia ROSSA.",
/* TR_DNS_GATEWAY_WITH_GREEN */
"La configurazione attuale non utilizza una scheda ethernet per l'interfaccia ROSSA. Le informazioni di DNS e gateway sono configurate automaticamente alla connessione.",
/* TR_DOMAINNAME */
"Nome dominio",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Il nome a dominio non può essere vuoto.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"Il nome dominio non può contenere spazi.",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Il nome del dominio può contenere solo lettere, numeri, trattini e punti.",
/* TR_DOMAIN_NAME_SUFFIX */
"Suffisso nome dominio:",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Suffisso nome dominio\n",
/* TR_DONE */
"Finito",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\nSi desidera cambiare queste impostazioni?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Impostazioni driver e schede",
/* TR_ENABLED */
"Abilitato",
/* TR_ENABLE_ISDN */
"Abilita ISDN",
/* TR_END_ADDRESS */
"Indirizzo finale:",
/* TR_END_ADDRESS_CR */
"Indirizzo finale\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Alcune schede ISDN (specialmente quelle ISA) possono richiedere parametri aggiuntivi per le informazioni di IRQ o di indirizzo IO. Se si dispone di tale scheda ISDN, inserire ora tali parametri. Per esempio: \"io=0x280 irq=9\". Saranno usati durante il rilevamento della scheda.",
/* TR_ENTER_ADMIN_PASSWORD */
"Inserire la password di 'admin' per %s. Questo utente sarà autorizzato ad accedere alle pagine web di amministrazione di %s.",
/* TR_ENTER_DOMAINNAME */
"Inserire nome dominio",
/* TR_ENTER_HOSTNAME */
"Inserire l'hostname della macchina.",
/* TR_ENTER_IP_ADDRESS_INFO */
"Inserire le informazioni dell'inidirizzo IP",
/* TR_ENTER_NETWORK_DRIVER */
"Impossibile rilevare automaticamente la scheda di rete. Inserire il driver e gli eventuali parametri opzionali per la scheda di rete.",
/* TR_ENTER_ROOT_PASSWORD */
"Inserire la password per l'utente 'root'. Accedere come 'root' per la riga di comando.",
/* TR_ENTER_SETUP_PASSWORD */
"Inserire la password per l'utente 'setup'. Accedere come 'setup' per eseguire il programma di setup.",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Inserire le informazioni IP per l'interfaccia %s.",
/* TR_ENTER_THE_LOCAL_MSN */
"Inserire il numero di telefono locale (MSN/EAZ).",
/* TR_ENTER_URL */
"Inserire il path URL per il files ipcop-<version>.tgz e images/scsidrv-<version>.img. ATTENZIONE: DNS non disponibile! Si dovrebbe usare solo http://X.X.X.X/<directory>",
/* TR_ERROR */
"Errore",
/* TR_ERROR_WRITING_CONFIG */
"Errore nella scrittura delle informazioni di configurazione.",
/* TR_EURO_EDSS1 */
"Euro (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Estrazione moduli...",
/* TR_FAILED_TO_FIND */
"Impossibile trovare il file URL.",
/* TR_FOUND_NIC */
"%s ha rilevato le seguenti schede di rete: %s",
/* TR_GERMAN_1TR6 */
"German 1TR6",
/* TR_HELPLINE */
"              <Tab>/<Alt-Tab> cambia elemento   |  <Space> seleziona",
/* TR_HOSTNAME */
"Hostname",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Hostname non può essere vuoto.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"Hostname non può contenere spazi.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"L'hostname può contenere solo lettere, numeri e trattini.",
/* TR_INITIALISING_ISDN */
"Inizializzazione ISDN...",
/* TR_INSERT_CDROM */
"Inserire il CD di %s nel drive CDROM.",
/* TR_INSERT_FLOPPY */
"Inserire il floppy del driver di %s.",
/* TR_INSTALLATION_CANCELED */
"Installaziona annullata.",
/* TR_INSTALLING_FILES */
"Installazione files...",
/* TR_INSTALLING_GRUB */
"Installazione GRUB...",
/* TR_INTERFACE */
"Interfaccia %s",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"Errore nell'attivazione dell'interfaccia.",
/* TR_INVALID_FIELDS */
"I seguenti campi non sono validi:\n\n",
/* TR_INVALID_IO */
"I dettagli inseriti per la porta IO non sono validi.",
/* TR_INVALID_IRQ */
"Le informazioni IRQ fornite non sono valide.",
/* TR_IP_ADDRESS_CR */
"Indirizzo IP\n",
/* TR_IP_ADDRESS_PROMPT */
"Indirizzo IP:",
/* TR_ISDN_CARD */
"Scheda ISDN",
/* TR_ISDN_CARD_NOT_DETECTED */
"Scheda ISDN non rilevata. E' necessario specificare i parametri opzionali se la scheda è di tipo ISA o richiede particolari impostazioni.",
/* TR_ISDN_CARD_SELECTION */
"Selezione scheda ISDN",
/* TR_ISDN_CONFIGURATION */
"Configurazione ISDN",
/* TR_ISDN_CONFIGURATION_MENU */
"Menu confugurazione ISDN",
/* TR_ISDN_NOT_SETUP */
"ISDN non impostata. Alcuni elementi non sono stati selezionati.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"L'ISDN non è stata ancora configurata. Selezionare l'elemento da configurare.",
/* TR_ISDN_PROTOCOL_SELECTION */
"Selezione protocollo ISDN",
/* TR_ISDN_STATUS */
"L'ISDN è attualmente %s.\n\n   Protocollo: %s\n   Scheda: %s\n   Numero telefonico locale: %s\n\nSelezionare l'elemento da riconfigurare, o scegliere di utilizzare le impostazioni correnti.",
/* TR_KEYBOARD_MAPPING */
"Mappatura tastiera",
/* TR_KEYBOARD_MAPPING_LONG */
"Selezionare il tipo di tastiera in uso dalla lista sottostante.",
/* TR_LEASED_LINE */
"Linea dedicata",
/* TR_LOADING_MODULE */
"Caricamento modulo...",
/* TR_LOADING_PCMCIA */
"Caricamento moduli PCMCIA...",
/* TR_LOOKING_FOR_NIC */
"Ricerca: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Creazione filesystem di boot...",
/* TR_MAKING_LOG_FILESYSTEM */
"Creazione filesystem di log...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Creazione del filesystem di root...",
/* TR_MAKING_SWAPSPACE */
"Creazione dell'area swap...",
/* TR_MANUAL */
"* MANUAL *",
/* TR_MAX_LEASE */
"Lease massimo (min):",
/* TR_MAX_LEASE_CR */
"Lease massimo\n",
/* TR_MISSING_BLUE_IP */
"Mancano le informazioni IP per l'interfaccia BLU.",
/* TR_MISSING_ORANGE_IP */
"Mancano le informazioni IP per l'interfaccia ARANCIO.",
/* TR_MISSING_RED_IP */
"Mancano le informazioni IP per l'interfaccia ROSSA.",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"Il nome del modulo non può essere vuoto.",
/* TR_MODULE_PARAMETERS */
"Inserire il nome del modulo ed i parametri che esso richiede.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Mounting filesystem di boot...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Mounting filesystem di log...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Mounting filesystem di root...",
/* TR_MOUNTING_SWAP_PARTITION */
"Mounting swap partition...",
/* TR_MSN_CONFIGURATION */
"Numero di telefono locale (MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Net mask:",
/* TR_NETWORKING */
"Rete",
/* TR_NETWORK_ADDRESS_CR */
"Indirizzo di rete\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Indirizzo di rete:",
/* TR_NETWORK_CONFIGURATION_MENU */
"Menu configurazione rete",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Configurazione del tipo di rete",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Selezionare la configurazione di rete per %s. I tipi di configurazione che seguono elencano le interfacce connesse ad ethernet. Se si modificano questi valori sarà necessario riavviare la rete e sarà anche necessario riconfigurare le impostazioni dei driver di rete.",
/* TR_NETWORK_MASK_CR */
"Net mask\n",
/* TR_NETWORK_SETUP_FAILED */
"Impostazione della rete fallita.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"Non tutte le schede sono state assegnate.",
/* TR_NO_BLUE_INTERFACE */
"Interfaccia BLU non assegnata.",
/* TR_NO_CDROM */
"CD-ROM non trovato.",
/* TR_NO_HARDDISK */
"Nessun hard disk trovato.",
/* TR_NO_IPCOP_TARBALL_FOUND */
"Impossibile trovare il tarball sul server web.",
/* TR_NO_ORANGE_INTERFACE */
"Nessuna interfaccia ARANCIO assegnata.",
/* TR_NO_RED_INTERFACE */
"Nessuna interfaccia ROSSA assegnata.",
/* TR_NO_SCSI_IMAGE_FOUND */
"Immagine SCSI non trovata sul web server.",
/* TR_NO_UNALLOCATED_CARDS */
"Rimangono delle schede non assegnate, ed altre sono richieste. E' possibile rilevare automaticamente e cercare altre schede, o scegliere di selezionare un driver da una lista.",
/* TR_OK */
"Ok",
/* TR_PARTITIONING_DISK */
"Partizionamento del disco...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"Le password non coincidono.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"La password non può essere vuota.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"La password non può contenere spazi.",
/* TR_PASSWORD_PROMPT */
"Password:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Il numero di telefono non può essere vuoto.",
/* TR_PREPARE_HARDDISK */
"Il programma di installazione preparerà ora l'hard disk su %s. Prima il disco sarà partizionato, e quindi sarà installato il filesystem nelle partizioni.",
/* TR_PRESS_OK_TO_REBOOT */
"Premere OK per riavviare.",
/* TR_PRIMARY_DNS */
"DNS primario:",
/* TR_PRIMARY_DNS_CR */
"DNS primario\n",
/* TR_PROBE */
"Rileva",
/* TR_PROBE_FAILED */
"Riconoscimento automatico fallito.",
/* TR_PROBING_SCSI */
"Ricerca dispositivi SCSI...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"Errore nell'impostazione della password di 'admin' per %s.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"Errore nell'impostazione della password di 'root'.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"Errore nell'impostazione della password di 'setup'.",
/* TR_PROTOCOL_COUNTRY */
"Protocollo/Paese",
/* TR_PULLING_NETWORK_UP */
"Avvio della rete...",
/* TR_PUSHING_NETWORK_DOWN */
"Arresto della rete...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Arresto reti non locali...",
/* TR_QUIT */
"Esci",
/* TR_RED_IN_USE */
"ISDN (o un'altra connessione) è attualmente in uso. Impossibile configurare l'ISDN mentre l'interfaccia ROSSA è attiva.",
/* TR_RESTART_REQUIRED */
"\n\nAl termine della configurazione sarà riavviata la rete.",
/* TR_RESTORE */
"Ripristina",
/* TR_RESTORE_CONFIGURATION */
"Se si dispone di un floppy con una configurazione di sistema del %s inserirlo nel lettore floppy e premere il pulsante di ripristino",
/* TR_ROOT_PASSWORD */
"Password per 'root'",
/* TR_SECONDARY_DNS */
"DNS secondario :",
/* TR_SECONDARY_DNS_CR */
"DNS secondario\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"DNS secondario specificato senza un DNS primario",
/* TR_SECTION_MENU */
"Menu",
/* TR_SELECT */
"Seleziona",
/* TR_SELECT_CDROM_TYPE */
"Selezionare il tipo di CDROM",
/* TR_SELECT_CDROM_TYPE_LONG */
"Nessun CDROM rilevato in questa macchina. Selezionare quale tra i seguenti driver si desidera usare per consentire a %s l'accesso al CDROM.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Selezionare il media d'installazione",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s può essere installato da diverse sorgenti. La più semplice è quella mediante il CDROM della macchina. Se il computer manca del CDROM, è possibile installare tramite un'altra macchina della rete che abbia i file di installazione disponibili via HTTP. In tale caso sarà richiesto il floppy con i driver di rete.",
/* TR_SELECT_NETWORK_DRIVER */
"Selezionare i driver di rete",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Selezionare i driver di rete per le schede installate in questo computer. Se si sceglie MANUALE, sarà possibile inserire il nome del modulo driver e i parametri per i driver che hanno particolari richieste, come le schede ISA.",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Selezionare l'interfaccia da riconfigurare.",
/* TR_SELECT_THE_ITEM */
"Selezionare l'elemento che si desidera modificare.",
/* TR_SETTING_ADMIN_PASSWORD */
"Impostazione password 'admin' per %s..",
/* TR_SETTING_ROOT_PASSWORD */
"Impostazione password 'root'..",
/* TR_SETTING_SETUP_PASSWORD */
"Impostazione password 'setup'..",
/* TR_SETUP_FINISHED */
"Installazione terminata. Premere OK per riavviare.",
/* TR_SETUP_NOT_COMPLETE */
"L'installazione iniziale non è stata terminata. Accertarsi che l'installazione sia completata correttamente eseguendo nuovamente il setup da shell.",
/* TR_SETUP_PASSWORD */
"Password per 'setup'",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Impostare i parametri opzionali per il modulo",
/* TR_SINGLE_GREEN */
"La configurazione è impostata per una sola interfaccia GREEN.",
/* TR_SKIP */
"Salta",
/* TR_START_ADDRESS */
"Indirizzo iniziale:",
/* TR_START_ADDRESS_CR */
"Indirizzo iniziale\n",
/* TR_STATIC */
"Statico",
/* TR_SUGGEST_IO */
"(suggerito %x)",
/* TR_SUGGEST_IRQ */
"(suggerito %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"Questo modulo del driver è già caricato.",
/* TR_TIMEZONE */
"Timezone",
/* TR_TIMEZONE_LONG */
"Scegliere la timezone in cui ci si trova dalla lista sottostante.",
/* TR_UNABLE_TO_EJECT_CDROM */
"Impossibile espellere il CDROM.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Impossibile estrarre i moduli.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Impossibile trovare altri driver.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Scheda ISDN non rilevata. E' necessario specificare i parametri opzionali se la scheda è di tipo ISA o richiede particolari impostazioni.",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"Impossibile inizializzare ISDN.",
/* TR_UNABLE_TO_INSTALL_FILES */
"Impossibile installare i files.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"Impossibile installare GRUB.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Impossibile caricare i moduli del driver.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Impossibile creare filesystem di boot.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Impossibile creare il filesystem di log.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Impossibile creare il filesystem di root.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Impossibile creare l'area di swap.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Impossibile creare symlink /dev/harddisk.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Impossibile creare symlink /dev/harddisk1.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Impossibile creare symlink /dev/harddisk2.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Impossibile creare symlink /dev/harddisk3.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Impossibile creare symlink /dev/harddisk4.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Impossibile creare symlink /dev/root.",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Impossibile fare il mount del filesystem di boot.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Impossibile fare il mount del filesystem di log.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Impossibile fare il mount del filesystem di proc.",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Impossibile fare il mount del filesystem di root.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Impossibile fare il mount la partizione di swap.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Impossibile aprire il file hosts principale.",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Impossibile aprire il file delle impostazioni",
/* TR_UNABLE_TO_PARTITION */
"Impossibile partizionare l'harddisk.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"Impossibile eliminare i file temporanei scaricati.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"Impossibile impostare l'hostname.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"Impossibile fare l'unmount del CDROM/floppydisk.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"Impossibile fare l'unmount dell'hard disk.",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"Impossibile scrivere su /etc/fstab",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"Impossibile scrivere su /etc/hostname",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"Impossibile scrivere su /etc/hosts.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"Impossibile scrivere su /etc/hosts.allow.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"Impossibile scrivere su /etc/hosts.deny.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"Impossibile scrivere %s/ethernet/settings.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"Impossibile scrivere su %s/main/hostname.conf",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"Impossibile scrivere %s/main/settings.",
/* TR_UNCLAIMED_DRIVER */
"E' presente una scheda di rete non assegnata di tipo:\n%s\n\nE' possibile assegnarla a:",
/* TR_UNKNOWN */
"SCONOSCIUTO",
/* TR_UNSET */
"NON DEFINITO",
/* TR_USB_KEY_VFAT_ERR */
"This USB key is invalid (no vfat partition found).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"ATTENZIONE",
/* TR_WARNING_LONG */
"Se si modifica questo indirizzo IP, e si è connessi da remoto, la connessione attuale alla macchina %s sarà perduta, e sarà necessario riconnettersi al nuovo IP. Questa è un'operazione pericolosa e dovrebbe essere svolta solo se si ha accesso fisico alla macchina nel caso qualcosa non andasse a buon fine.",
/* TR_WELCOME */
"Benvenuti nel programma di installazione di %s. Selezionando Annulla nelle prossime schermate verrà riavviato il sistema.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"L'attuale configurazione prevede una sola interfaccia di rete, e questa risulta già assegnata.",
}; 
  
