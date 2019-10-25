
import library.bmm as bmm


market_maker = bmm.BayesianMarketMaker();
market_maker.bayesian_market_maker(P0=28.325, sigma=0.13)

# alpha, sigma, p0, pos
market_maker.set_paramaters(alpha=0.8, sigma=0.13, p0=(28.025 + 28.325)/2, pos=0);
r = market_maker.strategy({'BidPrice': 28.025, 'AskPrice': 28.325})
print(r)