import socket
import json
import random
import sys

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
      self.joinedEvents = {} # 123456: playerJoinedEvent

   def handOutRoles(self):
      for client in clients:
         pass
      #set roles

   def handlePlayerMovedEvent(self, data):
      for client in clients:
         if client.address[0] == data["playerId"]:
            return
         
         client.send(data)

   # current solution: make the updateColorEvent client sided again, which means that
   # when the player joins, it is send an event to update it's color accordingly, and the server will also
   # use that color data when sending the playerJoined event to the rest of the clients.

   def handlePlayerJoinedEvent(self, data):
      # YOU NEED TO SEND PLAYER JOINED OF ALL OTHER PLAYERS TO THIS NEW CLIENT SINCE IT HASNT RECEIVED
      # THE JOIN EVENTS BEFORE, THEREFORE IT CANNOT SEE THEM
      self.playerCount += 1
      logger.info(f"{self.playerCount} of {self.minimumPlayers} players connected", "Server")
      receivedData = data["playerData"]

      newColor = self.assignColor(receivedData["playerId"])

      logger.info(f"Player {receivedData['name']}: {newColor} joined", "Server")
      self.playerIds[receivedData["playerId"]] = "defaultRole"

      print(len(clients))
      print(clients)

      for client in clients:
         try:
            addr = client.getClientAddress()
            if not addr == receivedData["playerId"]: # client is not self client
               data["eventType"] = "playerJoined"
               logger.info(f"Sending playerJoined event to {addr}", "Server")
               logger.info(f"Data: Name: {receivedData['name']}, Color: {newColor} ID: {receivedData['playerId']}", "Server")
               client.send(data)
               self.joinedEvents[addr] = data
            print(f"set {addr} in server joinedEventDict")
         except Exception as e:
            logger.error(e, "Networking")

      # and make sure to send all existing clients to the new client (not itself though)
      
      # add debugging statements around here, because for some reason it doesnt start sending playerJoined to the new client
      # of existing clients

      # maybe it has to do with the fact that its not appending its own event to joinedevents? check the conditions.

      try:

         for client in clients:
            addr = client.getClientAddress()
            if not addr == receivedData["playerId"]:
               print(f"client address {addr} is not equal to {receivedData['playerId']}")
               return
            print("found equal address, continiuing :D")
            print(f"it should iterate {len(self.joinedEvents)} times btw (2?)")
            for data in self.joinedEvents.values():
               print("iterating through joined events")
               logger.info(f"Sending playerJoined event to {addr}", "Server")
               logger.info(f"Data: Name: {receivedData['name']}, Color: {newColor} ID: {receivedData['playerId']}", "Server")
               client.send(data)

      except Exception as e:
         logger.error(e, "Networking")

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
         if not client.getClientAddress() == playerId:
            return
          
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
   
   def getClientAddress(self):
      return self.address[1]
   
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