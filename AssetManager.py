from logger import Logger
import pygame
import os

logger = Logger()

pygame.display.set_mode((1, 1), pygame.NOFRAME)

class assetManager:
      
      def __init__(self):

         self.whiteMovingSprites = self.getImages("./Sprites/Player/White/Move", transform=True, list=True)
         self.whiteDeathSprites = self.getImages("./Sprites/Player/White/Death", transform=True, list=True)
         self.redMovingSprites = self.getImages("./Sprites/Player/red/Move", transform=True, list=True)
         self.redDeathSprites = self.getImages("./Sprites/Player/red/Death", transform=True, list=True)
         self.defaultImage = self.getImages("./Sprites/Player", transform=True, list=True)[0]
         self.UI = self.getImages("./Sprites/UI", transform=False, list=False)
         logger.info(self.whiteMovingSprites, "WhiteChar")
         logger.info(self.whiteDeathSprites, "WhiteChar")

      def getImages(self, path, transform=True, list=False):
         os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
         new_map = {}
         newList = []
         logger.info(f"Loading files for {path}..", "AssetManager")
         
         for fileName in os.listdir(path):
            if fileName.endswith(".png"):
                  filePath = os.path.join(path, fileName)
                  image = pygame.image.load(filePath).convert_alpha()
                  name = fileName.split(".")[0]

                  if transform:
                     image = pygame.transform.scale(image, (64, 64))

                  if not list:
                     new_map[name] = image
                  else: # its a list
                     newList.append(image)

                  logger.info(f"loaded {fileName} with transform {transform}", "AssetManager")

         logger.success(f"loaded all files from {path}", "AssetManager")

         if not list:
            return new_map
         else:
            return newList