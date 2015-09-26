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
import subprocess as sp
import cv2
import cv2.cv as cv


from os.path import exists
from PIL import Image

import shlex
#from subprocess import Popen, PIPE

TICK_INTERVAL = 100  # in ms


os.environ["SDL_FBDEV"] = "/dev/fb1"
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
os.environ["SDL_MOUSEDRV"] = "TSLIB"
#os.putenv('SDL_NOMOUSE', '1')

global totalFrames
global count

bgBrightnessB = 128
bgBrightnessG = 128
whiteBrightness = 255

rising = True

pixels = None

wrapper = None

gammaLUT = array.array('B')

gammaLUT = [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
  1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
  2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
  5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
  10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
  17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
  25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
  37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
  51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
  69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
  90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
  115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
  144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
  177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
  215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255]

def gamma(input):
  return gammaLUT[input]


#
#  SEND DMX to OLA here
#
def DmxSent(state):
  if not state.Succeeded():
    wrapper.Stop()

def SendDMXFrames(pixels):
  ## schdule a function call in 100ms
  ## we do this first in case the frame computation takes a long time.
  #wrapper.AddEvent(TICK_INTERVAL, SendDMXFrame)

  # compute frame here  
  # set production to 288 channels per universe. 96 pixels
  # universe1 

  if pixels is not None:
    data1 = array.array('B')
    data2 = array.array('B')

    for x in range (0,72):
      r,g,b = pixels[x,0]
      data1.append(r)
      data1.append(g)
      data1.append(b)

    #print 'Should be sending DMX here:'

    # send
    wrapper.Client().SendDmx(11, data1, DmxSent)
    #wrapper.Client().SendDmx(12, data2, DmxSent)

  else:
    print 'Pixels not yet defined'


