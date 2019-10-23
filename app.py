import library.ea as ea
import library.yz as yz
import library.gan as gan
import redis
from pprint import pprint
import time
import datetime
from config import BITMEX_CONFIG, MYSQL_INFO, REDIS_INFO
import threading
import pymysql

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
        data = []

        for idx, val in enumerate(self.buy_data):
          data.append([val,self.sell_data[idx]])

        t = threading.Thread(target=self.calculate, args=(data, 'EA', 'LK'))
        t.start()
        t = threading.Thread(target=self.calculate, args=('EA', 'EHO', self.curs))
        t.start()
        t = threading.Thread(target=self.calculate, args=('YZ', 'LK', self.curs))
        t.start()
        t = threading.Thread(target=self.calculate, args=('YZ', 'EHO', self.curs))
        t.start()
        t = threading.Thread(target=self.calculate, args=('GAN', 'LK', self.curs))
        t.start()
        t = threading.Thread(target=self.calculate, args=('GAN', 'EHO', self.curs))
        t.start()

        self.buy_data.pop(0);
        self.sell_data.pop(0);
        self.buy_data.append(buy_count);
        self.sell_data.append(sell_count);

        # reset buy/sell count
        REDIS_CLIENT.set('BITMEX:BUY', 0)
        REDIS_CLIENT.set('BITMEX:SELL', 0)

      time.sleep(self.sleep_timer);

  def calculate(self, data, main, sub):

    if main == 'EA':
      instance = ea.EAClass();
    elif main == 'GAN':
      instance = gan.GANClass();
    else:
      instance = yz.YZClass();

    result = instance.run(data, sub);
    print(main ,sub)
    print(result)
    self.curs.execute("INSERT INTO paramaters (alpha, delta, mu, epsilon_b, epsilon_s, likval, pin, trade_type) VALUES(%s, %s, %s, %s, %s, %s, %s, %s);", \
      (float(result['alpha']), float(result['delta']), float(result['mu']), float(result['epsilon_b']), float(result['epsilon_s']), float(result['likval']), float(result['pin']), f'{main}:{sub}' ))

a = InfoTrader();
