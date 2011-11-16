var mainMenu = [
    { // 0
    text:'Главное',
    expanded: true,
    children:[{
        text:'Аккаунты',
        id:'accounts',
        type:'xaccountspanel',
        singleton: true,
        leaf:true
    },{
        text:'Тарифные планы',
        id:'tarifs',
        leaf:true
    },{
        text:'Подключаемые услуги',
        id:'addonservices',
        leaf:true
    },{
        text:'Активные одключаемые услуги',
        id:'activeaddonservices',
        leaf:true
    },{
        text:'История операций нал л/с',
        id:'transactions',
        leaf:true
    },{
        text:'Сообщения',
        id:'messages',
        leaf:true
    }]

},{ // 1
    text:'Справочники',
    expanded: true,
    children:[{
        text:'Сервера доступа',
        id:'nasses',
        type:'ebs_nasPanel',
        leaf:true
    },{
        text:'Расчётные периоды',
        id:'settlementperiods',
        leaf:true
    },{
        text:'Периоды тарификации',
        id:'timeperiods',
        leaf:true
    },{
        text:'Классы трафика',
        id:'trafficclass',
        leaf:true
    },{
        text:'Пользователи',
        id:'systemusers',
        leaf:true
    },{
        text:'Шаблоны документов',
        id:'templates',
        leaf:true
    }]

},{ // 2
    text:'Карточная система',
    expanded: true,
    children:[{
        text:'Карточки',
        id:'cards',
        leaf:true
    },{
        text:'Дилеры',
        id:'dealers',
        leaf:true
    }]

},{ // 3
    text:'Мониторинг и статистика',
    expanded: true,
    children:[{
        text:'Монитор сессий',
        id:'sessionmonitor',
        leaf:true
    },{
        text:'Логи авторизацией',
        id:'authlogs',
        leaf:true
    },{
        text:'Сетевая статистика',
        id:'netflowstats',
        leaf:true
    },{
        text:'Логи системы',
        id:'systemlogs',
        leaf:true
    },{
        text:'Лог действий',
        id:'actionlogs',
        leaf:true
    }]

},{// 4
    text:'Отчёты',
    expanded: true,
    children:[{
        text:'Загрузка процессора',
        id:'cpuload',
        leaf:true
    },{
        text:'Загрузка памяти',
        id:'memload',
        leaf:true
    },{
        text:'Сессии',
        id:'sessionreport',
        leaf:true
    },{
        text:'Пирог',
        id:'netflowstats',
        leaf:true
    },{
        text:'Загрузка по группам',
        id:'groupstats',
        leaf:true
    },{
        text:'Динамика прибыли',
        id:'moneystats',
        leaf:true
    }]
}];
