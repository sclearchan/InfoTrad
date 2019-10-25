import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import numpy as np
from .initializeProbability import initializeProbability
from .calcBidAsk import calcBidAsk
from .Probability import Probability
from .inventoryControl import inventoryControl


class BayesianMarketMaker:
    def __init__(self):
        self.TraderID = None
        self.Broker = None
        self.pos = 0
        self.profit = 0
        self.alpha = 0.90
        self.sigma = 0.13
        self.P0 = 0.000022475
        self._PAsk = 0
        self._PBid = 0
        self._P = list()
        self._V = list()

    def set_paramaters(self, alpha, sigma, p0, pos):
      self.pos = pos
      self.alpha = alpha
      self.sigma = sigma
      self.P0 = p0

    def bayesian_market_maker(self, P0=None, sigma=None):

        if (P0 is None) and (sigma is None):
            result = initializeProbability()
            self._P = result['P']
            self._V = result['V']
        else:
            self.P0 = P0
            self.sigma = sigma
            result = initializeProbability(P0=P0, sigma=sigma)
            self._P = result['P']
            self._V = result['V']

        result = calcBidAsk(self._V, self._P, self.alpha)
        self._PBid = result['PBid']
        self._PAsk = result['PAsk']


    def strategy(self, newData):
        bid = newData['BidPrice']
        ask = newData['AskPrice']

        if bid >= self._PAsk:
            # market sell order
            # placeOrder(obj, -1);
            # self.pos = self.pos - 1
            # self.profit = self.profit + (bid + ask) / 2
            self._P = Probability(self._PAsk, 1, self.alpha, self._P, self._V)
            # update bid/ask price estimates
            result = calcBidAsk(self._V, self._P, self.alpha)

            self._PBid = result['PBid']
            self._PAsk = result['PAsk']
            # Contol inventory
            result = inventoryControl(self.pos, self._PBid, self._PAsk)
            self._PBid = result['PBid']
            self._PAsk = result['PAsk']
        elif ask <= self._PBid:
            # market buy order
            # placeOrder(obj,1);
            # self.pos = self.pos + 1;
            # self.profit = self.profit - (ask + bid) / 2
            self._P = Probability(self._PBid, -1, self.alpha, self._P, self._V)
            # update bid/ask price estimates
            result = calcBidAsk(self._V, self._P, self.alpha)
            self._PBid = result['PBid']
            self._PAsk = result['PAsk']
            # Contol inventory
            result = inventoryControl(self.pos, self._PBid, self._PAsk)
            self._PBid = result['PBid']
            self._PAsk = result['PAsk']
        return {
          'ask': self._PAsk,
          'bid': self._PBid
        }


