from django.template import Library

from django_prices.templatetags import prices_i18n

from .. import exchange_currency

register = Library()


@register.filter
def in_currency(base, currency, **kwargs):
    converted_base = exchange_currency(base, currency)
    converted_base = converted_base.quantize('.01')
    return converted_base


@register.simple_tag
def discount_amount_in_currency(base, discount, currency):
    discount_amount = discount(base)
    converted_base = exchange_currency(base, to_currency=currency)
    discount_amount = exchange_currency(discount_amount, to_currency=currency)
    return discount_amount - converted_base


@register.filter
def amount(base, format='text'):
    return prices_i18n.amount(base, format=format)