def get_exitcode_stdout_stderr(cmd):
    """
    Execute the external command and get its exitcode, stdout and stderr.
    """
    args = shlex.split(cmd)

    proc = Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
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
    #loadImg = pygame.image.load("/home/pi/loading.png")
    #self.screen.blit(loadImg, (0, 0))
    # Render the screen
    pygame.display.update()

    # self.stream= cv2.VideoCapture('bigbuckbunny320p.mp4')
    # print self.stream.get(cv.CV_CAP_PROP_FRAME_HEIGHT)
    # print self.stream.get(cv.CV_CAP_PROP_FRAME_COUNT)
    # self.totalFrames = self.stream.get(cv.CAP_PROP_FRAME_COUNT)
    # print self.totalFrames
    self.count = 1
    self.mouse = False

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
    # cmd = 'tide -mr -l "Middle Arm, British Columbia" -s "96:00"'  # arbitrary external command, e.g. "python mytest.py"

    # if self.previousF == 0.0:
    #   exitcode, out, err = get_exitcode_stdout_stderr(cmd)
    #   tTime, val = out.split()
    #   self.previousF = float(val)
    #   print "Previous Value: %f" % self.previousF
    #   #
    #   # Changed to 10 for testing...
    #   #
    #   time.sleep(10)
    #   exitcode, out, err = get_exitcode_stdout_stderr(cmd)
    #   tTime, val = out.split()
    #   currentF = float(val)
    #   print "Current Value: %f" % currentF
    # else:
    #   self.previousF = currentF
    #   print "Previous Value: %f" % self.previousF
    #   exitcode, out, err = get_exitcode_stdout_stderr(cmd)
    #   tTime, val = out.split()
    #   currentF = float(val)
    #   print "Current Value: %f" % currentF

    # cmd = 'tide -l "Middle Arm, British Columbia" -em pMm -m g -gh 240 -gw 320 -f p > /tmp/pytide.png'
    # os.system( cmd )
    # xtideImg = Image.open("/tmp/pytide.png")

    # img = Image.new("RGB", (1, 200), "black")
    # pixels = img.load()
    # im = numpy.asarray(img)

    # tidePixels = xtideImg.load()

    # #lets work with the numbers a bit and create some variables.
    # if currentF > self.previousF:
    #   rising = True

    # percentage = currentF/5
    # goingUp = currentF/5*200
    # goingDown = 200 - (currentF/5*200)

    # print goingUp
    # print goingDown

    # #print im

    # # colour background
    # for y in range (0, 200):
    #   pixels[0, y] = (0, int(bgBrightnessG*percentage), int(bgBrightnessB)) # green varies with depth full blue

    # # colour indicator
    # # start from the top, as our image starts there.
    # # 
    # # This makes the image upside down!
    # #
    # #
    # # split tide into whole numbers and decimals on a range of 0 to 200
    # # the decimal will allow us to fade up the incoming pixel so it doesn't jump.
    # upDec, upInt = math.modf(goingUp)
    # downDec, downInt = math.modf(goingDown)


    # # current indicator is 7 pixels tall. May need to reduce that when we add the fade out tail.
    # pixels[0,upInt] = (int(whiteBrightness),int(whiteBrightness),int(whiteBrightness))
    # pixels[0,upInt-1] = (int(whiteBrightness),int(whiteBrightness),int(whiteBrightness))
    # pixels[0,upInt-2] = (int(whiteBrightness),int(whiteBrightness),int(whiteBrightness))
    # pixels[0,upInt+1] = (int(whiteBrightness),int(whiteBrightness),int(whiteBrightness))
    # pixels[0,upInt+2] = (int(whiteBrightness),int(whiteBrightness),int(whiteBrightness))

    # #draw leading edge fade
    # r, g, b = pixels[0,upInt+3] 
    # r = int(max(whiteBrightness*upDec , r))
    # g = int(max(whiteBrightness*upDec , g))
    # b = int(max(whiteBrightness*upDec , b))
    # pixels[0,upInt+3] = r,g,b
    # #draw trailing edge fade
    # r, g, b = pixels[0,upInt-3] 
    # r = int(max(whiteBrightness*downDec , r))
    # g = int(max(whiteBrightness*downDec , g))
    # b = int(max(whiteBrightness*downDec , b))
    # pixels[0,upInt-3] = r,g,b

    # #
    # #  Still need to draw the tail to indicate tide direction. We may also 
    # #

    # self.pixels = pixels
    # SendDMXFrames()

    # # colour background
    # for x in range (291,320):
    #   for y in range (0, 240):
    #     tidePixels[x, y] = (0, 0, 0) # black background.



    # # colour lighting pattern
    # for x in range (301,315):
    #   for y in range (0, 200):
    #     tidePixels[x, y+33] = pixels[0, 199-y] # add tide pattern NOTE that 

    # # convert PIL image to pygame image and output it to framebuffer.
    # mode = xtideImg.mode
    # size = xtideImg.size
    # data = xtideImg.tostring()

    # read 320*240*3 bytes (= 1 frame)
    # transform the byte read into a numpy array

    c = self.count
    c = c + 1

    if c == stream.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT):
        c = 0 #Or whatever as long as it is the same as next line
        stream.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, 0)
        print "loop"

    if stream.isOpened():
      rval, frame = stream.read()
      #print "frame: ", c
      #cv2.imwrite(str(c) + '.jpg',frame)
      self.count = c

      cv2.waitKey(10)

      # mode = 'RGB'
      # size = (320,180)
      # data = Img.tostring()
      # print data.len()
      if rval:
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if fbi.mouse:
          swellImg = pygame.image.frombuffer(frame.tostring(), frame.shape[1::-1], "RGB")
        else:
          swellImg = pygame.image.frombuffer(frameRGB.tostring(), frameRGB.shape[1::-1], "RGB")

        fbi.screen.blit(swellImg, (0, 0))
        pygame.display.update()
        time.sleep(.0022)

      img = Image.new("RGB", (72, 1), "black")
      pixels = img.load()
      #
      # CALCULATE AND SEND HERE
      # SEND DATA TO DMX HERE
      #
      for x in range (0,72):
        # looks like open cv images are BRG and Y,X by default 
        pixels[x,0] = gamma(frameRGB[80,x+124,0]),gamma(frameRGB[80,x+124,1]),gamma(frameRGB[80,x+124,2])
        #print pixels[x,0]

      SendDMXFrames(pixels)
      #
      # SEND DATA TO DMX HERE
      #
    #lets wait for a bit    
    #time.sleep(10)

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
                    if fbi is not None:
                      print fbi.mouse
                      fbi.mouse = not fbi.mouse
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

stream= cv2.VideoCapture('bigbuckbunny320p.mp4')
print stream.get(cv.CV_CAP_PROP_FRAME_HEIGHT)
print "format"
print stream.get(cv.CV_CAP_PROP_FORMAT)
print stream.get(cv.CV_CAP_PROP_FPS)
print stream.get(cv.CV_CAP_PROP_FRAME_COUNT)

frames = stream.get(cv.CV_CAP_PROP_FRAME_COUNT)
totalFrames = stream.get(cv.CV_CAP_PROP_FRAME_COUNT)
count=0


# Start OLA sender
wrapper = ClientWrapper()
#wrapper.AddEvent(TICK_INTERVAL, SendDMXFrames)
#wrapper.Run()

while True:
    #fbi.getTideData()
    fbi.tide()
