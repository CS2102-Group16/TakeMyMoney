//Javascript to check if username and password exist in database and exist

var attempt = 3; // Variable to count number of attempts.
//Global variable is probably not a good idea

// Below function Executes on click of login button.
function validate(){
    var user_email = document.getElementById("user_email").value;
    var password = document.getElementById("password").value;
    if ( user_email == "admin" && password == "admin"){
        alert ("Login successfully");
        window.location = "success.html"; // Redirecting to other page.
        return false;
    }

    else{
        attempt --;// Decrementing by one.
        alert("You have "+attempt+" attempt(s) left;");
        // Disabling fields after 3 attempts.
        if( attempt <= 0){
            document.getElementById("user_email").disabled = true;
            document.getElementById("password").disabled = true;
            document.getElementById("submit").disabled = true;
            return false;
        }
    }
}