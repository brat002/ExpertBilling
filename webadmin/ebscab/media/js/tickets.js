var sorted_option={'object':'',
							'reverse':''}

function archived_ticket(sender){
	sender = jQuery(sender)
	var id_ticket=sender.parent().parent().children(".id").text()
	jQuery.ajax({
		url:"/helpdesk/ajax/archived/tickets/",
		data:{'id_ticket':id_ticket, "is_archived":sender.is(":checked")}
	})
}							

function show_tickets(sender, table_id)
{
	sender = jQuery(sender)
	var table_tickets = sender.parent().parent()
	var data = jQuery(table_tickets).data(table_tickets.attr('name'))
	
	var val = jQuery(sender).find('option:selected').val()
	data['count_in_page']=val
	data['order_by_reverse']=false
	load_data(table_tickets,data['order_by'],data['order_by_reverse'], val)
}

function sorted(sender, table_tickets){
	sender = jQuery(sender)
	
	var data  = table_tickets.data(table_tickets.attr('name'))
	
	if (sorted_option['object']!=table_tickets.attr('name') || data['order_by']!=sender.attr('class') )
		{
			data['order_by'] = sender.attr('class')
			sorted_option['object']=table_tickets.attr('name')
			
			data['order_by_reverse'] = false
		}
	if (data['order_by_reverse']){
		data['order_by_reverse'] = false
	}
	else{ 
		data['order_by_reverse'] = true
	}
	
	load_data(table_tickets,data['order_by'],data['order_by_reverse'], data['count_in_page'] )
	
}

function load_data(sender, order_by,order_by_reverse, count)
{
			var obj_list = jQuery(sender).attr('name').split("_")
			var object = obj_list[0]
			var object_id = obj_list[1]
			var data= {"object":object, 'object_id':object_id}
			if (count)
				data["count"]=count
			if(order_by)
				data["order_by"]=order_by
			if (order_by_reverse)
				data['order_by_reverse']=order_by_reverse
			var content = jQuery(sender).children("div.content_tickets")
			ajax_load_block(content,"/helpdesk/ajax/load/table/tickets/",
								  data,
								  {"is_loader":true}, 
								  {"success":function(data){
								  	content.html(data)
									update_table(sender)
									jQuery("table.tickets").sortable({
											connectWith:".tickets",
											items:"tr:not(.title_table)",
											stop:function(e, ui){
												console.info(jQuery(ui.item).parent().parent())
												var object_var = jQuery(ui.item).parent().parent().attr('id').split("_")
												var change_ticket = {id:jQuery(ui.item).children('.id').text(),
																			  object:object_var[1],
																			  object_id:object_var[2]}
												jQuery.ajax({
													url:"/helpdesk/ajax/update/owner/tickets/",
													data:change_ticket
												})
											}
									})
								  }})
}
function show_table(sender, is_show)
{
	if (is_show){
		var data = sender.next().data(sender.next().attr('name'))
		load_data(sender.next(), data['order_by'], data['order_by_reverse'], data['count_in_page'])
		sender.css('background-image','url(/media/img/bg3.gif)'	)
		sender.children('a.link').children('img').attr('src','/media/img/open2.gif')
	}
	else{		
		jQuery(sender.next()).stopTime(jQuery(sender).attr('name'))
		sender.css('background-image','url(/media/img/bg2.gif)'	)
		sender.children('a.link').children('img').attr('src','/media/img/close.gif')
		
	}
}
function update_table(sender){
	var sender = jQuery(sender)
	var name = sender.attr('name')
	var seconds =parseInt(sender.children('div').children('select[name="time"]').val())*60
	var data = sender.data(sender.attr('name'))
	if (data['order_by_reverse']){
		sender.find('.title_table').children('.'+data['order_by']).children('img').attr('src','/media/img/down.gif')
	}
	else{
		sender.find('.title_table').children('.'+data['order_by']).children('img').attr('src','/media/img/up.gif')
	}
	jQuery(sender).stopTime(jQuery(sender).attr('name'))
	
	sender.everyTime(seconds+"s",name,function(){
				load_data(sender, data['order_by'], data['order_by_reverse'], data['count_in_page'])
			},1)
}
jQuery(document).ready(function(){
		
	
		jQuery(".auroramenu").find(' a.link').bind('click',function(){
			var sender = jQuery(this)
			var content = sender.parent()
			show_table(content, content.next().is(":visible"))
		})
		
		jQuery(".auroramenu div.tickets:visible").each(function(){
				var panel_link =  jQuery(this).parent().children('.name_object')
				panel_link.css('background-image','url(/media/img/bg3.gif)')
				panel_link.children('a.link').children('img').attr('src','/media/img/open2.gif')
				var count_in_page=jQuery('select[name="count_in_page"]').val()
				
				jQuery(this).data(jQuery(this).attr('name'), {'order_by':'id',
																	   'order_by_reverse':false, 
																	   'count_in_page':count_in_page})
				load_data(this,'id',false, count_in_page)
			})
	})

