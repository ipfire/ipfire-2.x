#!/usr/bin/perl
#
# EMBCop CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) Michel Schaaf
#
# $Id: netconfig.cgi,v 1.11.2.27 2005/10/27 07:40:14 schaaf Exp $
#

use strict;

# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %cgiparams=();
$cgiparams{'ACTION'} = '';
&Header::getcgihash(\%cgiparams);

my %ethsettings = ();
&General::readhash("${General::swroot}/ethernet/settings", \%ethsettings);

my $key = ();

my %net_config_type = (0 => "GREEN (RED is modem/ISDN)",
1 => "GREEN + ORANGE (RED is modem/ISDN)",
2 => "GREEN + RED",
3 => "GREEN + ORANGE + RED",
4 => "GREEN + BLUE (RED is modem/ISDN)",
5 => "GREEN + ORANGE + BLUE (RED is modem/ISDN)",
6 => "GREEN + BLUE + RED",
7 => "GREEN + ORANGE + BLUE + RED");

my %landevice = ("eth0", "eth1", "eth2", "eth3");
my %types = ("STATIC", "DHCP", "PPPOE", "PPTP");

my $dev_name = ();

my %nic = (
"100VG-AnyLan Network Adapters, HP J2585B, J2585A, etc" => "hp100" ,
"3Com EtherLink III" => "3c509" ,
"3Com 3c501" => "3c501" ,
"3Com ISA EtherLink XL" => "3c515" ,
"3Com 3c503 and 3c503/16" => "3c503" ,
"3Com EtherLink MC (3c523)" => "3c523" ,
"3Com EtherLink MC/32 (3c527)" => "3c527" ,
"3Com EtherLink Plus (3c505)" => "3c505" ,
"3Com EtherLink 16" => "3c507" ,
"3Com Corkscrew EtherLink PCI III/XL etc." => "3c59x" ,
"3Com Typhoon Family (3C990 3CR990 and variants)" => "typhoon" ,
"Adaptec Starfire/DuraLAN" => "starfire" ,
"Alteon AceNIC/3Com 3C985/Netgear GA620 Gigabit" => "acenic" ,
"AMD8111 based 10/100 Ethernet Controller" => "amd8111e" ,
"AMD LANCE/PCnetAllied Telesis AT1500,  J2405A, etc" => "lance" ,
"AMD PCnet32 and AMD PCnetPCI" => "pcnet32" ,
"Ansel Communications EISA 3200" => "ac3200" ,
"Apricot 680x0 VME, 82596 chipset" => "82596" ,
"AT1700/1720" => "at1700" ,
"Broadcom 4400" => "b44" ,
"Broadcom Tigon3" => "tg3" ,
"Cabletron E2100 series ethercards" => "e2100" ,
"CATC USB NetMate-based Ethernet" => "catc" ,
"CDC USB Ethernet" => "CDCEther" ,
"Crystal LAN CS8900/CS8920" => "cs89x0" ,
"Compaq Netelligent 10/100 TX PCI UTP, etc" => "tlan" ,
"D-Link DL2000-based Gigabit Ethernet" => "dl2k" ,
"Digi Intl. RightSwitch SE-X EISA and PCI" => "dgrs" ,
"Digital 21x4x Tulip PCI ethernet cards, etc." => "tulip" ,
"Digital DEPCA & EtherWORKS,DEPCA, DE100, etc" => "depca" ,
"DM9102 PCI Fast Ethernet Adapter" => "dmfe" ,
"Dummy Network Card (testing)" => "dummy" ,
"EtherWORKS DE425 TP/COAX EISA, DE434 TP PCI, etc." => "de4x5" ,
"EtherWORKS 3 (DE203, DE204 and DE205)" => "ewrk3" ,
"HP PCLAN/plus" => "hp-plus" ,
"HP LAN ethernet" => "hp" ,
"IBM LANA" => "ibmlana" ,
"ICL EtherTeam 16i/32" ,"eth16i" ,
"Intel i82557/i82558 PCI EtherExpressPro" => "e100" ,
"Intel EtherExpress Cardbus Ethernet" => "eepro100_cb" ,
"Intel i82595 ISA EtherExpressPro10/10+ driver" ,"eepro" ,
"Intel EtherExpress 16 (i82586)" => "eexpress" ,
"Intel Panther onboard i82596 driver" => "lp486e" ,
"Intel PRO/1000 Gigabit Ethernet" => "e1000" ,
"KLSI USB KL5USB101-based" => "kaweth" ,
"MiCom-Interlan NI5010 ethercard" => "ni5010" ,
"Mylex EISA LNE390A/B" => "lne390" ,
"Myson MTD-8xx PCI Ethernet" => "fealnx" ,
"National Semiconductor DP8381x" => "natsemi" ,
"National Semiconductor DP83820" => "ns83820" ,
"NE/2 MCA" => "ne2" ,
"NE2000 PCI cards, RealTEk RTL-8029, etc" => "ne2k-pci" ,
"NE1000 / NE2000 (non-pci)" => "ne" ,
"NI50 card (i82586 Ethernet chip)" => "ni52" ,
"NI6510, ni6510 EtherBlaster" => "ni65" ,
"Novell/Eagle/Microdyne NE3210 EISA" => "ne3210" ,
"NVidia Nforce2 Driver" => "forcedeth" ,
"Packet Engines Hamachi GNIC-II" => "hamachi" ,
"Packet Engines Yellowfin Gigabit-NIC" => "yellowfin" ,
"Pegasus/Pegasus-II USB ethernet" => "pegasus" ,
"PureData PDUC8028,WD8003 and WD8013 compatibles" => "wd" ,
"Racal-Interlan EISA ES3210" => "es3210" ,
"RealTek RTL-8139 Fast Ethernet" => "8139too" ,
"RealTek RTL-8139C+ series 10/100 PCI Ethernet" => "8139cp" ,
"RealTek RTL-8150 USB ethernet" => "rtl8150" ,
"RealTek RTL-8169 Gigabit Ethernet" => "r8169" ,
"SiS 900 PCI" => "sis900" ,
"SKnet MCA" => "sk_mca" ,
"SMC 9000 series of ethernet cards" => "smc9194" ,
"SMC EtherPower II" => "epic100" ,
"SMC Ultra/EtherEZ ISA/PnP Ethernet" => "smc-ultra" ,
"SMC Ultra32 EISA Ethernet" => "smc-ultra32" ,
"SMC Ultra MCA Ethernet" => "smc-mca" ,
"Sundance Alta" => "sundance" ,
"SysKonnect SK-98xx" => "sk98lin" ,
"Toshiba TC35815 Ethernet" => "tc35815" ,
"Tulip chipset Cardbus Ethernet" => "tulip_cb" ,
"USB Ethernet" => "usbnet" ,
"VIA Rhine PCI Fast Ethernet, etc" => "via-rhine" ,
"Winbond W89c840 Ethernet" => "winbond-840" ,
"Xircom Cardbus Ethernet" => "xircom_cb" ,
"Xircom (tulip-like) Cardbus Ethernet" => "xircom_tulip_cb" );

