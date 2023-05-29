from AlphaBot2 import AlphaBot2
import RPi.GPIO as GPIO
import curses
import time
from curses.textpad import Textbox, rectangle

class curses_inter(object):
    
    def __init__(self):
        self.Ab = AlphaBot2()           # Initializes AB instance for main program
        self.stdscr = curses.initscr()
        self.key = None
        self.stdscr.keypad(1)           # Enables use of special keys (arrow-keys) 
        self.stdscr.nodelay(True)

    def manual(self):
        self.key = self.stdscr.getch()                       # Waits for user to press key
        curses.noecho()                                      # Does not print pressed key to screen

        if self.key == curses.KEY_UP:
            self.stdscr.addstr(7, 1, "                  ")   # Overwrite previous message with spaces
            self.stdscr.addstr(7, 1, "Key Pressed: Up")
            self.Ab.forward()
            time.sleep(0.075)
            self.Ab.stop()
        if self.key == curses.KEY_LEFT:
            self.stdscr.addstr(7, 1, "                  ")
            self.stdscr.addstr(7, 1, "Key Pressed: Left")
            self.Ab.left()
            time.sleep(0.075)
            self.Ab.stop()
        if self.key == curses.KEY_RIGHT:
            self.stdscr.addstr(7, 1, "                  ")
            self.stdscr.addstr(7, 1, "Key Pressed: Right")
            self.Ab.right()
            time.sleep(0.075)
            self.Ab.stop()
        if self.key == curses.KEY_DOWN:
            self.stdscr.addstr(7, 1, "                  ")
            self.stdscr.addstr(7, 1, "Key Pressed: Down")
            self.Ab.backward()
            time.sleep(0.075)
            self.Ab.stop()
    
    def checking_keys(self):
        self.key = self.stdscr.getch() # Waits for user to press key
        curses.noecho()                # Does not print pressed key to screen

        if self.key == ord('m'):       # manual mode
            self.key = 'm'
            return self.key
        elif self.key == ord('a'):     # autonomous mode
            self.key = 'a'
            return self.key
        elif self.key == ord('q'):     # quit
            self.key = 'q'
            return self.key
        elif self.key == ord('t'):     # test
            self.key = 't'
            return self.key
                
