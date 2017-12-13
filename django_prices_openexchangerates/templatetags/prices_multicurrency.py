from django.template import Library

from .. import exchange_currency

register = Library()


@register.filter
def in_currency(amount, currency, **kwargs):
    converted_amount = exchange_currency(amount, currency)
    converted_amount = converted_amount.quantize('.01')
    return converted_amount