if ($cgiparams{'ACTION'} eq $Lang::tr{'save'}) {
$ethsettings{'CONFIG_TYPE'} = $cgiparams{'CONFIG_TYPE'};
$ethsettings{'GREEN_ADDRESS'} = $cgiparams{'GREEN_ADDRESS'};
$ethsettings{'GREEN_NETMASK'} = $cgiparams{'GREEN_NETMASK'};
$ethsettings{'GREEN_DRIVER'} = $cgiparams{'GREEN_DRIVER'};
$ethsettings{'GREEN_DRIVER_OPTIONS'} = $cgiparams{'GREEN_DRIVER_OPTIONS'};
$ethsettings{'GREEN_DEV'} = $cgiparams{'GREEN_DEV'};
$ethsettings{'GREEN_BROADCAST'} = $cgiparams{'GREEN_BROADCAST'};
$ethsettings{'GREEN_NETADDRESS'} = $cgiparams{'GREEN_NETADDRESS'};
$ethsettings{'RED_ADDRESS'} = $cgiparams{'RED_ADDRESS'};
$ethsettings{'RED_NETMASK'} = $cgiparams{'RED_NETMASK'};
$ethsettings{'RED_DRIVER'} = $cgiparams{'RED_DRIVER'};
$ethsettings{'RED_DRIVER_OPTIONS'} = $cgiparams{'RED_DRIVER_OPTIONS'};
$ethsettings{'RED_DEV'} = $cgiparams{'RED_DEV'};
$ethsettings{'RED_BROADCAST'} = $cgiparams{'RED_BROADCAST'};
$ethsettings{'RED_TYPE'} = $cgiparams{'RED_TYPE'};
$ethsettings{'RED_NETADDRESS'} = $cgiparams{'RED_NETADDRESS'};
$ethsettings{'ORANGE_ADDRESS'} = $cgiparams{'ORANGE_ADDRESS'};
$ethsettings{'ORANGE_NETMASK'} = $cgiparams{'ORANGE_NETMASK'};
$ethsettings{'ORANGE_DRIVER'} = $cgiparams{'ORANGE_DRIVER'};
$ethsettings{'ORANGE_DRIVER_OPTIONS'} = $cgiparams{'ORANGE_DRIVER_OPTIONS'};
$ethsettings{'ORANGE_DEV'} = $cgiparams{'ORANGE_DEV'};
$ethsettings{'ORANGE_BROADCAST'} = $cgiparams{'ORANGE_BROADCAST'};
$ethsettings{'ORANGE_NETADDRESS'} = $cgiparams{'ORANGE_NETADDRESS'};
$ethsettings{'BLUE_ADDRESS'} = $cgiparams{'BLUE_ADDRESS'};
$ethsettings{'BLUE_NETMASK'} = $cgiparams{'BLUE_NETMASK'};
$ethsettings{'BLUE_DRIVER'} = $cgiparams{'BLUE_DRIVER'};
$ethsettings{'BLUE_DRIVER_OPTIONS'} = $cgiparams{'BLUE_DRIVER_OPTIONS'};
$ethsettings{'BLUE_DEV'} = $cgiparams{'BLUE_DEV'};
$ethsettings{'BLUE_BROADCAST'} = $cgiparams{'BLUE_BROADCAST'};
$ethsettings{'BLUE_NETADDRESS'} = $cgiparams{'BLUE_NETADDRESS'};

&General::writehash("${General::swroot}/ethernet/settings", \%ethsettings);
}

