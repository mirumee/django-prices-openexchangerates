# coding: utf-8
from decimal import Decimal

import mock
import django
from django.test import TestCase, override_settings
from prices import Amount, Price
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
        amount = Amount(10, currency='USD')
        converted = exchange_currency(amount, 'USD')
        self.assertEqual(converted, amount)

    def test_base_currency_to_another(self, mock_qs):
        converted = exchange_currency(Amount(10, currency='USD'), 'EUR')
        self.assertEqual(converted.currency, 'EUR')
        self.assertIsNotNone(converted)

    def test_convert_another_to_base_currency(self, mock_qs):
        base_amount = Amount(10, currency='EUR')
        converted_amount = exchange_currency(base_amount, 'USD')
        self.assertEqual(converted_amount.currency, 'USD')

    def test_convert_two_non_base_currencies(self, mock_qs):
        base_amount = Amount(10, currency='EUR')
        converted_amount = exchange_currency(base_amount, 'GBP')
        self.assertEqual(converted_amount.currency, 'GBP')

    def test_convert_price_uses_passed_dict(self, mock_qs):
        base_amount = Amount(10, currency='USD')

        def custom_get_rate(currency):
            data = {'GBP': Decimal(5)}
            return data[currency]

        converted_amount = exchange_currency(
            base_amount, 'GBP', get_rate=custom_get_rate)
        self.assertFalse(mock_qs.called)
        self.assertEqual(converted_amount.currency, 'GBP')


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

    @override_settings(OPENEXCHANGERATES_BASE_CURRENCY='BTC')
    def test_convert_price_uses_passed_dict(self, mock_qs):
        pass

    @override_settings(OPENEXCHANGERATES_BASE_CURRENCY='BTC')
    def test_convert_price_uses_db_when_dict_not_passed(self, mock_qs):
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

    def test_gross_in_currency_with_kwargs(self, mock_qs):
        price = Price(net=Amount(Decimal('1.23456789'), currency='USD'),
                      gross=Amount(Decimal('1.23456789'), currency='USD'))
        result = prices_i18n.gross_in_currency(price, 'EUR', html=True)
        self.assertEqual(result, u'<span class="currency">€</span>2.47')

    def test_tax_in_currency_with_kwargs(self, mock_qs):
        price = Price(net=Amount(Decimal(1), currency='USD'),
                      gross=Amount(Decimal('2.3456'), currency='USD'))
        result = prices_i18n.tax_in_currency(price, 'EUR', html=True)
        self.assertEqual(result, u'<span class="currency">€</span>2.69')

    def test_net_in_currency_with_kwargs(self, mock_qs):
        price = Price(net=Amount(Decimal('1.23456789'), currency='USD'),
                      gross=Amount(Decimal('2.3456'), currency='USD'))
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
