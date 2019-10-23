import redis
import pymysql

from pprint import pprint
import time
import datetime
from config import BITMEX_CONFIG, MYSQL_INFO, REDIS_INFO

REDIS_CLIENT = redis.Redis(
  host = REDIS_INFO['host'],
  port = REDIS_INFO['port'],
  db = REDIS_INFO['db']
);

class QuotesSaver: 
  def __init__(self):
    self.quotes = {
      'ask': 0,
      'bid': 0,
    }

    self.sleep_timer = 1; # sec

    # Connection 으로부터 Cursor 생성
    self.conn = pymysql.connect(
      host = MYSQL_INFO['host'],
      user = MYSQL_INFO['user'],
      password = MYSQL_INFO['password'],
      db = MYSQL_INFO['db'],
      charset = 'utf8'
    );
    self.curs = self.conn.cursor()

    while True:
      self.run();
      time.sleep(self.sleep_timer);

  def run(self):
    ask = REDIS_CLIENT.get('BITMEX:ASK');
    bid = REDIS_CLIENT.get('BITMEX:BID');

    if ask != self.quotes['ask'] or bid != self.quotes['bid']:
      self.quotes['ask'] = ask
      self.quotes['bid'] = bid
      self.curs.execute("INSERT INTO quotes (ask, bid) VALUES(%s, %s);", (float(self.quotes['ask']), float(self.quotes['bid'])))
      self.conn.commit()
      print(self.quotes)


quotes_saver = QuotesSaver();
