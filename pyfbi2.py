import os
import pygame
from pygame.locals import *
import time
import random
import numpy
import math

from os.path import exists
from PIL import Image

import shlex
from subprocess import Popen, PIPE



os.environ["SDL_FBDEV"] = "/dev/fb1"
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
os.environ["SDL_MOUSEDRV"] = "TSLIB"
#os.putenv('SDL_NOMOUSE', '1')

bgBrightnessB = 255
bgBrightnessG = 255
whiteBrightness = 255

rising = True

previousF = 0
currentF = 0

def get_exitcode_stdout_stderr(cmd):
    """
    Execute the external command and get its exitcode, stdout and stderr.
    """
    args = shlex.split(cmd)

    proc = Popen(args, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    exitcode = proc.returncode
    #
    return exitcode, out, err

def getTideData():
  global previousF 
  global currentF
  cmd = 'tide -mr -l "Middle Arm, British Columbia" -s "96:00"'  # arbitrary external command, e.g. "python mytest.py"

  if previousF == 0.0:
    exitcode, out, err = get_exitcode_stdout_stderr(cmd)
    tTime, val = out.split()
    previousF = float(val)
    print "Previous Value: %f" %previousF
    time.sleep(30)
    exitcode, out, err = get_exitcode_stdout_stderr(cmd)
    tTime, val = out.split()
    currentF = float(val)
    print "Current Value: %f" %currentF
  else:
    previousF = currentF
    print "Previous Value: %f" %previousF
    exitcode, out, err = get_exitcode_stdout_stderr(cmd)
    tTime, val = out.split()
    currentF = float(val)
    print "Current Value: %f" %currentF



class pyFbi :
  screen = None;

  def __init__(self):
    pygame.init()
    pygame.display.init()
    size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    print "Framebuffer size: %d x %d" % (size[0], size[1])
    self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
    # Hide the mouse
    #pygame.mouse.set_visible(0)
    # Clear the screen to start
    self.screen.fill((0, 0, 0))        
    # Initialise font support
    pygame.font.init()
    # loading image
    loadImg = pygame.image.load("/home/pi/loading.png")
    self.screen.blit(loadImg, (0, 0))
    # Render the screen
    pygame.display.update()

  def __del__(self):
    "Destructor to make sure pygame shuts down, etc."

  def tide(self):
    # Load and display tide image
    cmd = 'tide -l "Middle Arm, British Columbia" -em pMm -m g -gh 240 -gw 320 -f p > /tmp/pytide.png'
    os.system( cmd )
    xtideImg = Image.open("/tmp/pytide.png")



    #    red = (255, 0, 0)
    #    self.screen.fill(red)
    # Update the display

    img = Image.new("RGB", (1, 200), "black")
    pixels = img.load()
    im = numpy.array(img)

    tidePixels = xtideImg.load()
    getTideData()

    # # load stored tide values
    # if exists(fileCurrent):
    #   cu = open(fileCurrent)
    #   print "Here's your file %r:" % fileCurrent
    #   currentTXT = cu.read()
    #   tTime, val = currentTXT.split()
    #   previousF = float(val)
    #   print previousF

    # if exists(filePrevious):
    #   pr = open(filePrevious)
    #   print "Here's your file %r:" % filePrevious
    #   previousTXT = pr.read()
    #   tTime, val = previousTXT.split()
    #   currentF = float(val)
    #   print currentF

    #lets work with the numbers a bit and create some variables.
    if currentF > previousF:
      rising = True

    percentage = currentF/5
    goingUp = currentF/5*200
    goingDown = 200 - (currentF/5*200)

    print goingUp
    print goingDown

    #print im

    # colour background
    for y in range (0, 200):
      pixels[0, y] = (0, int(bgBrightnessG*percentage), int(bgBrightnessB)) # green varies with depth full blue

    # colour indicator
    # start from the top, as our image starts there.
    # 
    # This makes the image upside down!
    #
    #
    # split tide into whole numbers and decimals on a range of 0 to 200
    # the decimal will allow us to fade up the incoming pixel so it doesn't jump.
    upDec, upInt = math.modf(goingUp)
    downDec, downInt = math.modf(goingDown)


    # current indicator is 7 pixels tall. May need to reduce that when we add the fade out tail.
    pixels[0,upInt] = (int(whiteBrightness),int(whiteBrightness),int(whiteBrightness))
    pixels[0,upInt-1] = (int(whiteBrightness),int(whiteBrightness),int(whiteBrightness))
    pixels[0,upInt-2] = (int(whiteBrightness),int(whiteBrightness),int(whiteBrightness))
    pixels[0,upInt+1] = (int(whiteBrightness),int(whiteBrightness),int(whiteBrightness))
    pixels[0,upInt+2] = (int(whiteBrightness),int(whiteBrightness),int(whiteBrightness))

    #draw leading edge fade
    r, g, b = pixels[0,upInt+3] 
    r = int(max(whiteBrightness*upDec , r))
    g = int(max(whiteBrightness*upDec , g))
    b = int(max(whiteBrightness*upDec , b))
    pixels[0,upInt+3] = r,g,b
    #draw trailing edge fade
    r, g, b = pixels[0,upInt-3] 
    r = int(max(whiteBrightness*downDec , r))
    g = int(max(whiteBrightness*downDec , g))
    b = int(max(whiteBrightness*downDec , b))
    pixels[0,upInt-3] = r,g,b

    #
    #  Still need to draw the tail to indicate tide direction. We may also 
    #


    # colour background
    for x in range (291,320):
      for y in range (0, 240):
        tidePixels[x, y] = (0, 0, 0) # black background.



    # colour lighting pattern
    for x in range (301,315):
      for y in range (0, 200):
        tidePixels[x, y+33] = pixels[0, 199-y] # add tide pattern NOTE that 

    # convert PIL image to pygame image and output it to framebuffer.
    mode = xtideImg.mode
    size = xtideImg.size
    data = xtideImg.tostring()
    tideImg = pygame.image.fromstring(data, size, mode)
    fbi.screen.blit(tideImg, (0, 0))
    pygame.display.update()

    #lets wait for a bit
    time.sleep(30)

# Create an instance of the PyFbi class

fbi = pyFbi()
while True:
  fbi.tide()
