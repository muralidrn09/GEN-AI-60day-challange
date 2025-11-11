import time

import pyautogui

time.sleep(5)  # Give user time to switch to the target application
x, y = pyautogui.position()  # Get the current mouse position
print(f"x: {x}, y:{y})")
