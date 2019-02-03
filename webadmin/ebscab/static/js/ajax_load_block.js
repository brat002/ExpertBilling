function ajax_load_block(id, url, data,kwargs, callbacks){
	if (jQuery(kwargs).attr('is_loader')==true)
						jQuery(id).html('<center><img src="/static/img/ajax-loader.gif"/></center>')
	jQuery(document).ready(function(){
		jQuery.ajax({
			url: url,
			data: data,
			beforeSend: function(){
				if (jQuery(callbacks).attr('beforeSend'))	{
					if (jQuery(kwargs).attr('object_before')) {
						callbacks['beforeSend'](kwargs['object_before'])
					}
					else
					{
						callbacks['beforeSend']()
					}
				}
			},

			success: function(data, status){
				if (jQuery(callbacks).attr('success')) {
					if (jQuery(kwargs).attr('object_success')) {
						callbacks['success']( data,status, kwargs['object_success'])
					}
					else
					{
						callbacks['success'](data,status)
					}
				}
				else {
					jQuery(id).html(data);
				}
			}
		})

	})
}
