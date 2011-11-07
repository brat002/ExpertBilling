/*!
 * Ext JS Library 3.2.1
 * Copyright(c) 2006-2010 Ext JS, Inc.
 * licensing@extjs.com
 * http://www.extjs.com/license
 */
Ext.onReady(function(){
    // basic tabs 1, built from existing content

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
            }*/
        ],
    }),
    sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
    width: 600,
    height: 300,
    frame: true,
    title: 'Framed with Row Selection and Horizontal Scrolling',
    iconCls: 'icon-grid'
});
//store.loadData(myData);


var form = new Ext.FormPanel({
    title: 'Simple Form with FieldSets',
    //labelWidth: 75, // label settings here cascade unless overridden
    url: 'save-form.php',
    frame:true,
    bodyStyle:'padding:5px 5px 5px 5px',
    width: 700,
    //renderTo: document.body,
    layout:'table', // arrange items in columns
    layoutConfig: {
        // The total column count must be specified here
        columns: 2
    },

    defaults: {      // defaults applied to items
        layout: 'form',
        border: true,
        bodyStyle: 'padding:4px 4px 4px 4px'
    },
    items: [{
        // Fieldset in Column 1
        xtype:'fieldset',
        columnWidth: 0.5,
        title: 'RADIUS параметры',
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
                fieldLabel: 'Идентификатор'
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
});

    var tabs = new Ext.TabPanel({
        renderTo: 'tabs1',
        //width:450,
        activeTab: 0,
        frame:true,
        defaults:{autoHeight: true},
        items:[
            form,
            grid
        ]
    });
//============================
  var spEditWindow = new Ext.Window(
  {
  layout:'fit',
  items:[{
        // Fieldset in Column 2 - Panel inside
        xtype:'fieldset',
        title: 'Расчётный период', // title, header, or checkboxToggle creates          
        autoHeight:true,
        //columnWidth: 0.5,
        checkboxToggle: false,
        collapsed: false, // fieldset initially collapsed
        layout:'fit',
        //rowspan:2,
        items : new Ext.form.FormPanel({
        layout:'form',
        width:450,
        height:450,
          items:[
          {
           fieldLabel: 'Название',
           xtype:'textfield',
          },
          {
          xtype:'checkbox',
          fieldLabel: 'Автостарт'
          }
          ,
          {
          xtype:'combo',
          fieldLabel: 'Продолжительность'
          }
          ]})
        }]
  
  }
  )
  spEditWindow.show();
//============================
});