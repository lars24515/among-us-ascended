import socket
import json
import random

from threading import Thread

# This will be purely python backend, no pygame

from logger import Logger
from AssetManager import assetManager

logger = Logger()
AssetManager = assetManager()

clients = []

class Server:

   def __init__(self, addr, port):
      self.address = addr
      self.port = port
      self.playerCount = 0
      self.minimumPlayers = 2
      self.gameStarted = False
      self.availableColors = { "white": AssetManager.whiteMovingSprites[0], "red": AssetManager.redMovingSprites[0] } 
      self.assignedColors = {} # 123456: {"white": AssetManager.whiteMovingSprites[0]}, {"red": AssetManager.redMovingSprites[0]}
      self.playerIds = {} # 123456: "impostor", 789012: "crewmate"

   def handOutRoles(self):
      for client in clients:
         pass
      #set roles

   def handlePlayerMovedEvent(self, data):
      for client in clients:
         if client.address[0] == data["playerId"]:
            return
         
         client.send(data)

   def handlePlayerJoinedEvent(self, data):
      self.playerCount += 1
      logger.info(f"{self.playerCount} of {self.minimumPlayers} players connected", "Server")
      data = data["playerData"]

      newColor = self.assignColor(data["playerId"])

      logger.info(f"Player {data['name']}: {newColor} joined", "Server")
      self.playerIds[data["playerId"]] = "defaultRole"

      for client in clients:
         try:
            if client.address[0] == ["playerId"]:
               return
         except KeyError:
            if client.address[0] == data["playerData"]["playerId"]:
               return

         # client is not self client
         # so tell client that a new player that isnt 'me' joined
         print("sending player joined")

         data = {
            "eventType": "playerJoined",
            "playerData": data
         }

         client.send(data)

      if self.playerCount == self.minimumPlayers:
         logger.info(f"Game starting with {self.playerCount} out of {self.minimumPlayers} players", "Server")
         self.gameStarted = True
         self.handOutRoles()
   
   def handlePlayerLeftEvent(self, data):
      logger.info(f"Player {data['name']} left", "Server")
      self.playerCount -= 1
      # Also free up that color as available

   def assignColor(self, playerId):
      color = random.choice(list(self.availableColors))
      self.assignedColors[playerId] = {color: self.availableColors[color]}
      del self.availableColors[color]

      for client in clients:
         logger.info(f"({client.address[1]} == {playerId}) == {client.address[1] == playerId}", "Debugger")

         if client.address[1] == playerId:
            data = {
               "eventType": "updatePlayerColor",
               "newColor": color
            }
            client.send(data)
            logger.info(f"Assigning color {color} to {playerId}..", "Server")
      return color

   def processData(self, data):
      match data["eventType"]:
         case "playerJoined":
            self.handlePlayerJoinedEvent(data)

         case "playerLeft":
            self.handlePlayerLeftEvent(data)
            
         case "playerMoved":
            self.handlePlayerMovedEvent(data)
   
  

server = Server("localhost", 8080)

class ClientConnection:
   def __init__(self, connection, address):
      self.connection = connection
      self.address = address
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
               server.processData(data)
               
               # process data from server

         except (ConnectionResetError, json.decoder.JSONDecodeError, KeyboardInterrupt):
            break
         

      logger.error(f"Lost connection to {self.address[1]}", "Server")
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
      except (ConnectionResetError, json.decoder.JSONDecodeError, KeyboardInterrupt):
         logger.warn("Shutting down server", "Server")
         break