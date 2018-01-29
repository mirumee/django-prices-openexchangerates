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
def discount_amount_in_currency(discount, value, currency):
    value = exchange_currency(value, to_currency=currency)
    discount_amount = exchange_currency(discount.amount, to_currency=currency)
    discount.amount = discount_amount
    return (value | discount) - value


@register.filter
def amount(obj, format='text'):
    return prices_i18n.amount(obj, format=format)
