from __future__ import unicode_literals

import operator
from decimal import Decimal

from django.conf import settings
from prices import Money, MoneyRange, TaxedMoney, TaxedMoneyRange

BASE_CURRENCY = getattr(settings, 'OPENEXCHANGERATES_BASE_CURRENCY', 'USD')

CENTS = Decimal('0.01')

default_app_config = 'django_prices_openexchangerates.apps.DjangoPricesOpenExchangeRatesConfig'


class CurrencyConversion:

    '''
    Adds a currency conversion to the Money or TaxedMoney
    '''

    def __init__(self, base_currency, to_currency, rate):
        self.base_currency = base_currency
        self.to_currency = to_currency
        self.rate = rate

    def __repr__(self):
        return ('CurrencyConversion(%r, %r, rate=%r)' % (
                self.base_currency, self.to_currency, self.rate))

    def apply(self, base):
        if isinstance(base, Money):
            return Money(base.amount * self.rate,
                         currency=self.to_currency)
        if isinstance(base, TaxedMoney):
            return TaxedMoney(Money(base.net.amount * self.rate,
                                    currency=self.to_currency),
                              Money(base.gross.amount * self.rate,
                                    currency=self.to_currency))


def get_conversion_rate(currency):
    """
    Fetch currency conversion rate from the database
    """
    from .models import ConversionRate
    try:
        rate = ConversionRate.objects.get_rate(currency)
    except ConversionRate.DoesNotExist:  # noqa
        raise ValueError('No conversion rate for %s' % (currency, ))
    return rate.rate


def convert_base(base, to_currency, get_rate=get_conversion_rate):
    """
    Converts Money or TaxedMoney to specified currency.
    get_rate parameter is a callable that returns proper conversion rate
    """
    if base.currency == to_currency:
        return base
    reverse_rate = False
    if to_currency == BASE_CURRENCY:
        # Fetch exchange rate for base currency and use 1 / rate
        # for conversion
        rate_currency = base.currency
        reverse_rate = True
    else:
        rate_currency = to_currency
    rate = get_rate(rate_currency)

    if reverse_rate:
        conversion_rate = 1 / rate
    else:
        conversion_rate = rate
    conversion = CurrencyConversion(
        base_currency=base.currency,
        to_currency=to_currency,
        rate=conversion_rate)
    return conversion.apply(base)


def exchange_currency(base, to_currency, get_rate=get_conversion_rate):
    """
    Exchanges Money, TaxedMoney or their ranges to the specified currency
    """
    if isinstance(base, MoneyRange):
        return MoneyRange(
            exchange_currency(base.start, to_currency, get_rate=get_rate),
            exchange_currency(base.stop, to_currency, get_rate=get_rate))
    if isinstance(base, TaxedMoneyRange):
        return TaxedMoneyRange(
            exchange_currency(base.start, to_currency, get_rate=get_rate),
            exchange_currency(base.stop, to_currency, get_rate=get_rate))
    if base.currency != BASE_CURRENCY:
        # Convert to default currency
        base = convert_base(base, BASE_CURRENCY, get_rate=get_rate)
    return convert_base(base, to_currency, get_rate=get_rate)
