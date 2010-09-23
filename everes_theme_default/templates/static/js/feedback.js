var Feedback = {};
Feedback.generate_comment_uuid = function(evt) {
    $.ajax({
        'type': "POST",
        'url' : "/api/generate_uuid/",
        'dataType': "json",
        'success': function (data) {
            $("#before_comment").hide();
            $('form[@name=comment_form]')[0].action = $('#comment_url_base').val() + data[0].fields.uniqueId + "/";
        }
    });
};

Feedback.generate_trackback_uuid = function(evt) {
    $.ajax({
        'type': "POST",
        'url' : "/api/generate_uuid/",
        'dataType': "json",
        'success': function (data) {
            $("#before_trackback").hide();
            $('#trackbackurl').text($('#trackback_url_base').val() + data[0].fields.uniqueId + "/");
        }
    });
};
