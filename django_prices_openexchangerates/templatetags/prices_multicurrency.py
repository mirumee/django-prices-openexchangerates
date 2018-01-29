from django.template import Library

from django_prices.templatetags import prices

from .. import exchange_currency

register = Library()


@register.filter
def in_currency(value, currency, **kwargs):
    converted_value = exchange_currency(value, currency)
    converted_value = converted_value.quantize('.01')
    return converted_value


@register.filter
def amount(obj):
    return prices.amount(obj)
