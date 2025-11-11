import webbrowser
import time
import pyautogui

# Safety & small pause between PyAutoGUI actions
pyautogui.FAILSAFE = True   # move mouse to top-left to abort
pyautogui.PAUSE = 0.35      # small pause after every PyAutoGUI call

TO_EMAIL = "muralinkl@zohomail.in"
SUBJECT = "Automated message from PyAutoGUI"
BODY = "TESTING OF PYAUTOGUI"

def open_gmail_compose():
    """
    Open Gmail's compose view directly using the compose URL.
    Note: this opens the default browser. Ensure you're logged in there.
    """
    # Opening the compose URL; Gmail usually loads a compose dialog automatically
    webbrowser.open("https://mail.google.com/mail/u/0/#inbox?compose=new")
    # Wait for browser to open & Gmail to load - adjust based on your network speed
    time.sleep(8)

def focus_gmail_window():
    """
    Try to ensure Gmail has focus. We attempt a safe approach:
    - Click near the center of the screen to give the browser focus.
    If you prefer, replace with coordinates for your machine.
    """
    screen_w, screen_h = pyautogui.size()
    pyautogui.click(screen_w // 2, screen_h // 4)  # click near top-middle to focus browser
    time.sleep(0.5)

def compose_and_send(to, subject, body):
    """
    Compose the mail using keyboard navigation which is more robust than fixed coordinates:
    - 'c' opens compose in Gmail (when Gmail window is focused)
    - type recipient, Enter to accept, Tab to reach subject, then Tab to reach body
    - Ctrl+Enter sends the email
    """
    # Open compose modal (works when Gmail window is focused)
    pyautogui.press('c')
    time.sleep(1)

    # Type recipient
    pyautogui.click(1246,420)
    pyautogui.write(to, interval=0.04)
    pyautogui.press('enter')    # accept the email address
    time.sleep(0.3)

    # Move to subject: pressing tab usually focuses subject after recipient accepted
    pyautogui.press('tab')
    time.sleep(0.2)
    pyautogui.write(subject, interval=0.04)
    time.sleep(0.2)

    # Move to message body
    pyautogui.press('tab')
    time.sleep(0.2)
    pyautogui.write(body, interval=0.04)
    time.sleep(0.5)

    # Send the email (Ctrl+Enter works in Gmail to send)
    pyautogui.hotkey('ctrl', 'enter')
    time.sleep(0.7)

def main():
    print("Opening Gmail...")
    open_gmail_compose()
    focus_gmail_window()

    # Optional: alert to user so they can move cursor away
    print("Composing message. Move mouse to top-left to abort if needed.")
    compose_and_send(TO_EMAIL, SUBJECT, BODY)
    print("Done. Check the Sent mail in your Gmail.")

if __name__ == "__main__":
    main()