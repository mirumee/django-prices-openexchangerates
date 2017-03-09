# coding: utf-8
from decimal import Decimal

import mock
import django
from django.test import TestCase, override_settings
from prices import Price
from .templatetags.prices_multicurrency import (
    gross_in_currency, tax_in_currency, net_in_currency)
from .templatetags import prices_multicurrency_i18n as prices_i18n
from . import CurrencyConversion, exchange_currency

django.setup()

RATES = {
    'USD': Decimal(1),
    'EUR': Decimal(2),
    'GBP': Decimal(4),
    'BTC': Decimal(10)}


def mock_rates(currency):
    from .models import ConversionRate
    return ConversionRate(to_currency=currency, rate=RATES[currency])


@mock.patch('django_prices_openexchangerates.models.ConversionRate.objects.get_rate',
            side_effect=mock_rates)
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
            side_effect=mock_rates)
class CurrencyConversionWithAnotherBaseCurrencyTestCase(CurrencyConversionTestCase):

    @override_settings(OPENEXCHANGERATES_BASE_CURRENCY='BTC')
    def test_the_same_currency_uses_no_conversion(self, mock_qs):
        pass

    @override_settings(OPENEXCHANGERATES_BASE_CURRENCY='BTC')
    def test_base_currency_to_another(self, mock_qs):
        pass

    @override_settings(OPENEXCHANGERATES_BASE_CURRENCY='BTC')
    def test_convert_another_to_base_currency(self, mock_qs):
        pass

    @override_settings(OPENEXCHANGERATES_BASE_CURRENCY='BTC')
    def test_convert_two_non_base_currencies(self, mock_qs):
        pass


class CurrencyConversionModifierTestCase(TestCase):
    def test_repr(self):
        modifier = CurrencyConversion(base_currency='USD', to_currency='EUR',
                                      rate=Decimal('0.5'))
        expected = "CurrencyConversion('USD', 'EUR', rate=Decimal('0.5'))"
        self.assertEqual(repr(modifier), expected)

@mock.patch('django_prices_openexchangerates.models.ConversionRate.objects.get_rate',
            side_effect=mock_rates)
class PricesMultiCurrencyTestCase(TestCase):

    def test_gross_in_currency(self, mock_qs):
        price = Price(net=Decimal('1.23456789'), currency='USD')
        result = gross_in_currency(price, 'EUR')
        self.assertEqual(result, {'currency': 'EUR',
                                  'amount': Decimal('2.47')})

    def test_tax_in_currency(self, mock_qs):
        price = Price(net=Decimal(1), gross=Decimal('2.3456'),
                      currency='USD')
        result = tax_in_currency(price, 'EUR')
        self.assertEqual(result, {'currency': 'EUR',
                                  'amount': Decimal('2.69')})

    def test_net_in_currency(self, mock_qs):
        price = Price(net=Decimal('1.23456789'), currency='USD')
        result = net_in_currency(price, 'EUR')
        self.assertEqual(result, {'currency': 'EUR',
                                  'amount': Decimal('2.47')})

    def test_gross_in_currency_with_kwargs(self, mock_qs):
        price = Price(net=Decimal('1.23456789'), currency='USD')
        result = prices_i18n.gross_in_currency(price, 'EUR', html=True)
        self.assertEqual(result, u'<span class="currency">€</span>2.47')

    def test_tax_in_currency_with_kwargs(self, mock_qs):
        price = Price(net=Decimal(1), gross=Decimal('2.3456'),
                      currency='USD')
        result = prices_i18n.tax_in_currency(price, 'EUR', html=True)
        self.assertEqual(result, u'<span class="currency">€</span>2.69')

    def test_net_in_currency_with_kwargs(self, mock_qs):
        price = Price(net=Decimal('1.23456789'), currency='USD')
        result = prices_i18n.net_in_currency(price, 'EUR', html=True)
        self.assertEqual(result, u'<span class="currency">€</span>2.47')


@mock.patch('django_prices_openexchangerates.models.cache')
class CachingManagerTestCase(TestCase):

    def test_get_rates_caches_results(self, mock_cache):
        from .models import get_rates, CACHE_KEY
        mock_qs = [mock_rates(currency) for currency in RATES]
        get_rates(qs=mock_qs)
        mock_cache.get.assert_called_with(CACHE_KEY)

    def test_get_rates_force_update_cache(self, mock_cache):
        from .models import get_rates, CACHE_KEY, CACHE_TIME
        mock_qs = [mock_rates(currency) for currency in RATES]
        expected_cache_content = {rate.to_currency: rate for rate in mock_qs}
        rates = get_rates(qs=mock_qs, force_refresh=True)
        mock_cache.set.assert_called_with(
            CACHE_KEY, expected_cache_content, CACHE_TIME)
        self.assertEqual(rates, expected_cache_content)
