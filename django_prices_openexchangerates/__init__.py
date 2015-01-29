from __future__ import unicode_literals

import operator
from decimal import Decimal
from prices import History, Price, PriceModifier

CENTS = Decimal('0.01')


class CurrencyConversion(PriceModifier):

    '''
    Adds a currency conversion to the price
    '''

    def __init__(self, base_currency, to_currency, rate):
        self.base_currency = base_currency
        self.to_currency = to_currency
        self.rate = rate

    def __repr__(self):
        return ('CurrencyConversion(%r, %r, rate=%r)' % (
                self.base_currency, self.to_currency, self.rate))

    def apply(self, price_obj):
        history = History(price_obj, operator.__or__, self)
        return Price(net=price_obj.net * self.rate,
                     gross=price_obj.gross * self.rate,
                     currency=self.to_currency, history=history)
