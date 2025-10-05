DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

SECRET_KEY = "irrelevant"
DEFAULT_CURRENCY = "USD"
AVAILABLE_PURCHASE_CURRENCIES = ["USD", "EUR", "GBP"]
OPENEXCHANGE_BASE_CURRENCY = "USD"
INSTALLED_APPS = ["django_prices_openexchangerates"]
