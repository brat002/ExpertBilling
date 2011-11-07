Ext.onReady(function(){
   // Menu containing actions
    var tabActions = new Ext.Panel({
    	frame:true,
    	title: 'Actions',
    	collapsible:true,
    	contentEl:'actions',
    	titleCollapse: true
    });
 
    // Parent Panel to hold actions menu
    var actionPanel = new Ext.Panel({
    	id:'action-panel',
    	region:'west',
    	split:true,
    	collapsible: true,
    	collapseMode: 'mini',
    	width:200,
    	minWidth: 150,
    	border: false,
    	baseCls:'x-plain',
    	items: [tabActions]
    });
 
    // Main (Tabbed) Panel
    var tabPanel = new Ext.TabPanel({
		region:'center',
		deferredRender:false,
		autoScroll: true, 
		margins:'0 4 4 0',
		activeTab:0,
		items:[{
			id:'tab1',
			contentEl:'tabs',
    		title: 'Main',
    		closable:false,
    		autoScroll:true
		}]
    });
 
    // Configure viewport
    viewport = new Ext.Viewport({
           layout:'border',
           items:[actionPanel,tabPanel]});
});