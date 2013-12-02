    $(document).ready(function() {
            /*
            $("#id_phone_m").inputmask("mask", {"mask": ["+9[9][9]-[9][9]-[9][9][9][9][9][9][9]",], skipOptionalPartCharacter: "", clearMaskOnLostFocus: true });
            $("#id_phone_h").inputmask("mask", {"mask": ["+9[9][9]-[9][9]-[9][9][9][9][9][9][9]"], skipOptionalPartCharacter: "", clearMaskOnLostFocus: true });
            $("#id_contactperson_phone").inputmask("mask", {"mask": ["+9[9][9]-[9][9]-[9][9][9][9][9][9][9]"], skipOptionalPartCharacter: "", clearMaskOnLostFocus: true });
            */


            {% if account %}

            {% endif %}
        //$('#generate_username').popover({title:'Действие над аккаунтом', content: 'Сгенерировать имя пользователя'});
        $("#generate_username").click(function() {
          $.getJSON('{% url 'generate_credentials' %}',{action:'login'},function(data,status){
           if( status=='success' ){
             if(data.success==true)
              $("#id_username").val(data.generated);
            else
              alert(data.generated)
          }else{
           alert('{% blocktrans %}В процессе отправки произошла ошибка.{% endblocktrans %}')
         }
       })
        });

        $("#modal-sendsms-dialog-table").click(function(event) {


          $('<div/>').dialog2({
            title: "{% blocktrans %}Отправить SMS{% endblocktrans %}", 
            content: this.href+'?accounts={{account.id}}', 
            id: "server-notice"
          });

          event.preventDefault(event);
        });
        
        //$('#generate_password').popover({title:'Действие над аккаунтом', content: 'Сгенерировать пароль'});
        $('#id_organization').click(function() {
          if ($('#id_organization').is(':checked')){
            $('#organization-fieldset').show();
          }else{
            $('#organization-fieldset').hide();
          }
          
        });
        if ($('#id_organization').is(':checked')){
          $('#organization-fieldset').show();
        }else{
          $('#organization-fieldset').hide();
        }
        
        $("#generate_password").click(function() {
          $.getJSON('{% url 'generate_credentials' %}',{action:'password'},function(data,status){
            if( status=='success' ){
              if(data.success==true)
                        //$("#id_password").val(data.generated);
                      $("#{{form.password.auto_id}}").val(data.generated);
                      else
                        alert(data.generated)
                    }else{
                      alert('{% blocktrans %}В процессе отправки произошла ошибка :({% endblocktrans %}')
                    }
                  })
        });


            //$('#modal-accounttariff-dialog').popover({title:'Действие над аккаунтом', content: 'Cменить тарифный план'});

            $("#modal-accounttariff-dialog").click(function(event) {
             $('<div/>').dialog2({
               title: "{% blocktrans %}Изменение тарифного плана{% endblocktrans %}", 
               content: "/ebsadmin/accounttariff/edit/?account_id={{account.id}}", 
               id: "server-notice"
             });

             event.preventDefault(event);
           });


            $("#modal-accounttariff-dialog-table").click(function(event) {
              $('<div/>').dialog2({
                title: "{% blocktrans %}Изменение тарифного плана{% endblocktrans %}", 
                content: "/ebsadmin/accounttariff/edit/?account_id={{account.id}}", 
                id: "server-notice"
              });

              event.preventDefault(event);
            });


            //$('#modal-suspendedperiod-dialog-table').popover({title:'Добавить период без списаний', content: 'Добавить период, во время которого с аккаунта не будут производиться списания по периодическим и подключаемым услугам.'});

            $("#modal-suspendedperiod-dialog-table").click(function(event) {
              $('<div/>').dialog2({
                title: "{% blocktrans %}Добавить период без списаний услуг{% endblocktrans %}", 
                content: "{% url 'suspendedperiod' %}?account_id={{account.id}}", 
                id: "server-notice"
              });

              event.preventDefault(event);
            });


            $("#modal-transaction-dialog").click(function(event) {
              $('<div/>').dialog2({
                title: "{% blocktrans %}Внести платёж{% endblocktrans %}", 
                content: "{% url 'transaction_edit' %}?account_id={{account.id}}", 
                id: "server-notice"
              });

              event.preventDefault(event);
            });

            $("#modal-bonustransaction-dialog").click(function(event) {
              $('<div/>').dialog2({
                title: "{% blocktrans %}Внести бонусный платёж{% endblocktrans %}", 
                content: "{% url 'bonus_transaction_edit' %}?account_id={{account.id}}", 
                id: "server-notice"
              });

              event.preventDefault(event);
            });
            
            $("#modal-accounthardware-dialog-table").click(function(event) {
              $('<div />').dialog2({
                title: "{% blocktrans %}Прикрепить оборудование{% endblocktrans %}", 
                content: "{% url 'accounthardware' %}?account_id={{account.id}}", 
                id: "accounthardware-modal"
              });

              event.preventDefault(event);
            });


            $("#modal-accountaddonservice-dialog").click(function(event) {
              $('<div />').dialog2({
                title: "{% blocktrans %}Прикрепить подключаемую услугу{% endblocktrans %}", 
                content: "{% url 'accountaddonservice' %}?account_id={{account.id}}", 
                id: "accountaddonservicer-modal"
              });

              event.preventDefault(event);
            });


            $("#modal-templateselect-dialog").click(function(event) {
              $('<div />').dialog2({
                title: "{% blocktrans %}Выберите шаблон документа{% endblocktrans %}", 
                content: "{% url 'templateselect' %}?account_id={{account.id}}&type=1&type=2", 
                id: "templateselect-modal",
              });

              event.preventDefault(event);
            });

            $(function() {
              $(".open-custom-dialog").click(function(event) {
                $('<div />').dialog2({
                  title: "{% blocktrans %}Добавить{% endblocktrans %}", 
                  content: this.href, 
                  id: "accountaddonservicer-modal"
                });

                event.preventDefault(event);
              });
            });
            $(".show-confirm").click(function(event) {
              a=$(this);
              $.fn.dialog2.helpers.confirm("{% blocktrans %}Вы действительно хотите удалить?{% endblocktrans %}", {
                confirm: function() {
                  $.getJSON(a.attr('href'),{},function(data,status){
                   if( status=='success' ){
                    if(data.status==true)
                    {
                     location.reload();
                   }else{
                    alert(data.message)
                  }

                }else{
                 alert('{% blocktrans %}Произошла непредвиденная ошибка{% endblocktrans %}')
               }

             })                       
                }, 
                decline: function() {  }
              });

              event.preventDefault(event);
            });
            $('#id_house').autocomplete({
              source: function( request, response )
              {                      
                $.ajax(
                { 
                  url: "{% url 'house' %}",
                  data: {
                    term: request.term, 
                                street_name: $('#id_street').val(),    //Pass the selected country to php
                                city_id: $('#id_city').val()
                              },        
                        type: "POST",  // a jQuery ajax POST transmits in querystring format in utf-8
                        dataType: "json",   //return data in json format                                                                                                                                       
                        success: function( data ) 
                        {
                          response( $.map( data.records, function( item ) 
                          {
                            return item.name
                          }));
                        }
                      });                
              },
                minChars: 0, // Минимальная длина запроса для срабатывания автозаполнения
                maxHeight: 400, // Максимальная высота списка подсказок, в пикселях
                width: 300, // Ширина списка
                zIndex: 9999, // z-index списка
                deferRequestBy: 300, // Задержка запроса (мсек), на случай, если мы не хотим слать миллион запросов, пока пользователь печатает. Я обычно ставлю 300.
                onSelect: function(data, value){ }, // Callback функция, срабатывающая на выбор одного из предложенных вариантов,
              });
    $('#id_street').autocomplete({
      source: function( request, response )
      {                      
        $.ajax(
        { 
          url: "{% url 'street' %}",
          data: {
            term: request.term, 
            city_id: $('#id_city').val()
          },        
                        type: "POST",  // a jQuery ajax POST transmits in querystring format in utf-8
                        dataType: "json",   //return data in json format                                                                                                                                       
                        success: function( data ) 
                        {
                          response( $.map( data.records, function( item ) 
                          {
                            return item.name
                          }));
                        }
                      });                
      },
                minChars: 0, // Минимальная длина запроса для срабатывания автозаполнения
                maxHeight: 400, // Максимальная высота списка подсказок, в пикселях
                width: 300, // Ширина списка
                zIndex: 9999, // z-index списка
                deferRequestBy: 300, // Задержка запроса (мсек), на случай, если мы не хотим слать миллион запросов, пока пользователь печатает. Я обычно ставлю 300.
                onSelect: function(data, value){ }, // Callback функция, срабатывающая на выбор одного из предложенных вариантов,
              });
            //activate latest tab, if it exists:
            var lastTab = $.cookie('account_last_tab');
            if (lastTab) {
              $('ul.nav-tabs').children().removeClass('active');
              $('a[href='+ lastTab +']').parents('li:first').addClass('active');
              $('div.tab-content').children().removeClass('active');
              $(lastTab).addClass('active');
            }else
            $('#tab-control a[href="#tab-first"]').tab('show');
            

            $('a[data-toggle="tab"]').on('shown', function(e){
                  //save the latest tab using a cookie:
                  $.cookie('account_last_tab', $(e.target).attr('href'));
                });

            $("#id_account-toolbar-save").click(function(event) {
              $('#id_form').submit();
              event.preventDefault(event);
            });


            /* subacc */
            $('#id_assign_vpn_ip_address').popover({title:'{% blocktrans %}Подбор IP адреса{% endblocktrans %}', content: '{% blocktrans %}Выдать следующий IP из пула или показать доcтупные{% endblocktrans %}', trigger: 'hover'});
            $('#id_subacc-vpn_ip_address').autocomplete({
              source: function( request, response )
              {                      
                $.ajax(
                { 
                  url: "{% url 'getipfrompool' %}",
                  data: {
                    term: request.term, 
                                    pool_id: $('#id_subacc-ipv4_vpn_pool').val(),    //Pass the selected country to php
                                  },        
                            type: "POST",  // a jQuery ajax POST transmits in querystring format in utf-8
                            dataType: "json",   //return data in json format                                                                                                                                       
                            success: function( data ) 
                            {
                              response( $.map( data.records, function( item ) 
                              {
                                return item
                              }));
                            }
                          });                
              },
                    minChars: 0, // Минимальная длина запроса для срабатывания автозаполнения
                    maxHeight: 400, // Максимальная высота списка подсказок, в пикселях
                    width: 300, // Ширина списка
                    zIndex: 9999, // z-index списка
                    deferRequestBy: 300, // Задержка запроса (мсек), на случай, если мы не хотим слать миллион запросов, пока пользователь печатает. Я обычно ставлю 300.
                    onSelect: function(data, value){ }, // Callback функция, срабатывающая на выбор одного из предложенных вариантов,
                  });
    $('#id_subacc-vpn_ip_address').click(function(){$('#id_subacc-vpn_ip_address').autocomplete('search')});
    $('#id_assign_vpn_ip_address').click(function(){
      if ($('#id_subacc-vpn_ip_address').val()=='' || $('#id_subacc-vpn_ip_address').val()=='0.0.0.0'){
        $('#id_subacc-vpn_ip_address').val('')
      }
      if ($('#id_subacc-vpn_ip_address').val()){
        $('#id_subacc-vpn_ip_address').autocomplete('search')
        return
      }
      $.ajax(
      { 
        url: "{% url 'getipfrompool' %}",
        data: {
          term: $('#id_subacc-vpn_ip_address').val(), 
                                    pool_id: $('#id_subacc-ipv4_vpn_pool').val(),    //Pass the selected country to php
                                    limit:1
                                  },        
                            type: "POST",  // a jQuery ajax POST transmits in querystring format in utf-8
                            dataType: "json",   //return data in json format                                                                                                                                       
                            success: function( data ) 
                            {
                              $('#id_subacc-vpn_ip_address').val(data.records);
                            }
                          });   
    });

    $('#id_assign_ipn_ip_address').popover({title:'{% blocktrans %}Подбор IP адреса{% endblocktrans %}', content: '{% blocktrans %}Выдать следующий IP из пула или показать дсотупные{% endblocktrans %}', trigger: 'hover'});
    $('#id_subacc-ipn_ip_address').autocomplete({
      source: function( request, response )
      {                      
        $.ajax(
        { 
          url: "{% url 'getipfrompool' %}",
          data: {
            term: request.term, 
                                    pool_id: $('#id_subacc-ipv4_ipn_pool').val(),    //Pass the selected country to php
                                  },        
                            type: "POST",  // a jQuery ajax POST transmits in querystring format in utf-8
                            dataType: "json",   //return data in json format                                                                                                                                       
                            success: function( data ) 
                            {
                              response( $.map( data.records, function( item ) 
                              {
                                return item
                              }));
                            }
                          });                
      },
                    minChars: 0, // Минимальная длина запроса для срабатывания автозаполнения
                    maxHeight: 400, // Максимальная высота списка подсказок, в пикселях
                    width: 300, // Ширина списка
                    zIndex: 9999, // z-index списка
                    deferRequestBy: 300, // Задержка запроса (мсек), на случай, если мы не хотим слать миллион запросов, пока пользователь печатает. Я обычно ставлю 300.
                    onSelect: function(data, value){ }, // Callback функция, срабатывающая на выбор одного из предложенных вариантов,
                  });
    $("#modal-ipn-ping-dialog").click(function(event) {
      $('<div />').dialog2({
        title: "Ping", 
        content: "{% url 'tools_ping' %}?ip="+ $('#id_subacc-ipn_ip_address').val()
      });

      event.preventDefault(event);
    });
    $("#modal-vpn-ping-dialog").click(function(event) {
      $('<div />').dialog2({
        title: "Ping", 
        content: "{% url 'tools_ping' %}?ip="+ $('#id_subacc-vpn_ip_address').val()
      });

      event.preventDefault(event);
    });
    $('#id_subacc-ipn_ip_address').click(function(){$('#id_subacc-ipn_ip_address').autocomplete('search')});
    $('#id_subacc-ipv6_vpn_ip_address').click(function(){$('#id_subacc-ipv6_vpn_ip_address').autocomplete('search')});
    $('#id_subacc-vpn_ipv6_ip_address').autocomplete({
      source: function( request, response )
      {                      
        $.ajax(
        { 
          url: "{% url 'getipfrompool' %}",
          data: {
            term: request.term, 
                                    pool_id: $('#id_subacc-ipv6_vpn_pool').val(),    //Pass the selected country to php
                                  },        
                            type: "POST",  // a jQuery ajax POST transmits in querystring format in utf-8
                            dataType: "json",   //return data in json format                                                                                                                                       
                            success: function( data ) 
                            {
                              response( $.map( data.records, function( item ) 
                              {
                                return item
                              }));
                            }
                          });                
      },
                    minChars: 0, // Минимальная длина запроса для срабатывания автозаполнения
                    maxHeight: 400, // Максимальная высота списка подсказок, в пикселях
                    width: 300, // Ширина списка
                    zIndex: 9999, // z-index списка
                    deferRequestBy: 300, // Задержка запроса (мсек), на случай, если мы не хотим слать миллион запросов, пока пользователь печатает. Я обычно ставлю 300.
                    onSelect: function(data, value){ }, // Callback функция, срабатывающая на выбор одного из предложенных вариантов,
                  });
    $('#id_subacc-assign_ipv6_vpn_ip_address').click(function(){
      if ($('#id_subacc-vpn_ipv6_ip_address').val()=='' || $('#id_subacc-vpn_ipv6_ip_address').val()==':::'){
        $('#id_subacc-vpn_ipv6_ip_address').val('')
      }
      if ($('#id_subacc-vpn_ipv6_ip_address').val()){
        $('#id_subacc-vpn_ipv6_ip_address').autocomplete('search')
        return
      }
      $.ajax(
      { 
        url: "{% url 'getipfrompool' %}",
        data: {
          term: $('#id_subacc-vpn_ipv6_ip_address').val(), 
                                    pool_id: $('#id_subacc-ipv6_vpn_pool').val(),    //Pass the selected country to php
                                    limit:1
                                  },        
                            type: "POST",  // a jQuery ajax POST transmits in querystring format in utf-8
                            dataType: "json",   //return data in json format                                                                                                                                       
                            success: function( data ) 
                            {

                              $('#id_subacc-vpn_ipv6_ip_address').val(data.records);
                            }
                          });   
    });


    $('#id_assign_ipn_ip_address').click(function(){
      if ($('#id_subacc-ipn_ip_address').val()=='' || $('#id_subacc-ipn_ip_address').val()=='0.0.0.0'){
        $('#id_subacc-ipn_ip_address').val('')
      }
      if ($('#id_subacc-ipn_ip_address').val()){
        $('#id_subacc-ipn_ip_address').autocomplete('search')
        return
      }
      $.ajax(
      { 
        url: "{% url 'getipfrompool' %}",
        data: {
          term: $('#id_subacc-ipn_ip_address').val(), 
                                    pool_id: $('#id_subacc-ipv4_ipn_pool').val(),    //Pass the selected country to php
                                    limit:1
                                  },        
                            type: "POST",  // a jQuery ajax POST transmits in querystring format in utf-8
                            dataType: "json",   //return data in json format                                                                                                                                       
                            success: function( data ) 
                            {
                              $('#id_subacc-ipn_ip_address').val(data.records);
                            }
                          });   
    });

    $('#id_get_mac_address').popover({title:'{% blocktrans %}Внимание{% endblocktrans %}', content: '{% blocktrans %}Этот функционал поддерживается только при использовании RouterOS MikroTik{% endblocktrans %}', trigger: 'hover'});
    $('#id_get_mac_address').click(function(){
      if (!$('#id_subacc-nas').val()==null){
        $.fn.dialog2.helpers.alert("{% blocktrans %}Вы не выбрали сервер доступа.{% endblocktrans %}", { 

        });
        return
      };
      if ($('#id_subacc-ipn_ip_address').val()==''){
        $.fn.dialog2.helpers.alert("{% blocktrans %}Вы не указали IPN IP адрес.{% endblocktrans %}", { 

        });
        return
      };
      $.ajax(
      { 
        url: "{% url 'get_mac_for_ip' %}",
        data: {
          nas_id: $('#id_subacc-nas').val(), 
                                    ipn_ip_address: $('#id_subacc-ipn_ip_address').val(),    //Pass the selected country to php
                                  },        
                            type: "POST",  // a jQuery ajax POST transmits in querystring format in utf-8
                            dataType: "json",   //return data in json format                                                                                                                                       
                            success: function( data ) 
                            {   
                              if(data.success==true){
                                $('#id_subacc-ipn_mac_address').val(data.mac);
                              }else{
                                $.fn.dialog2.helpers.alert("{% blocktrans %}Не удалось получить MAC адрес по причине {% endblocktrans %}"+ data.message, { 

                                });
                              }
                            }
                          });   


  });
    $("#subacc_generate_username").click(function() {
      $.getJSON('{% url 'generate_credentials' %}',{action:'login'},function(data,status){
        if( status=='success' ){
          if(data.success==true)
            $("#id_subacc-username").val(data.generated);
          else
            alert(data.generated)
        }else{
          alert('{% blocktrans %}В процессе отправки произошла ошибка{% endblocktrans %}')
        }
      })
    });
    $("#subacc_generate_password").click(function() {
      $.getJSON('{% url 'generate_credentials' %}',{action:'password'},function(data,status){
        if( status=='success' ){
          if(data.success==true)
            $("#id_subacc-password").val(data.generated);
          else
            alert(data.generated)
        }else{
          alert('{% blocktrans %}В процессе отправки произошла ошибка{% endblocktrans %}')
        }
      })
    });
    /* subacc */

    $(".comment-done").click(function(event) {
      $('<div />').dialog2({
        title: "{% blocktrans %}Изменить запись{% endblocktrans %}", 
        content: this.href, 
      });

      event.preventDefault(event);
    });
  });