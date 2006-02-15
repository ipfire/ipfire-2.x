/*
 * Spanish (es) Data File
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
 * (c) 2003 Curtis Anderson, Diego Lombardia, Mark Peter, QuiQue Soriano,
 * David Cabrera Lozano, Jose Sanchez, Santiago Cassina, Marcelo Zunino,
 * Marco van Beek, Alfredo Matignon, (c) 2005 Juan Janczuk 
 */
 
#include "libsmooth.h"

char *es_tr[] = {

/* TR_ADDRESS_SETTINGS */
"Configuración de direcciones",
/* TR_ADMIN_PASSWORD */
"Contraseña de usuario Admin",
/* TR_AGAIN_PROMPT */
"Otra vez:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Todas la tarjetas se asignaron con éxito.",
/* TR_AUTODETECT */
"* AUTODETECTAR *",
/* TR_BUILDING_INITRD */
"Generando INITRD...",
/* TR_CANCEL */
"Cancelar",
/* TR_CARD_ASSIGNMENT */
"Asignación de tarjetas",
/* TR_CHECKING */
"Chequeando la URL...",
/* TR_CHECKING_FOR */
"Verificando : %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Elija la tarjeta ISDN instalada en su equipo.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Elija el protocolo ISDN requerido:",
/* TR_CONFIGURE_DHCP */
"Ingrese la configuracion para el servidor DHCP.",
/* TR_CONFIGURE_NETWORKING */
"Configuración de Red",
/* TR_CONFIGURE_NETWORKING_LONG */
"Ahora debe configurar la red. Primero cargue el driver para su interfaz VERDE. Esto puede hacerse mediante autodeteccion, o eligiendo el driver adecuado de la lista disponible. Si tiene más de una tarjeta de red instalada, podrá configurar las restantes luego. Observe que si usted tiene más de una tarjeta que sea del mismo tipo que la VERDE y cada tarjeta requiere parámetros especiales del módulo, se deben ingresar los parámetros para todas las tarjetas de este tipo, de modo que todas pueden ser activadas cuando se configura el interfaz VERDE.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Configura los controladores de red, y cual es el inferfaz asignado a cada targeta también. La configuración actual es:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"Configura el CDROM eligiendo la dirección IO y/o IRQ adecuada.",
/* TR_CONGRATULATIONS */
"¡Felicitaciones!",
/* TR_CONGRATULATIONS_LONG */
"%s ha sido instalado exitosamente. Por favor, quite el disquete o CD que pueda tener en su PC. Se iniciará el Setup, en el podrá configurar ISDN, tarjetas de red, y contraseñas del sistema. Luego de finalizado el Setup, podrá apuntar su navegador web a http://%s:81 o https://%s:445 (o como nombró su %s), y configurar los accesos telefónicos y/o los accesos remotos que correspondan a su instalación. No olvide adjudicar una contraseña para el usuario \"dial\" en su %s, si no desea que usuarios \"admin\" puedan controlar el enlace.",
/* TR_CONTINUE_NO_SWAP */
"Su disco duro es muy pequeño, podrá continuar sin swap. (Usar con precaución)",
/* TR_CURRENT_CONFIG */
"Configuración actual: %s%s",
/* TR_DEFAULT_GATEWAY */
"Pta. enlace o gateway predetermino",
/* TR_DEFAULT_GATEWAY_CR */
"Pta. enlace o gateway predetermino\n",
/* TR_DEFAULT_LEASE */
"Renovación por defecto (min):",
/* TR_DEFAULT_LEASE_CR */
"Hora de renovación por defecto\n",
/* TR_DETECTED */
"Detectado un: %s",
/* TR_DHCP_HOSTNAME */
"Nombre de ordenador de DHCP",
/* TR_DHCP_HOSTNAME_CR */
"Nombre de ordenador de DHCP\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"Configuración del servidor DHCP",
/* TR_DISABLED */
"Deshabilitado",
/* TR_DISABLE_ISDN */
"Inhabilite RDSI",
/* TR_DISK_TOO_SMALL */
"Tu disco duro es demasiado pequeño.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"Opciones de DNS y Gateway",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Ingrese la información de DNS y puerta de enlace. Estas serán usadas solamente si el DHCP no está habilitado en la interfase ROJA.",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Su configuración no usa un adaptador ethernet para la interfase ROJA. La información de DNS y puerta de enlace para acceso telefonico a redes se configura automaticamente al momento de marcar la connección (dialup).",
/* TR_DOMAINNAME */
"Nombre de Dominio",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Debe asignar un nombre de Dominio.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"Nombre de Dominio no puede contener espacios.",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"El nombre de Dominio s o puede contener letras, números, guiones y puntos.",
/* TR_DOMAIN_NAME_SUFFIX */
"Sufijo del nombre de dominio",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Sufijo del nombre de dominio\n",
/* TR_DONE */
"Acabado",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\n¿Desea cambiar esta configuración?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Controladores y targetas asignadas",
/* TR_ENABLED */
"Activo",
/* TR_ENABLE_ISDN */
"Activar RDSI",
/* TR_END_ADDRESS */
"Dirección final:",
/* TR_END_ADDRESS_CR */
"Dirección final\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Algunas tarjetas ISDN (en particular las ISA) pueden necesitar parametros adicionales en la carga de su módulos para adjudicar IRQ o direcciones de I/O. Si tiene alguna de estas tarjetas, ingrese estos parámetros aquí. Por ejem: \"io=0x280 irq=9\". Esta información sera utilizada durante la deteccion de tarjetas.",
/* TR_ENTER_ADMIN_PASSWORD */
"Ingresar la contraseña de \"admin\" para %s. Este es el nombre de usuario que se usará para ingresar a las páginas web de administración de %s.",
/* TR_ENTER_DOMAINNAME */
"Ingresa el nombre del Dominio",
/* TR_ENTER_HOSTNAME */
"Ingrese el nombre de host para su máquina.",
/* TR_ENTER_IP_ADDRESS_INFO */
"Introduce información de la dirección IP.",
/* TR_ENTER_NETWORK_DRIVER */
"Falló la detección automática de la targeta de red. Introduce el controlador y parámetos para la targeta de red.",
/* TR_ENTER_ROOT_PASSWORD */
"Ingrese la contraseña para el usuario \"root\". Este es el nombre de usuario para acceder a la consola de comandos.",
/* TR_ENTER_SETUP_PASSWORD */
"Ingrese la contraseña para el usuario \"setup\". Este es el nombre de usuario para ingrear al sistema y ejecutar el programa Setup.",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Introduce la dirección IP para el interface %s.",
/* TR_ENTER_THE_LOCAL_MSN */
"Introduce el número de tléfono local (MSN/EAZ).",
/* TR_ENTER_URL */
"Ingresa la URL hacia los ficheros ipcop-<version>.tgz y images/scsidrv-<version>.img. ATENCIÓN: el DNS no disponible! La direccio debe tener la forma http://X.X.X.X/<carpeta>",
/* TR_ERROR */
"Error",
/* TR_ERROR_WRITING_CONFIG */
"Error al escribir la configuración.",
/* TR_EURO_EDSS1 */
"Euro (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Extrayendo los módulos...",
/* TR_FAILED_TO_FIND */
"Falló al buscar la url del fichero.",
/* TR_FOUND_NIC */
"%s fue detectado en el siguiente NIC en tu máquina: %s",
/* TR_GERMAN_1TR6 */
"1TR6 Alemán",
/* TR_HELPLINE */
"           <Tab>/<Alt-Tab> entre elementos | <Space> para seleccionar",
/* TR_HOSTNAME */
"Nombre de ordenador",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"El nombre del host no puede quedar en blanco.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"El nombre de host no puede contener espacios.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"El nombre de host s o puede contener letras, números y guiones.",
/* TR_INITIALISING_ISDN */
"Instalando ISDN...",
/* TR_INSERT_CDROM */
"Introduce el controlador del CD %s en la unidad de CDROM.",
/* TR_INSERT_FLOPPY */
"Introduce el controlador de disco %s en la unidad de disco.",
/* TR_INSTALLATION_CANCELED */
"Instalanción cancelada",
/* TR_INSTALLING_FILES */
"Instalando los ficheros....",
/* TR_INSTALLING_GRUB */
"Instalando GRUB...",
/* TR_INTERFACE */
"%s interfaz",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"Falló el arranque de la interfase.",
/* TR_INVALID_FIELDS */
"Los siguientes campos son erroneos:\n\n",
/* TR_INVALID_IO */
"El puerto de IO introducido es erroneo",
/* TR_INVALID_IRQ */
"El IRQ introducido es erroneo",
/* TR_IP_ADDRESS_CR */
"Dirección IP\n",
/* TR_IP_ADDRESS_PROMPT */
"Dirección IP:",
/* TR_ISDN_CARD */
"Tarjeta de RDSI",
/* TR_ISDN_CARD_NOT_DETECTED */
"No se detecto ninguna tarjeta / modem ISDN. Puede que su tarjeta necesite parámetros adicionales para la carga del módulo. Algunas tarjetas ISA requieren que se indique IRQ y dirección I/O.",
/* TR_ISDN_CARD_SELECTION */
"Selecciona la targeta ISDN",
/* TR_ISDN_CONFIGURATION */
"Configuración RDSI",
/* TR_ISDN_CONFIGURATION_MENU */
"Menú de configuración de ISDN",
/* TR_ISDN_NOT_SETUP */
"No ha sido configurado ISDN.  Algunos items no fuerón seleccionados.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"La configuración de su ISDN aún no esta completa. Selecione el elemento que desea configurar.",
/* TR_ISDN_PROTOCOL_SELECTION */
"Selección del protocolo ISDN",
/* TR_ISDN_STATUS */
"Actualmente el ISDN es %s.\n\n Protocolo: %s\n Targeta: %s\n Número de teléfono local: %s\n\nSelecciona el items que desees configurar, o acepta las opciones actuales.",
/* TR_KEYBOARD_MAPPING */
"Mapa del teclado",
/* TR_KEYBOARD_MAPPING_LONG */
"Elija el tipo de teclado que está utilizando de la lista siguiente.",
/* TR_LEASED_LINE */
"Line renovada",
/* TR_LOADING_MODULE */
"Cargando el modulo...",
/* TR_LOADING_PCMCIA */
"Cargando el module PCMCIA...",
/* TR_LOOKING_FOR_NIC */
"Buscando: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Generando el fichero de arranque de sistema",
/* TR_MAKING_LOG_FILESYSTEM */
"Creando ficheros del sistema log...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Creando ficheros del sistema root...",
/* TR_MAKING_SWAPSPACE */
"Creando ficheros del sistema swap...",
/* TR_MANUAL */
"* MANUAL *",
/* TR_MAX_LEASE */
"Renovación máxima (min):",
/* TR_MAX_LEASE_CR */
"Tiempo máximo de renovación\n",
/* TR_MISSING_BLUE_IP */
"No se encuentra la información de IP para el interfaz AZUL.",
/* TR_MISSING_ORANGE_IP */
"Perdiendo la información en el interfaz ORANGE",
/* TR_MISSING_RED_IP */
"Perdiendo la información IP en el interfaz RED.",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"El nombre del módulo no puede quedar en blanco.",
/* TR_MODULE_PARAMETERS */
"Ingrese nombre y parámetros del modulo para el dispositivo requerido.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Montando el sistema de ficheros boot...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Montando el sistema de ficheros log...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Montando el sistema de ficheros root...",
/* TR_MOUNTING_SWAP_PARTITION */
"Montando el sistema de ficheros swap...",
/* TR_MSN_CONFIGURATION */
"Número de teléfono local (MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Máscara de subred",
/* TR_NETWORKING */
"Red",
/* TR_NETWORK_ADDRESS_CR */
"Dirección de red\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Dirección de red ",
/* TR_NETWORK_CONFIGURATION_MENU */
"Menu de configuración de red",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Tipo de Configuración de Red.",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Elija el tipo de configuración de red para %s. Los siguiente tipos de configuración estan disponibles para las interfases relacionadas a una ethernet. Si cambia alguna de estas configuraciones, la red se reiniciará y se deberán reasignar los controladores de red.",
/* TR_NETWORK_MASK_CR */
"Máscara de red\n",
/* TR_NETWORK_SETUP_FAILED */
"Las opciones de la red han fallado.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"Ninguna targeta localizada.",
/* TR_NO_BLUE_INTERFACE */
"No hay interfaz AZUL asignado.",
/* TR_NO_CDROM */
"No encuentro el CD-ROM",
/* TR_NO_HARDDISK */
"No encuentro el DISCO DURO",
/* TR_NO_IPCOP_TARBALL_FOUND */
"No hay fichero ipcop en el Servidor Web.",
/* TR_NO_ORANGE_INTERFACE */
"No hay interfases NARANJA asignadas.",
/* TR_NO_RED_INTERFACE */
"No hay interfase ROJA asignada.",
/* TR_NO_SCSI_IMAGE_FOUND */
"No se ha encontrado una imágen SCSI en el Servidor Web.",
/* TR_NO_UNALLOCATED_CARDS */
"Se necesitan más tarjetas y no quedan tarjetas sin localizar. Debe autodetectar y buscar mas tarjetas, o elejir alguna de la lista.",
/* TR_OK */
"OK",
/* TR_PARTITIONING_DISK */
"Dividiendo el disco....",
/* TR_PASSWORDS_DO_NOT_MATCH */
"La contraseñas ingresadas no conciden.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"La contraseña no puede dejarse vacia.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"La contraseña no puede contener espacios.",
/* TR_PASSWORD_PROMPT */
"Contraseña:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"El número de teléfono debe estar relleno.",
/* TR_PREPARE_HARDDISK */
"El programa de instalación preparará la unidad de disco %s. Primero se hará el particionado del disco y de inmediato se creará el sistema de ficheros.",
/* TR_PRESS_OK_TO_REBOOT */
"Pulsa Aceptar para reiniciar.",
/* TR_PRIMARY_DNS */
"DNS primario:",
/* TR_PRIMARY_DNS_CR */
"DNS primaria\n",
/* TR_PROBE */
"Prueba",
/* TR_PROBE_FAILED */
"Auto detectando fallos.",
/* TR_PROBING_SCSI */
"Prueba de dispositivos SCSI...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"Problemas al fijar la password de admin %s.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"Problemas al fijar la password de 'root'.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"Problemas al fijar la password de 'setup'.",
/* TR_PROTOCOL_COUNTRY */
"Protocolo / País",
/* TR_PULLING_NETWORK_UP */
"Arrancando la red...",
/* TR_PUSHING_NETWORK_DOWN */
"Apagando la red...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Apagando una red no local...",
/* TR_QUIT */
"Salir",
/* TR_RED_IN_USE */
"ISDN (u otra conexión externa) está actualmente en uso. No debes configurar el ISDN mientras el interfaz RED esté activo.",
/* TR_RESTART_REQUIRED */
"\n\nLa configuración ha sido completada, necesita reiniciar la red.",
/* TR_RESTORE */
"Restablecer",
/* TR_RESTORE_CONFIGURATION */
"Si tienes un disco con %s configuración de sistema, inserta el disco en la unidad y pulsa el botón Restaurar. ",
/* TR_ROOT_PASSWORD */
"Contraseña de usuario 'root'",
/* TR_SECONDARY_DNS */
"DNS secundario",
/* TR_SECONDARY_DNS_CR */
"DNS secundaria\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"Especificó un DNS secundario sin un DNS primario.",
/* TR_SECTION_MENU */
"Sección menu",
/* TR_SELECT */
"Selecciona",
/* TR_SELECT_CDROM_TYPE */
"Selecciona el tipo de CDROM",
/* TR_SELECT_CDROM_TYPE_LONG */
"No ha sido detectado ningún CDROM en la máquina. Selecciona cual de los siguientes controladores deseas utilizar para %s pueda acceder al CDROM.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Selecciona un medio para la instalación",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s puede ser instalado de diferentes modos. El más fácil es hacerlo desde el CDROM. Otro modo, es copiar los ficheros de instalación a otra máquina a la que se accederá via HTTP o FTP. En este caso deberá preparar disquetes para acceder a la red. ",
/* TR_SELECT_NETWORK_DRIVER */
"Selecciona un controlador de red.",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Elija el controlador de red para la terjeta instalada es esta máquina. Si elije MANUAL, podrá ingresar el nombre y parámetros del módulo para los controladores que así lo requieran, como es el caso de algunas tarjetas ISA.",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Selecciona el interfaz que deseas volver a configurar",
/* TR_SELECT_THE_ITEM */
"Selecciona el item que deseas configurar.",
/* TR_SETTING_ADMIN_PASSWORD */
"Asignando contraseña de admin para %s ...",
/* TR_SETTING_ROOT_PASSWORD */
"Asignando contraseña de \"root\"...",
/* TR_SETTING_SETUP_PASSWORD */
"Asignando contraseña de \"setup\"...",
/* TR_SETUP_FINISHED */
"La configuración esta completa. Presione Ok para reiniciar.",
/* TR_SETUP_NOT_COMPLETE */
"La configuración inicial no está completa. Debe asegugarse de finalizar completamente el Setup, ejecutándolo nuevamente desde la consola mediante el comando \"setup\".",
/* TR_SETUP_PASSWORD */
"Contraseña de usuario 'Setup'",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Configuración de parámetros adicionales para módulos.",
/* TR_SINGLE_GREEN */
"Su configuración actual consta de una única interfase VERDE.",
/* TR_SKIP */
"Saltar",
/* TR_START_ADDRESS */
"Dirección de inicio:",
/* TR_START_ADDRESS_CR */
"Dirección inicial\n",
/* TR_STATIC */
"Estático",
/* TR_SUGGEST_IO */
"(sugiere %x)",
/* TR_SUGGEST_IRQ */
"(sugiere %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"El módulo para ese controlador ya está cargado.",
/* TR_TIMEZONE */
"Zona horaria",
/* TR_TIMEZONE_LONG */
"Elige tu zona horaria en la que te encuentras de la siguiente lista.",
/* TR_UNABLE_TO_EJECT_CDROM */
"Incapaz de expulsar el CDROM.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Incapaz de extraer los módulos.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Incapaz de encontrar más controladores.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Incapaz de encontrar una tarjeta ISDN en esta máquina. Necesitas especificar parámetros adicionales en el módulo si la tarjeta es ISA o tiene parámetros especiales.",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"Incapaz de inicializar ISDN.",
/* TR_UNABLE_TO_INSTALL_FILES */
"Imposible instalar los ficheros.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"Incapaz de intalar GRUB.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Incapaz de cargar el modulo controlador.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Incapaz de crear el sistema de ficheros boot.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Incapaz de crear el sistema de ficheros log.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Incapaz de crear el sistema de ficheros root.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Incapaz de crear el espacio swap.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Incapaz de crear el enlace simbólico /dev/harddisk.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Incapaz de crear el enlace simbólico /dev/harddisk1.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Incapaz de crear el enlace simbólico /dev/harddisk2.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Incapaz de crear el enlace simbólico /dev/harddisk3.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Incapaz de crear el enlace simbólico /dev/harddisk4.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Incapaz de crear el enlace simbólico /dev/root",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Incapaz de montar el sistema de ficheros boot.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Incapaz de montar el sistema de ficheros log.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Incapaz de montar el sistema de ficheros proc",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Incapaz de montar el sistema de ficheros root.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Incapaz de montar el sistema de ficheros swap.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Imposible abrir el fichero 'hosts'",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Incapaz de abrir el fichero de configuración",
/* TR_UNABLE_TO_PARTITION */
"Desabilitada la partición del disco",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"No es posible eliminar ficheros temporales.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"No es posible asignar nombre al host.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"Dehabilitado el desmontaje de la unidad CDROM/floppydisk.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"Incapaz de desmontar el disco duro.",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"Incapaz de escribir en /etc/fstab",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"Incapaz de escribir en /etc/hostname.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"Incapaz de escribir en /etc/hosts.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"Incapaz de escribir en /etc/hosts.allow.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"Incapaz de escribir en /etc/hosts.deny.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"Incapaz de escribir en %s/ethernet/settings.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"Incapaz de escribir en %s/main/hostname.conf",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"Incapaz de escribir en %s/main/settings.",
/* TR_UNCLAIMED_DRIVER */
"Hay una tarjeta de red libre del tipo:\n%s.\n\nPuede asignarla a:",
/* TR_UNKNOWN */
"DESCONOCIDO",
/* TR_UNSET */
"No fijado.",
/* TR_USB_KEY_VFAT_ERR */
"This USB key is invalid (no vfat partition found).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"ADVERTENCIA",
/* TR_WARNING_LONG */
"Si modifica esta dirección IP mientras la usa en su sesión remota actual, la conexión con %s se perderá. Esta es una operación riesgosa, y sólo debe proceder si posee acceso físico a la máquina cuya configuración modifica.",
/* TR_WELCOME */
"Bienvenido al programa de intalación %s . Si seleccionas Cancelar en alguna de las siguientes pantallas se reseteará la máquina.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Su configuración actual consta de una única interfase VERDE, a la que ya se ha asignado un controlador.",
}; 
  
