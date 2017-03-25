function date_validation(){
    var startDate = document.getElementById("start_date").value;
    var endDate = document.getElementById("end_date").value;

    var message

    if(!(startDate < endDate)) {
        $("#date_checker").html("Funding end date must be after start date");
        document.getElementById("submit").disabled = true;
    }
    else {
        $("#date_checker").html("");
        document.getElementById("submit").disabled = false;
    }
}