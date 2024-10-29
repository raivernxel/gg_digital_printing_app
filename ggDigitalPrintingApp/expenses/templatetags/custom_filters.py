from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter(name='add_class')
def add_class(value, arg):
    """
    Adds a CSS class to a form field widget.
    """
    css_classes = value.field.widget.attrs.get('class', '')
    return value.as_widget(attrs={'class': f'{css_classes} {arg}'.strip()})