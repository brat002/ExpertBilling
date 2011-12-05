Ext.onReady(function(){
    //Ext.app.REMOTING_API.enableBuffer = 100;
    Ext.ns('EBS');

    EBS.messages = {
        fadeSpeed: 250,
        fadeInterval:4000
    };
    
    EBS.base = {}; // Base components

    EBS.menu = [];

    // Datastore
    EBS.store = {};
    // Datastore field/type mapping
    EBS.reader = {};
    EBS.writer = {};
    

    EBS.topToolbar = [];
    EBS.bottomToolbar = [];
    EBS.forms = {}; // для форм из компонент
    EBS.windows = {};
    EBS.windows.keys =[];
    EBS.conponents = {};
    EBS.conponents.keys =[];
    Ext.Msg.minWidth = 360;
    
    // hide debug info. TODO: remove at production
    if(typeof(console) != "object"){
        var console = new (function(){
                this.log=function(){};
                this.info=this.log;
                this.trace=this.log
            })()
    }

    EBS.closeForm = function(self){
        winCmp = self.ownerCt.ownerCt;
        winCmp.hide().destroy();
        delete EBS.windows[winCmp.id];
    }
    
    ExInstancePanel = Ext.extend(Ext.Panel,{
    	
    	instance_id: 0,
    	parent_id:0,
    	ids:{},

    	initComponent: function() {     

    	    // Component Configuration...   
    	    var config = {
    	    		closable: true
    	    
    	    };  

    	    Ext.applyIf(this, Ext.applyIf(this.initialConfig, config));
    	    ExInstancePanel.superclass.initComponent.apply(this, arguments);       

    	},
    	
    });
    
    Ext.reg('xinstancecontainer', ExInstancePanel);
    
    ExInstanceWindow = Ext.extend(Ext.Window,{
    	
    	instance_id: 0,
    	parent_id:0,
    	ids:{},

    	initComponent: function() {     

    	    // Component Configuration...   
    	    var config = {
    	    		closable: true
    	    
    	    };  

    	    Ext.applyIf(this, Ext.applyIf(this.initialConfig, config));
    	    ExInstancePanel.superclass.initComponent.apply(this, arguments);       

    	},
    	
    });
    
    Ext.reg('xinstancewindow', ExInstanceWindow);
    
    EBS.displayForm = function(xtype, action, ids, self){
        /*
         * Вызывается из меню компоненты
         *
         * создает форму
         *
         **/

           console.log(action, self);
           var id, account_id;
           id=ids.id;
           
           account_id=ids.account_id;
            //Create edit window
           selection = self.selModel.selections;
           if(selection.items.length!=1 && id!=null){
               Ext.Msg.alert(i18n.information,i18n.please_select_one_row);
               return;
            }
           rec = selection.items[0];
           form = 'EBS.forms.'+xtype+'.'+action;
           window_key =  xtype+'_'+action;
           form_data = eval(form);
           form_callback = eval(form+'_submitAction');

           //if(typeof form_callback != "function")
           //    Ext.Msg.alert('Error: callback function is not accessible', form + '_submitAction ');

           //if(!EBS.windows[window_key]){
           winCmp = Ext.get(window_key);
           if(!winCmp){
                        winCmp = new ExInstanceWindow({
                            id:window_key,
                            instance_id:id,
                            ids:ids,
                            parent_id:account_id,
                            applyTo:Ext.get('body'),
                            //width:500,
                            //height:300,
                            //layout:'fit',
                            stateful:false,
                            title:form_data.windowTitle,
                            autoHeight: true,
                            autoWidth: true,
                            modal:true,
                            closable:true,
                            viewConfig: {
                                forceFit: true
                            },
                            
                            plain: true,
                            items: [form_data],
                            buttonAlign:'center',
                            buttons: [{
                                    text:'Ok',
                                    handler: function(obj, e){
                                    	form = this.ownerCt.ownerCt.items.items[0].getForm();
                                    	//alert(form.findField('service').getValue());
                                    	//form.submit({url:form.save_url, waitMsg:'Saving Data...', submitEmptyText: false, success: function(form,action) {        
                                        //	form.closeForm()}})	
                                        form_callback(obj, e, form,this.ownerCt.ownerCt);
                                        
                                        //
                                        //form.updateRecord(form.rec);
                                        //Update server data
                                        //form.rec.store.save();
                                        //winCmp = this.ownerCt.ownerCt;
                                        //winCmp.hide().destroy();
                                    	//form_data.submitForm(this);
                                        //delete EBS.windows[winCmp.id];
                                    }
                                },{
                                    text: 'Закрыть',
                                    handler: function(){
                                        EBS.closeForm(this)
                                    }
                                }]
                        });
                        EBS.windows[window_key] = winCmp;
                    }
             //form = winCmp.items.items[0].getForm();
             //form.rec = selection.items[0];
           if (id){
               form = winCmp.items.items[0].getForm();
               //form.rec = selection.items[0];
             
               //form.loadRecord(form.rec);
               form.load({url:form.url, method:'POST',params:{'id':id}} );
             }
             //form.loadRecord(form.rec);
             //form.load({url:'/account/', method:'GET',params:{'id':selection.items[0].id}} );
             winCmp.show();
    }

    EBS.displayCustomForm = function(xtype, action, ids, self){
        /*
         * Вызывается из меню компоненты
         *
         * создает форму
         *
         **/
    	   //alert(123);
           console.log(action, self);
           var id, account_id;
           id=ids.id;
           account_id=ids.account_id;
            //Create edit window
           //selection = self.selModel.selections;
           /*if(selection.items.length!=1 ){
               Ext.Msg.alert(i18n.information,i18n.please_select_one_row);
               return;
            }
            */
           //rec = selection.items[0];
           //alert(rec.id);
           form = 'EBS.forms.'+xtype+'.'+action;
           //alert(form);
           //alert(form);
           window_key =  xtype+'_'+action;
           //alert(window_key);
           form_data = eval(form);
           form_callback = eval(form+'_submitAction');

           //alert(form_data.windowTitle);
           //if(typeof form_callback != "function")
           //    Ext.Msg.alert('Error: callback function is not accessible', form + '_submitAction ');

           //if(!EBS.windows[window_key]){
           winCmp = Ext.get(window_key);
           if(!winCmp){
        	   		//alert('craca');
                        winCmp = new ExInstanceWindow({
                            id:window_key,
                            applyTo:Ext.get('body'),
                            instance_id:id,
                            ids:ids,
                            closable: true,
                            autoHeight: true,
                            autoWidth: true,
                            
                            modal:true,
                            stateful:false,
                            title:form_data.windowTitle,
                            viewConfig: {
                                forceFit: true
                            },
                            

                            plain: false,
                            items: [form_data],
                        });
                        EBS.windows[window_key] = winCmp;
                    }
           
           if (id){
             form = winCmp.items.items[0].getForm();
             //form.rec = selection.items[0];
           
             //form.loadRecord(form.rec);
             form.load({url:form.url, method:'POST',params:{'id':id}} );
           }
             //form.load({url:'/account/', method:'GET',params:{'id':selection.items[0].id}} );
           
             winCmp.show();
    }
    
    EBS.displayFormInTab = function(xtype, action, id, ids, self){
        /*
         * Вызывается из меню компоненты
         *
         * создает форму
         *
         **/

           console.log(action, self);
           
            //Create edit window
           /*selection = self.selModel.selections;
           if(selection.items.length!=1){
               Ext.Msg.alert(i18n.information,i18n.please_select_one_row);
               return;
            }
           rec = selection.items[0];*/
           form = 'EBS.forms.'+xtype+'.'+action;
           window_key =  xtype+'_'+action;
           form_data = eval(form);
           form_callback = eval(form+'_submitAction');

           //if(typeof form_callback != "function")
           //    Ext.Msg.alert('Error: callback function is not accessible', form + '_submitAction ');

           //if(!EBS.windows[window_key]){
           winCmp = Ext.get(window_key);

           //if(!winCmp){
           if(true){
                        winCmp = new ExInstancePanel({
                            id:window_key+id,
                            instance_id:id,
                            parent_id:id,
                            ids:ids,
                            applyTo:Ext.get('body'),
                            //width:500,
                            //height:300,
                            //bodyStyle:'padding:0 60px 0 60px',
                            title:form_data.windowTitle,
                            autoHeight: false,
                            viewConfig: {
                                forceFit: true
                            },

                            plain: true,
                            items: [form_data],

                        });
                        EBS.windows[window_key] = winCmp;
                    }
           	 if(id){
           		 form = winCmp.items.items[0].items.items[0].getForm();
           		 //form.rec = selection.items[0];
           		 //alert(form.url);
           		 form.load({url:form.url,method:form.method,params:{'id':id}});
           		 //form.loadRecord(form.rec);
           	 };
             EBS.windowCmp.add(winCmp)
             //winCmp.show();
    }

    EBS.displayFormInSpecTab = function(xtype, action, ids, tab, self){
        /*
         * Вызывается из меню компоненты
         *
         * создает форму
         *
         **/

           console.log(action, self);
           var id, account_id;
           id=ids.id;
           account_id=ids.account_id;
           selection = self.selModel.selections;
            //Create edit window
           /*
           if(selection.items.length!=1){
               Ext.Msg.alert(i18n.information,i18n.please_select_one_row);
               return;
            }
           rec = selection.items[0];*/
           form = 'EBS.forms.'+xtype+'.'+action;
           window_key =  xtype+'_'+action;
           form_data = eval(form);
           form_callback = eval(form+'_submitAction');

           //if(typeof form_callback != "function")
           //    Ext.Msg.alert('Error: callback function is not accessible', form + '_submitAction ');

           //if(!EBS.windows[window_key]){
           winCmp = Ext.get(window_key);

           //if(!winCmp){
           if(true){
                        winCmp = new ExInstancePanel({
                            id:window_key+id,
                            instance_id:id,
                            parent_id:account_id,
                            ids:ids,
                            applyTo:Ext.get('body'),
                            
                            
                            //height:1200,
                            //layout:'anchor',
                            //bodyStyle:'padding: 0 30% 0 30',
                            title:form_data.windowTitle,
                            closable:true,
                            //autoHeight: true,
                            //autoHeight: true,
                            //viewConfig: {
                            //    forceFit: true
                            //},
                            

                            
                            items: [form_data],

                        });
                        EBS.windows[window_key] = winCmp;
                    }
             form = winCmp.items.items[0].getForm();
             //form.rec = selection.items[0];
             //alert(account_id);
             if (id){
             	 form.load({url:form.url,method:form.method,params:{'id':selection.items[0].id}});
             };
             //form.loadRecord(form.rec);
             
             //tab.add(winCmp)
             EBS.windowCmp.add(winCmp)
             //winCmp.show();
    }

    
    
    EBS.displayWindow = function(xtype, params){
        /*
         * !!!Претендент на удаление!!!
         *
         * Вызывается из меню компоненты
         *
         * создает форму
         *
         * params = {action:action, self:self, selection:self.selModel.selections}
         **/
            //console.log(xtype, params)
    }

    //load menu
    var treePanel = new Ext.tree.TreePanel({
      id: 'tree-panel',
      //title: 'Sample Layouts',
        region:'north',
        split: true,
        //minSize: 150,
        autoScroll: true,
        autoHeight: true,
        // tree-specific configs:
        rootVisible: false,
        lines: true,
        singleExpand: false,
        useArrows: true,
        root: new Ext.tree.AsyncTreeNode({
            text: "Root",
            expanded: true,
            children: mainMenu
        }),
        listeners: {
                'click' : function(n){
                                    // get selected node
                                    var sn = this.selModel.selNode || {};
                                    if(n.leaf){ //&& n.id != sn.id
                                        var type = n.attributes.type;
                                        //console.info(n.id+'Grid',this,arguments, type);

                                        var type_exists = false;
                                        for(i=0;i<EBS.windows.keys.length;i++){
                                            if(EBS.windows.keys[i]==type){
                                                type_exists = true;
                                                break;
                                            }
                                        }
                                            /*  Если объект = синглетон:
                                             *  проверяется - создано ли уже такое окно
                                             *  если да- открывается, иначе создается новый компонент
                                             *
                                             *  у синглетона присутствует атрибут id. по нему делается проверка.
                                             *
                                             *TODO: Перенести в конструктор, где он и должен быть. проблема - инициализация.
                                             **/
                                        
                                        if(type_exists){
                                            if(n.attributes.singleton){
                                                if(EBS.windowCmp.items.containsKey(type)){
                                                    EBS.windowCmp.activate(type);
                                                }else{
                                                    cmp = Ext.create({
                                                        xtype:type,
                                                        id:type,
                                                        singleton:true
                                                        });
                                                    
                                                    
                                                    EBS.windowCmp.add(cmp);
                                                    cmp.show()
                                                    
                                                    
                                                }
                                            }else{
                                                cmp = Ext.create({
                                                    xtype:type
                                                    });
                                                EBS.windowCmp.add(cmp);
                                                cmp.show()
                                            }

                                        }

                                    }
                                    
                        }
        }
    });



    EBS.base = function(){
        Ext.QuickTips.init();
        Ext.state.Manager.setProvider(new  Ext.state.CookieProvider());

        Ext.Direct.on('message', function(e){
            if(console && console.log)
                console.log(String.format('<p><i>{0}</i></p>', e.data));
        });


        return {
            window: {},
            init: function(){
                        // initialize datastore
                        //EBS.store.accounts.load()
                        //EOF initialize datastore

                        //tabScrollerMenu =

                       //EBS.viewport =
                        new Ext.Viewport({
                            layout:'border',
                            //   renderTo:Ext.getBody(),
                            items:[
                            //Header
                                {
                                    height  : 100,
                                    id      : 'header',
                                    baseCls : 'header-line',
                                    region  :'north',
                                    html    : '<div class="user_block f-right"><span class="sustem_user">' + EBS.store.logged_user.username + '</span> <span class="exit"><a href="/helpdesk/logout/">'+i18n.logout+'</a></span></div>',
                                    border  :false,
                                    margins : '0 0 5 0'
                                },

                            // tab panel
                                {
                                    xtype   : 'panel',
                                    id      : 'center_panel',
                                    region  : 'center',
                                    height  : 200,
                                    width   : 400,
                                    layout  : 'fit',
                                    //title  : 'Exercising scrollable tabs with a tabscroller menu',
                                    items   : {
                                        xtype           : 'tabpanel',
                                        activeTab       : 0,
                                        id              : 'main_tab_panel',
                                        stateful: true,
                                        stateId: 'main_tab_panel',
                                        enableTabScroll : true,
                                        resizeTabs      : true,
                                        //minTabWidth     : 75,
                                        border          : false,
                                        defaults		: {               // defaults are applied to items, not the container
                                            				closable:true,
                                            				autoScroll:true,
                                        				},
                                        plugins         : [ new Ext.ux.TabScrollerMenu({
                                                                                        maxText  : 15,
                                                                                        pageSize : 5
                                                                                        })
                                                         ],
                                        /*items           : [
                                            {
                                                title : 'Welcome',
                                                html  : i18n.welcomeText
                                            },
                                            
                                            {
                                                xtype:'ebs_nasPanel',
                                                id:'ebs_nasPanel'

                                            }
                                        ]*/
                                    }
                                },
                            // Right help block
                                {
                                    id:'help_menu',
                                    region: 'east',
                                    title: 'Title for Panel',
                                    collapsible: true,
                                    html: i18n.helpMenuInnerText,
                                    split: true,
                                    width: 100,
                                    minWidth: 100

                                },
                            // Main menu block
                                {
                                    id      :'main_menu',
                                    xtype   : 'panel',
                                    region  : 'west',
                                    title   : 'Title for Panel',
                                    //layout  : 'accordion',
                                    collapsible: false,
                                    split   : true,
                                    //width   : 180,
                                    minWidth: 180,
                                    items: [treePanel]
                                    /*items : [{
                                                title: 'Users',
                                                xtype: 'panel',
                                                //scale: 'large',
                                                iconAlign: 'top',
                                                cls: 'x-btn-as-arrow',
                                                items : [{
                                                  title: '123',
                                                  handler : function(){
                                                      cmp = new EBS.conponents.usersGrid();
                                                      Ext.getCmp('main_tab_panel').add(cmp);
                                                  }
                                                }]
                                                  
                                              }
                                    ]*/

                                }
                            ]
                        }); //new Ext.Viewport
                        EBS.windowCmp = Ext.getCmp('main_tab_panel');
            }
        }
    }();


   /*
    window frame template = {
        menu_block = EBS.const.USER
        menu_name = EBS.locale.users_accounts;
        menu_order
        title
        description
        help_menu = {} //west_block /// need to extend
        menu
        panel
        }
   */





    




/* BASE Components*/
    EBS.base.GridPanel = Ext.extend(Ext.grid.GridPanel, {
        constructor: function(config) {

               Ext.apply(this, {
            	   plugins: [new Ext.ux.grid.Search({
                     				iconCls:'icon-zoom'
                     				,readonlyIndexes:['note']
                     				,disableIndexes:['pctChange']
                     				,minChars:2
                     				,autoFocus:true
                     				,mode:'local'
                     				,position:'top'
                     				,width:200
              //       			,menuStyle:'radio'
                     			})],
                    bbar: new Ext.PagingToolbar({
                           pageSize: 100,
                          // store: this.store,
                           displayInfo: true,
                           dispalyMsg: i18n.paginatorDispalyMsg,
                           emptyMsg: i18n.paginatorEmptyMsg
                           //plugins: [new Ext.ux.SlidingPager(), this.filters],
                        }),
                    selModel : new Ext.grid.RowSelectionModel({
                         singleSelect : true
                            })
                
                });
             EBS.base.GridPanel.superclass.constructor.call(this, config)
        },
        initComponent: function(arguments) {
            EBS.base.GridPanel.superclass.initComponent.apply(this, arguments);
        }



    });
    Ext.reg("ebs_base_grid", EBS.base.GridPanel);

    
    EBS.AccountsPanel = Ext.extend(Ext.TabPanel, {
        initComponent:function() {
           var config = {
						title:'Аккаунты',
						id:'accountspanel',
						activeTab       : 1,
						align:'center',
						items:[{						    	   
						    	    title:'Поиск',
								    xtype: 'form',
								    autoHeight: true,
								    autoScroll: true,
								    width: 320,
								    //width: 907,
								    activeItem: 0,
								    layout: 'accordion',
								    bodyStyle: 'padding:20px 150px 20px 150px',
								    buttonAlign: 'center',
								    //bodyStyle: "padding: 15px;"
								    //align:'center',
								    items: [
								            
								        {
								            xtype: 'fieldset',
								            autoHeight: true,
								            autoWidth: true,
								            //width: 600,
								            title: 'Учётные данные',
								            labelPad: 10,
								            //labelWidth: 200,
								            items: [
								                    {
								                    	xtype:'hidden',
								                    	name:'action',
								                    	value:'search',
								                    },
									                {
									                    xtype: 'xaccountslivesearchcombo',
									                    name: 'contract',
									                    field:'contract',
									                    valueField:'contract',
									                    displayField:'contract',
									                    anchor: '100%',
									                    fieldLabel: 'Договор',
									                    blankText: 'Укажите договор или его часть'
									                },
								                {
								                    xtype: 'xaccountslivesearchcombo',
								                    name: 'username',
								                    field:'username',
								                    valueField:'username',
								                    displayField:'username',
								                    anchor: '100%',
								                    fieldLabel: 'Имя пользователя',
								                    blankText: 'Укажите имя пользователя или его часть'
								                  
								                },
								                {
								                    xtype: 'xaccountslivesearchcombo',
								                    name: 'fullname',
								                    field:'fullname',
								                    displayField:'fullname',
								                    valueField:'fullname',
								                    hiddenField:'fullname',
								                    anchor: '100%',
								                    fieldLabel: 'ФИО',
								                    blankText: 'Укажите ФИО или его часть'
								                },
								                {
								                    xtype: 'textfield',
								                    name: 'contactperson',
								                    anchor: '100%',
								                    fieldLabel: 'Контактное лицо'
								                },
								                {
								                    xtype: 'xcombocity',
								                    name: 'city',
								                    hiddenName: 'city',
								                    anchor: '100%',
								                    fieldLabel: 'Город',
								                    listeners:{
                                                    	select: function(combo, record, index) {
                                                    		
                                                    		this.findParentByType('form').getForm().findField('street').clearValue();
															this.findParentByType('form').getForm().findField('street').store.load({params:{city_id: this.value}});
                                                    		
                                                          },
                                                   },
								                },
								                {
								                    xtype: 'xcombostreet',
								                    name: 'street',
								                    anchor: '100%',
								                    hiddenName: 'street',
								                    fieldLabel: 'Улица',
								                    listeners:{
                                                    	select: function(combo, record, index) {
                                                    		
                                                    		this.findParentByType('form').getForm().findField("house").clearValue();
															this.findParentByType('form').getForm().findField("house").store.load({params:{street_id: this.value}});                                                                              },
                                                   

                                                    },
								                    	
								                },
								                {
								                    xtype: 'xcombohouse',
								                    name: 'house',
								                    anchor: '100%',
								                    hiddenName: 'house',
								                    fieldLabel: 'Дом',
								                    
								                },
								                {
								                    xtype: 'textfield',
								                    name: 'house_bulk',
								                    anchor: '100%',
								                    fieldLabel: 'Подъезд'
								                },
								                {
								                    xtype: 'textfield',
								                    name: 'room',
								                    fieldLabel: 'Квартира'
								                },
								                {
						                            xtype: 'combo',
						                            name: 'status',
						                            fieldLabel: 'Статус',
						                            width:300,
						                            local:true,
						                            displayField:'status',
						                            hiddenName:'status',
						                            valueField:'id',
						                            typeAhead: true,
						                            mode: 'local',
						                            forceSelection: true,
						                            triggerAction: 'all',
						                            editable:false,
						                            store:  new Ext.data.ArrayStore({
						                                fields: ['id','status'],
						                                data : [['',''],
						                                        ['1','Активен'], 
						                                        ['2','Не активен, списывать периодические услуги'],
						                                        ['3','Не активен, не списывать периодические услуги'],
						                                        ['4','Пользовательская блокировка'],] 
						                            })
						                        },
								            ]
								        },
								        {
								            xtype: 'fieldset',
								            autoHeight: true,
								            autoWidth:true,
								            //width: 600,
								            title: 'Тарификация',
								            items: [
								                {
								                    xtype: 'compositefield',
								                    anchor: '100%',
								                    fieldLabel: 'Баланс',
								                    items: [
								                        {
								                            xtype: 'combo',
								                            name: 'ballance_exp',
								                            local:true,
								                            displayField:'exp',
								                            typeAhead: true,
								                            mode: 'local',
								                            forceSelection: true,
								                            triggerAction: 'all',
								                            editable:false,
								                            store:  new Ext.data.ArrayStore({
								                                fields: ['exp'],
								                                data : [[''],['<'],['<='],['='],['>='],['>']] 
								                            })
								                        },
								                        {
								                            xtype: 'textfield',
								                            name: 'ballance',
								                            
								                        }
								                    ]
								                },
								                {
								                    xtype: 'compositefield',
								                    anchor: '100%',
								                    fieldLabel: 'Кредит',
								                    items: [
								                        {
								                            xtype: 'combo',
								                            name: 'credit_exp',
								                            local:true,
								                            displayField:'exp',
								                            typeAhead: true,
								                            mode: 'local',
								                            forceSelection: true,
								                            triggerAction: 'all',
								                            editable:false,
								                            store:  new Ext.data.ArrayStore({
								                                fields: ['exp'],
								                                data : [[''],['<'],['<='],['='],['>='],['>']] 
								                            })
								                        },
								                        {
								                            xtype: 'textfield',
								                            name: 'credit',
								                            fieldLabel: 'Label'
								                        }
								                    ]
								                },
								                {
								                	xtype: 'multiselect',
								                    name:'tariff_filter',
								                    id:'tariff_filter',
								                    valueField:'tariff',
								                    displayField:'name',
								                    width:400,
								                    //autoWidth:true,
								                    autoHeight: true,
								                    maxHeight:200,
								                    border:true,
								                    store: new Ext.data.JsonStore({
								                        paramsAsHash: true,
								                        autoLoad: {},
								                        proxy: new Ext.data.HttpProxy({
								                            url: '/ebsadmin/tariffs/',
								                            method:'GET',
								                        }),    
								                        fields: ['tariff', 'name'],
								                        root: 'records',
								                        remoteSort:false,
								                        
								                      }
								                    ),
								                    fieldLabel: 'Тарифные планы',
								                   
								                },
								                {
								                    xtype: 'multiselect',
								                    multiSelect: true,
								                    columnResize: false,
								                    autoWidth:true,
								                    name:'group_filter',
								                    fieldLabel: 'Группа',
								                    
								                },
								               
								                {
								                    xtype: 'checkbox',
								                    boxLabel: 'BoxLabel',
								                    name:'ballance_blocked',
								                    anchor: '100%',
								                    fieldLabel: 'Блокировка по балансу'
								                },
								                {
								                    xtype: 'checkbox',
								                    boxLabel: 'BoxLabel',
								                    name:'limit_blocked',
								                    anchor: '100%',
								                    fieldLabel: 'Блокировка по лимитам'
								                }
								            ]
								        },
								        {
								            xtype: 'fieldset',
								            autoHeight: true,
								            autoWidth:true,
								            //width: 600,
								            title: 'Другое',
								            items: [
								                {
								                    xtype: 'multiselect',
								                    name:'nas_filter',
								                    id:'nas_filter',
								                    valueField:'nas',
								                    displayField:'name',
								                    fieldLabel: 'Сервер доступа',
								                    width:300,
								                    //autoWidth:true,
								                    autoHeight: true,
								                    maxHeight:200,
								                    border:true,
								                    store: new Ext.data.JsonStore({
								                        paramsAsHash: true,
								                        autoLoad: {},
								                        proxy: new Ext.data.HttpProxy({
								                            url: '/ebsadmin/nasses/',
								                            method:'GET',
								                        }),    
								                        fields: ['nas', 'name'],
								                        root: 'records',
								                        remoteSort:false,
								                        
								                      }
								                    ),
								                   
								                },
								                {
								                    xtype: 'checkboxgroup',
								                    anchor: '100%',
								                    fieldLabel: 'IPN статусы',
								                    items: [
								                        {
								                            xtype: 'checkbox',
								                            name: 'ipn_added',
								                            boxLabel: 'Добавлен'
								                        },
								                        {
								                            xtype: 'checkbox',
								                            name: 'ipn_enabled',
								                            boxLabel: 'Активен'
								                        },
								                        {
								                            xtype: 'checkbox',
								                            name: 'ipn_sleep',
								                            boxLabel: 'Не менять статус'
								                        }
								                    ]
								                },
								                {
								                	xtype: 'multiselect',
								                    name:'systemuser_filter',
								                    id:'systemuser_filter',
								                    valueField:'id',
								                    displayField:'name',
								                    width:400,
								                    //autoWidth:true,
								                    autoHeight: true,
								                    maxHeight:200,
								                    border:true,
								                    store: new Ext.data.JsonStore({
								                        paramsAsHash: true,
								                        autoLoad: {},
								                        proxy: new Ext.data.HttpProxy({
								                            url: '/ebsadmin/systemuser/',
								                            method:'GET',
								                        }),    
								                        fields: ['id', 'name'],
								                        root: 'records',
								                        remoteSort:false,
								                        
								                      }
								                    ),
								                    fieldLabel: 'Менеджер',
								                   
								                },
								                {
								                    xtype: 'compositefield',
								                    anchor: '100%',
								                    fieldLabel: 'Созданы',
								                    items: [
								                        {
								                            xtype: 'datefield',
								                            name: 'created_from',
								                            flex: 1,
								                            fieldLabel: 'Label'
								                        },
								                        {
								                            xtype: 'datefield',
								                            name: 'created_to',
								                            flex: 1,
								                            fieldLabel: 'Label'
								                        }
								                    ]
								                }
								            ]
								        
								        },
								       
								    ],
						       buttons:[{
									text:'Искать',
					        		handler:function(){
					        			var f;
					        			f=this.findParentByType('tabpanel').items.items[0].getForm();
					        			
					        			EBS.store.accounts.load({'params':f.getValues()})
					        		}
								},
								{
									text:'Добавить к результатам',
					        		handler:function(){
					        			var f;
					        			f=this.findParentByType('tabpanel').items.items[0].getForm();
					        			
					        			EBS.store.accounts.load({'params':f.getValues(),add:true})
					        		}
								},{
									text:'Очистить',
					        		handler:function(){
					        			var f;
					        			f=this.findParentByType('tabpanel').items.items[0].getForm();
					        			f.reset()
					        			//EBS.store.accounts.load({'params':f.getValues()})
					        		}
								}
								],
							},
					    	{
					      		xtype :'ebs_accountsPanel',
					    		id    :'ebs_accountsPanel',
					    		closable:false
					    	},
						
						]
						


        		}
           // apply config
           Ext.apply(this, Ext.apply(this.initialConfig, config));
    
           EBS.AccountsPanel.superclass.initComponent.apply(this, arguments);
       } // eo function initComponent
    
       ,onRender:function() {
           var me = this;
           
           EBS.AccountsPanel.superclass.onRender.apply(this, arguments);
       } // eo function onRender
     

   });
    Ext.reg('xaccountspanel', EBS.AccountsPanel);
    EBS.windows.keys[EBS.windows.keys.length] = 'xaccountspanel';

    EBS.AccountsLiveSearchCombo = Ext.extend(Ext.form.ComboBox, {
        initComponent:function() {
           var config = {
        		    anchor: '100%',
        		    displayField: 'username',
        		    valueField: 'id', 
        		    mode: 'remote',
        		    editable:true,
        		    triggerAction: 'all',
        		    typeAhead: false,
        		    minChars:2,
        		    blankText:'Укажите слово или часть слова для поиска',
        		    //field:'username',
        		    hideTrigger:true,
        		    pageSize:15,
        	        tpl: new Ext.XTemplate(
        	                '<tpl for="."><div class="search-item">',
        	                '<h3>Логин:{username}, ФИО: {fullname}, Договор: {contract}<br />Создан:<span>{created:date("M j, Y")}</span></h3>',
        	                '{excerpt}',
        	            '</div></tpl>'
        	        ),
        	        itemSelector: 'div.search-item',
        		    loadingText: 'Секундочку...',
        		    store:new Ext.data.Store({
        		    	autoLoad:true,
        		        proxy: new Ext.data.HttpProxy({
        		            url: '/ebsadmin/accounts/live/',
        		            method:'POST',
        		            
        		        }),
        		        
        		        reader: new Ext.data.JsonReader({
        		            root: 'records'
        		        }, [{
        		            name: 'id'
        		        }, {
        		            name: 'username'
        		        }, {
        		            name: 'created', type:'date',dateFormat: Date.patterns.ISO8601Long
        		        }, {
        		            name: 'fullname'
        		        }, {
        		            name: 'contract'
        		        } ])
        		    }),

        		}
           // apply config
           Ext.apply(this, Ext.applyIf(this.initialConfig, config));
           this.store.setBaseParam('field',this.field)
           EBS.AccountsLiveSearchCombo.superclass.initComponent.apply(this, arguments);
       } // eo function initComponent
    
       ,onRender:function() {
           var me = this;
           this.store.on('load',function(store) {
             //me.setValue('7', true);
             //me.store.setBaseParams({'field':this.field})
           })
           EBS.AccountsLiveSearchCombo.superclass.onRender.apply(this, arguments);
       } // eo function onRender
     

   });
    Ext.reg('xaccountslivesearchcombo', EBS.AccountsLiveSearchCombo);
    
    EBS.TrTypeCombo = Ext.extend(Ext.form.ComboBox, {
        initComponent:function() {
           var config = {
        		    anchor: '100%',
        		    fieldLabel: 'Тип платежа',
        		    displayField: 'name',
        		    valueField: 'id', 
        		    mode: 'remote',
        		    editable:false,
        		    triggerAction: 'all',
        		    typeAhead: true,
        		    store:new Ext.data.Store({
        		    	autoLoad:true,
        		        proxy: new Ext.data.HttpProxy({
        		            url: '/ebsadmin/transactiontypes/',
        		            method:'GET',
        		            
        		        }),
        		        
        		        reader: new Ext.data.JsonReader({
        		            root: 'records'
        		        }, [{
        		            name: 'id'
        		        }, {
        		            name: 'name'
        		        }])
        		    }),

        		}
           // apply config
           Ext.apply(this, Ext.apply(this.initialConfig, config));
    
           EBS.TrTypeCombo.superclass.initComponent.apply(this, arguments);
       } // eo function initComponent
    
       ,onRender:function() {
           var me = this;
           this.store.on('load',function(store) {
             me.setValue('7', true);
           })
           EBS.TrTypeCombo.superclass.onRender.apply(this, arguments);
       } // eo function onRender
     

   });
    Ext.reg('xtrtypecombo', EBS.TrTypeCombo);
    
    EBS.AddonServicesCombo = Ext.extend(Ext.form.ComboBox, {
        initComponent:function() {
           var config = {
        		    anchor: '100%',
        		    //fieldLabel: 'Тип платежа',
        		    displayField: 'name',
        		    valueField: 'id', 
        		    mode: 'remote',
        		    editable:false,
        		    triggerAction: 'all',
        		    typeAhead: true,
        		    tpl: new Ext.XTemplate(
        	                '<tpl for="."><div class="search-item">',
        	                '<h4>{name}, Цена: {cost}, <br /> <span style="font-size:10px;">Комментарий: {comment}</span></h4>',
        	                '{excerpt}',
        	            '</div></tpl>'
        	        ),
        	        itemSelector: 'div.search-item',
        		    store:new Ext.data.Store({
        		    	//autoLoad:true,
        		        proxy: new Ext.data.HttpProxy({
        		            url: '/ebsadmin/addonservices/',
        		            method:'GET',
        		            
        		        }),
        		        
        		        reader: new Ext.data.JsonReader({
        		            root: 'records'
        		        }, ['comment', 'burst_tx', 'wyte_period', 'cost', 'service_deactivation_action', 'max_tx', 'id', 'burst_rx', 'cancel_subscription', 'allow_activation', 'max_rx', 'wyte_cost', 'priority', 'nas', 'service_type', 'min_tx', 'timeperiod', 'change_speed', 'sp_period', 'min_rx', 'service_activation_action', 'change_speed_type', 'sp_type', 'deactivate_service_for_blocked_account', 'burst_treshold_rx', 'burst_time_rx', 'burst_time_tx', 'name', 'action', 'speed_units', 'burst_treshold_tx'])
        		    }),

        		}
           // apply config
           Ext.apply(this, Ext.apply(this.initialConfig, config));
    
           EBS.TrTypeCombo.superclass.initComponent.apply(this, arguments);
       } // eo function initComponent
    
       ,onRender:function() {
           var me = this;
           this.store.on('load',function(store) {
             //me.setValue('7', true);
           });
           me.store.load();
           EBS.AddonServicesCombo.superclass.onRender.apply(this, arguments);
       } // eo function onRender
     

   });
    Ext.reg('xaddonservicescombo', EBS.AddonServicesCombo);
    
    EBS.SubAccountsGrid = Ext.extend(Ext.grid.GridPanel, {
        initComponent:function() {
           var config = {
            	   xtype:'grid',
                   stateful: true,
                   collapsible: true,
                   stateId: 'stateSubaccountsGrid_',
                   plugins:['msgbus'],
                   //unstyled:true,
            	   store:new Ext.data.JsonStore({
       		        	paramsAsHash: true,
    			    //	autoLoad: {params:{start:0, limit:100}},
       		        	proxy: new Ext.data.HttpProxy({
       		        		url: '/ebsadmin/subaccounts/',
       		        		method:'POST',
       		        	}),    
       		        	fields: ['switch_port', 'ipn_speed', 'allow_dhcp', 'vpn_ip_address', 'allow_dhcp_with_block', 'ipn_sleep', 'speed', 'id', 'allow_addonservice', 'ipn_mac_address', 'allow_dhcp_with_minus', 'ipn_enabled', 'ipv4_vpn_pool', 'nas', 'ipv4_ipn_pool', 'allow_ipn_with_null', 'allow_ipn_with_minus', 'username', 'allow_dhcp_with_null', 'associate_pptp_ipn_ip', 'ipn_ip_address', 'associate_pppoe_ipn_mac', 'allow_ipn_with_block', 'vlan', 'allow_mac_update', 'allow_vpn_with_null', 'ipn_ipv6_ip_address', 'vpn_speed', 'allow_vpn_with_minus', 'password', 'ipn_added', 'account', 'switch', 'allow_vpn_with_block', 'need_resync', 'vpn_ipv6_ip_address'],
       		        	root: 'records',
       		        	remoteSort:false,
       		        	sortInfo:{
       		        		field:'username',
       		        		direction:'ASC'
       		        	},

            	   }),
            	   onChange:function(subject, message) {
            		   //Ext.Msg.alert(message);
            		   var me;
            		   me=this;
            		   account_id=this.findParentByType('xinstancecontainer').ids.id;
            		   
			        	  if (account_id){
			        		  //alert(account_id)
			        		  this.store.setBaseParam('account_id',account_id);
			        		  this.store.load();
			        	  }
            	       //Ext.Msg.alert(message);
            	    },
            	   bbar: new Ext.PagingToolbar({
                       pageSize: 100,
                      // store: this.store,
                       displayInfo: true,
                       dispalyMsg: i18n.paginatorDispalyMsg,
                       emptyMsg: i18n.paginatorEmptyMsg
                       //plugins: [new Ext.ux.SlidingPager(), this.filters],
                    }),
                selModel : new Ext.grid.RowSelectionModel({
                     singleSelect : true
                        }),
            	   //autoHeight: true,
            	   //autoWidth: true,
            	   listeners: {
 			          render:function(){
 			             // console.info('load',this,arguments);
 			        	  var account_id;
 			        	  //account_id=this.findParentByType('form').getForm().findField('id').value;
 			        	  account_id=this.findParentByType('xinstancecontainer').ids.id;
 			        	  
 			        	  
 			        	  if (account_id){
 			        		  //alert(account_id)
 			        		  this.store.setBaseParam('account_id',account_id);
 			        		  this.store.load();
 			        	  }
 			        	 var me;
 	            		   me=this;
 			        	 me.subscribe('ebs.subaccounts.change', {fn:this.onChange, single:false});
 			          },
 			          
 			         /*beforedestroy:function(){
 			             // console.info('load',this,arguments);
			        	  
			        	 this.unsubscribe('ebs.subaccounts.change');
			          },*/
            	   },
                   
            	   autoScroll: true,
            	   columns:[
            	            {
            	            	header:'id',
            	            	dataIndex:'id',
            	            	sortable:true
            	            },
            	            {
            	            	header:'Username',
            	            	dataIndex:'username',
            	            	sortable:true
            	            },
            	            {
            	            	header:'Сервер доступа',
            	            	dataIndex:'nas',
            	            	sortable:true
            	            },
            	            {
            	            	header:'IPv4 VPN',
            	            	dataIndex:'vpn_ip_address',
            	            	sortable:true
            	            },
            	            {
            	            	header:'IPv4 IPN',
            	            	dataIndex:'ipn_ip_address',
            	            	sortable:true
            	            },
            	            {
            	            	header:'MAC',
            	            	dataIndex:'ipn_mac_address',
            	            	sortable:true
            	            },
            	            {
            	            	header:'Коммутатор',
            	            	dataIndex:'switch',
            	            	sortable:true
            	            },
            	            {
            	            	header:'Порт коммутатора',
            	            	dataIndex:'switch_port',
            	            	sortable:true
            	            },
            	            {
            	            	header:'Custom VPN speed',
            	            	dataIndex:'vpn_speed',
            	            	sortable:true
            	            },
            	            {
            	            	header:'Custom IPN speed',
            	            	dataIndex:'ipn_speed',
            	            	sortable:true
            	            },
            	            {
            	                xtype: 'actioncolumn',
            	                header:'Отключить изменение IPN статуса',
            	                dataIndex:'ipn_sleep',
            	                width: 50,
            	                items: [{
            	                    //icon   : '/media/icons/16/delete.gif',  // Use a URL in the icon config
            	                    //tooltip: 'Была выполнена команда добавления ACL записи на сервере доступа',
            	                    handler: function(grid, rowIndex, colIndex) {
            	                    	var rec = grid.store.getAt(rowIndex);
            	                        //alert("Sell "+rec.get('ipn_added'));
            	                    	var act;
            	                    	if (rec.get('ipn_sleep')==true){
            	                    		act='ipn_disable';
            	                    	}else{
            	                    		act='ipn_enable';
            	                    	}
            	                        Ext.Ajax.request({
            	                            params: {subaccounts_id: [rec.get('id'),], state: rec.get('ipn_sleep'),action:act},
            	                            url: '/ebsadmin/actions/set/',
            	                            success: function (resp) {
            	                                var data;
            	                                data = Ext.decode(resp.responseText);
            	                                if (data.success === true) {
            	                                    
            	                                    if (rec.get('ipn_sleep')==true){
            	                                    	rec.set('ipn_sleep',false);
                        	                    	}else{
                        	                    		rec.set('ipn_sleep',true);
                        	                    	}
            	                                    
            	                                } else {
            	                                    Ext.MessageBox.alert('Ошибка', 'Состояние не изменено. '+data.msg);
            	                                }
            	                            },
            	                            failure: function () {
            	                            	Ext.MessageBox.alert('Ошибка', 'Состояние не изменено');
            	                            }
            	                        });
            	                    },
            	                
            	                    getClass: function(v, meta, rec) {          // Or return a class from a function
            	                        if (rec.get('ipn_sleep') ==true) {
            	                            this.items[0].tooltip = 'IPN действия не будут выполняться. Кликните, чтобы изменить.';
            	                            return 'disable-col';
            	                            
            	                        } else {
            	                            this.items[0].tooltip = 'IPN действия будут выполняться. Кликните, чтобы изменить.';
            	                            return 'enable-col';
            	                        }
            	                    }
            	                }]
            	            },
            	            {
            	                xtype: 'actioncolumn',
            	                header:'Добавлен в ACL',
            	                dataIndex:'ipn_added',
            	                width: 50,
            	                items: [{
            	                    //icon   : '/media/icons/16/delete.gif',  // Use a URL in the icon config
            	                    tooltip: 'Была выполнена команда добавления ACL записи на сервере доступа',
            	                    handler: function(grid, rowIndex, colIndex) {
            	                    	var rec = grid.store.getAt(rowIndex);
            	                        //alert("Sell "+rec.get('ipn_added'));
            	                    	var act;
            	                    	if (rec.get('ipn_added')==true){
            	                    		act='delete';
            	                    	}else{
            	                    		act='create';
            	                    	}
            	                        Ext.Ajax.request({
            	                            params: {subaccounts_id: [rec.get('id'),], state: rec.get('ipn_added'),action:act},
            	                            url: '/ebsadmin/actions/set/',
            	                            success: function (resp) {
            	                                var data;
            	                                data = Ext.decode(resp.responseText);
            	                                if (data.success === true) {
            	                                    
            	                                    if (rec.get('ipn_added')==true){
            	                                    	rec.set('ipn_added',false);
                        	                    	}else{
                        	                    		rec.set('ipn_added',true);
                        	                    	}
            	                                    
            	                                } else {
            	                                    Ext.MessageBox.alert('Ошибка', 'Состояние не изменено. '+data.msg);
            	                                }
            	                            },
            	                            failure: function () {
            	                            	Ext.MessageBox.alert('Ошибка', 'Состояние не изменено');
            	                            }
            	                        });
            	                    },
            	                
            	                    getClass: function(v, meta, rec) {          // Or return a class from a function
            	                        if (rec.get('ipn_added') ==true) {
            	                            this.items[0].tooltip = 'Активно! Кликните, чтобы отключить.';
            	                            return 'disable-col';
            	                            
            	                        } else {
            	                            this.items[0].tooltip = 'Не активно! Кликните, чтобы включить.';
            	                            return 'enable-col';
            	                        }
            	                    }
            	                }]
            	            },{
            	                xtype: 'actioncolumn',
            	                header:'Активен в ACL',
            	                dataIndex:'ipn_enabled',
            	                width: 50,
            	                items: [{
            	                    //icon   : '/media/icons/16/delete.gif',  // Use a URL in the icon config
            	                    tooltip: 'Была выполнена команда активации ACL записи на сервере доступа',
            	                    handler: function(grid, rowIndex, colIndex) {
            	                    	var rec = grid.store.getAt(rowIndex);
            	                        //alert("Sell "+rec.get('ipn_added'));
            	                    	var act;
            	                    	if (rec.get('ipn_enabled')==true){
            	                    		act='disable';
            	                    	}else{
            	                    		act='enable';
            	                    	}
            	                        Ext.Ajax.request({
            	                            params: {subaccounts_id: [rec.get('id'),], state: rec.get('ipn_enabled'),action:act},
            	                            url: '/ebsadmin/actions/set/',
            	                            success: function (resp) {
            	                                var data;
            	                                data = Ext.decode(resp.responseText);
            	                                if (data.success === true) {
            	                                    
            	                                    if (rec.get('ipn_enabled')==true){
            	                                    	rec.set('ipn_enabled',false);
                        	                    	}else{
                        	                    		rec.set('ipn_enabled',true);
                        	                    	}
            	                                    
            	                                } else {
            	                                    Ext.MessageBox.alert('Ошибка', 'Состояние не изменено. '+data.msg);
            	                                }
            	                            },
            	                            failure: function () {
            	                            	Ext.MessageBox.alert('Ошибка', 'Состояние не изменено');
            	                            }
            	                        });
            	                    },
            	                
            	                    getClass: function(v, meta, rec) {          // Or return a class from a function
            	                        if (rec.get('ipn_enabled') ==true) {
            	                            this.items[0].tooltip = 'Активно! Кликните, чтобы отключить.';
            	                            return 'disable-col';
            	                        } else {
            	                            this.items[0].tooltip = 'Не активно! Кликните, чтобы включить.';
            	                            
            	                            return 'enable-col';
            	                        }
            	                    }
            	                }]
            	            }                                                  	            
            	            ]
            		   
            		  
               }

        		
           // apply config
           Ext.apply(this, Ext.applyIf(this.initialConfig, config));
    
           EBS.SubAccountsGrid.superclass.initComponent.apply(this, arguments);
       } // eo function initComponent
    


   });

   Ext.reg('xsubaccountsgrid', EBS.SubAccountsGrid);
   
   EBS.AccountAddonServiceGrid = Ext.extend(Ext.grid.GridPanel, {
       initComponent:function() {
          var config = {
           	   xtype:'grid',
                  stateful: true,
                  stateId: 'stateAccountAddonServiceGrid_',
                  collapsible: true,
                  //unstyled:true,
           	   	  store:new Ext.data.JsonStore({
      		        	paramsAsHash: true,

      		        	//autoLoad: {params:{start:0, limit:100,'account_id': this.findParentByType('xinstancecontainer').instance_id}},
      		        	proxy: new Ext.data.HttpProxy({
      		        		url: '/ebsadmin/accountaddonservices/',
      		        		method:'POST',
      		        	}),    
      		        	fields: [{name: 'service', type:'string'},
      		        		{name: 'account', type:'int'},
      		        		{name: 'id', type:'int'},
      		        		{name: 'subaccount', type:'int'},
      		        		{name: 'activated', type: 'date', dateFormat: Date.patterns.ISO8601Long},
      		        		{name: 'deactivated',  type: 'date', dateFormat: Date.patterns.ISO8601Long},
      		        		{name: 'action_status', type:'boolean'},
      		        		{name: 'speed_status', type:'boolean'},
      		        		{name: 'temporary_blocked', type: 'date', dateFormat: Date.patterns.ISO8601Long},
      		        		{name: 'last_checkout', type: 'date', dateFormat: Date.patterns.ISO8601Long},],
      		        	root: 'records',
      		        	remoteSort:false,
      		        	sortInfo:{
      		        		field:'activated',
      		        		direction:'DESC'
      		        	},



           	   }),
           	   plugins:['msgbus'],	
           	
	     	   onChange:function(subject, message) {
	     		   //Ext.Msg.alert(message);
	     		   var me;
	     		   me=this;
	     	       me.store.load();
	     	       
	     	    },
               selModel : new Ext.grid.RowSelectionModel({
                    singleSelect : true
                       }),
           	   //autoHeight: true,
           	   //autoWidth: true,
           	   listeners: {
			          render:function(){
			             // console.info('load',this,arguments);
			        	  //alert(this.findParentByType('form').findParentByType('panel').instance_id);
			        	  this.store.setBaseParam('account_id', this.findParentByType('xinstancecontainer').instance_id);
			        	  if (this.findParentByType('xinstancecontainer').instance_id){
			        		  this.store.load();
			        	  }
			        	  var me;
	            		  me=this;
			        	  me.subscribe('ebs.accountaddonservice.change', {fn:this.onChange, single:false});
			          }
           	   },
                  
           	   autoScroll: true,
           	   columns:[
           	            {
           	            	header:'id',
           	            	dataIndex:'id',
           	            	sortable:true
           	            },
           	            {
           	            	header:'Услуга',
           	            	dataIndex:'service',
           	            	sortable:true
           	            },
           	            {
           	            	header:'Активирована',
           	            	dataIndex:'activated',
           	            	sortable:true,
           	            	renderer:Ext.util.Format.dateRenderer(Date.patterns.ISO8601Long),
           	            	
           	            },
           	            {
           	            	header:'Отключена',
           	            	dataIndex:'deactivated',
           	            	sortable:true,
           	            	renderer:Ext.util.Format.dateRenderer(Date.patterns.ISO8601Long),
           	            },
           	            {
           	            	header:'Последнее списание',
           	            	dataIndex:'last_checkout',
           	            	sortable:true,
           	            	renderer:Ext.util.Format.dateRenderer(Date.patterns.ISO8601Long),
           	            },
           	            {
           	            	header:'Команда активации выполнена',
           	            	dataIndex:'action_status',
           	            	sortable:true
           	            },
           	            {
           	            	header:'Команда установки скорости выполнена',
           	            	dataIndex:'speed_status',
           	            	sortable:true
           	            },
           	            ]
           		   
           		  
              }

       		
          // apply config
          Ext.apply(this, Ext.applyIf(this.initialConfig, config));
   
          EBS.AccountAddonServiceGrid.superclass.initComponent.apply(this, arguments);
      } // eo function initComponent
   


  });

  

  
   EBS.SuspendedPeriodGrid = Ext.extend(Ext.grid.GridPanel, {
	      initComponent:function() {
	         var config = {
	          	   xtype:'grid',
	                 stateful: true,
	                 stateId: 'stateSuspendedPeriodGrid',
	                 collapsible: true,
	                 //unstyled:true,
	          	   	  store:new Ext.data.JsonStore({
	     		        	paramsAsHash: true,

	     		        	//autoLoad: {params:{start:0, limit:100,'account_id': this.findParentByType('xinstancecontainer').instance_id}},
	     		        	proxy: new Ext.data.HttpProxy({
	     		        		url: '/ebsadmin/suspendedperiod/',
	     		        		method:'POST',
	     		        	}),    
	     		        	fields: [{name: 'id', type:'int'},
	     		        		
	     		        		{name: 'activated_by_account', type:'bool'},
	     		        		
	     		        		{name: 'start_date', type: 'date', dateFormat: Date.patterns.ISO8601Long},
	     		        		{name: 'end_date',  type: 'date', dateFormat: Date.patterns.ISO8601Long},
	     		        		],
	     		        	root: 'records',
	     		        	remoteSort:false,
	     		        	sortInfo:{
	     		        		field:'start_date',
	     		        		direction:'DESC'
	     		        	},



	          	   }),
	          	 plugins:['msgbus'],	
	           	
		     	   onChange:function(subject, message) {
		     		   //Ext.Msg.alert(message);
		     		   var me;
		     		   me=this;
		     		   this.store.setBaseParam('account_id', this.findParentByType('xinstancecontainer').ids.id);
		     	       me.store.load();
		     	       
		     	    },
	          	   tbar: [{
	 			    icon: media+'icons/16/arrow_refresh.png',
	 		        text: 'Обновить',
	 		        handler: function(){
	 		        	this.ownerCt.ownerCt.store.load();
	 		        }
	 		       },{
				        iconCls: 'icon-user-add',
				        text: 'Новый',
				        handler: function(){
				     	   var account_id;
				     	   account_id = this.findParentByType('xinstancecontainer').ids.id;
				     	   EBS.displayForm('ebs_accountsPanel', 'suspendedperiod',{'account_id':account_id,id:null}, this.findParentByType('grid'))
				     	   
				        }
				    },{
				        iconCls: 'icon-user-edit',
				        text: 'Редактировать',
				        handler: function(){
				     	   var id;
				     	   var account_id;
				     	   account_id = this.findParentByType('xinstancecontainer').ids.id;
				     	   id = this.findParentByType('grid').selModel.selections.items[0].id;
				     	   EBS.displayForm('ebs_accountsPanel', 'suspendedperiod',{'account_id':account_id,id:id}, this.findParentByType('grid'))
				        }
				    },{
				        //ref: '../removeBtn',
				        iconCls: 'icon-delete',
				        text: 'Remove',
				        //disabled: true,
				        ref: '../removeButton',
				        handler: function(){
				     	   
				        }
				    }],
	          	
		     	  
	              selModel : new Ext.grid.RowSelectionModel({
	                   singleSelect : true
	                      }),
	          	   //autoHeight: true,
	          	   //autoWidth: true,
	          	   listeners: {
				          render:function(){
				             // console.info('load',this,arguments);
				        	  //alert(this.findParentByType('form').findParentByType('panel').instance_id);
				        	  this.store.setBaseParam('account_id', this.findParentByType('xinstancecontainer').ids.id);
				        	  if (this.findParentByType('xinstancecontainer').ids.id){
				        		  this.store.load();
				        	  }
				        	  var me;
		            		  me=this;
				        	  me.subscribe('ebs.suspendedperiod.change', {fn:this.onChange, single:false});
				          }
	          	   },
	                 
	          	   autoScroll: true,
	          	   columns:[
	          	            {
	          	            	header:'id',
	          	            	dataIndex:'id',
	          	            	sortable:true
	          	            },
	          	            {
	          	            	header:'Начало',
	          	            	dataIndex:'start_date',
	          	            	renderer:Ext.util.Format.dateRenderer(Date.patterns.ISO8601Long),
	          	            	sortable:true
	          	            },
	          	            {
	          	            	header:'Конец',
	          	            	dataIndex:'end_date',
	          	            	renderer:Ext.util.Format.dateRenderer(Date.patterns.ISO8601Long),
	          	            	sortable:true
	          	            },
	          	            {
	          	            	header:'Включено пользователем',
	          	            	dataIndex:'activated_by_account',
	          	            	sortable:true,
	          	            },
	          	            
	          	            ]
	          		   
	          		  
	             }

	      		
	         // apply config
	         Ext.apply(this, Ext.applyIf(this.initialConfig, config));
	  
	         EBS.SuspendedPeriodGrid.superclass.initComponent.apply(this, arguments);
	     } // eo function initComponent
	  


	 });

	 Ext.reg('xsuspendedperiodgrid', EBS.SuspendedPeriodGrid);


 
  EBS.DocumentsGrid = Ext.extend(Ext.grid.GridPanel, {
      initComponent:function() {
         var config = {
          	   xtype:'grid',
                 stateful: true,
                 stateId: 'stateDocumentsGrid',
                 collapsible: true,
                 //unstyled:true,
          	   	  store:new Ext.data.JsonStore({
     		        	paramsAsHash: true,

     		        	//autoLoad: {params:{start:0, limit:100,'account_id': this.findParentByType('xinstancecontainer').instance_id}},
     		        	proxy: new Ext.data.HttpProxy({
     		        		url: '/ebsadmin/document/',
     		        		method:'POST',
     		        	}),    
     		        	fields: [{name: 'id', type:'int'},
     		        		{name: 'contractnumber', type:'string'},
     		        		{name: 'type', type:'string'},
     		        		
     		        		{name: 'date_start', type: 'date', dateFormat: Date.patterns.ISO8601Long},
     		        		{name: 'date_end',  type: 'date', dateFormat: Date.patterns.ISO8601Long},
     		        		],
     		        	root: 'records',
     		        	remoteSort:false,
     		        	sortInfo:{
     		        		field:'date_start',
     		        		direction:'DESC'
     		        	},



          	   }),
          	 plugins:['msgbus'],	
           	
	     	   onChange:function(subject, message) {
	     		   //Ext.Msg.alert(message);
	     		   var me;
	     		   me=this;
	     		   this.store.setBaseParam('account_id', this.findParentByType('xinstancecontainer').ids.id);
	     	       me.store.load();
	     	       
	     	    },
          	   tbar: [{
 			    icon: media+'icons/16/arrow_refresh.png',
 		        text: 'Обновить',
 		        handler: function(){
 		        	this.ownerCt.ownerCt.store.load();
 		        }
 		       },{
			        iconCls: 'icon-user-add',
			        text: 'Добавить',
			        handler: function(){
			     	   var account_id;
			     	   account_id = this.findParentByType('xinstancecontainer').ids.id;
			     	   EBS.displayForm('ebs_accountsPanel', 'document',{'account_id':account_id,id:null}, this.findParentByType('grid'))
			     	   
			        }
			    },{
			        iconCls: 'icon-user-edit',
			        text: 'Редактировать',
			        handler: function(){
			     	   var id;
			     	   var account_id;
			     	   account_id = this.findParentByType('xinstancecontainer').ids.id;
			     	   id = this.findParentByType('grid').selModel.selections.items[0].id;
			     	   EBS.displayForm('ebs_accountsPanel', 'document',{'account_id':account_id,id:id}, this.findParentByType('grid'))
			        }
			    },{
			        //ref: '../removeBtn',
			        iconCls: 'icon-delete',
			        text: 'Remove',
			        //disabled: true,
			        ref: '../removeButton',
			        handler: function(){
			     	   
			        }
			    }],
          	
	     	   onChange:function(subject, message) {
	     		   //Ext.Msg.alert(message);
	     		   var me;
	     		   me=this;
	     	       me.store.load();
	     	       
	     	    },
              selModel : new Ext.grid.RowSelectionModel({
                   singleSelect : true
                      }),
          	   //autoHeight: true,
          	   //autoWidth: true,
          	   listeners: {
			          render:function(){
			             // console.info('load',this,arguments);
			        	  //alert(this.findParentByType('form').findParentByType('panel').instance_id);
			        	  this.store.setBaseParam('account_id', this.findParentByType('xinstancecontainer').instance_id);
			        	  if (this.findParentByType('xinstancecontainer').instance_id){
			        		  this.store.load();
			        	  }
			        	  var me;
	            		  me=this;
			        	  me.subscribe('ebs.accountdocument.change', {fn:this.onChange, single:false});
			          }
          	   },
                 
          	   autoScroll: true,
          	   columns:[
          	            {
          	            	header:'id',
          	            	dataIndex:'id',
          	            	sortable:true
          	            },
          	            {
          	            	header:'Номер договора',
          	            	dataIndex:'contractnumber',
          	            	sortable:true
          	            },
          	            {
          	            	header:'Тип',
          	            	dataIndex:'type',
          	            	sortable:true
          	            },
          	            {
          	            	header:'С',
          	            	dataIndex:'date_start',
          	            	sortable:true,
          	            	renderer:Ext.util.Format.dateRenderer(Date.patterns.ISO8601Long),
          	            	
          	            },
          	            {
          	            	header:'По',
          	            	dataIndex:'date_end',
          	            	sortable:true,
          	            	renderer:Ext.util.Format.dateRenderer(Date.patterns.ISO8601Long),
          	            },
          	            
          	            ]
          		   
          		  
             }

      		
         // apply config
         Ext.apply(this, Ext.applyIf(this.initialConfig, config));
  
         EBS.DocumentsGrid.superclass.initComponent.apply(this, arguments);
     } // eo function initComponent
  


 });

 Ext.reg('xdocumentsgrid', EBS.DocumentsGrid);
 
  EBS.AccountHardwareGrid = Ext.extend(Ext.grid.GridPanel, {
      initComponent:function() {
         var config = {
          	   xtype:'grid',
                 stateful: true,
                 stateId: 'stateAccountAddonServiceGrid',
                 collapsible: true,
                 //unstyled:true,
          	   	  store:new Ext.data.JsonStore({
     		        	paramsAsHash: true,

     		        	//autoLoad: {params:{start:0, limit:100,'account_id': this.findParentByType('xinstancecontainer').instance_id}},
     		        	proxy: new Ext.data.HttpProxy({
     		        		url: '/ebsadmin/accountaddonservices/',
     		        		method:'POST',
     		        	}),    
     		        	fields: [{name: 'service', type:'string'},
     		        		{name: 'account', type:'int'},
     		        		{name: 'id', type:'int'},
     		        		{name: 'subaccount', type:'int'},
     		        		{name: 'activated', type: 'date', dateFormat: Date.patterns.ISO8601Long},
     		        		{name: 'deactivated',  type: 'date', dateFormat: Date.patterns.ISO8601Long},
     		        		{name: 'action_status', type:'boolean'},
     		        		{name: 'speed_status', type:'boolean'},
     		        		{name: 'temporary_blocked', type: 'date', dateFormat: Date.patterns.ISO8601Long},
     		        		{name: 'last_checkout', type: 'date', dateFormat: Date.patterns.ISO8601Long},],
     		        	root: 'records',
     		        	remoteSort:false,
     		        	sortInfo:{
     		        		field:'username',
     		        		direction:'ASC'
     		        	},



          	   }),
          	   plugins:['msgbus'],	
          	
	     	   onChange:function(subject, message) {
	     		   //Ext.Msg.alert(message);
	     		   var me;
	     		   me=this;
	     		   this.store.setBaseParam('account_id', this.findParentByType('xinstancecontainer').ids.account_id);
	     	       me.store.load();
	     	       
	     	    },
              selModel : new Ext.grid.RowSelectionModel({
                   singleSelect : true
                      }),
          	   //autoHeight: true,
          	   //autoWidth: true,
          	   listeners: {
			          render:function(){
			             // console.info('load',this,arguments);
			        	  //alert(this.findParentByType('form').findParentByType('panel').instance_id);
			        	  this.store.setBaseParam('account_id', this.findParentByType('xinstancecontainer').ids.account_id);
			        	  if (this.findParentByType('xinstancecontainer').ids.account_id){
			        		  this.store.load();
			        	  }
			        	  var me;
	            		  me=this;
			        	  me.subscribe('ebs.accountaddonservice.change', {fn:this.onChange, single:false});
			          }
          	   },
                 
          	   autoScroll: true,
          	   columns:[
          	            {
          	            	header:'id',
          	            	dataIndex:'id',
          	            	sortable:true
          	            },
          	            {
          	            	header:'Услуга',
          	            	dataIndex:'service',
          	            	sortable:true
          	            },
          	            {
          	            	header:'Активирована',
          	            	dataIndex:'activated',
          	            	sortable:true,
          	            	renderer:Ext.util.Format.dateRenderer(Date.patterns.ISO8601Long),
          	            	
          	            },
          	            {
          	            	header:'Отключена',
          	            	dataIndex:'deactivated',
          	            	sortable:true,
          	            	renderer:Ext.util.Format.dateRenderer(Date.patterns.ISO8601Long),
          	            },
          	            {
          	            	header:'Последнее списание',
          	            	dataIndex:'last_checkout',
          	            	sortable:true,
          	            	renderer:Ext.util.Format.dateRenderer(Date.patterns.ISO8601Long),
          	            },
          	            {
          	            	header:'Команда активации выполнена',
          	            	dataIndex:'action_status',
          	            	sortable:true
          	            },
          	            {
          	            	header:'Команда установки скорости выполнена',
          	            	dataIndex:'speed_status',
          	            	sortable:true
          	            },
          	            ]
          		   
          		  
             }

      		
         // apply config
         Ext.apply(this, Ext.applyIf(this.initialConfig, config));
  
         EBS.AccountHardwareGrid.superclass.initComponent.apply(this, arguments);
     } // eo function initComponent
  


 });

 Ext.reg('xaccounthardwaregrid', EBS.AccountHardwareGrid);
 
  
  EBS.AccountTariffsGrid = Ext.extend(Ext.grid.GridPanel, {
      initComponent:function() {
         var config = {
          	   xtype:'grid',
                 stateful: true,
                 collapsible: true,
                 //unstyled:true,
                 plugins:['msgbus'],
                 stateId: 'stateAccountTariffsGrid',
          	   	  store:new Ext.data.JsonStore({
     		        	paramsAsHash: true,

     		        	//autoLoad: {params:{start:0, limit:100,'account_id': this.findParentByType('form').findParentByType('panel').instance_id}},
     		        	proxy: new Ext.data.HttpProxy({
     		        		url: '/ebsadmin/accounttariffs/',
     		        		method:'POST',
     		        	}),    
     		        	fields: [{name: 'tarif'},
     		        		{name: 'id', type:'int'},
     		        		{name: 'datetime', type: 'date', dateFormat: Date.patterns.ISO8601Long},
     		        		{name: 'periodical_billed', type:'boolean'},
     		        		],
     		        	root: 'records',
     		        	remoteSort:false,



          	   }),
          	  onChange:function(subject, message) {
	     		   //Ext.Msg.alert(message);
	     		   var me;
	     		   me=this;
	     		   this.store.setBaseParam('account_id', this.findParentByType('xinstancecontainer').ids.id);
	     	       me.store.load();
	     	       
	     	    },
	     	    
	     	  
              selModel : new Ext.grid.RowSelectionModel({
                   singleSelect : true
                      }),
          	   //autoHeight: true,
          	   //autoWidth: true,
          	   listeners: {
			          render:function(){
			             // console.info('load',this,arguments);
			        	  //alert(this.findParentByType('form').findParentByType('panel').instance_id);
			        	  //this.store.setBaseParam('subaccount_id', this.findParentByType('form').findParentByType('panel').instance_id);
			        	  //alert();
			        	  this.store.setBaseParam('account_id', this.findParentByType('xinstancecontainer').ids.id);
			        	  if (this.findParentByType('xinstancecontainer').ids.id){
			        		  this.store.load();
			        	  }
			        	  var me;
	            		  me=this;
			        	  me.subscribe('ebs.accounttarif.change', {fn:this.onChange, single:false});
			          }
          	   },
                 
          	   autoScroll: true,
          	   
          	   columns:[
          	            {
          	            	header:'id',
          	            	dataIndex:'id',
          	            	sortable:true
          	            },
          	            {
          	            	header:'Тарифный план',
          	            	dataIndex:'tarif',
          	            	sortable:true
          	            },
          	            {
          	            	header:'Начало действия',
          	            	dataIndex:'datetime',
          	            	sortable:true,
          	            	renderer:Ext.util.Format.dateRenderer(Date.patterns.ISO8601Long),
          	            	
          	            },
          	            {
          	            	header:'Расчёты по период. услугам произведены',
          	            	dataIndex:'periodical_billed',
          	            	sortable:true,
          	            	
          	            },
          	            ]
          		   
          		  
             }

      		
         // apply config
         Ext.apply(this, Ext.applyIf(this.initialConfig, config));
  
         EBS.AccountTariffsGrid.superclass.initComponent.apply(this, arguments);
     } // eo function initComponent
  


 });

 Ext.reg('xaccounttariffsgrid', EBS.AccountTariffsGrid);
 
   EBS.ComboCity = Ext.extend(Ext.form.ComboBox, {
       initComponent:function() {
          var config = {
       		    anchor: '100%',
       		    fieldLabel: 'Город',
       		    displayField: 'name',
       		    valueField: 'id', 
       		    mode: 'remote',
       		    editable:false,
       		    triggerAction: 'all',
       		    typeAhead: true,
       		    store:new Ext.data.Store({
       		    	autoLoad:true,
       		        proxy: new Ext.data.HttpProxy({
       		            url: '/ebsadmin/city/',
       		            method:'GET',
       		            
       		        }),
       		        
       		        reader: new Ext.data.JsonReader({
       		            root: 'records'
       		        }, [{
       		            name: 'id'
       		        }, {
       		            name: 'name'
       		        }])
       		    }),

       		}
          // apply config
          Ext.apply(this, Ext.apply(this.initialConfig, config));
   
          EBS.ComboCity.superclass.initComponent.apply(this, arguments);
      } // eo function initComponent
   
      ,onRender:function() {
          var me = this;
          this.store.on('load',function(store) {
            me.setValue(null, true);
          })
          EBS.ComboCity.superclass.onRender.apply(this, arguments);
      } // eo function onRender
    

  });
   
  Ext.reg('xcombocity', EBS.ComboCity);
  
  EBS.ComboTariff = Ext.extend(Ext.form.ComboBox, {
      initComponent:function() {
         var config = {
      		  anchor: '100%',
      		mode: 'remote',
  		    editable:false,
            loadingText  : 'Searching...',
            pageSize     : 5,
  		    triggerAction: 'all',
  		    typeAhead: true,
              valueField:'tarif',
              displayField:'name',
              hiddenName:'tarif',

              store: new Ext.data.JsonStore({
                  autoLoad: true,
                  proxy: new Ext.data.HttpProxy({
                      url: '/ebsadmin/tariffs/',
                      method:'GET',
                  }),    
                  fields: ['name', 'tarif'],
                  root: 'records',
                  remoteSort:false,
                  
                }
              ),

      		}
         // apply config
         Ext.apply(this, Ext.applyIf(this.initialConfig, config));
  
         EBS.ComboTariff.superclass.initComponent.apply(this, arguments);
     } // eo function initComponent
  
     ,onRender:function() {
         var me = this;
         
         this.store.on('load',function(store) {
           //me.setValue(null, true);
         });
         me.store.load();
         EBS.ComboTariff.superclass.onRender.apply(this, arguments);
     } // eo function onRender
   

 });
  
 Ext.reg('xcombotariff', EBS.ComboTariff);
 
  EBS.ComboAddedLocal = Ext.extend(Ext.form.ComboBox, {
      initComponent:function() {
         var config = {
      		    anchor: '100%',
      		    editable:false,
      		    store: new Ext.data.ArrayStore({
                    fields: ['name', 'value'],
                    data : [['Добавлен',true],['Не добавлен',false],] // from states.js
                }),
                valueField:'value',
                displayField:'name',
                typeAhead: true,
                mode: 'local',
                triggerAction: 'all',
                

      		}
         // apply config
         Ext.apply(this, Ext.applyIf(this.initialConfig, config));
  
         EBS.ComboAddedLocal.superclass.initComponent.apply(this, arguments);
     } // eo function initComponent
  
     ,onRender:function() {
         var me = this;
         this.store.on('load',function(store) {
           //me.setValue('7', true);
         })
         EBS.ComboAddedLocal.superclass.onRender.apply(this, arguments);
     } // eo function onRender
   

 });
  
 Ext.reg('xcomboaddedlocal', EBS.ComboAddedLocal);

 EBS.ComboEnabledLocal = Ext.extend(Ext.form.ComboBox, {
     initComponent:function() {
        var config = {
     		    anchor: '100%',
     		    editable:false,
     		    store: new Ext.data.ArrayStore({
                   fields: ['name', 'value'],
                   data : [['Активирован',true],['Не активирован',false],] // from states.js
               }),
               valueField:'value',
               displayField:'name',
               typeAhead: true,
               mode: 'local',
               triggerAction: 'all',
               

     		}
        // apply config
        Ext.apply(this, Ext.applyIf(this.initialConfig, config));
 
        EBS.ComboAddedLocal.superclass.initComponent.apply(this, arguments);
    } // eo function initComponent
 
    ,onRender:function() {
        var me = this;
        this.store.on('load',function(store) {
          //me.setValue('7', true);
        })
        EBS.ComboEnabledLocal.superclass.onRender.apply(this, arguments);
    } // eo function onRender
  

});
 
Ext.reg('xcomboenabledlocal', EBS.ComboEnabledLocal);

  EBS.ComboStreet = Ext.extend(Ext.form.ComboBox, {
      initComponent:function() {
         var config = {
      		    anchor: '100%',
      		    fieldLabel: 'Улица',
      		    displayField: 'name',
      		    valueField: 'id', 
      		    mode: 'remote',
      		    editable:false,
                loadingText  : 'Searching...',
                pageSize     : 5,
      		    triggerAction: 'all',
      		    typeAhead: true,
      		    store:new Ext.data.Store({
      		    	autoLoad:true,
      		        proxy: new Ext.data.HttpProxy({
      		            url: '/ebsadmin/street/',
      		            method:'GET',
      		            
      		        }),
      		        
      		        reader: new Ext.data.JsonReader({
      		            root: 'records'
      		        }, [{
      		            name: 'id'
      		        }, {
      		            name: 'name'
      		        }])
      		    }),

      		}
         // apply config
         Ext.apply(this, Ext.apply(this.initialConfig, config));
  
         EBS.ComboStreet.superclass.initComponent.apply(this, arguments);
     } // eo function initComponent
  
     ,onRender:function() {
         var me = this;
         this.store.on('load',function(store) {
           me.setValue(null, true);
         })
         EBS.ComboStreet.superclass.onRender.apply(this, arguments);
     } // eo function onRender
   

 });
  
 Ext.reg('xcombostreet', EBS.ComboStreet);
   
 EBS.ComboHouse = Ext.extend(Ext.form.ComboBox, {
     initComponent:function() {
        var config = {
     		    anchor: '100%',
     		    fieldLabel: 'Дом',
     		    displayField: 'name',
     		    valueField: 'id', 
     		    mode: 'remote',
     		    editable:false,
     		    triggerAction: 'all',
     		    typeAhead: true,
     		    store:new Ext.data.Store({
     		    	//autoLoad:true,
     		        proxy: new Ext.data.HttpProxy({
     		            url: '/ebsadmin/house/',
     		            method:'GET',
     		            
     		        }),
     		        
     		        reader: new Ext.data.JsonReader({
     		            root: 'records'
     		        }, [{
     		            name: 'id'
     		        }, {
     		            name: 'name'
     		        }])
     		    }),

     		}
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
 
        EBS.ComboHouse.superclass.initComponent.apply(this, arguments);
    } // eo function initComponent
 
    ,onRender:function() {
        var me = this;
        this.store.on('load',function(store) {
        	if (!this.value){
          //me.setValue(null, true);
        	};
        })
        this.store.load();
        EBS.ComboHouse.superclass.onRender.apply(this, arguments);
    } // eo function onRender
  

});
 
Ext.reg('xcombohouse', EBS.ComboHouse);

EBS.ComboTemplate = Ext.extend(Ext.form.ComboBox, {
    initComponent:function() {
       var config = {
    		    displayField: 'name',
    		    valueField: 'id',
    		    
    		    mode: 'remote',
    		    editable:false,
    		    triggerAction: 'all',
    		    typeAhead: true,
    		    store:new Ext.data.Store({
    		    	autoLoad:true,
    		        proxy: new Ext.data.HttpProxy({
    		            url: '/ebsadmin/template/',
    		            method:'POST',
    		            
    		        }),
    		        
    		        reader: new Ext.data.JsonReader({
    		            root: 'records'
    		        }, [{
    		            name: 'id'
    		        }, {
    		            name: 'name'
    		        }])
    		    }),

    		}
       // apply config
       Ext.apply(this, Ext.applyIf(this.initialConfig, config));

       EBS.ComboTemplate.superclass.initComponent.apply(this, arguments);
   } // eo function initComponent


 

});

Ext.reg('xcombotemplate', EBS.ComboTemplate);

EBS.SystemUser = Ext.extend(Ext.form.ComboBox, {
    initComponent:function() {
       var config = {
    		    anchor: '100%',
    		    displayField: 'name',
    		    valueField: 'id', 
    		    mode: 'remote',
    		    editable:false,
    		    triggerAction: 'all',
    		    typeAhead: true,
    		    store:new Ext.data.Store({
    		    	autoLoad:true,
    		        proxy: new Ext.data.HttpProxy({
    		            url: '/ebsadmin/systemuser/',
    		            method:'GET',
    		            
    		        }),
    		        
    		        reader: new Ext.data.JsonReader({
    		            root: 'records'
    		        }, [{
    		            name: 'id'
    		        }, {
    		            name: 'name'
    		        }])
    		    }),

    		}
       // apply config
       Ext.apply(this, Ext.apply(this.initialConfig, config));

       EBS.SystemUser.superclass.initComponent.apply(this, arguments);
   } // eo function initComponent

   ,onRender:function() {
       var me = this;
       this.store.on('load',function(store) {
         me.setValue(null);
       })
       this.store.load();
       EBS.SystemUser.superclass.onRender.apply(this, arguments);
   } // eo function onRender
 

});

Ext.reg('xcombosystemuser', EBS.SystemUser);

EBS.ComboAccountStatus = Ext.extend(Ext.form.ComboBox, {
    initComponent:function() {
       var config = {
    		    anchor: '100%',
    		    displayField: 'name',
    		    valueField: 'id', 
    		    mode: 'remote',
    		    editable:false,
    		    triggerAction: 'all',
    		    typeAhead: true,
    		    store:new Ext.data.Store({
    		    	autoLoad:true,
    		        proxy: new Ext.data.HttpProxy({
    		            url: '/ebsadmin/accountstatus/',
    		            method:'GET',
    		            
    		        }),
    		        
    		        reader: new Ext.data.JsonReader({
    		            root: 'records'
    		        }, [{
    		            name: 'id'
    		        }, {
    		            name: 'name'
    		        }])
    		    }),

    		}
       // apply config
       Ext.apply(this, Ext.applyIf(this.initialConfig, config));

       EBS.ComboAccountStatus.superclass.initComponent.apply(this, arguments);
   } // eo function initComponent

   ,onRender:function() {
       var me = this;
       this.store.on('load',function(store) {
         me.setValue(1, true);
        
       })
       this.store.load();
       EBS.ComboAccountStatus.superclass.onRender.apply(this, arguments);
   } // eo function onRender
 

});

Ext.reg('xcomboaccountstatus', EBS.ComboAccountStatus);

EBS.ComboNas = Ext.extend(Ext.form.ComboBox, {
    initComponent:function() {
       var config = {
    		    anchor: '100%',
    		    displayField: 'name',
    		    valueField: 'id', 
    		    mode: 'remote',
    		    editable:false,
    		    triggerAction: 'all',
    		    typeAhead: true,
    		    store:new Ext.data.Store({
    		    	autoLoad: true,
    		        proxy: new Ext.data.HttpProxy({
    		            url: '/ebsadmin/nas/',
    		            method:'GET',
    		            
    		        }),
    		        
    		        reader: new Ext.data.JsonReader({
    		            root: 'records'
    		        }, [{
    		            name: 'id'
    		        }, {
    		            name: 'name'
    		        }])
    		    }),

    		}
       // apply config
       
       Ext.apply(this, Ext.applyIf(this.initialConfig, config));
       
       EBS.ComboNas.superclass.initComponent.apply(this, arguments);
   } // eo function initComponent

   ,onRender:function() {
	   //this.store.load();
       var me = this;

       this.store.on('load',function(store) {
    	   //alert(me.getValue());
    	   if (me.getValue()==0){
    		   me.setValue(null, true);
    	   }
       })
       this.store.load();
       EBS.ComboNas.superclass.onRender.apply(this, arguments);
   } // eo function onRender
 

});

Ext.reg('xcombonas', EBS.ComboNas);
 

EBS.ComboIpPool = Ext.extend(Ext.form.ComboBox, {
    initComponent:function() {
       var config = {
    		    anchor: '100%',
    		    displayField: 'name',
    		    valueField: 'id', 
    		    mode: 'remote',
    		    editable:false,
    		    triggerAction: 'all',
    		    pool_type:0,
    		    typeAhead: true,
    		    store:new Ext.data.Store({
    		    	autoLoad:true,
    		        proxy: new Ext.data.HttpProxy({
    		            url: '/ebsadmin/ippool/',
    		            method:'POST',
    		            
    		        }),
    		        
    		        reader: new Ext.data.JsonReader({
    		            root: 'records'
    		        }, [{
    		            name: 'id'
    		        }, {
    		            name: 'name'
    		        }])
    		    }),

    		}
       // apply config
       
       Ext.apply(this, Ext.applyIf(this.initialConfig, config));
       
       EBS.ComboIpPool.superclass.initComponent.apply(this, arguments);
       this.store.setBaseParam('pool_type', this.pool_type);
   } // eo function initComponent

   ,onRender:function() {
       var me = this;
       this.store.setBaseParam('pool_type', this.pool_type);
       this.store.on('load',function(store) {
    	   //alert(me.getValue());
    	   if (me.getValue()==0){
    		   me.setValue(null, true);
    	   }
       })
       this.store.load();
       EBS.ComboIpPool.superclass.onRender.apply(this, arguments);
   } // eo function onRender
 

});

Ext.reg('xcomboippool', EBS.ComboIpPool);

EBS.ComboSwitch = Ext.extend(Ext.form.ComboBox, {
    initComponent:function() {
       var config = {
    		    anchor: '100%',
    		    displayField: 'name',
    		    valueField: 'id', 
    		    mode: 'remote',
    		    editable:false,
    		    triggerAction: 'all',
    		    typeAhead: true,
    		    store:new Ext.data.Store({
    		    	//autoLoad:true,
    		        proxy: new Ext.data.HttpProxy({
    		            url: '/ebsadmin/switch/',
    		            method:'GET',
    		            
    		        }),
    		        
    		        reader: new Ext.data.JsonReader({
    		            root: 'records'
    		        }, [{
    		            name: 'id'
    		        }, {
    		            name: 'name'
    		        }])
    		    }),

    		}
       // apply config
       Ext.apply(this, Ext.apply(this.initialConfig, config));

       EBS.ComboSwitch.superclass.initComponent.apply(this, arguments);
       //this.store.setBaseParam('pool_type', this.pool_type);
   } // eo function initComponent

   ,onRender:function() {
	   this.store.load();
       var me = this;
       this.store.on('load',function(store) {
    	   //alert(me.getValue());
    	   if (me.getValue()==0){
    		   me.setValue(null, true);
    	   }
       })
       this.store.load();
       EBS.ComboSwitch.superclass.onRender.apply(this, arguments);
   } // eo function onRender
 

});

Ext.reg('xcomboswitch', EBS.ComboSwitch);


EBS.AccountHardwareGrid = Ext.extend(Ext.grid.GridPanel, {
    initComponent:function() {
       var config = {
        	   xtype:'grid',
               stateful: true,
               stateId: 'stateAccountHardwareGrid_',
               collapsible: false,
               //unstyled:true,
        	   	  store:new Ext.data.JsonStore({
   		        	paramsAsHash: true,

   		        	//autoLoad: {params:{start:0, limit:100,'account_id': this.findParentByType('xinstancecontainer').instance_id}},
   		        	proxy: new Ext.data.HttpProxy({
   		        		url: '/ebsadmin/accounthardware/',
   		        		method:'POST',
   		        	}),    
   		        	fields: [{name: 'account', type:'id'},
   		        		{name: 'hardware', type:'int'},
   		        		{name: 'id', type:'int'},
   		        		{name: 'datetime', type: 'date', dateFormat: Date.patterns.ISO8601Long},
   		        		{name: 'returned',  type: 'date', dateFormat: Date.patterns.ISO8601Long},
   		        		{name: 'comment', type:'string'},
   		        		],
   		        	root: 'records',
   		        	remoteSort:false,
   		        	sortInfo:{
   		        		field:'datetime',
   		        		direction:'DESC'
   		        	},



        	   }),
        	   plugins:['msgbus'],	
        	
      	   onChange:function(subject, message) {
      		   //Ext.Msg.alert(message);
      		   var me;
      		   me=this;
      		   account_id=this.findParentByType('xinstancecontainer').ids.account_id;
      		   
		        	  if (account_id){
		        		  //alert(account_id)
		        		  this.store.setBaseParam('account_id',account_id);
		        		  this.store.load();
		        	  }
      	       //Ext.Msg.alert(message);
      	    },
            selModel : new Ext.grid.RowSelectionModel({
                 singleSelect : true
                    }),
        	   //autoHeight: true,
        	   //autoWidth: true,
        	   listeners: {
			          render:function(){
			             // console.info('load',this,arguments);
			        	  //alert(this.findParentByType('form').findParentByType('panel').instance_id);
			        	  this.store.setBaseParam('account_id', this.findParentByType('xinstancecontainer').instance_id);
			        	  if (this.findParentByType('xinstancecontainer').instance_id){
			        		  this.store.load();
			        	  }
			        	  var me;
	            		  me=this;
			        	  me.subscribe('ebs.accounthardware.change', {fn:this.onChange, single:false});
			          }
        	   },
               
        	   autoScroll: true,
        	 tbar: [{
			    icon: media+'icons/16/arrow_refresh.png',
		        text: 'Обновить',
		        handler: function(){
		        	this.ownerCt.ownerCt.store.load();
		        }
		       },{
			        iconCls: 'icon-user-add',
			        text: 'Добавить',
			        handler: function(){
			     	   var account_id;
			     	   account_id = this.findParentByType('xinstancecontainer').ids.account_id;
			     	   EBS.displayForm('ebs_accountsPanel', 'accounthardware',{'account_id':account_id,id:null}, this.findParentByType('grid'))
			     	   
			        }
			    },{
			        iconCls: 'icon-user-edit',
			        text: 'Редактировать',
			        handler: function(){
			     	   var id;
			     	   var account_id;
			     	   account_id = this.findParentByType('xinstancecontainer').ids.account_id;
			     	   id = this.findParentByType('grid').selModel.selections.items[0].id;
			     	   EBS.displayForm('ebs_accountsPanel', 'accounthardware',{'account_id':account_id,id:id}, this.findParentByType('grid'))
			        }
			    },{
			        //ref: '../removeBtn',
			        iconCls: 'icon-delete',
			        text: 'Remove',
			        //disabled: true,
			        ref: '../removeButton',
			        handler: function(){
			     	   
			        }
			    }],
        	   columns:[
        	            {
        	            	header:'id',
        	            	dataIndex:'id',
        	            	sortable:true
        	            },
        	            {
        	            	header:'Оборудование',
        	            	dataIndex:'hardware',
        	            	sortable:true
        	            },
        	            {
        	            	header:'Выдано',
        	            	dataIndex:'datetime',
        	            	sortable:true,
        	            	renderer:Ext.util.Format.dateRenderer(Date.patterns.ISO8601Long),
        	            	
        	            },
        	            {
        	            	header:'Возвращено',
        	            	dataIndex:'deactivated',
        	            	sortable:true,
        	            	renderer:Ext.util.Format.dateRenderer(Date.patterns.ISO8601Long),
        	            },
        	            
        	            ]
        		   
        		  
           }

    		
       // apply config
       Ext.apply(this, Ext.applyIf(this.initialConfig, config));

       EBS.AccountHardwareGrid.superclass.initComponent.apply(this, arguments);
   } // eo function initComponent



});

Ext.reg('xaccounthardwaregrid', EBS.AccountHardwareGrid);
Ext.reg('xaccountaddonservicesgrid', EBS.AccountAddonServiceGrid);
/* EOF BASE Components*/





















});













