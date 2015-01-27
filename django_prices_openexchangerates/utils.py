from prices import Price
import logging

from django.conf import settings
from .models import ConversionRate

logger = logging.getLogger('django_prices_openexchangerates')


def convert_price(price, to_currency=settings.DEFAULT_CURRENCY):
    if price.currency == to_currency:
        return price

    converted_price = price.net

    if to_currency != settings.DEFAULT_CURRENCY:
        try:
            rate = ConversionRate.objects.get_rate(to_currency)
        except ConversionRate.DoesNotExist:
            logger.error('Conversion rate for %s is zero, failed to convert',
                         to_currency)
            raise ValueError(
                'no conversion rate for %s available' % to_currency)

        converted_price = rate.from_base_currency(converted_price)

    # convert the price currency to default currency
    if price.currency != settings.DEFAULT_CURRENCY:
        logger.debug('convert %s %s to %s', converted_price,
                     price.currency, to_currency)
        try:
            rate = ConversionRate.objects.get_rate(price.currency)
        except ConversionRate.DoesNotExist:
            logger.error(
                'tried to convert %s to %s but no conversion rate is '
                'available in the database', price.currency,
                settings.DEFAULT_CURRENCY)
            raise ValueError(
                'no conversion rate for %s available' % to_currency)
        try:
            converted_price = rate.to_base_currency(converted_price)
        except ZeroDivisionError:
            logger.error(
                'Conversion rate for %s is zero, failed to convert',
                rate.to_currency)
            raise ValueError('conversion rate for %s is 0', rate.to_currency)

    return Price(currency=to_currency, net=converted_price,
                 history=price.history)
