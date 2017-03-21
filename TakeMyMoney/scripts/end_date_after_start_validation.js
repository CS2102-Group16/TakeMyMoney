
//Below function to check end date is after start date
function date_validation(){
    var startDate = document.getElementById("start_date").value;
    var endDate = document.getElementById("end_date").value;
    var regExp = /(\d{1,2})\/(\d{1,2})\/(\d{2,4})/;
    if(parseInt(endDate.replace(regExp, "$3$2$1")) > parseInt(startDate.replace(regExp, "$3$2$1"))){
        alert("greater");
    }
}