# openexchangerates.org support for `django-prices`

```python
from prices import Amount
from django_prices_openexchangerates import exchange_currency

converted_price = exchange_currency(Amount(10, currency='USD'), 'EUR')
print(converted_price)
# Amount('8.84040', currency='EUR')
```

It will also create additional steps if it cannot convert directly: 

```python
from prices import Amount
from django_prices_openexchangerates import exchange_currency

converted_price = exchange_currency(Amount(10, currency='GBP'), 'EUR')
print(converted_price)
# Amount('13.31313588062401085236264978', currency='EUR')
```

Template filters can be used to convert currency and round amounts:

```html+django
{% load prices_multicurrency %}

<p>Price: {{ foo.price.gross|in_currency:'USD'|amount }} ({{ foo.price.net|in_currency:'USD'|amount }} + {{ foo.price|in_currency:'USD'|amount }} tax)</p>
```

When you install babel-django library, you can use i18n templatetags and display proper currency symbols

```html+django
{% load prices_multicurrency_i18n %}

<p>Price: {{ foo.price.gross|in_currency:'USD'|amount }} ({{ foo.price.net|in_currency:'USD'|amount }} + {{ foo.price|in_currency:'USD'|amount }} tax)</p>
```

Installation
==============
First install the package:
```
pip install django-prices-openexchangerates
```
Then add `'django_prices_openexchangerates'` to your `INSTALLED_APPS`.

Set following settings in your project's settings:

 * `OPENEXCHANGERATES_API_KEY`

 * `OPENEXCHANGERATES_BASE_CURRENCY` (defaults to `'USD'`, only premium accounts support other bases)

Use your admin console to create `ConversionRate` objects for each currency that you want to support.

Updating exchange rates
=======================
Fetch current rates from API with `./manage.py update_exchange_rates`

Schedule this task in cron job or in celery, to be always up to date with exchange rates

You can use `--all` flag in above command, to create exchange rates automatically for all available currencies.
