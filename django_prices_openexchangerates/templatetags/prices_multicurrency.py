from django.template import Library
from django_prices.templatetags import prices_i18n

from ..utils import exchange_currency

register = Library()


@register.simple_tag
def gross_in_currency(price, currency):
    converted_price = exchange_currency(price, currency)
    return prices_i18n.gross(converted_price)


@register.simple_tag
def net_in_currency(price, currency):
    converted_price = exchange_currency(price, currency)
    return prices_i18n.net(converted_price)


@register.simple_tag
def tax_in_currency(price, currency):
    converted_price = exchange_currency(price, currency)
    return prices_i18n.tax(converted_price)