&Header::showhttpheaders();

&Header::openpage($Lang::tr{'net config'}, 1, '');

&Header::openbigbox('100%', 'center');

&Header::openbox('100%', 'left', $Lang::tr{'net config'});

print <<END
<b>$Lang::tr{'net config type'}</b>
<form method="POST" action="netconfig.cgi">
<table width=100%>
<tr>
<td valign=top>
<select name="CONFIG_TYPE">
END
;

foreach my $k (sort keys %net_config_type){
	if ($k eq $ethsettings{'CONFIG_TYPE'}){
	print "<option value=\"$k\" selected>$net_config_type{$k}</option>";}else{
	print "<option value=\"$k\">$net_config_type{$k}</option>";}
}
print <<END
</select>
</td>
<td valign=top>$Lang::tr{'net config type help'}</td>
<td valign=top align=right><input type="reset" name="ACTION" value="$Lang::tr{'reset'}"><input type="submit" name="ACTION" value="$Lang::tr{'save'}"></td>
</tr>
</table>
END
;

print <<END
<hr><b>GREEN</b><br />
<table width=100%><tr>
<td width=12%>$Lang::tr{'ip address'}:</td>
<td width=12%><input type=text name="GREEN_ADDRESS" value="$ethsettings{'GREEN_ADDRESS'}" size=15></td>
<td width=12%>$Lang::tr{'netmask'}:</td>
<td width=12%><input type=text name="GREEN_NETMASK" value="$ethsettings{'GREEN_NETMASK'}" size=15></td>
<td>
$Lang::tr{'net address'}:
</td>
<td>
<input type=text name="GREEN_NETADDRESS" value="$ethsettings{'GREEN_NETADDRESS'}" size=15/>
</td>
</tr>
<tr>
<td>$Lang::tr{'broadcast'}:</td>
<td><input type=text name="GREEN_BROADCAST" value="$ethsettings{'GREEN_BROADCAST'}" size=15></td>
<td>$Lang::tr{'device'}:</td>
<td><select name="GREEN_DEV">
END
;

