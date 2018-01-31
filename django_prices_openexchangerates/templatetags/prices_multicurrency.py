from django.template import Library

from django_prices.templatetags import prices
from prices import Money

from .. import Exchangeable, exchange_currency

register = Library()


@register.filter
def in_currency(base: Exchangeable, currency: str, **kwargs) -> Exchangeable:
    converted_base = exchange_currency(base, currency)
    converted_base = converted_base.quantize('.01')
    return converted_base


@register.filter
def amount(obj: Money) -> str:
    return prices.amount(obj)
