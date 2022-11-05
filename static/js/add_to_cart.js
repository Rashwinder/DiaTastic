var count = 1;
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
        var BSL = parseFloat(parseFloat($('#blood_sugar_level').val()).toFixed(1));
        if(BSL > 30 || BSL < 0 || !BSL){
            alert('Please check your Blood Sugar Levels.');
            return false;
        } else{
            val_check++;
        };

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

        if(val_check == 7){
            // If dictionary is not empty:
            if(cart_dict.length != 0){

                // Iterate through the dictionary.
                for(i = 0; i < cart_dict.length; i++){

                    // If there is a duplicate:
                    if((cart_dict[i]['categoryId'] == categoryId ) && (cart_dict[i]['descriptionId'] == descriptionId) && (cart_dict[i]['portionId'] == portionId)){
                        dup = 1;
                        break;
                        } // End of if-statement.
                    }; // End of for-loop.
                } // End of cart_dict.length > 0

                if (dup == 1){
                    // Update the quantity in the cart.
                    cart_dict[i]['Q'] += Q;

                    // Update the quantity in the table.
                    document.querySelector("#quantity"+parseInt(i+1)).setAttribute('value', cart_dict[i]['Q']);
                } // End of duplicate check.


                // If the length of the dictionary == 0;
                else {
                    // Assign the new rows their new ID.
                    document.querySelector("#text1").setAttribute('value', category.options[category.selectedIndex].text);
                    document.querySelector("#text2").setAttribute('value', description.options[description.selectedIndex].text);
                    document.querySelector("#text3").setAttribute('value', portion.options[portion.selectedIndex].text);
                    document.querySelector("#text4").setAttribute('value', parseInt($('#quantity').val()));

                    document.querySelector("#text1").id = "category"+count;
                    document.querySelector("#text2").id = "description"+count;
                    document.querySelector("#text3").id = "portion"+count;
                    document.querySelector("#text4").id = "quantity"+count;
                    document.querySelector("#alonTr1").id = "alonTr"+count;

                    // Generate the new row.
                    $(".model1 tbody .alonTr").clone().appendTo(".tabInfo .tbody1");

                    // Reset the IDs.
                    document.querySelector("#category"+count).id = "text1";
                    document.querySelector("#description"+count).id = "text2";
                    document.querySelector("#portion"+count).id = "text3";
                    document.querySelector("#quantity"+count).id = "text4";
                    document.querySelector("#alonTr"+count).id = "alonTr1";
                    count++;

                    cart_dict.push({'date':date, 'time': time, 'BSL': BSL,
                                    'categoryId': categoryId, 'descriptionId': descriptionId, 'portionId': portionId,
                                    'Q': Q,'comment':comment
                                    });}

            console.log('The count is:', count);
            console.log('The cart is:', cart_dict);
        } // End of Validation Check.

    }) // End of AddTr.
}); // End of cart_dict function.

function deltr(opp) {
    var length = $(".tabInfo .tbody1>tr").length;
    //alert(length);
    if (length <= 1) {
        alert("less one row");
    } else {
        count--;
        $(opp).parent().parent().remove();//delete row
        id = parseInt($(opp).parent().parent().attr('id').slice(-1));
        cart_dict.splice(id-1, 1);
        console.log('Count after removing item:', count);}
        };