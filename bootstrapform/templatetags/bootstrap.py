from django import forms
from django import VERSION
from django.contrib.admin import widgets
from django.template import Context
from django.template.loader import get_template
from django import template

from bootstrapform import config

register = template.Library()


@register.filter
def bootstrap(element):
    markup_classes = {'label': '', 'value': '', 'single_value': ''}
    return render(element, markup_classes)


@register.filter
def bootstrap_inline(element):
    markup_classes = {'label': 'sr-only', 'value': '', 'single_value': ''}
    return render(element, markup_classes)


@register.filter
def bootstrap_horizontal(element, label_cols='col-sm-2 col-lg-2'):

    markup_classes = {'label': label_cols, 'value': '', 'single_value': ''}

    for cl in label_cols.split(' '):
        splitted_class = cl.split('-')

        try:
            value_nb_cols = int(splitted_class[-1])
        except ValueError:
            value_nb_cols = config.BOOTSTRAP_COLUMN_COUNT

        if value_nb_cols >= config.BOOTSTRAP_COLUMN_COUNT:
            splitted_class[-1] = config.BOOTSTRAP_COLUMN_COUNT
        else:
            offset_class = cl.split('-')
            offset_class[-1] = 'offset-' + str(value_nb_cols)
            splitted_class[-1] = str(config.BOOTSTRAP_COLUMN_COUNT - value_nb_cols)
            markup_classes['single_value'] += ' ' + '-'.join(offset_class)
            markup_classes['single_value'] += ' ' + '-'.join(splitted_class)

        markup_classes['value'] += ' ' + '-'.join(splitted_class)

    return render(element, markup_classes)


@register.filter
def add_input_classes(field):
    if not is_checkbox(field) and not is_multiple_checkbox(field) \
       and not is_radio(field) and not is_file(field) \
       and not is_select(field) and not is_splitdatetime(field):
        field_classes = field.field.widget.attrs.get('class', '')
        field_classes += ' form-control'
        field.field.widget.attrs['class'] = field_classes
    elif is_select(field):
        field_classes = field.field.widget.attrs.get('class', '')
        field_classes += ' combobox input-large form-control'
        field.field.widget.attrs['class'] = field_classes


def render(element, markup_classes):
    common_context = {
        'field_template': config.BOOTSTRAP_FIELD_TEMPLATE,
        'form_template': config.BOOTSTRAP_FORM_TEMPLATE,
        'formset_template': config.BOOTSTRAP_FORMSET_TEMPLATE,
    }

    if isinstance(element, forms.forms.BoundField):
        add_input_classes(element)
        template = get_template(config.BOOTSTRAP_FIELD_TEMPLATE)
        context = {'field': element, 'classes': markup_classes, 'form': element.form}
    else:
        has_management = getattr(element, 'management_form', None)
        if not hasattr(element, 'required_css_class'):
            element.required_css_class = 'required'
        if has_management:
            for form in element.forms:
                for field in form.visible_fields():
                    add_input_classes(field)

            template = get_template(config.BOOTSTRAP_FORMSET_TEMPLATE)
            context = {'formset': element, 'classes': markup_classes}
        else:
            for field in element.visible_fields():
                add_input_classes(field)

            template = get_template(config.BOOTSTRAP_FORM_TEMPLATE)
            context = {'form': element, 'classes': markup_classes}

    context = common_context.update(context)
    
    if VERSION[0] * 1000 + VERSION[1] < 1008:
        context = Context(context)

    return template.render(context)


@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxInput)


@register.filter
def is_multiple_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxSelectMultiple)


@register.filter
def is_radio(field):
    return isinstance(field.field.widget, forms.RadioSelect)


@register.filter
def is_select(field):
    return isinstance(field.field.widget, forms.Select)


@register.filter
def is_file(field):
    return isinstance(field.field.widget, forms.FileInput)


@register.filter
def is_splitdatetime(field):
    return isinstance(field.field.widget, widgets.AdminSplitDateTime)
