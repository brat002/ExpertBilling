$(document).ready(function() {

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

});