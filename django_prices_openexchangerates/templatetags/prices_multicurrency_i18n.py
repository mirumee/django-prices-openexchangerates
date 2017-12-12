from django.template import Library
from django_prices.templatetags import prices_i18n
from prices import Price

from .. import exchange_currency

register = Library()


@register.simple_tag
def discount_amount_in_currency(discount, price, currency):
    price = exchange_currency(price, to_currency=currency)
    discount_amount = exchange_currency(discount.amount, to_currency=currency)
    discount.amount = discount_amount
    return (price | discount) - price
