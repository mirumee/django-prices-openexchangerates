import operator
from decimal import Decimal, ROUND_HALF_UP
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
        return 'CurrencyConversion(base_currency=%s, to_currency=%s, ' \
               'rate=%0.04f)' % (self.base_currency, self.to_currency,
                                 self.rate)

    def apply(self, price_obj):
        history = History(price_obj, operator.__mul__, self)
        net = (price_obj.net * self.rate).quantize(CENTS,
                                                   rounding=ROUND_HALF_UP)
        gross = (price_obj.gross * self.rate).quantize(CENTS,
                                                       rounding=ROUND_HALF_UP)
        return Price(net=net, gross=gross,
                     currency=self.to_currency, history=history)
