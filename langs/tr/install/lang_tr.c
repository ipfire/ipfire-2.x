/*
 * Turkish (tr) Data File
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

char *tr_tr[] = {

/* TR_ISDN */
"ISDN",
/* TR_ERROR_PROBING_ISDN */
"ISDN aygıtları taramak için açılamıyor.",
/* TR_PROBING_ISDN */
"Tara ve ISDN aygıtlarını yapılandır.",
/* TR_MISSING_GREEN_IP */
"Yeşil IP yok!",
/* TR_CHOOSE_FILESYSTEM */
"Lütfen dosya sistemini seçin:",
/* TR_NOT_ENOUGH_INTERFACES */
"Seçiminize göre yeterli ağ kartı yok.\n\nGerekli: %d - Mevcut: %d\n",
/* TR_INTERFACE_CHANGE */
"Değiştirmek istediğiniz ara birimi seçiniz.\n\n",
/* TR_NETCARD_COLOR */
"Atanan Kartlar",
/* TR_REMOVE */
"Kaldır",
/* TR_MISSING_DNS */
"Eksik DNS.\n",
/* TR_MISSING_DEFAULT */
"Varsayılan Ağ Geçidi Eksik.\n",
/* TR_JOURNAL_EXT3 */
"Ext3 için günlük oluşturuluyor...",
/* TR_CHOOSE_NETCARD */
"Aşağıdaki ara birim için bir ağ kartı seçin - %s.",
/* TR_NETCARDMENU2 */
"Genişletilmiş Ağ Listesi",
/* TR_ERROR_INTERFACES */
"Sisteminizde hiç boş ara birim bulunmamaktadır.",
/* TR_REMOVE_CARD */
"Ağ kartı için tahsis edilenler silinsin mi? - %s",
/* TR_JOURNAL_ERROR */
"Günlük oluşturulamadı son çare olarak ext2 kullanılacak.",
/* TR_FILESYSTEM */
"Dosya Sistemini Seçin",
/* TR_ADDRESS_SETTINGS */
"Adres ayarları",
/* TR_ADMIN_PASSWORD */
"'admin' parolası",
/* TR_AGAIN_PROMPT */
"Tekrar:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Tüm kartalar başarılı bir şekilde atandı.",
/* TR_AUTODETECT */
"* OTOMATİK ALGILAMA *",
/* TR_BUILDING_INITRD */
"Ramdisk oluşturuluyor...",
/* TR_CANCEL */
"İptal",
/* TR_CARD_ASSIGNMENT */
"Kart ataması",
/* TR_CHECKING */
"URL kontrol ediliyor...",
/* TR_CHECKING_FOR */
"Kontrol: %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Bu bilgisayarda yüklü ISDN kartını seçin.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"İstediğiniz ISDN iletişim kuralını seçin.",
/* TR_CONFIGURE_DHCP */
"Ayar bilgilerini girerek DHCP sunucusu yapılandırın.",
/* TR_CONFIGURE_NETWORKING */
"Ağ yapılandırması",
/* TR_CONFIGURE_NETWORKING_LONG */
"Şimdi öncelikle YEŞİL ara birim için doğru sürücüyü yükleyerek ağınızı yapılandırmanız gerekir. Bir ağ kartı yüklemek için otomatik tarama yapabilir ya da listeden doğru sürücüyü seçebilirsiniz. Eğer birden fazla ağ kartınız varsa yapılandırmadan sonra da bu ağ kartlarının yüklenebileceğini unutmayın. Ayrıca birden fazla aynı türde ağ kartınız varsa hangi kartı YEŞİL ara birime atadığınızı unutmayın. Her kart için özel modül parametreleri eklemeniz gerekebilir. Eğer YEŞİL ara birimi yapılandırırken tüm ağ kartları aktifse tüm türdeki kartlar için parametreleri girmeniz gerekir.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Ağ sürücüleri ve hangi ara birim için hangi kartların atanacağını yapılandırın. Mevcut yapılandırma:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"Uygun GÇ ve/veya IRQ seçerek CDROM yapılandır.",
/* TR_CONGRATULATIONS */
"Tebrikler!",
/* TR_CONGRATULATIONS_LONG */
"%s başarıyla yüklendi. Şimdi bilgisayarınızdaki cdyi çıkartın. Kurulum ISDN, ağ kartları, sistem parolalarını yapılandırabileceğiniz programı çalıştıracaktır. Kurulum tamamlandıktan sonra bir internet tarayıcısı açıp adres satırına https://%s:444 (ya da %s sistem adınız) yazıp çevirmeli ağ (gerekliyse) ve uzaktan erişim yapılandırmalarınızı yapabilirsiniz.",
/* TR_CONTINUE_NO_SWAP */
"Sabit diskiniz çok küçük, ancak küçük bir takas alanı ile devam edebilirsiniz. (Dikkatli kullanın).",
/* TR_CURRENT_CONFIG */
"Geçerli yapılandırma: %s%s",
/* TR_DEFAULT_GATEWAY */
"Varsayılan Ağ Geçidi:",
/* TR_DEFAULT_GATEWAY_CR */
"Varsayılan Ağ Geçidi\n",
/* TR_DEFAULT_LEASE */
"Varsayılan kira (dakika):",
/* TR_DEFAULT_LEASE_CR */
"Varsayılan kira süresi\n",
/* TR_DETECTED */
"Algılanan: %s",
/* TR_DHCP_HOSTNAME */
"DHCP Ana bilgisayar adı:",
/* TR_DHCP_HOSTNAME_CR */
"DHCP Ana bilgisayar adı\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"DHCP sunucu yapılandırması",
/* TR_DISABLED */
"Devre Dışı",
/* TR_DISABLE_ISDN */
"ISDN Devre Dışı",
/* TR_DISK_TOO_SMALL */
"Sabit diskiniz çok küçük.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"DNS ve Ağ Geçidi ayarları",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"DNS ve Ağ Geçidi bilgilerini girin. Bu ayaralar KIRMIZI ara birim üzerinde sadece statik IP (eğer DNS ayarlarınız DHCP ise) ile kullanılır.",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Yapılandırmanız KIRMIZI ara birim için ethernet adaptörünü kullanamaz. DNS ve Çevirmeli ağ kullanıcıları için ağ geçidi bilgisi çevirmeli ağda otomatik olarak yapılandırılır.",
/* TR_DOMAINNAME */
"Alan adı",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Alan adı boş olamaz.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"Alan adı boşluk içeremez.",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Alan adı sadece harfler, sayılar, tire ve noktadan oluşturulabilir.",
/* TR_DOMAIN_NAME_SUFFIX */
"Alan adı son eki:",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Alan adı son eki\n",
/* TR_DONE */
"Bitti",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\nBu ayarları değiştirmek istiyor musunuz?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Sürücüler ve kart atamaları",
/* TR_ENABLED */
"Aktif",
/* TR_ENABLE_ISDN */
"ISDN aktif",
/* TR_END_ADDRESS */
"Bitiş adresi:",
/* TR_END_ADDRESS_CR */
"Bitiş adresi\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Bazı ISDN kartları (özellikle ISA olanlar) IRQ ve GÇ adres bilgilerini ayarlamak için ek modül parametrelerine ihtiyaç duyar.Böyle bir ISDN kartınız varsa burada bu ek parametreleri girin. Örneğin: \"io = 0x280 irq = 9 \". Bunlar kart algılama sırasında kullanılacaktır.",
/* TR_ENTER_ADMIN_PASSWORD */
"%s 'admin' kullanıcı parolasını giriniz. Bu, %s web yönetimi sayfalarının kayıtlarına erişebilen kullanıcıdır.",
/* TR_ENTER_DOMAINNAME */
"Alan adını girin",
/* TR_ENTER_HOSTNAME */
"Makinenin ana bilgisayar adını girin.",
/* TR_ENTER_IP_ADDRESS_INFO */
"IP adres bilgilerini girin.",
/* TR_ENTER_NETWORK_DRIVER */
"Otomatik olarak bir ağ kartı algılanamadı. Ağ kartı için sürücü ve isteğe bağlı olan parametreleri girin.",
/* TR_ENTER_ROOT_PASSWORD */
"'root' kullanıcı parolasını girin. Komut satırı erişimi için bu kullanıcı ile oturum açın.",
/* TR_ENTER_SETUP_PASSWORD */
"KALDIRILACAK",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"%s ara birimi için IP adres bilgilerini girin.",
/* TR_ENTER_THE_LOCAL_MSN */
"Yerel telefon numarasını girin (MSN/EAZ).",
/* TR_ENTER_URL */
"IPFire-<version>.tgz ve images/scsidrv-<version>.img dosyaları için URL adresini girin. UYARI: DNS mevcut deği! Bu sadece http://X.X.X.X/<directory> olmalıdır.",
/* TR_ERROR */
"Hata",
/* TR_ERROR_PROBING_CDROM */
"CD-ROM sürücüsü bulunamadı.",
/* TR_ERROR_WRITING_CONFIG */
"Yapılandırma bilgilerini yazma hatası.",
/* TR_EURO_EDSS1 */
"Avrupa (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Modüller açılıyor...",
/* TR_FAILED_TO_FIND */
"URL dosyası bulunamadı.",
/* TR_FOUND_NIC */
"%s makinenizde aşağıdaki NIC tespit edildi: %s",
/* TR_GERMAN_1TR6 */
"Alman 1TR6",
/* TR_HELPLINE */
"              <Tab>/<Alt-Tab> öğeler arasında   |  <Space> seçim",
/* TR_HOSTNAME */
"Ana bilgisayar adı",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Ana bilgisayar adı boş olamaz.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"Ana bilgisayar adı boşluk içeremez.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"Ana bilgisayar adı sadece harf, rakam ve tire içerebilir.",
/* TR_INITIALISING_ISDN */
"ISDN başlatılıyor...",
/* TR_INSERT_CDROM */
"Lütfen CD_ROM sürücüsüne %s CDsi yerleştirin.",
/* TR_INSERT_FLOPPY */
"Lütfen disket sürücüsüne %s sürücü disketini yerleştirin.",
/* TR_INSTALLATION_CANCELED */
"Kurulum iptal edildi.",
/* TR_INSTALLING_FILES */
"Dosyalar yükleniyor...",
/* TR_INSTALLING_GRUB */
"GRUB yükleniyor...",
/* TR_INSTALLING_LANG_CACHE */
"Dil dosyası yükleniyor...",
/* TR_INTERFACE */
"Ara birim - %s",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"Ara birim yükseltmesi başarısız oldu.",
/* TR_INVALID_FIELDS */
"Aşağıdaki alanlar geçersizdir:\n\n",
/* TR_INVALID_IO */
"Girilen GÇ bağlantı noktası detayları geçersiz. ",
/* TR_INVALID_IRQ */
"Girilen IRQ ayrıntıları geçersiz.",
/* TR_IP_ADDRESS_CR */
"IP adresi\n",
/* TR_IP_ADDRESS_PROMPT */
"IP adresi:",
/* TR_ISDN_CARD */
"ISDN kartı",
/* TR_ISDN_CARD_NOT_DETECTED */
"ISDN kartı algılanamdı. Kart bir ISA türü veya özel gereksinimleri olan bir kartsa ek modül parametreleri belirtmeniz gerekebilir.",
/* TR_ISDN_CARD_SELECTION */
"ISDN kart seçimi",
/* TR_ISDN_CONFIGURATION */
"ISDN Yapılandırması",
/* TR_ISDN_CONFIGURATION_MENU */
"ISDN yapılandırma listesi",
/* TR_ISDN_NOT_SETUP */
"ISDN kurulamadı. Bazı ürünleri seçmediniz.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"ISDN henüz yapılandırılmamış. Yapılandırmak istediğiniz öğeyi seçin.",
/* TR_ISDN_PROTOCOL_SELECTION */
"ISDN kural seçimi",
/* TR_ISDN_STATUS */
"ISDN şu anda %s.\n\n   Kural: %s\n   Kart: %s\n   Yerel telefon numarası: %s\n\nYeniden yapılandırmanız için istediğiniz öğeyi seçin ya da geçerli ayarları kullanmayı tercih edin.",
/* TR_KEYBOARD_MAPPING */
"Klavye haritası",
/* TR_KEYBOARD_MAPPING_LONG */
"Aşağıdaki listeden kullandığınız klavye türünü seçin.",
/* TR_LEASED_LINE */
"Kiralık hat",
/* TR_LOADING_MODULE */
"Modül yükleniyor...",
/* TR_LOADING_PCMCIA */
"PCMCIA modülleri yükleniyor...",
/* TR_LOOKING_FOR_NIC */
"Arayan: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Önyükleme dosya sistemi yapılandırılıyor...",
/* TR_MAKING_LOG_FILESYSTEM */
"Günlük dosya sistemi yapılandırılıyor...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Root dosya sistemi yapılandırılıyor...",
/* TR_MAKING_SWAPSPACE */
"Takas alanı yapılandırılıyor...",
/* TR_MANUAL */
"* EL İLE *",
/* TR_MAX_LEASE */
"En fazla kira (dak):",
/* TR_MAX_LEASE_CR */
"En fazla kira süresi\n",
/* TR_MISSING_BLUE_IP */
"MAVİ ara birimdeki IP bilgileri eksik.",
/* TR_MISSING_ORANGE_IP */
"TURUNCU ara birimdeki IP bilgileri eksik.",
/* TR_MISSING_RED_IP */
"KIRMIZI ara birimdeki IP bilgileri eksik.",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"Modül adı boş olamaz.",
/* TR_MODULE_PARAMETERS */
"Size gereken sürücü için modül adı ve parametrelerini girin.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Önyükleme dosya sistemi bağlanıyor...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Günlük dosya sistemi bağlanıyor...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Root dosya sistemi bağlanıyor...",
/* TR_MOUNTING_SWAP_PARTITION */
"Takas bölümü bağlanıyor...",
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
"Ağ yapılandırma listesi",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Ağ yapılandırma türü",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"%s için ağ yapılandırmasını seçin. Aşağıdaki yapılandırma türleri ethernet kartına atanmış ara birimleri listeler. Eğer bu ayarları değiştirirseniz ağın yeniden başlatılması gerekir ve yeniden ağ sürücülerinin atanması gerekir.",
/* TR_NETWORK_MASK_CR */
"Ağ maskesi\n",
/* TR_NETWORK_SETUP_FAILED */
"Ağ kurulumu başarısız oldu.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"Yeterince kart tahsis edilemedi.",
/* TR_NO_BLUE_INTERFACE */
"Hiçbir MAVİ ara birim atanmamış.",
/* TR_NO_CDROM */
"CD-ROM bulunamadı.",
/* TR_NO_GREEN_INTERFACE */
"Hiçbir YEŞİL ara birim atanmamış.",
/* TR_NO_HARDDISK */
"Sabit disk bulunamadı.",
/* TR_NO_IPCOP_TARBALL_FOUND */
"Web sunucuda hiçbir ipfire arşivi bulunamadı.",
/* TR_NO_ORANGE_INTERFACE */
"Hiçbir TURUNCU ara birim atanmamış.",
/* TR_NO_RED_INTERFACE */
"Hiçbir KIRMIZI ara birim atanmamış.",
/* TR_NO_SCSI_IMAGE_FOUND */
"Web sunucuda hiçbir SCSI kalıbı bulunamadı.",
/* TR_NO_UNALLOCATED_CARDS */
"Daha fazla ayrılmamış kart bulunmaktadır. Otamatik olarak daha fazla kartı aratabilir veya listeden bir sürücü seçebilirsiniz.",
/* TR_OK */
"Tamam",
/* TR_PARTITIONING_DISK */
"Disk bölümleniyor...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"Parolalar eşeleşmiyor.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"Parola boş olamaz.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"Parla boşluk içeremez.",
/* TR_PASSWORD_PROMPT */
"Parola:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Telefon numarası boş olamaz.",
/* TR_PREPARE_HARDDISK */
"Sabit disk kurulum programı /dev/sda üzerindeki %s sabit diski hazırlayacak. İlk olarak diskiniz bölümlendirilir ve daha sonra bu bölüme dosya sistemleri oluşturulur.\n\nDİSKTEKİ TÜM VERİLER SİLİNECEKTİR. Kabul ediyor musunuz?",
/* TR_PRESS_OK_TO_REBOOT */
"Yeniden Başlat",
/* TR_PRIMARY_DNS */
"Birincil DNS:",
/* TR_PRIMARY_DNS_CR */
"Birincil DNS\n",
/* TR_PROBE */
"Araştır",
/* TR_PROBE_FAILED */
"Otomatik algılama başarısız oldu.",
/* TR_PROBING_HARDWARE */
"Donanım algılanıyor...",
/* TR_PROBING_FOR_NICS */
"Ağ kartları algılanıyor...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"%s 'admin' kullanıcı parolası ayarları sorunlu.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"'root' parola ayarları sorunlu.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"KALDIRILACAK",
/* TR_PROTOCOL_COUNTRY */
"Kural/Ülke",
/* TR_PULLING_NETWORK_UP */
"Ağ alınıyor...",
/* TR_PUSHING_NETWORK_DOWN */
"Ağ bırakılıyor...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Düşmeyen ağ bitirliyor...",
/* TR_QUIT */
"Çık",
/* TR_RED_IN_USE */
"ISDN (ya da herhangi bir harici bağlantı) şu anda kullanımda. Kırmızı arabirim aktifken ISDN seçeneğini yapılandıramazsınız.",
/* TR_RESTART_REQUIRED */
"\n\nYapılandırma tamamlandığında ağı yeniden başlatmanız gerekir.",
/* TR_RESTORE */
"Geri Yükle",
/* TR_RESTORE_CONFIGURATION */
"Eğer %s sistem yapılandırması ile ilgili bir disketiniz varsa disketinizi disket sürücüsüne yerleştirin ve Geri Yükle düğmesine basın.",
/* TR_ROOT_PASSWORD */
"'root' parolası",
/* TR_SECONDARY_DNS */
"İkincil DNS:",
/* TR_SECONDARY_DNS_CR */
"İkincil DNS\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"Birincil DNS olmadan ikincil DNS belirtilmiş.",
/* TR_SECTION_MENU */
"Bölüm listesi",
/* TR_SELECT */
"Seç",
/* TR_SELECT_CDROM_TYPE */
"CD-ROM türünü seç",
/* TR_SELECT_CDROM_TYPE_LONG */
"Bu makinede CD-ROM bulunamadı. %s ile CD-ROM sürücüsüne erişilebilmesi için kullanmak istediğiniz sürücüyü aşağıdan seçin.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Kurulum ortamını seçin",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s birden fazla kaynaktan kurulabilir. En basit makineler de CD-ROM sürücüsü kullanmaktadır. Eğer bilgisayarınızda bir sürücü yoksa HTTP veya FTP üzerinden ayrıca kurulum dosyaları olan başka bir LAN üzerindeki makineden kurulum yapabilirsiniz.",
/* TR_SELECT_NETWORK_DRIVER */
"Ağ sürücüsünü seçin",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Bu makinede kurulu olan kart için bir ağ sürücüsü seçin. EL İLE seçeneğini seçerseniz özel gereksinimleri olan bir kart için (ISA kartlar gibi) sürücü modül adı ve parametrelerini yazmanız istenecektir",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Yeniden yapılandırmak istediğiniz ara birimi seçin.",
/* TR_SELECT_THE_ITEM */
"Yapılandırmak istediğiniz nesneyi seçin.",
/* TR_SETTING_ADMIN_PASSWORD */
"%s 'admin' kullanıcı parolası ayarlanıyor...",
/* TR_SETTING_ROOT_PASSWORD */
"'root' parolası ayarlanıyor....",
/* TR_SETTING_SETUP_PASSWORD */
"KALDIRILACAK",
/* TR_SETUP_FINISHED */
"Kurulum tamamlandı. Tamam tuşuna basın.",
/* TR_SETUP_NOT_COMPLETE */
"Başlangıç kurulumu tamamlanamadı. Şimdi kurulumu tekrar çalıştırarak ayarlarınızın düzgün yapılmış olduğundan emin olun.",
/* TR_SETUP_PASSWORD */
"KALDIRILACAK",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Ek modül parametreleri ayarlayın",
/* TR_SINGLE_GREEN */
"Sadece YEŞİL ara birim için ayarlarınızı yapılandırın.",
/* TR_SKIP */
"Atla",
/* TR_START_ADDRESS */
"Başlangıç adresi:",
/* TR_START_ADDRESS_CR */
"Başlangıç adresi\n",
/* TR_STATIC */
"Sabit",
/* TR_SUGGEST_IO */
"(öneri %x)",
/* TR_SUGGEST_IRQ */
"(öneri %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"Bu sürücü modülü zaten yüklü.",
/* TR_TIMEZONE */
"Zaman dilimi",
/* TR_TIMEZONE_LONG */
"Aşağıdaki listeden bulunduğunuz zaman dilimini seçin.",
/* TR_UNABLE_TO_EJECT_CDROM */
"CD-ROM çıkarmak için açılamıyor.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Modüller ayıklanamıyor.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Herhangi bir ek sürücü bulmak için açılamıyor.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Bu bilgisayar da bir ISDN kartı bulunamadı. Kart bir ISA türüdür veya özel gereksinimleri olan bir kart olabilir. Bu durumda ek modül parametreleri belirtmeniz gerekebilir.",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"ISDN başlatmak için açılamıyor.",
/* TR_UNABLE_TO_INSTALL_FILES */
"Dosyaları kurmak için açılamıyor.",
/* TR_UNABLE_TO_INSTALL_LANG_CACHE */
"Dil dosyalarını kurmak için açılamıyor.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"GRUB kurulamıyor.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Sürücü modülü yüklenemiyor.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Ön yükleme dosya sistemi oluşturulamıyor.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Günlük dosya sistemi oluşturulamıyor.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Root dosya sistemi oluşturulamıyor.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Takas alanı oluşturulamıyor.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Sembolik bağı oluşturulamıyor: /dev/harddisk.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Sembolik bağı oluşturulamıyor: /dev/harddisk1.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Sembolik bağı oluşturulamıyor: /dev/harddisk2.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Sembolik bağı oluşturulamıyor: /dev/harddisk3.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Sembolik bağı oluşturulamıyor: /dev/harddisk4.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Sembolik bağı oluşturulamıyor: /dev/root.",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Ön yükleme dosya sistemi bağlanamadı.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Günlük dosya sistemi bağlanamadı.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Proc dosya sistemi bağlanamadı.",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Root dosya sistemi bağlanamadı.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Takas bölümü bağlanamadı.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Ana bilgisayar dosyası açılamadı.",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Ayarlar dosyası açılamadı.",
/* TR_UNABLE_TO_PARTITION */
"Dsik bölümleri açılamadı.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"Geçici olarak indirilen dosyalar kaldırılamıyor.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"Ana bilgisayar adı ayarlamak için açılamıyor.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"CDROM/floppydisk ayrılamıyor.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"Sabit disk ayrılamıyor.",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"Yazmak için açılamıyor: /etc/fstab",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"Yazmak için açılamıyor: /etc/hostname",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"Yazmak için açılamıyor: /etc/hosts.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"Yazmak için açılamıyor: /etc/hosts.allow.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"Yazmak için açılamıyor: /etc/hosts.deny.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"Yazmak için açılamıyor: %s/ethernet/settings.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"Yazmak için açılamıyor: %s/main/hostname.conf",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"Yazmak için açılamıyor: %s/main/settings.",
/* TR_UNCLAIMED_DRIVER */
"Bu türe ait sahipsiz bir ethernet kartı yok:\n%s\n\nBunu atayabilirsiniz:",
/* TR_UNKNOWN */
"BİLİNMEYEN",
/* TR_UNSET */
"KURULMAMIŞ",
/* TR_USB_KEY_VFAT_ERR */
"Bu USB anahtarı geçersiz (vfat bölümü bulunamadı).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"UYARI",
/* TR_WARNING_LONG */
"Bu IP adresini değiştiriseniz %s makinesi ile uzak oturum bağlantısı kopar ve yeniden IP girmeniz gerekir.Bu riskli bir işlemdir. Bu işlem sırasında bir şeyler ters giderse düzeltmek için makineye fiziksel erişimizin varsa denemelisiniz",
/* TR_WELCOME */
"%s kurulum programına hoş geldiniz. Sonraki ekranların herhangi birinde İptal seçeneğini seçtiğinizde bilgisayar yeniden başlatılacaktır.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Zaten atanmış bir sürücünüz var. Yapılandırma sadece YEŞİL ara birim için yapılır.",
/* TR_YES */
"Evet",
/* TR_NO */
"Hayır",
/* TR_AS */
"-",
/* TR_IGNORE */
"Yok say",
/* TR_PPP_DIALUP */
"PPP ÇEVİRMELİ AĞ (PPPoE, modem, ATM ...)",
/* TR_DHCP */
"DHCP",
/* TR_DHCP_STARTSERVER */
"DHCP-sunucusu başlatılıyor ...",
/* TR_DHCP_STOPSERVER */
"DHCP-sunucusu durduruluyor ...",
/* TR_LICENSE_ACCEPT */
"Bu lisansı kabul ediyorum.",
/* TR_LICENSE_NOT_ACCEPTED */
"Lisans kabul edilmedi. Çık!",
/* TR_EXT2FS_DESCR */
"Ext2 - Günlük olmadan dosya sistemi (flash sürücüler için önerilen)",
/* TR_EXT3FS_DESCR */
"Ext3 - Günlük ile dosya sistemi",
/* TR_EXT4FS_DESCR */
"Ext4 - Günlük ile dosya sistemi",
/* TR_REISERFS_DESCR */
"ReiserFS - Günlük ile dosya sistemi",
/* TR_NO_LOCAL_SOURCE */
"Yerel kaynak medya bulunamadı. İndirme başlatılıyor​​.",
/* TR_DOWNLOADING_ISO */
"Kurulum kalıbı indiriliyor ...",
/* TR_DOWNLOAD_ERROR */
"İndirirken hata!",
/* TR_DHCP_FORCE_MTU */
"DHCP mtu zorla:",
};
