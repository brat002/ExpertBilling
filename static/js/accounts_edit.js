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

  // отображение полей для юр. лица при выборе соответствующего признака
  $('#id_organization').click(function() {
    if ($('#id_organization').is(':checked')){
      $('#organization-fieldset').show();
    } else {
      $('#organization-fieldset').hide();
    }
  });

  if ($('#id_organization').is(':checked')){
    $('#organization-fieldset').show();
  }else{
    $('#organization-fieldset').hide();
  }

  $("#modal-transaction-dialog").click(function(event) {
    var element = $(this);
    
    $('<div/>').dialog2({
      title: gettext('Внести платёж'), 
      content: element.attr('href')+'?accounts='+element.data('accountid'), 
      id: "server-notice"
    });

    event.preventDefault(event);
  });

});