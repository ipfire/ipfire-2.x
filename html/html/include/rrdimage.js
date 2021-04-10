/*#############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2021  IPFire Team  <info@ipfire.org>                     #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
#############################################################################*/

// "onclick" event handler for graph time range select button
// buttonObj: reference to the button
function rrdimage_selectRange(buttonObj) {
	if(! (buttonObj && ('range' in buttonObj.dataset))) {
		return; //required parameters are missing
	}

	// Get selected time range from button
	const range = buttonObj.dataset.range;
	
	// Get surrounding div box and select new range 
	let graphBox = $(buttonObj).closest('div');
	_rrdimg_setRange(graphBox, range);
}

// Document loaded: Process all graphs, start reload timers
$(function() {
	$('div.rrdimage').each(function() {
		let graphBox = $(this);
		_rrdimg_setRange(graphBox, graphBox.data('defaultRange'), true);
	});
});

//--- Internal functions ---

// Set or update graph time range, start automatic reloading
// graphBox: jQuery object, reference to graph div box
// range: time range (day, hour, ...)
// initMode: don't immediately reload graph, but force timers and attributes update
function _rrdimg_setRange(graphBox, range, initMode = false) {
	if(! ((graphBox instanceof jQuery) && (graphBox.length === 1))) {
		return; //graphBox element missing
	}

	// Check range parameter, default to "day" on error
	if(! ["hour", "day", "week", "month", "year"].includes(range)) {
		range = "day";
	}

	// Check if the time range is changed
	if((graphBox.data('range') !== range) || initMode) {
		graphBox.data('range', range); //Store new range
		
		// Update button highlighting
		graphBox.find('button').removeClass('selected');
		graphBox.find(`button[data-range="${range}"]`).addClass('selected');
	}

	// Clear pending reload timer to prevent multiple image reloads
	let timerId = graphBox.data('reloadTimer');
	if(timerId !== undefined) {
		window.clearInterval(timerId);
		graphBox.removeData('reloadTimer');
	}

	// Determine auto reload interval (in seconds),
	// interval = 0 disables auto reloading by default
	let interval = 0;
	switch(range) {
		case 'hour':
			interval = 60;
			break;

		case 'day':
		case 'week':
			interval = 300;
			break;
	}

	// Start reload timer and store reference
	if(interval > 0) {
		timerId = window.setInterval(function(graphRef) {
			_rrdimg_reload(graphRef);
		}, interval * 1000, graphBox);
		graphBox.data('reloadTimer', timerId);
	}

	// Always reload image unless disabled by init mode
	if(! initMode) {
		_rrdimg_reload(graphBox);
	}
}

// Reload graph image, add timestamp to prevent caching
// graphBox: jQuery object (graph element must be valid)
function _rrdimg_reload(graphBox) {
	const origin = graphBox.data('origin');
	const graph = graphBox.data('graph');	
	const timestamp = Date.now();

	// Get user selected range or fall back to default
	let range = graphBox.data('range');
	if(! range) {
		range = graphBox.data('defaultRange');
	}

	// Generate new image URL with timestamp
	const imageUrl = `/cgi-bin/getrrdimage.cgi?origin=${origin}&graph=${graph}&range=${range}&timestamp=${timestamp}`;

	// Get graph image and set new URL
	graphBox.children('img').first().attr('src', imageUrl);
}
