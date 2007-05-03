/*
File Info:	utility.js - JavaScript library

Author:		Drew S. Dupont

Date:		2/26/2003 - 8/12/2004 (or present day)

Description:	Utility functions in JavaScript
		Drew S. Dupont <dsdupont@alumni.indiana.edu>
*/
// Show/Hide HTML Span
function showHideHTML(id, content) {
	// Browser variables
	var ie45, ns6, ns4, dom = false;

	// Basic browser parse
	if (navigator.appName == "Microsoft Internet Explorer") {
		ie45 = parseInt(navigator.appVersion) >= 4;
	} else if (navigator.appName == "Netscape") {
		ns6 = parseInt(navigator.appVersion) >= 5;
		ns4 = parseInt(navigator.appVersion) < 5;
	}
	dom = ie45 || ns6;

	// Return if using an old Netscape browser
	if(ns4) return;

	// Check for type of call supported
	el = document.all ? document.all[id] : dom ? document.getElementById(id) : document.layers[id];

	// Check if content to be "switched" is ""
	if (content == "") {
		// Return old content and replace with ""
		content = el.innerHTML;
		el.innerHTML = "";
	} else {
		// Replace current content with new content and return ""
		el.innerHTML = content;
		content = "";
	}

	// Return content (either old or "")
	return content;
}

