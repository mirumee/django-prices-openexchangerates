from django.template import Library
from django_prices.templatetags import prices_i18n

from .. import exchange_currency

register = Library()


@register.simple_tag  # noqa
def gross_in_currency(price, currency):  # noqa
    converted_price = exchange_currency(price, currency)
    return prices_i18n.gross(converted_price)


@register.simple_tag  # noqa
def net_in_currency(price, currency):  # noqa
    converted_price = exchange_currency(price, currency)
    return prices_i18n.net(converted_price)


@register.simple_tag  # noqa
def tax_in_currency(price, currency):  # noqa
    converted_price = exchange_currency(price, currency)
    return prices_i18n.tax(converted_price)

