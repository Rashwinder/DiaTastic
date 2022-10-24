
// Initialise time now when page loads
var now = new Date();

// Function to pad numbers with leading zeros
function padNum(num, n = 2, char = "0") {
    return num.toString().padStart(n, char)
}

// Extract subportions of time and pad them
var day = padNum(now.getDate());
var month = padNum(now.getMonth()+1);
var year = now.getFullYear();
var hour = padNum(now.getHours());
var minute = padNum(now.getMinutes());

// Format is yyyy-mm-ddThh:mm where T is the designated separator
// var datetime = `${year}-${month}-${day}T${hour}:${minute}`;
var date = `${year}-${month}-${day}`
var time = `${hour}:${minute}`
// var datetime = `${date}T${time}`

document.getElementById("date").value = date;
document.getElementById("time").value = time;

// document.getElementById("datetimePicker").value = datetime;




// Example of retrieving date and time, yyyy-mm-dd & hh:mm, as strings
console.log(document.getElementById("datetimePicker").value.split("T"));