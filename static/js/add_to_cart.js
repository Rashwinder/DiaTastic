var count = [];
var row_count = 1;
var show_count = 20;
var cart_dict = new Array();
$(function () {
    $('.tbody1').on("click", ".alonTr .innerbtn", function () {
        $(this).next('.pop_box').slideDown('400');
    })
    $('.tbody1').on("click", ".alonTr .closepop", function () {
        $('.pop_box').slideUp('400');
    })

    // add new row

    $(".AddTr").click(function () {
        var dup = 0;
        var val_check = 0;
        var length = $(".tabInfo .tbody1>tr").length;

        var date = $('#date').val();
        if(!date){
            alert('Please check the date.');}
        else{
            val_check++;
        };

        var time = $('#time').val();
        if(time == ''){
            alert('Please check the time.');}
        else{
            val_check++;
        };

        // Blood Sugar Level
        var SplitString = $('#blood_sugar_level').val();

        // Split it by the decimal place.
        SplitString = String(SplitString)

        // If the value includes a period, it's a decimal.
        if(SplitString.includes('.')){
            // Split by the period.
            SplitString = SplitString.split('.');

            // If the integer part is greater than 2 characters, or the decimal part is greater than 1 character,
            // Throw an alert.
            if(SplitString[0].length > 2 || SplitString[1].length > 1){
                alert('Please check your Blood Sugar Levels.');
                }

            // Otherwise, the value is safe to be parsed as a float.
            else{
                var BSL = parseFloat($('#blood_sugar_level').val());

                // If the value is greater than 30, smaller than 0, or non-existent,
                // Throw an alert.
                if(BSL > 30 || BSL < 0 || !BSL){
                    alert('Please check your Blood Sugar Levels.');
                    return false;
                    }

                    // Otherwise, all verifications are true.
                    else{
                    val_check++;
                    };
                }
        }

        // If the value does not include a period, it's an integer.
        else{
            var BSL = parseInt($('#blood_sugar_level').val());

            // If the value is greater than 30, smaller than 0, or non-existent,
            // Throw an alert.
            if(BSL > 30 || BSL < 0 || !BSL){
                alert('Please check your Blood Sugar Levels.');
                return false;
                }

                // Otherwise, all verifications are true.
                else{
                val_check++;
                };
        }

        // Category ID
        var categoryId = parseInt($('#category').val());
        if(!parseInt(categoryId) || categoryId == ''){
            alert('Please check the category.');
            return false;
        } else{
            val_check++;
        };

        // Description ID
        var descriptionId = parseInt($('#description').val());
        if(!parseInt(descriptionId) || descriptionId == ''){
            alert('Please check the description.');
            return false;
        } else{
            val_check++;
        };

        // Portion ID
        var portionId = parseInt($('#portion').val());
        if(!parseInt(portionId) || portionId == ''){
            alert('Please check the portions.');
            return false;
        } else{
            val_check++;
        };

        // Quantity
        var Q = parseInt($('#quantity').val());
        if(!Q){
            alert('Please check the quantity.');
            return false;
        } else{
            val_check++;
        };

        // Comment
        var comment = $('#comment').val();

        // If val_check equal 7:
        if(val_check == 7){

            // If dictionary is not empty:
//            if(cart_dict.length != 0){

                // Iterate through the dictionary.
                for(i = 0; i < cart_dict.length; i++){

                    // If there is a duplicate:
                    if((cart_dict[i]['categoryId'] == categoryId ) && (cart_dict[i]['descriptionId'] == descriptionId) && (cart_dict[i]['portionId'] == portionId)){
                        // Set the dup value to 1.
                        dup = 1;

                        // Update the quantity in the cart.
                        cart_dict[i]['Q'] += Q;
                        var temp_Q = cart_dict[i]['Q']
                        // Break out of the for-loop.
                        break;
                    } // End of if-statement.
                } // End of for-loop.

                // If dup is 1:
                if (dup == 1){
                    // Iterate through the array.
                    for(const j of count){
                        // Save the values of each row of the cart.
                        cat_val = document.querySelector("#category"+j).value;
                        desc_val = document.querySelector("#description"+j).value;
                        port_val = document.querySelector("#portion"+j).value;
                        q_val = document.querySelector("#quantity"+j).value;
                        // If the rows match the current selected items, update the quantity.
                        if((cat_val == category.options[category.selectedIndex].text) && (desc_val == description.options[description.selectedIndex].text) && (port_val == portion.options[portion.selectedIndex].text)){
                            // Update the quantity in the table.
                            document.querySelector("#quantity"+j).setAttribute('value', temp_Q);
                        } // End of if-statement.
                    } // End of for-loop.
                } //End of if-statement.

                else {
                    // Assign the new rows their new ID.
                    document.querySelector("#text1").setAttribute('value', category.options[category.selectedIndex].text);
                    document.querySelector("#text2").setAttribute('value', description.options[description.selectedIndex].text);
                    document.querySelector("#text3").setAttribute('value', portion.options[portion.selectedIndex].text);
                    document.querySelector("#text4").setAttribute('value', parseInt($('#quantity').val()));

                    document.querySelector("#text1").id = "category"+row_count;
                    document.querySelector("#text2").id = "description"+row_count;
                    document.querySelector("#text3").id = "portion"+row_count;
                    document.querySelector("#text4").id = "quantity"+row_count;
                    document.querySelector("#alonTr1").id = "alonTr"+row_count;

                    // Generate the new row.
                    $(".model1 tbody .alonTr").clone().appendTo(".tabInfo .tbody1");

                    // Reset the IDs.
                    document.querySelector("#category"+row_count).id = "text1";
                    document.querySelector("#description"+row_count).id = "text2";
                    document.querySelector("#portion"+row_count).id = "text3";
                    document.querySelector("#quantity"+row_count).id = "text4";
                    document.querySelector("#alonTr"+row_count).id = "alonTr1";
                    count.push(row_count);
                    row_count++;


                    cart_dict.push({'date':date, 'time': time, 'BSL': BSL,
                                    'categoryId': categoryId, 'descriptionId': descriptionId, 'portionId': portionId,
                                    'Q': Q,'comment':comment
                                    });
                }
        } // End of Validation Check.

    }) // End of AddTr.
}); // End of cart_dict function.

function deltr(opp) {
    var length = $(".tabInfo .tbody1>tr").length;
    //alert(length);
    $(opp).parent().parent().remove();//delete row
    id = parseInt($(opp).parent().parent().attr('id').slice(-1));

    const index = count.indexOf(id)
    count.splice(index, 1);
    cart_dict.splice(index, 1);
    };