// Aurora Menu v1.0
// Design and conception by Aurora Studio http://www.aurora-studio.co.uk
// Plugin development by Invent Partners http://www.inventpartners.com
// Copyright Invent Partners & Aurora Studio 2009

var auroraMenuSpeed = 150;
$(document).ready(function(){
	
	$.cookie('testcookie' , 'expanded')
	$('.auroramenu').each(function(){
			var sender = jQuery(this)
			var tag_a = $(this).find('a.link');
			var next_tag = $(this).children('div.content');
			if ($.cookie('arMenu_' + next_tag.attr('id')) == 1) {
				next_tag.css("display", "none");
			};
			tag_a.bind('click', function (){
			var next_tag = sender.children('div.content')
			if (next_tag.is(":visible")){
				next_tag.slideUp(auroraMenuSpeed);
				next_tag.css('display','none');
				$.cookie('arMenu_' + next_tag.attr('id'), 1);
			}
			else{
				next_tag.slideDown(auroraMenuSpeed);
				next_tag.css('display','block');
				$.cookie('arMenu_' + next_tag.attr('id'), 0);
				
			};
			});
	});
});
