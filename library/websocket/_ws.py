import websocket
import numpy as np
import redis
try:
    import thread
except ImportError:
    import _thread as thread
import time

class WebSocket:
  def __init__(self, market, url):
    self.url = url;
    self.market = market;
    self.ws = None;

  def on_error(self, error):
    print(f'{self.market} Websocket Error, {error}')

  def on_close(self):
    print(f'{self.market} Websocket Close.')

  def connect(self, on_open, on_message):
    websocket.enableTrace(True)
    self.ws = websocket.WebSocketApp(self.url,
                              on_message = on_message,
                              on_error = self.on_error,
                              on_close = self.on_close)
    self.ws.on_open = on_open
    self.ws.run_forever()
    # thread.start_new_thread(ws.run_forever, ())
