$(document).ready(function() {

  // вызов диалога отправки смс из формы редактирования аккаунта
  $("#modal-sendsms-dialog-table").click(function(event) {
    var element = $(this);

    $('<div/>').dialog2({
      title: gettext('Отправить SMS'), 
      content: element.attr('href')+'?accounts=' + element.attr('accountid'), 
      id: "server-notice"
    });
    
    event.preventDefault(event);
  });

});