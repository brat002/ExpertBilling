// Aurora Menu v1.0
// Design and conception by Aurora Studio http://www.aurora-studio.co.uk
// Plugin development by Invent Partners http://www.inventpartners.com
// Copyright Invent Partners & Aurora Studio 2009

var auroraMenuSpeed = 150;
$(document).ready(function(){
	
	$.cookie('testcookie' , 'expanded')
	$('.auroramenu').each(function(){
			var tag_a = $(this).children('a');
			var next_tag = tag_a.next();
			if ($.cookie('arMenu_' + next_tag.attr('id')) == 1) {
				next_tag.css("display", "none");
				tag_a.attr('onClick', 'auroraMenuItem(\'' + this.id + '\'); return false;');
			}
			else {
				tag_a.attr('onClick', 'auroraMenuItem(\'' + this.id + '\'); return false;');
			};
	});
});
function auroraMenuItem(sender){
	var next_tag = jQuery('#'+sender).children('a').next()
	
	if (next_tag.is(":visible")){
		next_tag.slideUp(auroraMenuSpeed);
		next_tag.css('display','none');
		$.cookie('arMenu_' + next_tag.attr('id'), 1);
	}
	else{
		next_tag.slideDown(auroraMenuSpeed);
		$.cookie('arMenu_' + next_tag.attr('id'), 0);
		next_tag.css('display','block');
	};
};