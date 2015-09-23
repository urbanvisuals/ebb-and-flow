import os
import pygame
from pygame.locals import *
import time
import random
import numpy
import math
import signal
import threading
import array
from ola.ClientWrapper import ClientWrapper


from os.path import exists
from PIL import Image

import shlex
from subprocess import Popen, PIPE

TICK_INTERVAL = 100  # in ms


os.environ["SDL_FBDEV"] = "/dev/fb1"
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
os.environ["SDL_MOUSEDRV"] = "TSLIB"
#os.putenv('SDL_NOMOUSE', '1')

bgBrightnessB = 128
bgBrightnessG = 128
whiteBrightness = 255

rising = True

pixels = None

wrapper = None

#
#  SEND DMX to OLA here
#
def DmxSent(state):
  if not state.Succeeded():
    wrapper.Stop()

def SendDMXFrames():
  ## schdule a function call in 100ms
  ## we do this first in case the frame computation takes a long time.
  #wrapper.AddEvent(TICK_INTERVAL, SendDMXFrame)

  # compute frame here  
  # set production to 288 channels per universe. 96 pixels
  # universe1 

  if fbi.pixels is not None:
    data1 = array.array('B')
    data2 = array.array('B')

    for y in range (0,170):
      r,g,b = fbi.pixels[0,y]
      data1.append(r)
      data1.append(g)
      data1.append(b)

    # universe1 
    for y in range (170,199):
      r,g,b = fbi.pixels[0,y]
      data2.append(r)
      data2.append(g)
      data2.append(b)

    print 'Should be sending DMX here:'

    # send
    wrapper.Client().SendDmx(11, data1, DmxSent)
    wrapper.Client().SendDmx(12, data2, DmxSent)

  else:
    print 'Pixels not yet defined'


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


class pyFbi :
  screen = None;

  def __init__(self):
    pygame.init()
    pygame.time.set_timer(USEREVENT + 1, 10000)
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
    #cmd = 'tide -l "Middle Arm, British Columbia" -em pMm -m g -gh 240 -gw 320 -f p > /tmp/pytide.png'
    #os.system( cmd )
    self.previousF = 0
    self.currentF = 0

  def __del__(self):
      "Destructor to make sure pygame shuts down, etc."

  #def getTideData(self):
    # global previousF 
    # global currentF
    # global pixels
    # global tidePixels
    # global xtideImg

    # cmd = 'tide -mr -l "Middle Arm, British Columbia" -s "96:00"'  # arbitrary external command, e.g. "python mytest.py"

    # if previousF == 0.0:
    #   exitcode, out, err = get_exitcode_stdout_stderr(cmd)
    #   tTime, val = out.split()
    #   previousF = float(val)
    #   print "Previous Value: %f" %previousF
    #   #
    #   # Changed to 10 for testing...
    #   #
    #   time.sleep(10)
    #   exitcode, out, err = get_exitcode_stdout_stderr(cmd)
    #   tTime, val = out.split()
    #   currentF = float(val)
    #   print "Current Value: %f" %currentF
    # else:
    #   previousF = currentF
    #   print "Previous Value: %f" %previousF
    #   exitcode, out, err = get_exitcode_stdout_stderr(cmd)
    #   tTime, val = out.split()
    #   currentF = float(val)
    #   print "Current Value: %f" %currentF

    # cmd = 'tide -l "Middle Arm, British Columbia" -em pMm -m g -gh 240 -gw 320 -f p > /tmp/pytide.png'
    # os.system( cmd )
    # self.xtideImg = Image.open("/tmp/pytide.png")

    # img = Image.new("RGB", (1, 200), "black")
    # pixels = img.load()
    # im = numpy.asarray(img)

    # tidePixels = xtideImg.load()

  def tide(self):
    # Load and display tide image

    # self.getTideData()
    cmd = 'tide -mr -l "Middle Arm, British Columbia" -s "96:00"'  # arbitrary external command, e.g. "python mytest.py"

    if self.previousF == 0.0:
      exitcode, out, err = get_exitcode_stdout_stderr(cmd)
      tTime, val = out.split()
      self.previousF = float(val)
      print "Previous Value: %f" % self.previousF
      #
      # Changed to 10 for testing...
      #
      time.sleep(10)
      exitcode, out, err = get_exitcode_stdout_stderr(cmd)
      tTime, val = out.split()
      self.currentF = float(val)
      print "Current Value: %f" % self.currentF
    else:
      self.previousF = self.currentF
      print "Previous Value: %f" % self.previousF
      exitcode, out, err = get_exitcode_stdout_stderr(cmd)
      tTime, val = out.split()
      self.currentF = float(val)
      print "Current Value: %f" % self.currentF

    cmd = 'tide -l "Middle Arm, British Columbia" -em pMm -m g -gh 240 -gw 320 -f p > /tmp/pytide.png'
    os.system( cmd )
    xtideImg = Image.open("/tmp/pytide.png")

    img = Image.new("RGB", (1, 200), "black")
    pixels = img.load()
    im = numpy.asarray(img)

    tidePixels = xtideImg.load()

    #lets work with the numbers a bit and create some variables.
    if self.currentF > self.previousF:
      rising = True

    percentage = self.currentF/5
    goingUp = self.currentF/5*200
    goingDown = 200 - (self.currentF/5*200)

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

    self.pixels = pixels
    SendDMXFrames()

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
    time.sleep(10)

# Create an instance of the PyFbi class
fbi = pyFbi()


class MouseReader():
    def __init__(self, fbi):
        self.fbi = fbi
        self.terminated = False


    def terminate(self):
        self.terminated = True


    def __call__(self):
        while not self.terminated:
            # Look for Mouse events and print them
            for event in pygame.event.get():
                if(event.type is MOUSEBUTTONDOWN):
                    pos = pygame.mouse.get_pos()
                    print pos
            # sleep a bit to not hog CPU
            time.sleep(0.01)

# Start the thread running the callable
mousereader = MouseReader(fbi)
threading.Thread(target=mousereader).start()

def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    mousereader.terminate()
    pygame.display.quit()
    pygame.quit()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

# Start OLA sender
wrapper = ClientWrapper()
#wrapper.AddEvent(TICK_INTERVAL, SendDMXFrames)
#wrapper.Run()

while True:
    #fbi.getTideData()
    fbi.tide()
