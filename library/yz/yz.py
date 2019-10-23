
from scipy.cluster.hierarchy import dendrogram, linkage, cut_tree
from scipy.optimize import minimize
import numpy as np
from pprint import pprint
import math

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from likelihood import *

BUY = 0;
SELL = 1;

class YZClass:

  def run(self, data, choice="LK"):
    mean_b = np.mean([v[BUY] for v in data])
    mean_s = np.mean([v[SELL] for v in data])
    maxim = max([mean_b, mean_s])

    alpha_in = [0.1, 0.3, 0.5, 0.7, 0.9]
    delta_in = [0.1, 0.3, 0.5, 0.7, 0.9]
    gamma_in = [0.1, 0.3, 0.5, 0.7, 0.9]
    output = np.zeros(shape=(125, 6))

    dum = 0
    for i in range(0, 5):
      for j in range(0, 5):
        for k in range(0, 5):
          alpha = alpha_in[i]
          delta = delta_in[j]
          eb = gamma_in[k] * mean_b
          mu = (mean_b - eb) / (alpha * (1 - delta))
          es = mean_s - (alpha * delta * mu)
          if es <= 0 or mu > maxim:
            dum = dum + 1
            continue

          par0 = np.array([alpha, delta, mu, eb, es])
          if choice == 'LK':
            nLL = LK(data)
          elif choice == 'EHO':
            nLL = EHO(data)

          try:
            res = minimize(nLL, par0, method='nelder-mead')
          except:
            continue;

          if res:
            print(f'Optimize Result: {res.message}')
            return {
              'alpha': res.x[0],
              'delta': res.x[1],
              'mu': res.x[2],
              'epsilon_b': res.x[3],
              'epsilon_s': res.x[4],
              'likval': res.fun * -1,
              'pin': (res.x[0] * res.x[2]) / ((res.x[0] * res.x[2]) + res.x[2] + res.x[3])
            }

