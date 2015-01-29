from decimal import Decimal

import mock
from django.test import TestCase, override_settings
from prices import Price

from .utils import exchange_currency
from .models import ConversionRate
from . import CurrencyConversion


RATES = {
    'USD': Decimal(1),
    'EUR': Decimal(2),
    'GBP': Decimal(4),
    'BTC': Decimal(10)}


def get_rates(currency):
    return ConversionRate(to_currency=currency, rate=RATES[currency])


@mock.patch('django_prices_openexchangerates.models.ConversionRate.objects.get_rate',
            side_effect=get_rates)
class CurrencyConversionTestCase(TestCase):
    def test_the_same_currency_uses_no_conversion(self, mock_qs):
        price = Price(10, currency='USD')
        converted = exchange_currency(price, 'USD')
        self.assertIsNone(converted.history)
        self.assertEqual(converted, price)

    def test_base_currency_to_another(self, mock_qs):
        converted = exchange_currency(Price(10, currency='USD'), 'EUR')
        self.assertEqual(converted.currency, 'EUR')
        self.assertIsNotNone(converted.history)
        modifier = converted.history.right
        self.assertEqual(modifier.base_currency, 'USD')
        self.assertEqual(modifier.to_currency, 'EUR')

    def test_convert_another_to_base_currency(self, mock_qs):
        base_price = Price(10, currency='EUR')
        converted_price = exchange_currency(base_price, 'USD')
        self.assertEqual(converted_price.currency, 'USD')
        self.assertIsNotNone(converted_price.history)
        # 1 / rate should be used to calculate final amount
        conversion = converted_price.history.right
        self.assertEqual(conversion.base_currency, 'EUR')
        self.assertEqual(conversion.to_currency, 'USD')
        self.assertEqual(conversion.rate, 1 / RATES['EUR'])

    def test_convert_two_non_base_currencies(self, mock_qs):
        base_price = Price(10, currency='EUR')
        converted_price = exchange_currency(base_price, 'GBP')
        self.assertEqual(converted_price.currency, 'GBP')
        self.assertIsNotNone(converted_price.history)
        # Price should have two modifiers
        # EUR to USD and then USD to GBP
        first_operation = converted_price.history.left.history
        self.assertEqual(first_operation.left, base_price)
        self.assertEqual(first_operation.right.base_currency, 'EUR')
        self.assertEqual(first_operation.right.to_currency, 'USD')
        second_operation = converted_price.history.right
        self.assertEqual(second_operation.base_currency, 'USD')
        self.assertEqual(second_operation.to_currency, 'GBP')


@mock.patch('django_prices_openexchangerates.models.ConversionRate.objects.get_rate',
            side_effect=get_rates)
class CurrencyConversionWithAnotherBaseCurrencyTestCase(CurrencyConversionTestCase):

    @override_settings(OPENEXCHANGE_BASE_CURRENCY='BTC')
    def test_the_same_currency_uses_no_conversion(self, mock_qs):
        pass

    @override_settings(OPENEXCHANGE_BASE_CURRENCY='BTC')
    def test_base_currency_to_another(self, mock_qs):
        pass

    @override_settings(OPENEXCHANGE_BASE_CURRENCY='BTC')
    def test_convert_another_to_base_currency(self, mock_qs):
        pass

    @override_settings(OPENEXCHANGE_BASE_CURRENCY='BTC')
    def test_convert_two_non_base_currencies(self, mock_qs):
        pass


class CurrencyConversionModifierTestCase(TestCase):
    def test_repr(self):
        modifier = CurrencyConversion(base_currency='USD', to_currency='EUR',
                                      rate=Decimal('0.5'))
        expected = "CurrencyConversion(base_currency='USD', to_currency='EUR' rate=Decimal('0.5'))"
        self.assertEqual(repr(modifier), expected)