foreach (sort %landevice){
        if ($_ eq $ethsettings{'GREEN_DEV'}){
        print "<option value=\"$_\" selected>$_</option>";}else{
        print "<option value=\"$_\">$_</option>";}
}

print <<END
</select>
<td width=12%>$Lang::tr{'driver'}:$ethsettings{'GREEN_DRIVER'}</td>
<td width=40%><select name=GREEN_DRIVER>
END
;

foreach (sort keys %nic){
        if ($nic{$_} eq $ethsettings{'GREEN_DRIVER'}){
        print "<option value=\"$nic{$_}\" selected>$_</option>";}else{
        print "<option value=\"$nic{$_}\">$_</option>";}
}
print <<END
</select>
</tr>
<tr>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>$Lang::tr{'options'}:</td>
<td><input type=text name="GREEN_DRIVER_OPTIONS" value="$ethsettings{'GREEN_DRIVER_OPTIONS'}" size=45></td>
</tr>
</table>
<hr>
END
;

if ($ethsettings{'CONFIG_TYPE'} =~ /^(2|3|6|7)$/){
print <<END
<hr><b>RED</b><br />
<table width=100%><tr>
<td width=12%>$Lang::tr{'ip address'}:</td>
<td width=12%><input type=text name="RED_ADDRESS" value="$ethsettings{'RED_ADDRESS'}" size=15></td>
<td width=12%>$Lang::tr{'netmask'}:</td>
<td width=12%><input type=text name="RED_NETMASK" value="$ethsettings{'RED_NETMASK'}" size=15></td>
<td>$Lang::tr{'net address'}:</td>
<td><input type=text name="RED_NETADDRESS" value="$ethsettings{'RED_NETADDRESS'}" size=15/></td
</tr>
<tr>
<td>$Lang::tr{'device'}:</td>
<td><select name="RED_DEV">
END
;

foreach (sort %landevice){
        if ($_ eq $ethsettings{'RED_DEV'}){
        print "<option value=\"$_\" selected>$_</option>";}else{
        print "<option value=\"$_\">$_</option>";}
}

print <<END
</select>
</td>
<td>$Lang::tr{'broadcast'}:</td>
<td><input type=text name="RED_BROADCAST" value="$ethsettings{'RED_BROADCAST'}" size=15></td>
<td width=12%>$Lang::tr{'driver'}:$ethsettings{'RED_DRIVER'}</td>
<td width=40%><select name=RED_DRIVER>
END
;

foreach (sort keys %nic){
        if ($nic{$_} eq $ethsettings{'RED_DRIVER'}){
        print "<option value=\"$nic{$_}\" selected>$_</option>";}else{
        print "<option value=\"$nic{$_}\">$_</option>";}
}
print <<END
</select>
</tr><tr><td> $Lang::tr{'type'}:</td><td><select name="RED_TYPE">
END
;

foreach (sort %types){
        if ($_ eq $ethsettings{'RED_TYPE'}){
        print "<option value=\"$_\" selected>$_</option>";}else{
        print "<option value=\"$_\">$_</option>";}
}

print <<END
</select>
</td>
<td></td><td></td>
<td>$Lang::tr{'options'}:</td>
<td><input type=text name="RED_DRIVER_OPTIONS" value="$ethsettings{'RED_DRIVER_OPTIONS'}" size=45></td>
</tr>
</table>
<hr>
END
;

}

