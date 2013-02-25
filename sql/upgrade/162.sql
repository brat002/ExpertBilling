UPDATE billservice_template SET body='<html>
 <head>
 <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
 <style>
   td{
        FONT: 9px Times New Roman;
    }
    h1{
        FONT: 9px Arial;
    }
  </style>
 </head>
 <body>
  <table align=center width="85%">
    <tr>
     <td>
       <h1 align=center> <b> Квитанция об оплате услуг № {{transaction.id}} </b> </h1>
       <strong>Абонент:</strong> {{transaction.account.fullname}} <br>
       <strong>Логин:</strong> {{transaction.account.username}}<br>
       <strong>Сумма:</strong> {{transaction.summ|floatformat:2}}<br>
       <strong>Дата приема платежа:</strong> {{transaction.created}}<br>
    </td>
   </tr>
  </table>
 </body>
</html>' WHERE type_id=5;


UPDATE billservice_template SET body='<html>
            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            </head>
            <body>
              {% load billservice_tags %}
              {% mako %}
${account.id}<br />
${account.username}<br />
${account.password}<br />
${account.fullname}<br />
${account.email}<br />
${account.address}<br />

${account.status}<br />

${account.created}<br />
${account.ballance}<br />
${account.credit}<br />
${account.disabled_by_limit}<br />
${account.balance_blocked}<br />
${account.ipn_added}<br />
${account.city}<br />
${account.postcode}<br />
${account.region}<br />
${account.street}<br />
${account.house}<br />
${account.house_bulk}<br />
${account.entrance}<br />
${account.room}<br />
${account.allow_webcab}<br />
${account.allow_expresscards}<br />
${account.passport}<br />
${account.passport_date}<br />
${account.passport_given}<br />

              {% endmako %}
            
            
            </body>
            </html>
' WHERE type_id=1;

