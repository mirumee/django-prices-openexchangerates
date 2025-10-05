from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_prices_openexchangerates.currencies import CURRENCIES

BASE_CURRENCY = getattr(settings, "OPENEXCHANGERATES_BASE_CURRENCY", "USD")
CACHE_KEY = getattr(
    settings, "OPENEXCHANGERATES_CACHE_KEY", "openexchangerates_conversion_rates"
)
CACHE_TIME = getattr(settings, "OPENEXCHANGERATES_CACHE_TTL", 60 * 60)


def get_rates(qs, force_refresh=False):
    conversion_rates = cache.get(CACHE_KEY)
    if not conversion_rates or force_refresh:
        conversion_rates = {rate.to_currency: rate for rate in qs}
        cache.set(CACHE_KEY, conversion_rates, CACHE_TIME)
    return conversion_rates


class CachingManager(models.Manager):
    def get_rate(self, to_currency):  # noqa
        all_rates = get_rates(self.all())
        try:
            return all_rates[to_currency]
        except KeyError:
            msg = f"ConversionRate for {to_currency} does not exist"
            raise ConversionRate.DoesNotExist(msg)


class ConversionRate(models.Model):
    base_currency = BASE_CURRENCY

    to_currency = models.CharField(
        _("To"), max_length=3, db_index=True, choices=CURRENCIES, unique=True
    )

    rate = models.DecimalField(_("Conversion rate"), max_digits=20, decimal_places=12)

    modified_at = models.DateTimeField(auto_now=True)

    objects = CachingManager()

    class Meta:
        ordering = ["to_currency"]

    def save(self, *args, **kwargs):  # noqa
        """Save the model instance but only on successful validation."""
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):  # noqa
        if self.rate <= Decimal(0):
            raise ValidationError("Conversion rate has to be positive")
        if self.base_currency == self.to_currency:
            raise ValidationError("Can't set a conversion rate for the same currency")
        super().clean()

    def __str__(self):  # noqa
        return f"1 {self.base_currency} = {self.rate:.04f} {self.to_currency}"

    def __repr__(self):  # noqa
        return (
            f"ConversionRate(pk={self.pk!r}, "
            f"base_currency={self.base_currency!r}, "
            f"to_currency={self.to_currency!r}, "
            f"rate={self.rate!r})"
        )
