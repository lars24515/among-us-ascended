import socket
import json

class Network:
   def __init__(self):
      server_addr = "localhost"
      port = 8080

      self._queue = []

      self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.conn.settimeout(1)
      self.conn.connect((server_addr, port))
      self.conn.settimeout(None)

      print("Connected to server!")

   def send(self, data):
      self._queue.append(data)

   def thread(self):
      while True:
         try:
               data = json.loads(self.conn.recv(1024).decode())
               if data is not None:
                  print("received", data)

               next_data = self._queue.pop(0) if self._queue else None
               self.conn.sendall(json.dumps(next_data).encode())

         except socket.error:
               break
      print("Lost connection.")
