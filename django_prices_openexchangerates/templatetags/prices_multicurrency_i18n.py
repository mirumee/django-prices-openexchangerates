from django.template import Library

from django_prices.templatetags import prices_i18n

from .. import exchange_currency

register = Library()


@register.filter
def in_currency(amount, currency, **kwargs):
    converted_amount = exchange_currency(amount, currency)
    converted_amount = converted_amount.quantize('.01')
    return converted_amount


@register.simple_tag
def discount_amount_in_currency(discount, amount, currency):
    amount = exchange_currency(amount, to_currency=currency)
    discount_amount = exchange_currency(discount.amount, to_currency=currency)
    discount.amount = discount_amount
    return (amount | discount) - amount


@register.filter
def amount(obj, format='text'):
    return prices_i18n.amount(obj, format=format)
