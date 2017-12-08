from __future__ import unicode_literals

import operator
from decimal import Decimal

from django.conf import settings
from prices import Amount, Price, PriceRange

BASE_CURRENCY = getattr(settings, 'OPENEXCHANGERATES_BASE_CURRENCY', 'USD')

CENTS = Decimal('0.01')

default_app_config = 'django_prices_openexchangerates.apps.DjangoPricesOpenExchangeRatesConfig'


class CurrencyConversion(object):

    '''
    Adds a currency conversion to the price
    '''

    def __init__(self, base_currency, to_currency, rate):
        self.base_currency = base_currency
        self.to_currency = to_currency
        self.rate = rate

    def __repr__(self):
        return ('CurrencyConversion(%r, %r, rate=%r)' % (
                self.base_currency, self.to_currency, self.rate))

    def apply(self, price_obj):
        if isinstance(price_obj, Amount):
            return Amount(
                price_obj.value * self.rate, currency=self.to_currency)


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


def convert_price(price, to_currency, get_rate=get_conversion_rate):
    """
    Converts Price object to specified currency.
    get_rate parameter is a callable that returns proper conversion rate
    """
    if price.currency == to_currency:
        return price
    reverse_rate = False
    if to_currency == BASE_CURRENCY:
        # Fetch exchange rate for price currency and use 1 / rate
        # for conversion
        rate_currency = price.currency
        reverse_rate = True
    else:
        rate_currency = to_currency
    rate = get_rate(rate_currency)

    if reverse_rate:
        conversion_rate = 1 / rate
    else:
        conversion_rate = rate
    conversion = CurrencyConversion(
        base_currency=price.currency,
        to_currency=to_currency,
        rate=conversion_rate)
    return conversion.apply(price)


def exchange_currency(price, to_currency, get_rate=get_conversion_rate):
    """
    Exchanges Price or PriceRange to the specified currency
    """
    if isinstance(price, PriceRange):
        return PriceRange(
            exchange_currency(price.min_price, to_currency),
            exchange_currency(price.max_price, to_currency))
    if price.currency != BASE_CURRENCY:
        # Convert to default currency
        price = convert_price(price, BASE_CURRENCY, get_rate=get_rate)
    return convert_price(price, to_currency, get_rate=get_rate)
