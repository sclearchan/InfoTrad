from .initializeProbability import initializeProbability

Value = initializeProbability()
V = Value['V']
P = Value['P']

def Probability(price, trade, alpha, P, V):
    #Probablity calculation for Bayesian Market Maker

    Pold = P
    Pinfo = 0.5 + 0.5 * alpha

    if trade < 0:
        # sell order received
        for i in range(0,len(V)):
            if V[i] < price:
                P[i] = Pold[i] * Pinfo
            else:
                P[i] = Pold[i] * (1-Pinfo)
    else:
        # buy order received
        for i in range(0,len(V)):
            if V[i] > price:
                P[i] = Pold[i] * Pinfo
            else:
                P[i] = Pold[i] * (1-Pinfo)

    P = P/sum(P)

    return P
