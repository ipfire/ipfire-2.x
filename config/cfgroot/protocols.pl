# Protocols Data File
#
# This file is part of the IPCop Firewall.
#
# IPCop is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# IPCop is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IPCop; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# (c) The IPCop Team
#
# $Id: protocols.pl,v 1.2.2.1 2005/01/26 12:23:20 riddles Exp $
#
# Generated from /etc/protocols using:
# cat /etc/protocols | grep -ve "^#" | grep -v "^$" | \
#    awk '{ print "\""  $1  "\" => \"" $2 "\","}'
#
# Code supplied by Mark Wormgroor
#

package Protocols;

%protocols = (
"ip" => "0",
"icmp" => "1",
"igmp" => "2",
"ggp" => "3",
"ipencap" => "4",
"st" => "5",
"tcp" => "6",
"cbt" => "7",
"egp" => "8",
"igp" => "9",
"bbn-rcc" => "10",
"nvp" => "11",
"pup" => "12",
"argus" => "13",
"emcon" => "14",
"xnet" => "15",
"chaos" => "16",
"udp" => "17",
"mux" => "18",
"dcn" => "19",
"hmp" => "20",
"prm" => "21",
"xns-idp" => "22",
"trunk-1" => "23",
"trunk-2" => "24",
"leaf-1" => "25",
"leaf-2" => "26",
"rdp" => "27",
"irtp" => "28",
"iso-tp4" => "29",
"netblt" => "30",
"mfe-nsp" => "31",
"merit-inp" => "32",
"sep" => "33",
"3pc" => "34",
"idpr" => "35",
"xtp" => "36",
"ddp" => "37",
"idpr-cmtp" => "38",
"tp++" => "39",
"il" => "40",
"ipv6" => "41",
"sdrp" => "42",
"ipv6-route" => "43",
"ipv6-frag" => "44",
"idrp" => "45",
"rsvp" => "46",
"gre" => "47",
"mhrp" => "48",
"bna" => "49",
"ipv6-crypt" => "50",
"ipv6-auth" => "51",
"i-nlsp" => "52",
"swipe" => "53",
"narp" => "54",
"mobile" => "55",
"tlsp" => "56",
"skip" => "57",
"ipv6-icmp" => "58",
"ipv6-nonxt" => "59",
"ipv6-opts" => "60",
"cftp" => "62",
"sat-expak" => "64",
"kryptolan" => "65",
"rvd" => "66",
"ippc" => "67",
"sat-mon" => "69",
"visa" => "70",
"ipcv" => "71",
"cpnx" => "72",
"cphb" => "73",
"wsn" => "74",
"pvp" => "75",
"br-sat-mon" => "76",
"sun-nd" => "77",
"wb-mon" => "78",
"wb-expak" => "79",
"iso-ip" => "80",
"vmtp" => "81",
"secure-vmtp" => "82",
"vines" => "83",
"ttp" => "84",
"nsfnet-igp" => "85",
"dgp" => "86",
"tcf" => "87",
"eigrp" => "88",
"ospf" => "89",
"sprite-rpc" => "90",
"larp" => "91",
"mtp" => "92",
"ax.25" => "93",
"ipip" => "94",
"micp" => "95",
"scc-sp" => "96",
"etherip" => "97",
"encap" => "98",
"gmtp" => "100",
"ifmp" => "101",
"pnni" => "102",
"pim" => "103",
"aris" => "104",
"scps" => "105",
"qnx" => "106",
"a/n" => "107",
"ipcomp" => "108",
"snp" => "109",
"compaq-peer" => "110",
"ipx-in-ip" => "111",
"vrrp" => "112",
"pgm" => "113",
"l2tp" => "115",
"ddx" => "116",
"iatp" => "117",
"stp" => "118",
"srp" => "119",
"uti" => "120",
"smp" => "121",
"sm" => "122",
"ptp" => "123",
"isis" => "124",
"fire" => "125",
"crtp" => "126",
"crdup" => "127",
"sscopmce" => "128",
"iplt" => "129",
"sps" => "130",
"pipe" => "131",
"sctp" => "132",
"fc" => "133",
);
