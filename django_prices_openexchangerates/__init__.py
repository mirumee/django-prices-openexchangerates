from __future__ import unicode_literals

import operator
from decimal import Decimal

from django.conf import settings
from prices import History, Price, PriceModifier, PriceRange

BASE_CURRENCY = getattr(settings, 'OPENEXCHANGERATES_BASE_CURRENCY', 'USD')

CENTS = Decimal('0.01')

default_app_config = 'django_prices_openexchangerates.apps.DjangoPricesOpenExchangeRatesConfig'


class CurrencyConversion(PriceModifier):

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
        history = History(price_obj, operator.__or__, self)
        return Price(net=price_obj.net * self.rate,
                     gross=price_obj.gross * self.rate,
                     currency=self.to_currency, history=history)


def convert_price(price, to_currency):
    from .models import ConversionRate

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
    try:
        rate = ConversionRate.objects.get_rate(rate_currency)
    except ConversionRate.DoesNotExist:  # noqa
        raise ValueError('No conversion rate for %s' % (rate_currency, ))
    if reverse_rate:
        conversion_rate = 1 / rate.rate
    else:
        conversion_rate = rate.rate
    conversion = CurrencyConversion(
        base_currency=price.currency,
        to_currency=to_currency,
        rate=conversion_rate)
    return conversion.apply(price)


def exchange_currency(price, to_currency):
    if isinstance(price, PriceRange):
        return PriceRange(
            exchange_currency(price.min_price, to_currency),
            exchange_currency(price.max_price, to_currency))
    if price.currency != BASE_CURRENCY:
        # Convert to default currency
        price = convert_price(price, BASE_CURRENCY)
    return convert_price(price, to_currency)
