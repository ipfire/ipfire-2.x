/*
 * Vietnamese  (vi) Data File
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
 * (c) 2004 Le Dinh Long 
 */
 
#include "libsmooth.h"

char *vi_tr[] = {

/* TR_ADDRESS_SETTINGS */
"Thiết lập địa chỉ",
/* TR_ADMIN_PASSWORD */
"Mật khẩu Quản trị",
/* TR_AGAIN_PROMPT */
"Lặp lại:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Tất cả các card đã được cấp phát.",
/* TR_AUTODETECT */
"* TỰ ĐỘNG NHẬN  BIẾT *",
/* TR_BUILDING_INITRD */
"Đang tạo INITRD...",
/* TR_CANCEL */
"Huỷ bỏ",
/* TR_CARD_ASSIGNMENT */
"Chỉ định card",
/* TR_CHECKING */
"Đang kiểm tra URL...",
/* TR_CHECKING_FOR */
"Đang kiểm tra: %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Chọn card ISDN được gắn trên máy này.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Chọn giao thức ISDN cần có.",
/* TR_CONFIGURE_DHCP */
"Cấu hình dịch vụ DHCP bằng cách nhập các thông tin thiết lập.",
/* TR_CONFIGURE_NETWORKING */
"Cấu hình mạng",
/* TR_CONFIGURE_NETWORKING_LONG */
"Bây giờ bạn nên cấu hình mạng bằng cách nạp driver đúng cho giao tiếp GREEN trước. Bạn có thể thực hiện bằng cách tự động dò card mạng, hoặc chọn driver đúng từ danh sách cho trước. Lưu ý rằng nếu bạn có nhiều hơn một card mạng được gắn, bạn có thể cấu hình các cái khác sau trong quá trình cài đặt. Cũng nhớ rằng nếu bạn có nhiều hơn một card mạng có cùng kiểu GREEN và mỗi card cần các tham số cho mô-đun khác nhau, bạn cần nhập các tham số cho tất cả các card loại này để chúng có thể được kích hoạt khi cấu hình giao tiếp GREEN.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Cấu hình driver mạng và giao tiếp mỗi card được chỉ đến. Cấu hình hiện tại như sau:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"Cấu hình CDROM bằng cách chọn địa chỉ IO và/hoặc IRQ thích hợp.",
/* TR_CONGRATULATIONS */
"Xin chúc mừng!",
/* TR_CONGRATULATIONS_LONG */
"%s đã được cài đặt thành công. Hãy lấy đĩa mềm hay CDROM ra khỏi máy. Trình thiết lập sẽ chạy để bạn có thể cấu hình ISDN, card mạng và mật khẩu của hệ thống. Sau khi thiết lập hoàn tất, bạn nên dùng trình duyệt trỏ đến http://%s:81 hoặc https://%s:445 (hoặc tên gì bạn đã đặt cho %s), và cấu hình quay số (nếu cần thiết) và truy cập từ xa. Nhớ đặt mật khẩu cho user 'dial' trên %s, nếu bạn muốn các user không phải 'admin' có thể điều khiển đườn kết nối quay số.",
/* TR_CONTINUE_NO_SWAP */
"Đĩa cứng của bạn quá nhỏ, bạn có thể tiếp tục mà không có swap. (Cẩn thận khi dùng).",
/* TR_CURRENT_CONFIG */
"Cấu hình hiện tại: %s%s",
/* TR_DEFAULT_GATEWAY */
"Gateway Mặc định:",
/* TR_DEFAULT_GATEWAY_CR */
"Gateway Mặc định\n",
/* TR_DEFAULT_LEASE */
"Thời gian cấp đchỉ mặc định (phút):",
/* TR_DEFAULT_LEASE_CR */
"Thời gian cấp địa chỉ mặc định (phút)\n",
/* TR_DETECTED */
"Nhận biết một: %s",
/* TR_DHCP_HOSTNAME */
"Tên máy chủ DHCP:",
/* TR_DHCP_HOSTNAME_CR */
"Tên máy chủ DHCP\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"Cấu hình dịch vụ DHCP",
/* TR_DISABLED */
"Tắt",
/* TR_DISABLE_ISDN */
"Tắt ISDN",
/* TR_DISK_TOO_SMALL */
"Đĩa cứng của bạn quá nhỏ.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"Thiết lập DNS và Gateway",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Nhập thông tin DNS và gateway. Các thiết lập này chỉ được sử dụng với IP Tĩnh (và DHCP nếu DNS được đặt) trên giao tiếp RED.",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Cấu hình của bạn không sử dụng card ethernet cho giao tiếp RED. Thông tin DNS và Gateway cho các user quay số sẽ được tự động cấu hình lúc quay số.",
/* TR_DOMAINNAME */
"Tên miền",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Tên miền không thể trống.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"Tên miền không thể chứa khoảng trắng.",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Tên miền chỉ có thể chứa ký tự, chữ số, gạch ngang và dấu chấm.",
/* TR_DOMAIN_NAME_SUFFIX */
"Đuôi tên miền:",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Đuôi tên miền\n",
/* TR_DONE */
"Xong",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\nBạn có muốn thay đổi các thiết lập này?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Chỉ định driver và card",
/* TR_ENABLED */
"Bật",
/* TR_ENABLE_ISDN */
"Bật ISDN",
/* TR_END_ADDRESS */
"Địa chỉ cuối:",
/* TR_END_ADDRESS_CR */
"Địa chỉ cuối\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Một số card ISDN (nhất là card ISA) có thể cần thêm các tham số mô-đun khác để thiết lập thông tin IRQ và địa chỉ IO. Nếu bạn có loại card ISDN đó, nhập các tham số thêm ở đây. Ví dụ: \"io=0x280 irq=9\". Chúng sẽ được dùng khi nhận biết card.",
/* TR_ENTER_ADMIN_PASSWORD */
"Nhập mật khẩu quản trị %s. Nó sẽ được dùng để user đăng nhập vào trang web quản trị của %s.",
/* TR_ENTER_DOMAINNAME */
"Nhập Tên miền",
/* TR_ENTER_HOSTNAME */
"Nhập tên máy.",
/* TR_ENTER_IP_ADDRESS_INFO */
"Nhập thông tin địa chỉ IP",
/* TR_ENTER_NETWORK_DRIVER */
"Nhận biết card mạng tự động không được. Nhập driver và tham số tuỳ chọn cho card mạng.",
/* TR_ENTER_ROOT_PASSWORD */
"Nhập mật khẩu user 'root'. Đăng nhập với user này để thao tác dòng lệnh.",
/* TR_ENTER_SETUP_PASSWORD */
"Nhập mật khẩu user 'setup'. Đang nhập với user này để chạy chương trình thiết lập.",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Nhập thông tin địa chỉ IP cho giao tiếp %s.",
/* TR_ENTER_THE_LOCAL_MSN */
"Nhập số điện thoại nội hạt (MSN/EAZ).",
/* TR_ENTER_URL */
"Nhập đường dẫn URL đến file ipcop-<version>.tgz và images/scsidrv-<version>.img. CẢNH BÁO: DNS chưa có! Lúc này chỉ nên nhập dạng http://X.X.X.X/<directory> ",
/* TR_ERROR */
"Lỗi",
/* TR_ERROR_WRITING_CONFIG */
"Lỗi ghi thông tin cấu hình.",
/* TR_EURO_EDSS1 */
"Euro (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Đang bung các mô-đun...",
/* TR_FAILED_TO_FIND */
"Không tìm được file URL.",
/* TR_FOUND_NIC */
"%s đã nhận biết các NIC sau trên máy của bạn: %s",
/* TR_GERMAN_1TR6 */
"German 1TR6",
/* TR_HELPLINE */
"                 <Tab>/<Alt-Tab> để di chuyển | <Space> để chọn",
/* TR_HOSTNAME */
"Tên máy",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Tên máy không thể trống.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"Tên máy không thể chứa khoảng trắng.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"Tên máy chỉ có thể chứa ký tự, chữ số và gạch ngang.",
/* TR_INITIALISING_ISDN */
"Đang khởi động ISDN...",
/* TR_INSERT_CDROM */
"Hãy cho CD %s vào ổ CDROM.",
/* TR_INSERT_FLOPPY */
"Hãy cho đĩa mềm driver %s  vào ổ đĩa mềm.",
/* TR_INSTALLATION_CANCELED */
"Cài đặt bị huỷ bỏ.",
/* TR_INSTALLING_FILES */
"Đang cài đặt file...",
/* TR_INSTALLING_GRUB */
"Đang cài đặt GRUB...",
/* TR_INTERFACE */
"Giao tiếp %s",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"Giao tiếp không bật được.",
/* TR_INVALID_FIELDS */
"Các ô sau không hợp lệ:\n\n",
/* TR_INVALID_IO */
"Thông tin chi tiết cổng IO nhập vào không hợp lệ.",
/* TR_INVALID_IRQ */
"Thông tin chi tiết IRQ nhập vào không hợp lệ.",
/* TR_IP_ADDRESS_CR */
"Địa chỉ IP\n",
/* TR_IP_ADDRESS_PROMPT */
"Địa chỉ IP:",
/* TR_ISDN_CARD */
"Card ISDN",
/* TR_ISDN_CARD_NOT_DETECTED */
"Card ISDN không nhận biết được. Bạn cần phải khai báo các tham số phụ cho mô-đun nếu card là loại ISA hoặc có yêu cầu đặc biệt khác.",
/* TR_ISDN_CARD_SELECTION */
"Chọn card ISDN",
/* TR_ISDN_CONFIGURATION */
"Cấu hình ISDN",
/* TR_ISDN_CONFIGURATION_MENU */
"Menu cấu hình ISDN",
/* TR_ISDN_NOT_SETUP */
"ISDN chưa thiết lập. Một vài mục chưa được chọn.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"ISDN chưa được cấu hình. Chọn mục bạn muốn cấu hình.",
/* TR_ISDN_PROTOCOL_SELECTION */
"Chọn giao thức ISDN",
/* TR_ISDN_STATUS */
"ISDN hiện tại %s.\n\n Giao thức: %s\n Card: %s\n Số điện thoại nội hạt: %s\n\nChọn mục bạn muốn cấu hình lại, hoặc chọn để sử dụng thiết lập hiện tại.",
/* TR_KEYBOARD_MAPPING */
"Sắp đặt bàn phím",
/* TR_KEYBOARD_MAPPING_LONG */
"Chọn kiểu bàn phím bạn đang dùng từ danh sách sau.",
/* TR_LEASED_LINE */
"Kênh riêng",
/* TR_LOADING_MODULE */
"Đang nạp mô-đun...",
/* TR_LOADING_PCMCIA */
"Đang nạp PCMCIA mô-đun...",
/* TR_LOOKING_FOR_NIC */
"Đang tìm: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Đang tạo hệ thống file boot...",
/* TR_MAKING_LOG_FILESYSTEM */
"Đang tạo hệ thống file log...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Đang tạo hệ thống file root...",
/* TR_MAKING_SWAPSPACE */
"Đang tạo vùng swap...",
/* TR_MANUAL */
"* THỦ CÔNG *",
/* TR_MAX_LEASE */
"Thời gian cấp đchỉ tối đa (phút):",
/* TR_MAX_LEASE_CR */
"Thời gian tạm cấp tối đa\n",
/* TR_MISSING_BLUE_IP */
"Thiếu thông tin IP trên giao tiếp BLUE.",
/* TR_MISSING_ORANGE_IP */
"Thiếu thông tin IP trên giao tiếp ORANGE.",
/* TR_MISSING_RED_IP */
"Thiếu thông tin IP trên giao tiếp RED.",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"Tên mô-đun không thể để trống.",
/* TR_MODULE_PARAMETERS */
"Nhập tên mô-đun và tham số cho driver bạn cần.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Đang gắn kết hệ thống file boot...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Đang gắn kết hệ thống file log...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Đang gắn kết hệ thống file root...",
/* TR_MOUNTING_SWAP_PARTITION */
"Đang gắn kết phân vùng swap...",
/* TR_MSN_CONFIGURATION */
"Số điện thoại nội hạt (MSN/EAZ)",
/* TR_NETMASK_PROMPT */
"Mặt nạ địa chỉ:",
/* TR_NETWORKING */
"Mạng",
/* TR_NETWORK_ADDRESS_CR */
"Địa chỉ mạng\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Địa chỉ mạng:",
/* TR_NETWORK_CONFIGURATION_MENU */
"Menu cấu hình mạng",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Kiểu cấu hình mạng",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Chọn kiểu cấu hình mạng cho %s. Các kiểu cấu hình sau liệt kê các giao tiếp có gắn với card ethernet. Nếu bạn thay đổi thiết lập này, cần phải khởi động lại dịch vụ mạng, và bạn cũng sẽ phải cấu hình lại các chỉ định driver mạng.",
/* TR_NETWORK_MASK_CR */
"Mặt nạ địa chỉ mạng\n",
/* TR_NETWORK_SETUP_FAILED */
"Thiết lập mạng không được.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"Không cấp phát đủ card.",
/* TR_NO_BLUE_INTERFACE */
"Chưa chỉ định giao tiếp BLUE.",
/* TR_NO_CDROM */
"Không tìm thấy CD-ROM.",
/* TR_NO_HARDDISK */
"Không tìm thấy đĩa cứng.",
/* TR_NO_IPCOP_TARBALL_FOUND */
"Không tìm thấy file nén ipcop trên máy chủ Web.",
/* TR_NO_ORANGE_INTERFACE */
"Chưa chỉ định giao tiếp ORANGE.",
/* TR_NO_RED_INTERFACE */
"Chưa chỉ định giao tiếp RED.",
/* TR_NO_SCSI_IMAGE_FOUND */
"Không tìm thấy file ảnh SCSI trên máy chủ Web.",
/* TR_NO_UNALLOCATED_CARDS */
"Không còn card nào chưa được cấp phát, cần phải thêm. Bạn có thể tự động nhận biết và tìm thêm card, hoặc chọn để lựa một driver từ danh sách.",
/* TR_OK */
"OK",
/* TR_PARTITIONING_DISK */
"Đang phân vùng đĩa...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"Mật khẩu không khớp.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"Mật khẩu không thể để trống.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"Mật khẩu không thể chứa khoảng trắng.",
/* TR_PASSWORD_PROMPT */
"Mật khẩu:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Số điện thoại không thể trống.",
/* TR_PREPARE_HARDDISK */
"Chương trình cài đặt sẽ chuẩn bị đĩa cứng trên %s. Trước tiên đĩa sẽ được phân vùng, sau đó các hệ thống file sẽ được đặt trên các phân vùng đó.",
/* TR_PRESS_OK_TO_REBOOT */
"Nhấn Ok để khởi động lại.",
/* TR_PRIMARY_DNS */
"DNS Chính:",
/* TR_PRIMARY_DNS_CR */
"DNS Chính\n",
/* TR_PROBE */
"Dò tìm",
/* TR_PROBE_FAILED */
"Tự động nhận biết không được.",
/* TR_PROBING_SCSI */
"Đang dò tìm thiết bị SCSI...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"Có vấn đề với thiết lập mật khẩu quản trị %s.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"Có vấn đề với thiết lập mật khẩu 'root'.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"Có vấn đề với thiết lập mật khẩu 'setup'.",
/* TR_PROTOCOL_COUNTRY */
"Giao thức/Quốc gia",
/* TR_PULLING_NETWORK_UP */
"Đang bật mạng lên...",
/* TR_PUSHING_NETWORK_DOWN */
"Đang tắt mạng...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Đang tắt mạng ngoài nội bộ...",
/* TR_QUIT */
"Thoát",
/* TR_RED_IN_USE */
"ISDN (hoặc kết nối ra ngoài khác) đang sử dụng. Bạn không thể cấu hình ISDN khi giao tiếp RED còn đang hoạt động.",
/* TR_RESTART_REQUIRED */
"\n\nKhi cấu hình hoàn tất, cần phải khởi động lại dịch vụ mạng.",
/* TR_RESTORE */
"Phục hồi",
/* TR_RESTORE_CONFIGURATION */
"Nếu bạn có đĩa mềm chứa cấu hình %s, cho vào ổ đĩa mềm rồi nhấn nút Phục hồi.",
/* TR_ROOT_PASSWORD */
"Mật khẩu 'root'",
/* TR_SECONDARY_DNS */
"DNS Phụ:",
/* TR_SECONDARY_DNS_CR */
"DNS Phụ\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"Khai báo DNS Phụ mà không có DNS Chính",
/* TR_SECTION_MENU */
"Phần menu ",
/* TR_SELECT */
"Chọn",
/* TR_SELECT_CDROM_TYPE */
"Chọn kiểu CDROM",
/* TR_SELECT_CDROM_TYPE_LONG */
"Không có CD-ROM nào trên máy được nhận biết. Hãy chọn một trong số các driver sau bạn muốn dùng để %s có thể truy xuất được CD-ROM.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Chọn phương tiện cài đặt",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s có thể được cài đặt từ nhiều nguồn. Cách đơn giản nhất là dùng máy tính có ổ CDROM. Nếu máy tính không có ổ CDROM, bạn có thể cài thông qua một máy khác trong mạng LAN có chứa các file cài đặt qua HTTP. Trong trường hợp này cần phải có đĩa mềm chứa driver mạng.",
/* TR_SELECT_NETWORK_DRIVER */
"Chọn driver mạng",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Chọn driver mạng cho card được gắn trên máy này. Nếu bạn chọn THỦ CÔNG, bạn sẽ có thể nhập tên driver và các tham số cho các driver có các yêu cầu đặc biệt, chẳng hạn như card loại ISA.",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Chọn giao tiếp bạn muốn cấu hình lại.",
/* TR_SELECT_THE_ITEM */
"Chọn mục bạn muốn cấu hình.",
/* TR_SETTING_ADMIN_PASSWORD */
"Đang đặt mật khẩu quản trị %s...",
/* TR_SETTING_ROOT_PASSWORD */
"Đang đặt mật khẩu 'root'...",
/* TR_SETTING_SETUP_PASSWORD */
"Đang đặt mật khẩu 'setup'...",
/* TR_SETUP_FINISHED */
"Thiết lập hoàn tất. Nhấn Ok để khởi động lại.",
/* TR_SETUP_NOT_COMPLETE */
"Thiết lập khởi đầu không hoàn tất hết. Bạn phải chắc chắn chương trình Thiết lập kết thúc đúng đắn bằng cách chạy setup lại ở dòng lệnh.",
/* TR_SETUP_PASSWORD */
"mật khẩu 'setup'",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Đặt các tham số mô-đun khác",
/* TR_SINGLE_GREEN */
"Cấu hình của bạn được đặt cho một giao tiếp GREEN.",
/* TR_SKIP */
"Bỏ qua",
/* TR_START_ADDRESS */
"Địa chỉ đầu:",
/* TR_START_ADDRESS_CR */
"Địa chỉ đầu\n",
/* TR_STATIC */
"Tĩnh",
/* TR_SUGGEST_IO */
"(đề nghị %x)",
/* TR_SUGGEST_IRQ */
"(đề nghị %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"Mô-đun driver này đã được nạp.",
/* TR_TIMEZONE */
"Múi giờ",
/* TR_TIMEZONE_LONG */
"Chọn múi giờ bạn đang ở trong danh sách sau.",
/* TR_UNABLE_TO_EJECT_CDROM */
"Không thể đẩy CDROM ra.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Không thể bung các mô-đun.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Không thể tìm thấy thêm driver nào.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Không thể tìm thấy card ISDN trên máy này. Có thể bạn cần khai báo thêm các tham số khác cho mô-đun nếu card là loại ISA hoặc có các yêu cầu đặc biệt.",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"Không thể khởi tạo ISDN.",
/* TR_UNABLE_TO_INSTALL_FILES */
"Không thể cài đặt file.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"Không thể cài đặt GRUB.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Không thể nạp mô-đun driver.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Không thể tạo hệ thống file boot.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Không thể tạo hệ thống file log.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Không thể tạo hệ thống file root.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Không thể tạo không gian swap.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Không thể tạo liên kết /dev/harddisk.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Không thể tạo liên kết /dev/harddisk1.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Không thể tạo liên kết /dev/harddisk2.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Không thể tạo liên kết /dev/harddisk3.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Không thể tạo liên kết /dev/harddisk4.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Không thể tạo liên kết /dev/root.",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Không thể gắn kết hệ thống file boot.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Không thể gắn kết hệ thống file log.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Không thể gắn kết hệ thống file proc.",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Không thể gắn kết hệ thống file root.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Không thể gắn kết phân vùng swap.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Không thể mở file hosts.",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Không thể mở file chứa thiết lập.",
/* TR_UNABLE_TO_PARTITION */
"Không thể phân vùng đĩa cứng.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"Không thể xoá các file được tải xuống tạm.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"Không thể đặt được tên máy.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"Không thể gỡ gắn kết CDROM/đĩa mềm.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"Không thể gỡ gắn kết đĩa cứng.",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"Không thể ghi lên /etc/fstab.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"Không thể ghi lên /etc/hostname.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"Không thể ghi lên /etc/hosts.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"Không thể ghi lên /etc/hosts.allow.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"Không thể ghi lên /etc/hosts.deny.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"Không thể ghi lên %s/ethernet/settings.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"Không thể ghi lên %s/main/hostname.conf",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"Không thể ghi lên %s/main/settings.",
/* TR_UNCLAIMED_DRIVER */
"Có một card ethernet không đòi hỏi bắt buộc có kiểu:\n%s\n\nBạn có thể chỉ định nó cho:",
/* TR_UNKNOWN */
"KHÔNG RÕ",
/* TR_UNSET */
"CHƯA ĐẶT",
/* TR_USB_KEY_VFAT_ERR */
"This USB key is invalid (no vfat partition found).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"CẢNH BÁO",
/* TR_WARNING_LONG */
"Nếu bạn đổi địa chỉ IP này, và bạn đang đăng nhập từ xa, kết nối của bạn đến máy %s sẽ bị ngắt, bạn sẽ phải kết nối lại đến IP mới. Đây là một thao tác mạo hiểm, và bạn chỉ nên thử nếu bạn có thể truy cập vật lý vào máy, khi có gì đó không ổn. ",
/* TR_WELCOME */
"Chào mừng đến chương trình cài đặt %s. Chọn Huỷ bỏ khi ở bất kỳ màn hình nào sau đây sẽ khởi động lại máy tính.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Cấu hình của bạn được đặt cho một giao tiếp GREEN đã được chỉ định driver.",
}; 
  
