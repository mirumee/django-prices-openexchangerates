from django.template import Library

from django_prices.templatetags import prices

from .. import exchange_currency

register = Library()


@register.filter
def in_currency(base, currency, **kwargs):
    converted_base = exchange_currency(base, currency)
    converted_base = converted_base.quantize('.01')
    return converted_base


@register.filter
def amount(obj):
    return prices.amount(obj)
