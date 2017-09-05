$(document).ready(function() {
    $('#id_message_text').focus();
});

$('.input').keypress(function(e){
    if(e.keyCode==13) {
        if( !$('#id_message_text').val()=="" ) {
            $('.input').submit();
        } else {
            e.preventDefault();
        }
    }
})