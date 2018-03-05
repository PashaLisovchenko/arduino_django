function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});
$(document).ready(function() {
    var url = document.location.href;
    $('.send').click(function() {

    var knowledge_level = $('#id_knowledge_level').find(":selected").val();
    var analog = $('#id_analog').val();
    var digit = $('#id_digit').val();
    var voltage = $('#id_voltage').find(":selected").val();
    var processor_family = $('#id_processor_family').find(":selected").val();
    var language = $('#id_language').find(":selected").val();
    var price = $('#id_price').val();
    var form = $('#id_form').find(":selected").val();

    var processor = $('input[name=option1]:checked').val();
    console.log(processor);
    // console.log(knowledge_level, analog, digit, voltage, processor_family, language, price, form);
        $.ajax({
            type: "GET",
            url: url,
            dataType: 'html',
            data: {
                'knowledge_level':knowledge_level,
                'analog':analog,
                'digit':digit,
                'voltage':voltage,
                'processor_family':processor_family,
                'language':language,
                'price':price,
                'form':form
            },
            success: updateMessage,
            failure: function (data) {
                console.log("FAIL");
                console.log(data);
            }
        });
        function updateMessage(data) {
            console.log("SUCCESS");
            console.log(data);
            $('.board-tags').css({display: 'none'});
            $('.recommend').html(data);
        }
    });
});