var url = "{% url 'create_view' %}";

function SendCart(){
    var data = {cart_items: JSON.stringify(cart_dict), csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value};
    var posting = $.post('/create_view/', data);
}

$(document).ready(function (){
    $('#submit').click(function(){
        SendCart();
        });
    });