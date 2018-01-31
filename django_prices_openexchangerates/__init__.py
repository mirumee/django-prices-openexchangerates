import operator
from decimal import Decimal

from django.conf import settings
from prices import Money, MoneyRange, TaxedMoney, TaxedMoneyRange

BASE_CURRENCY = getattr(settings, 'OPENEXCHANGERATES_BASE_CURRENCY', 'USD')

default_app_config = 'django_prices_openexchangerates.apps.DjangoPricesOpenExchangeRatesConfig'


def get_rate_from_db(currency):
    """
    Fetch currency conversion rate from the database
    """
    from .models import ConversionRate
    try:
        rate = ConversionRate.objects.get_rate(currency)
    except ConversionRate.DoesNotExist:  # noqa
        raise ValueError('No conversion rate for %s' % (currency, ))
    return rate.rate


def get_conversion_rate(from_currency, to_currency, get_rate):
    """
    Get conversion rate to use in exchange
    """
    reverse_rate = False
    if to_currency == BASE_CURRENCY:
        # Fetch exchange rate for base currency and use 1 / rate
        # for conversion
        rate_currency = from_currency
        reverse_rate = True
    else:
        rate_currency = to_currency
    rate = get_rate(rate_currency)

    if reverse_rate:
        conversion_rate = 1 / rate
    else:
        conversion_rate = rate
    return conversion_rate


def exchange_currency(base, to_currency, get_rate=get_rate_from_db):
    """
    Exchanges Money, TaxedMoney and their ranges to the specified currency.
    get_rate parameter is a callable taking single argument (target currency)
    that returns proper conversion rate
    """
    if base.currency == to_currency:
        return base
    if base.currency != BASE_CURRENCY and to_currency != BASE_CURRENCY:
        # Exchange to base currency first
        base = exchange_currency(base, BASE_CURRENCY, get_rate=get_rate)

    conversion_rate = get_conversion_rate(base.currency, to_currency, get_rate)

    if isinstance(base, Money):
        return Money(base.amount * conversion_rate, currency=to_currency)
    if isinstance(base, MoneyRange):
        return MoneyRange(exchange_currency(base.start, to_currency,
                                            get_rate=get_rate),
                          exchange_currency(base.stop, to_currency,
                                            get_rate=get_rate))
    if isinstance(base, TaxedMoney):
        return TaxedMoney(Money(base.net.amount * conversion_rate,
                                currency=to_currency),
                          Money(base.gross.amount * conversion_rate,
                                currency=to_currency))
    if isinstance(base, TaxedMoneyRange):
        return TaxedMoneyRange(exchange_currency(base.start, to_currency,
                                                 get_rate=get_rate),
                               exchange_currency(base.stop, to_currency,
                                                 get_rate=get_rate))
