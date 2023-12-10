import pygame
import socket
import sys
import json
import os

import threading
from logger import Logger
from AssetManager import assetManager
from player import Player
from network import Network

logger = Logger()

class Game:

   def __init__(self):
      pygame.font.init()
      self.SCREEN_X = 1318
      self.SCREEN_Y = 641
      self.screen = pygame.display.set_mode((self.SCREEN_X, self.SCREEN_Y))
      self.running = True
      self.clock = pygame.time.Clock()
      self.playerDict = {} # john: (player object), jane, jack, game.players[name].position = clientData["position"]
      self.playerSprites = pygame.sprite.Group()
      self.network = None
      self.started = False
   
   def playerMovedEvent(self):
      return {
         "eventType": "playerMoved",
         "playerId": player.id,
         "name": player.username,
         "position": tuple(player.position),
         "color": player.color,
         "currentSprite": player.currentSprite
      }
   
   def playerJoinedEvent(self):
      return {
         "eventType": "playerJoined",
         "playerData": self.playerMovedEvent()
      }

   def playerLeftEvent(self):
      return {
         "eventType": "playerLeft",
         "playerId": player.id
      }

   def playerUpdatedColorEvent(self):
      return {
         "eventType": "playerUpdatedColor",
         "playerId": player.id,
         "newColor": player.color
      }

   def handleEventKey(self, key):
      # handle key events
      if key == pygame.K_ESCAPE:
         self.network.send(self.playerLeftEvent())
         game.network.connection.close()
         logger.warn("Shutting down client", "Client")
         self.running = False
         sys.exit()

      if key == pygame.K_LSHIFT:
         player.sprinting = not player.sprinting

   def handleEvents(self, event):
      # handle events
      if event.type == pygame.KEYDOWN:
         self.handleEventKey(event.key)
      
      keys = pygame.key.get_pressed()
      
      if keys[pygame.K_w]:
         player.animate()
         self.network.send(self.playerMovedEvent())
      
      if event.type == pygame.KEYUP:
         if event.key == pygame.K_w:
            player.keyup() 
         if event.key == pygame.K_LSHIFT:
            player.sprinting = not player.sprinting
   
   def calculateShadow(self):
      shadow_width, shadow_height = AssetManager.UI["shadow"].get_size()
      shadow_x = player.rect.centerx - shadow_width // 2
      shadow_y = player.rect.centery - shadow_height // 2
      return ((shadow_x, shadow_y))
   
   def draw(self):

      self.screen.fill((255, 255, 255) if not self.started else (0, 0, 0))
      self.screen.blit(AssetManager.UI["map"], (0, 0) if not self.started else None)

      self.playerSprites.update(self.screen, pygame.Vector2(pygame.mouse.get_pos()))
      self.playerSprites.draw(self.screen)

      if game.started:
         self.screen.blit(AssetManager.UI["shadow"], self.calculateShadow())

      staminaBar = pygame.transform.scale(AssetManager.UI["stamina_bar"], (int(player.stamina) * 2, 16))
      self.screen.blit(staminaBar, (20, self.SCREEN_Y - 30))

      self.screen.blit(self.usernameSurface, (player.position[0] - self.usernameSurface.get_width() // 4, player.position[1] - int(self.usernameSurface.get_height())))
   
   def start(self):

      self.font = pygame.font.Font("./sus.ttf", 37)
      self.usernameSurface = self.font.render(player.username, True, (255, 255, 255)) # draw username above head

      while self.running:
         for event in pygame.event.get():
            if event.type == pygame.QUIT:
               self.running = False
            else:
               self.handleEvents(event)

         self.draw()

         game.clock.tick(60)
         fps = int(self.clock.get_fps())
         pygame.display.set_caption(f"Among us Ascended [CLIENT] - FPS: {fps}")

         pygame.display.update()



game = Game()
AssetManager = assetManager()

class Menu:

   def __init__(self):
      pygame.font.init()
      self.SCREEN_X = 1318
      self.SCREEN_Y = 641
      self.screen = pygame.display.set_mode((self.SCREEN_X, self.SCREEN_Y))
      self.running = True
      self.clock = pygame.time.Clock()
      self.connectImage = AssetManager.UI["connect"]
      self.buttonRect = self.connectImage.get_rect()
      self.buttonX = game.SCREEN_X / 2 - self.buttonRect.width / 2
      self.buttonY = 463
      self.buttonRect.x, self.buttonRect.y = self.buttonX, self.buttonY
      self.username = os.getlogin()
      self.fontSize = 45
      self.font = pygame.font.Font("./sus.ttf", self.fontSize)
      self.usernameSurface = self.font.render(self.username, True, (255, 255, 255))
      self.usernameRect = self.usernameSurface.get_rect()
      self.usernameRect.x, self.usernameRect.y = 30, 467
      self.usernameWriting = False
      self.IPWriting = False
      self.ipInput = "localhost"
      self.ipSize = 90
      self.ipFont = pygame.font.Font(None, self.ipSize)
      self.ipTextSurface = self.ipFont.render(self.ipInput, True, (255, 255, 255))
      self.ipTextRect = self.ipTextSurface.get_rect()
      self.ipTextRect.x, self.ipTextRect.y = 361, 310


   def handleEventKey(self, event):
      # handle key events
      key = event.key
      if key == pygame.K_ESCAPE:
         self.running = False
         logger.warn("Exiting client", "Game")
         sys.exit()
      else: # username thing
         if self.usernameWriting:
            if key == pygame.K_BACKSPACE:
               self.username = self.username[:-1]
            else:
               self.username += event.unicode
         if self.IPWriting:
            if key == pygame.K_BACKSPACE:
               self.ipInput = self.ipInput[:-1]
            else:
               self.ipInput += event.unicode

   def handleEvents(self, event):

      if event.type == pygame.KEYDOWN:
         self.handleEventKey(event)
      
   def handleButtons(self, buttons, event):
      # handle button events
      if buttons[0] and self.buttonRect.collidepoint(pygame.mouse.get_pos()): # mouse button 1
         
         # Exit and continiue under the class with attempting to connect
         try:
            game.network = Network(serverAddress=menu.ipInput, serverPort=8080)
            self.running = False
         except socket.error as e:
            #self.running = False # this shoudl be removed, only temporary test
            logger.error(e, "Network")
            return
           
      if (
         event.type == pygame.MOUSEBUTTONDOWN
         and buttons[0]
         and self.usernameRect.collidepoint(pygame.mouse.get_pos())
      ):
         self.usernameWriting = not self.usernameWriting
         logger.info(f"{self.usernameWriting}", "UsernameSelected")

      if (
         event.type == pygame.MOUSEBUTTONDOWN
         and buttons[0]
         and not self.usernameRect.collidepoint(pygame.mouse.get_pos())
      ):
         self.usernameWriting = False
         logger.info(f"{self.usernameWriting}", "UsernameSelected")
      
      if (
         event.type == pygame.MOUSEBUTTONDOWN
         and buttons[0]
         and self.ipTextRect.collidepoint(pygame.mouse.get_pos())
      ):
         self.IPWriting = not self.IPWriting
         logger.info(f"{self.IPWriting}", "IPInputSelected")
      
      if (
         event.type == pygame.MOUSEBUTTONDOWN
         and buttons[0]
         and not self.ipTextRect.collidepoint(pygame.mouse.get_pos())
      ):
         self.IPWriting = False
         logger.info(f"{self.IPWriting}", "IPInputSelected")

   def draw(self):
      self.screen.blit(AssetManager.UI["menu"], (0, 0))
      self.screen.blit(AssetManager.UI["connect"], (self.buttonX, self.buttonY))
      self.usernameSurface = self.font.render(self.username, True, (255, 255, 255))
      self.screen.blit(self.usernameSurface, (self.usernameRect.topleft))
      self.ipTextSurface = self.ipFont.render(self.ipInput, True, (255, 255, 255))
      self.screen.blit(self.ipTextSurface, (self.ipTextRect.topleft))
      '''pygame.draw.rect(self.screen, (255, 0, 0), self.ipTextRect, 2)
      pygame.draw.rect(self.screen, (255, 0, 0), self.usernameRect, 2)''' # debugging
   
   def start(self):

      while self.running:
         for event in pygame.event.get():
            if event.type == pygame.QUIT:
               self.running = False

            self.handleEvents(event)
            self.handleButtons(pygame.mouse.get_pressed(), event)

         self.draw()

         game.clock.tick(60)
         fps = int(self.clock.get_fps())
         pygame.display.set_caption(f"Among us Ascended - Menu - [CLIENT] - FPS: {fps}")

         pygame.display.update()

menu = Menu()
menu.start()  # This will finish when the user connects or exits

# Attempt to connect to the server
#clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # maybe something along these lines
#clientSocket.connect((menu.ipInput, 8080))

player = Player(617, 152, menu.username, game.network.connection.getsockname()[1])
game.playerDict[player.id] = player
game.playerSprites.add(game.playerDict[player.id])

thread = threading.Thread(target=game.network.thread, daemon=True)
thread.start()

# set network attribuets, player, playerdict, etc.
game.network.player = player
game.network.playerDict = game.playerDict
game.network.playerSprites = game.playerSprites

game.network.send(game.playerJoinedEvent())

game.start()