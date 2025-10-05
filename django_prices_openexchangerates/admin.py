from django.contrib import admin

from django_prices_openexchangerates.models import ConversionRate


class ConversionRateAdmin(admin.ModelAdmin):
    list_display = ("rate", "to_currency")


admin.site.register(ConversionRate, ConversionRateAdmin)
