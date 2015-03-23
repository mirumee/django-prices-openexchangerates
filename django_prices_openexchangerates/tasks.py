from __future__ import division
from __future__ import unicode_literals

from decimal import Decimal

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .models import ConversionRate

ENDPOINT_LATEST = 'http://openexchangerates.org/api/latest.json'
BASE_CURRENCY = getattr(settings, 'OPENEXCHANGERATES_BASE_CURRENCY', 'USD')

try:
    API_KEY = settings.OPENEXCHANGERATES_API_KEY
except AttributeError:
    raise ImproperlyConfigured('OPENEXCHANGERATES_API_KEY is required')


def extract_rate(rates, currency):
    base_rate = rates[BASE_CURRENCY]
    return rates[currency] / base_rate


def get_latest_exchange_rates():
    response = requests.get(ENDPOINT_LATEST,
                            params={'app_id': API_KEY,
                                    'base': BASE_CURRENCY})
    response.raise_for_status()
    return response.json(parse_int=Decimal, parse_float=Decimal)['rates']


def update_conversion_rates():
    exchange_rates = get_latest_exchange_rates()
    conversion_rates = ConversionRate.objects.all()
    for conversion_rate in conversion_rates:
        new_exchange_rate = extract_rate(exchange_rates,
                                         conversion_rate.to_currency)
        conversion_rate.rate = new_exchange_rate
        conversion_rate.save(update_fields=['rate'])
    return conversion_rates
