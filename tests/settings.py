from __future__ import unicode_literals

SECRET_KEY = 'irrelevant'

INSTALLED_APPS = ['django_prices_openexchangerates', 'tests']

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True}]

DATABASES = {}

if 'sqlite' in DATABASES['default']['ENGINE']:
    DATABASES['default']['TEST'] = {  # noqa
        'SERIALIZE': False,
        'NAME': ':memory:',
        'MIRROR': None}