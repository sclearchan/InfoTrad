import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import numpy as np

from .calcBidAsk import calcBidAsk
from .initializeProbability import initializeProbability

Value = initializeProbability()
V = Value['V']
P = Value['P']

alpha = 0.90

Value2 = calcBidAsk(V, P, alpha)
PAsk = Value2['PAsk']
PBid = Value2['PBid']
pos = -10
# from scipy.interpolate import interp1d

def inventoryControl(pos, PBid, PAsk):
    #Inventory calculation for Bayesian Market Maker
    
    #sigmoidal function
    sig = (10 * (1+np.tanh((np.linspace(-3,3,13)))))
    xc = np.arange((len(sig)))
    offset = np.round(np.sign(pos)*np.interp(pos,xc,sig))/100

    if pos > 0:
        PAsk = PAsk - offset
        PBid = PBid - offset

    return {'PBid': PBid,'PAsk': PAsk}


