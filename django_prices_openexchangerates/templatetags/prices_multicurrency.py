from django.template import Library
from django_prices.templatetags import prices

from .. import exchange_currency

register = Library()


@register.simple_tag
def gross_in_currency(price, currency, **kwargs):
    converted_price = exchange_currency(price, currency)
    converted_price = converted_price.quantize('.01')
    return prices.gross(converted_price, **kwargs)


@register.simple_tag
def net_in_currency(price, currency, **kwargs):
    converted_price = exchange_currency(price, currency)
    converted_price = converted_price.quantize('.01')
    return prices.net(converted_price, **kwargs)


@register.simple_tag
def tax_in_currency(price, currency, **kwargs):
    converted_price = exchange_currency(price, currency)
    converted_price = converted_price.quantize('.01')
    return prices.tax(converted_price, **kwargs)
