# coding: utf-8
from __future__ import unicode_literals

import functools
from decimal import Decimal

# import mock
import pytest
from prices import (
    Money, TaxedMoney, MoneyRange, TaxedMoneyRange, percentage_discount)
from django_prices_openexchangerates import (
    CurrencyConversion, exchange_currency)
from django_prices_openexchangerates.models import ConversionRate, get_rates
from django_prices_openexchangerates.templatetags import (
    prices_multicurrency as rates_prices,
    prices_multicurrency_i18n as rates_prices_i18n)


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
    value = Money(10, currency='USD')
    converted_value = exchange_currency(value, 'USD')
    assert converted_value == value


def test_base_currency_to_another():
    value = Money(10, currency='USD')
    converted_value = exchange_currency(value, 'EUR')
    assert converted_value.currency == 'EUR'
    assert converted_value is not None


def test_convert_another_to_base_currency():
    value = Money(10, currency='EUR')
    converted_value = exchange_currency(value, 'USD')
    assert converted_value.currency == 'USD'


def test_convert_two_non_base_currencies():
    value = Money(10, currency='EUR')
    converted_value = exchange_currency(value, 'GBP')
    assert converted_value.currency == 'GBP'


def test_convert_value_uses_passed_dict():
    value = Money(10, currency='USD')

    def custom_get_rate(currency):
        data = {'GBP': Decimal(5)}
        return data[currency]

    converted_value = exchange_currency(value, 'GBP', get_rate=custom_get_rate)
    assert converted_value.currency == 'GBP'


def test_two_base_currencies_the_same_currency_uses_no_conversion():
    value = Money(10, currency='USD')
    converted_value = exchange_currency(value, 'USD')
    assert converted_value == value


def test_two_base_currencies_base_currency_to_another():
    value = Money(10, currency='USD')
    converted_value = exchange_currency(value, 'EUR')
    assert converted_value.currency == 'EUR'
    assert converted_value is not None


def test_two_base_currencies_convert_another_to_base_currency():
    value = Money(10, currency='EUR')
    converted_value = exchange_currency(value, 'USD')
    assert converted_value.currency == 'USD'


def test_two_base_currencies_convert_two_non_base_currencies():
    value = Money(10, currency='EUR')
    converted_value = exchange_currency(value, 'GBP')
    assert converted_value.currency == 'GBP'


def test_two_base_currencies_convert_price_uses_passed_dict():
    value = Money(10, currency='USD')

    def custom_get_rate(currency):
        data = {'GBP': Decimal(5)}
        return data[currency]

    converted_value = exchange_currency(value, 'GBP', get_rate=custom_get_rate)
    assert converted_value.currency == 'GBP'


def test_two_base_currencies_convert_price_uses_db_when_dict_not_passed():
    value = Money(10, currency='USD')
    converted_value = exchange_currency(value, 'GBP')
    assert converted_value.currency == 'GBP'


def test_exchange_currency_for_money_range():
    value = MoneyRange(Money(10, 'USD'), Money(15, 'USD'))

    value_converted = exchange_currency(value, 'GBP')
    assert value_converted.currency == 'GBP'
    assert value_converted.start.currency == 'GBP'
    assert value_converted.stop.currency == 'GBP'


def test_exchange_currency_for_money_range_uses_passed_dict():
    value = MoneyRange(Money(10, 'USD'), Money(15, 'USD'))

    def custom_get_rate(currency):
        data = {'GBP': Decimal(2)}
        return data[currency]

    value_converted = exchange_currency(value, 'GBP', get_rate=custom_get_rate)
    assert value_converted.currency == 'GBP'
    assert value_converted.start.currency == 'GBP'
    assert value_converted.start.amount == 20
    assert value_converted.stop.currency == 'GBP'
    assert value_converted.stop.amount == 30


def test_exchange_currency_for_taxed_money_range():
    value = TaxedMoneyRange(TaxedMoney(Money(10, 'USD'), Money(12, 'USD')),
                            TaxedMoney(Money(20, 'USD'), Money(24, 'USD')))

    value_converted = exchange_currency(value, 'GBP')
    assert value_converted.currency == 'GBP'
    assert value_converted.start.currency == 'GBP'
    assert value_converted.start.net.currency == 'GBP'
    assert value_converted.start.gross.currency == 'GBP'
    assert value_converted.stop.currency == 'GBP'
    assert value_converted.stop.net.currency == 'GBP'
    assert value_converted.stop.gross.currency == 'GBP'


