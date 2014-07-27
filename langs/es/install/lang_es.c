/*
 * Spanish (es) Data File
 *
 * This file is part of the IPFire.
 * 
 * IPFire is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * IPFire is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with IPFire; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
 *
 * (c) IPFire Team  <info@ipfire.org>
 *
 */
 
#include "libsmooth.h"

char *es_tr[] = {

/* TR_ISDN */
"ISDN",
/* TR_ERROR_PROBING_ISDN */
"Imposibe escanear dispositivos ISDN.",
/* TR_PROBING_ISDN */
"Buscando y configurando dispositivos ISDN.",
/* TR_MISSING_GREEN_IP */
"¡Hace falta la dirección ip en GREEN!",
/* TR_CHOOSE_FILESYSTEM */
"Por favor elija su sistema de Archivos:",
/* TR_NOT_ENOUGH_INTERFACES */
"No hay suficientes tarjetas de red para su selección.\n\nNecesarias: %d - Disponibles: %d\n",
/* TR_INTERFACE_CHANGE */
"Por favor elija la interfaz que desea modificar.\n\n",
/* TR_NETCARD_COLOR */
"Tarjetas de red asignadas",
/* TR_REMOVE */
"Remover",
/* TR_MISSING_DNS */
"Faltan DNS.\n",
/* TR_MISSING_DEFAULT */
"Falta la puerta de enlace por defecto.\n",
/* TR_JOURNAL_EXT3 */
"Creando journal para Ext3...",
/* TR_CHOOSE_NETCARD */
"Por favor elija una tarjeta de red para la siguiente interfaz  - %s.",
/* TR_NETCARDMENU2 */
"Menú de Red extendido",
/* TR_ERROR_INTERFACES */
"No hay interfaces libres en su sistema.",
/* TR_REMOVE_CARD */
"La ubicación de la tarjeta de red debería ser borrada? - %s",
/* TR_JOURNAL_ERROR */
"No se pudo crear el journal usando fallback a ext2.",
/* TR_FILESYSTEM */
"Seleccione el sistema de Archivos",
/* TR_ADDRESS_SETTINGS */
"Configuración de direcciones",
/* TR_ADMIN_PASSWORD */
"Contraseña 'admin'",
/* TR_AGAIN_PROMPT */
"Nuevamente:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Todas las tarjetas se asignaron correctamente.",
/* TR_AUTODETECT */
"* AUTODETECTANDO *",
/* TR_BUILDING_INITRD */
"Construyendo ramdisk...",
/* TR_CANCEL */
"Cancelar",
/* TR_CARD_ASSIGNMENT */
"Asignación de Tarjetas",
/* TR_CHECKING */
"Revisando URL...",
/* TR_CHECKING_FOR */
"Probando : %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Seleccione el tipo de tarjeta ISDN instalada en este computador.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Seleccione el protocolo ISDN que ud. requiera.",
/* TR_CONFIGURE_DHCP */
"Configure el servidor DHCP introduciendo la siguiente información.",
/* TR_CONFIGURE_NETWORKING */
"Configuraciónes de Red",
/* TR_CONFIGURE_NETWORKING_LONG */
"Ahora debería configurar la red primeramente cargando el driver correcto para la interfaz GREEN. Puede hacer esto, ya sea por medio de auto-detección de la tarjeta de red, o eligiendo el driver correcto de la lista. Tome en cuenta que si usted tiene mas de una tarjeta de red instalada, podrá configurar las demás posteriormente durante la instalación. También tenga en cuenta que si posee mas de una tarjeta que sea del mismo tipo que su interfaz GREEN, cada una requerirá parámetros de módulo especiales, los cuales debe introducir para cada una de las tarjetas, ya que todas las tarjetas se podrían activar cuando se configure la interfaz GREEN.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Configure los drivers de red, y a cual interfaz será asignada cada tarjeta. La configuración actual es la siguiente:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"Configure la unidad de CDROM eligiendo la dirección IO apropiada y/o la dirección IRQ.",
/* TR_CONGRATULATIONS */
"¡Felicidades!",
/* TR_CONGRATULATIONS_LONG */
"%s fué instalado exitosamente. Por favor retire cualquier CDROM de las unidades. La instalación se ejecutará ahora y usted podrá configurar las parámetros de ISDN, Tarjetas de red, y las contraseñas del sistema. Una vez que la instalación se halla completado usted podrá dirigir su navegador de internet a https://%s:444 (o a cualquiera que sea el nombre de su %s), y configurar la red por dialup (si fuese necesario) y el acceso remoto.",
/* TR_CONTINUE_NO_SWAP */
"Su disco duro es muy pequeño, pero podrá continuar un swap muy reducido (Use con precaución).",
/* TR_CURRENT_CONFIG */
"Configuración Actual: %s%s",
/* TR_DEFAULT_GATEWAY */
"Puerta de enlace por defecto:",
/* TR_DEFAULT_GATEWAY_CR */
"Puerta de enlace por defecto\n",
/* TR_DEFAULT_LEASE */
"Default lease (mins):",
/* TR_DEFAULT_LEASE_CR */
"Default lease time\n",
/* TR_DETECTED */
"Se detectó: %s",
/* TR_DHCP_HOSTNAME */
"DHCP Hostname:",
/* TR_DHCP_HOSTNAME_CR */
"DHCP Hostname\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"Configuración de servidor DHCP",
/* TR_DISABLED */
"Desactivado",
/* TR_DISABLE_ISDN */
"Desactivar ISDN",
/* TR_DISK_TOO_SMALL */
"Su disco duro es muy pequeño.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"Configuraciones de DNS y Puerta de enlace(Gateway)",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Introduzca la información de DNS y puerta de enlace predeterminado. Estas configuraciones sólo son utilizadas con IP estática (y DHCP si se configura el DNS) en la interfaz RED",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Su configuración no utiliza una interfaz ethernet para la interfaz RED. La información de Puerta de enlace y DNS para usuarios de dialup, es configurada automáticamente en el momento de marcar.",
/* TR_DOMAINNAME */
"Nombre de dominio",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Nombre de domino no puede estar vacío",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"El nombre de dominio no puede contener espacios",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Los nombres de dominio sólo pueden contener letras, números, guiones y guion_bajo",
/* TR_DOMAIN_NAME_SUFFIX */
"Sufijo de nombre de dominio:",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Sufijo de nombre de dominio\n",
/* TR_DONE */
"Terminado",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\n¿Desea cambiar estas configuraciones?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Drivers y asignación de tarjeta",
/* TR_ENABLED */
"Activado",
/* TR_ENABLE_ISDN */
"Activar ISDN",
/* TR_END_ADDRESS */
"Dirección final:",
/* TR_END_ADDRESS_CR */
"Dirección final\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Algunas tarjetas ISDN (especialmente las ISA) pueden requerir parámetros adicionales de módulo para configuracioenes como IRQ la dirección de dirección IO. Si usted tiene una tarjeta de este tipo, introduzca los parámetros adicionales aquí. Por ejemplo: 'io=0x280 irq=9'. Serán utilizados durante la detección de la tarjeta.",
/* TR_ENTER_ADMIN_PASSWORD */
"Introduzca la contraseña del usuario %s'admin'. Este es el usuario que accederá a la página de administración %sweb",
/* TR_ENTER_DOMAINNAME */
"Introduzca el nombre de dominio",
/* TR_ENTER_HOSTNAME */
"Introduzca el nombre host de la máquina",
/* TR_ENTER_IP_ADDRESS_INFO */
"Introduzca la dirección IP",
/* TR_ENTER_NETWORK_DRIVER */
"Fallo la detección automática de la tarjeta de red. Introduzca el driver y los parámetros opcionales para esta tarjeta de red.",
/* TR_ENTER_ROOT_PASSWORD */
"Introduzca la contraseña del usuario 'root'. Acceda como este usuario para obtener acceso a la línea de comandos.",
/* TR_ENTER_SETUP_PASSWORD */
"A REMOVER",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Introduzca la dirección IP para la interfaz %s .",
/* TR_ENTER_THE_LOCAL_MSN */
"Introduzca el número telefónico local",
/* TR_ENTER_URL */
"Introduzca  la ruta URL de losarchivo ipcop<version>.tgz e images/scsidrv-<version>.img  ADVERTENCIA: ¡DNS no disponible! Ahora debería ser solamente http://X.X.X.X/<directory>",
/* TR_ERROR */
"Error",
/* TR_ERROR_PROBING_CDROM */
"No se encontró unidad de CD/DVDROM",
/* TR_ERROR_WRITING_CONFIG */
"Error escribiendo la información de configuración",
/* TR_EURO_EDSS1 */
"Euro (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Extrayendo modulos...",
/* TR_FAILED_TO_FIND */
"Fallo al encontrar el archivo URL",
/* TR_FOUND_NIC */
"%s ha detectado la siguiente tarjeta de red en su máquina %s",
/* TR_GERMAN_1TR6 */
"German 1TR6",
/* TR_HELPLINE */
"              <Tab>/<Alt-Tab> entre elementos   |  <Espacio> selecciona",
/* TR_HOSTNAME */
"Nombre de host",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Nombre de host no puede estar vacío",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"Nombre de host no puede contener espacios.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"El nombre de host solo puede contener letra, números y guiones",
/* TR_INITIALISING_ISDN */
"Inicializando ISDN...",
/* TR_INSERT_CDROM */
"Por favor inserte el CD %s en la unidad de CD/DVD",
/* TR_INSERT_FLOPPY */
"Por favor inserte el diskette de drivers %s  en la unidad floppy",
/* TR_INSTALLATION_CANCELED */
"Instalación cancelada",
/* TR_INSTALLING_FILES */
"Instalando archivos...",
/* TR_INSTALLING_GRUB */
"Instalando GRUB...",
/* TR_INSTALLING_LANG_CACHE */
"Instalando archivos de idioma...",
/* TR_INTERFACE */
"Interfaz - %s",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"La interfaz falló en arrancar",
/* TR_INVALID_FIELDS */
"Los siguientes campos son inválidos:\n\n",
/* TR_INVALID_IO */
"Los detalles de puerto IO insertados son inválidos.",
/* TR_INVALID_IRQ */
"Los detalles de IRQ insertados son inválidos.",
/* TR_IP_ADDRESS_CR */
"Dirección IP\n",
/* TR_IP_ADDRESS_PROMPT */
"Dirección IP:",
/* TR_ISDN_CARD */
"Tarjeta ISDN",
/* TR_ISDN_CARD_NOT_DETECTED */
"La tarjeta ISDN no fue detectada. Tal vez debería específicar módulos de parámetro adicionales si la tarjeta es tipo ISA o tiene requerimentos especiales.",
/* TR_ISDN_CARD_SELECTION */
"Selección de tarjeta ISDN",
/* TR_ISDN_CONFIGURATION */
"Configuración ISDN",
/* TR_ISDN_CONFIGURATION_MENU */
"Menú de configuración ISDN",
/* TR_ISDN_NOT_SETUP */
"ISDN no está configurado. Algunos elementos no han sido seleccionados.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"ISDN no ha sido configurado aún. Seleccione el elemento que desea configurar",
/* TR_ISDN_PROTOCOL_SELECTION */
"Selección de protocolo ISDN",
/* TR_ISDN_STATUS */
"ISDN actual es %s.\n\n Protocolo: %s\n Tarjeta: %s\n Número de teléfono lcoal: %s\n\nSeleccione el elemento que desea reconfigurar, o elija usar la configuración actual.",
/* TR_KEYBOARD_MAPPING */
"Mapeo de teclado",
/* TR_KEYBOARD_MAPPING_LONG */
"Seleccione de la lista el tipo de teclado que está utilizando.",
/* TR_LEASED_LINE */
"Concesión de línea",
/* TR_LOADING_MODULE */
"Cargando módulo...",
/* TR_LOADING_PCMCIA */
"Cargando módulos PCMCIA...",
/* TR_LOOKING_FOR_NIC */
"Buscando: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Generando el sistema de arranque...",
/* TR_MAKING_LOG_FILESYSTEM */
"Generando el sistema de log...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Generando el sistema de archivos root...",
/* TR_MAKING_SWAPSPACE */
"Generando el espacio swap....",
/* TR_MANUAL */
"* MANUAL *",
/* TR_MAX_LEASE */
"Concesión MAX (mins):",
/* TR_MAX_LEASE_CR */
"Tiempo MAX de concesión\n",
/* TR_MISSING_BLUE_IP */
"Falta información IP en la interfaz BLUE",
/* TR_MISSING_ORANGE_IP */
"Falta información IP en la interfaz ORANGE",
/* TR_MISSING_RED_IP */
"Falta información IP en la interfaz RED",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"El nombre de módulo no puede estar vacío.",
/* TR_MODULE_PARAMETERS */
"Introduzca el nombre del módulo y los parámetros que requiera para sus drivers.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Montando sistema de archivos de arranque...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Montando sistema archvos log...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Montando sistema de archivos root....",
/* TR_MOUNTING_SWAP_PARTITION */
"Montando partición swap...",
/* TR_MSN_CONFIGURATION */
"Número telefónico local (MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Máscara de red:",
/* TR_NETWORKING */
"Redes",
/* TR_NETWORK_ADDRESS_CR */
"Dirección de red\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Dirección de red:",
/* TR_NETWORK_CONFIGURATION_MENU */
"Menú de configuración de red",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Tipo de configuración de red",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Seleccione la configuración de red para %s. Los siguientes tipos de configuración muestran aquellas interfaces que tengan asignada una tarjeta ethernet. Si ud. cambia esta configuración, será necesario reiniciar el servicio de red, y ud. deberá volver a asignar las asignaciones de tarjetas de red.",
/* TR_NETWORK_MASK_CR */
"Máscara de red\n",
/* TR_NETWORK_SETUP_FAILED */
"Configuración de red falló.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"No hay suficientes tarjetas de red para asignar.",
/* TR_NO_BLUE_INTERFACE */
"No se asignó interfaz BLUE.",
/* TR_NO_CDROM */
"No se encontró  CD/DVD.",
/* TR_NO_GREEN_INTERFACE */
"No se asignó interfaz GREEN.",
/* TR_NO_HARDDISK */
"No se encontró unidad de disco duro.",
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
"No se encontró ningun archivo tarball de ipcop en el servidor web",
/* TR_NO_ORANGE_INTERFACE */
"No se asignó Interfaz ORANGE.",
/* TR_NO_RED_INTERFACE */
"No se asignó interfaz ROJA.",
/* TR_NO_SCSI_IMAGE_FOUND */
"No se encontró imagen SCSI en el servidor web.",
/* TR_NO_UNALLOCATED_CARDS */
"No quedan tarjetas sin asignar. Se necesitan mas. Se puede proceder a autodetección y búsqueda de mas tarjetas o elegir un driver de la lista.",
/* TR_OK */
"Ok",
/* TR_PARTITIONING_DISK */
"Particionando Disco...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"Las contraseñas no concuerdan.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"La contraseña no puede ir en blanco.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"La contraseña no puede llevar espacios.",
/* TR_PASSWORD_PROMPT */
"Contraseña:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Número telefónico no puede ir en blanco.",
/* TR_PREPARE_HARDDISK */
"El programa de instalación va a preparar el disco duro en %s. Primero el disco será particionado y después se les colocará un sistema de archivos a las particiones.",
/* TR_PRESS_OK_TO_REBOOT */
"Presione Ok para reiniciar el sistema.",
/* TR_PRIMARY_DNS */
"DNS Primario:",
/* TR_PRIMARY_DNS_CR */
"DNS Primario\n",
/* TR_PROBE */
"Detección",
/* TR_PROBE_FAILED */
"Falló la auto detección",
/* TR_PROBING_HARDWARE */
"Detectando Hardware...",
/* TR_PROBING_FOR_NICS */
"Detectando NICs....",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"Problema estableciendo la contraseña del usuario %s 'admin'",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"Problema estableciendo la contraseña del usuario 'root'",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"A REMOVER",
/* TR_PROTOCOL_COUNTRY */
"Protocolo/País",
/* TR_PULLING_NETWORK_UP */
"Encendiendo la red...",
/* TR_PUSHING_NETWORK_DOWN */
"Apagando la red....",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Apagando red no local...",
/* TR_QUIT */
"Salir",
/* TR_RED_IN_USE */
"ISDN (u otra conexión externa) se encuentra en uso. No puede configurar ISDN mientras la interfaz RED está activa.",
/* TR_RESTART_REQUIRED */
"\n\nCuando la configuración se complete, Un reinicio de red será requerido",
/* TR_RESTORE */
"Restaurar",
/* TR_RESTORE_CONFIGURATION */
"Si cuenta con un floppy con la configuración del %s sistema en el, insertelo en la unidad lectora y presione el botón restaurar.",
/* TR_ROOT_PASSWORD */
"Contraseña 'root'",
/* TR_SECONDARY_DNS */
"DNS Secundario:",
/* TR_SECONDARY_DNS_CR */
"DNS Secundario\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"DNS Secundario especificado sinun servidor DNS primario",
/* TR_SECTION_MENU */
"Sección de Menú",
/* TR_SELECT */
"Selección",
/* TR_SELECT_CDROM_TYPE */
"Seleccione tipo de CDROM",
/* TR_SELECT_CDROM_TYPE_LONG */
"No se detectó unidad de CD/DVD en esta máquina. Por favor seleccione cual de los siguientes drivers desea usar para que %s pueda acceder a la unidad de CD/DVD",
/* TR_SELECT_INSTALLATION_MEDIA */
"Seleccione medio de instalación",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s puede ser instalado desde múltiples fuentes. La mas sencilla es usar la unidad de CD/DVD. Si la máquina carece de una, puede instalarlo desde otra máquina en la red local que tenga los archivos de instalación disponibles via HTTP o FTP.",
/* TR_SELECT_NETWORK_DRIVER */
"Seleccione drivers de red",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Seleccione el driver de red para la tarjeta instalada en esta máquina. Si usted elige MANUAL, se le dará una oportunidad de introducir los parámetros y nombres de módulo para los drivers que requieran configuracioens especiales como las tarjetas ISA",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Seleccione la  interfaz que desea reconfigurar",
/* TR_SELECT_THE_ITEM */
"Seleccione el elemento que desea configurar",
/* TR_SETTING_ADMIN_PASSWORD */
"Estableciendo la contraseña del usuario %s 'admin'...",
/* TR_SETTING_ROOT_PASSWORD */
"Estableciendo la contraseña del usuario 'root'...",
/* TR_SETTING_SETUP_PASSWORD */
"A REMOVER",
/* TR_SETUP_FINISHED */
"La configuración se ha completado. Presione Ok.",
/* TR_SETUP_NOT_COMPLETE */
"La configuración inicial no se completó totalmente. Asegúrese de configurar todo correctamente ejecutando setup de nuevo desde la línea de comandos.",
/* TR_SETUP_PASSWORD */
"A REMOVER",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Configurar parámetros de módulo adicionales",
/* TR_SINGLE_GREEN */
"Su configuración está dispuesta para una interface GREEN única",
/* TR_SKIP */
"Omitir",
/* TR_START_ADDRESS */
"Dirección de inicio:",
/* TR_START_ADDRESS_CR */
"Dirección de inicio\n",
/* TR_STATIC */
"Estático",
/* TR_SUGGEST_IO */
"(sugerir %x)",
/* TR_SUGGEST_IRQ */
"(sugerir %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"El módulo de este driver ya ha sido cargado.",
/* TR_TIMEZONE */
"Zona de tiempo",
/* TR_TIMEZONE_LONG */
"Seleccione su zona de tiempo de la siguiente lista.",
/* TR_UNABLE_TO_EJECT_CDROM */
"Imposible expulsar el CD/DVD",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Imposible extraer módulos.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Imposible encontrar drivers adicionales",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Imposible encontrar tarjeta ISDN en esta máquina. Podría necesitar especificar parámetros de módulo adicionales si la tarjeta es tipo ISA o tiene requerimientos especiales",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"Imposible inicializar ISDN",
/* TR_UNABLE_TO_INSTALL_FILES */
"Imposible instalar archivos.",
/* TR_UNABLE_TO_INSTALL_LANG_CACHE */
"Imposible instalar archivos de Idioma.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"Imposible instalar GRUB.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Imposible cargar driver de módulo.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Imposibe crear sistema de archivos de arranque.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Imposible crear sistema de archivos log.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Imposible crear sistema de archivos root.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Imposible crear espacio swap",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Imposible crear enlace simbólico /dev/harddisk.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Imposible crear enlace simbólico /dev/harddisk1.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Imposible crear enlace simbólico /dev/harddisk2.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Imposible crear enlace simbólico /dev/harddisk3.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Imposible crear enlace simbólico /dev/harddisk4.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Imposible crear enlace simbólico a /dev/root",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Imposible montar boot filesystem.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Imposible montar log filesystem.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Imposible montar proc filesystem.",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Imposible montar root filesystem.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Imposible montar the swap partition.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Imposible abrir main hosts file.",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Imposible abrir settings file",
/* TR_UNABLE_TO_PARTITION */
"Imposible particionar el disco.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"Imposible remover archivos de descarga temporales.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"Imposible asignar el nombre de host.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"Imposible desmontar la unidad CDROM/Floppydisk.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"Imposible desmontar disco duro.",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"Imposible escribir /etc/fstab",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"Imposible escribir /etc/hostname",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"Imposible escribir /etc/hosts.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"Imposible escribir /etc/hosts.allow.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"Imposible escribir /etc/hosts.deny.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"Imposible escribir %s/ethernet/settings.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"Imposible escribir %s/main/hostname.conf",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"Imposible escribir %s/main/settings.",
/* TR_UNCLAIMED_DRIVER */
"There is an unclaimed ethernet card of type:\n%s\n\nYou can assign this to:",
/* TR_UNKNOWN */
"DESCONOCIDO",
/* TR_UNSET */
"NO ASIGNADO",
/* TR_USB_KEY_VFAT_ERR */
"Esta unidad USB no es válida (no se encontró partición vfat).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"ADVERTENCIA",
/* TR_WARNING_LONG */
"Si usted cambia esta dirección IP mientras se encuentra conectado de manera remota, su conexión a esta máquina %s será terminada, i tendrá que reconectarse con la nueva dirección IP. Esta es una operación riesgosa y solamente debería ser intentada si usted tiene acceso físico a la máquina en caso de que algo salga mal.",
/* TR_WELCOME */
"Bienvenido al programa de instalación de %s. Si selecciona cancelar en cualquiera de las pantallas siguientes su computadora será reiniciada.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Su sistema está configurado a interfaz GREEN única, la cual ya ha sido asignada.",
/* TR_YES */
"Si",
/* TR_NO */
"No",
/* TR_AS */
"as",
/* TR_IGNORE */
"Ignorar",
/* TR_PPP_DIALUP */
"PPP DIALUP (PPPoE, modem, ATM ...)",
/* TR_DHCP */
"DHCP",
/* TR_DHCP_STARTSERVER */
"Iniciando Servidor DHCP ...",
/* TR_DHCP_STOPSERVER */
"Deteniendo Servidor DHCP ...",
/* TR_LICENSE_ACCEPT */
"I accept this license.",
/* TR_LICENSE_NOT_ACCEPTED */
"License not accepted. Exit!",
/* TR_EXT4FS */
"EXT4 - Filesystem",
/* TR_EXT4FS_WO_JOURNAL */
"EXT4 - Filesystem without journal",
/* TR_XFS */
"XFS - Filesystem",
/* TR_REISERFS */
"ReiserFS - Filesystem",
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
