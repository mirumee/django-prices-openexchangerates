# coding: utf-8
import functools
from decimal import Decimal

# import mock
import pytest
from prices import (
    Money, TaxedMoney, MoneyRange, TaxedMoneyRange, percentage_discount)
from django_prices_openexchangerates import exchange_currency
from django_prices_openexchangerates.models import ConversionRate, get_rates
from django_prices_openexchangerates.templatetags import prices_multicurrency


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


def test_conversionrate__str_repr(conversion_rates):
    obj = ConversionRate.objects.get(to_currency='EUR')

    assert str(obj) == '1 USD = 2.0000 EUR'

    obj_repr = repr(obj)
    assert 'ConversionRate' in obj_repr
    assert 'pk={},'.format(obj.pk) in obj_repr
    assert "base_currency='USD'," in obj_repr
    assert "to_currency='EUR'," in obj_repr


def test_the_same_currency_uses_no_conversion():
    value = Money(10, currency='EUR')
    converted_value = exchange_currency(value, 'EUR')
    assert converted_value == value


def test_base_currency_to_another():
    value = Money(10, currency='USD')
    converted_value = exchange_currency(value, 'EUR')
    assert converted_value == Money(20, currency='EUR')


def test_convert_other_currency_to_base_currency():
    value = Money(20, currency='EUR')
    converted_value = exchange_currency(value, 'USD')
    assert converted_value == Money(10, currency='USD')


def test_two_base_currencies_the_same_currency_uses_no_conversion():
    value = Money(10, currency='USD')
    converted_value = exchange_currency(value, 'USD')
    assert converted_value == value


def test_convert_two_non_base_currencies():
    value = Money(20, currency='EUR')
    converted_value = exchange_currency(value, 'GBP')
    assert converted_value == Money(40, currency='GBP')


def test_exchange_currency_uses_passed_conversion_rate():
    value = Money(10, currency='USD')
    custom_rate = Decimal(5)

    converted_value = exchange_currency(
        value, 'GBP', conversion_rate=custom_rate)
    assert converted_value == Money(50, currency='GBP')


def test_two_base_currencies_convert_price_uses_passed_conversion_rate():
    value = Money(10, currency='USD')
    custom_rate = Decimal('4.2')

    converted_value = exchange_currency(
        value, 'GBP', conversion_rate=custom_rate)
    assert converted_value == Money(42, 'GBP')


def test_exchange_currency_for_money_range():
    value = MoneyRange(Money(10, 'USD'), Money(15, 'USD'))

    value_converted = exchange_currency(value, 'GBP')
    assert value_converted.currency == 'GBP'
    assert value_converted.start == Money(40, currency='GBP')
    assert value_converted.stop == Money(60, currency='GBP')


def test_exchange_currency_for_money_range_uses_passed_conversion_rate():
    value = MoneyRange(Money(10, 'USD'), Money(15, 'USD'))
    custom_rate = Decimal(2)

    value_converted = exchange_currency(
        value, 'GBP', conversion_rate=custom_rate)
    assert value_converted.currency == 'GBP'
    assert value_converted.start == Money(20, currency='GBP')
    assert value_converted.stop == Money(30, currency='GBP')


def test_exchange_currency_for_taxed_money():
    value = TaxedMoney(Money(10, 'USD'), Money(12, 'USD'))

    value_converted = exchange_currency(value, 'GBP')
    assert value_converted.currency == 'GBP'
    assert value_converted.net == Money(40, currency='GBP')
    assert value_converted.gross == Money(48, currency='GBP')


def test_exchange_currency_for_taxed_money_uses_passed_conversion_rate():
    value = TaxedMoney(Money(10, 'USD'), Money(12, 'USD'))
    custom_rate = Decimal(2)

    value_converted = exchange_currency(
        value, 'GBP', conversion_rate=custom_rate)
    assert value_converted.currency == 'GBP'
    assert value_converted.net == Money(20, currency='GBP')
    assert value_converted.gross == Money(24, currency='GBP')


def test_exchange_currency_for_taxed_money_range():
    value = TaxedMoneyRange(
        TaxedMoney(Money(10, 'USD'), Money(12, 'USD')),
        TaxedMoney(Money(20, 'USD'), Money(24, 'USD')))

    value_converted = exchange_currency(value, 'GBP')
    assert value_converted.currency == 'GBP'
    assert value_converted.start.currency == 'GBP'
    assert value_converted.start.net == Money(40, currency='GBP')
    assert value_converted.start.gross == Money(48, currency='GBP')
    assert value_converted.stop.currency == 'GBP'
    assert value_converted.stop.net == Money(80, currency='GBP')
    assert value_converted.stop.gross == Money(96, currency='GBP')


def test_exchange_currency_for_taxed_money_range_uses_passed_conversion_rate():
    value = TaxedMoneyRange(
        TaxedMoney(Money(10, 'USD'), Money(12, 'USD')),
        TaxedMoney(Money(20, 'USD'), Money(24, 'USD')))
    custom_rate = Decimal(2)

    value_converted = exchange_currency(
        value, 'GBP', conversion_rate=custom_rate)
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


def test_exchange_currency_raises_for_nonsupported_type():
    with pytest.raises(TypeError):
        class PseudoMoneyType:
            currency = 'USD'
        converted_value = exchange_currency(PseudoMoneyType(), 'GBP')
    with pytest.raises(AttributeError):
        converted_value = exchange_currency('str', 'GBP')


def test_template_filter_money_in_currency():
    value = Money(Decimal('1.23456789'), currency='USD')
    result = prices_multicurrency.in_currency(value, currency='EUR')
    assert result == Money('2.47', 'EUR')


def test_get_rates_caches_results(conversion_rates):
    result = get_rates(qs=conversion_rates)
    assert all(currency in result.keys() for currency in ['BTC', 'GBP', 'EUR'])


def test_get_rates_force_update_cache(conversion_rates):
    expected_cache_content = {
        rate.to_currency: rate for rate in conversion_rates}
    rates = get_rates(qs=conversion_rates, force_refresh=True)
    assert rates == expected_cache_content
