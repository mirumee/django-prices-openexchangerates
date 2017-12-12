# coding: utf-8
from __future__ import unicode_literals

from decimal import Decimal

# import mock
import pytest
from prices import Amount, Price
from django_prices_openexchangerates.models import (
    ConversionRate, get_rates, CACHE_KEY, CACHE_TIME)
from django_prices_openexchangerates.templatetags import (
    prices_multicurrency_i18n as prices_i18n)
from django_prices_openexchangerates import (
    CurrencyConversion, exchange_currency)


RATES = {
    'EUR': Decimal(2),
    'GBP': Decimal(4),
    'BTC': Decimal(10)}


@pytest.fixture
def base_currency(db, settings):
    settings.OPENEXCHANGERATES_BASE_CURRENCY = 'BTC'


@pytest.fixture(autouse=True)
def conversion_rates(db):
    rates = []
    for currency, value in RATES.items():
        rate = ConversionRate.objects.create(
            to_currency=currency, rate=RATES[currency])
        rates.append(rate)
    return rates


def test_the_same_currency_uses_no_conversion():
    amount = Amount(10, currency='USD')
    converted = exchange_currency(amount, 'USD')
    assert converted == amount


def test_base_currency_to_another():
    converted = exchange_currency(Amount(10, currency='USD'), 'EUR')
    assert converted.currency == 'EUR'
    assert converted is not None


def test_convert_another_to_base_currency():
    base_amount = Amount(10, currency='EUR')
    converted_amount = exchange_currency(base_amount, 'USD')
    assert converted_amount.currency == 'USD'


def test_convert_two_non_base_currencies():
    base_amount = Amount(10, currency='EUR')
    converted_amount = exchange_currency(base_amount, 'GBP')
    assert converted_amount.currency == 'GBP'


def test_convert_price_uses_passed_dict():
    base_amount = Amount(10, currency='USD')

    def custom_get_rate(currency):
        data = {'GBP': Decimal(5)}
        return data[currency]

    converted_amount = exchange_currency(
        base_amount, 'GBP', get_rate=custom_get_rate)
    # self.assertFalse(mock_qs.called)
    assert converted_amount.currency == 'GBP'


def test_two_base_currencies_the_same_currency_uses_no_conversion():
    amount = Amount(10, currency='USD')
    converted = exchange_currency(amount, 'USD')
    assert converted == amount


def test_two_base_currencies_base_currency_to_another():
    converted = exchange_currency(Amount(10, currency='USD'), 'EUR')
    assert converted.currency == 'EUR'
    assert converted is not None


def test_two_base_currencies_convert_another_to_base_currency():
    base_amount = Amount(10, currency='EUR')
    converted_amount = exchange_currency(base_amount, 'USD')
    assert converted_amount.currency == 'USD'


def test_two_base_currencies_convert_two_non_base_currencies():
    base_amount = Amount(10, currency='EUR')
    converted_amount = exchange_currency(base_amount, 'GBP')
    assert converted_amount.currency == 'GBP'


def test_two_base_currencies_convert_price_uses_passed_dict():
    base_amount = Amount(10, currency='USD')

    def custom_get_rate(currency):
        data = {'GBP': Decimal(5)}
        return data[currency]

    converted_amount = exchange_currency(
        base_amount, 'GBP', get_rate=custom_get_rate)
    assert converted_amount.currency == 'GBP'


def test_two_base_currencies_convert_price_uses_db_when_dict_not_passed():
    base_amount = Amount(10, currency='USD')

    converted_amount = exchange_currency(
        base_amount, 'GBP')
    assert converted_amount.currency == 'GBP'


def test_repr():
    currency_base = 'USD'
    to_currency = 'EUR'
    modifier = CurrencyConversion(
        base_currency=currency_base, to_currency=to_currency,
        rate=Decimal('0.5'))
    expected = "CurrencyConversion(%r, %r, rate=Decimal('0.5'))" % (
        currency_base, to_currency)
    assert repr(modifier) == expected


# def test_gross_in_currency_with_kwargs():
#     price = Price(net=Amount(Decimal('1.23456789'), currency='USD'),
#                   gross=Amount(Decimal('1.23456789'), currency='USD'))
#     result = prices_i18n.gross_in_currency(price, 'EUR', html=True)
#     assert result == u'<span class="currency">€</span>2.47'
#
#
# def test_tax_in_currency_with_kwargs():
#     price = Price(net=Amount(Decimal(1), currency='USD'),
#                   gross=Amount(Decimal('2.3456'), currency='USD'))
#     result = prices_i18n.tax_in_currency(price, 'EUR', html=True)
#     assert result == u'<span class="currency">€</span>2.69'
#
#
# def test_net_in_currency_with_kwargs():
#     price = Price(net=Amount(Decimal('1.23456789'), currency='USD'),
#                   gross=Amount(Decimal('2.3456'), currency='USD'))
#     result = prices_i18n.net_in_currency(price, 'EUR', html=True)
#     assert result == u'<span class="currency">€</span>2.47'


# @mock.patch('django_prices_openexchangerates.models.cache')
# def test_get_rates_caches_results(mock_cache, conversion_rates):
#     get_rates(qs=conversion_rates)
#     mock_cache.get.assert_called_with(CACHE_KEY)
#
#
# @mock.patch('django_prices_openexchangerates.models.cache')
# def test_get_rates_force_update_cache(mock_cache, conversion_rates):
#     expected_cache_content = {
#         rate.to_currency: rate for rate in conversion_rates}
#     rates = get_rates(qs=conversion_rates, force_refresh=True)
#     mock_cache.set.assert_called_with(
#         CACHE_KEY, expected_cache_content, CACHE_TIME)
#     assert rates == expected_cache_content
