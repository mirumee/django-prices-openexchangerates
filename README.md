# django-prices-openexchangerates
openexchangerates.org support for django-prices

How to use it?
==============
- Install package with `./setup.py install`
- Add `django_prices_openexchangerates` to `INSTALLED_APPS`
- Register on https://openexchangerates.org/ and get API key
- Set following settings in your project's settings.py:
    - `OPENEXCHANGERATES_API_KEY`
    - `OPENEXCHANGE_BASE_CURRENCY` (Only if you have premium account and you don't want to use USD as base currency)
- Create `ConversionRate` objects manually (for each currency, that you want to support)
- Fetch current rates from API with `./manage.py update_exchange_rates`
- Schedule this task in cron job or in celery, to be always up to date with exchange rates