if ($ethsettings{'CONFIG_TYPE'} =~ /^(1|3|5|7)$/){
print <<END
<hr><b>ORANGE</b><br />
<table width=100%><tr>
<td width=12%>$Lang::tr{'ip address'}:</td>
<td width=12%><input type=text name="ORANGE_ADDRESS" value="$ethsettings{'ORANGE_ADDRESS'}" size=15></td>
<td width=12%>$Lang::tr{'netmask'}:</td>
<td width=12%><input type=text name="ORANGE_NETMASK" value="$ethsettings{'ORANGE_NETMASK'}" size=15></td>
<td>$Lang::tr{'net address'}:</td>
<td><input type=text name="ORANGE_NETADDRESS" value="$ethsettings{'ORANGE_NETADDRESS'}" size=15/></td>
</tr>
<tr>
<td>$Lang::tr{'device'}:</td>
<td><select name="ORANGE_DEV">
END
;

foreach (sort %landevice){
        if ($_ eq $ethsettings{'ORANGE_DEV'}){
        print "<option value=\"$_\" selected>$_</option>";}else{
        print "<option value=\"$_\">$_</option>";}
}

print <<END
</select>
</td>
<td>$Lang::tr{'broadcast'}:</td>
<td><input type=text name="ORANGE_BROADCAST" value="$ethsettings{'ORANGE_BROADCAST'}" size=15></td>
<td width=12%>$Lang::tr{'driver'}:$ethsettings{'ORANGE_DRIVER'}</td>
<td width=40%><select name=ORANGE_DRIVER>
END
;

foreach (sort keys %nic){
        if ($nic{$_} eq $ethsettings{'ORANGE_DRIVER'}){
        print "<option value=\"$nic{$_}\" selected>$_</option>";}else{
        print "<option value=\"$nic{$_}\">$_</option>";}
}
print <<END
</select>
</tr>
<tr>
<td></td><td></td>
<td></td><td></td>
<td>$Lang::tr{'options'}:</td>
<td><input type=text name="ORANGE_DRIVER_OPTIONS" value="$ethsettings{'ORANGE_DRIVER_OPTIONS'}" size=45></td>
</tr>
</table>
<hr>
END
;

}

if ($ethsettings{'CONFIG_TYPE'} =~ /^(4|5|6|7)$/){
print <<END
<hr><b>BLUE</b><br />
<table width=100%><tr>
<td width=12%>$Lang::tr{'ip address'}:</td>
<td width=12%><input type=text name="BLUE_ADDRESS" value="$ethsettings{'BLUE_ADDRESS'}" size=15></td>
<td width=12%>$Lang::tr{'netmask'}:</td>
<td width=12%><input type=text name="BLUE_NETMASK" value="$ethsettings{'BLUE_NETMASK'}" size=15></td>
<td>$Lang::tr{'net address'}:</td>
<td><input type=text name="BLUE_NETADDRESS" value="$ethsettings{'BLUE_NETADDRESS'}" size=15/></td>
</tr>
<tr>
<td>$Lang::tr{'device'}:</td>
<td><select name="BLUE_DEV">
END
;

foreach (sort %landevice){
        if ($_ eq $ethsettings{'BLUE_DEV'}){
        print "<option value=\"$_\" selected>$_</option>";}else{
        print "<option value=\"$_\">$_</option>";}
}

print <<END
</select>
</td>
<td>$Lang::tr{'broadcast'}:</td>
<td><input type=text name="BLUE_BROADCAST" value="$ethsettings{'BLUE_BROADCAST'}" size=15></td>
<td width=12%>$Lang::tr{'driver'}:$ethsettings{'BLUE_DRIVER'}</td>
<td width=40%><select name=BLUE_DRIVER>
END
;

foreach (sort keys %nic){
        if ($nic{$_} eq $ethsettings{'BLUE_DRIVER'}){
        print "<option value=\"$nic{$_}\" selected>$_</option>";}else{
        print "<option value=\"$nic{$_}\">$_</option>";}
}
print <<END
</select>
</td>
</tr>
<tr>
<td></td><td></td>
<td></td><td></td>
<td>$Lang::tr{'options'}:</td>
<td><input type=text name="BLUE_DRIVER_OPTIONS" value="$ethsettings{'BLUE_DRIVER_OPTIONS'}" size=45></td>
</tr>
</table>
<hr>
END
;

}

print <<END
</form>
END
;

&Header::closebox();

&Header::closebigbox();

&Header::closepage();
