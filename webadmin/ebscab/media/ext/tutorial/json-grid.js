Ext.onReady(function(){
    Ext.QuickTips.init();

//////////////////
    function onItemToggle(item, pressed){
        Ext.example.msg('Button Toggled', 'Button "{0}" was toggled to {1}.', item.text, pressed);
    }
    var tb = new Ext.Toolbar();
    tb.render('toolbar');

    tb.add({
        icon: 'list-items.gif', // icons can also be specified inline
        text: 'Внести платёж',
        cls: 'x-btn-icon',
        tooltip: '<b>Quick Tips</b><br/>Icon only button with tooltip'
    },{
        icon: 'list-items.gif', // icons can also be specified inline
        text: 'Сменить тариф',
        cls: 'x-btn-icon',
        tooltip: '<b>Quick Tips</b><br/>Icon only button with tooltip'
    });
    tb.doLayout();
/////////////////


    // create the Data Store
    var store = new Ext.data.JsonStore({
        root: 'data',
        //idProperty: 'taskId',
        fields: [
            'username', 'fullname', 'password', 'taskId'
        ],

        // load using script tags for cross domain, if the data in on the same domain as
        // this page, an HttpProxy would be better
        proxy: new Ext.data.HttpProxy({
            url: '/jsonaccounts',
            method: 'POST'
        })
    });
    store.setDefaultSort('username', 'desc');


    

    var grid = new Ext.grid.GridPanel({
        width:700,
        height:500,
        title:'browse accounts',
        store: store,
        trackMouseOver:false,
        disableSelection:false,
        loadMask: true,

        // grid columns
        columns:[{
            id: 'topic', // id assigned so we can apply custom css (e.g. .x-grid-col-topic b { color:#333 })
            header: "username",
            dataIndex: 'username',
            width: 120,
            //renderer: renderTopic,
            sortable: true
        },{
            header: "fullname",
            dataIndex: 'fullname',
            width: 70,
            hidden: false,
            sortable: true
        },{
            header: "password",
            dataIndex: 'password',
            width: 70,
            align: 'right',
            sortable: true
        }
        ,{
            header: "taskId",
            dataIndex: 'taskId',
            width: 70,
            align: 'right',
            sortable: true
        }
        ]


    });

    // render it
    grid.render('example-grid');

    // trigger the data store load
    store.load();
    //alert(store.data.items)

    function renderButtons(title){

        Ext.getBody().createChild({tag: 'h2', html: title});

        new ButtonPanel(
            'Icon and Text (left)',
            [{
                text: 'Внести платёж',
                iconCls: 'add',
                scale: 'large'
            },
            {
                text: 'Сменить тариф',
                iconCls: 'add',
                scale: 'large'
            },
            {
                text: 'Остаток трафика по лимиту',
                iconCls: 'add',
                scale: 'large'
            }    
            ,
            {
                text: 'Остаток предоплаченного трафика',
                iconCls: 'add',
                scale: 'large'
            }      
            ]
        );
      
       }
    renderButtons('Normal Buttons');

    ButtonPanel.override({
        enableToggle: true
    });
    
    
});

// Helper class for organizing the buttons
ButtonPanel = Ext.extend(Ext.Panel, {
    layout:'table',
    defaultType: 'button',
    baseCls: 'x-plain',
    cls: 'btn-panel',
    renderTo : 'example-buttons',
    menu: undefined,
    split: false,

    layoutConfig: {
        columns:3
    },

    constructor: function(desc, buttons){
        // apply test configs
        for(var i = 0, b; b = buttons[i]; i++){
            b.menu = this.menu;
            b.enableToggle = this.enableToggle;
            b.split = this.split;
            b.arrowAlign = this.arrowAlign;
        }
        var items = [{
            xtype: 'box',
            autoEl: {tag: 'h3', html: desc, style:"padding:15px 0 3px;"},
            colspan: 3
        }].concat(buttons);

        ButtonPanel.superclass.constructor.call(this, {
            items: items
        });
    }
});
