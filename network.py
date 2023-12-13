import socket
import json

from logger import Logger
from player import Player

logger = Logger()

class Network:
   def __init__(self, serverAddress, serverPort):
      self.serverAddress = serverAddress
      self.serverPort = serverPort
      self._queue = []
      self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.connection.settimeout(1)
      self.connection.connect((self.serverAddress, self.serverPort))
      self.connection.settimeout(None)
      self.serverAddress, self.serverPort = self.connection.getpeername()  # Get the server address and port
      self.playerDict = None
      self.playerSprites = None
      self.player = None
      logger.success(f"Connected to server at {self.serverAddress}:{self.serverPort}", "Client")
      self.clientIds = []
   
   def getClientAddress(self):
      return self.connection.getsockname()[1]
      
   def processData(self, data):
      match data["eventType"]:
         case "playerJoined":
            if data["playerData"]["playerId"] == self.getClientAddress():
               return
            
            print("received player joined:", data)
            data = data["playerData"]
            try:
               newPlayer = Player(data["position"][0], data["position"][1], data["name"], data["playerId"])
            except KeyError as e:
               print(data)
               print(e)


            try:
               self.playerDict[data["playerId"]] = newPlayer
               self.playerSprites.add(newPlayer)
               logger.success(f"Player {data['name']} joined", "Client")
            except Exception as e:
               logger.error(e, "Client")

         case "playerLeft":
            player = self.playerDict[data["playerId"]]
            self.playerSprites.remove(player)
            logger.info(f"Player {data['name']} left the game", "Client")

         case "playerMoved":
            try:
               player = self.playerDict[data["playerId"]]
            except KeyError:
               logger.error(f"Player {data['playerId']} not found", "Client")
               return

            player.position = data["position"]
            player.currentSprite = data["currentSprite"]

         case "updatePlayerColor":
            self.player.color = data["newColor"]
            logger.success(f"Updated player color to {self.player.color}", "Client")
            self.player.updateSpritePath()

   def send(self, data):
      self._queue.append(data)

   def thread(self):
      while True:
         try:
            received_data = self.connection.recv(1024).decode()
            #print("Received data:", received_data)
            data = json.loads(received_data)
               
            if data is not None:
               self.processData(data)

            nextData = self._queue.pop(0) if self._queue else None
            self.connection.sendall(json.dumps(nextData).encode())

         except socket.error:
            break
      logger.error("Lost connection to server\n", "Client")