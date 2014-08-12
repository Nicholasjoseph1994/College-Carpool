var countryRestrict = { 'country': 'us' };

$(document).ready(function () {
	var inputs = document.getElementsByClassName("autocomplete");
    for (var i = 0; i < inputs.length; ++i) {
    	// don't keep a handle to any of these autocomplete for now, but maybe in the future
    
    	new google.maps.places.Autocomplete(/** @type {HTMLInputElement} */(inputs[i]),
    		{componentRestrictions: countryRestrict}
    	);
    }
});
