/* refreshInetInfo.js
* functions for retrieving status information via jQuery
* Modified: March 6th, 2013 by michael@koehler.tk
* Authors: 	IPFire Team (info@ipfire.org)
			Kay-Michael Köhler (michael@koehler.tk)
* Visit http://www.ipfire.org/
*/

var t_current;
var t_last = 0;
var rxb_current;
var rxb_last = 0;
var txb_current;
var txb_last = 0;

$(document).ready(function(){
	refreshInetInfo();
});

function refreshInetInfo() {
	$.ajax({
		url: '/cgi-bin/speed.cgi',
		success: function(xml) {
			t_current = new Date();
			var t_diff = t_current - t_last;

			rxb_current = $("rxb", xml).text();
			var rxb_diff = rxb_current - rxb_last;
			rxb_last = rxb_current;

			var rx_bits = rxb_diff * 8192 / t_diff;
			var rx_fmt = format_bytes(rx_bits);

			txb_current = $("txb", xml).text();
			var txb_diff = txb_current - txb_last;
			txb_last = txb_current;

			var tx_bits = txb_diff * 8192 / t_diff;
			var tx_fmt = format_bytes(tx_bits);

			if (t_last != 0) {
				$("#rx_kbs").text(rx_fmt);
				$("#tx_kbs").text(tx_fmt);
			}

			t_last = t_current;
		}
	});

	window.setTimeout("refreshInetInfo()", 2000);
}

function format_bytes(bytes) {
	var units = ["bit/s", "kbit/s", "Mbit/s", "Gbit/s", "Tbit/s"];

	var unit = units[0];
	for (var i = 1; i < units.length; i++) {
		if (bytes < 1024)
			break;

		unit = units[i];
		bytes /= 1024;
	}

	// Round the output.
	bytes = bytes.toFixed(2);

	return bytes + " " + unit;
}
