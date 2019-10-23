import websocket
import numpy as np
import redis
try:
    import thread
except ImportError:
    import _thread as thread
import time


class RedisClient:
  def __init__(self, host, port, db, password):
    self.host = host;
    self.port = port;
    self.password = password;
    self.db = db;
    self.conn = redis.Redis(host=self.host, port=self.port, db=self.db, password=self.password)

