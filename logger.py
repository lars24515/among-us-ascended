import colorama
from colorama import Fore
from datetime import datetime

colorama.init(autoreset=True)

CYAN = Fore.LIGHTBLUE_EX
GREEN = Fore.LIGHTGREEN_EX
RED = Fore.LIGHTRED_EX
YELLOW = Fore.LIGHTYELLOW_EX
GRAY = Fore.LIGHTBLACK_EX

class Logger:

   def __init__(self):
      pass

   def getTime(self):
      current_time = datetime.now().time()
      return current_time.strftime("%H:%M:%S")

   def info(self, message, parent=""):
      print(f"{GRAY}[{self.getTime()}]{Fore.RESET}{GRAY}[{CYAN}{'i'}{GRAY}]{CYAN}{parent}:{' '}{message}")

   def error(self, message, parent=""):
      print(f"{GRAY}[{self.getTime()}]{Fore.RESET}{GRAY}[{RED}{'!'}{GRAY}]{RED}{parent}:{' Error: '}{message}")

   def warn(self, message, parent=""):
      print(f"{GRAY}[{self.getTime()}]{Fore.RESET}{GRAY}[{YELLOW}{'-'}{GRAY}]{YELLOW}{parent}:{' Warning: '}{message}")

   def success(self, message, parent=""):
      print(f"{GRAY}[{self.getTime()}]{Fore.RESET}{GRAY}[{GREEN}{'+'}{GRAY}]{GREEN}{parent}:{' '}{message}")