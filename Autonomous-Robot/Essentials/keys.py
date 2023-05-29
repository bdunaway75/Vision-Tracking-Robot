import time
import curses
import RPi.GPIO as GPIO
import time
from AlphaBot2 import AlphaBot2

Ab = AlphaBot2()
stdscr = curses.initscr()
curses.cbreak()
curses.noecho()
stdscr.keypad(1)

# stdscr.addstr(0,10,"Hit 'q' to quit")
# stdscr.refresh()

key = None
while (key != ord('q')):
    curses.halfdelay(4)
    key = stdscr.getch()
    stdscr.refresh()
    if key == curses.KEY_UP:
        stdscr.addstr(1, 1, "                  ")
        Ab.forward()
        stdscr.addstr(1, 1, "Key Pressed: Up")
    if key == curses.KEY_LEFT:
        stdscr.addstr(1, 1, "                  ")
        Ab.left()
        stdscr.addstr(1, 1, "Key Pressed: Left")
    if key == curses.KEY_RIGHT:
        stdscr.addstr(1, 1, "                  ")
        Ab.right()
        stdscr.addstr(1, 1, "Key Pressed: Right")
    if key == curses.KEY_DOWN:
        stdscr.addstr(1, 1, "                  ")
        Ab.backward()
        stdscr.addstr(1, 1, "Key Pressed: Down")
    elif key == -1:
        # stdscr.addstr(1, 1, "outside of loop")
        Ab.stop()
    
    
