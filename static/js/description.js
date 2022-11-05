var global_cat = 0;
var global_quantity = 0;
$("#category").change(function () {

  var e = document.getElementById('category');
  var url = $("#DiaryForm").attr("data-description-url");
  var categoryId = $('#category').val();
  global_cat = categoryId;

  $.ajax({

    url: url,
    data: {
      'category': categoryId
    },

    success: function (data) {
        $("#description").html(data);
    }

  });

});