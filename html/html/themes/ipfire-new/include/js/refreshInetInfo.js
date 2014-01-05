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
		success: function(xml){
			
			t_current = new Date();
			var t_diff = t_current - t_last;
			
			rxb_current = $("rxb",xml).text();
			var rxb_diff = rxb_current - rxb_last;
			rxb_last = rxb_current;

			var rx_kbs = rxb_diff/t_diff;
			rx_kbs = Math.round(rx_kbs*10)/10;

			txb_current = $("txb",xml).text();
			var txb_diff = txb_current - txb_last;
			txb_last = txb_current;

			var tx_kbs = txb_diff/t_diff;
			tx_kbs = Math.round(tx_kbs*10)/10;
			
			if (t_last != 0) {
				$("#rx_kbs").text(rx_kbs + ' kb/s');
				$("#tx_kbs").text(tx_kbs + ' kb/s');
				if ($("#bandwidthCalculationContainer").css('display') == 'none')
					$("#bandwidthCalculationContainer").css('display','block');
			}
			
			t_last = t_current;
		}
	});
	window.setTimeout("refreshInetInfo()", 2000);
}
