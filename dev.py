import os
import time
import random
import numpy
import math

from os.path import exists

import shlex
from subprocess import Popen, PIPE

os.environ["SDL_FBDEV"] = "/dev/fb1"

fileCurrent = "/tmp/currentTide"
filePrevious = "/tmp/previousTide"

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
  global previousF #if these are global why are they scoped in the method?
  global currentF #once we get some output without any devices loading we can move these around and figure out what they do/
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

	  print 'Booting script without display drivers'

  def tide(self):
    # Load and display tide image
    cmd = 'tide -l "Middle Arm, British Columbia" -m g -gh 240 -gw 320 -f p > /tmp/pytide.png'
    os.system( cmd )
    # xtideImg = Image.open("/tmp/pytide.png")

    # img = Image.new("RGB", (1, 192), "black")
    # pixels = img.load()
    # im = numpy.array(img)

    # tidePixels = xtideImg.load()
    getTideData()

    #lets work with the numbers a bit and create some variables.
    if currentF > previousF:
      rising = True

    percentage = currentF/5
    goingUp = currentF/5*192
    goingDown = 192 - (currentF/5*192)

    print goingUp
    print goingDown

    # colour background
    for y in range (0, 192):
      pixels[0, y] = (0, int(bgBrightnessG*percentage), int(bgBrightnessB)) # green varies with depth full blue

    # colour indicator
    # start from the top, as our image starts there.
    #
    # This makes the image upside down!
    # split tide into whole numbers and decimals on a range of 0 to 192
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

    # colour background
    for x in range (301,320):
      for y in range (0, 240):
        tidePixels[x, y] = (0, 0, 0) # black background.

    # colour lighting pattern
    for x in range (306,315):
      for y in range (0, 192):
        tidePixels[x, y+24] = pixels[0, 191-y] # add tide pattern NOTE that

    # convert PIL image to pygame image and output it to framebuffer.
    # mode = xtideImg.mode
    # size = xtideImg.size
    # data = xtideImg.tostring()
  #  tideImg = pygame.image.fromstring(data, size, mode)
#    fbi.screen.blit(tideImg, (0, 0))
    #pygame.display.update()

    #lets wait for a bit
    time.sleep(30)

# Create an instance of the PyFbi class
fbi = pyFbi()
while True:
  fbi.tide()
