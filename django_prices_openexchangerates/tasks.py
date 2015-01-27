from __future__ import division
from __future__ import unicode_literals

from decimal import Decimal

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .models import ConversionRate

BASE_URL = r'http://openexchangerates.org/api'
ENDPOINT_LATEST = BASE_URL + r'/latest.json'
try:
    API_KEY = settings.OPENEXCHANGERATES_API_KEY
except AttributeError:
    raise ImproperlyConfigured('OPENEXCHANGERATES_API_KEY is required')


class ExchangeRates(object):

    def __init__(self, rates, default_currency=None):
        self.rates = rates
        self.default_currency = (
            default_currency or settings.DEFAULT_CURRENCY)

    def __getitem__(self, item):
        rate = self.rates[item]
        return rate / self.rates[self.default_currency]


def get_latest_exchange_rates():
    response = requests.get(ENDPOINT_LATEST, params={'app_id': API_KEY})
    response.raise_for_status()
    exchange_data = response.json(parse_int=Decimal, parse_float=Decimal)
    return ExchangeRates(rates=exchange_data['rates'])


def update_conversion_rates():
    exchange_rates = get_latest_exchange_rates()
    conversion_rates = ConversionRate.objects.all()
    for conversion_rate in conversion_rates:
        new_exchange_rate = exchange_rates[conversion_rate.to_currency]
        conversion_rate.rate = new_exchange_rate
        conversion_rate.save()
    return conversion_rates
