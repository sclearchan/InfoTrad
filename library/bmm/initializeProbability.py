import numpy as np
import matplotlib.pyplot as plt

def initializeProbability(P0=28.585, sigma=0.13):
    v = np.arange((P0-6*sigma), (P0+6*sigma), 0.01)
    V = v.reshape((len(v),1))
    nd = (1/(sigma*np.sqrt(2*np.pi)))*np.exp(-np.power((V-P0),2)/(2*np.power(sigma,2)))
    nd = nd/sum(nd)
    P = nd
    return {'V': V,'P': P}

