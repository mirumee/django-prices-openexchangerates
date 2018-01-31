from typing import Callable

from django.template import Library
from django_prices.templatetags import prices_i18n
from prices import Money

from .. import Exchangeable, exchange_currency

Discount = Callable[[Exchangeable], Exchangeable]

register = Library()


@register.filter
def in_currency(base: Exchangeable, currency: str, **kwargs) -> Exchangeable:
    converted_base = exchange_currency(base, currency)
    converted_base = converted_base.quantize('.01')
    return converted_base


@register.simple_tag
def discount_amount_in_currency(
        base: Exchangeable, discount: Discount, currency: str) -> Exchangeable:
    discount_amount = discount(base)
    converted_base = exchange_currency(base, to_currency=currency)
    discount_amount = exchange_currency(discount_amount, to_currency=currency)
    return discount_amount - converted_base


@register.filter
def amount(base: Money, format='text') -> str:
    return prices_i18n.amount(base, format=format)
