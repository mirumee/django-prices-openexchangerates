from decimal import Decimal, ROUND_HALF_UP
from threading import local
from django_prices.models import PriceField
from django.core.exceptions import ValidationError

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from .currencies import CURRENCIES

CENTS = Decimal('0.01')

_thread_locals = local()


class CachingManager(models.Manager):

    def get_rate(self, to_currency):
        if not hasattr(_thread_locals, 'conversion_rates'):
            _thread_locals.conversion_rates = {}
        if to_currency not in _thread_locals.conversion_rates:
            rates = self.all()
            for rate in rates:
                _thread_locals.conversion_rates[rate.to_currency] = rate
        try:
            rate = _thread_locals.conversion_rates[to_currency]
        except KeyError:
            rate = self.get(to_currency=to_currency)
            _thread_locals.conversion_rates[to_currency] = rate
        return rate


@python_2_unicode_compatible
class ConversionRate(models.Model):

    base_currency = settings.DEFAULT_CURRENCY

    to_currency = models.CharField(
        _('To'), max_length=3, db_index=True,
        choices=CURRENCIES.items(), unique=True)

    rate = models.DecimalField(
        _('Conversion rate'), max_digits=12, decimal_places=5)

    modified_at = models.DateTimeField(auto_now=True)

    objects = CachingManager()

    class Meta:
        ordering = ['to_currency']

    def to_base_currency(self, value):
        price = value / self.rate
        return price.quantize(CENTS, rounding=ROUND_HALF_UP)

    def from_base_currency(self, value):
        price = value * self.rate
        return price.quantize(CENTS, rounding=ROUND_HALF_UP)

    def save(self, *args, **kwargs):
        """ Save the model instance but only on succesful validation. """
        self.full_clean()
        super(ConversionRate, self).save(*args, **kwargs)

    def clean(self):
        if self.rate <= Decimal(0):
            raise ValidationError('Conversion rate has to be positive')
        if self.base_currency == self.to_currency:
            raise ValidationError(
                'Can\'t set a conversion rate for the same currency')
        super(ConversionRate, self).clean()

    def __str__(self):
        return '1 {} = {:.4f} {}'.format(
            self.base_currency, self.rate, self.to_currency)


class MultiCurrencyPrice(object):

    currencies = {}

    def __init__(self, price, currency=None):
        self.price = price
        self.currency = currency or settings.DEFAULT_CURRENCY
        self.recalculate_currencies()

    def __repr__(self):
        base_price = self.price
        if base_price.net == base_price.gross:
            return 'MultiCurrencyPrice(%r, base_currency=%r, ' \
                   'available_currencies=%r)' % (
                       str(base_price.net), base_price.currency,
                       str(self.currencies.keys()))
        return ('MultiCurrencyPrice(net=%r, gross=%r, base_currency=%r, '
                'available_currencies=%r)' % (
                    str(base_price.net), str(base_price.gross),
                    base_price.currency,
                    str(self.currencies.keys())))

    def __lt__(self, other):
        return self.price < other

    def __le__(self, other):
        return self.price < other or self.price == other

    def __eq__(self, other):
        return self.price == other

    def __ne__(self, other):
        return not self.price == other

    def __mul__(self, other):
        return MultiCurrencyPrice(self.price.__mul__(other))

    def __rmul__(self, other):
        return MultiCurrencyPrice(self.price.__rmul__(other))

    def __add__(self, other):
        return MultiCurrencyPrice(self.price.__add__(other.price))

    def __sub__(self, other):
        return MultiCurrencyPrice(self.price.__sub__(other.price))

    def for_current_currency(self):
        if self.price.currency == self.currency:
            return self.price
        return self.currencies.get(self.currency) or self.price

    def recalculate_currencies(self):
        from .utils import convert_price
        for currency in settings.AVAILABLE_PURCHASE_CURRENCIES:
            if currency in CURRENCIES:
                self.currencies[currency] = convert_price(self.price, currency)

    @property
    def in_base_currency(self):
        return self.price


class MultiCurrencyPriceField(PriceField):

    def to_python(self, value):
        if isinstance(value, MultiCurrencyPrice) or value is None:
            return value
        price = super(MultiCurrencyPriceField, self).to_python(value)
        return MultiCurrencyPrice(price)

    def value_to_string(self, obj):
        return super(MultiCurrencyPriceField, self).value_to_string(obj.price)

    def for_current_currency(self):
        if self.price.currency == self.currency:
            return self.price
        return self.currencies.get(self.currency) or self.price
