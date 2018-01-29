from django.template import Library

from django_prices.templatetags import prices_i18n

from .. import exchange_currency

register = Library()


@register.filter
def in_currency(value, currency, **kwargs):
    converted_value = exchange_currency(value, currency)
    converted_value = converted_value.quantize('.01')
    return converted_value


@register.simple_tag
def discount_amount_in_currency(discount, price, currency):
    discount_amount = discount(price)
    price = exchange_currency(price, to_currency=currency)
    discount_amount = exchange_currency(discount_amount, to_currency=currency)
    return discount_amount - price


@register.filter
def amount(obj, format='text'):
    return prices_i18n.amount(obj, format=format)