// Check for special chars
function checkForSpecialChars(field, alphaStart, specialCheckChars) {
	// Local vars
	var alphaStartChars = /^[a-zA-Z]/;
	var noSpecialChars = /([^a-zA-Z0-9 _,?!':;\r\t\n\/\\\-\.#@]+)/;

	// Check if should start with an alpha char
	if (alphaStart) {
		// Make sure starts with a alpha char
		if (alphaStartChars.test(field.value)) {
			// Check for special chars
			if (noSpecialChars.test(field.value)) {
				// Return true
				return true;
			} else {
				// Check for specialCheckChars
				if (specialCheckChars && (specialCheckChars.test(field.value))) {
					// Return true
					return true;
				} else {
					// Return false
					return false;
				}
			}
		} else {
			// Return true
			return true;
		}
	} else {
		// Check if contains any special chars
		if (noSpecialChars.test(field.value)) {
			// Return true
			return true;
		} else {
			// Check for specialCheckChars
			if (specialCheckChars && (specialCheckChars.test(field.value))) {
				// Return true
				return true;
			} else {
				// Return false
				return false;
			}
		}
	}
} // End checkForSpecialChars

// Launch help
function launchHelp(helpSrc) {
	helpWindow = window.open(helpSrc, "helpWindow", "resizable=yes,menubar=no,statusbar=no,titlebar=no,scrollbars=yes,width=400,height=400")
	helpWindow.moveTo(25, 25);
	helpWindow.focus();
}

// Image On
function imageOn(imageName)	{
	document[imageName].src = eval(imageName + "_over.src");
}

// Image Off
function imageOff(imageName) {
	document[imageName].src = eval(imageName + ".src");
}

// Image Down
function imageDown(imageName) {
	document[imageName].src = eval(imageName + "_down.src");
}

// Image button On
function imageButtonOn(item, imageName)	{
	item.src = eval(imageName + "_over.src");
}

// Image button Off
function imageButtonOff(item, imageName) {
	item.src = eval(imageName + ".src");
}

// Image button Down
function imageButtonDown(item, imageName) {
	item.src = eval(imageName + "_down.src");
}

// changeStatus
function changeStatus(message) {
	// Set window status
	window.status = message;

	// Return true
	return true;
} // End changeStatus

// isNumeric function
function isNumeric(num) {
	// Boolean var
	var bolValidNum = true;
	var digits = "1234567890";
	var len = num.length;

	// Loop over num
	for (i = 0; i < len; ++i) {
		numSub = num.substring(i, i + 1);

		// Test for numeric match
		if (digits.indexOf(numSub) == -1) {
			bolValidNum = false;
		}
	}

	// Return boolean var
	return bolValidNum;
} // End isNumeric

// Check for numeric and display nice error
function checkNumeric(field, message) {
	// Is it valid
	if (!isNumeric(field.value)) {
		alert(message);
		field.focus();
	}
} // End checkNumeric

// Function getInt which return numeric value of passed in string
function getInt(str, i, minlength, maxlength) {
	for (x = maxlength; x >= minlength; --x) {
		var token = str.substring(i, i + x);

		// Check for numeric
		if (isNumeric(token)) {
			return token;
		}
	}

	// Return null
	return null;
}

// Function dateCheck, requires global err variable for passing error messages 
// and requires the isNumeric function
function dateCheck(date, humanname, dateFormat) {
	// Date validation
	var date_s = date;

	// If no dateFormat, then set one
	if (dateFormat == null) {
		format = "mm/dd/yyyy";
	} else {
		format = dateFormat;
	}

	var date_err = 0; // Possible values are 0, 1
	var date_year_err = 0; // Possible values are 0, 1
	var date_month_err = 0; // Possible values are 1-12
	var date_day_err = 0; // Possible values are 0, 1, 2, 3, 4
	var i_date_s = 0;
	var i_format = 0;
	var err = "";
	var c = "";
	var token = "";
	var token2 = "";
	var x, y;
	var year = 0;
	var month = 0;
	var date = 0;
	var bYearProvided = false;
	var MONTH_NAMES = new Array('January','February','March','April','May','June','July','August','September','October','November','December','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec');

	// Trim the leading spaces from the string
	while (date_s.charAt(0) == ' ') {
		date_s = date_s.slice(1);
	}

	while (i_format < format.length) {
		// Get next token from format string
		c = format.charAt(i_format);
		token = "";

		while ((format.charAt(i_format) == c) && (i_format < format.length)) {
			token += format.charAt(i_format);
			++i_format;
		}

		// Extract contents of value based on format token
		if ((token == "yyyy") || (token == "yy") || (token == "y")) {
			if (token == "yyyy") { x = 4; y = 4; } // 4-digit year
			if (token == "yy") { x = 2; y = 2; } // 2-digit year
			if (token == "y") { x = 2; y = 4; } // 2-or-4-digit year

			year = getInt(date_s, i_date_s, x, y);
			bYearProvided = true;

			if ((year == null) || (year.length != token.length)) {
				date_year_err = 1;
			}

			i_date_s += year.length;
		} else {
			if (token == "mmm") { // Month name
				month = 0;

				for (var i = 0; i < MONTH_NAMES.length; ++i) {
					var month_name = MONTH_NAMES[i];

					if (date_s.substring(i_date_s, (i_date_s + month_name.length)).toLowerCase() == month_name.toLowerCase()) {
						month = i + 1;

						if (month > 12) {
							month -= 12;
						}

						i_date_s += month_name.length;
						break;
					}
				}

				if ((month == 0) || (month < 1) || (month > 12)) {
					date_month_err = 1;
				}
			} else {
				if ((token == "mm") || (token == "m")) {
					x = token.length; y = 2;
					month = getInt(date_s, i_date_s, x, y);

					if ((month == null) || (month < 1) || (month > 12)) {
						date_month_err = 1;
					}

					i_date_s += month.length;
				} else {
					if (token=="dd" || token=="d") {
						x = token.length; y = 2;
						date = getInt(date_s, i_date_s, x, y);

						if ((date == null) || (date < 1) || (date > 31)) {
							date_day_err = 1;
						}

						i_date_s += date.length;
					} else {
						if (date_s.substring(i_date_s, (i_date_s + token.length)) != token) {
							date_err = 1;
						} else {
							i_date_s += token.length;
						}
					}
				}
			}
		}
	}

	// If there are any trailing characters left in the date_s, it doesn't match
	if (i_date_s != date_s.length) {
		date_err = 1;
	}

	// Is date valid for month?
	if ((month == 4) || (month == 6) || (month == 9) || (month == 11)) {
		if (date > 30) {
			date_day_err = 2;
		}
	} else {
		if (month == 2) {
			// Check for leap year
			if ((((year % 4) == 0) && ((year % 100) != 0)) || ((year % 400) == 0)) {
				// Leap year
				if (date > 29) {
					date_day_err = 3
				}
			} else {
				if (date > 28) {
					date_day_err = 4;
				}
			}
		} else {
			if (date > 31) {
				date_day_err = 1;
			}
		}
	}

	// Add to the error message, if needed
	if (date_err != 0) {
		err += "\n - The " + humanname + " must be a valid date in the format " + format + ".";
	}

	// Add to the error message, if needed
	if (date_month_err != 0) {
		err += "\n - The month must be between 1-12.";
	}

	// Add to the error message, if needed
	if (date_year_err != 0) {
		err += "\n - The " + humanname + " must have a valid year.";
	}

	// Add to the error message, if needed
	if (date_day_err != 0) {
		switch (date_day_err) {
			case 1:
				err += "\n - The month you entered in the " + humanname + " can only have between 1 and 31 days.";
				break;
			case 2:
				err += "\n - The month you entered in the " + humanname + " can only have between 1 and 30 days.";
				break;
			case 3:
				err += "\n - The month you entered in the " + humanname + " can only have between 1 and 29 days in a Leap Year.";
				break;
			default:
				err += "\n - The month you entered in the " + humanname + " can only have between 1 and 28 days in a non-Leap Year.";
				break;
		}
	}

	return err;
} // End dateCheck

// Compares two MM/DD/YYY dates for less than (-1), equal to (0), or 
// greater than (1)
function dateCompare(date1, date2) {
	var localDate1 = new Date(date1.substring(6,10), date1.substring(0,2), date1.substring(3,5));
	var localDate2 = new Date(date2.substring(6,10), date2.substring(0,2), date2.substring(3,5));

	// Greater than
	if (localDate1.getTime() > localDate2.getTime()) {
		return 1;
	} else {
		// Less than
		if (localDate1.getTime() < localDate2.getTime()) {
			return -1;
		} else {
			// Equal
			return 0;
		}
	}
} // End dateCompare

// All-purpose form validation script
function checkForm(dataForm) {
	var msg = "";
	var stripBlanksStart = /^\s+/g;
	var stripBlanksEnd = /\s+$/g;
	var squeezeBlanks = /\s+/g;
	var stripNonNumbers = /\D+/g;
	var stripNotDollars = /[^0-9\.]/g;
	var noSpaces = /\s+/g;
	var allNumbers = /^\d+$/;
	var zipCodeCheck = /^(\d{5})$|^(\d{5}-\d{4})$/;
	var passwordNumbers = /\d{1,}/;
	var passwordLetters = /\D{1,}/;
	var emailPattern = /^[a-zA-Z0-9]([a-zA-Z0-9_\-\.]*)@([a-zA-Z0-9_\-\.]*)(\.[a-zA-Z]{2,3}(\.[a-zA-Z]{2}){0,2})$/i;
	var replaceSeps = /[-,\.\/]/g;
	var time24Format = /^(([0-1]?\d)|(2[0-3])):[0-5]\d(:([0-5]\d))?/;
	var time12Format = /^(\d|0\d|1[0-2]):[0-5]\d(:[0-5]\d)?( (A|P)\.?M\.?)?/;
	var ipNetworkAddress = /^((\d{1,2}|[1]\d{2}|2[0-4]\d|25[0-5])(\.(\d{1,2}|[1]\d{2}|2[0-4]\d|25[0-5])){3}){1}((\/(0\.0\.0\.0|128\.0\.0\.0|192\.0\.0\.0|224\.0\.0\.0|240\.0\.0\.0|248\.0\.0\.0|252\.0\.0\.0|254\.0\.0\.0|(255\.(0\.0\.0|128\.0\.0|192\.0\.0|224\.0\.0|240\.0\.0|248\.0\.0|252\.0\.0|254\.0\.0|(255\.(0\.0|128\.0|192\.0|224\.0|240\.0|248\.0|252\.0|254\.0|(255\.(0|128|192|224|240|248|252|254|255))))))))|(\/(\d|[1-2]\d|3[0-2]))){0,1}$/;
	var ipNetworkPort = /^(\d{1,4}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5]){1}((\:|\-)(\d{1,4}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])){0,1}$/;
	var passwordLength = 6;
	var error_fields = "";
	var errors = "";

	// Loop over form elements
	for (var i = 0; i < dataForm.length; ++i) {
		var element = dataForm.elements[i];

		// Check for select box
		if (element.selectbox) {
			// Check for required
			if (element.required) {
				// Check for value
				if (element.options[element.selectedIndex].value == "") {
					error_fields += "\n - " + element.humanname + " requires a selection.";
				}
			}
			continue;
		}

		// Strip the leading and trailing blanks
		element.value = element.value.replace(stripBlanksStart, '');
		element.value = element.value.replace(stripBlanksEnd, '');

		// If it is required and is empty, alert
		if (element.required && (!element.value.length)) {
			error_fields += "\n - " + element.humanname + " is required.";
			continue;
		} else {
			// If it isn't required and doesn't have any length, skip it
			if ((! element.required) && (! element.value.length)) {
				continue;
			}
		}

		// Check for special characters
		if (element.checkspecialchars) {
			if (checkForSpecialChars(element, element.alphaStart, element.specialChars)) {
				error_fields += "\n - " + element.humanname + " contains invalid characters.";
				continue;
			}
		}
		
		// Convert to uppercase if necessary
		if (element.uppercase) {
			element.value = element.value.toUpperCase();
		}

		// Convert to uppercase if necessary
		if (element.lowercase) {
			element.value = element.value.toLowerCase();
		}

		// UCFirst if necessary
		if (element.ucfirst) {
			// Squeeze the blanks
			rs = element.value.replace(squeezeBlanks, ' ');
			dsegs = rs.split(' ');
			element.value = "";

			// Loop over chars
			for (j = 0; j < dsegs.length; ++j) {
				if (dsegs[j].length > 1) {
					fl = dsegs[j].substr(0, 1);
					fl = fl.toUpperCase();
					rn = dsegs[j].substr(1);
					rn = rn.toLowerCase();
					dsegs[j] = fl + rn;
				}

				// Check for first value
				element.value = j ? element.value + ' ' + dsegs[j] : dsegs[j];
			}
		}

		// Check for equality test
		if (element.equalto) {
			// Check for truevalue and use if found, otherwise use value
			var elementValue1 = element.truevalue ? element.truevalue : element.value;
			var elementValue2 = element.equaltovalue.truevalue ? element.equaltovalue.truevalue : element.equaltovalue.value;

			// Check for value equality
			if (elementValue1 != elementValue2) {
				error_fields +="\n - " + element.humanname + " is not the same as " + element.equaltovalue.humanname;
				continue;
			}
		}

		// Check for less than
		if (element.lessthan) {
			// Check for truevalue and use if found, otherwise use value
			var elementValue1 = element.truevalue ? element.truevalue : element.value;
			var elementValue2 = element.lessthanvalue.truevalue ? element.lessthanvalue.truevalue : element.lessthanvalue.value;

			// Check for values
			if ((elementValue1 != '') && (elementValue2 != '')) {
				// Check for value less than
				if (elementValue1 >= elementValue2) {
					error_fields +="\n - " + element.humanname + " must be less than " + element.lessthanvalue.humanname;
					continue;
				}
			}
		}

		// Check for less than equalto
		if (element.lessthanequalto) {
			// Check for truevalue and use if found, otherwise use value
			var elementValue1 = element.truevalue ? element.truevalue : element.value;
			var elementValue2 = element.lessthanequaltovalue.truevalue ? element.lessthanequaltovalue.truevalue : element.lessthanequaltovalue.value;

			// Check for values
			if ((elementValue1 != '') && (elementValue2 != '')) {
				// Check for value less than equalto
				if (elementValue1 > elementValue2) {
					error_fields +="\n - " + element.humanname + " must be less than or equal to " + element.lessthanequaltovalue.humanname;
					continue;
				}
			}
		}

		// Check for greater than
		if (element.greaterthan) {
			// Check for truevalue and use if found, otherwise use value
			var elementValue1 = element.truevalue ? element.truevalue : element.value;
			var elementValue2 = element.greaterthanvalue.truevalue ? element.greaterthanvalue.truevalue : element.greaterthanvalue.value;

			// Check for values
			if ((elementValue1 != '') && (elementValue2 != '')) {
				// Check for value greater than
				if (elementValue1 <= elementValue2) {
					error_fields +="\n - " + element.humanname + " must be greater than " + element.greaterthanvalue.humanname;
					continue;
				}
			}
		}

		// Check for greater than equalto
		if (element.greaterthanequalto) {
			// Check for truevalue and use if found, otherwise use value
			var elementValue1 = element.truevalue ? element.truevalue : element.value;
			var elementValue2 = element.greaterthanequaltovalue.truevalue ? element.greaterthanequaltovalue.truevalue : element.greaterthanequaltovalue.value;

			// Check for values
			if ((elementValue1 != '') && (elementValue2 != '')) {
				// Check for value greater than equalto
				if (elementValue1 < elementValue2) {
					error_fields +="\n - " + element.humanname + " must be greater than or equal to " + element.greaterthanequaltovalue.humanname;
					continue;
				}
			}
		}

		// Check a price (sort of)
		if (element.price) {
			// Strip out currency stuff
			element.value = element.value.replace(stripNotDollars, '');
			continue;
		}

		// Check a telephone number
		if (element.telephone) {
			// Strip out parens and spaces
			rs = element.value.replace(stripNonNumbers, '');

			if (rs.length == 7) {
				element.value = rs.substr(0, 3) + "-" + rs.substr(3, 4);
			} else {
				if (rs.length == 10) {
					element.value = rs.substr(0, 3) + "-" + rs.substr(3, 3) + "-" + rs.substr(6, 4);
				} else { 
					error_fields += "\n - " + element.humanname + " is an invalid telephone number.";
				}
			}
			continue;
		}

		// Check a zip code
		if (element.zipcode) {
			if (!zipCodeCheck.test(element.value)) {
				error_fields +="\n - " + element.humanname + " is an invalid zipcode.";
			}
			continue;
		}

		// Check a password (sort of)
		if (element.password) {
			if (element.value.length < passwordLength) {
				error_fields += "\n - " + element.humanname + " is too short";
				error_fields += "\n      Minimum length is " + passwordLength + " characters.";
				continue;
			}

			if (!passwordNumbers.test(element.value)) {
				error_fields += "\n - " + element.humanname + " must contain at least one number.";
				continue;
			}

			if (!passwordLetters.test(element.value)) {
				error_fields += "\n - " + element.humanname + " must contain at least one letter.";
				continue;
			}
		}

		// Check for all numbers
		if (element.numeric) {
			if (!allNumbers.test(element.value)) {
				error_fields += "\n - " + element.humanname + " is not numeric.";
			}
			continue;
		}

		// Check an email address for validity
		if (element.email) {
			element.value = element.value.replace(noSpaces, '');

			if (!emailPattern.test(element.value)) {
				error_fields += "\n - " + element.humanname + " is not a valid email address.";
			}
			continue;
		}

		// Check a date
		if (element.date) {
			error_fields += dateCheck(element.value, element.humanname, element.format);
			continue;
		}

		// Check a time
		if (element.time) {
			// Check for 24 hour time
			if (element.time24) {
				// Check for valid
				if (!time24Format.test(element.value)) {
					error_fields += "\n - " + element.humanname + " is not a valid 24 hour time.";
				}
			} else {
				// Check for valid
				if (!time12Format.test(element.value)) {
					error_fields += "\n - " + element.humanname + " is not a valid 12 hour time.";
				}
			}
			continue;
		}

		// Check the lengths
		if (element.minlen && (element.value.length < element.minlen)) {
			error_fields += "\n - " + element.humanname + " is too short";
			error_fields += "\n      Minimum length is " + element.minlen + " characters.";
			continue;
		}

		if (element.maxlen && (element.value.length > element.maxlen)) {
			error_fields +="\n - " + element.humanname + " is too long";
			error_fields +="\n      Maximum length is " + element.maxlen + " characters.";
			continue;
		}

		// Check for ip/network address
		if (element.ipnetworkaddress) {
			if (!ipNetworkAddress.test(element.value)) {
				error_fields +="\n - " + element.humanname + " is not a valid ip/network address";
			}
			continue;
		}

		// Check for ip/network port
		if (element.ipnetworkport) {
			if (!ipNetworkPort.test(element.value)) {
				error_fields +="\n - " + element.humanname + " is not a valid ip/network port";
			} else {
				var searchChar = "";
				var portArray = "";

				if (element.value.indexOf(":") > -1) {
					searchChar = ":";
				} else if (element.value.indexOf("-") > -1) {
					searchChar = "-";
				}
				
				if (searchChar != '') {
					portArray = element.value.split(searchChar);

					if (portArray.length == 2) {
						if (parseInt(portArray[0]) > parseInt(portArray[1])) {
							error_fields +="\n - " + element.humanname + " can not have a start port greater than an end port";
						}
					}
				}
			}
			continue;
		}
	}

	// Check for any errors
	if (error_fields == "") {
		return true;
	} else {
		msg = "The following fields have errors:\n";
		msg += error_fields;
		alert(msg);
		return false;
	}
}

// Clear data
function clearData(field, data) {
	// Check if they equal
	if (field.value == data) {
		// Clear data
		field.value = '';
	}
}

// Set empty data
function setEmptyData(field, data) {
	// Check if they equal
	if (! field.value.length) {
		// Clear data
		field.value = data;
	}
}

// Trim whitespace from beginning and end
function trim(data) {
	var objRegExp = /^(\s*)$/;

	// Check for all spaces
	if (objRegExp.test(data)) {
		data = data.replace(objRegExp, '');

		if (data.length == 0)
			return data;
	}

	// Check for leading & trailing spaces
	objRegExp = /^(\s*)([\W\w]*)(\b\s*$)/;

	if (objRegExp.test(data)) {
		// Remove leading and trailing whitespace characters
		data = data.replace(objRegExp, '$2');
	}

	return data;
}