def test_exchange_currency_for_taxed_money_range_uses_passed_dict():
    value = TaxedMoneyRange(TaxedMoney(Money(10, 'USD'), Money(12, 'USD')),
                            TaxedMoney(Money(20, 'USD'), Money(24, 'USD')))

    def custom_get_rate(currency):
        data = {'GBP': Decimal(2)}
        return data[currency]

    value_converted = exchange_currency(value, 'GBP', get_rate=custom_get_rate)
    assert value_converted.currency == 'GBP'
    assert value_converted.start.currency == 'GBP'
    assert value_converted.start.net.currency == 'GBP'
    assert value_converted.start.net.amount == 20
    assert value_converted.start.gross.currency == 'GBP'
    assert value_converted.start.gross.amount == 24
    assert value_converted.stop.currency == 'GBP'
    assert value_converted.stop.net.currency == 'GBP'
    assert value_converted.stop.net.amount == 40
    assert value_converted.stop.gross.currency == 'GBP'
    assert value_converted.stop.gross.amount == 48


def test_repr():
    currency_base = 'USD'
    to_currency = 'EUR'
    modifier = CurrencyConversion(
        base_currency=currency_base, to_currency=to_currency,
        rate=Decimal('0.5'))
    expected = "CurrencyConversion(%r, %r, rate=Decimal('0.5'))" % (
        currency_base, to_currency)
    assert repr(modifier) == expected


def test_template_filter_money_in_currency():
    value = Money(Decimal('1.23456789'), currency='USD')
    result = rates_prices.in_currency(value, currency='EUR')
    assert result == Money(Decimal('2.47'), currency='EUR')


def test_template_filter_money_in_currency_amount():
    value = Money(Decimal('1.23456789'), currency='USD')
    result = rates_prices.in_currency(value, currency='EUR')
    result = rates_prices.amount(result)
    assert result == '2.47 <span class="currency">EUR</span>'


def test_template_filter_amount_i18n_in_currency():
    value = Money(Decimal('1.23456789'), currency='USD')
    result = rates_prices_i18n.in_currency(value, currency='EUR')
    assert result == Money(Decimal('2.47'), currency='EUR')


def test_template_filter_amount_i18n_in_currency_amount():
    value = Money(Decimal('1.23456789'), currency='USD')
    result = rates_prices_i18n.in_currency(value, 'EUR')
    result = rates_prices_i18n.amount(result)
    assert result == '€2.47'


def test_template_filter_discount_amount_in_currency():
    value = TaxedMoney(Money(1, 'USD'), Money(5, 'USD'))
    discount = functools.partial(percentage_discount, percentage=50)
    result = rates_prices_i18n.discount_amount_in_currency(
        discount, value, 'GBP')
    assert result == TaxedMoney(Money(-4, 'GBP'), Money(-10, 'GBP'))


def test_get_rates_caches_results(conversion_rates):
    result = get_rates(qs=conversion_rates)
    assert all(currency in result.keys() for currency in ['BTC', 'GBP', 'EUR'])


def test_get_rates_force_update_cache(conversion_rates):
    expected_cache_content = {
        rate.to_currency: rate for rate in conversion_rates}
    rates = get_rates(qs=conversion_rates, force_refresh=True)
    assert rates == expected_cache_content


def test_currency_conversion_apply_to_money():
    conversion = CurrencyConversion(
        base_currency='USD', to_currency='EUR', rate=2)
    value = Money(10, 'USD')
    value_converted = conversion.apply(value)
    assert value_converted.currency == 'EUR'
    assert value_converted.amount == 20


def test_currency_conversion_apply_to_taxed_money():
    conversion = CurrencyConversion(
        base_currency='USD', to_currency='EUR', rate=2)
    value = TaxedMoney(Money(10, 'USD'), Money(12, 'USD'))
    value_converted = conversion.apply(value)
    assert value_converted.currency == 'EUR'
    assert value_converted.net.currency == 'EUR'
    assert value_converted.net.amount == 20
    assert value_converted.gross.currency == 'EUR'
    assert value_converted.gross.amount == 24
