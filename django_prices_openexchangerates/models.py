from __future__ import unicode_literals

from decimal import Decimal, ROUND_HALF_UP
from threading import local

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
        return '1 %s = %.04f %s' % (
            self.base_currency, self.rate, self.to_currency)
