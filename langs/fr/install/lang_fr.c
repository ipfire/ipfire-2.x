/*
 * French (fr) Data File
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
 * (c) 2003 Bertrand Sarthre, Michel Janssens, Erwann Simon, Patrick Bernaud,
 * Marc Faid'herbe, Eric Legigan, Eric Berthomier, Stèphane Le Bourdon,
 * Stèphane Thirion, Jan M. Dziewulski, spoutnik, Eric Darriak, Eric Boniface,
 * Franck Bourdonnec 
 */
 
#include "libsmooth.h"

char *fr_tr[] = {

/* TR_ADDRESS_SETTINGS */
"Configuration de l'adresse",
/* TR_ADMIN_PASSWORD */
"Mot de passe 'Admin'",
/* TR_AGAIN_PROMPT */
"Vérification:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Toutes les cartes ont été attribuées.",
/* TR_AUTODETECT */
"* AUTODETECT *",
/* TR_BUILDING_INITRD */
"INITRD en préparation...",
/* TR_CANCEL */
"Annuler",
/* TR_CARD_ASSIGNMENT */
"Affectation des cartes",
/* TR_CHECKING */
"Vérification de l'URL...",
/* TR_CHECKING_FOR */
"Vérification: %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Choisissez la carte RNIS (ISDN) installée dans cet ordinateur.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Choisissez le protocole RNIS (ISDN) dont vous avez besoin.",
/* TR_CONFIGURE_DHCP */
"Configurez le serveur DHCP en entrant les paramètres de configuration.",
/* TR_CONFIGURE_NETWORKING */
"Configuration du réseau",
/* TR_CONFIGURE_NETWORKING_LONG */
"Vous devez maintenant configurer le réseau en choisissant dans un premier temps le pilote correct pour l'interface VERTE. Vous pouvez demander à ce qu'elle soit détectée automatiquement, ou choisir le pilote correct dans une liste. Notez que si vous avez plus d'une carte réseau installée, vous pourrez configurer les autres plus tard durant l'installation. Notez également que si vous possédez plusieurs cartes du même type que l'interface VERTE et que chaque carte nécessite des paramètres particuliers, vous devez entrer les paramètres pour toutes les cartes du même type afin que toutes les cartes puissent devenir actives quand vous configurez l'interface VERTE.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Configurez les pilotes réseau, et l'interface à laquelle chaque carte est affectée.  La configuration actuelle est la suivante:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"Configurez le CD-ROM en choisissant l'adresse IO et/ou l'IRQ approprié(s).",
/* TR_CONGRATULATIONS */
"Félicitations!",
/* TR_CONGRATULATIONS_LONG */
"%s a été installé avec succès. Veuillez retirer toute disquette ou CD-ROM de l'ordinateur. L'utilitaire de configuration va maintenant s'exécuter et vous permettre de configurer les cartes réseaux, le RNIS et les mots de passe système. Une fois la configuration terminée, vous pourrez utiliser votre navigateur sur http://%s:81 ou https://%s:445 (ou tout autre nom que vous aurez donné à votre IPCop), et configurer la connexion via modem (si requise) et l'accès externe. Pensez à donner un mot de passe à l'utilisateur 'dial' %s, si vous voulez que des utilisateurs non 'admin' de %s puissent contrôler la connexion.",
/* TR_CONTINUE_NO_SWAP */
"La taille de votre disque dur est inférieure à celle qui est nécessaire; il vous est possible de continuer sans utilisation de mémoire paginée. (A utiliser avec précaution).",
/* TR_CURRENT_CONFIG */
"Configuration actuelle: %s%s",
/* TR_DEFAULT_GATEWAY */
"Passerelle par défaut:",
/* TR_DEFAULT_GATEWAY_CR */
"Passerelle par défaut\n",
/* TR_DEFAULT_LEASE */
"Bail par défaut (min):",
/* TR_DEFAULT_LEASE_CR */
"Durée par défaut du bail\n",
/* TR_DETECTED */
"Carte détectée: %s",
/* TR_DHCP_HOSTNAME */
"Nom d'hôte DHCP:",
/* TR_DHCP_HOSTNAME_CR */
"Nom d'hôte DHCP\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"Configuration du serveur DHCP ",
/* TR_DISABLED */
"Désactivé",
/* TR_DISABLE_ISDN */
"Désactiver RNIS (ISDN)",
/* TR_DISK_TOO_SMALL */
"La capacité de votre disque dur est insuffisante.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"Configuration du DNS et de la Passerelle",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Entrez les informations de DNS et de Passerelle. Ces paramètres ne sont utiles que si DHCP est désactivé pour l'interface ROUGE.",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Votre configuration n'utilise pas d'adaptateur ethernet pour son interface ROUGE. Les informations de DNS et de Passerelle seront définies automatiquement au moment de la connexion.",
/* TR_DOMAINNAME */
"Nom de domaine",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Le nom de domaine ne peut être vide.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"Le nom de domaine ne peut contenir des espaces",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Le nom de domaine ne peut contenir que des lettres, des chiffres ou les signes - et .",
/* TR_DOMAIN_NAME_SUFFIX */
"Suffixe de nom de domaine:",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Suffixe de nom de domaine\n",
/* TR_DONE */
"Continuer",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\nSouhaitez-vous modifier ces paramètres ?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Affectation des pilotes et des cartes",
/* TR_ENABLED */
"Activé",
/* TR_ENABLE_ISDN */
"Activer RNIS (ISDN)",
/* TR_END_ADDRESS */
"Adresse de fin:",
/* TR_END_ADDRESS_CR */
"Adresse de fin\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Certaines cartes RNIS (particulièrement les ISA) peuvent nécessiter des paramètres additionnels du module pour configurer l'IRQ et l'adresse IO. Si vous possédez une telle carte, entrez ces paramètres. Par exemple: \"io=0x280 irq=9\". Ils seront utilisés pour la détection de la carte.",
/* TR_ENTER_ADMIN_PASSWORD */
"Entrez le mot de passe de l'utilisateur 'admin' de %s. C'est l'utilisateur permettant d'accéder aux pages web d'administration de %s.",
/* TR_ENTER_DOMAINNAME */
"Entrez le nom de domaine",
/* TR_ENTER_HOSTNAME */
"Entrez le nom d'hôte de la machine.",
/* TR_ENTER_IP_ADDRESS_INFO */
"Saisissez les informations sur l'adresse IP",
/* TR_ENTER_NETWORK_DRIVER */
"La détection automatique de la carte réseau a échoué. Entrez le pilote et les paramètres optionnels de la carte réseau.",
/* TR_ENTER_ROOT_PASSWORD */
"Entrez le mot de passe de l'utilisateur 'root'. Utilisez ce login pour un accès en ligne de commande.",
/* TR_ENTER_SETUP_PASSWORD */
"Entrez le mot de passe de l'utilisateur 'setup'. Utilisez ce login pour un accès à  l'utilitaire de configuration.",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Entrez les informations sur l'adresse IP pour l'interface %s.",
/* TR_ENTER_THE_LOCAL_MSN */
"Entrez le numéro de téléphone local (MSN/EAZ).",
/* TR_ENTER_URL */
"Entrez l'URL des fichiers ipcop-<version>.tgz et images/scsidrv-<version>.img. ATTENTION : le DNS n'est pas actif ! L'URL doit être de la forme 'http://X.X.X.X/<directory>'",
/* TR_ERROR */
"Erreur",
/* TR_ERROR_WRITING_CONFIG */
"Erreur d'écriture du fichier de configuration.",
/* TR_EURO_EDSS1 */
"Euro (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Extraction des modules...",
/* TR_FAILED_TO_FIND */
"Echec dans la recherche de l'URL.",
/* TR_FOUND_NIC */
"%s a détecté la carte suivante sur votre machine: %s",
/* TR_GERMAN_1TR6 */
"German 1TR6",
/* TR_HELPLINE */
"         <Tab>/<Alt-Tab> entre les éléments  |  <Espace> sélectionner",
/* TR_HOSTNAME */
"Nom d'hôte",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Un nom d'hôte doit être défini.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"Un nom d'hôte ne peut contenir d'espaces.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"Un nom d'hôte ne peut être composé que de lettres, de chiffres et de tirets.",
/* TR_INITIALISING_ISDN */
"Initialisation du RNIS (ISDN)...",
/* TR_INSERT_CDROM */
"Veuillez insérer le CD %s dans le lecteur de CD-ROM.",
/* TR_INSERT_FLOPPY */
"Veuillez insérer la disquette de pilotes %s dans le lecteur de disquette.",
/* TR_INSTALLATION_CANCELED */
"Installation annulée.",
/* TR_INSTALLING_FILES */
"Installation des fichiers...",
/* TR_INSTALLING_GRUB */
"Installation de GRUB...",
/* TR_INTERFACE */
"interface %s",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"L'activation de l'interface a échoué.",
/* TR_INVALID_FIELDS */
"Les champs suivants sont invalides:\n\n",
/* TR_INVALID_IO */
"L'adresse I/O saisie est invalide. ",
/* TR_INVALID_IRQ */
"L'IRQ saisie est invalide.",
/* TR_IP_ADDRESS_CR */
"Adresse IP\n",
/* TR_IP_ADDRESS_PROMPT */
"Adresse IP:",
/* TR_ISDN_CARD */
"Carte RNIS (ISDN)",
/* TR_ISDN_CARD_NOT_DETECTED */
"Aucune carte RNIS n'a été détectée. Vous devez préciser des paramètres additionnels du module s'il s'agit d'une carte ISA ou si elle nécessite des paramètres particuliers.",
/* TR_ISDN_CARD_SELECTION */
"Sélection de la carte RNIS (ISDN)",
/* TR_ISDN_CONFIGURATION */
"Configuration RNIS (ISDN)",
/* TR_ISDN_CONFIGURATION_MENU */
"Menu de configuration RNIS (ISDN)",
/* TR_ISDN_NOT_SETUP */
"Le RNIS (ISDN) n'est pas configuré. Certains éléments n'ont pas été sélectionnés.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"Le RNIS (ISDN) n'a pas été configuré. Choisissez l'élément que vous souhaitez configurer.",
/* TR_ISDN_PROTOCOL_SELECTION */
"Sélection du protocole RNIS (ISDN)",
/* TR_ISDN_STATUS */
"RNIS est actuellement: %s.\n\n   Protocole: %s\n   Carte: %s\n   Numéro de téléphone local : %s\n\nChoisissez l'élément que vous souhaitez reconfigurer, ou choisissez d'utiliser les paramètres actuels.",
/* TR_KEYBOARD_MAPPING */
"Configuration du clavier",
/* TR_KEYBOARD_MAPPING_LONG */
"Choisissez dans la liste ci-dessous le type de clavier que vous utilisez.",
/* TR_LEASED_LINE */
"Ligne louée",
/* TR_LOADING_MODULE */
"Chargement du module...",
/* TR_LOADING_PCMCIA */
"Chargement des modules PCMCIA ...",
/* TR_LOOKING_FOR_NIC */
"Recherche: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Création du système de fichiers boot...",
/* TR_MAKING_LOG_FILESYSTEM */
"Création du système de fichiers log...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Mise en place du système de fichiers racine...",
/* TR_MAKING_SWAPSPACE */
"Mise en place de l'espace de swap...",
/* TR_MANUAL */
"* MANUEL *",
/* TR_MAX_LEASE */
"Bail maximum (min):",
/* TR_MAX_LEASE_CR */
"Durée maximale du bail\n",
/* TR_MISSING_BLUE_IP */
"Informations d'adressage IP manquantes pour l'interface BLEUE",
/* TR_MISSING_ORANGE_IP */
"Informations d'adressage IP manquantes pour l'interface ORANGE",
/* TR_MISSING_RED_IP */
"Informations d'adressage IP manquantes pour l'interface ROUGE",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"Un nom de module doit être spécifié.",
/* TR_MODULE_PARAMETERS */
"Entrez le nom du module et les paramètres requis par le pilote.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Montage du système de fichiers boot...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Montage du système de fichiers log...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Montage du système de fichiers racine...",
/* TR_MOUNTING_SWAP_PARTITION */
"Montage de la partition de swap...",
/* TR_MSN_CONFIGURATION */
"Numéro de téléphone local (MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Masque du réseau:",
/* TR_NETWORKING */
"Réseau",
/* TR_NETWORK_ADDRESS_CR */
"Adresse du réseau\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Adresse du réseau:",
/* TR_NETWORK_CONFIGURATION_MENU */
"Menu de configuration réseau",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Type de configuration réseau",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Choisissez la configuration réseau pour %s.  Les types de configuration suivants listent les interfaces attachées à un périphérique ethernet. Si vous modifiez cette configuration, le réseau devra être redémarré, et vous devrez redéfinir l'affectation des pilotes et des cartes.",
/* TR_NETWORK_MASK_CR */
"Masque du réseau\n",
/* TR_NETWORK_SETUP_FAILED */
"Echec de la configuration réseau.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"Pas assez de cartes affectées.",
/* TR_NO_BLUE_INTERFACE */
"Aucune interface BLEUE n'est définie.",
/* TR_NO_CDROM */
"Aucun CD-ROM détecté",
/* TR_NO_HARDDISK */
"Aucun disque dur détecté.",
/* TR_NO_IPCOP_TARBALL_FOUND */
"Archive ipcop non trouvée sur le serveur Web",
/* TR_NO_ORANGE_INTERFACE */
"Aucune interface ORANGE n'est définie.",
/* TR_NO_RED_INTERFACE */
"Aucune interface ROUGE n'est définie.",
/* TR_NO_SCSI_IMAGE_FOUND */
"Image SCSI non trouvée sur le serveur Web",
/* TR_NO_UNALLOCATED_CARDS */
"Il ne reste aucune carte non attribuée or d'autres sont requises. Vous pouvez effectuer une recherche automatique, ou choisir un pilote dans la liste suivante.",
/* TR_OK */
"Ok",
/* TR_PARTITIONING_DISK */
"Partitionnement du disque...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"Les mots de passe ne correspondent pas.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"Vous devez définir un mot de passe.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"Le mot de passe ne peut contenir des espaces.",
/* TR_PASSWORD_PROMPT */
"Mot de passe:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Un numéro de téléphone doit être entré.",
/* TR_PREPARE_HARDDISK */
"Le programme d'installation va maintenant préparer le disque dur principal (%s). En premier lieu, le disque sera partitionné, puis un système de fichiers sera installé sur chacune des partitions.",
/* TR_PRESS_OK_TO_REBOOT */
"Presser Ok pour redémarrer.",
/* TR_PRIMARY_DNS */
"DNS Primaire:",
/* TR_PRIMARY_DNS_CR */
"DNS Primaire\n",
/* TR_PROBE */
"Rechercher",
/* TR_PROBE_FAILED */
"L'auto détection a échoué.",
/* TR_PROBING_SCSI */
"Détection des périphériques SCSI ...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"Problème lors de la définition du mot de passe 'admin' de %s.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"Problème lors de la définition du mot de passe 'root'.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"Problème lors de la définition du mot de passe 'setup'.",
/* TR_PROTOCOL_COUNTRY */
"Protocole/Pays",
/* TR_PULLING_NETWORK_UP */
"Lancement du réseau...",
/* TR_PUSHING_NETWORK_DOWN */
"Arrêt du réseau...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Arrêt du réseau non local...",
/* TR_QUIT */
"Quitter",
/* TR_RED_IN_USE */
"RNIS (ou une autre connexion externe) est actuellement utilisée. Vous ne pouvez pas configurer RNIS (ISDN) si l'interface ROUGE est active.",
/* TR_RESTART_REQUIRED */
"\n\nQuand la configuration est terminée, le réseau doit être redémarré.",
/* TR_RESTORE */
"Restaurer",
/* TR_RESTORE_CONFIGURATION */
"Si vous possédez une disquette de configuration système de %s, placez-la dans le lecteur et appuyez sur le bouton Restaurer.",
/* TR_ROOT_PASSWORD */
"Mot de passe 'root'",
/* TR_SECONDARY_DNS */
"DNS Secondaire:",
/* TR_SECONDARY_DNS_CR */
"DNS Secondaire\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"Un DNS Secondaire est spécifié mais aucun DNS Primaire",
/* TR_SECTION_MENU */
"Menu Section ",
/* TR_SELECT */
"Sélectionner",
/* TR_SELECT_CDROM_TYPE */
"Sélectionner le type de CD-ROM",
/* TR_SELECT_CDROM_TYPE_LONG */
"Aucun CD-ROM n'a été trouvé sur votre machine. Veuillez sélectionner le pilote que vous désirez utiliser pour que %s puisse accéder au CD-ROM.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Sélectionner le support pour l'installation",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s peut être installé depuis de multiples sources, le plus simple étant d'utiliser le CD-ROM fourni. Si l'ordinateur ne possède pas de lecteur de CD-ROM, vous devrez installer via une autre machine mettant à disposition les fichiers d'installation par HTTP. Dans ce cas, la disquette de pilotes réseaux sera requise.",
/* TR_SELECT_NETWORK_DRIVER */
"Choisissez le pilote réseau",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Choisissez le pilote réseau pour la carte installée dans cette machine. Si vous choisissez MANUEL, vous devrez entrer le nom du module pilote et les paramètres pour les pilotes qui le requièrent, notamment pour les cartes ISA.",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Choisissez l'interface que vous souhaitez reconfigurer.",
/* TR_SELECT_THE_ITEM */
"Choisissez l'élément que vous souhaitez configurer.",
/* TR_SETTING_ADMIN_PASSWORD */
"Définition du mot de passe 'admin' de %s ....",
/* TR_SETTING_ROOT_PASSWORD */
"Définition du mot de passe 'root'....",
/* TR_SETTING_SETUP_PASSWORD */
"Définition du mot de passe 'setup'....",
/* TR_SETUP_FINISHED */
"L'installation est terminée. Choississez Ok pour redémarrer.",
/* TR_SETUP_NOT_COMPLETE */
"La configuration n'est pas terminée. Vous pourrez y revenir ultérieurement en lançant 'setup' dans une console (PuTTY, ssh).",
/* TR_SETUP_PASSWORD */
"Mot de passe 'setup'",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Définition des paramètres additionnels du module ",
/* TR_SINGLE_GREEN */
"Votre configuration est définie pour une interface VERTE unique.",
/* TR_SKIP */
"Passer",
/* TR_START_ADDRESS */
"Adresse de départ:",
/* TR_START_ADDRESS_CR */
"Adresse de départ\n",
/* TR_STATIC */
"Statique",
/* TR_SUGGEST_IO */
"(propose %x)",
/* TR_SUGGEST_IRQ */
"(propose %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"Ce module est déjà chargé.",
/* TR_TIMEZONE */
"Fuseau horaire",
/* TR_TIMEZONE_LONG */
"Choisissez dans la liste ci-dessous le fuseau horaire dans lequel vous vous situez.",
/* TR_UNABLE_TO_EJECT_CDROM */
"Impossible d'éjecter le CD-ROM.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Impossible d'extraire les modules.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Impossible de trouver d'autres pilotes.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Aucune carte RNIS (ISDN) n'a été détectée. Vous devez préciser des paramètres additionnels du module s'il s'agit d'une carte ISA ou si elle nécessite des paramètres particuliers.",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"Impossible d'initialiser le RNIS (ISDN).",
/* TR_UNABLE_TO_INSTALL_FILES */
"Impossible d'installer les fichiers.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"Impossible d'installer GRUB.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Impossible de charger le module du pilote.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Impossible de créer le système de fichiers boot.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Impossible de créer le système de fichiers log.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Impossible de créer le système de fichiers racine.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Impossible de mettre en place l'espace de swap.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Impossible de créer le lien symbolique /dev/harddisk.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Impossible de créer le lien symbolique /dev/harddisk1.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Impossible de créer le lien symbolique /dev/harddisk2.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Impossible de créer le lien symbolique /dev/harddisk3.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Impossible de créer le lien symbolique /dev/harddisk4.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Impossible de créer le lien symbolique /dev/root",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Impossible de monter le système de fichiers boot.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Impossible de monter le système de fichiers log.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Impossible de monter le système de fichiers proc",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Impossible de monter le système de fichiers racine.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Impossible de monter la partition de swap.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Impossible d'ouvrir le fichier principal hosts.",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Le fichier de configuration n'a pu être ouvert",
/* TR_UNABLE_TO_PARTITION */
"Impossible de partitionner le disque.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"Impossible de supprimer les fichiers temporaires.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"Impossible de renseigner le nom d'hôte.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"Impossible de démonter le CD-ROM/lecteur de disquette.",
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
"Il reste une carte ethernet non affectée de type:\n%s\n\n Vous pouvez l'affecter à:",
/* TR_UNKNOWN */
"INCONNU",
/* TR_UNSET */
"INDETERMINE",
/* TR_USB_KEY_VFAT_ERR */
"Cette clé USB n'est pas utilisable (pas de partition vfat reconnue).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"ATTENTION",
/* TR_WARNING_LONG */
"Si vous changez l'adresse IP et que vous êtes connecté à distance, votre connexion à la machine %s prendra fin et vous devrez vous reconnecter avec la nouvelle adresse. C'est une opération risquée qui ne devrait être tentée que si vous avez un accès physique à la machine en cas de problème.",
/* TR_WELCOME */
"Bienvenue dans le programme d'installation d'%s. Sélectionner Annuler sur l'un des écrans suivants redémarrera votre ordinateur.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Votre configuration est composée d'une unique interface VERTE pour laquelle un pilote a déja été assigné.",
}; 
  
