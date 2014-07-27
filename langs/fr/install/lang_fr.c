/*
 * French (fr) Data File
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

char *fr_tr[] = {

/* TR_ISDN */
"RNIS",
/* TR_ERROR_PROBING_ISDN */
"Impossible de scanner les périphériques RNIS.",
/* TR_PROBING_ISDN */
"Recherche et configuration des périphériques RNIS.",
/* TR_MISSING_GREEN_IP */
"Adresse IP de l'interface verte manquante !",
/* TR_CHOOSE_FILESYSTEM */
"Choisissez SVP votre système de fichiers :",
/* TR_NOT_ENOUGH_INTERFACES */
"Il n'y a pas assez de cartes réseau pour ce choix.\n\nRequise : %d - Disponible : %d\n",
/* TR_INTERFACE_CHANGE */
"Choisissez SVP l'interface que vous souhaitez modifier.\n\n",
/* TR_NETCARD_COLOR */
"Cartes assignées",
/* TR_REMOVE */
"Enlever",
/* TR_MISSING_DNS */
"DNS manquants.\n",
/* TR_MISSING_DEFAULT */
"Passerelle par défaut manquante.\n",
/* TR_JOURNAL_EXT3 */
"Création du journal pour Ext3...",
/* TR_CHOOSE_NETCARD */
"Choisissez SVP une carte réseau pour l'interface suivante - %s.",
/* TR_NETCARDMENU2 */
"Menu réseau étendu",
/* TR_ERROR_INTERFACES */
"Il n'y a aucune interface de libre sur votre système.",
/* TR_REMOVE_CARD */
"L'attribution de la carte réseau doit-elle être supprimée ? - %s",
/* TR_JOURNAL_ERROR */
"Impossible de céer le journal, utilisation de ext2 en remplacement.",
/* TR_FILESYSTEM */
"Choix du système de fichier",
/* TR_ADDRESS_SETTINGS */
"Paramètres d'adresse",
/* TR_ADMIN_PASSWORD */
"Mot de passe 'admin'",
/* TR_AGAIN_PROMPT */
"Encore:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Attribution de toutes les cartes avec succès.",
/* TR_AUTODETECT */
"* AUTO-DETECTION *",
/* TR_BUILDING_INITRD */
"Génération du ramdisk...",
/* TR_CANCEL */
"Annuler",
/* TR_CARD_ASSIGNMENT */
"Attribution de la carte",
/* TR_CHECKING */
"Vérification de l'URL...",
/* TR_CHECKING_FOR */
"Vérification pour : %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Choisissez la carte RNIS sur cet ordinateur.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Choisissez le procole RNIS requis.",
/* TR_CONFIGURE_DHCP */
"Configurez le serveur DHCP en saisissant les paramètres.",
/* TR_CONFIGURE_NETWORKING */
"Configuration du réseau",
/* TR_CONFIGURE_NETWORKING_LONG */
"Vous devriez maintenant configurer le réseau en commençant par choisir le pilote approprié pour l'interface verte. Vous pouvez essayer la détection automatique ou choisir vous-même le bon pilote. Notez que si vous avez plus d'une carte réseau installée, vous pourrez configurer les autres ultérieurement. Notez également que si vous avez plus d'une carte qui a le même type que la VERTE et que chacune requiert des paramètres de module spéciaux, vous devriez saisir les paramètres pour toutes les cartes de ce type maintenant de façon à ce que toutes cartes deviennent actives quand vous configurez l'interface verte.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Configurer les pilotes réseaux, et à quelle interface chaque carte est assignée.  La configuration actuelle est comme suit :\n\n",
/* TR_CONFIGURE_THE_CDROM */
"Configurez le CDROM en choisissant l'adresse IO et/ou IRQ appropriées.",
/* TR_CONGRATULATIONS */
"Félicitation!",
/* TR_CONGRATULATIONS_LONG */
"%s a été installé avec succès. Merci de retirer les CDROMs de l'ordinateur. L'installation va maintenant commencer la configuration pendant laquelle vous pourrez configurer RNIS, les cartes réseaux et les mots de passe du système. Après la fin de l'installation, vous pourrez vous rendre avec votre navigateur web à l'adresse https://%s:444 (ou quelque soit le nom %s que vous avez donné), afin de configurer le réseau commuté (si nécessaire) et l'accès distant.",
/* TR_CONTINUE_NO_SWAP */
"Votre disque dur est très petit, mais vous pouvez continuer avec une petite partition d'échange. (Utiliser avec précaution).",
/* TR_CURRENT_CONFIG */
"Configuration actuelle : %s%s",
/* TR_DEFAULT_GATEWAY */
"Passerelle par défaut :",
/* TR_DEFAULT_GATEWAY_CR */
"Passerelle par défaut\n",
/* TR_DEFAULT_LEASE */
"Bail par défaut (mins):",
/* TR_DEFAULT_LEASE_CR */
"Bail par défaut\n",
/* TR_DETECTED */
"Détecté: %s",
/* TR_DHCP_HOSTNAME */
"Hôte DHCP :",
/* TR_DHCP_HOSTNAME_CR */
"Hôte DHCP\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"Configuration du serveur DHCP",
/* TR_DISABLED */
"Désactivé",
/* TR_DISABLE_ISDN */
"Désactiver RNIS",
/* TR_DISK_TOO_SMALL */
"Votre disque dur est trop petit.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"Paramètres DNS et de la passerelle",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Saisissez les DNS et les informations de la passerelle.  Ces paramètres ne sont utilisés qu'avec une IP statique (et DHCP si les DNS sont saisis) sur l'interface rouge (RED).",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Votre configuration n'utilise pas d'adaptateur ethernet pour l'interface rouge.  DNS et les informations de la passerelle pour les utilisateur de réseau commuté est configuré automatiquement au moment de la connexion.",
/* TR_DOMAINNAME */
"Nom de domaine",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Le nom de domaine ne peut être vide.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"Le nom de domaine ne peut pas contenir d'espaces.",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Le nom de domaine ne peut contenir que des lettres, chiffres, -, et des points.",
/* TR_DOMAIN_NAME_SUFFIX */
"Suffixe du nom de domaine :",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Suffixe du nom de domaine\n",
/* TR_DONE */
"Terminé",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\nVoulez-vous changer ces paramètres ?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Attribution des pilotes et des cartes",
/* TR_ENABLED */
"Activé",
/* TR_ENABLE_ISDN */
"Activer RNIS",
/* TR_END_ADDRESS */
"Adresse de fin :",
/* TR_END_ADDRESS_CR */
"Adresse de fin\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Certaines cartes RNIS (particulièrement les ISA) peut nécessiter des paramètres supplémentaires pour configurer les adresses IRQ et IO. Si vous avez une telle carte, saisissez ces paramètres ici. Par exemple : \"io=0x280 irq=9\". Ils seront utilisés pendant la détection des cartes.",
/* TR_ENTER_ADMIN_PASSWORD */
"Saisissez le mot de passe pour l'administrateur 'admin' d'%s.  C'est l'utilisateur à utiliser pour l'interface d'administration web %s.",
/* TR_ENTER_DOMAINNAME */
"Entrez un nom de domaine",
/* TR_ENTER_HOSTNAME */
"Entrez le nom d'hôte de la machine.",
/* TR_ENTER_IP_ADDRESS_INFO */
"Entez l'adresse IP",
/* TR_ENTER_NETWORK_DRIVER */
"La détection automatique de la carte réseau a échoué. Entrez les pilotes et paramètres optionnels pour la carte réseau.",
/* TR_ENTER_ROOT_PASSWORD */
"Entrez le mot de passe 'root'. Il est utilisé pour l'accès en ligne de commande.",
/* TR_ENTER_SETUP_PASSWORD */
"A ENLEVER",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Entrez les informations IP pour l'interface %s.",
/* TR_ENTER_THE_LOCAL_MSN */
"Entrez le numéro de téléphone local (MSN/EAZ).",
/* TR_ENTER_URL */
"Entrez l'URL vers ipcop-<version>.tgz et les fichiers images/scsidrv-<version>.img. ATTENTION : DNS non disponibles ! Ca devrait être quelque chose comme http://X.X.X.X/<dossier>",
/* TR_ERROR */
"Erreur",
/* TR_ERROR_PROBING_CDROM */
"Aucun lecteur CDROM trouvé.",
/* TR_ERROR_WRITING_CONFIG */
"Erreur lors de l'écriture des informations de configuration.",
/* TR_EURO_EDSS1 */
"Euro (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Extraction des modules...",
/* TR_FAILED_TO_FIND */
"Impossible de  trouver le fichier URL.",
/* TR_FOUND_NIC */
"%s a détecté la carte réseau suivante sur votre machine : %s",
/* TR_GERMAN_1TR6 */
"German 1TR6",
/* TR_HELPLINE */
"              <Tab>/<Alt-Tab> changer d'élément   |  <Espace> sélectionner",
/* TR_HOSTNAME */
"Nom d'hôte",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Le nom d'hôte ne peut être vide.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"Le nom d'hôte ne peut contenir d'espaces.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"Le nom d'hôte ne peut contenir que des lettres, chiffres et traits d'union.",
/* TR_INITIALISING_ISDN */
"Initialisation RNIS...",
/* TR_INSERT_CDROM */
"Insérez le CD %s dans le lecteur de CDROM.",
/* TR_INSERT_FLOPPY */
"Insérez la disquette du driver %s dans le lecteur de disquette.",
/* TR_INSTALLATION_CANCELED */
"Installation annulée.",
/* TR_INSTALLING_FILES */
"Installation des fichiers...",
/* TR_INSTALLING_GRUB */
"Installation de GRUB...",
/* TR_INSTALLING_LANG_CACHE */
"Installation des fichiers de langues...",
/* TR_INTERFACE */
"Interface - %s",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"L'interface n'a pas pu être activée.",
/* TR_INVALID_FIELDS */
"Les champs suivants sont invalides :\n\n",
/* TR_INVALID_IO */
"Les détails du port d'IO sont invalides. ",
/* TR_INVALID_IRQ */
"Les détails IRQ sont invalides.",
/* TR_IP_ADDRESS_CR */
"Adresse IP\n",
/* TR_IP_ADDRESS_PROMPT */
"Adresse IP :",
/* TR_ISDN_CARD */
"Carte RNIS",
/* TR_ISDN_CARD_NOT_DETECTED */
"Carte RNIS non détectée. Vous devez peut-être spécifier des paramètres additionnels si la carte est de type ISA ou si elle a des spécifications particulières.",
/* TR_ISDN_CARD_SELECTION */
"Sélection de la carte RNIS",
/* TR_ISDN_CONFIGURATION */
"Configuration RNIS",
/* TR_ISDN_CONFIGURATION_MENU */
"Menu de configuration RNIS",
/* TR_ISDN_NOT_SETUP */
"RNIS non installé. Certains paramètres n'ont pas été sélectionnés.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"RNIS n'a pas encore été configuré. Sélectionnez le paramètre que vous souhaitez configurer.",
/* TR_ISDN_PROTOCOL_SELECTION */
"Sélection du protocole RNIS",
/* TR_ISDN_STATUS */
"RNIS est actuellement %s.\n\n   Protocole : %s\n   Carte : %s\n   Numéro de téléphone local : %s\n\nSélectionnez le paramètre que vous voulez reconfigurer, ou utilisez les paramètres actuels.",
/* TR_KEYBOARD_MAPPING */
"Organisation du clavier",
/* TR_KEYBOARD_MAPPING_LONG */
"Choisissez le type de clavier que vous utilisez dans la liste ci-dessous.",
/* TR_LEASED_LINE */
"Leased line (ligne dédiée)",
/* TR_LOADING_MODULE */
"Chargement du module...",
/* TR_LOADING_PCMCIA */
"Chargement du module PCMCIA...",
/* TR_LOOKING_FOR_NIC */
"Recherche de: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Génération du système de fichier de démarrage...",
/* TR_MAKING_LOG_FILESYSTEM */
"Génération du système de fichier de log...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Génération du système de fichier de root...",
/* TR_MAKING_SWAPSPACE */
"Génération de la partition swap...",
/* TR_MANUAL */
"* MANUEL *",
/* TR_MAX_LEASE */
"Bail Max (mins):",
/* TR_MAX_LEASE_CR */
"Bail Max\n",
/* TR_MISSING_BLUE_IP */
"Paramètres IP manquants sur l'interface BLEUE.",
/* TR_MISSING_ORANGE_IP */
"Paramètres IP manquants sur l'interface ORANGE.",
/* TR_MISSING_RED_IP */
"Paramètres IP manquants sur l'interface ROUGE.",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"Le nom du module ne peut être vide.",
/* TR_MODULE_PARAMETERS */
"Entrer les paramètres et le nom du module pour le pilote requis.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Montage du système de fichier de boot...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Montage du système de fichier de log...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Montage du système de fichier de root...",
/* TR_MOUNTING_SWAP_PARTITION */
"Montage de la partition swap...",
/* TR_MSN_CONFIGURATION */
"Numéro de téléphone local (MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Masque réseau :",
/* TR_NETWORKING */
"Réseau",
/* TR_NETWORK_ADDRESS_CR */
"Adresse réseau\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Adresse réseau :",
/* TR_NETWORK_CONFIGURATION_MENU */
"Menu de configuration du réseau",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Type de configuration réseau",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Sélectionnez la configuration réseau pour %s.  Les types de configuration suivants listent les interfaces ethernet. Si vous changez ce paramètre, un redémarrage du réseau est requis, et vous devrez reconfigurer les attributions des pilotes.",
/* TR_NETWORK_MASK_CR */
"Masque réseau\n",
/* TR_NETWORK_SETUP_FAILED */
"Installation du réseau échouée.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"Trop peu de cartes ont été attribuée.",
/* TR_NO_BLUE_INTERFACE */
"Interface BLEUE non attribuée.",
/* TR_NO_CDROM */
"Aucun CD-ROM trouvé.",
/* TR_NO_GREEN_INTERFACE */
"Interface VERTE non attribuée.",
/* TR_NO_HARDDISK */
"Aucun disque dur trouvé.",
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
"Aucun tarball ipcop trouvé sur le serveur Web.",
/* TR_NO_ORANGE_INTERFACE */
"Interface ORANGE non attribuée.",
/* TR_NO_RED_INTERFACE */
"Interface ROUGE non attribuée.",
/* TR_NO_SCSI_IMAGE_FOUND */
"Aucune image SCSI trouvée sur le serveur Web.",
/* TR_NO_UNALLOCATED_CARDS */
"Aucune carte non attribuée restante, il en faut plus. Vous pouvez auto-détecter et rechercher plus de cartes ou choisissez un pilote dans la liste.",
/* TR_OK */
"Ok",
/* TR_PARTITIONING_DISK */
"Partitionnement du disque...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"Les mots de passe ne correspondent pas.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"Le mot de passe ne peut être vide.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"Le mot de  passe ne peut contenir d'espaces.",
/* TR_PASSWORD_PROMPT */
"Mot de passe :",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Le numéro de téléphone ne peut être vide.",
/* TR_PREPARE_HARDDISK */
"Le programme d'installation va maintenant préparer le disque %s. Il sera d'abord partitionné, puis les systèmes de fichiers seront installés.",
/* TR_PRESS_OK_TO_REBOOT */
"Appuyer sur Ok pour redémarrer.",
/* TR_PRIMARY_DNS */
"DNS primaire :",
/* TR_PRIMARY_DNS_CR */
"DNS primaire\n",
/* TR_PROBE */
"Auto-détection",
/* TR_PROBE_FAILED */
"Auto-détection échouée.",
/* TR_PROBING_HARDWARE */
"Détection du matériel...",
/* TR_PROBING_FOR_NICS */
"Détection des cartes réseaux...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"Problème lors de la configuration du mot de passe 'admin' %s.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"Problème lors de la configuration du mot de passe 'root'.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"A ENLEVER",
/* TR_PROTOCOL_COUNTRY */
"Protocole/Pays",
/* TR_PULLING_NETWORK_UP */
"Démarrage du réseau...",
/* TR_PUSHING_NETWORK_DOWN */
"Arrêt du réseau...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Arrêt du réseau distant...",
/* TR_QUIT */
"Quitter",
/* TR_RED_IN_USE */
"RNIS (ou une autre connexion externe) est actuellement utilisée.  Vous ne pouvez pas configurer RNIS pendant que l'interface ROUGE est utilisée.",
/* TR_RESTART_REQUIRED */
"\n\nLorsque la configuration sera terminée, un redémarrage du réseau sera requis.",
/* TR_RESTORE */
"Restaurer",
/* TR_RESTORE_CONFIGURATION */
"Si vous avez une disquette avec une configuration système %s, insérez la disquette dans le lecteur et appuyer sur restaurer.",
/* TR_ROOT_PASSWORD */
"Mot de passe 'root'",
/* TR_SECONDARY_DNS */
"DNS secondaire :",
/* TR_SECONDARY_DNS_CR */
"DNS secondaire\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"DNS secondaire spécifié sans un DNS primaire",
/* TR_SECTION_MENU */
"Menu de sélection",
/* TR_SELECT */
"Sélectionner",
/* TR_SELECT_CDROM_TYPE */
"Sélectionner le type de CDROM",
/* TR_SELECT_CDROM_TYPE_LONG */
"Aucun CD-ROM détecté sur la machine.  Sélectionnez lequel des pilotes suivants vous voulez utiliser afin que %s accède au CD-ROM.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Sélectionner le média d'installation",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s peut être installé depuis de multiples sources.  La manière la plus simple est d'utiliser une machine avec un CD-ROM. S'il n'y a aucun lecteur, vous pouvez installer via une autre machine du réseau qui possède les fichiers d'installation disponibles par FTP ou HTTP.",
/* TR_SELECT_NETWORK_DRIVER */
"Sélectionner un pilote réseau",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Sélectionner le pilote réseau pour la carte installée sur la machine. Si vous sélectionner MANUEL, vous pourrez saisir le nom du pilote ainsi que les paramètres pour les pilotes qui sont spécifiques comme les cartes ISA.",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Sélectionnez l'interface que vous voulez reconfigurer.",
/* TR_SELECT_THE_ITEM */
"Sélectionner l'élément que vous voulez configurer.",
/* TR_SETTING_ADMIN_PASSWORD */
"Paramétrage le mot de passe 'admin' de %s...",
/* TR_SETTING_ROOT_PASSWORD */
"Paramétrage du mot de passe 'root'....",
/* TR_SETTING_SETUP_PASSWORD */
"A ENLEVER",
/* TR_SETUP_FINISHED */
"Installation terminée.",
/* TR_SETUP_NOT_COMPLETE */
"L'installation initiale n'est pas complètement finie.  Vous devez vous assurer que l'installation s'est finie correctement en relançant l'installation depuis le shell.",
/* TR_SETUP_PASSWORD */
"A ENLEVER",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Choisissez les paramètres additionnels du module",
/* TR_SINGLE_GREEN */
"Votre configuration est définie pour une unique interface VERTE.",
/* TR_SKIP */
"Passer",
/* TR_START_ADDRESS */
"Adresse de début :",
/* TR_START_ADDRESS_CR */
"Adresse de début\n",
/* TR_STATIC */
"Statique",
/* TR_SUGGEST_IO */
"(suggère %x)",
/* TR_SUGGEST_IRQ */
"(suggère %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"Ce pilote est déjà chargé.",
/* TR_TIMEZONE */
"Fuseau horaire",
/* TR_TIMEZONE_LONG */
"Choisissez votre fuseau horaire dans la liste ci-dessous.",
/* TR_UNABLE_TO_EJECT_CDROM */
"Impossible d'éjecter le CD-ROM.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Impossible d'extraire les modules.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Impossible de trouver des pilotes supplémentaires.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Impossible de trouver une carte RNIS sur cet ordinateur. Vous devrez peut-être spécifier des paramètres additionnels si la carte est de type ISA ou si elle a des spécificités.",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"Impossible d'initialiser RNIS.",
/* TR_UNABLE_TO_INSTALL_FILES */
"Impossible d'installer les fichiers.",
/* TR_UNABLE_TO_INSTALL_LANG_CACHE */
"Impossible d'installer les fichiers de langues.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"Impossible d'installer GRUB.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Impossible de charger le pilote.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Impossible de générer le système de fichiers boot.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Impossible de générer le système de fichiers log.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Impossible de générer le système de fichiers root.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Impossible de générer la partition swap.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Impossible de créer le symlink /dev/harddisk.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Impossible de créer le simlink /dev/harddisk1.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Impossible de créer le symlink /dev/harddisk2.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Impossible de créer le symlink /dev/harddisk3.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Impossible de créer le symlink /dev/harddisk4.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Impossible de créer le symlink /dev/root.",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Impossible de monter le système de fichier boot.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Impossible de monter le système de fichier log.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Impossible de monter le système de fichier proc.",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Impossible de monter le système de fichier root.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Impossible de monter la partition swap.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Impossible d'ouvrir le fichier hosts principal.",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Impossible d'ouvrir le fichier settings",
/* TR_UNABLE_TO_PARTITION */
"Impossible de partitionner le disque.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"Impossible de supprimer les fichiers téléchargés temporaires.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"Impossible de définir le nom d'hôte.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"Impossible de démonter le CDROM/disquette.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"Impossible de démonter le disque dur.",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"Impossible d'écrire /etc/fstab",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"Impossible d'écrire /etc/hostname",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"Impossible d'écrire /etc/hosts.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"Impossible d'écrire /etc/hosts.allow.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"Impossible d'écrire /etc/hosts.deny.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"Impossible d'écrire %s/ethernet/settings.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"Impossible d'écrire %s/main/hostname.conf",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"Impossible d'écrire %s/main/settings.",
/* TR_UNCLAIMED_DRIVER */
"Il y a une carte ethernet non assignée de type :\n%s\n\nVous pouvez l'assigner à :",
/* TR_UNKNOWN */
"INCONNU",
/* TR_UNSET */
"NON DEFINIE",
/* TR_USB_KEY_VFAT_ERR */
"La clé USB est invalide (aucune partition vfat).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"ATTENTION",
/* TR_WARNING_LONG */
"Si vous changez cette adresse IP et que vous êtes connecté à distance, la connexion à la machine %s sera interrompue et vous aurez à vous reconnecter avec la nouvelle IP. C'est une opération risquée et ne devrait pas être tentée si vous n'avez pas d'accès physique à la machine dans le cas où quelque chose se passe mal.",
/* TR_WELCOME */
"Bienvenue dans le programme d'installation d'%s. Si vous sélectionnez Annuler sur n'importe lequel des écrans suivants, ceci redémarrera l'ordinateur.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Votre configuration est définie pour une interface VERTE unique, qui a déjà un pilote assigné.",
/* TR_YES */
"Oui",
/* TR_NO */
"Non",
/* TR_AS */
"comme",
/* TR_IGNORE */
"Ignorer",
/* TR_PPP_DIALUP */
"PPP DIALUP (PPPoE, Modem, ATM ...)",
/* TR_DHCP */
"DHCP",
/* TR_DHCP_STARTSERVER */
"Démarrage du serveur DHCP ...",
/* TR_DHCP_STOPSERVER */
"Arrêt du serveur DHCP ...",
/* TR_LICENSE_ACCEPT */
"J'accepte les termes de cette licence.",
/* TR_LICENSE_NOT_ACCEPTED */
"Je n'accepte pas les termes de cette licence, quitter le programme d'installation.",
/* TR_EXT4FS */
"EXT4 - Filesystem",
/* TR_EXT4FS_WO_JOURNAL */
"EXT4 - Filesystem without journal",
/* TR_XFS */
"XFS - Filesystem",
/* TR_REISERFS */
"ReiserFS - Filesystem",
/* TR_NO_LOCAL_SOURCE */
"Pas de source locale trouvée. Démarrage du téléchargement.",
/* TR_DOWNLOADING_ISO */
"Téléchargement du fichier image ISO ...",
/* TR_DOWNLOAD_ERROR */
"Erreur pendant le téléchargement!",
/* TR_DHCP_FORCE_MTU */
"Force DHCP mtu:",
/* TR_IDENTIFY */
"Identify",
/* TR_IDENTIFY_SHOULD_BLINK */
"Selected port should blink now ...",
/* TR_IDENTIFY_NOT_SUPPORTED */
"Function is not supported by this port.",
};