/*
 


   this.topToolbar = [
                         {
                            //text: 'ok',
                            icon: media+'icons/16/new/wand.png',
                            height:32,
                            width:32,
                            tooltip: 'Just a magic!',
                            handler: function () {}
                        },
                         {
                            text: 'Print',
                            icon: media+'icons/16/new/printer.png',
                            height:32,
                            width:32,
                            tooltip: 'Print current panel',
                            handler: function () {
                                //Ext.ux.Printer.print(mainPanel)
                            }
                        },
                        {
                            xtype: 'tbfill'
                        },
                        {
                            xtype: 'tbbutton',
                            id:'exclamation',
                            text: '<b>10</b> New messages',
                            tooltip: 'Urgent messages from administration',
                            icon: media+'/helpdesk_img/show_comments.png'
                        },
                        {
                            xtype: 'tbseparator'
                        },
                        {
                            xtype: 'tbbutton',
                            text: 'Username',
                            icon: media+'icons/16/new/user.png',
                            height:32,
                            width:32,
                            menu: [{
                                text: 'Settings',
                                icon: media+'icons/16/new/cog.png'
                            },
                            {
                                text: 'Item'
                            },
                            {
                                xtype: 'tbseparator'
                            },
                            {
                                text: 'Logout',
                                icon: media+'icons/16/new/door_out.png'
                            }]
                        }

                    ];


 */















/*
 *tests:
Создаст все доступные окна

for(i=0;i<EBS.windows.keys.length;i++){
    cmp =Ext.create({xtype:EBS.windows.keys[i]});
    Ext.getCmp('main_tab_panel').add(cmp);
}

 */