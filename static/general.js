$(document).ready(function() {
    $(".show-confirm").click(function(event) {
        a = $(this);
        $.fn.dialog2.helpers.confirm(a.data('clickmessage'), {
            confirm: function() {
                $.getJSON(a.attr('href'), {}, function(data,status){
                    if( status=='success' ) {
                        if(data.status==true) {
                            location.reload();
                        } else {
                            alert(data.message)
                        }
                    } else {
                        alert('{% blocktrans %}Произошла непредвиденная ошибка{% endblocktrans %}')
                    }
                })                      
            }, 
            decline: function() {  }
        });
        event.preventDefault(event);
    });
});