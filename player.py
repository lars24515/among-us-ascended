import pygame
import random
import math

from AssetManager import assetManager
from logger import Logger

AssetManager = assetManager()
logger = Logger()

availableColors = { "white": AssetManager.whiteMovingSprites[0], "red": AssetManager.redMovingSprites[0] } 

class Player(pygame.sprite.Sprite):

   class Hand:

      def __init__(self, player, radius, color, thickness):
         self.player = player 
         self.radius = radius
         self.color = color
         self.thickness = thickness
         self.position = None
         self.item = None
         self.x = None
         self.y = None

      def update(self, angle, screen):
         adjusted_radius = self.radius / 2 * 1.8

         center_x = self.player.position.x + self.player.width / 2
         center_y = self.player.position.y + self.player.height / 2

         hand_x = center_x + adjusted_radius * math.cos(math.radians(angle))
         hand_y = center_y + adjusted_radius * math.sin(math.radians(angle))

         self.x, self.y = hand_x, hand_y

         self.position = (int(hand_x), int(hand_y))
         pygame.draw.circle(screen, (0, 0, 0), self.position, self.thickness + 2)
         pygame.draw.circle(screen, self.color, self.position, self.thickness)

   def __init__(self, x, y, username):
      super().__init__()
      self.username = username
      self.x = x
      self.y = y
      self.position = pygame.Vector2(x, y)
      self.color = random.choice(list(availableColors.keys()))
      self.image = availableColors[self.color]
      self.rect = self.image.get_rect()
      self.rect.x, self.rect.y = self.x, self.y
      self.height = self.image.get_height()
      self.width = self.image.get_width()
      self.hand = self.Hand(self, radius=32, color=(255, 0, 0), thickness=5)
      self.velocity = 2
      self.stamina = 100
      self.staminaDrain = 0.5
      self.staminaRegen = 0.125
      self.sprinting = False
      self.isAnimating = False
      self.currentSprite = 0
      self.angle = 0
      # log
      logger.info(f"Player {self.color}: {self.username} created at {self.position}. Animating: {self.isAnimating} Sprinting: {self.sprinting}", "PlayerManager")

   def calculate_velocity(self, cursor_position):

      max_velocity = 1.5
      min_velocity = 0.5

      distance = self.position.distance_to(cursor_position)
      max_distance = 200.0 
      normalized_distance = min(distance / max_distance, 1.0)

      self.velocity = min_velocity + normalized_distance * (max_velocity - min_velocity)

      if self.sprinting and not self.stamina <= 0:
         self.velocity +=1
         self.stamina -= self.staminaDrain

   def animate(self):
      self.isAnimating = True
   
   def keyup(self):
      self.isAnimating = False
      self.currentSprite = 0
   
   def flipSelfImage(self):
      self.image = pygame.transform.flip(self.image, True, False)

   def check_collision(self, next_position, screen):
        color_at_next_position = screen.get_at((int(self.hand.x), int(self.hand.y)))
        return color_at_next_position == (0, 0, 0, 255)

   def update(self, screen, cursorPosition):

      dx = cursorPosition.x - self.position.x
      dy = cursorPosition.y - self.position.y
      angle = math.atan2(dy, dx)
      self.angle = math.degrees(angle)

      if self.isAnimating:
         
         self.currentSprite += 0.17

         if self.currentSprite >= 4:  # 4 frames in all animations
               self.currentSprite = 0

         move_distance = self.velocity
         move_angle = math.radians(self.angle)

         delta_x = move_distance * math.cos(move_angle)
         delta_y = move_distance * math.sin(move_angle)

         self.position.x += delta_x
         self.position.y += delta_y

         self.calculate_velocity(cursorPosition)

         nextPosition = (int(self.position.x + delta_x), int(self.position.y + delta_y))
         if self.check_collision(nextPosition, screen):
               self.velocity = 0
      
      if not self.sprinting:
         self.stamina += self.staminaRegen

         if self.stamina > 100:
            self.stamina = 100

      self.hand.update(self.angle, screen)

      self.rect.x, self.rect.y = self.position

      if self.angle < -90 or self.angle >= 90:
         self.image = AssetManager.whiteMovingSprites[int(self.currentSprite)]
         self.flipSelfImage()
      else:
         self.image = AssetManager.whiteMovingSprites[int(self.currentSprite)]