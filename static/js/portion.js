$("#description").change(function () {

  var e = document.getElementById('description');
  var url = $("#DiaryForm").attr("data-portion-url");
  var categoryId = $('#category').val();
  var descriptionId = $('#description').val();

  $.ajax({

    url: url,
    data: {
      'category': categoryId,
      'description': descriptionId
    },

    success: function (data) {   // `data` is the return of the `load_cities` view function
        $("#portion").html(data);  // replace the contents of the city input with the data that came from the server
    }
  });

});