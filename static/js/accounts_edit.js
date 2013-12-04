$(document).ready(function() {

  // вызов диалога отправки смс из формы редактирования аккаунта
  $("#modal-sendsms-dialog-table").click(function(event) {
    var element = $(this);

    $('<div/>').dialog2({
      title: gettext('Отправить SMS'), 
      content: element.attr('href')+'?accounts='+element.data('accountid'), 
      id: "server-notice"
    });

    event.preventDefault(event);
  });

  $(".comment-done").click(function(event) {
    $('<div />').dialog2({
      title: gettext('Изменить запись'),
      content: this.href, 
    });

    event.preventDefault(event);
  });

});