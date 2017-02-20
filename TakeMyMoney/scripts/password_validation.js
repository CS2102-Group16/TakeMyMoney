//Javascript to ensure password and confirm_password in add_new_user are equal

//http://keithscode.com/tutorials/javascript/3-a-simple-javascript-password-validator.html

function checkPass()
{
    //Store the password field objects into variables ...
    var pass1 = document.getElementById('password');
    var pass2 = document.getElementById('confirm_password');
    //Store the Confirmation Message Object ...
    var message = document.getElementById('confirmMessage');
    //Set the colors we will be using ...
    var goodColor = "#66cc66";
    var badColor = "#ff6666";
    //Compare the values in the password field
    //and the confirmation field
    if(password.value == confirm_password.value){
        //The passwords match.
        //Set the color to the good color and inform
        //the user that they have entered the correct password
        confirm_password.style.backgroundColor = goodColor;
        message.style.color = goodColor;
        message.innerHTML = "Passwords Match!"
    }else{
        //The passwords do not match.
        //Set the color to the bad color and
        //notify the user.
        confirm_password.style.backgroundColor = badColor;
        message.style.color = badColor;
        message.innerHTML = "Passwords Do Not Match!"
    }
}