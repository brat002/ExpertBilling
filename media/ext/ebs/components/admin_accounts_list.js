Ext.onReady(function(){
    Ext.ns('EBS.forms.ebs_accountsPanel')
    EBS.conponents.accountsGrid = Ext.extend(EBS.base.GridPanel, {
         initComponent: function() {
                /*
                 *ф-я вызывается в менюшке. В качестве параметров идут self, вызываемая ф-я, если нужно - параметры.
                 *берем функцию через  eval и вызываем ее с параметрами
                 *id у self обязательна.
                 *
                 *Будут перенесены в базовый компонент. менять сразу во всех компонентах!
                 **/
                this.tbFormCallBack = function(self, action){EBS.displayForm(self.xtype, action, self)}
                this.tbCustomFormCallBack = function(self, action){EBS.displayCustomForm(self.xtype, action,{}, self)}

                this.tbNewFormInTabCallBack = function(self, action){
                	id=null;
                	
                	EBS.displayFormInTab(self.xtype, action,id, {'account_id':id}, self)
                	}
                this.tbFormInTabCallBack = function(self, action, id){
                	//alert(id);
                	//alert(self.selModel);
                	
                		id=self.selModel.selections.items[0].id;
                		//alert(self.selModel.selections.items[0]);
                	
                	EBS.displayFormInTab(self.xtype, action,id, {'id':id}, self)
                	}
                this.tbWindowCallBack = function(self, action){EBS.displayWindow(self.xtype, action, self)}
                this.tbCommandCallBack = function(self, a,b,c){
                    eval(action)(a,b,c)
                }
                
                this.tbFormReloadCallBack = function(self){
                	
                	
                	self.store.load();
                	}

             // MENU
             this.topToolbar = new Ext.Toolbar({
                    enableOverflow: true,
                    items:[
						{
						    icon: media+'icons/16/add.png',
						    height:16,width:16,
						    text: 'Добавить',
						    handler: this.tbNewFormInTabCallBack.createCallback(this, 'edit_user')
						},
                         {
                            icon: media+'icons/16/pencil.png',
                            height:16,width:16,
                            text: 'Редактировать',
                            handler: this.tbFormInTabCallBack.createCallback(this, 'edit_user',null)
                        },{
                            text: i18n.print,
                            icon: media+'icons/16/printer.png',
                            height:16,width:16,
                            tooltip: i18n.printToolTip,
                            handler: function(){Ext.ux.Printer.print(this.ownerCt.ownerCt)}
                        },
                        {xtype: 'tbseparator'},
                        {
                            xtype: 'tbbutton',
                            text: 'Действия',
                            icon: media+'icons/16/new/user.png',
                            height:16,width:16,
                            menu: [
                                {
                                    text : "Пополнить баланс",
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbCustomFormCallBack.createCallback(this,'edit_credit')
                                },{
                                    text : i18n.accounts.edit_server,
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbFormCallBack.createCallback(this,'edit_server')
                                },{
                                    text : i18n.accounts.set_ipn,
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbFormCallBack.createCallback(this,'set_ipn')
                                },{
                                    text : i18n.accounts.set_vpn,
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbFormCallBack.createCallback(this,'edit_server')
                                },{
                                    text : i18n.accounts.set_mac,
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbFormCallBack.createCallback(this,'set_mac')
                                },{
                                    text : i18n.accounts.set_ipn_from_pool,
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbFormCallBack.createCallback(this,'set_ipn_from_pool')
                                },{
                                    text : i18n.accounts.set_vpn_from_pool,
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbFormCallBack.createCallback(this,'set_vpn_from_pool')
                                },{
                                    text : i18n.accounts.set_flags,
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbFormCallBack.createCallback(this,'set_flags')
                                }

                            ]
                        },{xtype: 'tbseparator'},{
                            text: i18n.save,
                            icon: media+'icons/16/accept.png',
                            height:16,width:16,
                            tooltip: i18n.saveToolTip,
                            handler: EBS.store.accounts.save
                        }
                        ,{xtype: 'tbseparator'},{
                            text: 'Обновить',
                            icon: media+'icons/16/arrow_refresh.png',
                            height:24,width:24,
                            tooltip: i18n.saveToolTip,
                            handler: this.tbFormReloadCallBack.createCallback(this)
                        }

                    ]
                });






             Ext.apply(this, {
                                id:'accounts_list',
                                view: new Ext.grid.GroupingView(),
                                store   : EBS.store.accounts,
                                closable:false,
                              //  plugins : [this.filters],
                                tbar    : this.topToolbar,
                                stateId:'accounts_list_',
                                defaults: {
                                    sortable: true,
                                    menuDisabled: false,
                                    //width: 20
                                },
                                columns : [
                                    {
                                        header   : '#',
                                        sortable : true,
                                        //width    : 85,
                                        //locked: true,
                                        dataIndex: 'id',
                                        filter: {
                                            type: 'numeric'
                                        }

                                    },                                
                                    {
                                        header   : 'Логин',
                                        sortable : true,
                                        //width    : 85,
                                        //locked: true,
                                        dataIndex: 'username',
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                    {
                                        header   : 'Договор',
                                        sortable : true,
                                        //width    : 85,
                                        //locked: true,
                                        dataIndex: 'contract',
                                        filter: {
                                            type: 'string'
                                        }

                                    },      
                                    {
                                        header   : 'Тариф',
                                        sortable : true,
                                        //width    : 85,
                                        //locked: true,
                                        dataIndex: 'tariff',
                                        filter: {
                                            type: 'string'
                                        }

                                    }, 
                                    {
                                        header   : "ФИО",
                                        sortable : true,
                                        autoexpand:true,
                                        width:200,
                                        dataIndex: 'fullname',
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                    {
                                        header   : i18n.accounts.ballance,
                                        sortable : true,
                                        //autoexpand:true,
                                        width:200,
                                        dataIndex: 'ballance',
                                        renderer: EBS.moneyRenderer,
                                        filter: {
                                            type: 'string'
                                        }

                                    },  
                                    

                                   {
                                        header   : i18n.accounts.credit,
                                        sortable : true,
                                        //autoexpand:true,
                                        //width:200,
                                        dataIndex: 'credit',
                                        
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                   {
                                        header   : 'Город',
                                        sortable : true,
                                        //autoexpand:true,
                                        //width:200,
                                        dataIndex: 'city',
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                    {
                                        header   : 'Улица',
                                        sortable : true,
                                        //autoexpand:true,
                                        //width:200,
                                        dataIndex: 'street',
                                        filter: {
                                            type: 'string'
                                        }

                                    },                                    
                                   {
                                        header   : 'Дом',
                                        sortable : true,
                                        //autoexpand:true,
                                        //width:200,
                                        dataIndex: 'house',
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                    {
                                        header   : 'Квартира',
                                        sortable : true,
                                        //autoexpand:true,
                                        //width:200,
                                        dataIndex: 'room',
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                    {
                                        header   : 'Контактное лицо',
                                        sortable : true,
                                        //autoexpand:true,
                                        //width:200,
                                        dataIndex: 'contactperson',
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                    {
                                        header   : 'Контактный телефон',
                                        sortable : true,
                                        //autoexpand:true,
                                        //width:200,
                                        dataIndex: 'contactphone',
                                        filter: {
                                            type: 'string'
                                        }

                                    },    
                                    {
                                        header   : 'Домашний телефон',
                                        sortable : true,
                                        //autoexpand:true,
                                        //width:200,
                                        dataIndex: 'phone_h',
                                        filter: {
                                            type: 'string'
                                        }

                                    },     
                                    {
                                        header   : 'Мобильный телефон',
                                        sortable : true,
                                        //autoexpand:true,
                                        //width:200,
                                        dataIndex: 'phone_m',
                                        filter: {
                                            type: 'string'
                                        }

                                    },                                      
                                    {
                                        header   : i18n.accounts.created,
                                        //width    : 115,
                                        sortable : true,
                                        renderer:Ext.util.Format.dateRenderer(Date.patterns.ISO8601Long),
                                        dataIndex: 'created'
                                    },

                                    {
                                        header   : i18n.accounts.email,
                                        //width    : 115,
                                        sortable : true,
                                        dataIndex: 'email',
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                ],
                                listeners: {/*
                                    render:function(){
                                     this.bbar.updateInfo();
                                    }*/
                                },
                                stripeRows: false,
                                title: i18n.accounts.accounts,
                                stateful: true,
                                //stateId: 'accountsgrid',
                                
                            //bbar:this.pagination
                });
            this.bbar.store = this.store;
            this.on('rowdblclick', function(eventGrid, rowIndex, e) {
            	this.tbFormInTabCallBack(this, 'edit_user',this.selModel.selections.items[0].id);
            	
            	}, this);            
            EBS.conponents.accountsGrid.superclass.initComponent.apply(this, arguments);
            //this.bbar.updateInfo();

         } //initComponent
     });

    	
    EBS.forms.ebs_accountsPanel.document = {
    	    xtype: 'form',
    	    width: 905,
    	    height: 580,
    	    title: 'Документ',
    	    layout:'fit',
    	    plugins:['msgbus'],
    	    url:'/ebsadmin/document/get/', 
			save_url:'/ebsadmin/document/set/',
			method:'POST',
			tbar: [{
 			    icon: media+'icons/16/printer.png',
 		        text: 'Распечатать',
 		        handler: function(){
 		        	//alert(this.ownerCt.ownerCt.url);
 		        	Ext.ux.Printer.print(this.ownerCt.ownerCt.getForm().findField('body'));
 		        	
 		        }
 		       }],
			
			listeners:{
				'render': function(){
					//alert(this.findParentByType('xinstancewindow').ids.account_id);
					this.getForm().findField('account').setValue(this.findParentByType('xinstancewindow').ids.account_id);
				}
			},
			reader: new Ext.data.JsonReader({
			    idProperty: 'id',          
			    root: 'records',             
			    fields: [
					{name: 'id', type:'int'},
					{name: 'account', type:'int'},
					{name: 'type', type:'int'},
					{name: 'body', type:'string'},
					{name: 'contractnumber', type:'string'},
					{name: 'comment', type:'string'},
					{name: 'date_end', type:'date', dateFormat: Date.patterns.ISO8601Long},
					{name: 'date_start', type:'date', dateFormat: Date.patterns.ISO8601Long},
			    ]
			}),
    	    items: [
    	        {
    	            xtype: 'fieldset',
    	            title: 'Параметры документа',
    	            items: [
    	                {
    	                    xtype: 'xcombotemplate',
    	                    name: 'type',
    	                    hiddenName: 'type',
    	                    anchor: '50%',
    	                    fieldLabel: 'Тип документа'
    	                },
    	                {
    	                    xtype: 'hidden',
    	                    name: 'id',
    	                },
    	                {
    	                    xtype: 'hidden',
    	                    name: 'account',
    	                },    	                
    	                {
    	                    xtype: 'combo',
    	                    name: 'contractnumber',
    	                    anchor: '50%',
    	                    fieldLabel: 'Номер/шаблон',
    	                    
                     		    
                     		    displayField: 'template',
                     		    valueField: 'template', 
                     		    mode: 'remote',
                     		    editable:true,
                                loadingText  : 'Searching...',
                                pageSize     : 25,
                     		    triggerAction: 'all',
                     		    typeAhead: false,
                     		    // ref:
								// 'store/p',
                     		    listeners:{
                 		        	focus:function(obj, options){
                 		        		
                 		        	},
                 		        	// scope:this.ownerCt,
                 		        	
                 		        },
                 		        
                     		    store:new Ext.data.Store({
                     		    	
                     		    	
                     		        proxy: new Ext.data.HttpProxy({
                     		            url: '/ebsadmin/contracttemplate/',
                     		            method:'POST',
                     		            
                     		        }),
                     		        
                     		        reader: new Ext.data.JsonReader({
                     		        	totalProperty: 'totalCount',
                     		            root: 'records'
                     		        }, [{
                     		            name: 'template'
                     		        }])
                     		    }),
                                
                            
    	                },
    	                {
    	                    xtype: 'xdatetime',
    	                    name: 'date_start',
    	                    anchor: '50%',
    	                    fieldLabel: 'Начало'
    	                },
    	                {
    	                    xtype: 'button',
    	                    text: 'Сгенерировать',
    	                    anchor: '50%',
    	                    fieldLabel: '&nbsp',
    	                    handler: function(button, evt){
    	                    	parentwindow = button.findParentByType('xinstancewindow');
	                    		form = button.findParentByType('form').getForm();
	                    	    account = parentwindow.ids.account_id;
	                    	    contractnumber = form.findField('contractnumber').getValue();
	                    	    template = form.findField('type').getValue();
	                    	    date_start = form.findField('date_start').getValue();
	                    	    date_end = form.findField('date_end').getValue();
	                    	    if (date_end){
	                    	    	date_end=date_end.format(Date.patterns.ISO8601Long)
	                    	    }
    	                    	Ext.Ajax.request({
    	                            params: {account: account,contractnumber:contractnumber, template:template,date_start: date_start.format(Date.patterns.ISO8601Long),date_end:date_end},
    	                            url: '/ebsadmin/documentrender/',
    	                            success: function (resp) {
    	                                var data;
    	                                data = Ext.decode(resp.responseText);
    	                                if (data.success === true) {
    	                                    
    	                                	form.findField('body').setValue(data.body);
    	                                    
    	                                } else {
    	                                    Ext.MessageBox.alert('Ошибка', 'Состояние не изменено. '+data.msg);
    	                                }
    	                            },
    	                            failure: function () {
    	                            	Ext.MessageBox.alert('Ошибка', 'Состояние не изменено');
    	                            }
    	                        });
    	                    }
    	                    
    	                    
    	                },
    	                {
    	                    xtype: 'htmleditor',
    	                    
    	                    ref:'../editor',
    	                    name: 'body',
    	                    anchor: '100%',
    	                    fieldLabel: 'Текст'
    	                },
    	                {
    	                    xtype: 'xdatetime',
    	                    name: 'date_end',
    	                    anchor: '50%',
    	                    fieldLabel: 'Окончание'
    	                },
    	                {
    	                    xtype: 'textarea',
    	                    name: 'comment',
    	                    anchor: '50%',
    	                    fieldLabel: 'Комментарий'
    	                }
    	            ]
    	        }
    	    ]
    	}

    
    EBS.forms.ebs_accountsPanel.document_submitAction =  function(object, event, form, window){
    	
    	
 	    f=form;
 	    pub = function(){window.items.items[0].publish('ebs.accountdocument.change', 'msg');	}
        
        form.submit({url:form.save_url, waitMsg:'Saving Data...', submitEmptyText: true, success: function(obj,action) {        
        	
        	pub();
        	window.hide().destroy()
            delete EBS.windows[window.id];

        },failure: function(form,action) {        
         	Ext.Msg.alert('Ошибка', action.result.msg )}});
    }
    
/* ACCOUNTS FORMS*/
    EBS.forms.ebs_accountsPanel.edit_user = {
                                        xtype: 'panel',
                                        //id: 'account-info',
                                        windowTitle:'Параметры аккаунта',
                                        closable:false,
                                        autoScroll:true,
                                        layout:'fit',
                                        height: '100%',
                                        width: '100%',
                                        items:[		{xtype: 'form',
													//id: 'account-info',
													//title:'Account details',
													autoScroll:true,
													autoHeight:true,
													layout:'anchor',
													url:'/ebsadmin/account/', 
													save_url:'/ebsadmin/account/save/',
													standardSubmit: false,
													frame:false,
													border:false,
													method:'POST',
										     	   tbar: [{
										               iconCls: 'icon-user-add',
										               text: 'Сохранить',
										               handler: function(){
					                                        form = this.ownerCt.ownerCt.getForm();
					                                        form.submit({url:form.save_url, waitMsg:'Saving Data...', submitEmptyText: true, 
					                                        	success: function(form,action) {        
					                                        		form.ownerCt.findParentByType('xinstancecontainer').ids={'id':action.result.account_id};
					                                        	
					                                        	Ext.Msg.alert('Данные были успешно сохранены', 'Данные были успешно сохранены' )
					                                        	form.load({url:form.url,method:form.method,params:{'id':action.result.account_id}});
					                                        	},
					                                        	failure: function(form,action) {        
						                                        	Ext.Msg.alert('Ошибка', action.result.msg )}});
										            	   //this.findParentByType('tabpanel').add(this.findParentByType('grid'))
										            	   //EBS.displayCustomForm('ebs_accountsPanel', 'subaccounts', this.findParentByType('grid'))
										            	   //self.tbFormInTabCallBack.createCallback(this, 'edit_user',null)
										            	   //EBS.displayFormInSpecTab('ebs_accountsPanel', 'subaccounts', 33, this.findParentByType('tabpanel'), this.findParentByType('grid'))
										               }
										           },{
										               //ref: '../removeBtn',
										               iconCls: 'icon-user-close',
										               text: 'Закрыть',
										               handler: function(){
										            	   EBS.closeForm(this.ownerCt.ownerCt)
										               }
										           },{
										               //ref: '../removeBtn',
										               iconCls: 'icon-moneyadd',
										               text: 'Пополнить баланс',
										               handler: function(){
										            	   EBS.closeForm(this.ownerCt.ownerCt)
										               }
										           },
										           {
										               //ref: '../removeBtn',
										               iconCls: 'icon-user-radauths',
										               text: 'История RADIUS авторизаций',
										               handler: function(){
										            	   EBS.closeForm(this.ownerCt.ownerCt)
										               }
										           },{
										               //ref: '../removeBtn',
										               iconCls: 'icon-user-radauths',
										               text: 'RADIUS сессии',
										               handler: function(){
										            	   EBS.closeForm(this.ownerCt.ownerCt)
										               }
										           },{
										               //ref: '../removeBtn',
										               iconCls: 'icon-user-money',
										               text: 'История платежей и списаний',
										               handler: function(){
										            	   EBS.closeForm(this.ownerCt.ownerCt)
										               }
										           },{
										               //ref: '../removeBtn',
										               iconCls: 'icon-user-money',
										               text: 'История изменения баланса',
										               handler: function(){
										            	   EBS.closeForm(this.ownerCt.ownerCt)
										               }
										           },{
										               //ref: '../removeBtn',
										               iconCls: 'icon-user-trafinfo',
										               text: 'Остаток предоплаченного трафика',
										               handler: function(){
										            	   EBS.closeForm(this.ownerCt.ownerCt)
										               }
										           },{
										               //ref: '../removeBtn',
										               iconCls: 'icon-user-trafinfo',
										               text: 'Остаток предоплаченного времени',
										               handler: function(){
										            	   EBS.closeForm(this.ownerCt.ownerCt)
										               }
										           }
										           ],
													reader: new Ext.data.JsonReader({
													    idProperty: 'id',          
													    root: 'records',             
													    fields: [
													        {name: 'allow_webcab', type:'boolean'},
															{name: 'house', type:'int'},
															{name: 'street', type:'int'},
															{name: 'postcode', type:'int'},
															{name: 'suspended', type:'int'},
															{name: 'id', type:'int'},
															{name: 'city', type:'int'},
															{name: 'password', type:'string'},
															{name: 'ballance', type:'float'},
															{name: 'email', type:'string'},
															{name: 'username', type:'string'},
															{name: 'entrance', type:'string'},
															{name: 'vlan', type:'int'},
															{name: 'allow_expresscards', type:'boolean'},
															{name: 'disabled_by_limit', type:'boolean'},
															{name: 'balance_blocked', type:'boolean'},
															{name: 'room', type:'string'},
															{name: 'created', type:'date', dateFormat: Date.patterns.ISO8601Long},
															{name: 'region', type:'string'},
															{name: 'credit', type:'float'},
															{name: 'ipn_status', type:'boolean'},
															{name: 'house_bulk', type:'string'},
															{name: 'fullname', type:'string'},
															{name: 'passport', type:'string'},
															{name: 'passport_given', type:'string'},
															{name: 'phone_h', type:'string'},
															{name: 'phone_m', type:'string'},
															{name: 'contactperson_phone', type:'string'},
															{name: 'comment', type:'string'},
															{name: 'row', type:'int'},
															{name: 'elevator_direction', type:'string'},
															{name: 'contactperson', type:'string'},
															{name: 'status', type:'int'},
															{name: 'passport_date', type:'string'},
															{name: 'contract' , type:'string'},
															{name: 'systemuser', type:'int'},
															{name: 'last_balance_null', type:'date', dateFormat: Date.patterns.ISO8601Long},
															{name: 'entrance_code', type:'string'},
															{name: 'private_passport_number', type:'string'},
															{name: 'allow_ipn_with_null', type:'boolean'},
															{name: 'allow_ipn_with_minus', type:'boolean'},
															{name: 'allow_ipn_with_block', type:'boolean'},
															{name: 'tariff', type:'string'},
													    ]
													}), 
												items:[
{
    xtype: 'tabpanel',
    height: '100%',
    plain: true,
    
    //autoHeight:true,
    deferredRender:false,
    defaults:{
    	hideMode:'offsets',
    },
    activeTab: 0,
    items: [
                   {
                       xtype: 'panel',
                       autoScroll: true,
                       layout: 'hbox',
                       title: 'Общее',
                       autoHeight: true,

                       items: [
                           {
                               xtype: 'container',
                               height: 817,
                               width: 412,
                               layout: 'vbox',
                               items: [
                                   {
                                    xtype: 'fieldset',
                                    width: 402,
                                    title: 'Учётные данные',
                                    items: [
					                        {
					                            xtype: 'hidden',
					                            name:'id'
					                        },{
											    xtype: 'container',
											    layout: 'hbox',
											    align: 'middle',
											    fieldLabel: 'Логин',
											    defaults:{
	    	                                        margins:'0 5 5 0',    	                                        
	    	                                    },
	    	                                    baseCls:'x-plain',
											    anchor: '100%',
											    items: [
			    	                                    {
			    	                                        xtype: 'textfield',
			    	                                        name: 'username',
			    	                                        anchor: '90%',
			    	                                        //fieldLabel: 'Логин'
			    	                                    },{
			    	                                        xtype: 'button',
			    	                                        anchor: '10%',
			    	                                        text: 'Сгенерировать',
			    	                                        handler:function(button, event){
			    	                                        	Ext.Ajax.request({
			    	                	                            params: {'action':'login'},
			    	                	                            url: '/ebsadmin/credentials/gen/',
			    	                	                            success: function (resp) {
			    	                	                                var data;
			    	                	                                data = Ext.decode(resp.responseText);
			    	                	                                if (data.success === true) {
			    	                	                                	button.findParentByType('form').getForm().findField('username').setValue(data.generated);
			    	                	                                    
			    	                	                                } else {
			    	                	                                    Ext.MessageBox.alert('Ошибка', 'Неверный запрос. ');
			    	                	                                }
			    	                	                            },
			    	                	                            failure: function () {
			    	                	                            	Ext.MessageBox.alert('Ошибка', 'Ошибка передачи данных');
			    	                	                            }
			    	                	                        });
			    	                                        }
			    	                                    }
			    	                                    ]
	    	                                    },
	    	                                    {
												    xtype: 'container',
												    layout: 'hbox',
												    align: 'middle',
												    fieldLabel: 'Пароль',
												    defaults:{
		    	                                        margins:'0 5 5 0',    	                                        
		    	                                    },
		    	                                    baseCls:'x-plain',
												    anchor: '100%',
												    items: [
			    	                                    
			    	                                    {
			    	                                        xtype: 'textfield',
			    	                                        name: 'password',
			    	                                        anchor: '100%',
			    	                                        fieldLabel: 'Пароль'
			    	                                    },{
			    	                                        xtype: 'button',
			    	                                        anchor: '10%',
			    	                                        text: 'Сгенерировать',
			    	                                        handler:function(button, event){
			    	                                        	Ext.Ajax.request({
			    	                	                            params: {'action':'password'},
			    	                	                            url: '/ebsadmin/credentials/gen/',
			    	                	                            success: function (resp) {
			    	                	                                var data;
			    	                	                                data = Ext.decode(resp.responseText);
			    	                	                                if (data.success === true) {
			    	                	                                	button.findParentByType('form').getForm().findField('password').setValue(data.generated);
			    	                	                                    
			    	                	                                } else {
			    	                	                                    Ext.MessageBox.alert('Ошибка', 'Неверный запрос. ');
			    	                	                                }
			    	                	                            },
			    	                	                            failure: function () {
			    	                	                            	Ext.MessageBox.alert('Ошибка', 'Ошибка передачи данных');
			    	                	                            }
			    	                	                        });
			    	                                        }
			    	                                    }
			    	                                    ]
		    	                                    },
					                        {
					                        	xtype: 'xdatetime',
					                            name: 'created',
					                            anchor: '100%',
					                            fieldLabel: 'Дата создания'
					                        },
					                        {
					                            xtype: 'container',
					                            forceLayout: true,
					                            layout: 'hbox',
					                            anchor: '100%',
					                            fieldLabel: 'Номер договора',
					                            pack: 'center',
					                            items: [
					                                {
					                                    xtype: 'combo',
					                                    name:'contract',
					                                    flex: 1,
				                                    
    	                                                anchor: '100%',
    	                                     		    
    	                                     		    displayField: 'template',
    	                                     		    valueField: 'template', 
    	                                     		    mode: 'remote',
    	                                     		    editable:false,
    	                                                loadingText  : 'Searching...',
    	                                                pageSize     : 25,
    	                                     		    triggerAction: 'all',
    	                                     		    typeAhead: false,
    	                                     		    // ref:
														// 'store/p',
    	                                     		    listeners:{
	                                     		        	focus:function(obj, options){
	                                     		        		
	                                     		        	},
	                                     		        	// scope:this.ownerCt,
	                                     		        	
	                                     		        },
	                                     		        
    	                                     		    store:new Ext.data.Store({
    	                                     		    	
    	                                     		    	
    	                                     		        proxy: new Ext.data.HttpProxy({
    	                                     		            url: '/ebsadmin/contracttemplate/',
    	                                     		            method:'POST',
    	                                     		            
    	                                     		        }),
    	                                     		        
    	                                     		        reader: new Ext.data.JsonReader({
    	                                     		        	totalProperty: 'totalCount',
    	                                     		            root: 'records'
    	                                     		        }, [{
    	                                     		            name: 'template'
    	                                     		        }])
    	                                     		    }),
	    	                                            
					                                },
					                                {
					                                    xtype: 'button',
					                                    text: 'Печать',
					                                    flex: 1
					                                }
					                            ]
					                        }
					                    ]
                                },
                                   {
                                       xtype: 'fieldset',
                                       height: 318,
                                       width: 402,
                                       title: 'Данные аккаунта',
                                       labelWidth: 140,
                                       items: [
                                           {
                                               xtype: 'textfield',
                                               name: 'contactperson',
                                               anchor: '100%',
                                               fieldLabel: 'Контактное лицо'
                                           },
                                           {
                                               xtype: 'textfield',
                                               name: 'contactphone',
                                               anchor: '100%',
                                               fieldLabel: 'Контактный телефон'
                                           },
                                           {
                                               xtype: 'textfield',
                                               name: 'fullname',
                                               anchor: '100%',
                                               fieldLabel: 'ФИО'
                                           },
                                           {
                                               xtype: 'textfield',
                                               name: 'email',
                                               anchor: '100%',
                                               fieldLabel: 'E-mail'
                                           },
                                           {
                                               xtype: 'textfield',
                                               name: 'phone_h',
                                               anchor: '100%',
                                               fieldLabel: 'Дом. телефон'
                                           },
                                           {
                                               xtype: 'textfield',
                                               name: 'phone_m',
                                               anchor: '100%',
                                               fieldLabel: 'Моб. телефон'
                                           },
                                           {
                                               xtype: 'textfield',
                                               name: 'passport',
                                               anchor: '100%',
                                               fieldLabel: '№ паспорта'
                                           },
                                           {
                                               xtype: 'textfield',
                                               name: 'private_passport_number',
                                               anchor: '100%',
                                               fieldLabel: 'Индив. номер'
                                           },
                                           {
                                               xtype: 'textfield',
                                               name: 'passport_given',
                                               anchor: '100%',
                                               fieldLabel: 'Паспорт выдан'
                                           },
                                           {
                                               xtype: 'datefield',
                                               name: 'passport_date',
                                               anchor: '100%',
                                               fieldLabel: 'Когда'
                                           }
                                       ]
                                   },
                                   {
                                       xtype: 'fieldset',
                                       height: 351,
                                       width: 402,
                                       title: 'Адрес',
                                       items: [
                                               {
												    xtype: 'xcombocity',
												    name: 'city',
												    hiddenName: "city",
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
                   	                            xtype: 'textfield',
                   	                            name: 'region',
                   	                            anchor: '100%',
                   	                            fieldLabel: 'Подъезд'
                   	                        },
                   	                        {
                   	                            xtype: 'textfield',
                   	                            name: 'postcode',
                   	                            anchor: '100%',
                   	                            fieldLabel: 'Район'
                   	                        },
                   	                        {
                                                   xtype: 'xcombostreet',
                                                   name: 'street',
                                                   //id:'street',
                                                   hiddenName: "street",
                                                   anchor: '100%',
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
                                                   //id:'house',
                                                   hiddenName: "house",
                                                   anchor: '100%',
                                                   fieldLabel: 'Дом'
                                               },
                   	                        {
                   	                            xtype: 'textfield',
                   	                            name: 'house_bulk',
                   	                            anchor: '100%',
                   	                            fieldLabel: 'Корпус'
                   	                        },
                   	                        {
                   	                            xtype: 'textfield',
                   	                            name: 'entrance_code',
                   	                            anchor: '100%',
                   	                            fieldLabel: 'Код домофона'
                   	                        },
                   	                        {
                   	                            xtype: 'textfield',
                   	                            name: 'row',
                   	                            anchor: '100%',
                   	                            fieldLabel: 'Этаж'
                   	                        },
                   	                        {
                   	                            xtype: 'textfield',
                   	                            name: 'elevator_direction',
                   	                            anchor: '100%',
                   	                            fieldLabel: 'Направление от лифта'
                   	                        },
                   	                        {
                   	                            xtype: 'textfield',
                   	                            name: 'room',
                   	                            anchor: '100%',
                   	                            fieldLabel: 'Квартира'
                   	                        },
                   	                        {
                   	                            xtype: 'textfield',
                   	                            anchor: '100%',
                   	                            fieldLabel: 'Подъезд'
                   	                        }
                   	                        ]
                                   }
                               ]
                           },
                           {
                               xtype: 'container',
                               height: 1000,
                               width: 700,
                               layout: 'vbox',
                               items: [
                                   {
                                       xtype: 'container',
                                       height: 105,
                                       width:'100%',
                                       layout: 'hbox',
                                       flex: 1,
                                       items: [
                                           {
                                               xtype: 'fieldset',
                                               height: 104,
                                               width: 291,
                                               padding: '',
                                               title: 'Баланс',
                                               items: [
                                                       {
                                                           xtype: 'textfield',
                                                           name: 'ballance',
                                                           anchor: '100%',
                                                           disabled:true,
                                                           fieldLabel: 'Баланс'
                                                       },
                                                       {
                                                           xtype: 'textfield',
                                                           name: 'credit',
                                                           anchor: '100%',
                                                           fieldLabel: 'Кредит'
                                                       }
                                                   ]
                                           },
                                           {
                                               xtype: 'fieldset',
                                               height: 105,
                                               width: 394,
                                               title: 'Параметры',
                                               items: [
           					                        {
                                                        xtype: 'xcomboaccountstatus',
                                                        name: 'status',
                                                        hiddenName: "status",
                                                        anchor: '100%',
                                                        fieldLabel: 'Статус',
                                                       
                                                    },
                                                    {
                                                        xtype: 'xcombosystemuser',
                                                        name: 'systemuser',
                                                        hiddenName: "systemuser",
                                                        anchor: '100%',
                                                        fieldLabel: 'Персональный менеджер'
                                                    }
        					                    ]
                                           }
                                       ]
                                   },
                                   {
                                	 xtype:'fieldset',
                                	 title:'Информация',
                                	 
                                	 items:[
                                	        {
                                	        	xtype:'displayfield',
                                	        	fieldLabel:'Тарифный план',
                                	        	name:'tariff'
                                	        }
                                	        ]
                                   },
                                   {
									   xtype:'xsubaccountsgrid',
									   //autoHeight:true,
									   title:'Субаккаунты',
									   authHeight: true,
									   height:300,
									   autoWidth:true,
									   autoScroll:true,
									   tbar: [{
										    icon: media+'icons/16/arrow_refresh.png',
									        text: 'Обновить',
									        handler: function(){
									     	   //this.findParentByType('tabpanel').add(this.findParentByType('grid'))
									     	   //EBS.displayCustomForm('ebs_accountsPanel', 'subaccounts', this.findParentByType('grid'))
									     	   //self.tbFormInTabCallBack.createCallback(this, 'edit_user',null)
									     	   //var account_id;
									     	   
									     	  //account_id = this.findParentByType('xinstancecontainer').parent_id;
									        	this.ownerCt.ownerCt.store.load();
									     	   //EBS.displayFormInSpecTab('ebs_accountsPanel', 'subaccounts', {'account_id':account_id, 'id':null}, this.findParentByType('tabpanel'), this.findParentByType('grid'))
									        }
									    },{
								        iconCls: 'icon-user-add',
								        text: 'Добавить',
								        handler: function(){
								     	   //this.findParentByType('tabpanel').add(this.findParentByType('grid'))
								     	   //EBS.displayCustomForm('ebs_accountsPanel', 'subaccounts', this.findParentByType('grid'))
								     	   //self.tbFormInTabCallBack.createCallback(this, 'edit_user',null)
								     	   var account_id;
								     	   //alert(this.findParentByType('xinstancecontainer').ids.id);
								     	  account_id = this.findParentByType('xinstancecontainer').ids.id;
								     	  if (!account_id){
								     		  Ext.Msg.alert('Действие не может быть выполнено','Сохраните аккаунт.');
								     	  }else{
								     		  EBS.displayFormInSpecTab('ebs_accountsPanel', 'subaccounts', {'account_id':account_id, 'id':null}, this.findParentByType('tabpanel'), this.findParentByType('grid'))
								     	  }
								     	  //EBS.displayFormInSpecTab('ebs_accountsPanel', 'subaccounts', {'account_id':account_id, 'id':null}, this.findParentByType('tabpanel'), this.findParentByType('grid'))
								        }
								    },{
								        iconCls: 'icon-user-edit',
								        text: 'Редактировать',
								        handler: function(){
								     	   //this.findParentByType('tabpanel').add(this.findParentByType('grid'))
								     	   //EBS.displayCustomForm('ebs_accountsPanel', 'subaccounts', this.findParentByType('grid'))
								     	   //self.tbFormInTabCallBack.createCallback(this, 'edit_user',null)
								     	   var id;
								     	   var account_id;
								     	   account_id = this.findParentByType('form').getForm().findField('id').value;
								     	   id = this.findParentByType('grid').selModel.selections.items[0].id;
								     	   EBS.displayFormInSpecTab('ebs_accountsPanel', 'subaccounts', {'account_id':account_id, 'id':id}, this.findParentByType('tabpanel'), this.findParentByType('grid'))
								     	   //EBS.displayForm('ebs_accountsPanel', 'subaccounts', {'account_id':account_id, 'id':id}, this.findParentByType('grid'))
								        }
								    },{
								        //ref: '../removeBtn',
								        iconCls: 'icon-user-delete',
								        text: 'Remove',
								        disabled: false,
								        handler: function(){
								        	id = this.findParentByType('grid').selModel.selections.items[0].id;
								        	store = this.findParentByType('grid').store;
								        	if(id){
								        		Ext.Ajax.request({
		            	                            params: {id: id},
		            	                            url: '/ebsadmin/subaccounts/delete/',
		            	                            success: function (resp) {
		            	                                var data;
		            	                                data = Ext.decode(resp.responseText);
		            	                                if (data.success === true) {
		            	                                    
		            	                                	store.load();
		            	                                    
		            	                                } else {
		            	                                    Ext.MessageBox.alert('Ошибка', 'Субаккаунт не удалён. '+data.msg);
		            	                                }
		            	                            },
		            	                            failure: function () {
		            	                            	Ext.MessageBox.alert('Ошибка', 'Субаккаунт не удалён. ');
		            	                            }
		            	                        });
								        	}
								        }
								    },{
								        iconCls: 'icon-user-add',
								        text: 'Добавить подключаемую услугу',
								        handler: function(){
								     	   //this.findParentByType('tabpanel').add(this.findParentByType('grid'))
								     	   //EBS.displayCustomForm('ebs_accountsPanel', 'subaccounts', this.findParentByType('grid'))
								     	   //self.tbFormInTabCallBack.createCallback(this, 'edit_user',null)
								     	   var account_id;
								     	   
								     	   account_id = this.findParentByType('tabpanel').items.items[0].getForm().findField('id').value;
								     	   
								     	   EBS.displayFormInSpecTab('ebs_accountsPanel', 'subaccounts', {'account_id':account_id, 'id':null}, this.findParentByType('tabpanel'), this.findParentByType('grid'))
								        }
								    }],
								},
								{
				                    xtype: 'xaccountaddonservicesgrid',
				                    authHeight: true,
				                    autoWidth:true,
				                    autoScroll:true,
				                    height:300,
				                    title: 'Подключаемые услуги',
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
								     	   
									     	   account_id = this.findParentByType('xinstancecontainer').parent_id;
								     	   EBS.displayForm('ebs_accountsPanel', 'accountaddonservice',{'account_id':account_id,id:null}, this.findParentByType('grid'))
								     	   
								        }
								    },{
								        iconCls: 'icon-user-edit',
								        text: 'Редактировать',
								        handler: function(){
								     	   var id;
								     	   var account_id;
								     	   account_id = this.findParentByType('xinstancecontainer').parent_id;
								     	   id = this.findParentByType('grid').selModel.selections.items[0].id;
								     	   EBS.displayForm('ebs_accountsPanel', 'accountaddonservice',{'account_id':account_id,id:id}, this.findParentByType('grid'))
								        }
								    },{
								        //ref: '../removeBtn',
								        iconCls: 'icon-user-delete',
								        text: 'Отключить',
								        disabled: true,
								        handler: function(){
								     	   
								        }
								    }],
				                    
				                },
				                {
				                	xtype:'container',
				                	layout:'hbox',
				                	height:300,
				                	width:'100%',
				                	items:[
					                {
					                    xtype: 'xaccounttariffsgrid',
					                    authHeight: true,
					                    width: '50%',
					                    title: 'Тарифные планы',
					                    height:300,
					                    
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
									     	   account_id = this.findParentByType('xinstancecontainer').parent_id;
									     	   EBS.displayForm('ebs_accountsPanel', 'tpchange',{'account_id':account_id,id:null}, this.findParentByType('grid'))
									     	   
									        }
									    },{
									        iconCls: 'icon-user-edit',
									        text: 'Редактировать',
									        handler: function(){
									     	   var id;
									     	   var account_id;
									     	   account_id = this.findParentByType('xinstancecontainer').parent_id;
									     	   id = this.findParentByType('grid').selModel.selections.items[0].id;
									     	   EBS.displayForm('ebs_accountsPanel', 'tpchange',{'account_id':account_id,id:id}, this.findParentByType('grid'))
									        }
									    },{
									        //ref: '../removeBtn',
									        iconCls: 'icon-delete',
									        text: 'Удалить',
									        //disabled: true,
									        ref: '../removeButton',
									        handler: function(){
									     	   
									        }
									    }],
					                    
					                },
					                {
			                            xtype: 'xdocumentsgrid',
			                            height:300,
			                            width: '50%',
			                            title: 'Документы'
			                        },
				                ]},
                           {
                               xtype: 'container',
                               layout: 'column',
                               flex: 1,
                               items: [
                                   {
                                       xtype: 'container',
                                       layout: 'form',
                                       items: [
                                           {
                                               xtype: 'textarea',
                                               height: 113,
                                               width: 300,
                                               name: 'comment',
                                               fieldLabel: 'Комментарий'
                                           }
                                       ]
                                   },
                                   {
                                       xtype: 'fieldset',
                                       height: 112,
                                       width: 574,
                                       title: 'Опции',
                                       items: [
                                           {
                                               xtype: 'checkbox',
                                               boxLabel: 'Разрешить активацию подключаемых услуг',
                                               anchor: '100%',
                                               fieldLabel: 'Label',
                                               hideLabel: true
                                           },
                                           {
                                               xtype: 'checkbox',
                                               boxLabel: 'Разрешить вход в веб-кабинет',
                                               anchor: '100%',
                                               fieldLabel: 'Label',
                                               hideLabel: true
                                           }
                                       ]
                                   }
                               ]
                           }
                       ]
                   },
                   
               ]
},{
    xtype: 'panel',
    autoScroll: true,
    layout: 'column',
    title: 'Информация',
    items: [
        {
            xtype: 'container',
            height: 352,
            width: 367,
            layout: 'hbox',
            pack: 'center',
            items: [
                {
                    xtype: 'fieldset',
                    stateful: true,
                    width: 366,
                    animCollapse: true,
                    title: 'Юр. лицо',
                    items: [
                        {
                            xtype: 'textfield',
                            name: 'organization_name',
                            anchor: '100%',
                            fieldLabel: 'Название'
                        },
                        {
                            xtype: 'textfield',
                            name: 'uraddress',
                            anchor: '100%',
                            fieldLabel: 'Юр. адрес'
                        },
                        {
                            xtype: 'textfield',
                            name: 'okpo',
                            anchor: '100%',
                            fieldLabel: 'ОКПО'
                        },
                        {
                            xtype: 'textfield',
                            name: 'unp',
                            anchor: '100%',
                            fieldLabel: 'УНП'
                        },
                        {
                            xtype: 'textfield',
                            name: 'organization_phone',
                            anchor: '100%',
                            fieldLabel: 'Телефон'
                        },
                        {
                            xtype: 'textfield',
                            name: 'organization_fax',
                            anchor: '100%',
                            fieldLabel: 'Факс'
                        },
                        {
                            xtype: 'textfield',
                            name: 'organization_kpp',
                            anchor: '100%',
                            fieldLabel: 'КПП'
                        },
                        {
                            xtype: 'textfield',
                            name: 'kor_s',
                            anchor: '100%',
                            fieldLabel: 'Корр. счёт'
                        },
                        {
                            xtype: 'textfield',
                            name: 'bank_name',
                            anchor: '100%',
                            fieldLabel: 'Банк'
                        },
                        {
                            xtype: 'textfield',
                            name: 'bankcode',
                            anchor: '100%',
                            fieldLabel: 'Код банка'
                        },
                        {
                            xtype: 'textfield',
                            name: 'rs',
                            anchor: '100%',
                            fieldLabel: 'Расчётный счёт'
                        },
                        {
                            xtype: 'textfield',
                            name: 'currency',
                            anchor: '100%',
                            fieldLabel: 'Валюта'
                        }
                    ]
                }
            ]
        },
        {
            xtype: 'container',
            height: 560,
            width: 739,
            layout: 'vbox',
            flex: 1,
            items: [
                {
                    xtype: 'xsuspendedperiodgrid',
                    height: 241,
                    title: 'Периоды паузы',
                    
                },
                {
                    xtype: 'xaccounthardwaregrid',
                    height: 241,
                    title: 'Оборудование на руках',
                    
                }
            ]
        }
    ]
}
]}]}]};
                                        
    /*EBS.forms.ebs_accountsPanel.edit_user_submitAction =  function(object, event){
        //form = object.ownerCt;
        //console.log(form);
    }*/
    
    EBS.forms.ebs_accountsPanel.suspendedperiod = {
    	    xtype: 'form',
    	    height: 150,
    	    width: 610,
    	    layout: 'fit',
    	    url:'/ebsadmin/suspendedperiod/get/',
    	    save_url:'/ebsadmin/suspendedperiod/set/',
    	    method:'POST',
    	    plugins:['msgbus'],
    	    closeForm:function(instance_id)
    	    {
    	    	owner = this.ownerCt;
    	    	owner.hide().destroy();
    	    	delete EBS.windows[owner.id];
    	    },
    	    listeners:{
    			'render': function(){
    				
    				this.getForm().findField('account').setValue(this.findParentByType('xinstancewindow').ids.account_id);
    			}
    		},
    	    
    	    
    	    reader: new Ext.data.JsonReader({
			    idProperty: 'id',          
			    root: 'records',             
			    fields: [{name: 'id', type:'int'},
			             {name: 'account', type:'int'},
  		        		{name: 'activated_by_account', type:'bool'},
  		        		
  		        		{name: 'start_date', type: 'date', dateFormat: Date.patterns.ISO8601Long},
  		        		{name: 'end_date',  type: 'date', dateFormat: Date.patterns.ISO8601Long},
  		        		],
			      
			}), 
    	    padding: 5,
    	    windowTitle: 'Параметры паузы',
    	    items: [
    	        {
    	            xtype: 'fieldset',
    	            height: 116,
    	            width:'100%',
    	            title: 'Параметры паузы',
    	            items: [
    	                {
    	                    xtype: 'hidden',
    	                    name:'account'
    	                },{
    	                    xtype: 'hidden',
    	                    name:'id'
    	                },{
    	                    xtype: 'combo',
    	                    anchor: '100%',
    	                    fieldLabel: 'Тип паузы'
    	                },
    	                {
    	                    xtype: 'compositefield',
    	                    anchor: '100%',
    	                    fieldLabel: 'Период',
    	                    items: [
    	                        {
    	                            xtype: 'displayfield',
    	                            value: 'c',
    	                            
    	                            fieldLabel: 'Label'
    	                        },
    	                        {
    	                            xtype: 'xdatetime',
    	                            flex: 1,
    	                            name:'start_date'
    	                        },
    	                        {
    	                            xtype: 'displayfield',
    	                            value: 'по',
    	                            
    	                            fieldLabel: 'Label'
    	                        },
    	                        {
    	                            xtype: 'xdatetime',
    	                            flex: 1,
    	                            name:'end_date'
    	                        }
    	                    ]
    	                }
    	            ]
    	        }
    	    ]
    	}

    EBS.forms.ebs_accountsPanel.suspendedperiod_submitAction =  function(object, event, form, window){
    	
    	
 	    f=form;
 	    pub = function(){window.items.items[0].publish('ebs.suspendedperiod.change', 'msg');	}
        
        form.submit({url:form.save_url, waitMsg:'Saving Data...', submitEmptyText: true, success: function(obj,action) {        
        	
        	pub();
        	window.hide().destroy()
            delete EBS.windows[window.id];

        },failure: function(form,action) {        
         	Ext.Msg.alert('Ошибка', action.result.msg )}});
    }
   //win.show();
    EBS.forms.ebs_accountsPanel.accountaddonservice = {
    	    xtype: 'form',
    	    height: 243,
    	    width: 620,
    	    layout: 'fit',
    	    padding: 5,
    	    windowTitle: 'Подключаемая улуга',
    	    url:'/ebsadmin/accountaddonservices/get/',
    	    save_url:'/ebsadmin/accountaddonservices/set/',
    	    method:'POST',
    	    plugins:['msgbus'],
    	    closeForm:function(instance_id)
    	    {
    	    	owner = this.ownerCt;
    	    	owner.hide().destroy();
    	    	delete EBS.windows[owner.id];
    	    },

		    reader: new Ext.data.JsonReader({
			    idProperty: 'id',          
			    root: 'records',             
			    fields: [{name: 'temporary_blocked_checkbox', type:'boolean'},
			             {name: 'account', type:'int'},
			             {name: 'subaccount', type:'int'},
			             {name: 'service', type:'int'},
			             {name: 'deactivated', type:'date', dateFormat: Date.patterns.ISO8601Long},
			             {name: 'activated', type:'date', dateFormat: Date.patterns.ISO8601Long},
			             {name: 'id', type:'int'},
			             ]
			      
			}), 
    		loadForm:function(instance_id)
    	    {
    	    	this.load({'id':instance_id});
    	    },
    	    items: [
    	        {
    	            xtype: 'tabpanel',
    	            deferredRender:false,
                    defaults:{
                    	hideMode:'offsets',
                    },
    	            height: 277,
    	            width: 550,
    	            activeTab: 0,
    	            items: [
    	                {
    	                    xtype: 'panel',
    	                    padding: 10,
    	                    title: 'Параметры',
    	                    items: [
    	                        {
    	                            xtype: 'fieldset',
    	                            autoHeight: true,
    	                            title: 'Параметры',
    	                            items: [
    	                                {
    	                                    xtype: 'hidden',
    	                                    name:'id',
    	                                },{
    	                                    xtype: 'hidden',
    	                                    name:'account',
    	                                },{
    	                                    xtype: 'hidden',
    	                                    name:'subaccount',
    	                                },{
    	                                    xtype: 'xaddonservicescombo',
    	                                    anchor: '100%',
    	                                    name:'service',
    	                                    hiddenName:'service',
    	                                    valueField:'id',
    	                                    fieldLabel: 'Услуга'
    	                                },
    	                                {
    	                                    xtype: 'checkbox',
    	                                    boxLabel: 'Временно отключить услугу',
    	                                    anchor: '100%',
    	                                    name:'temporary_blocked_checkbox',
    	                                    fieldLabel: 'Пауза'
    	                                },
    	                                {
    	                                    xtype: 'container',
    	                                    layout: 'hbox',
    	                                    baseCls:'x-plain',
    	                                    layout:'hbox',
    	                                    layoutConfig: {
    	                                        padding: 0
    	                                    },
    	                                    defaults:{
    	                                        margins:'0 5 0 0',    	                                        
    	                                    },
    	                                    fieldLabel: 'Действие',
    	                                    align: 'middle',
    	                                    items: [
    	                                        {
    	                                            xtype: 'displayfield',
    	                                            value: 'с  '
    	                                        },
    	                                        {
    	                                            xtype: 'xdatetime',
    	                                            //width: 174
    	                                            name:'activated'
    	                                        },
    	                                        {
    	                                            xtype: 'displayfield',
    	                                            value: 'по'
    	                                        },
    	                                        {
    	                                            xtype: 'xdatetime',
    	                                            //width: 184
    	                                            name:'deactivated'
    	                                        }
    	                                    ]
    	                                },
    	                                {
    	                                    xtype: 'textfield',
    	                                    anchor: '100%',
    	                                    fieldLabel: 'Особая цена',
    	                                    name:'price_cost'
    	                                }
    	                            ]
    	                        }
    	                    ]
    	                },
    	                {
    	                    //xtype: 'panel',
    	                    //layout: 'fit',
    	                    //padding: 10,
    	                    title: 'Комментарий',
    	                    items: [
    	                        {
    	                            xtype: 'container',
    	                            layout: 'form',
    	                            items: [
    	                               
    	                            ]
    	                        }
    	                    ]
    	                },
    	                {
    	                    xtype: 'panel',
    	                    layout: 'fit',
    	                    title: 'История изменений',
    	                    items: [
    	                        {
    	                            xtype: 'container'
    	                        }
    	                    ]
    	                }
    	            ]
    	        }
    	    ]
    	}
    EBS.forms.ebs_accountsPanel.accountaddonservice_submitAction =  function(object, event, form, window){
    	
    	var acc_id;
    	acc_id = form.findField('account').getValue();
    	if (!acc_id)
    		{
    		form.findField('account').setValue(window.ids.account_id);
    		
    		
    		}
    	/*form.submit({url:form.save_url, waitMsg:'Saving Data...', submitEmptyText: false, success: function(form,action) {        
            	form.closeForm()},
            	
    	})*/
    	
    	//form = this.ownerCt.ownerCt.getForm();
 	    f=form;
 	    pub = function(){window.items.items[0].publish('ebs.accountaddonservice.change', 'msg');	}
        
        form.submit({url:form.save_url, waitMsg:'Saving Data...', submitEmptyText: true, success: function(obj,action) {        
        	
        	pub();
        	form.closeForm()
        },failure: function(form,action) {        
         	Ext.Msg.alert('Ошибка', action.result.msg )}});
    }
    
    EBS.forms.ebs_accountsPanel.tpchange = {
    	    xtype: 'form',
    	    height: 156,
    	    width: 398,
    	    padding:10,
    	    plugins:['msgbus'],
    	    url:'/ebsadmin/tpchange/',
    	    save_url:'/ebsadmin/tpchange/set/',
    	    method:'POST',
    	    loadForm:function(instance_id)
    	    {
    	    	this.load({'id':instance_id});
    	    },
    	    closeForm:function(instance_id)
    	    {
    	    	owner = this.ownerCt;
    	    	owner.hide().destroy();
    	    	delete EBS.windows[owner.id];
    	    },
    	    
        	
    	    reader: new Ext.data.JsonReader({
			    idProperty: 'id',          
			    root: 'records',             
			    fields: [
			        {name: 'periodical_billed', type:'boolean'},
					{name: 'tarif', type:'int'},
					{name: 'account', type:'int'},
					{name: 'datetime', type:'date', dateFormat: Date.patterns.ISO8601Long},
					{name: 'id', type:'int'},
			    ]
			}), 
    	    windowTitle: 'Смена тарифного плана',
    	    items: [
    	        {
    	            xtype: 'fieldset',
    	            height: 92,
    	            title: 'Параметры',
    	            items: [
    	                {
    	                    xtype: 'xcombotariff',
    	                    fieldLabel: 'Новый тариф',
    	                    name:'tarif',
    	                    anchor: '100%',
    	                },
    	                {
    	                    xtype: 'xdatetime',
    	                    name: 'datetime',
    	                    anchor: '100%',
    	                    fieldLabel: 'Дата перехода'
    	                },
    	                {
    	                    xtype: 'hidden',
    	                    name: 'id',
    	                },
    	                {
    	                    xtype: 'hidden',
    	                    name: 'account',
    	                    listeners: {
        	                    'render' : function(n){
        	                    	//alert(this.findParentByType('xinstancecontainer').parent_id);
        	                    	this.setValue(this.findParentByType('xinstancewindow').parent_id);
        	                    	//alert(this.value);
        	                    }
        	                    }
    	                }
    	            ]
    	        }
    	    ],

    	    
    	};

    EBS.forms.ebs_accountsPanel.tpchange_submitAction =  function(object, event, form, window){
    	
    	
 	    f=form;
 	    pub = function(){window.items.items[0].publish('ebs.accounttarif.change', 'msg');	}
        
        form.submit({url:form.save_url, waitMsg:'Saving Data...', submitEmptyText: true, success: function(obj,action) {        
        	
        	pub();
        	form.closeForm()
        },failure: function(form,action) {        
         	Ext.Msg.alert('Ошибка', action.result.msg )}});
    }
    
    EBS.forms.ebs_accountsPanel.edit_credit = {
                                        xtype: 'form',
                                        id: 'account-credit',
                                        windowTitle:'Платёж',
                                        layout: 'fit',
                                        buttonAlign:'center',
                                        padding:5,
                                        //autoHeight:true,
                                        items:[
                                               {
                                                    xtype: 'fieldset',
                                                    autoHeight: false,
                                                    autoWidth: false,
                                                    height: 231,
                                                    title: 'Параметры платежа',
                                                    labelWidth: 150,
                                                    items: [{
                                                    		xtype:'xtrtypecombo',
                                                    		name:'transaction_type_id',
                                                    		id:'transaction_type_id',
                                                    	},
                                                        
                                                        {
                                                            xtype: 'numberfield',
                                                            name: 'summ',
                                                            anchor: '100%',
                                                            fieldLabel: 'Сумма'
                                                        },
                                                        {
                                                            xtype: 'textfield',
                                                            name: 'document',
                                                            anchor: '100%',
                                                            fieldLabel: 'Документ'
                                                        },
                                                        {
                                                            xtype: 'textfield',
                                                            name: 'description',
                                                            anchor: '100%',
                                                            fieldLabel: 'Комментарий'
                                                        },
                                                        {
                                                            xtype: 'xdatetime',
                                                            name: 'created',
                                                            anchor: '100%',
                                                            fieldLabel: 'Дата'
                                                        },
                                                        {
                                                            xtype: 'checkbox',
                                                            boxLabel: 'Да',
                                                            anchor: '100%',
                                                            fieldLabel: 'Обещанный платёж'
                                                        },
                                                        {
                                                            xtype: 'compositefield',
                                                            anchor: '100%',
                                                            fieldLabel: 'Истекает',
                                                            items: [
                                                                {
                                                                    xtype: 'xdatetime',
                                                                    width: 212
                                                                },
                                                                {
                                                                    xtype: 'checkbox',
                                                                    boxLabel: 'Никогда',
                                                                    fieldLabel: 'Label'
                                                                }
                                                            ]
                                                        }
                                                        
                                                    ]
                                                }],
                                                buttons:[                                 
                                                        {
                                                            xtype: 'button',
                                                            width: 131,
                                                            text: 'Зачислить'
                                                        },
                                                        {
                                                            xtype: 'button',
                                                            icon: media+'icons/16/printer.png',
                                                            width: 157,
                                                            text: 'Печать'
                                                        },
                                                        {
                                                            xtype: 'button',
                                                            width: 158,
                                                            text: 'Закрыть',
                                                            handler:{
                                                            	//EBS.closeForm(this);
                                                            }
                                                        }
                                                   
                                                
                                                
                                                
                                            ]
    
                                        
    									
                                      }
    EBS.forms.ebs_accountsPanel.edit_credit_submitAction =  function(object, event){
        form = object.ownerCt;
        //console.log(form);
    }
/* EOF ACCOUNTS FORMS*/

/* Subaccounts edit*/
    EBS.forms.ebs_accountsPanel.subaccounts = {
    	    xtype: 'form',
    	    windowTitle:'Редактирование субаккаунта',
    	    url:'/ebsadmin/subaccounts/get/',
    	    save_url:'/ebsadmin/subaccounts/set/',
    	    method:'POST',
    	    //autoHeight:true,
    	    //padding:10,
    	    align:'center',
    	    //frame:true,
    	    layout: 'auto',
    	    autoScroll: true,
    	    bodyStyle:'padding:0 30% 0 30%',
    	    plugins:['msgbus'],
     	    tbar: [{
               iconCls: 'icon-user-add',
               text: 'Сохранить',
               handler: function(){
            	   form = this.ownerCt.ownerCt.getForm();
            	   f=this.ownerCt.ownerCt;
            	   pub = function(){f.publish('ebs.subaccounts.change', 'msg');	}
                   
                   form.submit({url:form.save_url, waitMsg:'Saving Data...', submitEmptyText: true, success: function(obj,action) {        
                   	Ext.Msg.alert('Данные были успешно сохранены', 'Данные были успешно сохранены' );
                   	pub();
                   },failure: function(form,action) {        
                    	Ext.Msg.alert('Ошибка', action.result.msg )}});
                   
            	   //this.findParentByType('tabpanel').add(this.findParentByType('grid'))
            	   //EBS.displayCustomForm('ebs_accountsPanel', 'subaccounts', this.findParentByType('grid'))
            	   //self.tbFormInTabCallBack.createCallback(this, 'edit_user',null)
            	   //EBS.displayFormInSpecTab('ebs_accountsPanel', 'subaccounts', 33, this.findParentByType('tabpanel'), this.findParentByType('grid'))
               }
           },{
               iconCls: 'icon-user-add',
               text: 'Сохранить как копию',
               handler: function(){
            	   form = this.ownerCt.ownerCt.getForm();
            	   f=this.ownerCt.ownerCt;
            	   pub = function(){f.publish('ebs.subaccounts.change', 'msg');	}
                   form.findField('id').setValue('');
                   form.submit({url:form.save_url, waitMsg:'Saving Data...', submitEmptyText: true, success: function(obj,action) {        
                   	Ext.Msg.alert('Данные были успешно сохранены', 'Данные были успешно сохранены' );
                   	pub();
                   },failure: function(form,action) {        
                    	Ext.Msg.alert('Ошибка', action.result.msg )}});
                   
            	   //this.findParentByType('tabpanel').add(this.findParentByType('grid'))
            	   //EBS.displayCustomForm('ebs_accountsPanel', 'subaccounts', this.findParentByType('grid'))
            	   //self.tbFormInTabCallBack.createCallback(this, 'edit_user',null)
            	   //EBS.displayFormInSpecTab('ebs_accountsPanel', 'subaccounts', 33, this.findParentByType('tabpanel'), this.findParentByType('grid'))
               }
           },{
               //ref: '../removeBtn',
               iconCls: 'icon-user-close',
               text: 'Закрыть',
               //disabled: true,
               handler: function(){
            	   winCmp = this.ownerCt.ownerCt.ownerCt;
                   winCmp.hide().destroy();
                   delete EBS.windows[winCmp.id];
               }
           }],
			reader: new Ext.data.JsonReader({
			    idProperty: 'id',          
			    root: 'records',             
			    fields: [
			        {name: 'switch_port',  type:'int'},
			    	
			    	{name: 'ipn_speed', type:'string'},
			    	{name: 'allow_dhcp', type:'string'},
			    	{name: 'vpn_ip_address', type:'string'},
			    	{name: 'allow_dhcp_with_block', type:'boolean'},
			    	{name: 'ipn_sleep', type:'boolean'},
			    	{name: 'speed', type:'string'},
			    	{name: 'id',  type:'int'},
			    	{name: 'allow_addonservice', type:'boolean'},
			        {name: 'ipn_mac_address', type:'string'},
		             {name: 'allow_dhcp_with_minus', type:'boolean'},
		             {name: 'ipn_enabled', type:'boolean'},
		             
		             {name: 'ipv4_vpn_pool',  type:'int'},
		             {name: 'nas',  type:'int'},
		             {name: 'ipv4_ipn_pool',  type:'int'},
		             {name: 'subaccount_id',  type:'int'},
		             {name:  'allow_ipn_with_null', type:'boolean'},
		             {name: 'allow_ipn_with_minus', type:'boolean'},
		             {name: 'username', type:'string'},
		             {name: 'allow_dhcp_with_null', type:'boolean'},
		             {name: 'associate_pptp_ipn_ip', type:'boolean'},
		             {name: 'ipn_ip_address', type:'string'},
		             {name: 'associate_pppoe_ipn_mac', type:'boolean'},
		             {name: 'allow_ipn_with_block', type:'boolean'},
		             {name: 'vlan',  type:'int'},
		             {name: 'allow_mac_update', type:'boolean'},
		             {name: 'allow_vpn_with_null', type:'boolean'},
		             {name: 'ipn_ipv6_ip_address', type:'string'},
		             {name: 'vpn_speed', type:'string'},
		             {name: 'allow_vpn_with_minus', type:'boolean'},
		             {name: 'password', type:'string'},
		             {name: 'ipn_added', type:'boolean'},
		             {name: 'account', type:'string'},
		             
		             {name: 'switch',  type:'int'},
		             {name: 'allow_vpn_with_block', type:'boolean'},
		             {name: 'need_resync', type:'boolean'},
		             {name: 'vpn_ipv6_ip_address', type:'string'},
			             ]
			}), 
    	    //padding: 10,
    	    //align: 'stretchmax',
    	    //padding: 10,
    	    items: [
    	            {
    	            	xtype:'hidden',
    	            	name:'id',
    	            },{
    	            	xtype:'hidden',
    	            	name:'account',
    	            	listeners: {
    	                    'render' : function(n){
    	                    	//alert(this.findParentByType('xinstancecontainer').parent_id);
    	                    	this.setValue(this.findParentByType('xinstancecontainer').ids.account_id);
    	                    	//alert(this.value);
    	                    }
    	                    }
    	            },
    	           
    	                    {
    	                        xtype: 'container',
    	                        autoHeight: true,
    	                        width: '100%',
    	                        
    	                        items: [
    	                            {
    	                                xtype: 'fieldset',
    	                                autoHeight: true,
    	                                width: 533,
    	                                padding: '10px',
    	                                title: 'Привязка к оборудованию',
    	                                items: [
    	                                    {
    	                                        xtype: 'xcombonas',
    	                                        
    	                                        name: 'nas',
    	                                        hiddenName: 'nas',
    	                                        anchor: '100%',
    	                                        fieldLabel: 'Сервер доступа'
    	                                    },
    	                                    {
    	                                        xtype: 'xcomboswitch',
    	                                        name: 'switch',
    	                                        hiddenName: 'switch',
    	                                        anchor: '100%',
    	                                        fieldLabel: 'Коммутатор'
    	                                    },
    	                                    {
    	                                        xtype: 'textfield',
    	                                        name: 'switch_port',
    	                                        anchor: '100%',
    	                                        fieldLabel: 'Порт'
    	                                    },
    	                                    {
    	                                        xtype: 'textfield',
    	                                        name: 'vlan',
    	                                        anchor: '100%',
    	                                        fieldLabel: 'VLAN'
    	                                    }
    	                                ]
    	                            }
    	                        ]
    	                    },
    	                    {
    	                        xtype: 'container',
    	                        autoWidth: true,
    	                        width: 757,
    	                        items: [
    	                            {
    	                                xtype: 'fieldset',
    	                                width: 533,
    	                                title: 'RADIUS авторизация',
    	                                collapsible:true,
    	                                items: [
											{
											    xtype: 'container',
											    layout: 'hbox',
											    align: 'middle',
											    fieldLabel: 'Логин',
											    defaults:{
	    	                                        margins:'0 5 5 0',    	                                        
	    	                                    },
	    	                                    baseCls:'x-plain',
											    anchor: '100%',
											    items: [
			    	                                    {
			    	                                        xtype: 'textfield',
			    	                                        name: 'username',
			    	                                        anchor: '90%',
			    	                                        //fieldLabel: 'Логин'
			    	                                    },{
			    	                                        xtype: 'button',
			    	                                        anchor: '10%',
			    	                                        text: 'Сгенерировать',
			    	                                        handler:function(button, event){
			    	                                        	Ext.Ajax.request({
			    	                	                            params: {'action':'login'},
			    	                	                            url: '/ebsadmin/credentials/gen/',
			    	                	                            success: function (resp) {
			    	                	                                var data;
			    	                	                                data = Ext.decode(resp.responseText);
			    	                	                                if (data.success === true) {
			    	                	                                	button.findParentByType('form').getForm().findField('username').setValue(data.generated);
			    	                	                                    
			    	                	                                } else {
			    	                	                                    Ext.MessageBox.alert('Ошибка', 'Неверный запрос. ');
			    	                	                                }
			    	                	                            },
			    	                	                            failure: function () {
			    	                	                            	Ext.MessageBox.alert('Ошибка', 'Ошибка передачи данных');
			    	                	                            }
			    	                	                        });
			    	                                        }
			    	                                    }
			    	                                    ]
	    	                                    },
	    	                                    {
												    xtype: 'container',
												    layout: 'hbox',
												    align: 'middle',
												    fieldLabel: 'Пароль',
												    defaults:{
		    	                                        margins:'0 5 5 0',    	                                        
		    	                                    },
		    	                                    baseCls:'x-plain',
												    anchor: '100%',
												    items: [
			    	                                    
			    	                                    {
			    	                                        xtype: 'textfield',
			    	                                        name: 'password',
			    	                                        anchor: '100%',
			    	                                        fieldLabel: 'Пароль'
			    	                                    },{
			    	                                        xtype: 'button',
			    	                                        anchor: '10%',
			    	                                        text: 'Сгенерировать',
			    	                                        handler:function(button, event){
			    	                                        	Ext.Ajax.request({
			    	                	                            params: {'action':'password'},
			    	                	                            url: '/ebsadmin/credentials/gen/',
			    	                	                            success: function (resp) {
			    	                	                                var data;
			    	                	                                data = Ext.decode(resp.responseText);
			    	                	                                if (data.success === true) {
			    	                	                                	button.findParentByType('form').getForm().findField('password').setValue(data.generated);
			    	                	                                    
			    	                	                                } else {
			    	                	                                    Ext.MessageBox.alert('Ошибка', 'Неверный запрос. ');
			    	                	                                }
			    	                	                            },
			    	                	                            failure: function () {
			    	                	                            	Ext.MessageBox.alert('Ошибка', 'Ошибка передачи данных');
			    	                	                            }
			    	                	                        });
			    	                                        }
			    	                                    }
			    	                                    ]
		    	                                    },
    	                                    {
    	                                        xtype: 'container',
    	                                        layout: 'hbox',
    	                                        fieldLabel: 'IPv4 VPN IP',
    	                                        align: 'middle',
    	                                        items: [
    	                                            {
    	                                                xtype: 'combo',
    	                                                name: 'vpn_ip_address',
    	                                                vtype:'IPAddress',
    	                                                value:'0.0.0.0',
    	                                                flex: 1,
    	                                                anchor: '100%',
    	                                     		    
    	                                     		    displayField: 'ipaddress',
    	                                     		    valueField: 'ipaddress', 
    	                                     		    mode: 'remote',
    	                                     		    editable:true,
    	                                                loadingText  : 'Searching...',
    	                                                pageSize     : 25,
    	                                     		    triggerAction: 'all',
    	                                     		    typeAhead: false,
    	                                     		    //ref: 'store/p',
    	                                     		    listeners:{
	                                     		        	focus:function(obj, options){
	                                     		        		pool_id=this.findParentByType('form').getForm().findField('ipv4_vpn_pool').getValue();
	                                     		        		//alert();
	                                     		        		obj.store.setBaseParam('pool_id',pool_id);
	                                     		        		if (pool_id){
	                                     		        			obj.store.load()
	                                     		        		}
	                                     		        	},
	                                     		        	//scope:this.ownerCt,
	                                     		        	
	                                     		        },
	                                     		        
    	                                     		    store:new Ext.data.Store({
    	                                     		    	ref: '../st',
    	                                     		    	param:{pool_id:function (){return this.ownerCt.ownerCt.ipv4_vpn_pool.getValue()}},
    	                                     		        proxy: new Ext.data.HttpProxy({
    	                                     		            url: '/ebsadmin/ipaddress/getfrompool/',
    	                                     		            method:'POST',
    	                                     		            
    	                                     		        }),
    	                                     		        
    	                                     		        reader: new Ext.data.JsonReader({
    	                                     		        	totalProperty: 'totalCount',
    	                                     		            root: 'records'
    	                                     		        }, [{
    	                                     		            name: 'ipaddress'
    	                                     		        }])
    	                                     		    }),
    	                                            },
    	                                            {
    	                                                xtype: 'xcomboippool',
    	                                                name: 'ipv4_vpn_pool',
    	                                                hiddenName: 'ipv4_vpn_pool',
    	                                                type:0,
    	                                                flex: 1
    	                                            }
    	                                        ]
    	                                    },
    	                                    {
    	                                        xtype: 'container',
    	                                        layout: 'hbox',
    	                                        anchor: '100%',
    	                                        hidden:true,
    	                                        fieldLabel: 'IPv6 VPN IP',
    	                                        items: [
    	                                            {
    	                                                xtype: 'textfield',
    	                                                name: 'vpn_ipv6_ip_address',
    	                                                vtype:'IPv6Address',
    	                                                value:'::',
    	                                                flex: 1
    	                                            },
    	                                            {
    	                                                xtype: 'xcomboippool',
    	                                                pool_type:2,
    	                                                
    	                                                flex: 1
    	                                            }
    	                                        ]
    	                                    },
    	                                    {
    	                                        xtype: 'checkbox',
    	                                        name: 'allow_vpn_with_null',
    	                                        boxLabel: 'Разрешить RADIUS авторизацию при нулевом балансе',
    	                                        anchor: '100%',

    	                                        hideLabel: true
    	                                    },
    	                                    {
    	                                        xtype: 'checkbox',
    	                                        name: 'allow_vpn_with_minus',
    	                                        boxLabel: 'Разрешить RADIUS авторизацию при отрицательном балансе',
    	                                        anchor: '100%',

    	                                        hideLabel: true
    	                                    },
    	                                    {
    	                                        xtype: 'checkbox',
    	                                        name: 'allow_vpn_with_block',
    	                                        boxLabel: 'Разрешить RADIUS авторизацию при блокировке по балансу/лимитам трафика',
    	                                        anchor: '100%',

    	                                        hideLabel: true
    	                                    },
    	                                    {
    	                                        xtype: 'checkbox',
    	                                        name: 'associate_pptp_ipn_ip',
    	                                        boxLabel: 'Привязать PPTP авторизацию к IPN IP',
    	                                        anchor: '100%',

    	                                        hideLabel: true
    	                                    },
    	                                    {
    	                                        xtype: 'checkbox',
    	                                        name: 'associate_pppoe_ipn_mac',
    	                                        boxLabel: 'Привязать PPPOE авторизацию к IPN MAC',
    	                                        anchor: '100%',

    	                                        hideLabel: true
    	                                    },
    	                                    {
    	                                        xtype: 'textfield',
    	                                        anchor: '100%',
    	                                        fieldLabel: 'Скорость'
    	                                    }
    	                                ]
    	                            }
    	                        ]
    	                    },
    	                    {
    	                        xtype: 'container',
    	                        items: [
    	                            {
    	                                xtype: 'fieldset',
    	                                width: 533,
    	                                title: 'IPN авторизация',
    	                                collapsible:true,
    	                                items: [
    	                                    {
    	                                        xtype: 'container',
    	                                        layout: 'hbox',
    	                                        anchor: '100%',
    	                                        fieldLabel: 'IPv4 IPN IP',
    	                                        align: 'middle',
    	                                        items: [
    	                                            {
    	                                                xtype: 'combo',
    	                                                name: 'ipn_ip_address',
    	                                                vtype:'IPAddress',
    	                                                value:'0.0.0.0',
    	                                                flex: 1,
    	                                                anchor: '100%',
    	                                     		    
    	                                     		    displayField: 'ipaddress',
    	                                     		    valueField: 'ipaddress', 
    	                                     		    mode: 'remote',
    	                                     		    editable:true,
    	                                                loadingText  : 'Searching...',
    	                                                pageSize     : 25,
    	                                     		    triggerAction: 'all',
    	                                     		    typeAhead: false,
    	                                     		    //ref: 'store/p',
    	                                     		    listeners:{
	                                     		        	focus:function(obj, options){
	                                     		        		pool_id=this.findParentByType('form').getForm().findField('ipv4_ipn_pool').getValue();
	                                     		        		//alert();
	                                     		        		obj.store.setBaseParam('pool_id',pool_id);
	                                     		        		if (pool_id){
	                                     		        			obj.store.load()
	                                     		        		}
	                                     		        	},
	                                     		        	//scope:this.ownerCt,
	                                     		        	
	                                     		        },
	                                     		        
    	                                     		    store:new Ext.data.Store({
    	                                     		    	ref: '../st',
    	                                     		    	param:{pool_id:function (){return this.ownerCt.ownerCt.ipv4_vpn_pool.getValue()}},
    	                                     		        proxy: new Ext.data.HttpProxy({
    	                                     		            url: '/ebsadmin/ipaddress/getfrompool/',
    	                                     		            method:'POST',
    	                                     		            
    	                                     		        }),
    	                                     		        
    	                                     		        reader: new Ext.data.JsonReader({
    	                                     		        	totalProperty: 'totalCount',
    	                                     		            root: 'records'
    	                                     		        }, [{
    	                                     		            name: 'ipaddress'
    	                                     		        }])
    	                                     		    }),
    	                                            },
    	                                            {
    	                                                xtype: 'xcomboippool',
    	                                                name: 'ipv4_ipn_pool',
    	                                                hiddenName: 'ipv4_ipn_pool',
    	                                                pool_type: 1,
    	                                                flex: 1
    	                                            }
    	                                        ]
    	                                    },
    	                                    {
    	                                        xtype: 'container',
    	                                        layout: 'hbox',
    	                                        anchor: '100%',
    	                                        fieldLabel: 'IPN MAC',
    	                                        items: [
    	                                            {
    	                                                xtype: 'textfield',
    	                                                width: 130,
    	                                                name: 'ipn_mac_address',
    	                                                flex: 1
    	                                            },
    	                                            {
    	                                                xtype: 'button',
    	                                                text: 'Определить',
    	                                                flex: 1,
    	                                                width:100,
    	                                                //getmacforip
    	                                                handler:function(button, event){
    	                                                	//button.disable();
    	                                                	button.setText('Подождите');
		    	                                        	Ext.Ajax.request({
		    	                	                            params: {'nas_id':button.findParentByType('form').getForm().findField('nas').getValue(),
		    	                	                            	'ipn_ip_address':button.findParentByType('form').getForm().findField('ipn_ip_address').getValue()
		    	                	                            	},
		    	                	                            url: '/ebsadmin/getmacforip/',
		    	                	                            success: function (resp) {
		    	                	                                var data;
		    	                	                                data = Ext.decode(resp.responseText);
		    	                	                                //button.enable();
		    	                	                                button.setText('Определить');
		    	                	                                if (data.success === true) {
		    	                	                                	button.findParentByType('form').getForm().findField('ipn_mac_address').setValue(data.mac);
		    	                	                                    
		    	                	                                } else {
		    	                	                                    Ext.MessageBox.alert('Ошибка', 'Неверный запрос. '+data.msg);
		    	                	                                }
		    	                	                            },
		    	                	                            failure: function () {
		    	                	                            	button.setText('Определить');
		    	                	                            	Ext.MessageBox.alert('Ошибка', 'Ошибка передачи данных');
		    	                	                            }
		    	                	                        });
		    	                                        }
    	                                            }
    	                                        ]
    	                                    },
    	                                    {
    	                                        xtype: 'container',
    	                                        hidden:true,
    	                                        layout: 'hbox',
    	                                        anchor: '100%',
    	                                        fieldLabel: 'IPv6 IPN IP',
    	                                        items: [
    	                                            {
    	                                                xtype: 'textfield',
    	                                                name: 'ipn_ipv6_ip_address',
    	                                                vtype:'IPv6Address',
    	                                                value:'::',
    	                                                flex: 1
    	                                            },
    	                                            {
    	                                                xtype: 'combo',
    	                                                flex: 1
    	                                            }
    	                                        ]
    	                                    },
    	                                    {
    	                                        xtype: 'checkbox',
    	                                        name: 'allow_dhcp',
    	                                        boxLabel: 'Выдавать IPN IP адрес по DHCP',
    	                                        anchor: '100%',
    	                                        fieldLabel: 'Label',
    	                                        hideLabel: true
    	                                    },
    	                                    {
    	                                        xtype: 'checkbox',
    	                                        name: 'allow_dhcp_with_null',
    	                                        boxLabel: 'Выдавать IP адрес по DHCP при нулевом балансе',
    	                                        anchor: '100%',
    	                                        fieldLabel: 'Label',
    	                                        hideLabel: true
    	                                    },
    	                                    {
    	                                        xtype: 'checkbox',
    	                                        name: 'allow_dhcp_with_minus',
    	                                        boxLabel: 'Выдавать IP адрес по DHCP при отрицательном балансе',
    	                                        anchor: '100%',
    	                                        fieldLabel: 'Label',
    	                                        hideLabel: true
    	                                    },
    	                                    {
    	                                        xtype: 'checkbox',
    	                                        name: 'allow_dhcp_with_block',
    	                                        boxLabel: 'Выдавать IP адрес по DHCP при блокировке по балансу/лимитам трафика',
    	                                        anchor: '100%',
    	                                        fieldLabel: 'Label',
    	                                        hideLabel: true
    	                                    },
    	                                    {
    	                                        xtype: 'checkbox',
    	                                        name: 'allow_ipn_with_null',
    	                                        boxLabel: 'Разрешить IPN доступ при нулевом балансе',
    	                                        anchor: '100%',
    	                                        fieldLabel: 'Label',
    	                                        hideLabel: true
    	                                    },
    	                                    {
    	                                        xtype: 'checkbox',
    	                                        name: 'allow_ipn_with_minus',
    	                                        boxLabel: 'Разрешить IPN доступ при отрицательном балансе',
    	                                        anchor: '100%',
    	                                        fieldLabel: 'Label',
    	                                        hideLabel: true
    	                                    },
    	                                    {
    	                                        xtype: 'checkbox',
    	                                        name: 'allow_ipn_with_block',
    	                                        boxLabel: 'Разрешить IPN доступ при блокировке по балансу/лимитам трафика',
    	                                        anchor: '100%',
    	                                        fieldLabel: 'Label',
    	                                        hideLabel: true
    	                                    },
    	                                    {
    	                                        xtype: 'checkbox',
    	                                        name: 'allow_mac_update',
    	                                        boxLabel: 'Разрешить обновление IPN MAC адреса через веб-кабинет',
    	                                        anchor: '100%',
    	                                        fieldLabel: 'Label',
    	                                        hideLabel: true
    	                                    },
    	                                    {
    	                                        xtype: 'textfield',
    	                                        anchor: '100%',
    	                                        fieldLabel: 'Скорость'
    	                                    }
    	                                ]
    	                            }
    	                        ]
    	                    },
    	                    {
    	                        xtype: 'container',
    	                        width: 100,
    	                        flex: 1,
    	                        items: [
    	                            {
    	                                xtype: 'fieldset',
    	                                width: 533,
    	                                defaults: {
    	                                    hideLabel: true
    	                                },
    	                                title: 'Опции',
    	                                items: [
    	                                    {
    	                                        xtype: 'checkbox',
    	                                        name: 'allow_addonservice',
    	                                        boxLabel: 'Разрешить активацию подключаемых услуг через веб-кабинет',
    	                                        anchor: '100%',
    	                                        fieldLabel: 'Label'
    	                                    }
    	                                ]
    	                            }
    	                        ]
    	                    }
    	        
    	        
    	    ]
    	}
    EBS.forms.ebs_accountsPanel.subaccounts.edit_submitAction =  function(object, event){
form = object.ownerCt;
//console.log(form);
}
    Ext.reg("ebs_accountsPanel", EBS.conponents.accountsGrid);
    EBS.windows.keys[EBS.windows.keys.length] = 'ebs_accountsPanel';
    
    
});
