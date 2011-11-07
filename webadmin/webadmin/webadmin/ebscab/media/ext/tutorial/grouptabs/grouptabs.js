/*!
 * Ext JS Library 3.2.1
 * Copyright(c) 2006-2010 Ext JS, Inc.
 * licensing@extjs.com
 * http://www.extjs.com/license
 */
Ext.onReady(function() {
	Ext.QuickTips.init();
    
    // create some portlet tools using built in Ext tool ids
    var tools = [{
        id:'gear',
        handler: function(){
            Ext.Msg.alert('Message', 'The Settings tool was clicked.');
        }
    },{
        id:'close',
        handler: function(e, target, panel){
            panel.ownerCt.remove(panel, true);
        }
    }];

    var viewport = new Ext.Viewport({
        layout:'fit',
        items:[{
            xtype: 'grouptabpanel',
    		tabWidth: 185,
    		activeGroup: 0,
    		items: [{
    			mainItem: 0,
    			items: [
    			
              {
                    xtype: 'portal',
                    title: 'Обзор системы',
                    tabTip: 'Dashboard tabtip',
                    items:[{
                        columnWidth:.33,
                        style:'padding:10px 0 10px 10px',
                        items:[{
                            title: 'Grid in a Portlet',
                            layout:'fit',
                            tools: tools,
                            items: new SampleGrid([0, 2, 3])
                        },{
                            title: 'Another Panel 1',
                            tools: tools,
                            html: Ext.example.shortBogusMarkup
                        }]
                    },{
                        columnWidth:.33,
                        style:'padding:10px 0 10px 10px',
                        items:[{
                            title: 'Panel 2',
                            tools: tools,
                            html: Ext.example.shortBogusMarkup
                        },{
                            title: 'Another Panel 2',
                            tools: tools,
                            html: Ext.example.shortBogusMarkup
                        }]
                    },{
                        columnWidth:.33,
                        style:'padding:10px',
                        items:[{
                            title: 'Panel 3',
                            tools: tools,
                            html: Ext.example.shortBogusMarkup
                        },{
                            title: 'Another Panel 3',
                            tools: tools,
                            html: Ext.example.shortBogusMarkup
                        }]
                    }]                    
                },
                
        {
    				title: 'Аккаунты',
                    layout: 'fit',
                    iconCls: 'x-icon-tickets',
                    tabTip: 'Tickets tabtip',
                    style: 'padding: 10px;',
    				items: [new SampleGrid([0,1,2,3,4])]
    			},
          {
    				title: 'Тарифные планы',
                    layout: 'fit',
                    iconCls: 'x-icon-tickets',
                    tabTip: 'Tickets tabtip',
                    style: 'padding: 10px;',
    				items: [new SampleGrid([0,1,2,3,4])]
    			}, 
          {
    				title: 'Платежи и списания',
                    layout: 'fit',
                    iconCls: 'x-icon-tickets',
                    tabTip: 'Tickets tabtip',
                    style: 'padding: 10px;',
    				items: [new SampleGrid([0,1,2,3,4])]
    			}, 
                 {
    				title: 'Сообщения и новости',
                    iconCls: 'x-icon-subscriptions',
                    tabTip: 'Subscriptions tabtip',
                    style: 'padding: 10px;',
					layout: 'fit',
    				items: [{
						xtype: 'tabpanel',
						activeTab: 1,
						items: [{
							title: 'Nested Tabs',
							html: Ext.example.shortBogusMarkup
						}]	
					}]	
    			},
          {
    				title: 'Subscriptions1',
                    iconCls: 'x-icon-subscriptions',
                    tabTip: 'Subscriptions tabtip',
                    style: 'padding: 10px;',
					layout: 'fit',
    				items: [{
						xtype: 'tabpanel',
						activeTab: 1,
						items: [{
							title: 'Nested Tabs',
							html: Ext.example.shortBogusMarkup
						},
{
							title: 'Nested Tabs2',
							html: Ext.example.shortBogusMarkup
						}
             ]	
					},
          
          ]	
    			},
           {
    				title: 'Users',
                    iconCls: 'x-icon-users',
                    tabTip: 'Users tabtip',
                    style: 'padding: 10px;',
    				html: Ext.example.shortBogusMarkup			
    			}]
            }, {
                expanded: true,
                items: [{title: 'Конфигурация', iconCls: 'x-icon-configuration', style: 'padding: 10px;', tabTip: 'Configuration tabtip'},{
                    title: 'Серверы доступа',
                    iconCls: 'x-icon-templates',
                    tabTip: 'Configuration tabtip',
                    style: 'padding: 10px;',
                    html: Ext.example.shortBogusMarkup 
                }, {
                    title: 'Расчётные периоды',
                    iconCls: 'x-icon-templates',
                    tabTip: 'Templates tabtip',
                    style: 'padding: 10px;',
                    html: Ext.example.shortBogusMarkup
                }
              , {
                    title: 'Периоды тарификации',
                    iconCls: 'x-icon-templates',
                    tabTip: 'Templates tabtip',
                    style: 'padding: 10px;',
                    html: Ext.example.shortBogusMarkup
                }      
              , {
                    title: 'Классы трафика',
                    iconCls: 'x-icon-templates',
                    tabTip: 'Templates tabtip',
                    style: 'padding: 10px;',
                    html: Ext.example.shortBogusMarkup
                }       
              , {
                    title: 'Системные пользователи',
                    iconCls: 'x-icon-templates',
                    tabTip: 'Templates tabtip',
                    style: 'padding: 10px;',
                    html: Ext.example.shortBogusMarkup
                }  
              , {
                    title: 'Правила смены ТП',
                    iconCls: 'x-icon-templates',
                    tabTip: 'Templates tabtip',
                    style: 'padding: 10px;',
                    html: Ext.example.shortBogusMarkup
                }   
              , {
                    title: 'Подключаемые услуги',
                    iconCls: 'x-icon-templates',
                    tabTip: 'Templates tabtip',
                    style: 'padding: 10px;',
                    html: Ext.example.shortBogusMarkup
                }  
              , {
                    title: 'IP пулы',
                    iconCls: 'x-icon-templates',
                    tabTip: 'Templates tabtip',
                    style: 'padding: 10px;',
                    html: Ext.example.shortBogusMarkup
                }    
              , {
                    title: 'Шаблоны документов',
                    iconCls: 'x-icon-templates',
                    tabTip: 'Templates tabtip',
                    style: 'padding: 10px;',
                    html: Ext.example.shortBogusMarkup
                }     
              , {
                    title: 'Логи системы',
                    iconCls: 'x-icon-templates',
                    tabTip: 'Templates tabtip',
                    style: 'padding: 10px;',
                    html: Ext.example.shortBogusMarkup
                }      
              , {
                    title: 'Логи операций',
                    iconCls: 'x-icon-templates',
                    tabTip: 'Templates tabtip',
                    style: 'padding: 10px;',
                    html: Ext.example.shortBogusMarkup
                }                                                                                                
                ]
            }
            , {
                expanded: true,
                items: [{title: 'Статистика', iconCls: 'x-icon-configuration', style: 'padding: 10px;', tabTip: 'Configuration tabtip'},{
                    title: 'Монитор сессий',
                    iconCls: 'x-icon-templates',
                    tabTip: 'Configuration tabtip',
                    style: 'padding: 10px;',
                    html: Ext.example.shortBogusMarkup 
                }, {
                    title: 'NetFlow статистика',
                    iconCls: 'x-icon-templates',
                    tabTip: 'Templates tabtip',
                    style: 'padding: 10px;',
                    html: Ext.example.shortBogusMarkup
                }
                                                                                              
                ]
            }
            , {
                expanded: true,
                items: [{title: 'Отчёты', iconCls: 'x-icon-configuration', style: 'padding: 10px;', tabTip: 'Configuration tabtip'},{
                    title: 'Отчёт по сессиям',
                    iconCls: 'x-icon-templates',
                    tabTip: 'Configuration tabtip',
                    style: 'padding: 10px;',
                    html: Ext.example.shortBogusMarkup 
                }, {
                    title: 'Отчёт по загрузке канала',
                    iconCls: 'x-icon-templates',
                    tabTip: 'Templates tabtip',
                    style: 'padding: 10px;',
                    html: Ext.example.shortBogusMarkup
                }
              , {
                    title: 'Отчёт по объёму трафика',
                    iconCls: 'x-icon-templates',
                    tabTip: 'Templates tabtip',
                    style: 'padding: 10px;',
                    html: Ext.example.shortBogusMarkup
                }                                                                           
                ]
            }  
            , {
                expanded: true,
                items: [{title: 'Карточная платформа', iconCls: 'x-icon-configuration', style: 'padding: 10px;', tabTip: 'Configuration tabtip'},{
                    title: 'Нереализованные карты',
                    iconCls: 'x-icon-templates',
                    tabTip: 'Configuration tabtip',
                    style: 'padding: 10px;',
                    html: Ext.example.shortBogusMarkup 
                }, {
                    title: 'Дилеры',
                    iconCls: 'x-icon-templates',
                    tabTip: 'Templates tabtip',
                    style: 'padding: 10px;',
                    html: Ext.example.shortBogusMarkup
                }
                                                                                  
                ]
            }         
            ]

		}]
    });
});
