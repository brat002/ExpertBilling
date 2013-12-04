$(document).ready(function() {
    
    // отображение диалогового окна для подтверждения действия
    $(".show-confirm").click(function(event) {
        a = $(this);

        if (a.data('clickmessage')) {
            message = a.data('clickmessage');
        } else {
            message = gettext('Вы действительно хотите удалить?');
        }

        $.fn.dialog2.helpers.confirm(a.data('clickmessage'), {
            confirm: function() {
                $.getJSON(a.attr('href'), {}, function(data,status){
                    if(status == 'success') {
                        if(data.status == true) {
                            location.reload();
                        } else {
                            alert(data.message)
                        }
                    } else {
                        alert(gettext('Произошла непредвиденная ошибка'))
                    }
                })                      
            }, 
            decline: function() {}
        });
        event.preventDefault(event);
    });
});