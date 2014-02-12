/*
 * English (en) Data File
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
 */
 
#include "libsmooth.h"

char *en_tr[] = {

/* TR_ISDN */
"ISDN",
/* TR_ERROR_PROBING_ISDN */
"Unable to scan for ISDN devices.",
/* TR_PROBING_ISDN */
"Scanning and configuring ISDN devices.",
/* TR_MISSING_GREEN_IP */
"Missing Green IP!",
/* TR_CHOOSE_FILESYSTEM */
"Please choose your filesystem:",
/* TR_NOT_ENOUGH_INTERFACES */
"Not enough netcards for your choice.\n\nNeeded: %d - Available: %d\n",
/* TR_INTERFACE_CHANGE */
"Please choose the interface you wish to change.\n\n",
/* TR_NETCARD_COLOR */
"Assigned Cards",
/* TR_REMOVE */
"Remove",
/* TR_MISSING_DNS */
"Misssing DNS.\n",
/* TR_MISSING_DEFAULT */
"Missing Default Gateway.\n",
/* TR_JOURNAL_EXT3 */
"Creating journal for Ext3...",
/* TR_CHOOSE_NETCARD */
"Please choose a networkcard for the following interface - %s.",
/* TR_NETCARDMENU2 */
"Extended Networkmenu",
/* TR_ERROR_INTERFACES */
"There are no free interfaces on your system.",
/* TR_REMOVE_CARD */
"Should the allocation for the networkcard be deleted? - %s",
/* TR_JOURNAL_ERROR */
"Could not create the journal, using fallback to ext2.",
/* TR_FILESYSTEM */
"Choose Filesystem",
/* TR_ADDRESS_SETTINGS */
"Address settings",
/* TR_ADMIN_PASSWORD */
"'admin' password",
/* TR_AGAIN_PROMPT */
"Again:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"All cards successfully allocated.",
/* TR_AUTODETECT */
"* AUTODETECT *",
/* TR_BUILDING_INITRD */
"Building ramdisk...",
/* TR_CANCEL */
"Cancel",
/* TR_CARD_ASSIGNMENT */
"Card assignment",
/* TR_CHECKING */
"Checking URL...",
/* TR_CHECKING_FOR */
"Checking for: %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Choose the ISDN card installed in this computer.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Choose the ISDN protocol you require.",
/* TR_CONFIGURE_DHCP */
"Configure the DHCP server by entering the settings information.",
/* TR_CONFIGURE_NETWORKING */
"Configure networking",
/* TR_CONFIGURE_NETWORKING_LONG */
"You should now configure networking by first loading the correct driver for the GREEN interface. You can do this by either auto-probing for a network card, or by choosing the correct driver from a list. Note that if you have more then one network card installed, you will be able to configure the others later on in the installation. Also note that if you have more then one card which is the same type as GREEN and each card requires special module parameters, you should enter parameters for all cards of this type such that all cards can become active when you configure the GREEN interface.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Configure network drivers, and which interface each card is assigned to.  The current configuration is as follows:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"Configure the CDROM by choosing the appropriate IO address and/or IRQ.",
/* TR_CONGRATULATIONS */
"Congratulations!",
/* TR_CONGRATULATIONS_LONG */
"%s was successfully installed. Please remove any CDROMs in the computer. Setup will now run where you may configure ISDN, network cards, and the system passwords. After Setup has been completed, you should point your web browser at https://%s:444 (or whatever you name your %s), and configure dialup networking (if required) and remote access.",
/* TR_CONTINUE_NO_SWAP */
"Your harddisk is very small, but you can continue with an very small swap. (Use with caution).",
/* TR_CURRENT_CONFIG */
"Current config: %s%s",
/* TR_DEFAULT_GATEWAY */
"Default Gateway:",
/* TR_DEFAULT_GATEWAY_CR */
"Default Gateway\n",
/* TR_DEFAULT_LEASE */
"Default lease (mins):",
/* TR_DEFAULT_LEASE_CR */
"Default lease time\n",
/* TR_DETECTED */
"Detected a: %s",
/* TR_DHCP_HOSTNAME */
"DHCP Hostname:",
/* TR_DHCP_HOSTNAME_CR */
"DHCP Hostname\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"DHCP server configuration",
/* TR_DISABLED */
"Disabled",
/* TR_DISABLE_ISDN */
"Disable ISDN",
/* TR_DISK_TOO_SMALL */
"Your harddisk is too small.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"DNS and Gateway settings",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Enter the DNS and gateway information.  These settings are used only with Static IP (and DHCP if DNS set) on the RED interface.",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Your configuration does not utilise an ethernet adaptor for its RED interface.  DNS and Gateway information for dialup users is configured automatically at dialup time.",
/* TR_DOMAINNAME */
"Domain name",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Domain name cannot be empty.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"Domain name cannot contain spaces.",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Domain name may only contain letters, numbers, hyphens and periods.",
/* TR_DOMAIN_NAME_SUFFIX */
"Domain name suffix:",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Domain name suffix\n",
/* TR_DONE */
"Done",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\nDo you wish to change these settings?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Drivers and card assignments",
/* TR_ENABLED */
"Enabled",
/* TR_ENABLE_ISDN */
"Enable ISDN",
/* TR_END_ADDRESS */
"End address:",
/* TR_END_ADDRESS_CR */
"End address\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Some ISDN cards (especially ISA ones) may require additional module parameters for setting IRQ and IO address information. If you have such a ISDN card, enter these extra parameters here. For example: \"io=0x280 irq=9\". They will be used during card detection.",
/* TR_ENTER_ADMIN_PASSWORD */
"Enter %s 'admin' user password.  This is the user to use for logging into the %s web administration pages.",
/* TR_ENTER_DOMAINNAME */
"Enter Domain name",
/* TR_ENTER_HOSTNAME */
"Enter the machine's hostname.",
/* TR_ENTER_IP_ADDRESS_INFO */
"Enter the IP address information",
/* TR_ENTER_NETWORK_DRIVER */
"Failed to detect a network card automatically. Enter the driver and optional parameters for the network card.",
/* TR_ENTER_ROOT_PASSWORD */
"Enter the 'root' user password. Login as this user for commandline access.",
/* TR_ENTER_SETUP_PASSWORD */
"TO BE REMOVED",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Enter the IP address information for the %s interface.",
/* TR_ENTER_THE_LOCAL_MSN */
"Enter the local phone number (MSN/EAZ).",
/* TR_ENTER_URL */
"Enter the URL path to the ipcop-<version>.tgz and images/scsidrv-<version>.img files. WARNING: DNS not available! This should now just be http://X.X.X.X/<directory>",
/* TR_ERROR */
"Error",
/* TR_ERROR_PROBING_CDROM */
"No CDROM drive found.",
/* TR_ERROR_WRITING_CONFIG */
"Error writing configuration information.",
/* TR_EURO_EDSS1 */
"Euro (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Extracting modules...",
/* TR_FAILED_TO_FIND */
"Failed to find URL file.",
/* TR_FOUND_NIC */
"%s has detected the following NIC in your machine: %s",
/* TR_GERMAN_1TR6 */
"German 1TR6",
/* TR_HELPLINE */
"              <Tab>/<Alt-Tab> between elements   |  <Space> selects",
/* TR_HOSTNAME */
"Hostname",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Hostname cannot be empty.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"Hostname cannot contain spaces.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"Hostname may only contain letters, numbers and hyphens.",
/* TR_INITIALISING_ISDN */
"Initialising ISDN...",
/* TR_INSERT_CDROM */
"Please insert the %s CD in the CDROM drive.",
/* TR_INSERT_FLOPPY */
"Please insert the %s driver diskette in the floppy drive.",
/* TR_INSTALLATION_CANCELED */
"Installation cancelled.",
/* TR_INSTALLING_FILES */
"Installing files...",
/* TR_INSTALLING_GRUB */
"Installing GRUB...",
/* TR_INSTALLING_LANG_CACHE */
"Installing language files...",
/* TR_INTERFACE */
"Interface - %s",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"Interface failed to come up.",
/* TR_INVALID_FIELDS */
"The following fields are invalid:\n\n",
/* TR_INVALID_IO */
"The IO port details entered are invalid. ",
/* TR_INVALID_IRQ */
"The IRQ details entered are invalid.",
/* TR_IP_ADDRESS_CR */
"IP address\n",
/* TR_IP_ADDRESS_PROMPT */
"IP address:",
/* TR_ISDN_CARD */
"ISDN card",
/* TR_ISDN_CARD_NOT_DETECTED */
"ISDN card not detected. You may need to specify additional module parameters if the card is an ISA type or it has special requirements.",
/* TR_ISDN_CARD_SELECTION */
"ISDN card selection",
/* TR_ISDN_CONFIGURATION */
"ISDN Configuration",
/* TR_ISDN_CONFIGURATION_MENU */
"ISDN configuration menu",
/* TR_ISDN_NOT_SETUP */
"ISDN not setup. Some items have not been selected.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"ISDN has not yet been configured. Select the item you wish to configure.",
/* TR_ISDN_PROTOCOL_SELECTION */
"ISDN protocol selection",
/* TR_ISDN_STATUS */
"ISDN is currently %s.\n\n   Protocol: %s\n   Card: %s\n   Local phone number: %s\n\nSelect the item you wish to reconfigure, or choose to use the current settings.",
/* TR_KEYBOARD_MAPPING */
"Keyboard mapping",
/* TR_KEYBOARD_MAPPING_LONG */
"Choose the type of keyboard you are using from the list below.",
/* TR_LEASED_LINE */
"Leased line",
/* TR_LOADING_MODULE */
"Loading module...",
/* TR_LOADING_PCMCIA */
"Loading PCMCIA modules...",
/* TR_LOOKING_FOR_NIC */
"Looking for: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Making boot filesystem...",
/* TR_MAKING_LOG_FILESYSTEM */
"Making log filesystem...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Making root filesystem...",
/* TR_MAKING_SWAPSPACE */
"Making swap space...",
/* TR_MANUAL */
"* MANUAL *",
/* TR_MAX_LEASE */
"Max lease (mins):",
/* TR_MAX_LEASE_CR */
"Max lease time\n",
/* TR_MISSING_BLUE_IP */
"Missing IP information on the BLUE interface.",
/* TR_MISSING_ORANGE_IP */
"Missing IP information on the ORANGE interface.",
/* TR_MISSING_RED_IP */
"Missing IP information on the RED interface.",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"Module name cannot be blank.",
/* TR_MODULE_PARAMETERS */
"Enter the module name and parameters for the driver you require.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Mounting boot filesystem...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Mounting log filesystem...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Mounting root filesystem...",
/* TR_MOUNTING_SWAP_PARTITION */
"Mounting swap partition...",
/* TR_MSN_CONFIGURATION */
"Local phone number (MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Network mask:",
/* TR_NETWORKING */
"Networking",
/* TR_NETWORK_ADDRESS_CR */
"Network address\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Network address:",
/* TR_NETWORK_CONFIGURATION_MENU */
"Network configuration menu",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Network configuration type",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Select the network configuration for %s.  The following configuration types list those interfaces which have ethernet attached. If you change this setting, a network restart will be required, and you will have to reconfigure the network driver assignments.",
/* TR_NETWORK_MASK_CR */
"Network mask\n",
/* TR_NETWORK_SETUP_FAILED */
"Network setup failed.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"Not enough cards were allocated.",
/* TR_NO_BLUE_INTERFACE */
"No BLUE interface assigned.",
/* TR_NO_CDROM */
"No CD-ROM found.",
/* TR_NO_GREEN_INTERFACE */
"No GREEN interface assigned.",
/* TR_NO_HARDDISK */
"No hard disk found.",
/* TR_NO_IPCOP_TARBALL_FOUND */
"No ipcop tarball found on Web Server.",
/* TR_NO_ORANGE_INTERFACE */
"No ORANGE interface assigned.",
/* TR_NO_RED_INTERFACE */
"No RED interface assigned.",
/* TR_NO_SCSI_IMAGE_FOUND */
"No SCSI image found on Web Server.",
/* TR_NO_UNALLOCATED_CARDS */
"No unallocated cards remaining, more are required. You may autodetect and look for more cards, or choose to select a driver from the list.",
/* TR_OK */
"Ok",
/* TR_PARTITIONING_DISK */
"Partitioning disk...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"Passwords do not match.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"Password cannot be blank.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"Password cannot contain spaces.",
/* TR_PASSWORD_PROMPT */
"Password:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Phone number cannot be empty.",
/* TR_PREPARE_HARDDISK */
"The installation program will now prepare the harddisk on %s. First the disk will be partitioned, and then the partitions will have a filesystem put on them.\n\nALL DATA ON THE DISK WILL BE DESTROYED. Do you agree to continue?",
/* TR_PRESS_OK_TO_REBOOT */
"Press Ok to reboot.",
/* TR_PRIMARY_DNS */
"Primary DNS:",
/* TR_PRIMARY_DNS_CR */
"Primary DNS\n",
/* TR_PROBE */
"Probe",
/* TR_PROBE_FAILED */
"Auto detecting failed.",
/* TR_PROBING_HARDWARE */
"Probing hardware...",
/* TR_PROBING_FOR_NICS */
"Probing for NICs...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"Problem setting %s 'admin' user password.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"Problem setting 'root' password.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"TO BE REMOVED",
/* TR_PROTOCOL_COUNTRY */
"Protocol/Country",
/* TR_PULLING_NETWORK_UP */
"Pulling network up...",
/* TR_PUSHING_NETWORK_DOWN */
"Pushing network down...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Pushing non local network down...",
/* TR_QUIT */
"Quit",
/* TR_RED_IN_USE */
"ISDN (or another external connection) is currently in use.  You may not configure ISDN while the RED interface is active.",
/* TR_RESTART_REQUIRED */
"\n\nWhen configuration is complete, a network restart will be required.",
/* TR_RESTORE */
"Restore",
/* TR_RESTORE_CONFIGURATION */
"If you have a floppy with an %s system configuration on it, place the floppy in the floppy drive and press the Restore button.",
/* TR_ROOT_PASSWORD */
"'root' password",
/* TR_SECONDARY_DNS */
"Secondary DNS:",
/* TR_SECONDARY_DNS_CR */
"Secondary DNS\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"Secondary DNS specified without a Primary DNS",
/* TR_SECTION_MENU */
"Section menu",
/* TR_SELECT */
"Select",
/* TR_SELECT_CDROM_TYPE */
"Select CDROM type",
/* TR_SELECT_CDROM_TYPE_LONG */
"No CD-ROM was detected in this machine.  Please select which of the following drivers you wish to use so that %s can access the CD-ROM.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Select installation media",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s can be installed from multiple sources.  The simplest is to use the machines CDROM drive. If the computer lacks a drive, you may install via another machine on the LAN which has the installation files available via HTTP or FTP.",
/* TR_SELECT_NETWORK_DRIVER */
"Select network driver",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Select the network driver for the card installed in this machine. If you select MANUAL, you will be given an opportunity to enter the driver module name and parameters for drivers which have special requirements, such as ISA cards.",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Select the interface you wish to reconfigure.",
/* TR_SELECT_THE_ITEM */
"Select the item you wish to configure.",
/* TR_SETTING_ADMIN_PASSWORD */
"Setting %s 'admin' user password...",
/* TR_SETTING_ROOT_PASSWORD */
"Setting 'root' password....",
/* TR_SETTING_SETUP_PASSWORD */
"TO BE REMOVED",
/* TR_SETUP_FINISHED */
"Setup is complete.  Press Ok.",
/* TR_SETUP_NOT_COMPLETE */
"Initial setup was not entirely complete.  You must ensure that Setup is properly finished by running setup again at the shell.",
/* TR_SETUP_PASSWORD */
"TO BE REMOVED",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Set additional module parameters",
/* TR_SINGLE_GREEN */
"Your configuration is set for a single GREEN interface.",
/* TR_SKIP */
"Skip",
/* TR_START_ADDRESS */
"Start address:",
/* TR_START_ADDRESS_CR */
"Start address\n",
/* TR_STATIC */
"Static",
/* TR_SUGGEST_IO */
"(suggest %x)",
/* TR_SUGGEST_IRQ */
"(suggest %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"This driver module is already loaded.",
/* TR_TIMEZONE */
"Timezone",
/* TR_TIMEZONE_LONG */
"Choose the timezone you are in from the list below.",
/* TR_UNABLE_TO_EJECT_CDROM */
"Unable to eject the CDROM.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Unable to extract modules.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Unable to find any additional drivers.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Unable to find an ISDN card in this computer. You may need to specify additional module parameters if the card is an ISA type or it has special requirements.",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"Unable to initialise ISDN.",
/* TR_UNABLE_TO_INSTALL_FILES */
"Unable to install files.",
/* TR_UNABLE_TO_INSTALL_LANG_CACHE */
"Unable to install language files.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"Unable to install GRUB.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Unable to load driver module.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Unable to make boot filesystem.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Unable to make log filesystem.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Unable to make root filesystem.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Unable to make swap space.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Unable to create symlink /dev/harddisk.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Unable to create symlink /dev/harddisk1.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Unable to create symlink /dev/harddisk2.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Unable to create symlink /dev/harddisk3.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Unable to create symlink /dev/harddisk4.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Unable to create symlink /dev/root.",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Unable to mount boot filesystem.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Unable to mount log filesystem.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Unable to mount proc filesystem.",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Unable to mount root filesystem.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Unable to mount the swap partition.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Unable to open main hosts file.",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Unable to open settings file",
/* TR_UNABLE_TO_PARTITION */
"Unable to partition the disk.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"Unable to remove temporary downloaded files.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"Unable to set hostname.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"Unable to unmount the CDROM/floppydisk.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"Unable to unmount harddisk.",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"Unable to write /etc/fstab",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"Unable to write /etc/hostname",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"Unable to write /etc/hosts.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"Unable to write /etc/hosts.allow.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"Unable to write /etc/hosts.deny.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"Unable to write %s/ethernet/settings.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"Unable to write %s/main/hostname.conf",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"Unable to write %s/main/settings.",
/* TR_UNCLAIMED_DRIVER */
"There is an unclaimed ethernet card of type:\n%s\n\nYou can assign this to:",
/* TR_UNKNOWN */
"UNKNOWN",
/* TR_UNSET */
"UNSET",
/* TR_USB_KEY_VFAT_ERR */
"This USB key is invalid (no vfat partition found).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"WARNING",
/* TR_WARNING_LONG */
"If you change this IP address, and you are logged in remotely, your connection to the %s machine will be broken, and you will have to reconnect on the new IP. This is a risky operation, and should only be attempted if you have physical access to the machine, should something go wrong.",
/* TR_WELCOME */
"Welcome to the %s installation program. Selecting Cancel on any of the following screens will reboot the computer.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Your configuration is set for a single GREEN interface, which already has a driver assigned.",
/* TR_YES */
"Yes",
/* TR_NO */
"No",
/* TR_AS */
"as",
/* TR_IGNORE */
"Ignore",
/* TR_PPP_DIALUP */
"PPP DIALUP (PPPoE, modem, ATM ...)",
/* TR_DHCP */
"DHCP",
/* TR_DHCP_STARTSERVER */
"Starting DHCP-server ...",
/* TR_DHCP_STOPSERVER */
"Stopping DHCP-server ...",
/* TR_LICENSE_ACCEPT */
"I accept this license.",
/* TR_LICENSE_NOT_ACCEPTED */
"License not accepted. Exit!",
/* TR_EXT2FS_DESCR */
"Ext2 - Filesystem without journal (suggested for flashdrives)",
/* TR_EXT3FS_DESCR */
"Ext3 - Filesystem with journal",
/* TR_EXT4FS_DESCR */
"Ext4 - Filesystem with journal",
/* TR_REISERFS_DESCR */
"ReiserFS - Filesystem with journal",
/* TR_NO_LOCAL_SOURCE */
"No local source media found. Starting download.",
/* TR_DOWNLOADING_ISO */
"Downloading Installation-Image ...",
/* TR_DOWNLOAD_ERROR */
"Error while downloading!",
/* TR_DHCP_FORCE_MTU */
"Force DHCP mtu:",
/* TR_IDENTIFY */
"Identify",
/* TR_IDENTIFY_SHOULD_BLINK */
"Selected port should blink now ...",
/* TR_IDENTIFY_NOT_SUPPORTED */
"Function is not supported by this port.",
};
