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
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Software Development :: Libraries :: Python Modules']

setup(name='django-prices-openexchangerates',
      author='Mirumee Software',
      author_email='hello@mirumee.com',
      description='openexchangerates.org support for django-prices',
      license='BSD',
      version='0.1',
      url='https://github.com/mirumee/django-prices-openexchanerates',
      packages=['django_prices_openexchangerates'],
      include_package_data=True,
      classifiers=CLASSIFIERS,
      install_requires=['django', 'django-prices>=0.3.4'],
      platforms=['any'],
      zip_safe=False)

