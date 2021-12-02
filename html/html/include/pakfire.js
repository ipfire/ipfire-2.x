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

"use strict";

// Pakfire Javascript functions (requires jQuery)
class PakfireJS {
	constructor() {
		//--- Public properties ---
		// Translation strings
		this.i18n = new PakfireI18N();

		//--- Private properties ---
		// Status flags (access outside constructor only with setter/getter)
		this._states = Object.create(null);
		this._states.running = false;
		this._states.reboot = false;

		// Status refresh helper
		this._autoRefresh = {
			delay: 1000, //Delay between requests (default: 1s)
			jsonAction: 'getstatus', //CGI POST action parameter
			timeout: 5000, //XHR timeout (5s)

			delayTimer: null, //setTimeout reference
			jqXHR: undefined, //jQuery.ajax promise reference
			get runningDelay() { //Waiting for end of delay
				return (this.delayTimer !== null);
			},
			get runningXHR() { //Waiting for CGI response
				return (this.jqXHR && (this.jqXHR.state() === 'pending'));
			},
			get isRunning() {
				return (this.runningDelay || this.runningXHR);
			}
		};
	}

	//### Public properties ###

	// Pakfire is running (true/false)
	set running(state) {
		if(this._states.running !== state) {
			this._states.running = state;
			this._states_onChange('running');
		}
	}
	get running() {
		return this._states.running;
	}

	// Reboot needed (true/false)
	set reboot(state) {
		if(this._states.reboot !== state) {
			this._states.reboot = state;
			this._states_onChange('reboot');
		}
	}
	get reboot() {
		return this._states.reboot;
	}

	// Status refresh interval in ms
	set refreshInterval(delay) {
		if(delay < 500) {
			delay = 500; //enforce reasonable minimum
		}
		this._autoRefresh.delay = delay;
	}
	get refreshInterval() {
		return this._autoRefresh.delay;
	}

	// Document loaded (call once from jQuery.ready)
	documentReady() {
		// Status refresh late start
		if(this.running && (! this._autoRefresh.isRunning)) {
			this._autoRefresh_runNow();
		}
	}

	//### Private properties ###

	// Pakfire status change handler
	// property: Affected status (running, reboot, ...)
	_states_onChange(property) {
		// Always update UI
		if(this.running) {
			$('#pflog-status').text(this.i18n.get('working'));
			$('#pflog-action').empty();
		} else {
			$('#pflog-status').text(this.i18n.get('finished'));
			if(this.reboot) { //Enable return or reboot links in UI
				$('#pflog-action').html(this.i18n.get('link_reboot'));
			} else {
				$('#pflog-action').html(this.i18n.get('link_return'));
			}
		}

		// Start/stop status refresh if Pakfire started/stopped
		if(property === 'running') {
			if(this.running) {
				this._autoRefresh_runNow();
			} else {
				this._autoRefresh_clearSchedule();
			}
		}
	}

	//--- Status refresh scheduling functions ---

	// Immediately perform AJAX status refresh request
	_autoRefresh_runNow() {
		if(this._autoRefresh.runningXHR) {
			return; // Don't send multiple requests
		}
		this._autoRefresh_clearSchedule(); // Stop scheduled refresh, will send immediately

		// Send AJAX request, attach listeners
		this._autoRefresh.jqXHR = this._JSON_get(this._autoRefresh.jsonAction, this._autoRefresh.timeout);
		this._autoRefresh.jqXHR.done(function() { // Request succeeded
			if(this.running) { // Keep refreshing while Pakfire is running
				this._autoRefresh_scheduleRun();
			}
		});
		this._autoRefresh.jqXHR.fail(function() { // Request failed
			this._autoRefresh_scheduleRun(); // Try refreshing until valid status is received
		});
	}

	// Schedule next refresh
	_autoRefresh_scheduleRun() {
		if(this._autoRefresh.runningDelay || this._autoRefresh.runningXHR) {
			return; // Refresh already scheduled or in progress
		}
		this._autoRefresh.delayTimer = window.setTimeout(function() {
			this._autoRefresh.delayTimer = null;
			this._autoRefresh_runNow();
		}.bind(this), this._autoRefresh.delay);
	}

	// Stop scheduled refresh (can still be refreshed up to 1x if XHR is already sent)
	_autoRefresh_clearSchedule() {
		if(this._autoRefresh.runningDelay) {
			window.clearTimeout(this._autoRefresh.delayTimer);
			this._autoRefresh.delayTimer = null;
		}
	}

	//--- JSON request & data handling ---

	// Load JSON data from Pakfire CGI, using a POST request
	// action: POST paramter "json-[action]"
	// maxTime: XHR timeout, 0 = no timeout
	_JSON_get(action, maxTime = 0) {
		return $.ajax({
			url: '/cgi-bin/pakfire.cgi',
			method: 'POST',
			timeout: maxTime,
			context: this,
			data: {'ACTION': `json-${action}`},
			dataType: 'json' //automatically check and convert result
		})
			.done(function(response) {
				this._JSON_process(action, response);
			});
	}

	// Process successful response from Pakfire CGI
	// action: POST paramter "json-[action]" used to send request
	// data: JSON data object
	_JSON_process(action, data) {
		// Pakfire status refresh
		if(action === this._autoRefresh.jsonAction) {
			// Update status flags
			this.running = (data['running'] != '0');
			this.reboot = (data['reboot'] != '0');

			// Update timer display
			if(this.running && data['running_since']) {
				$('#pflog-time').text(this.i18n.get('since') + data['running_since']);
			} else {
				$('#pflog-time').empty();
			}

			// Print log messages
			let messages = "";
			data['messages'].forEach(function(line) {
				messages += `${line}\n`;
			});
			$('#pflog-messages').text(messages);
		}
	}
}

// Simple translation strings helper
// Format: {key: "translation"}
class PakfireI18N {
	constructor() {
		this._strings = Object.create(null); //Object without prototypes
	}

	// Get translation
	get(key) {
		if(Object.prototype.hasOwnProperty.call(this._strings, key)) {
			return this._strings[key];
		}
		return `(undefined string '${key}')`;
	}

	// Load key/translation object
	load(translations) {
		if(translations instanceof Object) {
			Object.assign(this._strings, translations);
		}
	}
}

//### Initialize Pakfire ###
const pakfire = new PakfireJS();

$(function() {
	pakfire.documentReady();
});
