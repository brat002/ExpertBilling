Ext.onReady(function(){
    Ext.ns('EBS.forms.ebs_nasPanel')
    EBS.conponents.nasGrid = Ext.extend(EBS.base.GridPanel, {
         initComponent: function() {
                /*
                 *ф-я вызывается в менюшке. В качестве параметров идут self, вызываемая ф-я, если нужно - параметры.
                 *берем функцию через  eval и вызываем ее с параметрами
                 *id у self обязательна.
                 *
                 *Будут перенесены в базовый компонент. менять сразу во всех компонентах!
                 **/
                this.tbFormCallBack = function(self, action){
                    //console.log('EBS.forms.'+self.xtype+'.'+action,{action:action, self:self, selection:self.selModel.selections});
                    EBS.displayForm(self.xtype, {action:action, self:self, selection:self.selModel.selections})
                }
                this.tbWindowCallBack = function(self, action){
                    EBS.displayWindow(self.xtype, {action:action, self:self, selection:self.selModel.selections})
                }
                this.tbCommandCallBack = function(self, action, param1){
                    eval(action)(param1)
                }

             // MENU
                          this.topToolbar = [
                         {
                            //text: 'ok',
                            icon: media+'icons/16/pencil.png',
                            height:16,width:16,
                            text: i18n.edit,
                            handler: function () {}
                        },{
                            text: i18n.print,
                            icon: media+'icons/16/printer.png',
                            height:16,width:16,
                            tooltip: i18n.printToolTip,
                            handler: function () {
                                //Ext.ux.Printer.print(mainPanel)
                            }
                        },
                        {xtype: 'tbseparator'},
                        {
                            xtype: 'tbbutton',
                            text: 'Действия',
                            icon: media+'icons/16/new/user.png',
                            height:16,width:16,
                            menu: [
                                {
                                    text : 'add',
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbFormCallBack.createCallback(this,'user_add')
                                },{
                                    text : 'user_remove',
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbFormCallBack.createCallback(this,'user_remove')
                                },{
                                    text : 'user_activate',
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbFormCallBack.createCallback(this,'user_activate')
                                },{
                                    text : 'user_deactivate',
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbFormCallBack.createCallback(this,'user_deactivate')
                                }
                            ]
                        },
                        {
                            xtype: 'tbbutton',
                            text: 'VPN / IPN',
                            icon: media+'icons/16/new/user.png',
                            height:16,width:16,
                            menu: [
                                {
                                    text : 'user_vpn_speed',
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbFormCallBack.createCallback(this,'user_vpn_speed')
                                },{
                                    text : 'user_ipn_speed',
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbFormCallBack.createCallback(this,'user_ipn_speed')
                                },{
                                    text :'user_vpn_reset',
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbFormCallBack.createCallback(this,'user_vpn_reset')
                                }
                            ]
                        },{xtype: 'tbseparator'},{
                            text: i18n.save,
                            icon: media+'icons/16/accept.png',
                            height:16,width:16,
                            tooltip: i18n.saveToolTip,
                            handler: EBS.store.nas.save
                        }


                    ];






        Ext.apply(this, {
                store   : EBS.store.nas,
                closable:true,
               // plugins : [this.filters],
                tbar    : this.topToolbar,
                columns : [
                {
                    header   : 'Название',
                    sortable : true,
                    width    : 85,
                    locked: true,
                    dataIndex: 'name',
                    filter: {
                        type: 'string'
                    }

                },
                {
                    header   : 'Идентификатор',
                    sortable : true,
                    //autoexpand:true,
                    width:200,
                    dataIndex: 'identify'
                    //filter: {
                    //    type: 'string'
                    //}

                },
                {
                    header   : 'ipaddress',
                    width    : 115,
                    sortable : true,
                    //      renderer : Ext.util.Format.dateRenderer('Y-m-d h:i a'),
                    dataIndex: 'ipaddress'
                },
                {
                    header   : 'secret',
                    width    : 115,
                    sortable : true,
                    //      renderer : Ext.util.Format.dateRenderer('Y-m-d h:i a'),
                    dataIndex: 'secret'
                },
                ],
                listeners: {
                  rowdblclick: function(grid, rowIndex, evnt) {
                    rec = EBS.store.nas.getAt(rowIndex);
                    EBS.windows.nasInfo.show(this);
                    Ext.getCmp('nas-info').getForm().loadRecord(rec);
                    }
                },
                stripeRows: true,
                title: 'Сервера доступа',
                stateful: true,
                stateId: 'nasgrid'
            //    bbar:this.pagination
            });
            this.bbar.store = this.store;
            EBS.conponents.nasGrid.superclass.initComponent.apply(this, arguments);
            //this.bbar.updateInfo();

         } //initComponent
     });


/* ACCOUNTS FORMS*/
    // Параметры сервера доступа
    EBS.forms.ebs_nasPanel.user_add = {
                        xtype: 'form',
                        id: 'nas-info',
                        windowTitle: 'RADIUS параметры',
                        items: [{
                            // Fieldset in Column 1
                            xtype:'fieldset',
                            columnWidth: 0.5,
                            collapsible: false,
                            autoHeight:true,
                            width: 400,
                            defaults: {
                                anchor: '-20' // leave room for error icon
                            },
                            defaultType: 'textfield',
                            items :[{
                                xtype:'combo',
                                fieldLabel: 'Тип сервера доступа',
                                mode: 'local',
                                store: new Ext.data.ArrayStore({
                                    id: 0,
                                    fields: [
                                    'nasId',
                                    'nasName'
                                    ],
                                    data: [['mikrotik4', 'MikroTik 4'], ['mikrotik3', 'MikroTik 3']]
                                }),
                                valueField: 'nasId',
                                displayField: 'nasName'
                            },
                            {
                                fieldLabel: 'Идентификатор',
                                name: 'identify'
                            }
                            ,
                            {
                                fieldLabel: 'Realm'
                            }
                            ,{
                                fieldLabel: 'Секрет'
                            }, {
                                fieldLabel: 'IP'
                            },
                            {
                                xtype: 'numberfield',
                                fieldLabel: 'Coa'
                            }
                            ]
                        },{
                            // Fieldset in Column 2 - Panel inside
                            xtype:'fieldset',
                            title: 'Статистика', // title, header, or checkboxToggle creates fieldset header
                            autoHeight:true,
                            columnWidth: 0.5,
                            checkboxToggle: false,
                            collapsed: false, // fieldset initially collapsed
                            layout:'form',
                            rowspan:2,
                            items :[]
                        },

                        {
                            // Fieldset in Column 1
                            xtype:'fieldset',
                            //columnWidth: 0.5,
                            title: 'Параметры управления',
                            collapsible: false,
                            autoHeight:true,
                            defaults: {
                                anchor: '-20' // leave room for error icon
                            },
                            defaultType: 'textfield',
                            items :[{
                                xtype:'combo',
                                fieldLabel: 'Тип',
                                disabled: true,
                                mode: 'local',
                                store: new Ext.data.ArrayStore({
                                    id: 0,
                                    fields: [
                                    'typeId',
                                    'nasType'
                                    ],
                                    data: [['int_ssh', 'Internal SSH'], ['ext_ssh', 'External SSH'], ['custom', 'Custom']]
                                }),
                                valueField: 'typeId',
                                displayField: 'nasType'
                            },
                            {
                                fieldLabel: 'Username'
                            }, {
                                fieldLabel: 'Password'
                            },
                            {
                                xtype:'button',
                                text:'Проверить'
                            }
                            ]
                        }]

                };
    EBS.forms.ebs_nasPanel.add_user_submitAction =  function(object, event){
        form = object.ownerCt;
        console.log(form);
    }
/* EOF ACCOUNTS FORMS*/

    Ext.reg("ebs_nasPanel", EBS.conponents.nasGrid);
    EBS.windows.keys[EBS.windows.keys.length] = 'ebs_nasPanel';
});





