from typing import TypeVar

from django.template import Library
from django_prices.templatetags import prices
from prices import Money, MoneyRange, TaxedMoney, TaxedMoneyRange

from .. import exchange_currency

T = TypeVar('T', Money, MoneyRange, TaxedMoney, TaxedMoneyRange)

register = Library()


@register.filter
def in_currency(base: T, currency: str) -> T:
    converted_base = exchange_currency(base, currency)
    converted_base = converted_base.quantize('.01')
    return converted_base


@register.filter
def amount(obj: Money) -> str:
    return prices.amount(obj)
