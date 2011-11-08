Ext.onReady(function(){


    EBS.base.init();


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