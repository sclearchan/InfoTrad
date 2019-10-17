
from scipy.cluster.hierarchy import dendrogram, linkage, cut_tree
from scipy.optimize import minimize
import numpy as np
from pprint import pprint
import math

BUY = 0;
SELL = 1;

def EHO(data):
  params = data;

  def run(x):
    bPrice = [v[BUY] for v in params];
    sPrice = [v[SELL] for v in params];
    trade_days = len(params)
    alpha = x[0]
    delta = x[1]
    mu = x[2]
    epsb = x[3]
    epss = x[4]
    LK_I = 0;
    LK_OUT = 0;

    for idx in range(0, trade_days):
      buy_s = bPrice[idx];
      sell_s = sPrice[idx];
      M = min([buy_s, sell_s]) + max([buy_s, sell_s]) / 2;
      Xs = epss/(mu + epss);
      Xb = epsb/(mu + epsb);
      try:
        part1 = -(epsb + epss) + M * math.log(Xb + Xs) + buy_s * math.log(mu + epsb) + sell_s * math.log(mu + epss);
        part2 = math.log(alpha * (1 - delta) * math.exp(-mu) * math.pow(Xs, sell_s-M) * math.pow(Xb, -M) + alpha * delta * math.exp(-mu) * math.pow(Xb, buy_s-M) * math.pow(Xs, -M) + (1 - alpha) * math.pow(Xs, sell_s - M) * math.pow(Xb, buy_s - M));
        LK_I = LK_I + (part1 + part2);
      except:
        break;

    if((epsb >= 0) and (epss >= 0) and (mu >= 0) and (alpha >= 0) and (delta >= 0) and (alpha <= 1) and (delta <= 1)):
      LK_OUT = -LK_I
    else:
      LK_OUT = 1;

    return LK_OUT;

  return run;

def LK(data):
  '''
    data[0] : alpha
    data[1] : delta
    data[2] : mu
    data[3] : epsb
    data[4] : epss
  '''
  params = data;

  def run(x):
    # print('{:f}, {:f}, {:f}, {:f}, {:f}'.format(float(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4])))
    bPrice = [v[BUY] for v in params];
    sPrice = [v[SELL] for v in params];
    trade_days = len(params)
    alpha = x[0]
    delta = x[1]
    mu = x[2]
    epsb = x[3]
    epss = x[4]
    LK_I = 0;
    LK_OUT = 0;
    for idx in range(0, trade_days):
      buy_s = bPrice[idx];
      sell_s = sPrice[idx];
      e1 = -mu - sell_s * math.log(1 + (mu/epss));
      e2 = -mu - buy_s * math.log(1 + (mu/epsb));
      e3 = -buy_s * math.log(1 + (mu/epsb)) - sell_s * math.log(1 + (mu/epss));
      emax = max([e1, e2, e3])
      part1 = -epsb - epss + buy_s * math.log(mu + epsb) + sell_s * math.log(mu + epss) + emax;
      part2 = math.log(alpha * delta * math.exp(e1 - emax) + alpha * (1 - delta) * math.exp(e2 - emax) + (1 - alpha) * math.exp(e3 - emax));
      LK_I = LK_I + (part1 + part2);

    if((epsb >= 0) and (epss >= 0) and (mu >= 0) and (alpha >= 0) and (delta >= 0) and (alpha <= 1) and (delta <= 1)):
      LK_OUT = -LK_I
    else:
      LK_OUT = 1;

    return LK_OUT;

  return run;


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

