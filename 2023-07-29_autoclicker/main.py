import pyautogui
import time
import msvcrt

"""
python3 ./2023-07-29_autoclicker/main.py
"""

def is_pressed(key):
    return msvcrt.kbhit() and msvcrt.getch() == key.encode()

# simple autoclicker that clicks where the mouse is at, n times per second. 
n = 1
autoclick = False
while True:
    if is_pressed(b'x'):
        autoclick = not autoclick
        print(f"Autoclick: {autoclick}")

    if autoclick:
        pyautogui.click()
        time.sleep(1/n)
