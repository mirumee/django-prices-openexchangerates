from typing import Callable, TypeVar

from django.template import Library
from django_prices.templatetags import prices_i18n
from prices import Money, MoneyRange, TaxedMoney, TaxedMoneyRange

from .. import exchange_currency

T = TypeVar('T', Money, MoneyRange, TaxedMoney, TaxedMoneyRange)

register = Library()


@register.filter
def in_currency(base: T, currency: str) -> T:
    converted_base = exchange_currency(base, currency)
    converted_base = converted_base.quantize('.01')
    return converted_base


@register.simple_tag
def discount_amount_in_currency(
        base: T, discount: Callable[[T], T], currency: str) -> T:
    discount_amount = discount(base)
    converted_base = exchange_currency(base, to_currency=currency)
    discount_amount = exchange_currency(discount_amount, to_currency=currency)
    return discount_amount - converted_base