/*

Ext.onReady( function() {
    //usersPanel = new Ext.grid.GridPanel();

    EBS.conponents.nasGrid = Ext.extend(EBS.base.GridPanel, {
        initComponent: function() {


            ////////////////////////////////////////////
            var myData = [
            ['Добавить абонента на сервер доступа', '3m Co'],
            ['Удалить абонента с сервера доступа', 'Alcoa Inc'],
            ['Установить скорость для VPN', 'Altria Group Inc'],
            ['Установить скорость для IPN', 'American Express Company'],
            ['Сбросить VPN сессию', 'reset'],
            ['Активировать абонента', 'enable'],
            ['Деактивировать абонента', 'disable'],
            ];

            var fm = Ext.form;
            var grid = new Ext.grid.EditorGridPanel({
                store: new Ext.data.ArrayStore({
                    autoDestroy: true,
                    //reader: reader,
                    fields: [{name:'name'}, {name:'data'}],
                    data:myData,
                }),
                clicksToEdit: 1,
                autoExpandColumn: 'data',
                colModel: new Ext.grid.ColumnModel({
                    defaults: {
                        width: 120,
                        sortable: true
                    },
                    columns: [
                    {id: 'name', header: 'Тип', sortable: true, dataIndex: 'name'},
                    {id: 'data', header: 'Действие', dataIndex: 'data', editor: new fm.TextField({allowBlank: false})},
                    /*{header: 'Price', renderer: Ext.util.Format.usMoney, dataIndex: 'price'},
                     {header: 'Change', dataIndex: 'change'},
                     {header: '% Change', dataIndex: 'pctChange'},
                     // instead of specifying renderer: Ext.util.Format.dateRenderer('m/d/Y') use xtype
                     {
                     header: 'Last Updated', width: 135, dataIndex: 'lastChange',
                     xtype: 'datecolumn', format: 'M d, Y'
//                      }*/
/*                    ],
                }),
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                width: 600,
                height: 300,
                frame: true,
                title: 'Framed with Row Selection and Horizontal Scrolling',
                iconCls: 'icon-grid'
            });
            ////////////////////////////////////////////
            // create the Grid




            
            this.bbar.store = this.store;
            EBS.conponents.nasGrid.superclass.initComponent.apply(this, arguments);
        } //initComponent
    });

});
*/