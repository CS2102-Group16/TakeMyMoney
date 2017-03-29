function date_validation(){
    var startDate = document.getElementById("start_date").value;
    var endDate = document.getElementById("end_date").value;

    var message

    if(!(startDate < endDate)) {
        $("#date_checker").html("Funding start date must be before end date");
        document.getElementById("submit").disabled = true;
    }
    else {
        $("#date_checker").html("");
        document.getElementById("submit").disabled = false;
    }
}