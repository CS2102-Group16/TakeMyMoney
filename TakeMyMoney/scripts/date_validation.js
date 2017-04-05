function date_validation(){
    var startDate = document.getElementById("start_date").value;
    var endDate = document.getElementById("end_date").value;

    startDate = startDate == "" ? null : new Date(startDate);
    endDate = endDate == "" ? null : new Date(endDate);

    var message

    if (startDate !== null && endDate !== null && !(startDate < endDate)) {
        $("#date_error").css("display", "block");
        document.getElementById("submit").disabled = true;
    }
    else {
        $("#date_error").css("display", "none");
        document.getElementById("submit").disabled = false;
    }
}