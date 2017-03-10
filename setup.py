#! /usr/bin/env python
import os
from setuptools import setup

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')

CLASSIFIERS = [
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Software Development :: Libraries :: Python Modules']

setup(
    name='django-prices-openexchangerates',
    author='Mirumee Software',
    author_email='hello@mirumee.com',
    description='openexchangerates.org support for django-prices',
    license='BSD',
    version='0.1.13',
    url='https://github.com/mirumee/django-prices-openexchanerates',
    packages=[
        'django_prices_openexchangerates',
        'django_prices_openexchangerates.management',
        'django_prices_openexchangerates.management.commands',
        'django_prices_openexchangerates.migrations',
        'django_prices_openexchangerates.templatetags'],
    include_package_data=True,
    classifiers=CLASSIFIERS,
    install_requires=['Django>=1.4', 'django-prices>=0.3.4', 'prices>=0.5.2'],
    platforms=['any'],
    tests_require=['mock==1.0.1'],
    test_suite='django_prices_openexchangerates.tests',
    zip_safe=False)

