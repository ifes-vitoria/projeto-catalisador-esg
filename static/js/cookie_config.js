function setCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + value + expires + "; path=/";
}

function eraseCookie(name) {
    document.cookie = name + '=; Max-Age=-99999999;';
}

function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = ca.length; i >= 0; i--) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

function parseCookies() {
    const cookies = document.cookie.split('; ');
    let cookieDict = {};

    cookies.forEach(cookie => {
        const [key, value] = cookie.split('=');
        cookieDict[key] = value;
    });

    return cookieDict;
}

function findFirstCheckedElement(ids) {
    for (var i = 0; i < ids.length; i++) {
        var element = document.getElementById(ids[i]);
        if (element && element.checked) {
            return i;
        }
    }
    return null;
}

        // Function to check if at least one radio button is checked
        function isAnyRadioButtonChecked(ids) {
            // Iterate over each ID
            for (let id of ids) {
                    // Find the radio button by ID and check if it is checked
                    if (document.querySelector(`input[id="${id}"]:checked`)) {
                            return true; // Return true if any radio button is checked
                    }
            }
            return false; // Return false if none are checked
    }
