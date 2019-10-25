import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import numpy as np
from .initializeProbability import initializeProbability

Value = initializeProbability()
V = Value['V']
P = Value['P']

alpha = 0.90


# Bid Calculation
def bidCalc(count, V, P, Pinfo):
    N = len(V)
    a = 0
    b = 0

    for j in range(1, count + 1):
        a = a + (V[j-1] * P[j-1])

    for k in range(count + 1, N + 1):
        b = b + (V[k-1] * P[k-1])

    PBid = 2 * (Pinfo * a + (1 - Pinfo)*b)
    bidError = np.abs(V[count-1] - PBid)

    return (PBid, bidError)

#Ask Calculation
def askCalc(count, V, P, Pinfo):
    N = len(V)
    a = 0
    b = 0

    for j in range(1, count):
        a = a + (V[j-1] * P[j-1])

    for k in range(count, N + 1):
        b = b + (V[k-1] * P[k-1]);

    PAsk = 2 * ((1-Pinfo) * a + Pinfo*b)
    askError = np.abs(V[count-1] - PAsk)

    return (PAsk, askError)


def calcBidAsk(V, P, alpha):
#Bid/Ask calculation for Bayesian Market Maker
    N = len(V)
    #Expected value, rodunded to nearest cent
    E = np.round(sum(np.multiply(V, P)) * 100) / 100

    Pinfo = 0.5 + 0.5 * alpha
    #Find where E is in V
    bidError = np.zeros((N,1))
    PBid = np.zeros((N,1))

    for i in range(1, N+1):
        # from Vmin to V=E
        PBid[i-1], bidError[i-1] = bidCalc(i, V, P, Pinfo)

    minbiderr = np.min(bidError)
    biderrind = np.where(minbiderr == bidError)
    PBid = np.minimum(V[biderrind],E)

    askError = np.zeros((N,1))
    PAsk = np.zeros((N,1))

    # loop over all values of V from E to Vmax
    for i in range (1, N+1):
        # from V=E to Vmax
        PAsk[i-1], askError[i-1] = askCalc(i, V, P, Pinfo)

    minaskerr = np.min(askError)
    askerrind = np.where(minaskerr == askError)   
    PAsk = np.maximum(V[askerrind],E)

    return {'PBid': PBid[0], 'PAsk': PAsk[0]}
