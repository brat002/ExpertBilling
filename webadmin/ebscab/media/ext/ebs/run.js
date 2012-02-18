Ext.onReady(function(){


    //EBS.base.init();



    EBS.messages.exclamation = Ext.get('exclamation');
    if(EBS.messages.exclamation){
        EBS.messages.timer = setInterval(function(){
            EBS.messages.exclamation.fadeOut();
            setTimeout(function(){
                EBS.messages.exclamation.fadeIn();
            }, EBS.messages.fadeSpeed);
        },EBS.messages.fadeInterval);
    }

    
  



});


//Ext.onReady(EBS.base.init);