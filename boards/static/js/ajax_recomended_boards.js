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
            success: recommendation,
            failure: function (data) {
                console.log("FAIL");
                console.log(data);
            }
        });
        function recommendation(data) {
            console.log("SUCCESS");
            $('#boards').css({display: 'none'});
            $('.board-tags').css({display: 'none'});
            $('.recommend').html(data);
        }
    });
});