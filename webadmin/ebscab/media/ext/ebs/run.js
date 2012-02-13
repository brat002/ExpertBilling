Ext.onReady(function(){


    //EBS.base.init();

	winPanel = new Ext.Window({
		title: 'Sample Window', //Title of the Window 
		//autoHeight: true, //Height of the Window will be auto
		width:500, //Width of the Window
		height:500, //Width of the Window
		layout:'fit',
		//resizable: true, //Resize of the Window, if false - it cannot be resized
		//closable: false, //Hide close button of the Window
		//modal: true, //When modal:true it make the window modal and mask everything behind it when displayed
	
		applyTo:Ext.get('body'),
		items:{xtype:'xaccountspanel'}
		});
	winPanel.show();

    EBS.messages.exclamation = Ext.get('exclamation');
    if(EBS.messages.exclamation){
        EBS.messages.timer = setInterval(function(){
            EBS.messages.exclamation.fadeOut();
            setTimeout(function(){
                EBS.messages.exclamation.fadeIn();
            }, EBS.messages.fadeSpeed);
        },EBS.messages.fadeInterval);
    }

    
    
    setTimeout(function(){
        Ext.get('loading').remove();
        Ext.get('loading-mask').fadeOut({remove:true});
    }, 250);



});


//Ext.onReady(EBS.base.init);