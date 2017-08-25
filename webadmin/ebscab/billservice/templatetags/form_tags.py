# -*- coding: utf-8 -*-

from django import template
from django.forms.widgets import CheckboxInput


register = template.Library()


class FormFieldNode(template.Node):

    def __init__(self, field_var, tmpl, template_vars, params):
        self.field_var = template.Variable(field_var)
        self.tmpl = tmpl
        self.template_vars = template_vars
        self.params = params

    def render(self, context):
        field = self.field_var.resolve(context)
        if isinstance(field.field.widget, CheckboxInput):
            tmpl = 'checkbox'
        else:
            tmpl = self.tmpl
        t = template.loader.get_template('lib/tags/form_fields/%s.html' % tmpl)
        _context = {'field': field}
        for var in self.template_vars:
            tmpl_var = template.Variable(var)
            try:
                _context[var] = tmpl_var.resolve(context)
            except template.VariableDoesNotExist:
                pass
        for param in self.params:
            _context[param] = True
        return t.render(_context)


@register.tag
def form_field(parser, token):
    """
    Тэг для отрисовки поля формы.
    Формат:
    {% form_field <field> <name> [template_var1, template_var2, 'argument1', 'argument2', ...] %}
    field - поле формы (переменная шаблона)
    name - имя шаблона например, block, inline, tr и т.д. Должен совпадать
    с названием шаблона: block.html, inline.html ... Может быть без кавычек.
    Допускается вложенность: custom/username = username.html в папке custom
    После этих двух обязательных аргументов может быть любое количество необязательных,
    если без кавычек - это должна быть переменная шаблона, если в кавычках - любой
    произвольный параметр.
    Произвольные параметры передаются в шаблон со значением True.
    Примеры:
    {% for field in form %}
        {% form_field field block forloop %}
    {% endfor %}

    {% form_field form.username block 'last' %}
    """
    args = token.split_contents()
    template_vars = []
    params = []

    try:
        field_var = args[1]
        tmpl = args[2].strip('\'"')
    except:
        raise template.TemplateSyntaxError, "Form_field tag arguments error."

    if len(args) > 3:
        args = args[3:]
        for arg in args:
            if arg[0] in ('"', "'") and arg[len(arg) - 1] == arg[0]:
                params.append(str(arg[1:len(arg) - 1]))
            else:
                template_vars.append(arg)

    return FormFieldNode(field_var, tmpl, template_vars, params)
