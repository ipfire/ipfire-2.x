/*
 * Turkish (tr) Data File
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
 * (c) 2003 Ismail Murat Dilek
 *  
 */
 
#include "libsmooth.h"

char *tr_tr[] = {

/* TR_ADDRESS_SETTINGS */
"Adres ayarları",
/* TR_ADMIN_PASSWORD */
"Yönetici parolası",
/* TR_AGAIN_PROMPT */
"Tekrar:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Tüm kartlar başarıyla tahsis edildi.",
/* TR_AUTODETECT */
"* OTOTESBİT *",
/* TR_BUILDING_INITRD */
"Building INITRD...",
/* TR_CANCEL */
"Vazgeç",
/* TR_CARD_ASSIGNMENT */
"Kart ataması",
/* TR_CHECKING */
"Checking URL...",
/* TR_CHECKING_FOR */
"Denetleniyor: %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Bu bilgisayarda kullanılan ISDN kartı seçiniz.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Kullanacağınız ISDN protokolünü seçiniz.",
/* TR_CONFIGURE_DHCP */
"Ayar bilgilerini girerek DHCP sunucusunu konfigüre ediniz.",
/* TR_CONFIGURE_NETWORKING */
"Ağı konfigüre et",
/* TR_CONFIGURE_NETWORKING_LONG */
"Şu anda, öncelikle YEŞİL arabirim için doğru sürücüyü yükleyerek ağ ayarlarınızı yapabilirsiniz. Bunu yapmak için iki seçeneğiniz var, otomatik tanımayı seçebilirsiniz ya da listeden uygun bir sürücü seçebilirsiniz. Birden fazla ağ kartı kullanacaksanız, diğerlerini yine kurulum içinde daha sonra ayarlayabilirsiniz. YEŞİL ile aynı tipte birden fazla kartınız varsa, ve her kart özel modül parametreleri istiyorsa, bu tipteki tüm kartlar için parametreleri girerseniz YEŞİL arabirimi kongifüre ettiğinizde tüm kartlar aktif olacaktır.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Her kart atanmış arabirim için ağ sürücülerinizi konfigüre edin.  Geçerli konfigürasyon şöyledir:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"CDROM için uygun bir IO adresi ve/veya IRQ adresi seçiniz.",
/* TR_CONGRATULATIONS */
"Tebrikler!",
/* TR_CONGRATULATIONS_LONG */
"%s başarılı olarak kuruldu. Lütfen tüm disketleri ve CDROM ları sürücülerden çıkarın. Kur, şimdi ISDN, ağ kartları ve sistem parolalarını ayarlayacağınız arabirimi çalıştıracak. Kur tamamlandıktan sonra, web tarayıcınızla http://%s:81 adresine veya https://%s:445 adresine (ya da %s de ne ismi kullandıysanız) girin, ve çevirmeli ağ(if required) ve uzaktan erişimi ayarlayın. &s çevirmeli kullanıcısıiçin bir parola vermeyi unutmayın, %s istemiyorsanız, 'yönetici' kullanıcılar bağlantıyı kontrol edebileceklerdir.",
/* TR_CONTINUE_NO_SWAP */
"Your harddisk is very small, but you can continue without any swap. (Use with caution).",
/* TR_CURRENT_CONFIG */
"Geçerli konfigürasyon: %s%s",
/* TR_DEFAULT_GATEWAY */
"Varsayılan Ağ geçidi:",
/* TR_DEFAULT_GATEWAY_CR */
"Varsayılan Ağ geçidi\n",
/* TR_DEFAULT_LEASE */
"Varsayılan kira (dk):",
/* TR_DEFAULT_LEASE_CR */
"Varsayılan kira süresi\n",
/* TR_DETECTED */
"Tesbit edilen: %s",
/* TR_DHCP_HOSTNAME */
"DHCP Makina adı:",
/* TR_DHCP_HOSTNAME_CR */
"DHCP Makina adı\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"DHCP sunucusu ayarları",
/* TR_DISABLED */
"Pasif",
/* TR_DISABLE_ISDN */
"ISDN kullanma",
/* TR_DISK_TOO_SMALL */
"Your harddisk is too small.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"DNS ve Ağ geçidi ayarları",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"DNS ve ağ geçidi bilgilerini girin.  Bu ayarlar sadece DHCP KIRMIZI arabirim üzerinde pasif edilmişse geçerlidir.",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Konfigürasyonunuz KIRMIZI arabirim için bir ethernet bağdaştırıcısı kullanmıyor. Çevirmeli kullanıcılar için DNS ve Ağ geçidi bilgileri arama anında otomatik olarak ayarlanacaktır.",
/* TR_DOMAINNAME */
"Domain name",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Domain name cannot be empty.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"Domain name cannot contain spaces.",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Domain name may only contain letters, numbers, hyphens and periods.",
/* TR_DOMAIN_NAME_SUFFIX */
"Etki alanı son eki:",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Etki alanı son eki\n",
/* TR_DONE */
"Tamam",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\nBu ayarları değiştirmek istiyor musunuz?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Sürücüler ve kart atamaları",
/* TR_ENABLED */
"Aktif",
/* TR_ENABLE_ISDN */
"ISDN kullan",
/* TR_END_ADDRESS */
"Bitiş adresi:",
/* TR_END_ADDRESS_CR */
"Bitiş adresi\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Bazı ISA kartlar (özellikle ISA olanlar) IRQ ve IQ adres bilgileri için ilave modül parametreleri isterler. Böyle bir kartınız varsa bu ilave parametreleri buraya giriniz. Örneğin: \"io=0x280 irq=9\".Bu paramet5reler kart saptanması sırasında kullanılacaktır. ",
/* TR_ENTER_ADMIN_PASSWORD */
"%s yönetici parolasını girin.  Bu, %s web yönetimi sayfalarınınkayıtlarına erişebilen kullanıcıdır.",
/* TR_ENTER_DOMAINNAME */
"Enter Domain name",
/* TR_ENTER_HOSTNAME */
"Makina adını giriniz.",
/* TR_ENTER_IP_ADDRESS_INFO */
"IP adres bilgilerini gir",
/* TR_ENTER_NETWORK_DRIVER */
"Ağ kartı otomatik olarak tesbit edilemedi. Ağ kartı için sürücü ve ilave parametreleri giriniz.",
/* TR_ENTER_ROOT_PASSWORD */
"'root' için parola girin. Komut satırı erişimi için bu kullanıcı ile oturum açın.",
/* TR_ENTER_SETUP_PASSWORD */
"'setup' kullanıcı parolasını girin. Setup programına erişebilmek için bu kullanıcı ile oturum açın.",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"%s arabirimi için IP adres bilgilerini girin.",
/* TR_ENTER_THE_LOCAL_MSN */
"Yerel telefon numarasını giriniz (MSN/EAZ).",
/* TR_ENTER_URL */
"Enter the URL path to the ipcop-<version>.tgz and images/scsidrv-<version>.img files. WARNING: DNS not available! This should now just be http://X.X.X.X/<directory>",
/* TR_ERROR */
"Hata",
/* TR_ERROR_WRITING_CONFIG */
"Konfigürasyon bilgisi yazılamadı.",
/* TR_EURO_EDSS1 */
"Euro (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Extracting modules...",
/* TR_FAILED_TO_FIND */
"Failed to find URL file.",
/* TR_FOUND_NIC */
"%s tarafından makinanızda şu NIC bulundu: %s",
/* TR_GERMAN_1TR6 */
"German 1TR6",
/* TR_HELPLINE */
"              <Tab>/<Alt-Tab> öğeler arasında   |  <Boşluk> seçim",
/* TR_HOSTNAME */
"Makina adı",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Makina adı boş olamaz.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"Makina adı boşluk içeremez.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"Hostname may only contain letters, numbers and hyphens.",
/* TR_INITIALISING_ISDN */
"ISDN başlatılıyor...",
/* TR_INSERT_CDROM */
"%s CD sini CDROM sürücüye takınız.",
/* TR_INSERT_FLOPPY */
"%s sürücü disketini disket sürücüye takınız.",
/* TR_INSTALLATION_CANCELED */
"Yükleme iptal edildi.",
/* TR_INSTALLING_FILES */
"Dosyalar kuruluyor...",
/* TR_INSTALLING_GRUB */
"GRUB kuruluyor...",
/* TR_INTERFACE */
"%s arabirim",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"Arabirim başlatılamadı.",
/* TR_INVALID_FIELDS */
"Şu alanlar geçersiz:\n\n",
/* TR_INVALID_IO */
"Girilen IO kapı ayrıntıları geçersiz. ",
/* TR_INVALID_IRQ */
"Girilen IRQ ayrıntıları geçersiz.",
/* TR_IP_ADDRESS_CR */
"IP adresi\n",
/* TR_IP_ADDRESS_PROMPT */
"IP adresi:",
/* TR_ISDN_CARD */
"ISDN Kartı",
/* TR_ISDN_CARD_NOT_DETECTED */
"ISDN kart bulunamadı. ISA ya da özel gereksinimleri olan bir kart kullanıyorsanız ilave modül parametrelerini belirtebil	irsiniz.",
/* TR_ISDN_CARD_SELECTION */
"ISDN kart seçimi",
/* TR_ISDN_CONFIGURATION */
"ISDN Ayarları",
/* TR_ISDN_CONFIGURATION_MENU */
"ISDN Konfigürasyonu menüsü",
/* TR_ISDN_NOT_SETUP */
"ISDN ayarlanmadı. Bazı öğeler henüz seçilmemiş.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"ISDN henüz ayarlanmamış. Ayarlamak istediğiniz öğeyi seçin.",
/* TR_ISDN_PROTOCOL_SELECTION */
"ISDN protokol seçimi",
/* TR_ISDN_STATUS */
"ISDN şu anda %s.\n\n   Protokol: %s\n   Kart: %s\n   Yerel telefon numarası: %s\n\nTekrar ayarlamak istediğiniz elemanı seçin, ya da geçerli ayarları kullanmayı seçin.",
/* TR_KEYBOARD_MAPPING */
"Klavye haritası",
/* TR_KEYBOARD_MAPPING_LONG */
"Aşağıdaki listeden kullandığınız klavye tipini seçiniz.",
/* TR_LEASED_LINE */
"Kiralık hat",
/* TR_LOADING_MODULE */
"Modül yükleniyor...",
/* TR_LOADING_PCMCIA */
"Loading PCMCIA modules...",
/* TR_LOOKING_FOR_NIC */
"%s için aranıyor.",
/* TR_MAKING_BOOT_FILESYSTEM */
"Önyükleme dosya sistemi oluşturuluyor...",
/* TR_MAKING_LOG_FILESYSTEM */
"Kayıt dosya sistemi oluşturuluyor...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Kök dosya sistemi oluşturuluyor...",
/* TR_MAKING_SWAPSPACE */
"Takas alanı oluşturuluyor...",
/* TR_MANUAL */
"* EL İLE *",
/* TR_MAX_LEASE */
"En fazla kira (dk):",
/* TR_MAX_LEASE_CR */
"EN fazla kira süresi\n",
/* TR_MISSING_BLUE_IP */
"Missing IP information on the BLUE interface.",
/* TR_MISSING_ORANGE_IP */
"TURUNCU arabirim üzerinde hatalı IP adresi.",
/* TR_MISSING_RED_IP */
"KIRMIZI arabirim üzerinde hatalı IP adresi.",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"Modul adı boş olamaz.",
/* TR_MODULE_PARAMETERS */
"Gereksinim duyduğunuz sürücü için modül adı ve parametrelerini giriniz.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Önyükleme dosya sistemi bağlanıyor...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Kayıt dosya sistemi bağlanıyor...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Kök dosya sistemi bağlanıyor...",
/* TR_MOUNTING_SWAP_PARTITION */
"Takas alanı bağlanıyor...",
/* TR_MSN_CONFIGURATION */
"Yerel telefon numarası (MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Ağ maskesi:",
/* TR_NETWORKING */
"Ağ",
/* TR_NETWORK_ADDRESS_CR */
"Ağ adresi\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Ağ adresi:",
/* TR_NETWORK_CONFIGURATION_MENU */
"Ağ konfigürasyonu menüsü",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Ağ konfigürasyon tipi",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"%s için ağ konfigürasyonunu seçiniz.  Aşağıdaki konfigürasyon tipleri ethernet bağlı arabirimlerin listesidir. Bu ayarları değiştirdiğinzde, ağın yeniden başlatılması gereklidir, ve ağ sürücü atamaları yeniden yapılmalıdır.",
/* TR_NETWORK_MASK_CR */
"Ağ maskesi\n",
/* TR_NETWORK_SETUP_FAILED */
"Ağ ayarları geçersiz.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"Yeterli kart tahsis edilmedi.",
/* TR_NO_BLUE_INTERFACE */
"No BLUE interface assigned.",
/* TR_NO_CDROM */
"No CD-ROM found.",
/* TR_NO_HARDDISK */
"No hard disk found.",
/* TR_NO_IPCOP_TARBALL_FOUND */
"No ipcop tarball found on Web Server.",
/* TR_NO_ORANGE_INTERFACE */
"TURUNCU arabirim atanmamış.",
/* TR_NO_RED_INTERFACE */
"KIRMIZI arabirim atanmamış.",
/* TR_NO_SCSI_IMAGE_FOUND */
"No SCSI image found on Web Server.",
/* TR_NO_UNALLOCATED_CARDS */
"tahsis edilmemiş kart kalmadı, daha fazlası gereklidir. Kartı otomatik arattırabilirsiniz veya Listeden birtane seçebilirsiniz.",
/* TR_OK */
"Tamam",
/* TR_PARTITIONING_DISK */
"Disk bölümleniyor...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"Parolalar eşleşmiyor.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"Parola boş olamaz.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"Password cannot contain spaces.",
/* TR_PASSWORD_PROMPT */
"Parola:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Telefon numarası boş olamaz.",
/* TR_PREPARE_HARDDISK */
"S¸imdi kurulum programı %s üzerinde sabit diski hazırlayacaktır. Öncelikle disk bölümlenecek, daha sonra bu bölümlemeler üzerinebir dosya sistemi yazılacaktır.",
/* TR_PRESS_OK_TO_REBOOT */
"Resetleme için Tamam a basınız.",
/* TR_PRIMARY_DNS */
"Birincil DNS:",
/* TR_PRIMARY_DNS_CR */
"Birincil DNS\n",
/* TR_PROBE */
"Araştırma",
/* TR_PROBE_FAILED */
"Otomatik tanıma başarısız.",
/* TR_PROBING_SCSI */
"Probing SCSI devices...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"%s yönetici parolası ayarlanamadı.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"'root' parolası ayarlanamadı.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"'setup' parolası ayarlanamadı.",
/* TR_PROTOCOL_COUNTRY */
"Protokol/Ülke",
/* TR_PULLING_NETWORK_UP */
"Ağ başlatılıyor...",
/* TR_PUSHING_NETWORK_DOWN */
"Ağ durduruluyor...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Yerel olmayan ağ durduruluyor...",
/* TR_QUIT */
"Çıkış",
/* TR_RED_IN_USE */
"ISDN (ya da herhangi bir harici bağlantı) şu anda kullanımda. Kırmızı arabirim aktif iken ISDN i konfigüre etmemelisiniz.",
/* TR_RESTART_REQUIRED */
"\n\nKonfigürasyon tamamlandığında, ağ yeniden başlatılmalıdır.",
/* TR_RESTORE */
"Geri al",
/* TR_RESTORE_CONFIGURATION */
"Üzerinde %s sistem konfigürasyonu olan bir disketiniz varsa, lütfen bunudisket sürücüye takınız ve \"geri al\" düğmesine basınız.",
/* TR_ROOT_PASSWORD */
"'root' parola",
/* TR_SECONDARY_DNS */
"İkincil DNS:",
/* TR_SECONDARY_DNS_CR */
"İkincil DNS\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"Birincil DNS olmadan İkincil DNS belirtildi",
/* TR_SECTION_MENU */
"Bölüm menüsü",
/* TR_SELECT */
"Seçim",
/* TR_SELECT_CDROM_TYPE */
"CDROM tipini seçiniz.",
/* TR_SELECT_CDROM_TYPE_LONG */
"Bu makinada CDROM bulunamadı.  Lütfen %s nin cdrom yerine kullanması için s¸u sürücülerden birisini seçiniz.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Kurulum ortamını seçiniz",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s çoklu kaynaktan kurulabilir. En basit olanı makinanın cdrom sürücüsünü kullanmaktır. Eğer bilgisayarın sürücüsü yoksa, yerel ağ üzerinde HTTP ile dosya alabileceğiniz bir bilgisayar mevcut ise onun üzerinden de kurulum yapabilirsiniz. Bu durumda ağ sürücü disketi gerekecektir.",
/* TR_SELECT_NETWORK_DRIVER */
"Ağ sürücüsü seçiniz",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Bu makinada kurulu olan kart için bir ağ sürücüsü seçin. EL İLE yi seçerseniz , Özel gereksinimleri olan bir kart için (ISA kartlar gibi) sürücü modül adı ve parametrelerini yazmanız istenecektir.",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Yeniden ayarlamak istediğiniz arabirimi seçin.",
/* TR_SELECT_THE_ITEM */
"Ayarlamak istediğiniz öğeyi seçiniz.",
/* TR_SETTING_ADMIN_PASSWORD */
"%s yönetici parolası ayarlanıyor....",
/* TR_SETTING_ROOT_PASSWORD */
"'root' parolası ayarlanıyor....",
/* TR_SETTING_SETUP_PASSWORD */
"'setup' parolası ayarlanıyor....",
/* TR_SETUP_FINISHED */
"Kurulum tamamlandı. Yeniden başlatmak için Tamam a basınız",
/* TR_SETUP_NOT_COMPLETE */
"Başlangıç kurulumu tümüyle tamamlanamadı.  Kurulumu yeniden kabuktan çalıştırınca doğru olarak tammalandığından emin olun.",
/* TR_SETUP_PASSWORD */
"'setup' parola",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"İlave modül parametrelerini ayarla",
/* TR_SINGLE_GREEN */
"Konfigürasyonunuz bir tekil YEŞİL arabirim için yapıldı.",
/* TR_SKIP */
"Atla",
/* TR_START_ADDRESS */
"Başlangıç adresi:",
/* TR_START_ADDRESS_CR */
"Başlangıç adresi\n",
/* TR_STATIC */
"Statik",
/* TR_SUGGEST_IO */
"(önerilen %x)",
/* TR_SUGGEST_IRQ */
"(önerilen %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"Bu sürücü modülü zaten yüklü.",
/* TR_TIMEZONE */
"Saat dilimi",
/* TR_TIMEZONE_LONG */
"Bulunduğunuz yerin zaman dilimini aşağıdaki listeden seçiniz.",
/* TR_UNABLE_TO_EJECT_CDROM */
"CDROM açılamadı.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Unable to extract modules.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"İlave sürücü bulunamadı.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Bu bilgisayarda bir ISDN kart bulunamadı. ISA ya da özel gereksinimleri olan bir kart kullanıyorsanız ilave modül parametrelerini belirtebilirsiniz. ",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"ISDN başlatılamadı.",
/* TR_UNABLE_TO_INSTALL_FILES */
"Dosyalar kurulamadı.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"GRUB kurulamadı.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Sürücü modülü yüklenemiyor.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Önyükleme dosya sistemi oluşturulamadı.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Kayıt dosya sistemi oluşturulamadı.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Kök dosya sistemi oluşturulamadı.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Takas alanı oluşturulamadı.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"/dev/harddisk için symlink oluşturulamadı.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"/dev/harddisk1 için symlink oluşturulamadı.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"/dev/harddisk2 için symlink oluşturulamadı.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"/dev/harddisk3 için symlink oluşturulamadı.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"/dev/harddisk4 için symlink oluşturulamadı.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"/dev/root için symlink oluşturulamadı.",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Önyükleme dosya sistemi bağlanamadı.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Kayıt dosya sistemi bağlanamadı.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"/proc dosya sistemi bag˘lanamadı.",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Kök dosya sistemi bağlanamadı.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Takas alanı bağlanamadı.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Unable to open main hosts file.",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Ayar dosyası açılamıyor",
/* TR_UNABLE_TO_PARTITION */
"Disk bölümlenemiyor.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"İndirilen geçici dosyalar silinemedi.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"Makina adı yazılamıyor.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"cdrom/disket sürücü ayrılamadı.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"Sabit disk ayrılamadı.",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"/etc/fstab dosyasına yazılşamıyor",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"/etc/hostname dosyasına yazılşamıyor",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"/etc/hosts soayası yazılamıyor.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"/etc/hosts.allow dosyası yazılamıyor.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"/etc/hosts.deny dosyası yazılamıyor.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"%s/ethernet/settings yazılamıyor.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"%s/main/hostname.conf dosyası yazılamıyor.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"%s/main/settings yazılamıyor.",
/* TR_UNCLAIMED_DRIVER */
"TAlep edilmemiş bir ethernet kartı:\n%s\n\nBunu şuna atayabilirsiniz:",
/* TR_UNKNOWN */
"BİLİNMEYEN",
/* TR_UNSET */
"UNSET",
/* TR_USB_KEY_VFAT_ERR */
"This USB key is invalid (no vfat partition found).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"DİKKAT",
/* TR_WARNING_LONG */
"Bu IP adresini değiştirirseniz, ve uzaktan oturum açmışsanız, %s makinası ile bağlantınız kesilecektir, ve bundan sonrayeni IP ile bağlanmanız gerekecektir. Bu riskli bir işlemdir, vefiziksel olarak makinanın başında iken, ve birşeyler yanlış gittiğinde yapılmalıdır.",
/* TR_WELCOME */
"%s kurulum programına hoşgeldiniz. Sonraki ekranların herhangi birindeVazgeç i seçtiğinizde bilgisayar yeniden başlatılacaktır.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Konfigürasyonunuz, zaten bir sürücü atanmış olan  tekil YEŞİL arabirim için yapılmış. ",
}; 
  
