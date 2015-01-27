from decimal import Decimal
import mock
from django.conf import settings
from django.db import models
from django.test import TestCase
from prices import Price
from .models import MultiCurrencyPriceField, MultiCurrencyPrice

RATES = {
    'USD': Decimal(1),
    'EUR': Decimal(2),
    'GBP': Decimal(4)}


def convert_price_mock(price, to_currency='USD'):
    if price.currency == to_currency:
        return price
    converted_price = price.net
    if to_currency != settings.DEFAULT_CURRENCY:
        converted_price = price.net * RATES[to_currency]
    if price.currency != settings.DEFAULT_CURRENCY:
        converted_price = price.net / RATES[price.currency]

    return Price(currency=to_currency, net=converted_price,
                 history=price.history)


class Product(models.Model):

    price = MultiCurrencyPriceField(verbose_name='Price', currency='USD',
                                    default='5')


@mock.patch('django_prices_openexchangerates.utils.convert_price',
            side_effect=convert_price_mock)
class MultiCurrencyPriceFieldTest(TestCase):

    def test_init(self, mock_converter):
        product = Product()
        self.assertEqual(product.price, Price(net=5, currency='USD'))

    def test_to_python(self, mock_converter):
        field = MultiCurrencyPriceField(currency='USD')
        base_price = Price(7, currency='USD')
        result = field.to_python(7)
        self.assertTrue(isinstance(result, MultiCurrencyPrice))
        self.assertEqual(result.price, base_price)

    def test_currency_conversion(self, mock_item):
        field = MultiCurrencyPriceField(currency='USD')
        net_val = Decimal(10)
        result = field.to_python(net_val)
        base_price = Price(net_val, currency='USD')
        gbp_val = RATES['GBP'] * net_val
        eur_val = RATES['EUR'] * net_val
        self.assertEqual(set(result.currencies.keys()),
                         set(settings.AVAILABLE_PURCHASE_CURRENCIES))
        self.assertEqual(result.price, base_price)
        self.assertEqual(result.currencies['GBP'],
                         Price(currency='GBP', net=gbp_val))
        self.assertEqual(result.currencies['EUR'],
                         Price(currency='EUR', net=eur_val))


@mock.patch('django_prices_openexchangerates.utils.convert_price',
            side_effect=convert_price_mock)
class MultiCurrencyPriceTest(TestCase):

    @mock.patch('django_prices_openexchangerates.utils.convert_price',
                side_effect=convert_price_mock)
    def setUp(self, mock_item):
        self.price1 = MultiCurrencyPrice(Price(10, currency='USD'))
        self.price2 = MultiCurrencyPrice(Price(25, currency='USD'))

    def test_add(self, mock_item):
        expected_usd = 10 + 25
        expected_eur = expected_usd * RATES['EUR']
        expected_gbp = expected_usd * RATES['GBP']
        prices_sum = self.price1 + self.price2
        self.assertEqual(prices_sum.in_base_currency.gross, expected_usd)
        self.assertEqual(prices_sum.currencies['EUR'].gross, expected_eur)
        self.assertEqual(prices_sum.currencies['GBP'].gross, expected_gbp)

    def test_sub(self, mock_item):
        expected_usd = 25 - 10
        expected_eur = expected_usd * RATES['EUR']
        expected_gbp = expected_usd * RATES['GBP']
        prices_sum = self.price2 - self.price1
        self.assertEqual(prices_sum.in_base_currency.gross, expected_usd)
        self.assertEqual(prices_sum.currencies['EUR'].gross, expected_eur)
        self.assertEqual(prices_sum.currencies['GBP'].gross, expected_gbp)

    def test_mul(self, mock_item):
        expected_usd = 25 * 5
        expected_eur = expected_usd * RATES['EUR']
        expected_gbp = expected_usd * RATES['GBP']
        prices_sum = self.price2 * 5
        self.assertEqual(prices_sum.in_base_currency.gross, expected_usd)
        self.assertEqual(prices_sum.currencies['EUR'].gross, expected_eur)
        self.assertEqual(prices_sum.currencies['GBP'].gross, expected_gbp)

    def test_rmul(self, mock_item):
        expected_usd = Decimal('0.1') * 25
        expected_eur = expected_usd * RATES['EUR']
        expected_gbp = expected_usd * RATES['GBP']
        prices_sum = Decimal('0.1') * self.price2
        self.assertEqual(prices_sum.in_base_currency.gross, expected_usd)
        self.assertEqual(prices_sum.currencies['EUR'].gross, expected_eur)
        self.assertEqual(prices_sum.currencies['GBP'].gross, expected_gbp)
