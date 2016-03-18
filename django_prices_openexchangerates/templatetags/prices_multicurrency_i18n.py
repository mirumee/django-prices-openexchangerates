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


@register.simple_tag
def discount_amount_in_currency(discount, price, currency):
    price = exchange_currency(price, to_currency=currency)
    discount_amount = exchange_currency(discount.amount, to_currency=currency)
    discount.amount = discount_amount
    return (price | discount) - price
