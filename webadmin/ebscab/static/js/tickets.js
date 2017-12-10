var sorted_option={'object':'',
							'reverse':''};

function archived_ticket(table_id, ticket_id){
	table_id = jQuery(table_id);
	jQuery.ajax({
		url:"/helpdesk/ajax/archived/tickets/",
		data:{'ticket_id':ticket_id},
		type:"POST",
		success:function(data){
			load_data( table_id.parent().parent(), data['order_by'], data['order_by_reverse'], data['count_in_page'])
		}
	});
};

function show_tickets(sender, div_content)
{
	sender = jQuery(sender);
	var table_tickets = sender.parent().parent().parent().parent();
	div_content = jQuery("div"+div_content);
	var data = jQuery(div_content).data(div_content.attr('name'));

	var val = jQuery(sender).find('option:selected').val();
	data['count_in_page']=val;
	data['order_by_reverse']=false;
	load_data(div_content,data['order_by'],data['order_by_reverse'], val);
};

function sorted(sender, table_tickets){
	sender = jQuery(sender);
	var data  = table_tickets.data(table_tickets.attr('name'));

	if (sorted_option['object']!=table_tickets.attr('name') || data['order_by']!=sender.attr('class') )
		{
			data['order_by'] = sender.attr('class');
			sorted_option['object']=table_tickets.attr('name');
			data['order_by_reverse'] = false;
		};

	if (data['order_by_reverse']){
		data['order_by_reverse'] = false;
	}
	else{
		data['order_by_reverse'] = true;
	};
	load_data(table_tickets,data['order_by'],data['order_by_reverse'], data['count_in_page'] );
};

function load_data(sender, order_by,order_by_reverse, count)
{
			sender = jQuery(sender)
			var obj_list = sender.attr('name').split("_");
			var object = obj_list[0];
			var object_id = obj_list[1];
			var data= {"object":object, 'object_id':object_id};
			if (count)
				data["count"]=count;
			if(order_by)
				data["order_by"]=order_by;
			if (order_by_reverse)
				data['order_by_reverse']=order_by_reverse;
			var content = sender.children("div.content_tickets");
			ajax_load_block(content,"/helpdesk/ajax/load/table/tickets/",
								  data,
								  {"is_loader":true},
								  {"success":function(data){
								  	content.html(data);
									update_table(sender);
									jQuery("table.tickets").sortable({
											connectWith:".tickets",
											items:"tr:not(.title_table)",
											stop:function(e, ui){
												var object_var = jQuery(ui.item).parent().parent().attr('id').split("_");
												var change_ticket = {'id':jQuery(ui.item).children('.id').text(),
																			  'object':object_var[1],
																			  'object_id':object_var[2]}
												jQuery.ajax({
													url:"/helpdesk/ajax/update/owner/tickets/",
													data:change_ticket
												})
											}
									})
								  }});
};

function load_users(sender)
{
			var data= {}
			var content = jQuery("div.content_users")
			$('input.data').each(function(n,element){
									if($(element).attr('type')!="button") {
										 data[$(element).attr('name')]=$(element).val();
									}
								});
			ajax_load_block(content,"/helpdesk/users/",
								  data,
								  {"is_loader":true}
								  )
}

function show_table(sender, is_show)
{
	if (is_show){
		var data = sender.next().data(sender.next().attr('name'));
		load_data(sender.next(), data['order_by'], data['order_by_reverse'], data['count_in_page']);
		sender.css('font-weight', 'bold');
		sender.children('a.link').children('img').attr('src','/static/img/open2.gif');
	}
	else{
		jQuery(sender.next()).stopTime(jQuery(sender).attr('name'));
		sender.css('font-weight', 'normal');
		sender.children('a.link').children('img').attr('src','/static/img/close.gif');
	};
};

function show_hide_table(sender, is_show)
{
	if (is_show){
		var data = sender.next().data(sender.next().attr('name'));
		sender.css('font-weight', 'bold');
		sender.children('a.link').children('img').attr('src','/static/img/open2.gif');
	}
	else{
		jQuery(sender.next()).stopTime(jQuery(sender).attr('name'));
		sender.css('font-weight', 'normal');
		sender.children('a.link').children('img').attr('src','/static/img/close.gif');
	};
};


function update_table(sender){
	var name = sender.attr('name');

	var seconds =parseInt(sender.find('select[name="time"]').val())*60;
	var data = sender.data(name);

	if (data['order_by_reverse']){
		sender.find('.title_table').children('.'+data['order_by']).children('img').attr('src','/static/img/down.gif');
	}
	else{
		sender.find('.title_table').children('.'+data['order_by']).children('img').attr('src','/static/img/up.gif');
	}
	jQuery(sender).stopTime(jQuery(sender).attr('name'));
	sender.everyTime(seconds+"s",name,function(){
				load_data(sender, data['order_by'], data['order_by_reverse'], data['count_in_page']);
			},1)
};

function deleted_tickets(table_id){
	table_id = jQuery(table_id);
	var is_deleted = table_id.find('input[name="is_deleted"]:checked');
	var ids_tickets =[];
	var data = table_id.parent().parent().data(table_id.parent().parent().attr('name'));
	is_deleted.parent().parent().find('.id').each(function(){
	jQuery.merge(ids_tickets,[parseInt(jQuery(this).text())]);
	})

	jQuery.ajax({
		url:"/helpdesk/ajax/deleted/tickets/",
		data:{'ids_tickets':JSON.stringify(ids_tickets)},
		type:"POST",
		success:function(data){
			load_data( table_id.parent().parent(), data['order_by'], data['order_by_reverse'], data['count_in_page'])
		}
	});
};
