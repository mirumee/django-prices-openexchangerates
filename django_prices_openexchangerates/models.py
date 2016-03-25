from __future__ import unicode_literals

from decimal import Decimal
from threading import local

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from .currencies import CURRENCIES

BASE_CURRENCY = getattr(settings, 'OPENEXCHANGERATES_BASE_CURRENCY', 'USD')

_thread_locals = local()


class CachingManager(models.Manager):

    def get_rate(self, to_currency):  # noqa
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

    base_currency = BASE_CURRENCY

    to_currency = models.CharField(
        _('To'), max_length=3, db_index=True,
        choices=CURRENCIES.items(), unique=True)

    rate = models.DecimalField(
        _('Conversion rate'), max_digits=13, decimal_places=6)

    modified_at = models.DateTimeField(auto_now=True)

    objects = CachingManager()

    class Meta:
        ordering = ['to_currency']

    def save(self, *args, **kwargs):  # noqa
        """ Save the model instance but only on successful validation. """
        self.full_clean()
        super(ConversionRate, self).save(*args, **kwargs)

    def clean(self):  # noqa
        if self.rate <= Decimal(0):
            raise ValidationError('Conversion rate has to be positive')
        if self.base_currency == self.to_currency:
            raise ValidationError(
                'Can\'t set a conversion rate for the same currency')
        super(ConversionRate, self).clean()

    def __str__(self):  # noqa
        return '1 %s = %.04f %s' % (self.base_currency, self.rate,
                                    self.to_currency)

    def __repr__(self):  # noqa
        return (
            'ConversionRate(pk=%r, base_currency=%r, to_currency=%r, rate=%r)' % (
                self.pk, self.base_currency, self.to_currency, self.rate))
