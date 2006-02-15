/*
 * Latino-American Span (la) Data File
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
 * (c) 2003 Fernando D. Diaz Bottaro 
 */
 
#include "libsmooth.h"

char *la_tr[] = {

/* TR_ADDRESS_SETTINGS */
"Configuración de direcciones",
/* TR_ADMIN_PASSWORD */
"Contraseña de usuario Admin",
/* TR_AGAIN_PROMPT */
"Otra vez:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Todas la tarjetas se asignaron con éxito.",
/* TR_AUTODETECT */
"* AUTODETECTADO *",
/* TR_BUILDING_INITRD */
"Creando INITRD...",
/* TR_CANCEL */
"Cancelar",
/* TR_CARD_ASSIGNMENT */
"Asignación de tarjetas",
/* TR_CHECKING */
"Chequeando URL...",
/* TR_CHECKING_FOR */
"Verificando: %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Elija la tarjeta ISDN instalada en esta computadora.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Elija el protocolo ISDN requerido:",
/* TR_CONFIGURE_DHCP */
"Configure el servidor DHCP ingresando la información de configuración.",
/* TR_CONFIGURE_NETWORKING */
"Configuración de Red",
/* TR_CONFIGURE_NETWORKING_LONG */
"Ahora debe configurar la red cargando primero el controlador para su interface VERDE. Esto puede hacerse mediante autodetección de la tarjeta de red, o eligiendo el driver adecuado desde una lista disponible. Si tiene más de una tarjeta de red instalada, podrá configurar las restantes luego. Observe que si usted tiene más de una tarjeta que sea igual que la VERDE y cada tarjeta requiere parámetros especiales del módulo, se deben ingresar los parámetros para todas las tarjetas de este tipo, de modo que todas pueden ser activadas cuando se configura la interface VERDE.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Configure los controladores de red, y que tarjetas de red se asignarán a que interfaces. La configuración actual es la siguiente:",
/* TR_CONFIGURE_THE_CDROM */
"Configure el CDROM eligiendo la dirección E/S y el IRQ adecuado.",
/* TR_CONGRATULATIONS */
"¡Felicitaciones!",
/* TR_CONGRATULATIONS_LONG */
"%s ha sido instalado exitosamente. Por favor, quite el disquete o CD que pueda tener en su PC. Se iniciará el Programa de Instalación, en el podrá configurar ISDN, tarjetas de red, y contraseñas del sistema. Luego de finalizado el Programa de Instalación, podrá acceder con su navegador web a http://%s:81 o https://%s:445 (o el nombre que haya puesto a su %s), y configurar el acceso telefónico (si se requiere) y/o el acceso remoto. No olvide colocar una contraseña para el usuario 'dial' en su %s, si no desea que usuarios 'admin' puedan controlar el enlace.",
/* TR_CONTINUE_NO_SWAP */
"Su Disco Duro es demasiado chico, pero puede continuar sin Swap. (Use con precaución).",
/* TR_CURRENT_CONFIG */
"Configuración actual: %s%s",
/* TR_DEFAULT_GATEWAY */
"Pta. enlace o gateway predeterminado:",
/* TR_DEFAULT_GATEWAY_CR */
"Pta. enlace o gateway predeterminado\n",
/* TR_DEFAULT_LEASE */
"Concesión por defecto (min):",
/* TR_DEFAULT_LEASE_CR */
"Tiempo de concesión por defecto\n",
/* TR_DETECTED */
"Detectado un: %s",
/* TR_DHCP_HOSTNAME */
"Nombre del host DHCP:",
/* TR_DHCP_HOSTNAME_CR */
"Nombre del host DHCP\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"Configuración del servidor DHCP",
/* TR_DISABLED */
"Desactivado",
/* TR_DISABLE_ISDN */
"Desactivar RDSI (ISDN)",
/* TR_DISK_TOO_SMALL */
"Su disco duro es demasiado pequeño.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"Opciones de DNS y Gateway",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Ingrese la información de DNS y Puerta de Enlace. Estas serán usadas solamente si el DHCP no está habilitado en la interface ROJA.",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Su configuración no usa un adaptador ethernet para la interface ROJA. La información de DNS y Puerta de Enlace para el usuario de acceso telefónico se configura automaticamente en el momento de la conexión.",
/* TR_DOMAINNAME */
"Nombre de Dominio",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Nombre de Dominio no puede quedar en blanco.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"El Nombre de Dominio no puede contener espacios.",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Nombre de Dominio puede contener solo letras, números, guiones y puntos. ",
/* TR_DOMAIN_NAME_SUFFIX */
"Sufijo del nombre de dominio:",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Sufijo del nombre de dominio\n",
/* TR_DONE */
"Hecho",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\n¿Desea cambiar esta configuración?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Asignación de controladores y tarjetas",
/* TR_ENABLED */
"Activado",
/* TR_ENABLE_ISDN */
"Activar RDSI (ISDN)",
/* TR_END_ADDRESS */
"Dirección final:",
/* TR_END_ADDRESS_CR */
"Dirección final\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Algunas tarjetas ISDN (en particular las ISA) pueden necesitar parámetros adicionales para configurar el IRQ y la dirección de E/S. Si tiene alguna de estas tarjetas, ingrese aquí estos parámetros. Por ejemplo: &quot;io=0x280 irq=9&quot;. Esta información será utilizada durante la detección de la tarjeta.",
/* TR_ENTER_ADMIN_PASSWORD */
"Ingrese la contraseña para &quot;admin&quot; de %s. Este es el usuario que se usará para ingresar a las páginas web de administración de %s.",
/* TR_ENTER_DOMAINNAME */
"Ingrese Nombre de Dominio",
/* TR_ENTER_HOSTNAME */
"Ingrese el nombre de host para su máquina.",
/* TR_ENTER_IP_ADDRESS_INFO */
"Ingrese la información de la dirección IP.",
/* TR_ENTER_NETWORK_DRIVER */
"La detección automática de la tarjeta de red ha fallado. Introduzca el controlador y los parámetos opcionales para la tarjeta de red.",
/* TR_ENTER_ROOT_PASSWORD */
"Ingrese la contraseña para el usuario 'root'. Iniciando sesión con este usuario podrá acceder a la consola de comandos.",
/* TR_ENTER_SETUP_PASSWORD */
"Ingrese la contraseña para el usuario 'setup'. Iniciando sesión con este usuario podrá acceder al programa 'setup'.",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Ingrese la información de la dirección IP para la interface %s.",
/* TR_ENTER_THE_LOCAL_MSN */
"Ingrese el número de teléfono local (MSN/EAZ).",
/* TR_ENTER_URL */
"Ingrese la dirección URL para los archivos ipcop-<version>.tgz y images/scsidrv-<version>.img. ATENCIÓN: DNS no está disponible! La url debe ser solo del tipo http://x.x.x.x/<directorio>",
/* TR_ERROR */
"Error",
/* TR_ERROR_WRITING_CONFIG */
"Error al escribir la configuración.",
/* TR_EURO_EDSS1 */
"Euro (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Extrayendo los módulos...",
/* TR_FAILED_TO_FIND */
"No se ha encontrado el archivo en la URL.",
/* TR_FOUND_NIC */
"%s ha detectado la siguiente NIC en su máquina: %s",
/* TR_GERMAN_1TR6 */
"1TR6 Alemán",
/* TR_HELPLINE */
"           <Tab>/<Alt-Tab> entre elementos | <Space> para seleccionar",
/* TR_HOSTNAME */
"Nombre del Host",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"El nombre del host no puede quedar en blanco.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"El nombre del host no puede contener espacios.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"Nombre de Host solo puede contener letras, números y guiones.",
/* TR_INITIALISING_ISDN */
"Inicializando ISDN...",
/* TR_INSERT_CDROM */
"Por favor, introduzca el CD de %s en la unidad de CDROM.",
/* TR_INSERT_FLOPPY */
"Por favor, introduzca el disquete con el controlador de %s en la disquetera.",
/* TR_INSTALLATION_CANCELED */
"Instalación cancelada.",
/* TR_INSTALLING_FILES */
"Instalando los archivos...",
/* TR_INSTALLING_GRUB */
"Instalando GRUB...",
/* TR_INTERFACE */
"interface %s",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"La inicialización de la interface ha fallado.",
/* TR_INVALID_FIELDS */
"Los siguientes campos no son válidos:\n\n",
/* TR_INVALID_IO */
"La información del puerto de E/S ingresada no es válida.",
/* TR_INVALID_IRQ */
"El IRQ ingresado no es válido.",
/* TR_IP_ADDRESS_CR */
"Dirección IP\n",
/* TR_IP_ADDRESS_PROMPT */
"Dirección IP:",
/* TR_ISDN_CARD */
"Tarjeta RDSI (ISDN)",
/* TR_ISDN_CARD_NOT_DETECTED */
"No se ha detectado la tarjeta ISDN. Puede que necesite especificar parámetros adicionales (IRQ o puertos E/S) si la tarjeta es del tipo ISA o tiene requerimientos especiales.",
/* TR_ISDN_CARD_SELECTION */
"Selección de la tarjeta ISDN",
/* TR_ISDN_CONFIGURATION */
"Configuración ISDN",
/* TR_ISDN_CONFIGURATION_MENU */
"Menú de configuración de ISDN",
/* TR_ISDN_NOT_SETUP */
"No ha sido configurado ISDN.  Algunos items no fueron seleccionados.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"ISDN aún no esta configurado. Selecione el item que desea configurar.",
/* TR_ISDN_PROTOCOL_SELECTION */
"Selección del protocolo ISDN",
/* TR_ISDN_STATUS */
"Actualmente el ISDN es %s.\n\n Protocolo: %s\n Tarjeta: %s\n Número de teléfono local: %s\n\nSeleccione el item que desea volver a configurar, o elija usar la configuración actual.",
/* TR_KEYBOARD_MAPPING */
"Mapa del teclado",
/* TR_KEYBOARD_MAPPING_LONG */
"Elija el tipo de teclado que está utilizando de la lista siguiente.",
/* TR_LEASED_LINE */
"Línea renovada",
/* TR_LOADING_MODULE */
"Cargando el módulo...",
/* TR_LOADING_PCMCIA */
"Cargando módulos PCMCIA...",
/* TR_LOOKING_FOR_NIC */
"Buscando: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Creando el sistema de archivos 'boot'",
/* TR_MAKING_LOG_FILESYSTEM */
"Creando el sistema de archivos 'log'",
/* TR_MAKING_ROOT_FILESYSTEM */
"Creando el sistema de archivos 'root'",
/* TR_MAKING_SWAPSPACE */
"Creando el espacio de 'swap'",
/* TR_MANUAL */
"* MANUAL *",
/* TR_MAX_LEASE */
"Concesión máxima (min):",
/* TR_MAX_LEASE_CR */
"Tiempo máximo de concesión\n",
/* TR_MISSING_BLUE_IP */
"Información IP de la interface AZUL se perdió.",
/* TR_MISSING_ORANGE_IP */
"Perdiendo la IP de la interface NARANJA.",
/* TR_MISSING_RED_IP */
"Perdiendo la IP de la interface ROJA.",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"El nombre del módulo no puede quedar en blanco.",
/* TR_MODULE_PARAMETERS */
"Ingrese el nombre y los parámetros del modulo para el controlador requerido.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Montando el sistema de archivos boot...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Montando el sistema de archivos log...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Montando el sistema de archivos root...",
/* TR_MOUNTING_SWAP_PARTITION */
"Montando la partición swap...",
/* TR_MSN_CONFIGURATION */
"Número de teléfono local (MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Máscara de subred:",
/* TR_NETWORKING */
"Red",
/* TR_NETWORK_ADDRESS_CR */
"Dirección de red\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Dirección de red:",
/* TR_NETWORK_CONFIGURATION_MENU */
"Menú de configuración de red",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Tipo de configuración de red",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Seleccione el tipo de configuración de red para %s. Los tipos de configuraciones siguientes muestran aquellas interfaces que tienen una tarjeta ehternet asignada. Si cambia alguna de estas configuraciones, es necesario reiniciar la red, y habrá que reconfigurar las asignaciones del controlador de red.",
/* TR_NETWORK_MASK_CR */
"Máscara de red\n",
/* TR_NETWORK_SETUP_FAILED */
"La configuración de la red ha fallado.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"No se localizaron suficientes tarjetas.",
/* TR_NO_BLUE_INTERFACE */
"No se han asignado interface AZUL.",
/* TR_NO_CDROM */
"No se encontrado CD-ROMs.",
/* TR_NO_HARDDISK */
"No se ha encontrado Disco Duro.",
/* TR_NO_IPCOP_TARBALL_FOUND */
"No se ha encontrado un .tar.gz de Ipcop en el Servidor Web.",
/* TR_NO_ORANGE_INTERFACE */
"No hay ninguna interface NARANJA asignada.",
/* TR_NO_RED_INTERFACE */
"No hay ninguna interface ROJA asignada.",
/* TR_NO_SCSI_IMAGE_FOUND */
"No se ha encontrador una imágen SCSI en el Servidor Web.",
/* TR_NO_UNALLOCATED_CARDS */
"Se requieren más tarjetas y no quedan tarjetas detectadas. Puede usar 'autodetectar' o elejir seleccionar un controlador de la lista.",
/* TR_OK */
"Aceptar",
/* TR_PARTITIONING_DISK */
"Particionando el disco...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"Las contraseñas ingresadas no coinciden.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"La contraseña no puede dejarse en blanco.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"La contraseña no puede tener espacios.",
/* TR_PASSWORD_PROMPT */
"Contraseña:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Debe especificar un número de teléfono.",
/* TR_PREPARE_HARDDISK */
"El programa de instalación preparará ahora el disco duro %s. Primero se hará el particionado del disco y de inmediato se creará el sistema de archivos.",
/* TR_PRESS_OK_TO_REBOOT */
"Pulse Aceptar para reiniciar.",
/* TR_PRIMARY_DNS */
"DNS primario:",
/* TR_PRIMARY_DNS_CR */
"DNS primario\n",
/* TR_PROBE */
"Prueba",
/* TR_PROBE_FAILED */
"La autodetección ha fallado.",
/* TR_PROBING_SCSI */
"Detectando dispositivos SCSI...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"Problemas al asignar la contraseña del usuario admin de %s.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"Problemas al asignar la contraseña del usuario 'root'.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"Problemas al asignar la contraseña del usuario 'setup'.",
/* TR_PROTOCOL_COUNTRY */
"Protocolo/País",
/* TR_PULLING_NETWORK_UP */
"Iniciando la red...",
/* TR_PUSHING_NETWORK_DOWN */
"Apagando la red...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Apagando una red no local...",
/* TR_QUIT */
"Salir",
/* TR_RED_IN_USE */
"ISDN (u otra conexión externa) está actualmente en uso. No debe configurar el ISDN mientras la interface ROJA esté activa.",
/* TR_RESTART_REQUIRED */
"\n\nCuando la configuración se complete, necesitará reiniciar la red.",
/* TR_RESTORE */
"Restaurar",
/* TR_RESTORE_CONFIGURATION */
"Si tiene un disquete con la configuración de sistema %s, introduzca el disquete en la disquetera y pulse el botón Restaurar.",
/* TR_ROOT_PASSWORD */
"Contraseña del usuario 'root'",
/* TR_SECONDARY_DNS */
"DNS secundario:",
/* TR_SECONDARY_DNS_CR */
"DNS secundario\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"Especificó un DNS secundario sin un DNS primario.",
/* TR_SECTION_MENU */
"Sección menú",
/* TR_SELECT */
"Seleccionar",
/* TR_SELECT_CDROM_TYPE */
"Seleccione el tipo de CDROM",
/* TR_SELECT_CDROM_TYPE_LONG */
"No se ha detectado ningún CDROM en esta máquina. Por favor, seleccione cual de los siguientes controladores desea utilizar para que %s pueda acceder al CDROM.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Seleccione un medio para la instalación",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s puede ser instalado desde diferentes medios. Lo más fácil es instalarlo desde la unidad de CDROM. Si la computadora carece de una, puede hacer la instalación desde otra máquina en la LAN que tenga los archivos de instalación disponibles via HTTP o FTP. En este caso deberá preparar disquetes para acceder a la red. ",
/* TR_SELECT_NETWORK_DRIVER */
"Seleccionar controlador de red",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Elija el controlador de red para la terjeta instalada en esta máquina. Si elige MANUAL, tendrá la oportunidad de ingresar el nombre y los parámetros del módulo para los controladores que así lo requieran, como es el caso de algunas tarjetas ISA.",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Seleccione la interface que desea volver a configurar.",
/* TR_SELECT_THE_ITEM */
"Seleccione el item que desea configurar.",
/* TR_SETTING_ADMIN_PASSWORD */
"Asignando contraseña del usuario admin de %s ...",
/* TR_SETTING_ROOT_PASSWORD */
"Asignando contraseña del usuario 'root' ...",
/* TR_SETTING_SETUP_PASSWORD */
"Asignando contraseña del usuario 'setup' ...",
/* TR_SETUP_FINISHED */
"La configuración se ha completado. Presione Aceptar para reiniciar.",
/* TR_SETUP_NOT_COMPLETE */
"La configuración inicial no se ha completado. Debe asegugarse de que el programa de instalación finalice correctamente, ejecutándolo nuevamente desde la consola de comandos escribiendo 'setup'.",
/* TR_SETUP_PASSWORD */
"Contraseña del usuario 'setup'",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Configurar parámetros adicionales de módulos",
/* TR_SINGLE_GREEN */
"Su configuración actual consta de una única interface VERDE.",
/* TR_SKIP */
"Saltar",
/* TR_START_ADDRESS */
"Dirección de inicio:",
/* TR_START_ADDRESS_CR */
"Dirección de inicio\n",
/* TR_STATIC */
"Estático",
/* TR_SUGGEST_IO */
"(sugiere %x)",
/* TR_SUGGEST_IRQ */
"(sugiere %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"Este módulo de controlador ya está cargado.",
/* TR_TIMEZONE */
"Zona horaria",
/* TR_TIMEZONE_LONG */
"Elija la zona horaria en la que se encuentra de la siguiente lista.",
/* TR_UNABLE_TO_EJECT_CDROM */
"Incapaz de expulsar el CDROM.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Incapaz de extraer los módulos.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Incapaz de encontrar controladores adicionales.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Incapaz de encontrar una tarjeta ISDN en esta computadora. Debe especificar parámetros adicionales para el módulo si la tarjeta es del tipo ISA o si tiene requerimientos especiales.",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"Incapaz de inicializar ISDN.",
/* TR_UNABLE_TO_INSTALL_FILES */
"Imposible instalar los archivos.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"Incapaz de intalar GRUB.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Incapaz de cargar el modulo del controlador.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Incapaz de crear el sistema de archivos boot.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Incapaz de crear el sistema de archivos log.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Incapaz de crear el sistema de archivos root.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Incapaz de crear el espacio de swap.",
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
"Incapaz de montar el sistema de archivos boot.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Incapaz de montar el sistema de archivos log.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Incapaz de montar el sistema de archivos proc",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Incapaz de montar el sistema de archivos root.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Incapaz de montar la partición swap.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"No se puede abrir el archivo 'hosts' principal",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Incapaz de abrir el archivo de configuraciones",
/* TR_UNABLE_TO_PARTITION */
"Incapaz de particionar el disco.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"No es posible eliminar archivos temporales.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"No es posible asignar nombre al host.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"No se puede desmontar el CDROM/floppydisk.",
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
"Hay una tarjeta ethernet libre del tipo:\n%s\n\n Puede asignarla a:",
/* TR_UNKNOWN */
"DESCONOCIDO",
/* TR_UNSET */
"NO CONFIGURADO",
/* TR_USB_KEY_VFAT_ERR */
"This USB key is invalid (no vfat partition found).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"ADVERTENCIA",
/* TR_WARNING_LONG */
"Si cambia esta dirección IP, y está conectado remotamente, su conexión con la máquina %s se perderá, y tendrá que reconectarse con la nueva IP. Esta es una operación riesgosa, y sólo debe intentarse si posee acceso físico a la máquina cuya configuración modifica.",
/* TR_WELCOME */
"Bienvenido al programa de intalación %s. Seleccionando Cancelar en alguna de las siguientes pantallas se reiniciará la computadora.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Su configuración actual consta de una única interface VERDE, a la que ya se ha asignado un controlador.",
}; 
  
