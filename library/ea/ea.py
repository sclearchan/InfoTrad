from scipy.cluster.hierarchy import dendrogram, linkage, cut_tree
from scipy.optimize import minimize
import numpy as np
from pprint import pprint
import math

BUY = 0;
SELL = 1;
SIGN_IMBALANCE = 2;
ABS_IMBALANCD = 3;
CLUSTER = 4;
BADGOOD_CLUSTER = 5;

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

class EAClass:

  def run(self, data, choice="LK"):
    ''' run ea
      Args:
        data(2-D Array) : BUY and SELLS Prices.
        likelihood: "LK" or "EHO"
      
      Returns:
        1-D Array: result
      
      Example:
        >>> r = run_ea(data, "LK")
    '''

    # Imbalance with sign and abs
    for idx, val in enumerate(data):
      data[idx].append(val[BUY] - val[SELL]);
      data[idx].append(abs(val[BUY] - val[SELL]));

    # Complete linkage clustering
    Z2 = linkage([[d[ABS_IMBALANCD]] for d in data], method='complete', metric='euclidean');
    f2 = cut_tree(Z2, 2);
    for idx, v in enumerate(f2):
      data[idx].append(v[0]);

    # Calculate the means of abs_imbalance for each clusters
    f_mean = np.mean([v[ABS_IMBALANCD] for v in data if v[CLUSTER] == 0]);
    s_mean = np.mean([v[ABS_IMBALANCD] for v in data if v[CLUSTER] == 1]);

    # Assign clustering
    means = [f_mean, s_mean];
    event = means.index(max(means));
    no_event = means.index(min(means));
    event_data = [v for v in data if v[CLUSTER] == event];

    # Cluster Event cluster into good-bad event with sign_imbalance
    Z2 = linkage([[v[SIGN_IMBALANCE]] for v in event_data], method='complete', metric='euclidean');
    f2 = cut_tree(Z2, n_clusters=2);
    for idx, v in enumerate(f2):
      event_data[idx].append(v[0]);

    # Calculate the mean of Buy and Sell Orders with respect to their clusters 
    bad_buy_mean = np.mean([v[BUY] for v in event_data if v[BADGOOD_CLUSTER] == 0]);
    good_buy_mean = np.mean([v[BUY] for v in event_data if v[BADGOOD_CLUSTER] == 1]);
    no_buy_mean = np.mean([v[BUY] for v in data if v[CLUSTER] == no_event]);
    bad_sell_mean = np.mean([v[SELL] for v in event_data if v[BADGOOD_CLUSTER] == 0]);
    good_sell_mean = np.mean([v[SELL] for v in event_data if v[BADGOOD_CLUSTER] == 1]);
    no_sell_mean = np.mean([v[SELL] for v in data if v[CLUSTER] == no_event]);

    # Weight
    n_b = len([v for v in data if v[CLUSTER] == no_event]);
    n_g = len([v for v in event_data if v[BADGOOD_CLUSTER] == 1]);
    n_n = len([v for v in event_data if v[BADGOOD_CLUSTER] == 0]);
    sum_n = n_b + n_g + n_n;
    w_b = n_b / sum_n;
    w_g = n_g / sum_n;
    w_n = n_n / sum_n;

    # Calculating the parameter estimates
    alpha = w_b + w_g;
    delta = w_b / alpha;
    epsilon_b = (w_b / (w_b + w_n)) * bad_buy_mean + (w_n / (w_b + w_n)) * no_buy_mean;
    epsilon_s = (w_g / (w_g + w_n)) * good_sell_mean + (w_n / (w_g + w_n)) * no_sell_mean;

    mu_b = max([good_buy_mean-epsilon_b, 0])
    mu_s = max([bad_sell_mean-epsilon_s, 0])
    mu = (w_g / (w_g + w_b)) * mu_b + (w_b / (w_g + w_b)) * mu_s;
    paramater = np.array([alpha, delta, mu, epsilon_b, epsilon_s])

    if choice == 'LK': 
      nLL = LK(data);
    elif choice == 'EHO':
      nLL = EHO(data);

    res = minimize(nLL, paramater, method='nelder-mead')
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