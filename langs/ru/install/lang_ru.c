/*
 * Russian (ru) Data File
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
 * along with IPCop; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
 * 
 * (c) IPFire Team  <info@ipfire.org>
 *
 */
#include "libsmooth.h"

char *ru_tr[] = {
/* TR_ISDN */
"ISDN",
/* TR_ERROR_PROBING_ISDN */
"Невозможно просканировать ISDN устройства.",
/* TR_PROBING_ISDN */
"ISDN устройства сканируются и настраиваются.",
/* TR_MISSING_GREEN_IP */
"Не найден Green IP!",
/* TR_CHOOSE_FILESYSTEM */
"Пожалуйста укажите вашу файловую систему:",
/* TR_NOT_ENOUGH_INTERFACES */
"Недостаточно сетевых карт для Вашего выбора.\n\nНеобходимо: %d - Доступно: %d\n",
/* TR_INTERFACE_CHANGE */
"Пожалуйста укажите интерфейс, который хотите изменить.\n\n",
/* TR_NETCARD_COLOR */
"Назначенные карты",
/* TR_REMOVE */
"Удалить",
/* TR_MISSING_DNS */
"Не найден DNS.\n",
/* TR_MISSING_DEFAULT */
"Не найден шлюз.\n",
/* TR_JOURNAL_EXT3 */
"Создаются журналы для Ext3...",
/* TR_CHOOSE_NETCARD */
"Пожалуйста укажите сетевую карту для следующего интерфейса - %s.",
/* TR_NETCARDMENU2 */
"Расширенное сетевое меню",
/* TR_ERROR_INTERFACES */
"В Вашей системе нет свободных интерфейсов.",
/* TR_REMOVE_CARD */
"Удалить сетевую карту? - %s",
/* TR_JOURNAL_ERROR */
"Не получилось создать журнал, пробуем ext2.",
/* TR_FILESYSTEM */
"Укажите файловую систему",
/* TR_ADDRESS_SETTINGS */
"Настройки адреса",
/* TR_ADMIN_PASSWORD */
"Пароль 'admin'",
/* TR_AGAIN_PROMPT */
"Ещё раз:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Все карты успешно установлены.",
/* TR_AUTODETECT */
"* АВТООПРЕДЕЛЕНИЕ *",
/* TR_BUILDING_INITRD */
"Создаётся ramdisk...",
/* TR_CANCEL */
"Отмена",
/* TR_CARD_ASSIGNMENT */
"Установка карт",
/* TR_CHECKING */
"Проверяется URL...",
/* TR_CHECKING_FOR */
"Проверка для: %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Укажите ISDN карту, установленную в этом компьютере.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Укажите необходимый ISDN протокол.",
/* TR_CONFIGURE_DHCP */
"Введите необходимые настройки DHCP сервера.",
/* TR_CONFIGURE_NETWORKING */
"Настройка сети",
/* TR_CONFIGURE_NETWORKING_LONG */
"Необходимо настроить сеть, загрузив драйвер для  GREEN интерфейса. Вы можете воспользоваться автоподбором драйвера для сетевой карты или самостоятельно указать его из списка. Позже Вы сможете подобрать драйвер и для остальных сетевых карт. Также, если у Вас более одной карты такого же типа, как для GREEN интерфейса, и каждая требует особых параметров, то Вам следует указать эти параметры, чтобы все карты были активны во время настройки GREEN интерфейса.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Назначьте драйверы интерфейсам. Текущая конфигурация следующая:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"Для настройки CDROM необходимо указать его IO адрес и/или IRQ.",
/* TR_CONGRATULATIONS */
"Поздравляем!",
/* TR_CONGRATULATIONS_LONG */
"%s был успешно установлен. Пожалуйста достаньте CD диск из привода. Далее будет предложена настройка ISDN, сетевых карт, и системных паролей. После окончания установки появится возможность настройки сервера с помощью браузера через веб-интерфейс по адресу https://%s:444 (или по имени, которое Вы указали для %s), где будет предложена настройка dialup подключения (если требуется) и удалённого доступа.",
/* TR_CONTINUE_NO_SWAP */
"Ваш жёсткий диск слишком мал, но установка всё же возможна с очень маленьким разделом swap. (Будьте внимательны).",
/* TR_CURRENT_CONFIG */
"Текущая конфигурация: %s%s",
/* TR_DEFAULT_GATEWAY */
"Основной шлюз:",
/* TR_DEFAULT_GATEWAY_CR */
"Основной шлюз\n",
/* TR_DEFAULT_LEASE */
"Аренда по умолчанию (в минутах):",
/* TR_DEFAULT_LEASE_CR */
"Время аренды по умолчанию\n",
/* TR_DETECTED */
"Обнаружен: %s",
/* TR_DHCP_HOSTNAME */
"Имя хоста DHCP:",
/* TR_DHCP_HOSTNAME_CR */
"Имя хоста DHCP\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"Настройка DHCP сервера",
/* TR_DISABLED */
"Выключен",
/* TR_DISABLE_ISDN */
"Выключить ISDN",
/* TR_DISK_TOO_SMALL */
"Ваш жёсткий диск слишком мал.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"Настройка DNS и шлюза",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Введите DNS шлюз.  Эти настройки используются только со статическим IP (и DHCP если указан DNS) на RED интерфейсе.",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Ваши настройки не используются ethernet адаптером для  RED интерфейса.  Информация о DNS и шлюзе для пользователей dialup получается автоматически при подключении.",
/* TR_DOMAINNAME */
"Имя домена",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Имя домена не может быть пустым.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"В имени домена не должно быть пробелов.",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Имя домена может содержать только буквы, цифры, дефисы и нижние подчёркивания.",
/* TR_DOMAIN_NAME_SUFFIX */
"Префикс доменного имени:",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Префикс доменного имени\n",
/* TR_DONE */
"Готово",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\nХотите поменять эти настройки?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Назначение драйверов и карт",
/* TR_ENABLED */
"Включено",
/* TR_ENABLE_ISDN */
"Включить ISDN",
/* TR_END_ADDRESS */
"Конечный адрес:",
/* TR_END_ADDRESS_CR */
"Конечный адрес\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Некоторые ISDN карты (особенно ISA) Могут потребовать дополнительных параметров для задания IRQ и IO адреса. Если у Вас такая  ISDN карта, введите эти параметры тут. Пример: \"io=0x280 irq=9\". Эти параметры будут использоваться во время определения карты.",
/* TR_ENTER_ADMIN_PASSWORD */
"Введите %s 'admin' пароль.  Эта учётная запись используется для входа на веб интерфейс %s.",
/* TR_ENTER_DOMAINNAME */
"Введите имя домена",
/* TR_ENTER_HOSTNAME */
"Введите имя хоста.",
/* TR_ENTER_IP_ADDRESS_INFO */
"введите IP адрес",
/* TR_ENTER_NETWORK_DRIVER */
"Не удалось автоматически определить сетевую карту. Введите дополнительные параметры для этой сетевой карты.",
/* TR_ENTER_ROOT_PASSWORD */
"Введите пароль для 'root'. Эта учётная запись используется для доступа с командной строки.",
/* TR_ENTER_SETUP_PASSWORD */
"БУДЕТ УДАЛЁН",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Введите IP адрес для %s интерфейса.",
/* TR_ENTER_THE_LOCAL_MSN */
"Введите номер телефона (MSN/EAZ).",
/* TR_ENTER_URL */
"Укажите URL к ipcop-<version>.tgz и images/scsidrv-<version>.img файлам. ВНИМАНИЕ: DNS не работает! Пример: http://X.X.X.X/<directory>",
/* TR_ERROR */
"Ошибка",
/* TR_ERROR_PROBING_CDROM */
"Не найден привод CDROM.",
/* TR_ERROR_WRITING_CONFIG */
"Ошибка записи настроек.",
/* TR_EURO_EDSS1 */
"Евро (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Модули извлекаются...",
/* TR_FAILED_TO_FIND */
"Не удалось найти файл по этому URL.",
/* TR_FOUND_NIC */
"%s обнаружил следующий NIC в Вашем компьютере: %s",
/* TR_GERMAN_1TR6 */
"German 1TR6",
/* TR_HELPLINE */
"              <Tab>/<Alt-Tab> Переключает   |  <Space> Выделяет",
/* TR_HOSTNAME */
"Имя хоста",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Имя хоста не может быть пустым.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"Имя хоста не может содержать пробелы.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"В имени хоста могут быть только буквы, цифры дефисы.",
/* TR_INITIALISING_ISDN */
"Устанавливается ISDN...",
/* TR_INSERT_CDROM */
"Пожалуйста вставьте %s CD в привод CDROM.",
/* TR_INSERT_FLOPPY */
"Пожалуйста вставьте %s дискету с драйверами в привод floppy.",
/* TR_INSTALLATION_CANCELED */
"Установка отменена.",
/* TR_INSTALLING_FILES */
"Устанавливаются файлы...",
/* TR_INSTALLING_GRUB */
"Устанавливается GRUB...",
/* TR_INSTALLING_LANG_CACHE */
"Устанавливаются языковые пакеты...",
/* TR_INTERFACE */
"Интерфейс - %s",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"Не удалось поднять интерфейс.",
/* TR_INVALID_FIELDS */
"В следующих полях есть ошибки:\n\n",
/* TR_INVALID_IO */
"Параметры IO порта содержат ошибки. ",
/* TR_INVALID_IRQ */
"Параметры IRQ details содержат ошибки.",
/* TR_IP_ADDRESS_CR */
"IP адрес\n",
/* TR_IP_ADDRESS_PROMPT */
"IP адреса:",
/* TR_ISDN_CARD */
"ISDN карта",
/* TR_ISDN_CARD_NOT_DETECTED */
"ISDN карта не найдена. Возможно стоит указать дополнительные параметры модулю, если у вас карта типа ISA или имеет особые параметры.",
/* TR_ISDN_CARD_SELECTION */
"выбор ISDN карты",
/* TR_ISDN_CONFIGURATION */
"Настройка ISDN",
/* TR_ISDN_CONFIGURATION_MENU */
"Меню настройки ISDN",
/* TR_ISDN_NOT_SETUP */
"ISDN не настроена. Некоторые элементы не были указаны.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"ISDN ещё не настроена. Укажите элемент, который хотите настроить.",
/* TR_ISDN_PROTOCOL_SELECTION */
"выбор ISDN протокола",
/* TR_ISDN_STATUS */
"ISDN сейчас %s.\n\n   Протокол: %s\n   Карта: %s\n   Телефон: %s\n\nУкажите элемент для перенастройки, или сохраните текущие настройки.",
/* TR_KEYBOARD_MAPPING */
"Раскладка клавиатуры",
/* TR_KEYBOARD_MAPPING_LONG */
"Укажите тип используемой клавиатуры из списка ниже. (обычно подходит ru_win )",
/* TR_LEASED_LINE */
"Зарезервированная строка",
/* TR_LOADING_MODULE */
"Грузится модуль...",
/* TR_LOADING_PCMCIA */
"Грузятся PCMCIA модули...",
/* TR_LOOKING_FOR_NIC */
"Поиск: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Создаётся файловой системы загрузчика...",
/* TR_MAKING_LOG_FILESYSTEM */
"Создаётся файловая система под логи...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Создаётся корневая файловая система...",
/* TR_MAKING_SWAPSPACE */
"Создаётся swap...",
/* TR_MANUAL */
"* MANUAL *",
/* TR_MAX_LEASE */
"Max аренда (минуты):",
/* TR_MAX_LEASE_CR */
"Время Max аренды\n",
/* TR_MISSING_BLUE_IP */
"Не указан IP на BLUE интерфейсе.",
/* TR_MISSING_ORANGE_IP */
"Не указан IP на ORANGE интерфейсе.",
/* TR_MISSING_RED_IP */
"Не указан IP на RED интерфейсе.",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"Имя модуля не может быть пустым.",
/* TR_MODULE_PARAMETERS */
"Введите имя модуля и параметры для нужного драйвера.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Монтируется файловая система для загрузчика...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Монтируется файловая система для логов...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Монтируется корневая файловая система...",
/* TR_MOUNTING_SWAP_PARTITION */
"Монтируется swap...",
/* TR_MSN_CONFIGURATION */
"Номер телефона (MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Маска подсети:",
/* TR_NETWORKING */
"Сеть",
/* TR_NETWORK_ADDRESS_CR */
"Сетевой адрес\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Сетевой адрес:",
/* TR_NETWORK_CONFIGURATION_MENU */
"Меню настройки сети",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Настройка типа сетевого подключения",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Укажите сетевые настройки для %s.  Ниже представлен список для интернет подключения. Если Вы решите поменять эти настройки,Потребуется перезапуск сети, а так же потребуется переназначить драйвера сетевых карт.",
/* TR_NETWORK_MASK_CR */
"Маска подсети\n",
/* TR_NETWORK_SETUP_FAILED */
"Не удалось настроить сеть.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"Выделено недостаточно сетевых карт.",
/* TR_NO_BLUE_INTERFACE */
"Не назначен BLUE интерфейс.",
/* TR_NO_CDROM */
"Не найден CD-ROM.",
/* TR_NO_GREEN_INTERFACE */
"Не назначен  GREEN интерфейс.",
/* TR_NO_HARDDISK */
"Не найден жсткий диск.",
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
/* TR_NO_IPCOP_TARBALL_FOUND */
"На сервере не найден архив ipcop.",
/* TR_NO_ORANGE_INTERFACE */
"Не назначен ORANGE интерфейс.",
/* TR_NO_RED_INTERFACE */
"Не назначен RED интерфейс.",
/* TR_NO_SCSI_IMAGE_FOUND */
"По этому адресу не найден образ SCSI.",
/* TR_NO_UNALLOCATED_CARDS */
"Нужно больше карт. Можно попытаться поискать или указать другие карты на этой машине, или указать драйвер из списка ниже.",
/* TR_OK */
"Ok",
/* TR_PARTITIONING_DISK */
"Разбивка диска...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"Пароли не совпадают.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"Пароль не может быть пустым.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"Пароль не должен содержать пробелы.",
/* TR_PASSWORD_PROMPT */
"Пароль:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Номер телефона не может быть пустым.",
/* TR_PREPARE_HARDDISK */
"Мастер установки сейчас подготовит диски на %s. Сперва будет проводиться разбиение диска, а затем разделам будут назначены файловые системы.",
/* TR_PRESS_OK_TO_REBOOT */
"Нажмите Ok для перезагрузки.",
/* TR_PRIMARY_DNS */
"Основной DNS:",
/* TR_PRIMARY_DNS_CR */
"Основной DNS\n",
/* TR_PROBE */
"Пробовать",
/* TR_PROBE_FAILED */
"Не удалось определить автоматически.",
/* TR_PROBING_HARDWARE */
"Определение железа...",
/* TR_PROBING_FOR_NICS */
"Определение NIC...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"Возникли проблемы при установке на %s пароля для 'admin'.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"Возникли проблемы при установке пароля для 'root'.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"БУДЕТ УДАЛЁН",
/* TR_PROTOCOL_COUNTRY */
"Протокол/Страна",
/* TR_PULLING_NETWORK_UP */
"Поднимаем сеть...",
/* TR_PUSHING_NETWORK_DOWN */
"Отключаем сеть...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Отключаем нелокальную сеть...",
/* TR_QUIT */
"Выход",
/* TR_RED_IN_USE */
"ISDN (или другое внешнее подключение) задействовано в данный момент.  Не получится настроить ISDN пока RED интерфейс активен.",
/* TR_RESTART_REQUIRED */
"\n\nПосле настройки потребуется перезапуск сети.",
/* TR_RESTORE */
"Восстановить",
/* TR_RESTORE_CONFIGURATION */
"Если у Вас есть floppy с настройками %s , вставьте floppy диск и нажмите кнопку восстановления.",
/* TR_ROOT_PASSWORD */
"пароль 'root'",
/* TR_SECONDARY_DNS */
"Второй DNS:",
/* TR_SECONDARY_DNS_CR */
"Второй DNS\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"Второй DNS указан без основного DNS",
/* TR_SECTION_MENU */
"Меню разделов",
/* TR_SELECT */
"Выбрать",
/* TR_SELECT_CDROM_TYPE */
"Выделить тип CDROM",
/* TR_SELECT_CDROM_TYPE_LONG */
"Не найден CD-ROM на этой машине.  Пожалуйста укажите какой драйвер Вы собираетесь использовать, чтобы %s увидел CD-ROM.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Укажите носитель с установщиком",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s может быть установлен разными способами.  Самый простой - использовать привод CDROM. Если его нет, то можно попробовать установку с другой машины в LAN сети, где установочные файлы доступны по HTTP или FTP протоколу.",
/* TR_SELECT_NETWORK_DRIVER */
"Укажите сетевой драйвер",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Укажите драйвер для сетевой карты, установленной на этой машине. Если Вы указываете ВРУЧНУЮ, у Вас появится возможность задать название модуля драйвера и параметра для драйвера с особыми настройками, например для ISA карты.",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Укажите интерфейс для перенастройки.",
/* TR_SELECT_THE_ITEM */
"Укажите, что хотите настроить.",
/* TR_SETTING_ADMIN_PASSWORD */
"Записывается 'admin' пароль для %s...",
/* TR_SETTING_ROOT_PASSWORD */
"Записывается 'root' пароль....",
/* TR_SETTING_SETUP_PASSWORD */
"БУДЕТ УДАЛЁН",
/* TR_SETUP_FINISHED */
"Установка окончена.  Нажмите Ok.",
/* TR_SETUP_NOT_COMPLETE */
"Первоначальная установка не была завершена полностью.  Необходимо убедиться, что настройка полностью завершена выполнив команду setup ещё раз в shell оболочке.",
/* TR_SETUP_PASSWORD */
"БУДЕТ УДАЛЁН",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Задать дополнительные параметры модуля",
/* TR_SINGLE_GREEN */
"Ваши настройки задаются для одного GREEN интерфейса.",
/* TR_SKIP */
"Пропустить",
/* TR_START_ADDRESS */
"Начальный адрес:",
/* TR_START_ADDRESS_CR */
"Начальный адрес\n",
/* TR_STATIC */
"Статический",
/* TR_SUGGEST_IO */
"(Предлагаемый %x)",
/* TR_SUGGEST_IRQ */
"(Предлагаемый %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"Модуль этого драйвера уже установлен.",
/* TR_TIMEZONE */
"Часовой пояс",
/* TR_TIMEZONE_LONG */
"Укажите свою временную зону из списка ниже.",
/* TR_UNABLE_TO_EJECT_CDROM */
"Не могу открыть CDROM.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Не удалось распаковать модули.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Не удалось найти какие-либо дополнительные драйверы.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Не удалось найти ISDN карты на этом компьютере. Возможно стоит указать дополнительные параметры, если у вас карта типа ISA или имеет особые настройки.",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"Не удаётся инициализировать ISDN.",
/* TR_UNABLE_TO_INSTALL_FILES */
"Не удалось установить файлы.",
/* TR_UNABLE_TO_INSTALL_LANG_CACHE */
"Не удалось установить языковые пакеты.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"Не удалось установить GRUB.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Не удалось подгрузить модули драйверов.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Не удалось создать файловую систему для boot.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Не удалось создать файловую систему для логов.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Не удалось создать корневую файловую систему.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Не удалось создать swap.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Не удалось создать симлинк /dev/harddisk.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Не удалось создать симлинк /dev/harddisk1.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Не удалось создать симлинк /dev/harddisk2.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Не удалось создать симлинк /dev/harddisk3.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Не удалось создать симлинк /dev/harddisk4.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Не удалось создать симлинк /dev/root.",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Не удалось смонтировать раздел boot.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Не удалось смонтировать раздел с логами.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Не удалось смонтировать раздел proc.",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Не удалось смонтировать корневой раздел .",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Не удалось смонтировать раздел swap.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Не удалось открыть основной файл хостов.",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Не удалось открыть файл настроек",
/* TR_UNABLE_TO_PARTITION */
"Не удалось разбить диск на разделы.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"Не удаётся удалить временные загруженные файлы.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"Не удалось задать имя хоста.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"Не удаётся смонтировать привод CDROM/floppy.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"Не получается отмонтировать жёсткие диски.",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"Не могу записать в /etc/fstab",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"Не могу записать в /etc/hostname",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"Не могу записать в /etc/hosts.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"Не могу записать в /etc/hosts.allow.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"Не могу записать в /etc/hosts.deny.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"Не могу записать в %s/ethernet/settings.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"Не могу записать в %s/main/hostname.conf",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"Не могу записать в %s/main/settings.",
/* TR_UNCLAIMED_DRIVER */
"Обнаружена невостребованная сетевая карта типа:\n%s\n\nМожно ей назначить:",
/* TR_UNKNOWN */
"НЕИЗВЕСТНО",
/* TR_UNSET */
"НЕЗАДАНО",
/* TR_USB_KEY_VFAT_ERR */
"Неправильный USB носитель (не найден раздел vfat).",
/* TR_US_NI1 */
"Использовать NI1",
/* TR_WARNING */
"ВНИМАНИЕ",
/* TR_WARNING_LONG */
"Если изменить этот IP адрес, и в данный момент Вы подключены удалённо, то естественным образм Ваше соединение с %s будет потеряно. Придётся переподключиться к НОВОМУ IP. Эта процедура довольно рискована, есть у Вас нет возможности физического доступа к машине, на случай если что-то пойдёт не так.",
/* TR_WELCOME */
"Добро пожаловать в мастер настройки %s . Отмена установки на любом этапе приведёт к перезагрузке.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Ваша конфигурация настроена на один GREEN интерфейс, который уже оснащён драйвером.",
/* TR_YES */
"Да",
/* TR_NO */
"Нет",
/* TR_AS */
"как",
/* TR_IGNORE */
"Игнорировать",
/* TR_PPP_DIALUP */
"PPP DIALUP (PPPoE, модем, ATM ...)",
/* TR_DHCP */
"DHCP",
/* TR_DHCP_STARTSERVER */
"Запуск DHCP-server ...",
/* TR_DHCP_STOPSERVER */
"Остановка DHCP-server ...",
/* TR_LICENSE_ACCEPT */
"Я принимаю эту лицензию.",
/* TR_LICENSE_NOT_ACCEPTED */
"Лицензия не принята. Выход!",
/* TR_EXT4FS */
"EXT4 - Filesystem",
/* TR_EXT4FS_WO_JOURNAL */
"EXT4 - Filesystem without journal",
/* TR_REISERFS */
"ReiserFS - Filesystem",
/* TR_NO_LOCAL_SOURCE */
"Локальный источник не найден. Начинаю загрузку.",
/* TR_DOWNLOADING_ISO */
"Загружается установочный образ ...",
/* TR_DOWNLOAD_ERROR */
"Во время загрузки произошла ошибка!",
/* TR_DHCP_FORCE_MTU */
"Форсировать DHCP mtu:",
/* TR_IDENTIFY */
"Identify",
/* TR_IDENTIFY_SHOULD_BLINK */
"Selected port should blink now ...",
/* TR_IDENTIFY_NOT_SUPPORTED */
"Function is not supported by this port.",
};
