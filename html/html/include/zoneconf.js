/*#############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2020  IPFire Team  <info@ipfire.org>                     #
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

//zoneconf.cgi dynamic highlighting of interface access selection
//(call this from "onchange" event of selection elements)
function highlightAccess(selectObj) {
	if(!(selectObj && ('zone' in selectObj.dataset) && ('mac' in selectObj.dataset))) {
		return; //required parameters are missing
	}

	var zoneColor = selectObj.dataset.zone.trim().toLowerCase(); //zone color (red/green/blue/orange) CSS class

	function colorParentCell(obj, color, enabled = true) { //find nearest parent table cell of "obj" and set its CSS color class
		do {
			obj = obj.parentElement;
		} while(obj && (obj.nodeName.toUpperCase() !== 'TD'));
		if(obj && (['green', 'red', 'orange', 'blue'].includes(color))) {
			obj.classList.toggle(color, enabled);
		}
	}

	//handle other associated input fields
	if(selectObj.type.toUpperCase() === 'RADIO') { //this is a radio button group: clear all highlights
		let radios = document.getElementsByName(selectObj.name);
		radios.forEach(function(button) {
			if(button.nodeName.toUpperCase() === 'INPUT') { //make sure the found element is a button
				colorParentCell(button, zoneColor, false); //remove css
			}
		});
	} else { //this is a dropdown menu: enable/disable additional VLAN tag input box
		let tagInput = document.getElementById('TAG-' + selectObj.dataset.zone + '-' + selectObj.dataset.mac); //tag input element selector
		if(tagInput) {
			tagInput.disabled = (selectObj.value !== 'VLAN'); //enable tag input if VLAN mode selected
		}
	}

	//if interface is assigned, highlight table cell in zone color
	colorParentCell(selectObj, zoneColor, (selectObj.value !== 'NONE'));
}
