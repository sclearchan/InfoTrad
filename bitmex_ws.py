
import redis
from config import BITMEX_CONFIG, REDIS_INFO
from library.websocket import WebSocket
import json
import time

REDIS_CLIENT = redis.Redis(
  host = REDIS_INFO['host'],
  port = REDIS_INFO['port'],
  db = REDIS_INFO['db']
);

class BitmexWS:
  def __init__(self):
    self.wsc = WebSocket(market='BITMEX', url=BITMEX_CONFIG['WS_URL'])
    self.wsc.connect(self.on_open, self.on_message) 
    # Init buy, sell tick count
    REDIS_CLIENT.set('BITMEX:BUY', 0)
    REDIS_CLIENT.set('BITMEX:SELL', 0)
    REDIS_CLIENT.set('BITMEX:ASK', 0)
    REDIS_CLIENT.set('BITMEX:BID', 0)

  @staticmethod
  def on_message(ws, msg):
    p = json.loads(msg);

    buy_count = 0
    buy_price = REDIS_CLIENT.get('BITMEX:ASK')
    sell_count = 0
    sell_price = REDIS_CLIENT.get('BITMEX:BID')
    if 'table' in p:
      for order in p['data']:
        if order['side'] == 'Buy':
          buy_count += 1;
          buy_price = order['price'] 
        else:
          sell_count += 1;
          sell_price = order['price']

    REDIS_CLIENT.set('BITMEX:ASK', buy_price)
    REDIS_CLIENT.set('BITMEX:BID', sell_price)
    REDIS_CLIENT.set('BITMEX:BUY', int(REDIS_CLIENT.get('BITMEX:BUY')) + buy_count)
    REDIS_CLIENT.set('BITMEX:SELL', int(REDIS_CLIENT.get('BITMEX:SELL')) + sell_count)
    print('{}, {}'.format(REDIS_CLIENT.get('BITMEX:BUY'), REDIS_CLIENT.get('BITMEX:SELL')))

  @staticmethod
  def on_open(ws):
    sub = {"op": "subscribe", "args": ['trade:XBTUSD']}
    print('Subscribe, {}'.format(sub))
    ws.send(json.dumps(sub))

bitmex_ws = BitmexWS();