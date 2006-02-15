/*
 * Finnish  (fi) Data File
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
 * (c) 2003 Kai Käpölä 
 */
 
#include "libsmooth.h"

char *fi_tr[] = {

/* TR_ADDRESS_SETTINGS */
"Osoiteasetukset",
/* TR_ADMIN_PASSWORD */
"Admin salasana",
/* TR_AGAIN_PROMPT */
"Uudelleen:",
/* TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED */
"Kaikki kortit ovat määritelty onnistuneesti.",
/* TR_AUTODETECT */
"* AUTOMAATTITUNNISTUS *",
/* TR_BUILDING_INITRD */
"Tallennetaan INITRD...",
/* TR_CANCEL */
"Peruuta",
/* TR_CARD_ASSIGNMENT */
"Korttivalinnat",
/* TR_CHECKING */
"Tarkistetaan osoitetta...",
/* TR_CHECKING_FOR */
"Tarkistetaan: %s",
/* TR_CHOOSE_THE_ISDN_CARD_INSTALLED */
"Valitse tietokoneeseen asennettu ISDN-kortti.",
/* TR_CHOOSE_THE_ISDN_PROTOCOL */
"Valitse käyttämäsi ISDN-protokolla.",
/* TR_CONFIGURE_DHCP */
"Konfiguroi DHCP-palvelin syöttämällä asetustiedot.",
/* TR_CONFIGURE_NETWORKING */
"Asenna verkkoyhteydet",
/* TR_CONFIGURE_NETWORKING_LONG */
"Verkkoyhteyksien asentaminen tapahtuu lataamalla oikea ajuri VIHREÄLLE liitännälle. Voit tehdä tämän automaattihaulla tai valitsemalla ajurin listasta. Mikäli sinulla on usempi kuin yksi verkkokortti huomaa että voit asentaa niiden ajurit myöhemmässä vaiheessa. Huomaaa myös että jos sinulla on useampi saman tyyppinen verkkokortti kuin VIHREÄ:llä yhteydellä, joudut antamaan niille kaikille tarvittavat parametrit jotta kaikki saman tyyppiset verkkokortit ovat käytettävissä VIHREÄN yhteyden asennuksessa.",
/* TR_CONFIGURE_NETWORK_DRIVERS */
"Asenna verkkoajurit ja määrittele mihin yhteyteen kutakin verkokorttia käytetään. Tämän hetkinen konfiguraatio:\n\n",
/* TR_CONFIGURE_THE_CDROM */
"Valitse CDROM-aseman käyttämisen edellyttämät IO-osoite ja/tai IRQ.",
/* TR_CONGRATULATIONS */
"Onneksi olkoon!",
/* TR_CONGRATULATIONS_LONG */
"%s asennettiin onnistuneesti. Poista levykkeet ja cd-levyt asemista. Seuraavaksi asennetaan ISDN- ja verkkortit, sekä järjestelmän salasanat. Asennuksen jälkeen mene www-selaimella osoitteeseen http://%s:81 tai https://%s:445 (tai miksi nyt sitten nimesitkään %s:n) ja asenna tarvittaessa soittosarjayhteys. Muista asettaa salasana 'dial'-käyttäjälle, mikäli haluat tavallisten käyttäjien ottavan yhteyden soittosarjaan. Muussa tapauksessa vain 'admin' käyttäjillä on oikeus avata yhteys.",
/* TR_CONTINUE_NO_SWAP */
"Kovalevysi kapasiteetti on pieni, mutta voit jatkaa ilman levymuistia. (Käytettävä varoen!!)",
/* TR_CURRENT_CONFIG */
"Nykyinen konfiguraatio: %s%s",
/* TR_DEFAULT_GATEWAY */
"Oletusyhdyskäytävä:",
/* TR_DEFAULT_GATEWAY_CR */
"Oletusyhdyskäytävä\n",
/* TR_DEFAULT_LEASE */
"Oletusvarausaika (min):",
/* TR_DEFAULT_LEASE_CR */
"Oletusvarausaika\n",
/* TR_DETECTED */
"Tunnistettu: %s",
/* TR_DHCP_HOSTNAME */
"DHCP-isäntänimi:",
/* TR_DHCP_HOSTNAME_CR */
"DHCP isäntänimi\n",
/* TR_DHCP_SERVER_CONFIGURATION */
"DHCP-palvelimen asetukset",
/* TR_DISABLED */
"Ei käytössä",
/* TR_DISABLE_ISDN */
"Poista ISDN käytöstä",
/* TR_DISK_TOO_SMALL */
"Käytettävän kiintolevyn kapasiteetti on liian pieni.",
/* TR_DNS_AND_GATEWAY_SETTINGS */
"DNS- ja yhdyskäytävä asetukset",
/* TR_DNS_AND_GATEWAY_SETTINGS_LONG */
"Syötä nimipalvelun (DNS) ja yhdyskäytävän (Gateway) tiedot. Näitä asetuksia käytetään ainoastaan mikäli DHCP ei ole käytössä PUNAISESSA-liitännässä.",
/* TR_DNS_GATEWAY_WITH_GREEN */
"Valitsemasi käyttötapa ei käytä PUNAISENA-liitäntänä ethernetiä. Nimipalvelu (DNS) ja yhdyskäytävä (Gateway) asetetaan automaattisesti modeemin yhteyden muodostuksessa.",
/* TR_DOMAINNAME */
"Toimialuenimi (Domainname)",
/* TR_DOMAINNAME_CANNOT_BE_EMPTY */
"Domain-nimi ei voi olla tyhjä.",
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
"Toimialuenimessä ei voi olla välilyöntejä.",
/* TR_DOMAINNAME_NOT_VALID_CHARS */
"Domain-nimessä voi käyttää vain kirjaimia, numeroita, tavuviivaa ja pistettä.",
/* TR_DOMAIN_NAME_SUFFIX */
"Toimialueen nimen pääte",
/* TR_DOMAIN_NAME_SUFFIX_CR */
"Toimialuenimen pääte\n",
/* TR_DONE */
"Valmis",
/* TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS */
"\nHaluatko muuttaa näitä asetuksia?",
/* TR_DRIVERS_AND_CARD_ASSIGNMENTS */
"Ajurit ja korttien käyttö",
/* TR_ENABLED */
"Käytössä",
/* TR_ENABLE_ISDN */
"ISDN käyttöön",
/* TR_END_ADDRESS */
"Loppuosoite:",
/* TR_END_ADDRESS_CR */
"Loppuosoite\n",
/* TR_ENTER_ADDITIONAL_MODULE_PARAMS */
"Eräät ISDN-kortit (erityisesti ISA-väyläään kytkettävä) tarvitsevat toimiakseen keskeytysnumeron (IRQ) ja IO-osoitteen. Mikäli käytössä on tälläinen ISDN-kortti täytyy nämä parametrit syöttää nyt. Esim. \"io=0x280 irq=9\". Parametrejä käytetään kortin tunnistuksessa.",
/* TR_ENTER_ADMIN_PASSWORD */
"Syötä %s:n admin salasana. Tämä käyttäjä voi käyttää %s:n www-ylläpitosivuja.",
/* TR_ENTER_DOMAINNAME */
"Syötä toimialuenimi (Domainname)",
/* TR_ENTER_HOSTNAME */
"Syötä tietokoneen nimi.",
/* TR_ENTER_IP_ADDRESS_INFO */
"Syötä IP-osoite",
/* TR_ENTER_NETWORK_DRIVER */
"Automaattitunnistus ei löytänyt ainuttakaan verkkokorttia. Syötä ajurin nimi ja tarvittavat parametrit:",
/* TR_ENTER_ROOT_PASSWORD */
"Syötä 'root'-käyttäjän salasana. Tämä käyttäjä voi kirjautua pääteyhteydellä.",
/* TR_ENTER_SETUP_PASSWORD */
"Syötä 'setup'-käyttäjän salasana. Tämä käyttäjä voi käyttää asennusohjelmaa.",
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
"Syötä IP-osoite yhteydelle %s.",
/* TR_ENTER_THE_LOCAL_MSN */
"Syötä paikallinen puhelinumero (MSN/EAZ).",
/* TR_ENTER_URL */
"Syötä URL-osoite josta löytyy ipcop-<version>.tgz ja images/scsidrv-<version>.img tiedostot. VAROITUS: Nimipalvelu (DNS) ei ole käytössä! Käytä esim. http://X.X.X.X/<hakemisto>",
/* TR_ERROR */
"Virhe",
/* TR_ERROR_WRITING_CONFIG */
"Asetuksen kirjoittamisessa tapahtui virhe.",
/* TR_EURO_EDSS1 */
"Euro (EDSS1)",
/* TR_EXTRACTING_MODULES */
"Puretaan moduleita...",
/* TR_FAILED_TO_FIND */
"URL-tiedostoa ei löydy.",
/* TR_FOUND_NIC */
"%s löysi tietokoneesta verkkokortin: %s",
/* TR_GERMAN_1TR6 */
"Saksalainen 1TR6",
/* TR_HELPLINE */
"           <Tab>/<Alt-Tab> vaihtaa kohdetta | <Välilyönti> valitsee",
/* TR_HOSTNAME */
"Isäntänimi (Hostname)",
/* TR_HOSTNAME_CANNOT_BE_EMPTY */
"Isäntänimi ei voi olla tyhjä.",
/* TR_HOSTNAME_CANNOT_CONTAIN_SPACES */
"Isäntänimessä ei saa olla välilyöntejä.",
/* TR_HOSTNAME_NOT_VALID_CHARS */
"Hostnamessa on sallittua käyttää vain kirjaimia, numeroita ja tavuviivaa.",
/* TR_INITIALISING_ISDN */
"Alustetaan ISDN...",
/* TR_INSERT_CDROM */
"Laita CDROM-asemaan levy %s.",
/* TR_INSERT_FLOPPY */
"Laita levyasemaan tarvittava ajurilevyke (%s).",
/* TR_INSTALLATION_CANCELED */
"Asennus peruutettu.",
/* TR_INSTALLING_FILES */
"Asennetaan tiedostoja...",
/* TR_INSTALLING_GRUB */
"Asennetaan GRUB...",
/* TR_INTERFACE */
"%s-liitäntä",
/* TR_INTERFACE_FAILED_TO_COME_UP */
"Verkkoyhteyttä ei saatu käynnistettyä.",
/* TR_INVALID_FIELDS */
"Tarkista seuraavat kentät:\n\n",
/* TR_INVALID_IO */
"Syötetty IO-osoite ei kelpaa.",
/* TR_INVALID_IRQ */
"Syötetty keskeytyspyyntönumero (IRQ) ei kelpaa.",
/* TR_IP_ADDRESS_CR */
"IP-osoite\n",
/* TR_IP_ADDRESS_PROMPT */
"IP-osoite:",
/* TR_ISDN_CARD */
"ISDN-kortti",
/* TR_ISDN_CARD_NOT_DETECTED */
"ISDN-korttia ei tunnistettu. Mikäli kortti on ISA-väylässä joudut syöttämään lisäparametreja.",
/* TR_ISDN_CARD_SELECTION */
"ISDN-kortin valinta",
/* TR_ISDN_CONFIGURATION */
"ISDN asetukset",
/* TR_ISDN_CONFIGURATION_MENU */
"ISDN asetukset",
/* TR_ISDN_NOT_SETUP */
"ISDNää ei asennettu. Joitain kohteita ei ole valittu.",
/* TR_ISDN_NOT_YET_CONFIGURED */
"ISDN on määrittelelmättä. Valitse asennettava kohde.",
/* TR_ISDN_PROTOCOL_SELECTION */
"ISDN-protokollan valinta",
/* TR_ISDN_STATUS */
"Käytössä oleva ISDN on %s.\n\n Prokolla: %s\n Kortti: %s\n Paikkallispuhelinumero: %s\n\n Valitse asetus jota haluat muuttaa tai valitset käytä jatkaaksesi nykyisten asetusten käyttöä.",
/* TR_KEYBOARD_MAPPING */
"Näppäimistöasettelu",
/* TR_KEYBOARD_MAPPING_LONG */
"Valitse näppäimistöasettelu:",
/* TR_LEASED_LINE */
"Varattu linja",
/* TR_LOADING_MODULE */
"Ladataan modulia...",
/* TR_LOADING_PCMCIA */
"Lataan PCMCIA-modulit...",
/* TR_LOOKING_FOR_NIC */
"Etsitään: %s",
/* TR_MAKING_BOOT_FILESYSTEM */
"Luodaan käynnistystiedostojärjestelmä...",
/* TR_MAKING_LOG_FILESYSTEM */
"Luodaan loki tiedostojärjestelmä...",
/* TR_MAKING_ROOT_FILESYSTEM */
"Luodaan juuritiedostojärjestelmä...",
/* TR_MAKING_SWAPSPACE */
"Luodaan välimuistitila (swap)...",
/* TR_MANUAL */
"* KÄSIN *",
/* TR_MAX_LEASE */
"Maksimi varausaika (min):",
/* TR_MAX_LEASE_CR */
"Maksimi varausaika\n",
/* TR_MISSING_BLUE_IP */
"SINISEN-liitännän IP-osoite puuttuu.",
/* TR_MISSING_ORANGE_IP */
"ORANSSIN-liitännän IP-osoite puuttuu.",
/* TR_MISSING_RED_IP */
"PUNAISEN-liitännän IP-osoite puuttuu.",
/* TR_MODULE_NAME_CANNOT_BE_BLANK */
"Modulin nimi ei voi olla tyhjä.",
/* TR_MODULE_PARAMETERS */
"Syötä asennettavan modulin nimi ja parametrit.",
/* TR_MOUNTING_BOOT_FILESYSTEM */
"Otetaan käyttöön käynnistys-tiedostojärjestelmä...",
/* TR_MOUNTING_LOG_FILESYSTEM */
"Otetaan käyttöön loki-tiedostojärjestelmä...",
/* TR_MOUNTING_ROOT_FILESYSTEM */
"Otetaan käyttöön juuritiedostojärjestelmä...",
/* TR_MOUNTING_SWAP_PARTITION */
"Otetaan käyttöön välimuisti-tila (swap)...",
/* TR_MSN_CONFIGURATION */
"Paikallispuhelinumero (MSN(EAZ)",
/* TR_NETMASK_PROMPT */
"Verkkopeite:",
/* TR_NETWORKING */
"Verkotus",
/* TR_NETWORK_ADDRESS_CR */
"Verkko-osoite\n",
/* TR_NETWORK_ADDRESS_PROMPT */
"Verkko-osoite:",
/* TR_NETWORK_CONFIGURATION_MENU */
"Verkkoasetusten valikko",
/* TR_NETWORK_CONFIGURATION_TYPE */
"Verkkoasennuksen tyyppi",
/* TR_NETWORK_CONFIGURATION_TYPE_LONG */
"Valitse %s:n verkkoasetukset. Seuraavat asetusvaihtoehdot näyttävät ne liitännät joihin verkko on kytkettynä. Mikäli muutat valintaa, käynnistetään verkkoyhteydet uudelleen ja ajurit tulee kohdentaa uudelleen.",
/* TR_NETWORK_MASK_CR */
"Verkkopeite\n",
/* TR_NETWORK_SETUP_FAILED */
"Verkon asentaminen epäonnistui.",
/* TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED */
"Kortteja ei löytynyt riittävää määrää.",
/* TR_NO_BLUE_INTERFACE */
"SINISTÄ-liityntää ei ole asetettu..",
/* TR_NO_CDROM */
"CD-ROM-asemaa ei löydy.",
/* TR_NO_HARDDISK */
"Kiintolevyä ei löydy.",
/* TR_NO_IPCOP_TARBALL_FOUND */
"WWW-palvelimelta ei löydy IpCOpin tar-pakettia.",
/* TR_NO_ORANGE_INTERFACE */
"ORANSSIlle yhteydelle ei ole määrätty verkkokorttia.",
/* TR_NO_RED_INTERFACE */
"PUNAISTA-liitäntää ei ole asetettu.",
/* TR_NO_SCSI_IMAGE_FOUND */
"WWW-palvelimelta ei löydy SCSI-imagea.",
/* TR_NO_UNALLOCATED_CARDS */
"Vapaita kortteja ei ole jäljellä vaikka lisää pitäisi olla. Voit antaa automaattihaun etsiä lisää kortteja tai voit valita ajurin listasta.",
/* TR_OK */
"Ok",
/* TR_PARTITIONING_DISK */
"Osioidaan kiintolevy...",
/* TR_PASSWORDS_DO_NOT_MATCH */
"Salasanat eivät täsmää.",
/* TR_PASSWORD_CANNOT_BE_BLANK */
"Salasana ei voi olla tyhjä.",
/* TR_PASSWORD_CANNOT_CONTAIN_SPACES */
"Salasanassa ei voi käyttää välilyöntejä.",
/* TR_PASSWORD_PROMPT */
"Salasana:",
/* TR_PHONENUMBER_CANNOT_BE_EMPTY */
"Puhelinnumero ei voi olla tyhjä.",
/* TR_PREPARE_HARDDISK */
"Seuraavaksi asennusohjelma valmistelee %s:n kiintolevyn asennusta varten. Ensin kiintolevy osioidaan ja sen jälkeen osioille rakennetaan tiedostojärjestelmät.",
/* TR_PRESS_OK_TO_REBOOT */
"Valitse OK käynnistääksesi uudelleen.",
/* TR_PRIMARY_DNS */
"Ensisijainen DNS-palvelin:",
/* TR_PRIMARY_DNS_CR */
"Ensisijainen DNS-palvelin\n",
/* TR_PROBE */
"Tunnista",
/* TR_PROBE_FAILED */
"Automaattinen tunnistus epäonnistui.",
/* TR_PROBING_SCSI */
"Etsitään SCSI-laitteita...",
/* TR_PROBLEM_SETTING_ADMIN_PASSWORD */
"%s:n admin salasanan asettaminen ei onnistu.",
/* TR_PROBLEM_SETTING_ROOT_PASSWORD */
"Root-käyttäjän salasanan asettaminen ei onnistu.",
/* TR_PROBLEM_SETTING_SETUP_PASSWORD */
"Setup-käyttäjän salasanan asettamien ei onnistu.",
/* TR_PROTOCOL_COUNTRY */
"Protokolla/Maa",
/* TR_PULLING_NETWORK_UP */
"Käynnistetään verkkoyhteydet...",
/* TR_PUSHING_NETWORK_DOWN */
"Suljetaan verkkoyhteydet...",
/* TR_PUSHING_NON_LOCAL_NETWORK_DOWN */
"Suljetaan ulkoiset verkkoyhteydet...",
/* TR_QUIT */
"Lopeta",
/* TR_RED_IN_USE */
"ISDN (tai muu ulkoinen yhteys) on käytössä. Et voi muuttaa ISDN-asetuksia kun PUNAINEN-liitäntä on käytössä.",
/* TR_RESTART_REQUIRED */
"\n\nAsennuksen jälkeen verkkoyhteydet on käynnistettävä uudelleen.",
/* TR_RESTORE */
"Palauta",
/* TR_RESTORE_CONFIGURATION */
"Mikäli levyasemaan laitetussa levykkeessä on %s:n asetukset voit palauttaa ne käyttöön klikkaamalla Palauta-painiketta.",
/* TR_ROOT_PASSWORD */
"'root' salasana",
/* TR_SECONDARY_DNS */
"Toissijainen DNS-palvelin:",
/* TR_SECONDARY_DNS_CR */
"Toissijainen DNS-palvelin\n",
/* TR_SECONDARY_WITHOUT_PRIMARY_DNS */
"Toissijainen DNS-palvelin määritelty ilman ensisijaista DNS-palvelinta",
/* TR_SECTION_MENU */
"Kappalevalikko",
/* TR_SELECT */
"Valitse",
/* TR_SELECT_CDROM_TYPE */
"Valitse CDROM-tyyppi",
/* TR_SELECT_CDROM_TYPE_LONG */
"Tietokoneesta ei löyty CDROM-asemaa. Valitse seuraavista yhteensopiva ajuri, jolla %s pystyy käyttämään CDROM-asemaa.",
/* TR_SELECT_INSTALLATION_MEDIA */
"Valitse asennusväline",
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
"%s voidaan asentaa useasta lähteestä. Helpoin tapa on käyttää tietokoneen CDROM-asemaa. Mikäli sitä ei ole käytettävissä, voit asentaa myös verkon kautta toisesta koneesta kunhan tiedostot ovat saatavissa HTTP-protokollaa käyttämäällä. Tällöin tarvitset verkkokortin ajurilevykkeen.",
/* TR_SELECT_NETWORK_DRIVER */
"Valitse verkkokortin ajuri",
/* TR_SELECT_NETWORK_DRIVER_LONG */
"Valitse tietokoneeseesi asennetun verkkokortin ajuri. Mikäli valitset KÄSIN, sinulla on mahdollisuus syöttää  parametrit, joita tarvitsevat mm. ISA-väyläiset ajurit.",
/* TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE */
"Valitse uudelleen määriteltävä liitäntä.",
/* TR_SELECT_THE_ITEM */
"Valitse määriteltävä kohde.",
/* TR_SETTING_ADMIN_PASSWORD */
"Asetetaan %s admin-salasana...",
/* TR_SETTING_ROOT_PASSWORD */
"Asetetaan 'root' salasanaa....",
/* TR_SETTING_SETUP_PASSWORD */
"Asetetaan 'setup' salasanaa....",
/* TR_SETUP_FINISHED */
"Asennus on valmis. Valitse OK käynnistääksesi uudelleen.",
/* TR_SETUP_NOT_COMPLETE */
"Asennusta ei suoritettu loppuun. Varmista asennuksen onnistuminen suorittamalla asennus (Setup) uudelleen komentoriviltä.",
/* TR_SETUP_PASSWORD */
"'setup' salasana",
/* TR_SET_ADDITIONAL_MODULE_PARAMETERS */
"Modulin lisäasetukset",
/* TR_SINGLE_GREEN */
"Sinulla on käytössä yhden VIHREÄN liitännän asetukset",
/* TR_SKIP */
"Ohita",
/* TR_START_ADDRESS */
"Ensimmäinen osoite:",
/* TR_START_ADDRESS_CR */
"Alkuosoite\n",
/* TR_STATIC */
"Kiinteä",
/* TR_SUGGEST_IO */
"(oletus %x)",
/* TR_SUGGEST_IRQ */
"(oletus %d)",
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
"Ajurimoduli on jo ladattu.",
/* TR_TIMEZONE */
"Aikavyöhyke",
/* TR_TIMEZONE_LONG */
"Valitse aikavyöhyke listasta.",
/* TR_UNABLE_TO_EJECT_CDROM */
"CD-levyn poistaminen CDROM-asemasta ei onnistu.",
/* TR_UNABLE_TO_EXTRACT_MODULES */
"Modulien purkaminen ei onnistu.",
/* TR_UNABLE_TO_FIND_ANY_ADDITIONAL_DRIVERS */
"Lisäajureita ei löydy.",
/* TR_UNABLE_TO_FIND_AN_ISDN_CARD */
"Tietokoneesta ei löydy ISDN-korttia. Mikäli ISDN-korttisi kytketään ISA-väylään tai se tarvitsee erikoisasetuksia kokeile lisätä ajurimodulille sopivat parametrit.",
/* TR_UNABLE_TO_INITIALISE_ISDN */
"ISDN:n alustus ei onnistu.",
/* TR_UNABLE_TO_INSTALL_FILES */
"Tiedostojen asennus ei onnistu.",
/* TR_UNABLE_TO_INSTALL_GRUB */
"GRUB:n asennus ei onnistu.",
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
"Ajurimodulien lataus ei onnistu.",
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
"Käynnistystiedostojärjestelmän (BOOT) luonti ei onnistu.",
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
"Loki-tiedostojärjestelmän luonti ei onnistu.",
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
"Juuri-tiedostojärjestelmän luonti ei onnistu.",
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
"Välimuisti-tilan (swap) luonti ei onnistu.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
"Symbolisen linkin /dev/harddisk luonti ei onnistu .",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
"Symbolisen linkin /dev/harddisk1 luonti ei onnistu .",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
"Symbolisen linkin /dev/harddisk2 luonti ei onnistu .",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
"Symbolisen linkin /dev/harddisk3 luonti ei onnistu.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
"Symbolisen linkin  /dev/harddisk4 luonti ei onnistu.",
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
"Symbolisen linkin  /dev/root luonti ei onnistu.",
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
"Käynnistys-tiedostojärjestelmään yhdistäminen ei onnistu.",
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
"Log´ki-tiedostojärjestelmään yhdistäminen ei onnistu.",
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
"Proc-tiedostojärjestelmään yhdistäminen ei onnistu.",
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
"Juuri-tiedostojärjestelmään yhdistäminen ei onnistu.",
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
"Välimuisti-tilan (swap) käyttöönotto ei onnistu.",
/* TR_UNABLE_TO_OPEN_HOSTS_FILE */
"Tiedostoa 'hosts' ei pystytä avamaan.",
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
"Asetustiedoston avaaminen ei onnistu.",
/* TR_UNABLE_TO_PARTITION */
"Levyn osioiminen ei onnistu.",
/* TR_UNABLE_TO_REMOVE_TEMP_FILES */
"Ladattujen tilapäistiedostojen poisto ei onnistu.",
/* TR_UNABLE_TO_SET_HOSTNAME */
"Isäntänimeä ei voi asettaa.",
/* TR_UNABLE_TO_UNMOUNT_CDROM */
"Ei voi katkaista yhteyttä CDROM/levyasema.",
/* TR_UNABLE_TO_UNMOUNT_HARDDISK */
"Ei voi katkaista yhteyttä harddisk.",
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */
"Ei voi kirjoittaa /etc/fstab ",
/* TR_UNABLE_TO_WRITE_ETC_HOSTNAME */
"Ei voi kirjoittaa /etc/hostname",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS */
"Ei voi kirjoittaa /etc/hosts.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW */
"Ei voi kirjoittaa /etc/hosts.allow.",
/* TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY */
"Ei voi kirjoittaa /etc/hosts.deny.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_ETHERNET_SETTINGS */
"Ei voi kirjoittaa %s/ethernet/settings.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF */
"Ei voi kirjoittaa %s/main/hostname.conf.",
/* TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_SETTINGS */
"Ei voi kirjoitaa %s/main/settings.",
/* TR_UNCLAIMED_DRIVER */
"Järjestelmässä on käyttämön ethernet-liitäntä: \n%s\n\nVoit asettaa sen käytettäväksi:",
/* TR_UNKNOWN */
"TUNTEMATON",
/* TR_UNSET */
"ASETTAMATTA",
/* TR_USB_KEY_VFAT_ERR */
"This USB key is invalid (no vfat partition found).",
/* TR_US_NI1 */
"US NI1",
/* TR_WARNING */
"VAROITUS",
/* TR_WARNING_LONG */
"Mikäli olet IP-osoitetta vaihtaessasi etäyhteydessä yhteytesi %s:n katkeaa ja joudut avaamaan uuden yhteyden uudella IP-osoitteella. Tähän sisältyy omat riskinsä ja on suositeltavampaa suorittaa operaatio tietokoneen konsolilta.",
/* TR_WELCOME */
"Tervetuloa %s:n asennusohjelmaan. Mikäli valitset missä tahansa vaiheessa PERUUTA tietokone käynnistetään uudeelleen.",
/* TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER */
"Käytössäsi on asetukset yhdelle VIHREÄlle liitynnälle, jolla on jo ajuri valittuna.",
}; 
  
