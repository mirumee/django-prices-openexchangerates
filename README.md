# django-prices-openexchangerates
openexchangerates.org support for django-prices

```python
from prices import Price
from django_prices_openexchangerates import exchange_currency

converted_price = exchange_currency(Price(10, currency='USD'), 'EUR')
print(converted_price)
# Price('8.84040', currency='EUR')
print(converted_price.history)
# (Price('10', currency='USD') | CurrencyConversion('USD', 'EUR', rate=Decimal('0.88404')))
```

It will also create additional steps if it cannot convert directly: 

```python
from prices import Price
from django_prices_openexchangerates import exchange_currency

converted_price = exchange_currency(Price(10, currency='GBP'), 'EUR')
print(converted_price)
# Price('13.31313588062401085236264978', currency='EUR')
print(converted_price.history)
# ((Price('10', currency='GBP') | CurrencyConversion('GBP', 'USD', rate=Decimal('1.507272590247946341095787173'))) | CurrencyConversion('USD', 'EUR', rate=Decimal('0.88326')))
```

Templatetags can be used to convert currency and round amounts:

```django
{% load prices_multicurrency %}

<p>Price: {% gross_in_currency foo.price 'USD' %} ({% net_in_currency foo.price 'USD' %} + {% tax_in_currency foo.price 'USD' %} tax)</p>
```

When you install babel-django library, you can use i18n templatetags and display proper currency symbols

```django
{% load prices_multicurrency_i18n %}

<p>Price: {% gross_in_currency foo.price 'USD' %} ({% net_in_currency foo.price 'USD' %} + {% tax_in_currency foo.price 'USD' %} tax)</p>
```

Installation
==============
```
pip install django-prices-openexchangerates
```
Add `django_prices_openexchangerates` to `INSTALLED_APPS`

Set following settings in your project's settings.py:

 * `OPENEXCHANGERATES_API_KEY`

 * `OPENEXCHANGERATES_BASE_CURRENCY` (Only if you have premium account and you don't want to use USD as base currency)

Create `ConversionRate` objects manually (for each currency, that you want to support)

Updating exchange rates
=======================
Fetch current rates from API with `./manage.py update_exchange_rates`

Schedule this task in cron job or in celery, to be always up to date with exchange rates
