Ext.onReady(function(){
    Ext.ns('EBS.forms.ebs_sessionmonitorPanel')
    EBS.conponents.sessionmonitorGrid = Ext.extend(EBS.base.GridPanel, {
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
						    icon: media+'icons/16/add.png',
						    height:16,width:16,
						    text: i18n.edit,
						    handler: this.tbNewFormInTabCallBack.createCallback(this, 'edit_user')
						},
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
                            xtype: 'tbbutton',
                            text: 'Действия',
                            icon: media+'icons/16/new/user.png',
                            height:16,width:16,
                            menu: [
                                {
                                    text : "Редактировать кредит",
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





             //['account', 'called_id', 'interrim_update', 'session_status', 'bytes_in', 'date_end', 'date_start', 'session_time', 'caller_id', 'bytes_out', 'sessionid', 'speed_string', 'nas_id', 'framed_protocol', 'framed_ip_address', 'id', 'subaccount']
             Ext.apply(this, {
                                id:'sessionmonitor_list',
                                view: new Ext.grid.GroupingView(),
                                store   : EBS.store.sessions,
                                windowTitle:'Монитор',
                                closable:false,
                              //  plugins : [this.filters],
                                tbar    : this.topToolbar,
                                columns : [
                                    {
                                        header   : '#',
                                        sortable : true,
                                        //width    : 85,
                                        locked: true,
                                        dataIndex: 'id',
                                        filter: {
                                            type: 'numeric'
                                        }

                                    },{
                                        header   : 'Session ID',
                                        sortable : true,
                                        //width    : 85,
                                        //locked: true,
                                        dataIndex: 'sessionid',
                                        filter: {
                                            type: 'string'
                                        }

                                    },                                
                                    {
                                        header   : 'Аккаунт',
                                        sortable : true,
                                        //width    : 85,
                                        //locked: true,
                                        dataIndex: 'account',
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                    {
                                        header   : 'Субаккаунт',
                                        sortable : true,
                                        //width    : 85,
                                        //locked: true,
                                        dataIndex: 'subaccount',
                                        filter: {
                                            type: 'string'
                                        }

                                    },      
                                    {
                                        header   : 'NAS',
                                        sortable : true,
                                        //width    : 85,
                                        //locked: true,
                                        dataIndex: 'nas_id',
                                        filter: {
                                            type: 'string'
                                        }

                                    },      
                                    {
                                        header   : 'Caller ID',
                                        sortable : true,
                                        //width    : 85,
                                        //locked: true,
                                        dataIndex: 'caller_id',
                                        filter: {
                                            type: 'string'
                                        }

                                    }, 
                                    {
                                        header   : "Called ID",
                                        sortable : true,
                                        autoexpand:true,
                                        width:200,
                                        dataIndex: 'called_id',
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                    {
                                        header   : 'Framed Protocol',
                                        sortable : true,
                                        //autoexpand:true,
                                        width:200,
                                        dataIndex: 'framed_protocol',
                                        
                                        filter: {
                                            type: 'string'
                                        }

                                    },  
                                    

                                   {
                                        header   : 'Framed IP Address',
                                        sortable : true,
                                        //autoexpand:true,
                                        //width:200,
                                        dataIndex: 'framed_ip_address',
                                        
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                   {
                                        header   : 'Начало',
                                        sortable : true,
                                        //autoexpand:true,
                                        //width:200,
                                        dataIndex: 'date_start',
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                    {
                                        header   : 'Последний пакет',
                                        sortable : true,
                                        //autoexpand:true,
                                        //width:200,
                                        dataIndex: 'interrim_update',
                                        filter: {
                                            type: 'string'
                                        }

                                    },                                    
                                    {
                                        header   : 'Конец',
                                        sortable : true,
                                        //autoexpand:true,
                                        //width:200,
                                        dataIndex: 'date_end',
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                    {
                                        header   : 'Время',
                                        sortable : true,
                                        //autoexpand:true,
                                        //width:200,
                                        dataIndex: 'session_time',
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                    {
                                        header   : 'Данные',
                                        sortable : true,
                                        //autoexpand:true,
                                        //width:200,
                                        //dataIndex: 'contactperson',
                                        renderer: function(value, p, r)
                                        {return bytesToSize(r.data['bytes_in']) + '/' + bytesToSize(r.data['bytes_out'])},
                                        filter: {
                                            type: 'string'
                                        }

                                    },

                                    {
                                        header   : 'Статус',
                                        //width    : 115,
                                        sortable : true,
                                        dataIndex: 'session_status',
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
                                stateId: 'accountsgrid',
                                
                            //bbar:this.pagination
                });
            this.bbar.store = this.store;
            this.on('rowdblclick', function(eventGrid, rowIndex, e) {
            	this.tbFormInTabCallBack(this, 'edit_user',this.selModel.selections.items[0].id);
            	
            	}, this);            
            EBS.conponents.sessionmonitorGrid.superclass.initComponent.apply(this, arguments);
            //this.bbar.updateInfo();

         } //initComponent
     });


    Ext.reg("ebs_sessionmonitorPanel", EBS.conponents.sessionmonitorGrid);
    EBS.windows.keys[EBS.windows.keys.length] = 'ebs_sessionmonitorPanel';
    
    
});
