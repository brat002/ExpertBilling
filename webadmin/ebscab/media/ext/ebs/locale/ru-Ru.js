// // EBS localization file
// URL template:
//             "ext/ebs/locale/" + LANGUAGE_CODE + ".js"
// 

// TODO: мультиязычность

Ext.onReady(function(){
    Date.patterns = {
        ISO8601Long: "Y-m-d H:i:s",
        ISO8601Short: "Y-m-d",
        ShortDate: "n/j/Y",
        LongDate: "l, F d, Y",
        FullDateTime: "l, F d, Y g:i:s A",
        MonthDay: "F d",
        ShortTime: "g:i A",
        LongTime: "g:i:s A",
        SortableDateTime: "Y-m-d\\TH:i:s",
        UniversalSortableDateTime: "Y-m-d H:i:sO",
        YearMonth: "F, Y"
    };

    EBS.moneyRenderer = function pctChange(val){
        if(val > 0){
            return '<span style="background-color:green;color:#ffdc51;">' + val.toFixed(2) + ' руб.</span>';
        }else if(val == 0){
            return '<span style="background-color:lightyellow;">' + val.toFixed(2) + ' руб.</span>';
        }
        else if(val < 0){
            return '<span style="background-color:red;color:#ffffff;">' + val.toFixed(2) + ' руб.</span>';
        }
        return val;
    }
});



var i18n = {
    // System
   
    welcomeText:        "<p>Click 'Users' button</p>",
    helpMenuInnerText:  "",
    firebugAlert:       "<br/><p>Активен отладчик! Существуют известные проблеммы производительности.</p>",
    logout:             "Выход",

    //Grid
    paginatorDispalyMsg: 'Displaying {0} - {1} of {2}',
    paginatorEmptyMsg: 'No Media Found'
};

i18n.accounts = {
    accounts    :'Аккаунты',
    //---
    id          : 'id',
    username    : 'имя пользователя',
    fio         : 'ФиО',
    ballance    : 'Баланс',
    nas         :'NAS',
    credit      :'Кредит',
    vpn_ip_address:'VPN IP',
    ipn_ip_address:'IPN IP',
    created     :'Created',
    email       :'Email'
    };




/*
    // Formatting and manipulating dates
    var now = new Date();
    var ISO8601Long = now.format(Date.patterns.ISO8601Long);
    //ISO8601Long is similar to 2009-03-05 14:01:45
    var ISO8601Short = now.format(Date.patterns.ISO8601Short);
    //ISO8601Long is similar to 2009-03-05
    var ShortDate = now.format(Date.patterns.ShortDate);
    //ISO8601Long is similar to 3/5/2009
    var LongDate = now.format(Date.patterns.LongDate);
    //ISO8601Long is similar to Thursday, March 05, 2009
    var FullDateTime = now.format(Date.patterns.FullDateTime);
    //ISO8601Long is similar to Thursday, March 05, 2009 2:01:45 PM
    var MonthDay = now.format(Date.patterns.MonthDay);
    //ISO8601Long is similar to March 05
    var ShortTime = now.format(Date.patterns.ShortTime);
    //ISO8601Long is similar to 2:01 PM
    var LongTime = now.format(Date.patterns.LongTime);
    //ISO8601Long is similar to 2:01:45 PM
    var SortableDateTime = now.format(Date.patterns.SortableDateTime);
    //ISO8601Long is similar to 2009-03-05T14:01:45
    var UniversalSortableDateTime = now.format(Date.patterns.UniversalSortableDateTime);
    //ISO8601Long is similar to 2009-03-05 14:01:45-0500
    var YearMonth = now.format(Date.patterns.YearMonth);
    //ISO8601Long is similar to March, 2009
*/