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
    }]
}
];
