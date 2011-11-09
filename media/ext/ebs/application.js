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
    EBS.displayForm = function(xtype, action, self){
        /*
         * Вызывается из меню компоненты
         *
         * создает форму
         *
         **/

           console.log(action, self);

            //Create edit window
           selection = self.selModel.selections;
           if(selection.items.length!=1){
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
                        winCmp = new Ext.Window({
                            id:window_key,
                            applyTo:Ext.get('body'),
                            width:500,
                            height:300,
                            title:form_data.windowTitle,
                            autoHeight: true,
                            viewConfig: {
                                forceFit: true
                            },
                            tools : [{
                                    id: 'gear',
                                    handler: function() {
                                        Ext.Msg.alert('TODO:','Attach as tab.');
                                        }
                                   }],

                            plain: true,
                            items: [form_data],
                            buttons: [{
                                    text:'Submit',
                                    handler: function(obj, e){
                                        form_callback(obj, e);
                                        form = this.ownerCt.ownerCt.items.items[0].getForm()
                                        form.updateRecord(form.rec);
                                        //Update server data
                                        //form.rec.store.save();
                                        EBS.closeForm(this)
                                    }
                                },{
                                    text: 'Close',
                                    handler: function(){
                                        EBS.closeForm(this)
                                    }
                                }]
                        });
                        EBS.windows[window_key] = winCmp;
                    }
             form = winCmp.items.items[0].getForm();
             form.rec = selection.items[0];

             //form.loadRecord(form.rec);
             //form.load({url:'/account/', method:'GET',params:{'id':selection.items[0].id}} );
             winCmp.show();
    }

    EBS.displayCustomForm = function(xtype, action, self){
        /*
         * Вызывается из меню компоненты
         *
         * создает форму
         *
         **/

           console.log(action, self);

            //Create edit window
           selection = self.selModel.selections;
           if(selection.items.length!=1){
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
                        winCmp = new Ext.Window({
                            id:window_key,
                            applyTo:Ext.get('body'),
                            //width:500,
                            //height:300,
                            layout:'anchor',
                            title:form_data.windowTitle,
                            autoHeight: false,
                            viewConfig: {
                                forceFit: true
                            },
                            tools : [{
                                    id: 'gear',
                                    handler: function() {
                                        Ext.Msg.alert('TODO:','Attach as tab.');
                                        }
                                   }],

                            plain: true,
                            items: [form_data],
                        });
                        EBS.windows[window_key] = winCmp;
                    }
             form = winCmp.items.items[0].getForm();
             form.rec = selection.items[0];

             //form.loadRecord(form.rec);
             //form.load({url:'/account/', method:'GET',params:{'id':selection.items[0].id}} );
             winCmp.show();
    }
    
    EBS.displayFormInTab = function(xtype, action, id, self){
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
                        winCmp = new Ext.Panel({
                            id:window_key+id,
                            applyTo:Ext.get('body'),
                            //width:500,
                            //height:300,
                            title:form_data.windowTitle,
                            autoHeight: false,
                            viewConfig: {
                                forceFit: true
                            },
                            tools : [{
                                    id: 'gear',
                                    handler: function() {
                                        Ext.Msg.alert('TODO:','Attach as tab.');
                                        }
                                   }],

                            plain: true,
                            items: [form_data],
                            buttons: [{
                                    text:'Submit',
                                    handler: function(obj, e){
                                        form_callback(obj, e);
                                        form = this.ownerCt.ownerCt.items.items[0].getForm()
                                        form.submit({url:form.save_url, waitMsg:'Saving Data...', submitEmptyText: true});
                                        //Update server data
                                        //form.rec.store.save();
                                        //EBS.closeForm(this)
                                    }
                                },{
                                    text: 'Close',
                                    handler: function(){
                                        EBS.closeForm(this)
                                    }
                                }]
                        });
                        EBS.windows[window_key] = winCmp;
                    }
             form = winCmp.items.items[0].getForm();
             //form.rec = selection.items[0];
             //alert(form.url);
             form.load({url:form.url,method:form.method,params:{'id':id}});
             //form.loadRecord(form.rec);
             
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
        minSize: 150,
        autoScroll: true,
        autoHeight: true,
        // tree-specific configs:
        rootVisible: false,
        lines: false,
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
                                                }
                                            }else{
                                                cmp = Ext.create({
                                                    xtype:type
                                                    });
                                                EBS.windowCmp.add(cmp);
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
                                        minTabWidth     : 75,
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
                                        items           : [
                                            {
                                                title : 'Welcome',
                                                html  : i18n.welcomeText
                                            },
                                            {
                                                xtype :'ebs_accountsPanel',
                                                id    :'ebs_accountsPanel'

                                            },
                                            {
                                                xtype:'ebs_nasPanel',
                                                id:'ebs_nasPanel'

                                            }
                                        ]
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
            //me.setValue('7', true);
          })
          EBS.ComboCity.superclass.onRender.apply(this, arguments);
      } // eo function onRender
    

  });
   
  Ext.reg('xcombocity', EBS.ComboCity);
  
  
  EBS.ComboStreet = Ext.extend(Ext.form.ComboBox, {
      initComponent:function() {
         var config = {
      		    anchor: '100%',
      		    fieldLabel: 'Улица',
      		    displayField: 'name',
      		    valueField: 'id', 
      		    mode: 'remote',
      		    editable:false,
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
           //me.setValue('7', true);
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
     		    	autoLoad:true,
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
          //me.setValue('7', true);
        })
        EBS.ComboHouse.superclass.onRender.apply(this, arguments);
    } // eo function onRender
  

});
 
Ext.reg('xcombohouse', EBS.ComboHouse);

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
         //me.setValue('7', true);
       })
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
       Ext.apply(this, Ext.apply(this.initialConfig, config));

       EBS.ComboAccountStatus.superclass.initComponent.apply(this, arguments);
   } // eo function initComponent

   ,onRender:function() {
       var me = this;
       this.store.on('load',function(store) {
         //me.setValue('7', true);
       })
       EBS.ComboAccountStatus.superclass.onRender.apply(this, arguments);
   } // eo function onRender
 

});

Ext.reg('xcomboaccountstatus', EBS.ComboAccountStatus);

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