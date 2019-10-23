import library.ea as ea
import library.yz as yz
import library.gan as gan
import redis
from pprint import pprint
import time
import datetime
from config import BITMEX_CONFIG, MYSQL_INFO, REDIS_INFO
import threading
from multiprocessing import Process

import pymysql
import copy

REDIS_CLIENT = redis.Redis(
  host = REDIS_INFO['host'],
  port = REDIS_INFO['port'],
  db = REDIS_INFO['db']
);

class InfoTrader:

  def __init__(self):
    self.sleep_timer = 1; # sec
    self.buy_data = [];
    self.sell_data = [];
    REDIS_CLIENT.set('BITMEX:BUY', 0)
    REDIS_CLIENT.set('BITMEX:SELL', 0)
    # Connection 으로부터 Cursor 생성
    self.conn = pymysql.connect(
      host = MYSQL_INFO['host'],
      user = MYSQL_INFO['user'],
      password = MYSQL_INFO['password'],
      db = MYSQL_INFO['db'],
      autocommit = True,
      charset = 'utf8'
    );
    self.curs = self.conn.cursor()
    self.run();

  def run(self):
    while True:
      buy_count = int(REDIS_CLIENT.get('BITMEX:BUY'))
      sell_count = int(REDIS_CLIENT.get('BITMEX:SELL'))

      if len(self.buy_data) < 12:
        self.buy_data.append(buy_count);
        self.sell_data.append(sell_count);
      else:
        # shift buy/sell count data
        buy_data = copy.deepcopy(self.buy_data)
        sell_data = copy.deepcopy(self.sell_data)
        process = [];

        process.append(Process(target=self.calculate, args=(buy_data, sell_data, 'EA', 'LK')))
        process.append(Process(target=self.calculate, args=(buy_data, sell_data, 'EA', 'EHO')))

        for p in process:
          p.start();

        # t = Process(target=self.calculate, args=(buy_data, sell_data, 'EA', 'LK'))
        # t.start()
        # t = Process(target=self.calculate, args=(buy_data, sell_data,'EA', 'EHO'))
        # t.start()
        # t = Process(target=self.calculate, args=(buy_data, sell_data,'YZ', 'LK'))
        # t.start()
        # t = Process(target=self.calculate, args=(buy_data, sell_data,'YZ', 'EHO'))
        # t.start()
        # t = Process(target=self.calculate, args=(buy_data, sell_data,'GAN', 'LK'))
        # t.start()
        # t = Process(target=self.calculate, args=(buy_data, sell_data,'GAN', 'EHO'))
        # t.start()

        self.buy_data.pop(0);
        self.sell_data.pop(0);
        self.buy_data.append(buy_count);
        self.sell_data.append(sell_count);

        # reset buy/sell count
        REDIS_CLIENT.set('BITMEX:BUY', 0)
        REDIS_CLIENT.set('BITMEX:SELL', 0)

      time.sleep(self.sleep_timer);

  def calculate(self, buy, sell, main, sub):
    data = []

    for idx, val in enumerate(buy):
      data.append([val, sell[idx]])
    to_save_data = copy.deepcopy(data);

    if main == 'EA':
      instance = ea.EAClass();
    elif main == 'GAN':
      instance = gan.GANClass();
    else:
      instance = yz.YZClass();

    result = instance.run(data, sub);

    try:
      self.curs.execute("INSERT INTO paramaters (alpha, delta, mu, epsilon_b, epsilon_s, likval, pin, trade_type, cal_data) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);", \
        (str(result['alpha']), str(result['delta']), str(result['mu']), str(result['epsilon_b']), str(result['epsilon_s']), str(result['likval']), str(result['pin']), f'{main}:{sub}', str(to_save_data) ))
    except:
      print('*'*20,' error start')
      print(result)
      print('*'*20,' error end')

a = InfoTrader();
