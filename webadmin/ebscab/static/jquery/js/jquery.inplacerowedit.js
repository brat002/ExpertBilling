(function($) {
    $.fn.inplacerowedit = function(options) {
        var ops = $.extend({}, $.fn.inplacerowedit.defaults, options);
        $(this).find(ops.editbuttonselector).click(function(e) {
            e.preventDefault();
            var editbtn = $(this);
            var savebtn = $('<a href="#"></a>').text(ops.updatebuttontext).addClass(ops.updatebuttonclass);
            var cancelbtn = $('<a href="#"></a>').text(ops.cancelbuttontext).addClass(ops.cancelbuttonclass);
            var td = editbtn.parents('td');
            var tr = editbtn.parents('tr:eq(0)');
            tr.children('td').each(function(i) {
                var self = $(this);
                
                if (ops.inputs[i] == null || ops.inputs[i].disabled)
                    return;
                    
                // hide contents
                var text = self.text();
                var html = self.html();
                var hiddenDiv = $('<div />').css('display', 'none').addClass('inplacerowedit-hidden').text(html);
                self.html(hiddenDiv);

                // add input
                var inputOptions = getInputOptions(ops.inputs[i]);
                var inputFunc = $.fn.inplacerowedit.inputtypes[inputOptions.type];
                var input = inputFunc(text, inputOptions.options, self.width());
                input.attr('name', inputOptions.name);
                if ($.isFunction(inputOptions.after))
                    inputOptions.after(input);
                self.append(input);
            });
            tr.find(ops.buttonareaselector).hide();
            var btndiv = $('<div />');
            btndiv.append(savebtn);
            btndiv.append('&nbsp;');
            btndiv.addClass('buttons');
            btndiv.append(cancelbtn);
            
            savebtn.click(function(e) {
                e.preventDefault();

                // build data
                var data = tr.find(':input').serializeArray();
                ops.beforesubmit(tr, data);

                // submit
                $.ajax({
                    async: false,
                    cache: false,
                    data: data,
                    dataType: 'json',
                    url: ops.url,
                    type: ops.method,
                    success: function(data, textStatus) {
                        window.location.reload()
                        return
                    	btndiv.remove();
                        tr.children('td').each(function(i) {
                        if (ops.inputs[i] == null || ops.inputs[i].disabled)
                            return;
                        $(this).html($(this).html().replace($(this).text(), data.model[ops.inputs[i].name]));
                        });
                        tr.find(ops.buttonareaselector).show();
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        cancelbtn.click();
                    }
                });
            });
            cancelbtn.click(function(e) {
                btndiv.remove();
                tr.children('td').each(function(i) {
                    if (ops.inputs[i] == null || ops.inputs[i].disabled)
                        return;
                    var hiddenDiv = $(this).children('div.inplacerowedit-hidden');
                    //$(this).empty();
                    $(this).html(hiddenDiv.text());
                });
                tr.find(ops.buttonareaselector).show();
                e.preventDefault();
            });
            td.append(btndiv);

        });
        return $(this);
    };
//    $.fn.clearinvalid = function(field) {
//        var arr = Array();
//        $.each(invalidFields, function(i, val) {
//            if (val[0] == field)
//                arr[arr.length] = i;
//        });
//        arr.sort(function(a, b) { return a - b })
//        var offset = 0;
//        $.each(arr, function(i, val) {
//            arr.splice(parseInt(val) + offset, 1);
//            offset++;
//        });
//        alert(invalidFields.length);
//        if (invalidFields.length == 0)
//            savebtn.removeAttr('disabled');
//    };
//    $.fn.invalidate = function(field, error) {
//        var val = [field, error];
//        if ($.inArray(val, invalidFields) < 0) {
//            invalidFields[invalidFields.length] = val;
//            savebtn.attr('disabled', 'true');
//        }
//    };
//    $.fn.isvalid = function() {
//        return invalidFields.length == 0
//    }
    $.fn.inplacerowedit.defaults = {
        beforesubmit: function(){},
        buttonareaselector: 'div.buttons',
        editbuttonselector: 'a.edit',
        updatebuttontext: 'save',
        updatebuttonclass: 'update',
        cancelbuttontext: 'cancel',
        cancelbuttonclass: 'cancel',
        url: '',
        method: 'POST'
    };
    $.fn.inplacerowedit.inputtypes = Array();
    $.fn.inplacerowedit.inputtypes['text'] = function(val, options, tdwidth) {
        return $('<input />').attr('type', 'text').width(tdwidth).val(val);
    };
    $.fn.inplacerowedit.inputtypes['select'] = function(val, options, tdheight, tdwidth) {
        var select = $('<select />').width(60);//.val(val);
        for(var i = 0; i < options.length ; i++){
            var option = $('<option />').val(options[i].value).attr('name', options[i].name).html(options[i].name);
            select.append(option);
       }
        return select;
    };    
    $.fn.inplacerowedit.inputtypes['datepicker'] = function(val, options, tdwidth) {
        var width = tdwidth < 75 ? tdwidth : 75;
        var textbox = $.fn.inplacerowedit.inputtypes['text'](val, options, width);
        textbox.datepicker(options);
        return textbox;
    };
    function getInputOptions(setting) {
        var type = setting.type ? setting.type : 'text';
        var name = setting.name ? setting.name : '';
        var options = setting.option ? setting.option : null;
        var after = setting.afterCreate ? setting.afterCreate : null;

        return { type: type, options: options, name: name, after: after };
    }
})(jQuery);