Ext.onReady(function(){
    //usersPanel = new Ext.grid.GridPanel();

    EBS.conponents.usersGrid = Ext.extend(Ext.grid.GridPanel, {
         initComponent: function() {



            /**
             * Custom function used for column renderer
             * @param {Object} val
             */
            function change(val) {
                if (val > 0) {
                    return '<span style="color:green;">' + val + '</span>';
                } else if (val < 0) {
                    return '<span style="color:red;">' + val + '</span>';
                }
                return val;
            }













            // create the Grid
            encode = true;
            local = false;
            var filters = new Ext.ux.grid.GridFilters({
                // encode and local configuration options defined previously for easier reuse
                encode: false, // json encode the filter query
                local: false,   // defaults to false (remote filtering)
                filters: [{
                    type: 'string',
                    dataIndex: 'username'
                },{
                    type: 'string',
                    dataIndex: 'fullname'
                },{
                    type: 'numeric',
                    dataIndex: 'ballance'
                }, {
                    type: 'date',
                    dataIndex: 'created'
                }/*, {
                    type: 'list',
                    dataIndex: 'size',
                    options: ['small', 'medium', 'large', 'extra large'],
                    phpMode: true
                }*/
               ]
            });
            pagination = new Ext.PagingToolbar({
                           pageSize: 80,
                           store: EBS.store.users,
                           displayInfo: true,
                           dispalyMsg: 'Displaying {0} - {1} of {2}',
                           emptyMsg: 'No Media Found',
                           plugins: [new Ext.ux.SlidingPager(), filters]

                        });






            /* EDITOR TEST */

            //Create edit window
            if(!EBS.window.userInfo){
                        EBS.window.userInfo = new Ext.Window({
                            applyTo:Ext.get('ext-gen17'),
                            layout:'fit',
                            width:500,
                            height:300,
                            closeAction:'hide',
                            plain: true,

                            items: [{
                                        xtype: 'form',
                                        id: 'user-info',
                                        items:{
                                            columnWidth: 0.4,
                                            xtype: 'fieldset',
                                            id:'qqq',
                                            labelWidth: 120,
                                            title:'User details',
                                            defaults: {width: 140, border:false},
                                            defaultType: 'textfield',
                                            autoHeight: true,
                                            border: false,
                                            // Can be autogenerated
                                            items: [{
                                                        fieldLabel: 'Username',
                                                        name: 'username'
                                                    },{
                                                        fieldLabel: 'Fullname',
                                                        name: 'fullname'
                                                    },{
                                                        fieldLabel: 'ballance',
                                                        name: 'ballance'
                                                    },{
                                                        fieldLabel: 'E-mail',
                                                        name: 'email'
                                                    },{
                                                        fieldLabel: 'Created',
                                                        name: 'created',
                                                        xtype:'displayfield'
                                                    }]
                                           }
                                      }
                                    ],

                            buttons: [{
                                text:'Submit',
                                disabled:true
                            },{
                                text: 'Close',
                                handler: function(){
                                    EBS.window.userInfo.hide();
                                }
                            }]
                        });
                    }

            /* EOF EDITOR TEST */











            // create the Grid
            encode = true;
            local = false;
            this.filters = new Ext.ux.grid.GridFilters({
                                    // encode and local configuration options defined previously for easier reuse
                                    encode: false, // json encode the filter query
                                    local: false,   // defaults to false (remote filtering)
                                    filters: [{
                                        type: 'string',
                                        dataIndex: 'username'
                                    },{
                                        type: 'string',
                                        dataIndex: 'fullname'
                                    },{
                                        type: 'numeric',
                                        dataIndex: 'ballance'
                                    }, {
                                        type: 'date',
                                        dataIndex: 'created'
                                    }/*, {
                                        type: 'list',
                                        dataIndex: 'size',
                                        options: ['small', 'medium', 'large', 'extra large'],
                                        phpMode: true
                                    }*/
                                   ]
                                });
            this.pagination = new Ext.PagingToolbar({
                           pageSize: 80,
                           store: EBS.store.users,
                           displayInfo: true,
                           dispalyMsg: 'Displaying {0} - {1} of {2}',
                           emptyMsg: 'No Media Found',
                           plugins: [new Ext.ux.SlidingPager(), filters]

                        });

             Ext.apply(this, {
                                store: EBS.store.users,
                                plugins: [this.filters],
                                columns: [
                                    {
                                        header   : 'Username',
                                        sortable : true,
                                        width    : 85,
                                        locked: true,
                                        dataIndex: 'username',
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                    {
                                        header   : 'Fullname',
                                        sortable : true,
                                        //autoexpand:true,
                                        width:200,
                                        dataIndex: 'fullname',
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                    {
                                        header   : 'Created',
                                        width    : 115,
                                        sortable : true,
                                  //      renderer : Ext.util.Format.dateRenderer('Y-m-d h:i a'),
                                        dataIndex: 'created'
                                    },

                                    {
                                        header   : 'Email',
                                        width    : 115,
                                        sortable : true,
                                        dataIndex: 'email',
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                    {
                                        header   : 'Ballance',
                                        width    : 115,
                                        sortable : true,
                                        renderer : 'usMoney',
                                        dataIndex: 'ballance'
                                    },

                                    {
                                        xtype: 'actioncolumn',
                                        width: 30,
                                        items: [{
                                                icon   : media + 'icons/16/new/page_edit.png',  // Use a URL in the icon config
                                                tooltip: 'Action icon',
                                                handler: function(grid, rowIndex, colIndex) {
                                                    //console.log(grid, rowIndex, colIndex);
                                                    //Ext.MessageBox.alert('Action button', 'Sample data. Sample data. Sample data.')
                                                    rec = EBS.store.users.getAt(rowIndex);
                                                    EBS.window.userInfo.show(this);
                                                    Ext.getCmp('user-info').getForm().loadRecord(rec);

                                                    /*EBS.window.userInfo.getForm().load({
                                                                        params: {
                                                                            uid: EBS.store.users.getAt(rowIndex)
                                                                        }
                                                                    });*/


                                                }
                                            }
                                        ]
                                    }
                                ],
                                stripeRows: true,
                                title: 'Grid',
                                stateful: true,
                                stateId: 'grid',
                                bbar:this.pagination
                });

            EBS.conponents.superclass.initComponent.apply(this, arguments);
         } //initComponent
     });
    Ext.reg("ebs_usersPanel", EBS.conponents.usersGrid);
    EBS.window.keys[EBS.conponents.keys.length] = 'ebs_usersPanel';

























    /*




         EBS.topToolbar = [
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
    // --------------------------------
        EBS.mainPanel = new Ext.Panel({
                    id: 'main-panel',
                    region: 'center',
                    layout:'border',
                    defaults:{
                        region:'center'
                    },
                    tbar:EBS.topToolbar,
                    bbar:EBS.bottomToolbar,
                    items: [mainPanel]
                });*/


        //if(typeof(topToolbar)=='object' && topToolbar.length>0)
         //   EBS.mainPanel.tbar = topToolbar;
        //if(typeof(bottomToolbar)=='object' && bottomToolbar.length>0)
       //     EBS.mainPanel.tbar = bottomToolbar;


    // Load datastorages















});
