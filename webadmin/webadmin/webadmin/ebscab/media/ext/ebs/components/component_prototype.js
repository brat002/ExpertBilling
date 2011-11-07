Ext.onReady(function(){
    Ext.ns('EBS.forms.ebs_xxxxxxxxxxxxxxxxPanel')
    EBS.conponents.accountsGrid = Ext.extend(EBS.base.GridPanel, {
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
             this.topToolbar = new Ext.Toolbar({
                    enableOverflow: true,
                    items:[
                         {
                            icon: media+'icons/16/pencil.png',
                            height:32,
                            width:32,
                            text: i18n.edit,
                            handler: this.tbFormCallBack.createCallback('edit_user')
                        },{
                            text: i18n.print,
                            icon: media+'icons/16/printer.png',
                            height:32,
                            width:32,
                            tooltip: 'Print current panel',
                            handler: function(){Ext.ux.Printer.print(Ext.getCmp('accounts_list'))}
                        },{
                            text: 'Test alert',
                            handler: this.tbCommandCallBack.createCallback(this,'alert',1)
                        },
                        {xtype: 'tbseparator'},
                        {
                            xtype: 'tbbutton',
                            text: 'Действия',
                            icon: media+'icons/16/new/user.png',
                            height:32,
                            width:32,
                            menu: [
                                {
                                    text : i18n.XXXXXXXXXXX,
                                    icon: media+'icons/XXXXXXXXXXXXXXXX.png',
                                    handler: this.tbFormCallBack.createCallback(this,'edit_field')
                                },
                                {
                                    text : i18n.XXXXXXXXXXX,
                                    icon: media+'icons/XXXXXXXXXXXXXXXX.png',
                                    handler: this.tbFormCallBack.createCallback(this,'edit_field')
                                }
                            ]
                        }

                    ]
                });






             Ext.apply(this, {
                                id:'accounts_list',
                                store   : EBS.store.accounts,
                                closable:true,
                              //  plugins : [this.filters],
                                tbar    : this.topToolbar,
                                columns : [
                                                ... Columns or colmodel ...
                                ],
                                listeners: {/*
                                    render:function(){
                                     this.bbar.updateInfo();
                                    }*/
                                },
                                stripeRows: true,
                                title: ... Title ...,
                                stateful: true,
                                stateId: ... Text coockie provider name ...
                            //bbar:this.pagination
                });
            this.bbar.store = this.store;
            EBS.conponents.accountsGrid.superclass.initComponent.apply(this, arguments);
            //this.bbar.updateInfo();

         } //initComponent
     });


/* ACCOUNTS FORMS*/
    EBS.forms.ebs_xxxxxxxxxxxxxxxxPanel.edit_credit = {
                                        xtype: 'form',
                                        id: 'account-info',
                                        items:{
                                            columnWidth: 0.4,
                                            xtype: 'fieldset',
                                            id:'qqq',
                                            labelWidth: 120,
                                            title:'Account details',
                                            defaults: {width: 140, border:false},
                                            defaultType: 'textfield',
                                            autoHeight: true,
                                            border: false,
                                            // Can be autogenerated
                                            items: [
                                                ... Form items ...
                                            ]
                                           }
                                      };
    EBS.forms.ebs_xxxxxxxxxxxxxxxxPanel.edit_credit_submitAction =  function(object, event){
        form = object.ownerCt;
        console.log(form);
    }
/* EOF ACCOUNTS FORMS*/

    Ext.reg("ebs_xxxxxxxxxxxxxxxxPanel", EBS.conponents.accountsGrid);
    EBS.windows.keys[EBS.windows.keys.length] = 'ebs_xxxxxxxxxxxxxxxxPanel';
});
