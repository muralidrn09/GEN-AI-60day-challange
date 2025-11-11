import time
import webbrowser

import pyautogui

# Step 1: Open the browser
webbrowser.open("https://www.google.com")
time.sleep(2)  # Wait for browser to open

# Step 2: Click on the Google search bar
pyautogui.click(763, 460)  # Adjust coordinates for your Google search bar
time.sleep(1)

# Step 3: Type "WhatsApp Web" and press Enter
pyautogui.write("WhatsApp Web", interval=0.1)
pyautogui.press("enter")
time.sleep(2)

# Step 4: Click on the first link (top search result)
pyautogui.click(343, 362)  # Adjust this to where the first link appears
time.sleep(1)  # Wait for WhatsApp Web to load completely

# Step 5: Search for the contact (e.g., Priyamurali)
pyautogui.click(
    218, 194
)  # Click on s                                 earch box on WhatsApp Web
# time.sleep(1)
pyautogui.typewrite("Priyanka Murali", interval=0.1)
time.sleep(3)

# Step 6: Click on the chat
pyautogui.click(218, 194)  # Adjust to the first chat result
time.sleep(2)

# Step 7: Type and send a message
pyautogui.write("Hi, how are you?", interval=0.1)
pyautogui.press("enter")

print("Message sent successfully ✅")
