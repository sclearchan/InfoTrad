from scipy.cluster.hierarchy import dendrogram, linkage, cut_tree
from scipy.optimize import minimize, fmin
import numpy as np
from pprint import pprint
import math

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from likelihood import *

BUY = 0;
SELL = 1;
SIGN_IMBALANCE = 2;
ABS_IMBALANCD = 3;
CLUSTER = 4;
BADGOOD_CLUSTER = 5;

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
    
    # result = []
    # alpha_plt = [];
    # delta_plt = [];
    # def callback(x):
    #     fobj = nLL(x)
    #     alpha_plt.append(x[0])
    #     delta_plt.append(x[1])
    #     result.append(-fobj)
    # res = minimize(nLL, paramater,  method='Nelder-Mead', tol=1e-06, callback=callback, options={'disp':True})
    # import matplotlib.pylab as plt
    # plt.figure(1)
    # plt.plot(result, 'r-')
    # plt.figure(2)
    # plt.plot(alpha_plt, 'r-')
    # plt.plot(delta_plt, 'b-')
    # plt.show()

    res = minimize(nLL, paramater,  method='Nelder-Mead')
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