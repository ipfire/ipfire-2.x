/*
 * Portuguese  (pt) Data File
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
 * (c) 2003 Luis Santos, Renato Kenji Kano, Mark Peter, Wladimir Nunes,
 * Daniela Cattarossi 
 */
 
#include "libsmooth.h"

char *pt_tr[] = {

/* TR_ADDRESS_SETTINGS */
"Configurações de endereço",
/* TR_ADMIN_PASSWORD */
"Palavra-passe do administrador",
/* TR_AGAIN_PROMPT */
"Novamente:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Todas as placas alocadas com sucesso.",
/* TR_AUTODETECT */
"* AUTO-DETECÇÃO *",
/* TR_BUILDING_INITRD */
"Construindo INITRD...",
/* TR_CANCEL */
"Cancela",
/* TR_CARD_ASSIGNMENT */
"Atribuição da placa",
/* TR_CHECKING */
"Verificando URL...",
/* TR_CHECKING_FOR */
"Procurando por: %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Escolha a placa RDIS instalada neste computador.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Escolha o protocolo RDIS requerido.",
/* TR_CONFIGURE_DHCP */
"Configure o servidor DHCP entrando com as informações.",
/* TR_CONFIGURE_NETWORKING */
"Configure a rede",
/* TR_CONFIGURE_NETWORKING_LONG */
"Você agora deve configurar a rede primeiro carregando o driver correto para a interface VERDE. Você pode fazer isso por teste automático da placa de rede ou escolhendo o driver correto da lista. Note que se houver mais de uma placa de rede do mesmo tipo como VERDE e cada placa precisar de parâmetros especiais do módulo, você deve entrar com estes parâmetros para todas as placas de modo que todas ativem-se quando você configurar a interface VERDE.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Configure os drivers de rede a a qual placa estes pertencem. A configuração actual é a seguinte:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"Configure o CD-ROM escolhendo o endereço de I/O e/ou o IRQ apropriados.",
/* TR_CONGRATULATIONS */
"Parabéns!",
/* TR_CONGRATULATIONS_LONG */
"%s foi instalado com sucesso. Por favor remova qualquer disquete ou CD-ROM deste computador. O programa de configuração será executado agora e permitirá que seja configurado RDIS, placas de rede e palavras-passe do sistema. Depois da configuração estar completa, você apontar seu web browser para http?//%s:81 ou https://%s:445 (ou seja lá como tiver nomeado seu %s), e configurar a marcação (se necessário) e acesso remoto. Lembre-se de definir a palavra-passe para o utilizador 'marcador' no %s, se você quiser que utilizador não administradores do %s possam controlar o link.",
/* TR_CONTINUE_NO_SWAP */
"Seu disco rígido é muito pequeno mas você pode continuar sem qualquer área de troca (swap). Use com cuidado.",
/* TR_CURRENT_CONFIG */
"Configuração atual:%s%s",
/* TR_DEFAULT_GATEWAY */
"Gateway Padrão:",
/* TR_DEFAULT_GATEWAY_CR */
"Gateway Padrão\n",
/* TR_DEFAULT_LEASE */
"Lease padrão (mins):",
/* TR_DEFAULT_LEASE_CR */
"Tempo de lease padrão\n",
/* TR_DETECTED */
"Detectado um: %s",
/* TR_DHCP_HOSTNAME */
"Hostname DHCP:",
/* TR_DHCP_HOSTNAME_CR */
"Hostname DHCP\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"Configuração do servidor DHCP",
/* TR_DISABLED */
"Desactivado",
/* TR_DISABLE_ISDN */
"Desactivar RDIS",
/* TR_DISK_TOO_SMALL */
"O seu disco duro é muito pequeno.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"Configurações de DNS e Gateway",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Entre os parâmetros de DNS e gateway. Este serão usados apenas se o DHCP estiver desactivado na interface VERMELHA.",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Sua configuração não utiliza um adaptador ethernet como sua interface VERMELHA. A informação de DNS e gateway para conexão discada é configurada automaticamente quando a discagem é completada.",
/* TR_DOMAINNAME */
"NomeDomínio",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"O Nome de Domínio não pode estar vazio.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"NomeDomínio não pode conter espaços.",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"O Nome de Domínio pode apenas conter letras, números, hífens e pontos.",
/* TR_DOMAIN_NAME_SUFFIX */
"Sufixo do domínio:",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Sufixo do domínio\n",
/* TR_DONE */
"Pronto",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\nVocê quer mudar estes parâmetros?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Atribuições de drivers e placas",
/* TR_ENABLED */
"Activado",
/* TR_ENABLE_ISDN */
"Activar RDIS",
/* TR_END_ADDRESS */
"Endereço final:",
/* TR_END_ADDRESS_CR */
"Endereço final\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Algumas placas RDIS (especialmente os ISA) podem requerer parâmetros adicionais do módulo para ajustes de IRQ e endereços de I/O. Se você tiver um destes cartões ISDN, entre estes parâmetros extras aqui. Por exemplo: \"io=0x280 irq=9\". Eles serão usados durante a detecção da placa.",
/* TR_ENTER_ADMIN_PASSWORD */
"Entre com a palavra-passe admin do %s. Este é o utilizador para entrar nas páginas web de administração do %s.",
/* TR_ENTER_DOMAINNAME */
"Introduza NomeDomínio",
/* TR_ENTER_HOSTNAME */
"Entre com o nome de anfitrião desta máquina.",
/* TR_ENTER_IP_ADDRESS_INFO */
"Entre com a informação do endereço IP",
/* TR_ENTER_NETWORK_DRIVER */
"A detecção automática da placa de rede falhou. Introduza o driver e parâmetros opcionais usados para esta placa de rede.",
/* TR_ENTER_ROOT_PASSWORD */
"Introduza a palavra-passe do utilizador 'root'. Entre com este utilizador para acesso via linha de comandos.",
/* TR_ENTER_SETUP_PASSWORD */
"Introduza a senha do utilizador 'setup'. Este é o utilizador que deve ser usado para aceder o programa de configuração.",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Introduza a informação do endereço IP para o interface %s.",
/* TR_ENTER_THE_LOCAL_MSN */
"Entre com o número de telefone local (MSN/EAZ).",
/* TR_ENTER_URL */
"Introduza o caminho URL para os ficheiros ipcop-<version>.tgz e images/scsidrv-<version>.img . ATENÇÃO: DNS não disponível! Deve ser apenas http://X.X.X.X/<directory>",
/* TR_ERROR */
"Erro",
/* TR_ERROR_WRITING_CONFIG */
"Erro gravando a configuração.",
/* TR_EURO_EDSS1 */
"Euro (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Extraindo módulos...",
/* TR_FAILED_TO_FIND */
"Falhou a procura de ficheiro URL.",
/* TR_FOUND_NIC */
"%s detectou o seguinte NIC em sua máquina: %s",
/* TR_GERMAN_1TR6 */
"1TR6 Alemão",
/* TR_HELPLINE */
"            <Tab>/<Alt-Tab> entre elementos  |  <Espaço> seleciona",
/* TR_HOSTNAME */
"Nome de Anfitrião",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Nome do anfitrião não pode ficar vazio.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"Nome do anfitrião não pode conter espaços.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"O Hostname só pode conter letras, números e hífens.",
/* TR_INITIALISING_ISDN */
"Iniciando RDIS...",
/* TR_INSERT_CDROM */
"Por Favor insira o %s CD na drive de CDROM",
/* TR_INSERT_FLOPPY */
"Por favor, insira o disquete com o driver %s.",
/* TR_INSTALLATION_CANCELED */
"Instalação cancelada.",
/* TR_INSTALLING_FILES */
"Instalando arquivos...",
/* TR_INSTALLING_GRUB */
"Instalando GRUB...",
/* TR_INTERFACE */
"Interface %s",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"Não consegui levantar o interface.",
/* TR_INVALID_FIELDS */
"Os seguintes campos são inválidos:\n\n",
/* TR_INVALID_IO */
"A porta de I/O fornecida é inválida.",
/* TR_INVALID_IRQ */
"O IRQ fornecido é inválido.",
/* TR_IP_ADDRESS_CR */
"Endereço de IP\n",
/* TR_IP_ADDRESS_PROMPT */
"Endereço de IP:",
/* TR_ISDN_CARD */
"Placa RDIS",
/* TR_ISDN_CARD_NOT_DETECTED */
"Placa Rdis não detectado. Você pode precisar especificar parâmetros adicionais se a placa for ISA ou tiver necessidades especiais.",
/* TR_ISDN_CARD_SELECTION */
"Selecção da placa RDIS",
/* TR_ISDN_CONFIGURATION */
"Configuração da RDIS.",
/* TR_ISDN_CONFIGURATION_MENU */
"Menu de configuração da RDIS",
/* TR_ISDN_NOT_SETUP */
"RDIS não configurada. Parece que alguns parâmetros não foram selecionados.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"RDIS não configurada ainda. Selecione o ítem que deseja configurar.",
/* TR_ISDN_PROTOCOL_SELECTION */
"Seleção de protocolo RDIS.",
/* TR_ISDN_STATUS */
"RDIS actual é %s.\n\n Protocolo: %s\n Placa: %s\n Telefone local: %s\n\nSelecione o item que deseja configurar ou escolha usar os valores correntes.",
/* TR_KEYBOARD_MAPPING */
"Mapeamento de teclado",
/* TR_KEYBOARD_MAPPING_LONG */
"Escolha o tipo de teclado que está a usar da lista abaixo.",
/* TR_LEASED_LINE */
"Linha alugada",
/* TR_LOADING_MODULE */
"Carregando módulo...",
/* TR_LOADING_PCMCIA */
"Carregando módulos PCMCIA...",
/* TR_LOOKING_FOR_NIC */
"Procurando por: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Criando sistema de arquivos de boot...",
/* TR_MAKING_LOG_FILESYSTEM */
"Criando sistema de arquivos de registro...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Criando sistema de arquivos raiz...",
/* TR_MAKING_SWAPSPACE */
"Criando espaço de troca...",
/* TR_MANUAL */
"* MANUAL *",
/* TR_MAX_LEASE */
"Lease max. (mins):",
/* TR_MAX_LEASE_CR */
"Tempo max. de lease\n",
/* TR_MISSING_BLUE_IP */
"Falta informação IP do interface Azul.",
/* TR_MISSING_ORANGE_IP */
"Falta informação do IP da interface LARANJA.",
/* TR_MISSING_RED_IP */
"Falta informação IP da interface VERMELHA.",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"Nome do módulo não pode estar vazio.",
/* TR_MODULE_PARAMETERS */
"Introduza o nome do módulo e os parâmetros para o driver que você quer usar.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Montando o sistema de arquivos boot...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Montando o sistema de arquivos log...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Montando o sistema de arquivos raiz...",
/* TR_MOUNTING_SWAP_PARTITION */
"Montando partição de troca...",
/* TR_MSN_CONFIGURATION */
"Número de telefone local (MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Máscara de rede:",
/* TR_NETWORKING */
"Rede",
/* TR_NETWORK_ADDRESS_CR */
"Endereço de rede\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Endereço de rede:",
/* TR_NETWORK_CONFIGURATION_MENU */
"Menu de configuração de rede",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Tipo de configuração de rede",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Seleccione a configuração de rede para %s. Os tipos de configuração seguintes listam quais interfaces tem ethernet conectada. Se você mudar esta configuração, uma reinicialização da rede será necessária e você terá que reconfigurar os drivers de rede alocados.",
/* TR_NETWORK_MASK_CR */
"Máscara de rede\n",
/* TR_NETWORK_SETUP_FAILED */
"Configuração de rede falhou.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"Não foram alocados cartões suficientes.",
/* TR_NO_BLUE_INTERFACE */
"Não está atribuido nenhum interface Azul.",
/* TR_NO_CDROM */
"Não foi encontrado nenhum CD-ROM",
/* TR_NO_HARDDISK */
"Nenhum disco duro encontrado.",
/* TR_NO_IPCOP_TARBALL_FOUND */
"Não foi encontrado o tarball no Servidor Web.",
/* TR_NO_ORANGE_INTERFACE */
"Nenhuma interface LARANJA atribuida.",
/* TR_NO_RED_INTERFACE */
"Nenhuma interface VERMELHA atribuida.",
/* TR_NO_SCSI_IMAGE_FOUND */
"Não foi encontrada imagem SCSI no Servidor Web.",
/* TR_NO_UNALLOCATED_CARDS */
"Nenhuma placa livre encontrada, são necessárias mais. Você pode escolher usar a auto-detecção para procurar por mais placas ou escolher um driver da lista.",
/* TR_OK */
"Ok",
/* TR_PARTITIONING_DISK */
"A criar partições...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"As palavras-passe não coincidem.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"A palavra-passe não pode ficar em branco.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"A Palavra passe não pode conte espaços.",
/* TR_PASSWORD_PROMPT */
"Palavra-passe:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Número do telefone não pode ser vazio.",
/* TR_PREPARE_HARDDISK */
"O programa de instalação preparará agora o disco duro em %s. Primeiramente o disco será particionado e então as partições terão um sistema de arquivos colocado nas mesmas.",
/* TR_PRESS_OK_TO_REBOOT */
"Pressione OK para reiniciar.",
/* TR_PRIMARY_DNS */
"DNS Primário:",
/* TR_PRIMARY_DNS_CR */
"DNS primário\n",
/* TR_PROBE */
"Teste",
/* TR_PROBE_FAILED */
"Auto detecção falhou.",
/* TR_PROBING_SCSI */
"Analisando dispositivos SCSI...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"Problema ao definir a palavra-passe admin do %s.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"Problema ao definir a palavra-passe 'root' do %s.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"Problema em definir a palavra-passe 'setup' do %s.",
/* TR_PROTOCOL_COUNTRY */
"Protocolo/País",
/* TR_PULLING_NETWORK_UP */
"Erguendo a rede...",
/* TR_PUSHING_NETWORK_DOWN */
"Derrubando a rede...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Derrubando a rede não local...",
/* TR_QUIT */
"Sair",
/* TR_RED_IN_USE */
"A RDIS (ou outra conexão externa) em uso. Não se pode configurar a RDIS enquanto a interface VERMELHA estiver ativa.",
/* TR_RESTART_REQUIRED */
"\n\nQuando a configuração estiver completa, uma reinicialização da rede será requerida.",
/* TR_RESTORE */
"Recuperar",
/* TR_RESTORE_CONFIGURATION */
"Se você tiver um disquete com a configuração do %s, coloque-o no drive e acione o botão Restore.",
/* TR_ROOT_PASSWORD */
"palavra-passe \"root\"",
/* TR_SECONDARY_DNS */
"DNS secundário:",
/* TR_SECONDARY_DNS_CR */
"DNS secundário\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"DNS secundário especificado sem um DNS primário",
/* TR_SECTION_MENU */
"Menu de selecção",
/* TR_SELECT */
"Seleccione",
/* TR_SELECT_CDROM_TYPE */
"Seleccione o tipo do CD-ROM",
/* TR_SELECT_CDROM_TYPE_LONG */
"Nenhum CD-ROM foi detectado nesta máquina. Por favor, selecione qual dos seguintes drivers você quer usar para que %s possa aceder ao CD-ROM.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Selecione o suporte da instalação",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s pode ser instalado de multiplas fontes. A mais simples é usar o CD-ROM da máquina. Se o computador não tiver um, você pode instalar via outra máquina na rede que tenha os arquivos de instalação disponíveis via HTTP. Neste caso um disquete com os drivers de rede serão necessários.",
/* TR_SELECT_NETWORK_DRIVER */
"Selecione o controlador de rede",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Selecione o driver para a placa de rede que está instalada nesta máquina. Se você selecionar MANUAL, lhe será dada a oprtunidade de entrar com o nome do módulo e parâmetros para drivers que tiverem necessidades especiais como para placas ISA.",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Selecione a interface que deseja reconfigurar.",
/* TR_SELECT_THE_ITEM */
"Selecione o ítem que deseja configurar.",
/* TR_SETTING_ADMIN_PASSWORD */
"Definindo a palavra passe do admin de %s...",
/* TR_SETTING_ROOT_PASSWORD */
"Definindo a palavra-passe do root...",
/* TR_SETTING_SETUP_PASSWORD */
"Definindo a palavra do 'setup'...",
/* TR_SETUP_FINISHED */
"Configuração terminada. Pressione OK para reiniciar.",
/* TR_SETUP_NOT_COMPLETE */
"A configuração inicial não foi inteiramente terminada. Você deve assegurar-se que a instalação seja finalizada corretamente, executando de novo a configuração no terminal.",
/* TR_SETUP_PASSWORD */
"Palavra-passe do setup",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Ajuste os parâmetros adicionais do módulo.",
/* TR_SINGLE_GREEN */
"A sua configuração está definida para uma interface VERDE apenas.",
/* TR_SKIP */
"Saltar",
/* TR_START_ADDRESS */
"Endereço inicial:",
/* TR_START_ADDRESS_CR */
"Endereço inicial\n",
/* TR_STATIC */
"Estático",
/* TR_SUGGEST_IO */
"(sugestão %x)",
/* TR_SUGGEST_IRQ */
"(sugestão %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"Este módulo já está carregado.",
/* TR_TIMEZONE */
"Fuso horário",
/* TR_TIMEZONE_LONG */
"Escolha o fuso horário em que você se encontra da lista abaixo.",
/* TR_UNABLE_TO_EJECT_CDROM */
"Não foi possível ejectar o CD-ROM.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Não foi possível extrair os módulos.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Não foi possível encontrar nenhum driver adicional.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Não foi possível encontrar uma placa RDIS. Pode ser necessário especificar parâmetros adicionais para o módulo se a placa for tipo ISA ou tiver características especiais.",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"Incapaz de inicializar RDIS",
/* TR_UNABLE_TO_INSTALL_FILES */
"Impossível instalar arquivos.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"Não foi possível instalar GRUB.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Não foi possível carregar o módulo do driver.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Impossibilitado de criar arquivos de boot.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Não foi possível criar o sistema de arquivos de registro.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Não foi possível criar o sistema de arquivos raiz.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Não foi possível criar o espaço de troca.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Incapaz de criar a ligação simbólica /dev/harddisk",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Incapaz de criar a ligação simbólica /dev/harddisk1.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Incapaz de criar a ligação simbólica /dev/harddisk.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Incapaz de criar a ligação simbólica /dev/harddisk3.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Incapaz de criar a ligação simbólica /dev/harddisk4.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Incapaz de criar a ligação simbólica /dev/root.",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Não foi possível montar o sistema de arquivos boot.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Não foi possível montar o sistema de arquivos de registro.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Não foi possível montar o sistema de arquivos proc.",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Não foi possível montar o sistema de arquivos raiz.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Não foi possível montar a partição de troca.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Incapaz de abrir ficheiro principal de hosts.",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Não foi possível abrir o arquivo de configuração.",
/* TR_UNABLE_TO_PARTITION */
"Não foi possível particionar o disco.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"Não foi possível remover os arquivos temporários.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"Não foi possível ajustar o nome do host.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"Não foi possível desmontar o CD-ROM/disquete.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"Não foi possível desmontar o disco rígido.",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"Não foi possível gravar /etc/fstab",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"Não foi possível gravar /etc/hostname",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"Não foi possível gravar /etc/hosts",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"Não foi possível gravar /etc/hosts.allow.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"Não foi possível gravar /etc/hosts.deny.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"Não foi possível gravar %s/ethernet/settings.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"Não foi possível gravar %s/main/hostname.conf",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"Não foi possível gravar %s/main/settings.",
/* TR_UNCLAIMED_DRIVER */
"Há um cartão ethernet não relacionado do tipo:\n%s\n\nVocê pode relaciona-lo a:",
/* TR_UNKNOWN */
"DESCONHECIDO",
/* TR_UNSET */
"UNSET",
/* TR_USB_KEY_VFAT_ERR */
"This USB key is invalid (no vfat partition found).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"ATENÇÃO",
/* TR_WARNING_LONG */
"Se você mudar este endereço IP e estiver conectado remotamente, sua conexão à máquina %s será interrompida e você tera que se reconectar no novo IP. Esta é uma operação arriscada e deve ser tentada apenas se você tiver acesso físico à maquina para o casod e algo sair errado.",
/* TR_WELCOME */
"Bem-vindo ao programa de instalação do %s. Ao cancelar em qualquer das próximas etapas o computador será reinicializado.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"A sua configuração consta de uma interface VERDE, que já tem um driver atribuído.",
}; 
  
