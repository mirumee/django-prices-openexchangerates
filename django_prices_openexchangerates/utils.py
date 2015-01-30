from django.conf import settings

from .models import ConversionRate
from . import CurrencyConversion

BASE_CURRENCY = getattr(settings, 'OPENEXCHANGERATES_BASE_CURRENCY', 'USD')


def _convert_price(price, to_currency):
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
        raise ValueError('No conversion rate for %s' % (price.currency, ))
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
    if price.currency != BASE_CURRENCY:
        # Convert to default currency
        price = _convert_price(price, BASE_CURRENCY)
    return _convert_price(price, to_currency)

