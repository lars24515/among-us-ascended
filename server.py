import socket
import json
from threading import Thread

# This will be purely python backend, no pygame

from logger import Logger
logger = Logger()

clients = []

class Server:

   def __init__(self, addr, port):
      self.address = addr
      self.port = port
      self.data = {}
   
   def updateClients(self):
      for client in clients:
         client.send(self.data)

server = Server("192.168.10.189", 8080)

class ClientConnection:
   def __init__(self, connection, address):
      self.connection = connection
      self. address = address
      self._queue = []
   
   def send(self, data):
      self._queue.append(data)
   
   def thread(self):
      while True:
         try:
            nextData = self._queue.pop(0) if self._queue else None
            self.connection.sendall(json.dumps(nextData).encode())
            data = json.loads(self.connection.recv(1024).decode())

            if data is not None:
               logger.info(f"Received {data} from {self.address}", "Server")
               server.data[self.address[1]] = data
               server.updateClients()

         except (ConnectionResetError, KeyboardInterrupt):
            break
         

      logger.error(f"Lost connection to {self.address}", "Server")
      self.connection.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
   serverSocket.bind((server.address, server.port))
   serverSocket.listen(2)
   logger.success(f"Server listening on {server.address}:{server.port}", "Server")

   while True:
      try:
         connection, address = serverSocket.accept()
         logger.success(f"Conected to {address}", "Server")
         user = ClientConnection(connection=connection, address=address)
         clients.append(user)
         thread = Thread(target=user.thread, daemon=True)
         thread.start()
      except KeyboardInterrupt:
         logger.warn("Shutting down server", "Server")
         break