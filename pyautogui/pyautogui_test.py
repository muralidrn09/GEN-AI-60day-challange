import time

import pyautogui

# Mouser operations
pyautogui.click(100, 100)  # Move mouse to (100, 100) over 1 second
# pyautogui.rightClick(100, 100)  # Right click at (200, 200)

time.sleep(10)  # Pause for 1 second

x, y = pyautogui.position()  # Get the current mouse position
print(f"Current mouse position: ({x}, {y})")
pyautogui.rightClick(x, y)  # Right click at the current mouse position
time.sleep(2)  # Pause for 1 second
pyautogui.doubleClick(x, y)  # Double click at the current mouse position
time.sleep(2)  # Pause for 1 second
pyautogui.scroll(500)  # Scroll up 500 units
