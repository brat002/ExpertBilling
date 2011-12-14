Ext.onReady(function(){
	  EBS.ComboMultiSelectTariff = Ext.extend(Ext.ux.form.LovCombo, {
	      initComponent:function() {
	         var config = {
	        		 valueField:'tarif',
	                 displayField:'name',
	                 hiddenName:'tarif',
	                 
	                 fieldLabel: 'Тариф',
	                 editable:false,
	                 typeAhead: true,
	                 width:200,
	                 mode:'remote',
	                 triggerAction:'all',
	                 hideOnSelect:true,
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
	  
	         EBS.ComboMultiSelectTariff.superclass.initComponent.apply(this, arguments);
	     } // eo function initComponent

	   

	 });
	  
	 Ext.reg('xcombomultitariff', EBS.ComboMultiSelectTariff);
    Ext.ns('EBS.forms.ebs_transactionreportPanel')
    EBS.conponents.transactionreportGrid = Ext.extend(EBS.base.GridPanel, {
         initComponent: function() {
                /*
                 *ф-я вызывается в менюшке. В качестве параметров идут self, вызываемая ф-я, если нужно - параметры.
                 *берем функцию через  eval и вызываем ее с параметрами
                 *id у self обязательна.
                 *
                 *Будут перенесены в базовый компонент. менять сразу во всех компонентах!
                 **/
                this.tbFormCallBack = function(self, action){EBS.displayForm(self.xtype, action, self)}
                this.tbCustomFormCallBack = function(self, action){EBS.displayCustomForm(self.xtype, action, self)}

                this.tbNewFormInTabCallBack = function(self, action){
                	id=null;
                	
                	EBS.displayFormInTab(self.xtype, action,id, {'account_id':id}, self)
                	}
                this.tbFormInTabCallBack = function(self, action, id){
                	//alert(id);
                	//alert(self.selModel);
                	
                		id=self.selModel.selections.items[0].id;
                		//alert(self.selModel.selections.items[0]);
                	
                	EBS.displayFormInTab(self.xtype, action,id, {'account_id':id}, self)
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
                            icon: media+'icons/16/pencil.png',
                            height:16,width:16,
                            text: i18n.edit,
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
                            text: 'Сбросить сессию',
                            icon: media+'icons/16/printer.png',
                            height:16,width:16,
                            tooltip: i18n.printToolTip,
                            handler: function(){Ext.ux.Printer.print(this.ownerCt.ownerCt)}
                        },
                        
                        	       {
                        	    	   xtype: 'checkbox',
                        	    	   boxLabel:'Только активные',
                        	    	   width:130,
                        	    		   
                        	       },
                        	       {xtype: 'tbseparator'},
                        	       {
                        	    	   //xtype:'label',
                        	    	   text:'c',
                        	    	   width:10,
                        	       },
                        	       {
                        	    	   xtype:'xdatetime',
                        	    	   width:250,
                        	    	   
                        	       },
                        	       {
                        	    	   //xtype:'label',
                        	    	   text:'по',
                        	    	   width:10,
                        	       },
                        	       {
                        	    	   xtype:'xdatetime',
                        	    	   width:250,
                        	    	   
                        	       }
                        	      
                        ,{
                            text: 'Обновить',
                            icon: media+'icons/16/arrow_refresh.png',
                            height:24,width:24,
                            tooltip: i18n.saveToolTip,
                            handler: this.tbFormReloadCallBack.createCallback(this)
                        }

                    ]
                });





             //['account', 'called_id', 'interrim_update', 'session_status', 'bytes_in', 'date_end', 'date_start', 'session_time', 'caller_id', 'bytes_out', 'sessionid', 'speed_string', 'nas_id', 'framed_protocol', 'framed_ip_address', 'id', 'subaccount']
             Ext.apply(this, {
                                id:'transactionreport_list',
                                view: new Ext.grid.GroupingView(),
                                store: EBS.store.transactionreport,
                                title: 'Список операций',
                                closable:false,
                              //  plugins : [this.filters],
                                tbar    : this.topToolbar,
                                cm: new Ext.grid.ColumnModel({}),
                                //columns:[],
                                
                                listeners: {/*
                                    render:function(){
                                     this.bbar.updateInfo();
                                    }*/
                                },
                                stripeRows: false,
                                stateful: true,
                                stateId: 'transactionreportgrid',
                                
                            //bbar:this.pagination
                });
            this.bbar.store = this.store;
            this.on('rowdblclick', function(eventGrid, rowIndex, e) {
            	//this.tbFormInTabCallBack(this, 'edit_user',this.selModel.selections.items[0].id);
            	
            	}, this);    
            
            EBS.conponents.transactionreportGrid.superclass.initComponent.apply(this, arguments);
            this.store.on('load', function(){
            	/**
            	* Thats the magic! <img src="http://erhanabay.com/wp-includes/images/smilies/icon_smile.gif" alt=":)" class="wp-smiley">
            	*
            	* JSON data returned from server has the column definitions
            	*/
            	if(typeof(this.store.reader.jsonData.metaData.fields) === 'object') {
            	var columns = [];
            	/**
            	* Adding RowNumberer or setting selection model as CheckboxSelectionModel
            	* We need to add them before other columns to display first
            	*/

            	Ext.each(this.store.reader.jsonData.metaData.fields, function(column){
            	columns.push(column);
            	});
            	/**
            	* Setting column model configuration
            	*/
            	
            	this.getColumnModel().setConfig(columns);
            	}
            	/**
            	* Unmasking grid
            	*/
            	
            	}, this);
            	
            //this.bbar.updateInfo();

         } //initComponent
     });


    Ext.reg("ebs_transactionreportPanel", EBS.conponents.transactionreportGrid);
    EBS.windows.keys[EBS.windows.keys.length] = 'ebs_transactionreportPanel';
    
    EBS.TransactionReportPanel = Ext.extend(Ext.TabPanel, {
        initComponent:function() {
           var config = {
						title:'Параметры отчёта',
						//id:'accountspanel',
						activeTab       : 0,
						//pack:'center',
						//bodyStyle: 'padding:20px 20% 20px 20%',
						items:[{
						    xtype:'container',
						    layout:'auto',
						    title: 'Настройки отчёта',
						    height:600,
						    layoutConfig: {
		                    	pack: 'center',
		                    	align: 'middle'
		                    	},
						    items:[
							{
						    xtype: 'form',
						    //height: 638,
						    width: 890,
						    layout: 'vbox',
						    save_url:'/ebsadmin/transactionreport/',
						    padding: 5,
						    height:600,
						    buttonAlign: 'center',
						    
						    items: [
						        {
						           
				                    xtype: 'fieldset',
				                    width: 837,
				                    layout: 'hbox',
				                    title: 'Период',
				                    layoutConfig: {
				                    	pack: 'center',
				                    	align: 'middle'
				                    	},
				                    	//bodyStyle:'padding:10 10 10 10;',
				                    defaults: {
				                    		border: true,
				                    		 
				                                 margins:'0 5 0 0',
				                    		},
				                    items: [
				                        {
				                            xtype: 'label',
				                            width: 16,
				                            text: 'С',
				                            
				                        },
				                        {
				                            xtype: 'xdatetime',
				                            name:'start_date',
				                            width: 220,
				                            
				                        },
				                        {
				                            xtype: 'label',
				                            width: 25,
				                            text: 'По',
				                            
				                        },
				                        {
				                            xtype: 'xdatetime',
				                            name:'end_date',
				                            width: 220,
				                            
				                           
				                        }
				                    ]
						               
						        },
						        {
						            xtype: 'container',
						            //height: 509,
						            width: 834,
						            layout: 'hbox',
						            pack:'center',
						            items: [
						                {
						                    xtype: 'container',
						                    height: 402,
						                    width: 420,
						                    layout: 'vbox',
						                    flex: 1,
						                    items: [
						                        {
						                            xtype: 'fieldset',
						                            width: 416,
						                            title: 'Аккаунты',
						                            items: [
						                                {
						                                    xtype: 'compositefield',
						                                    anchor: '100%',
						                                    fieldLabel: 'Аккаунт',
						                                    items: [
						                                        {
												                    xtype: 'xaccountslivesearchcombo',
												                    name: 'account',
												                    hiddenName: 'account',
												                    field:'username',
												                    valueField:'id',
												                    editable:true,
												                    displayField:'username',
												                    //anchor: '100%',
												                    width:200,
												                    fieldLabel: 'Аккаунт',
												                    blankText: 'Укажите имя пользователя или его часть'
												                  
												                },
						                                        
						                                    ]
						                                }
						                                
						                            ]
						                        },
						                        {
						                            xtype: 'fieldset',
						                            //height: 137,
						                            width: 416,
						                            title: 'Состав отчёта',
						                            items: [
						                                {
						                                    xtype: 'compositefield',
						                                    
						                                    anchor: '100%',
						                                    fieldLabel: 'Тарифы',
						                                    items: [
						                                        {
						                                            xtype: 'xcombomultitariff',
						                                            name:'tarif',
						                                            hiddenName:'tarif',
						                                            name:'tarif',
						                                            id:'tarifftransactionreportid',
						                                            fieldLabel: 'Тариф',
						                                            editable:false,
						                                            typeAhead: true,
						                                            width:200,
						                                            
						                                        },
						                                        {
						                                            xtype: 'checkbox',
						                                            boxLabel: 'Все',
						                                            fieldLabel: 'Все',
						                                            id:'tarifftransactionreportselectallid',
						                                            listeners:{
						                                            	'check':function (cb,state){
		                                                            		if (!Ext.getCmp('tarifftransactionreportselectallid').checked){
		                                                            			Ext.getCmp('tarifftransactionreportid').deselectAll();
		                                                            		}else{
		                                                            			Ext.getCmp('tarifftransactionreportid').selectAll();
		                                                            		}
		                                                            		
		                                                            	}
						                                            }
						                                        }
						                                    ]
						                                },
						                                {
						                                    xtype: 'compositefield',
						                                    name: 'ps',
						                                    anchor: '100%',
						                                    fieldLabel: 'Период.услуги',
						                                    items: [
						                                        {
						                                            xtype: 'lovcombo',
						                                            valueField:'id',
						                                            displayField:'name',
						                                            hiddenName:'periodicalservice',
						                                            name:'periodicalservice',
						                                            fieldLabel: 'Период. услуги',
						                                            editable:false,
						                                            typeAhead: true,
						                                            id:'pstransactionreportid',
						                                            width:200,
						                                            mode:'remote',
						                                            triggerAction:'all',
						                                            hideOnSelect:true,
						                                            store: new Ext.data.JsonStore({
						                                                autoLoad: true,
						                                                proxy: new Ext.data.HttpProxy({
						                                                    url: '/ebsadmin/periodicalservice/',
						                                                    method:'POST',
						                                                }),    
						                                                fields: ['id', 'name'],
						                                                root: 'records',
						                                                remoteSort:false,
						                                                
						                                              }
						                                            ),
						                                        },
						                                        {
						                                            xtype: 'checkbox',
						                                            boxLabel: 'Все',
						                                            fieldLabel: 'Все',
						                                            id:'pstransactionreportselectallid',
						                                            listeners:{
						                                            	'check':function (cb,state){
		                                                            		if (!Ext.getCmp('pstransactionreportselectallid').checked){
		                                                            			Ext.getCmp('pstransactionreportid').deselectAll();
		                                                            		}else{
		                                                            			Ext.getCmp('pstransactionreportid').selectAll();
		                                                            		}
		                                                            		
		                                                            	}
						                                            }
						                                        }
						                                    ]
						                                },
						                                {
						                                    xtype: 'compositefield',
						                                    anchor: '100%',
						                                    fieldLabel: 'Подключаемые услуги',
						                                    items: [
						                                        {
						                                            xtype: 'lovcombo',
						                                            valueField:'id',
						                                            displayField:'name',
						                                            hiddenName:'addonservice',
						                                            name:'addonservice',
						                                            width:200,
						                                            editable:false,
						                                            typeAhead: true,
						                                            mode:'remote',
						                                            id:'addstransactionreportid',
						                                            triggerAction:'all',
						                                            hideOnSelect:true,
						                                            store: new Ext.data.JsonStore({
						                                                autoLoad: true,
						                                                proxy: new Ext.data.HttpProxy({
						                                                    url: '/ebsadmin/addonservice/',
						                                                    method:'POST',
						                                                }),    
						                                                fields: ['id', 'name'],
						                                                root: 'records',
						                                                remoteSort:false,
						                                                
						                                              }
						                                            ),
						                                        },
						                                        {
						                                            xtype: 'checkbox',
						                                            boxLabel: 'Все',
						                                            fieldLabel: 'Все',
						                                            id:'addstransactionreportselectallid',
						                                            listeners:{
						                                            	'check':function (cb,state){
		                                                            		if (!Ext.getCmp('addstransactionreportselectallid').checked){
		                                                            			Ext.getCmp('addstransactionreportid').deselectAll();
		                                                            		}else{
		                                                            			Ext.getCmp('addstransactionreportid').selectAll();
		                                                            		}
		                                                            		
		                                                            	}
						                                            }
						                                        }
						                                    ]
						                                }
						                            ]
						                        },
						                        {
						                            xtype: 'fieldset',
						                            width: 416,
						                            title: 'Параметры отчёта',
						                            flex: 1,
						                            items: [
						                                {
						                                    xtype: 'radiogroup',
						                                    anchor: '100%',
						                                    fieldLabel: 'Пагинация',
						                                    items: [
						                                        {
						                                            xtype: 'radio',
						                                            boxLabel: 'Постранично'
						                                        },
						                                        {
						                                            xtype: 'radio',
						                                            boxLabel: 'На одной странице'
						                                        }
						                                    ]
						                                }
						                            ]
						                        }
						                    ]
						                },
						                {
						                    xtype: 'container',
						                    flex: 1,
						                    //width:360,
						                    items: [
						                        {
						                            xtype: 'fieldset',
						                            //height: 395,
						                            autoHeight:true,
						                            //width: 1337,
						                            width:450,
						                            title: 'Типы операций',
						                            items: [
						                                {
						                                    xtype: 'xcheckboxlistgrid',
						                                    columnResize: false,
						                                    fieldLabel: 'Типы',
						                                    ref:'../../../transactiontypelist',
						                                    height:200,
						                                    width:290,
						                                    stateful:true,
						                                    stateId:'transactiontypegridstates',
						                                    displayField:'name',
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
						                        		        }, {
						                        		            name: 'internal_name'
						                        		        }])
						                        		    })
						                                },
						                                
						                                {
						                                    xtype: 'xcheckboxlistgrid',
						                                    columnResize: false,
						                                    fieldLabel: 'Авторы',
						                                    ref:'../../../systemuserlist',
						                                    height:200,
						                                    width:290,
						                                    stateful:true,
						                                    stateId:'systemuserscheckgridstates',
						                                    displayField:'name',
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
						                        		    })
						                                },
						                            ]
						                        }
						                    ]
						                }
						            ]
						        }
						    ],
						       buttons:[{
									text:'Искать',
					        		handler:function(){
					        			var f;
					        			f=this.findParentByType('tabpanel').items.items[0].items.items[0].getForm();
					        			transactiontypes=this.findParentByType('form').transactiontypelist.getSelectedId();
					        			systemusers=this.findParentByType('form').systemuserlist.getSelectedId();
					        			
					        			//EBS.store.transactionreport.setBaseParam('systemuser',systemusers);
					        			//EBS.store.transactionreport.setBaseParam('transactiontype', transactiontypes);
					        			
					        			d=f.getValues();
					        			var res={};
					        			res.start_date=d.start_date;
					        			res.end_date=d.end_date;
					        			res.account = d.account;
					        			if (systemusers.length>0){
					        				res.systemusers=systemusers;
					        			}
					        			if (transactiontypes.length>0){
					        				res.transactiontype=transactiontypes;
					        			}
					        			if (d.tarif){
					        				res.tarif = d.tarif.split(',');
					        			}
					        			if (d.addonservice){
					        				res.addonservice=d.addonservice.split(',');
					        			}
					        			if (d.periodicalservice){
					        				res.periodicalservice=d.periodicalservice.split(',');
					        			}
					        			EBS.store.transactionreport.load({params:res});
					        			/*f.submit({url:f.save_url, params:{'systemuser':systemusers,'transactiontype':transactiontypes},waitMsg:'Saving Data...', submitEmptyText: true, success: function(obj,action) {        
					                       	Ext.Msg.alert('Данные были успешно сохранены', 'Данные были успешно сохранены' );
					                       
					                       },failure: function(form,action) {        
					                        	Ext.Msg.alert('Ошибка', action.result.msg )}});*/
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
						}]},
				    	{
				      		xtype :'ebs_transactionreportPanel',
				    		//id    :'ebs_transactionreportPanel',
				    		closable:false
				    	},
						
						]
						


        		}
           // apply config
           Ext.apply(this, Ext.apply(this.initialConfig, config));
    
           EBS.TransactionReportPanel.superclass.initComponent.apply(this, arguments);
       } // eo function initComponent
    
       ,onRender:function() {
           var me = this;
           
           EBS.TransactionReportPanel.superclass.onRender.apply(this, arguments);
       } // eo function onRender
     

   });
    Ext.reg('xtransactionreportpanel', EBS.TransactionReportPanel);
    EBS.windows.keys[EBS.windows.keys.length] = 'xtransactionreportpanel';
    
});
