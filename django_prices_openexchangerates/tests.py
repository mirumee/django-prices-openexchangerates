from decimal import Decimal
import mock
from django.conf import settings
from django.db import models
from django.test import TestCase
from prices import Price
from .models import MultiCurrencyPriceField


class Product(models.Model):

    price = MultiCurrencyPriceField(verbose_name='Price', currency='USD',
                                    default='5')


class MultiCurrencyPriceFieldTest(TestCase):

    @mock.patch('django_prices_openexchangerates.models.ConversionRate.objects')
    def test_init(self, mock_item):
        get_rate_mock = mock.Mock()
        eur_val = Decimal(1)
        gbp_val = Decimal(2)
        get_rate_mock.from_base_currency.side_effect = [eur_val, gbp_val]
        mock_item.get_rate.return_value = get_rate_mock
        product = Product()
        self.assertEqual(product.price, Price(net=5, currency='USD'))

    @mock.patch('django_prices_openexchangerates.models.ConversionRate.objects')
    def test_to_python(self, mock_item):
        get_rate_mock = mock.Mock()
        eur_val = Decimal(1)
        gbp_val = Decimal(2)
        get_rate_mock.from_base_currency.side_effect = [eur_val, gbp_val]
        mock_item.get_rate.return_value = get_rate_mock
        field = MultiCurrencyPriceField(currency='USD')
        base_price = Price(7, currency='USD')
        result = field.to_python(7)
        self.assertEqual(set(result.currencies.keys()),
                         set(settings.AVAILABLE_PURCHASE_CURRENCIES))
        self.assertEqual(result.price, base_price)
        self.assertEqual(result.currencies['GBP'],
                         Price(currency='GBP', net=gbp_val))
        self.assertEqual(result.currencies['EUR'],
                         Price(currency='EUR', net=eur_val))
