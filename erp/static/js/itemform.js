$(document).ready(function () {
    $("#id_department").change(function () {
        var department_id = $(this).val();
        $.ajax({
            url: "load-categories",
            data: { department_id: department_id },
            success: function (data) {
                $("#id_category").empty();
                $.each(data, function (index, category) {
                    console.log(category);
                    $("#id_category").append(new Option(category.category_name, category.id));
                });
            }
        });
    });
});