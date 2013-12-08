$(document).ready(function() {

  // отображение диалогового окна для подтверждения действия
  $(".show-confirm").click(function(event) {
    a = $(this);

    if (a.data('clickmessage')) {
      message = a.data('clickmessage');
    } else {
      message = gettext('Удалить?');
    }

    $.fn.dialog2.helpers.confirm(message, {
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

  // отображение модального диалогового окна
  $(".general-modal-dialog").click(function(event) {
    var element = $(this);
    
    $('<div/>').dialog2({
      title: element.data('dlgtitle'), 
      content: element.attr('href'), 
      id: element.data('dlgbodyid')
    });

    event.preventDefault(event);
  });
});