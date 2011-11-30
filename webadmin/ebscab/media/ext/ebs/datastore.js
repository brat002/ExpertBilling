Ext.onReady(function(){

EBS.store.logged_user = {
                username: username //stored in 'index' page
            };

// Accounts
EBS.reader.accounts = new Ext.data.JsonReader({
    root: 'records',
    id: 'id',
    idProperty: 'id',
    fields: [
        {name:'id', type:'int'},
        'vpn_ip_address', 'status', 'ipn_ip_address','username','password', 
        'city', 'street', 'nas', 'fullname', 'email', 'comment',
        {name:'created', type: 'date', dateFormat: Date.patterns.ISO8601Long},
        {name:'ballance', type:'float'},
        {name:'credit', type:'float'}
    ]
});
EBS.writer.accounts = new Ext.data.JsonWriter({
    root: 'records',
    id: 'id',
    fields: [
        {name:'id', type:'int'},
        'vpn_ip_address', 'status', 'ipn_ip_address','username','password',
        'city', 'street', 'nas', 'fullname', 'email', 'comment',
        {name:'created', type: 'date', dateFormat: Date.patterns.ISO8601Long},
        {name:'ballance', type:'float'},
        {name:'credit', type:'float'}
    ]
});

EBS.store.accounts_ = new Ext.data.DirectStore({
              storeId:'accounts',
              paramsAsHash: true,
              autoLoad: {params:{start:0, limit:100}},
              directFn: EBS.accounts.getAccountsList,
              reader: EBS.reader.accounts,
              writer: EBS.writer.accounts ,
              /*fields: ['vpn_ip_address', 'status', 'ipn_ip_address','username',
                      'password','id', 'city', 'street', 'credit', 'nas',
                      'created','fullname', 'email', 'ballance'],*/
              //root: 'records',
              remoteSort:true,
              sortInfo:{
                   field:'username',
                   direction:'ASC'
              },
              listeners: {
                    load:function(){
                        //console.info('load',this,arguments);
                    }
            }
        });

EBS.store.accounts = new Ext.data.GroupingStore({
    paramsAsHash: true,
    autoLoad: {params:{start:0, limit:100}},
    proxy: new Ext.data.HttpProxy({
        url: '/ebsadmin/accounts/',
        method:'GET',
    }),    
    reader:new Ext.data.JsonReader({
        root: 'records',
        id: 'id',
        idProperty: 'id',
        totalProperty:'total',
        fields: ['comment', 'tariff', 'status', 'allow_webcab', 'house', 'street', 'postcode', 'suspended', 'id', 'row', {'name':'city', type:'string'}, 'systemuser', 'contactperson_phone', 'ipn_status', 'nas', 'entrance_code', 'elevator_direction', 'passport', 'allow_ipn_with_null', 'allow_ipn_with_minus', 'last_balance_null', 'email', 'username', 'entrance', 'phone_m', 'phone_h', 'allow_ipn_with_block', 'allow_expresscards', 'contract', 'address', 'private_passport_number', 'password', 'disabled_by_limit', 'balance_blocked', 'room', 'created', 'region', 'contactperson', 'credit', 'ballance', 'house_bulk', 'fullname', 'passport_given'],
        
    }),
    //fields: ['comment', 'status', 'allow_webcab', 'house', 'street', 'postcode', 'suspended', 'id', 'row', 'city', 'systemuser', 'contactperson_phone', 'ipn_status', 'nas', 'entrance_code', 'elevator_direction', 'passport', 'allow_ipn_with_null', 'allow_ipn_with_minus', 'last_balance_null', 'email', 'username', 'entrance', 'phone_m', 'phone_h', 'allow_ipn_with_block', 'allow_expresscards', 'contract', 'address', 'private_passport_number', 'password', 'disabled_by_limit', 'balance_blocked', 'room', 'created', 'region', 'contactperson', 'credit', 'ballance', 'house_bulk', 'fullname', 'passport_given'],
    //root: 'records',
    remoteSort:false,
    sortInfo:{
         field:'username',
         direction:'ASC'
    },
    listeners: {
          load:function(){
             // console.info('load',this,arguments);
          }
  }
});

EBS.store.sessions = new Ext.data.GroupingStore({
    paramsAsHash: true,
    autoLoad: {params:{start:0, limit:100}},
    proxy: new Ext.data.HttpProxy({
        url: '/ebsadmin/sessions/',
        method:'GET',
    }),    
    reader:new Ext.data.JsonReader({
        root: 'records',
        id: 'id',
        idProperty: 'id',
        totalProperty:'total',
        fields: ['account', 'called_id', 'interrim_update', 'session_status', 'bytes_in', 'date_end', 'date_start', 'session_time', 'caller_id', 'bytes_out', 'sessionid', 'speed_string', 'nas_id', 'framed_protocol', 'framed_ip_address', 'id', 'subaccount'],
        
    }),
    //fields: ['comment', 'status', 'allow_webcab', 'house', 'street', 'postcode', 'suspended', 'id', 'row', 'city', 'systemuser', 'contactperson_phone', 'ipn_status', 'nas', 'entrance_code', 'elevator_direction', 'passport', 'allow_ipn_with_null', 'allow_ipn_with_minus', 'last_balance_null', 'email', 'username', 'entrance', 'phone_m', 'phone_h', 'allow_ipn_with_block', 'allow_expresscards', 'contract', 'address', 'private_passport_number', 'password', 'disabled_by_limit', 'balance_blocked', 'room', 'created', 'region', 'contactperson', 'credit', 'ballance', 'house_bulk', 'fullname', 'passport_given'],
    //root: 'records',
    remoteSort:false,
    sortInfo:{
         field:'account',
         direction:'ASC'
    },
    listeners: {
          load:function(){
             // console.info('load',this,arguments);
          }
  }
});

EBS.store.subaccounts = new Ext.data.JsonStore({
    paramsAsHash: true,
    //autoLoad: {params:{start:0, limit:100}},
    proxy: new Ext.data.HttpProxy({
        url: '/ebsadmin/subaccounts/',
        method:'GET',
    }),    
    fields: ['vpn_ip_address', 'status', 'ipn_ip_address','username',
            'password','id', 'city', 'street', 'credit', 'nas',
            'created','fullname', 'email', 'ballance'],
    root: 'records',
    remoteSort:true,
    sortInfo:{
         field:'username',
         direction:'ASC'
    },
    listeners: {
          load:function(){
             // console.info('load',this,arguments);
          }
  }
});

//EBS.store.subaccounts = 
// EOF Accounts


EBS.store.session_monitor = new Ext.data.DirectStore({
              storeId:'radius',
              paramsAsHash: true,
              directFn: EBS.radius.getSessionList,
              fields: ['id','account_id', 'account', 'sessionid', 'date_start', 'interrim_update', 'date_end', 'caller_id', 'called_id', 'nas_id', 'session_time', 'framed_protocol', 'bytes_in', 'bytes_out', 'session_status', 'framed_ip_address', 'nas_int_id'],
              root: 'records',
              remoteSort:false,
              sortInfo:{
                   field:'id',
                   direction:'ASC'
              },
              listeners: {
                    load:function(){
                        console.info('load',this,arguments);
                    }
            }

        });


EBS.store.nas = new Ext.data.DirectStore({
              storeId:'nas',
              paramsAsHash: true,
              directFn: EBS.nas.getNasList,
              autoLoad: {params:{start:0, limit:100}},
              fields: ['id','name', 'identify', 'ipaddress', 'secret'],
              root: 'records',
              remoteSort:false,
              sortInfo:{
                   field:'ipaddress',
                   direction:'ASC'
              },
              listeners: {
                    load:function(){
                    //    console.info('load',this,arguments);
                    }
            }

        });

EBS.store.settlement_periods = new Ext.data.DirectStore({
              storeId:'settlement_period',
              paramsAsHash: true,
              directFn: EBS.settlement_period.getSettlementPeriods,
              fields: ['id','name', 'time_start', 'autostart', 'length', 'length_in'],
              root: 'records',
              remoteSort:false,
              sortInfo:{
                   field:'name',
                   direction:'ASC'
              },
              listeners: {
                    load:function(){
                    //    console.info('load',this,arguments);
                    }
            }

        });


});
