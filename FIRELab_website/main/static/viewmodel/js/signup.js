//password check
function check(input) {
        if (input.value != document.getElementById('signup_password').value) {
            input.setCustomValidity("Password doesn't match!");
        } else {
            // input is valid -- reset the error message
            input.setCustomValidity('');
        }
    }