/**
  * Ext 2.0 Linked Combos Tutorial
  * by Jozef Sakalos, aka Saki
  * http://extjs.com/learn/Tutorial:Linked_Combos_Tutorial_for_Ext_2
  */
 
// reference local blank image
Ext.BLANK_IMAGE_URL = '../resources/images/default/s.gif';
 
Ext.namespace('LCombo', 'LCombo.countries', 'LCombo.cities');
 
LCombo.countries = [
     ['USA', 'United States of America']
    ,['D', 'Germany']
    ,['F', 'France']
    ,['GB', 'Great Britain']
];
 
LCombo.cities = [
     [1, 'USA', 'New York']
    ,[2, 'USA', 'Cleveland']
    ,[3, 'USA', 'Austin']
    ,[4, 'USA', 'Los Angeles']
    ,[5, 'D', 'Berlin']
    ,[6, 'D', 'Bonn']
    ,[7, 'F', 'Paris']
    ,[8, 'F', 'Nice']
    ,[9, 'GB', 'London']
    ,[10, 'GB', 'Glasgow']
    ,[11, 'GB', 'Liverpool']
];
 
// create application
LCombo.app = function() {
    // do NOT access DOM from here; elements don't exist yet
 
    // private variables
 
    // private functions
 
    // public space
    return {
 
        // public methods
        init: function() {
            var form = new Ext.FormPanel({
                 renderTo:document.body
                ,width: 400
                ,height: 300
                ,style:'margin:16px'
                ,bodyStyle:'padding:10px'
                ,title:'Linked Combos'
                ,defaults: {xtype:'combo'}
                ,items:[{
                     fieldLabel:'Select Country'
                    ,displayField:'country'
                    ,valueField:'cid'
                    ,store: new Ext.data.SimpleStore({
                         fields:['cid', 'country']
                        ,data:LCombo.countries
                    })
                    ,triggerAction:'all'
                    ,mode:'local'
                    ,listeners:{select:{fn:function(combo, value) {
                        var comboCity = Ext.getCmp('combo-city');        
                        comboCity.clearValue();
                        comboCity.store.filter('cid', combo.getValue());
                        }}
                    }
 
                },{
                     fieldLabel:'Select City'
                    ,displayField:'city'
                    ,valueField:'id'
                    ,id:'combo-city'
                    ,store: new Ext.data.SimpleStore({
                         fields:['id', 'cid', 'city']
                        ,data:LCombo.cities
                    })
                    ,triggerAction:'all'
                    ,mode:'local'
                    ,lastQuery:''
                }]
            });
        }
    };
}(); // end of app
 
// end of file