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
		this._states.failure = false;

		// Status refresh helper
		this._autoRefresh = {
			delay: 1000, //Delay between requests (minimum: 500, default: 1s)
			jsonAction: 'getstatus', //CGI POST action parameter
			timeout: 5000, //XHR timeout (0 to disable, default: 5s)

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

		// Return to main screen helper
		this._pageReload = {
			delay: 1000, //Delay before page reload (default: 1s)
			enabled: false, //Reload disabled by default

			delayTimer: null, //setTimeout reference
			get isTriggered() { //Reload timer started
				return (this.delayTimer !== null);
			}
		};
	}

	//### Public properties ###

	// Note on using the status flags
	// running: Pakfire is performing a task.
	//    Writing "true" activates the periodic AJAX/JSON status polling, writing "false" stops polling.
	//    When the task has been completed, status polling stops and this returns to "false".
	//    The page can then be reloaded to go back to the main screen. Writing "false" does not trigger a reload.
	//    "refreshInterval" and "setupPageReload" can be used to adjust the respective behaviour.
	// reboot: An update requires a reboot.
	//    If set to "true", a link to the reboot menu is shown after the task is completed.
	// failure: An error has occured.
	//    To display the error log, the page does not return to the main screen.

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

	// Error encountered (true/false)
	set failure(state) {
		if(this._states.failure !== state) {
			this._states.failure = state;
			this._states_onChange('failure');
		}
	}
	get failure() {
		return this._states.failure;
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

	// Configure page reload after successful task (returns to main screen)
	// delay: In ms
	setupPageReload(enabled, delay) {
		if(delay < 0) {
			delay = 0;
		}
		this._pageReload.delay = delay;
		this._pageReload.enabled = enabled;
	}

	// Document loaded (call once from jQuery.ready)
	documentReady() {
		// Status refresh late start
		if(this.running && (! this._autoRefresh.isRunning)) {
			this._autoRefresh_runNow();
		}
	}

	// Reload entire CGI page (clears POST/GET data from history)
	documentReload() {
		let url = window.location.origin + window.location.pathname;
		window.location.replace(url);
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
			if(this.failure) {
				$('#pflog-status').text(this.i18n.get('finished error'));
			} else {
				$('#pflog-status').text(this.i18n.get('finished'));
			}
			if(this.reboot) { //Enable return or reboot links in UI
				$('#pflog-action').html(this.i18n.get('link_return') + " &bull; " + this.i18n.get('link_reboot'));
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

		// Always stay in the log viewer if Pakfire failed
		if(property === 'failure') {
			if(this.failure) {
				this._pageReload_cancel();
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

	// Start delayed page reload to return to main screen
	_pageReload_trigger() {
		if((! this._pageReload.enabled) || this._pageReload.isTriggered) {
			return; // Disabled or already started
		}
		this._pageReload.delayTimer = window.setTimeout(function() {
			this._pageReload.delayTimer = null;
			this.documentReload();
		}.bind(this), this._pageReload.delay);
	}

	// Stop scheduled reload
	_pageReload_cancel() {
		if(this._pageReload.isTriggered) {
			window.clearTimeout(this._pageReload.delayTimer);
			this._pageReload.delayTimer = null;
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
			this.failure = (data['failure'] != '0');

			// Update timer display
			if(this.running && data['running_since']) {
				$('#pflog-time').text(this.i18n.get('since') + " " + data['running_since']);
			} else {
				$('#pflog-time').empty();
			}

			// Print log messages
			let messages = "";
			data['messages'].forEach(function(line) {
				messages += `${line}\n`;
			});
			$('#pflog-messages').text(messages);

			// Pakfire finished without errors, return to main screen
			if((! this.running) && (! this.failure)) {
				this._pageReload_trigger();
			}
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
