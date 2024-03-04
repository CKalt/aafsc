//this function is responsible for handling the drop down expansions when
//the user clicks on the text and not the arrow
//it was acquired by infragistics support
function WebDropDown_MouseDown(sender, e) {
    if (e.get_browserEvent().target.attributes["mkr"]) {
        //check the mkr attributes of the input element
        var inputAttr = e.get_browserEvent().target.attributes["mkr"].value;
        if (inputAttr == "Input") {
            sender.openDropDown();
        }
    }
}

//this function validates a date that the user inputs against a 
//maximum and minimum date for the WebDateTimeEditor. The asp.net
//range validator does not work for this infragistics control
function validateDateRange(userInput, minimumDate, maximumDate) {
    var mindate = new Date();
    var maxdate = new Date();

    userInput = userInput.replace(/\_/g, "");
    mindate.setDate(mindate.getDate() - minimumDate); //20 years
    maxdate.setDate(maxdate.getDate() + maximumDate);

    var arrayOfValues = userInput.split(' ');
    var enteredDate = new Date(arrayOfValues[0]);

    var goodtoGo = false;

    if (enteredDate > mindate && enteredDate < maxdate) {
        goodtoGo = true;
    }
    return goodtoGo;
}
