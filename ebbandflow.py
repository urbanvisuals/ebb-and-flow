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
from ola import OlaClient 
import select 


from os.path import exists
from PIL import Image

import shlex
from subprocess import Popen, PIPE

#
#   FUNCTIONS   #################################################################################
# 

#
#   SEND DMX    #################################
# 

def SendDMXFrames(pixels):

  # set production to 288 channels per universe. 96 pixels

  if pixels is not None:
    data1 = array.array('B')
    data2 = array.array('B')

    # universe 1
    for y in range (0,170):
      r,g,b = pixels[0,y]
      data1.append(r)
      data1.append(g)
      data1.append(b)

    # universe 2
    for y in range (170,199):
      r,g,b = pixels[0,y]
      data2.append(r)
      data2.append(g)
      data2.append(b)

    # print 'Should be sending DMX here:'

    # send
    ola_client.SendDmx(11, data1)
    ola_client.SendDmx(12, data2)


  else:
    print 'pixels not yet defined'


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


#
#   TIDE RUNNER   ################################
# 

def xtideRunner():
  """ xtideRunner runs xtide and generates the output image for pygame to display """
  
  global currentF
  global previousF
  global rising
  global pixels
  global ebbImg

  # get current tide value
  cmd = 'tide -mr -l "Middle Arm, British Columbia" -s "96:00"'  # arbitrary external command, e.g. "python mytest.py"
  previousF = currentF
  exitcode, out, err = get_exitcode_stdout_stderr(cmd)
  tTime, val = out.split()
  currentF = float(val)
  print "Current Value: %f" % currentF

  # Let's equalize the two values if previousF is still 0
  # 10 seconds later we'll get a true previous value
  #
  if previousF == 0.0:
    previousF = currentF
  print "Previous Value: %f" % previousF

  #lets work with the numbers a bit and create some variables.
  if currentF > previousF:
    rising = True

  percentage = currentF/5
  goingUp = currentF/5*200
  goingDown = 200 - (currentF/5*200)

  print goingUp
  print goingDown

  # get current tide image and load into an array
  cmd = 'tide -l "Middle Arm, British Columbia" -em pMm -m g -gh 240 -gw 320 -f p > /tmp/pytide.png'
  os.system( cmd )
  xtideImg = Image.open("/tmp/pytide.png")
  tidePixels = xtideImg.load()

  # generate 200 pixel image and create an array
  img = Image.new("RGB", (1, 200), "black")
  pixels = img.load()
  im = numpy.asarray(img)

  # colour background
  for y in range (0, 200):
    pixels[0, y] = (0, int(bgBrightnessG*percentage), int(155-(bgBrightnessB*percentage))) # green varies with depth full blue

  # colour indicator
  # start from the top, as our image starts there.
  # 
  # This makes the image upside down!
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
  ebbImg = pygame.image.fromstring(data, size, mode)


#
#   VARS   #################################################################################
# 

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
ebbImg = None

mouseBool = False

previousF = 0.0
currentF = 0.0

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



#
#   INIT   #################################################################################
# 

# Start OLA sender
# let OlaClient create the socket itself 
ola_client = OlaClient.OlaClient() 
sock = ola_client.GetSocket() 

# defining custom events for pygame 
XTIDE_TIMER = pygame.USEREVENT + 1 
SEND_DMX_EVENT_TIMER = pygame.USEREVENT + 2 

pygame.init()
pygame.time.set_timer(USEREVENT + 1, 10000)
pygame.display.init()
size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
print "Framebuffer size: %d x %d" % (size[0], size[1])
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
print "init clock"
clock = pygame.time.Clock() 
# set a timer to send dmx. 
print "timers"
pygame.time.set_timer(SEND_DMX_EVENT_TIMER, 40) 
pygame.time.set_timer(XTIDE_TIMER, 10000) 
# Hide the mouse
pygame.mouse.set_visible(1)
# Clear the screen to start
screen.fill((0, 0, 0))        
# Initialise font support
pygame.font.init()
# loading image
ebbImg = pygame.image.load("/home/pi/loading.png")
screen.blit(ebbImg, (0, 0))
# Render the screen
pygame.display.update()
#cmd = 'tide -l "Middle Arm, British Columbia" -em pMm -m g -gh 240 -gw 320 -f p > /tmp/pytide.png'
#os.system( cmd )

# run xtide once to get current values
xtideRunner() 
previousF = currentF

#
#   LOOP   #################################################################################
#

while True:
  # print "loop started"
  # check for pygame events 
  for event in pygame.event.get(): 
    if event.type == pygame.QUIT: 
      pygame.display.quit()
      pygame.quit()
      sys.exit()     
    if event.type == QUIT: 
      pygame.display.quit()
      pygame.quit()
      sys.exit() 
    if event.type == KEYDOWN and e.key == K_ESCAPE:
      pygame.display.quit()
      pygame.quit()
      sys.exit() 

    # send dmx timer reached 
    if event.type == SEND_DMX_EVENT_TIMER: 
      SendDMXFrames(pixels)
    if event.type == XTIDE_TIMER: 
      xtideRunner()
    if event.type == MOUSEBUTTONDOWN:
      print mouseBool
      mouseBool = not mouseBool

  if mouseBool:
    # put code here to display the current time and display it onscreen
   screen.fill((255,255,255))
   screen.blit(ebbImg, (0,0), None, BLEND_RGB_SUB)
    #
  else:
    screen.blit(ebbImg, (0, 0))

  #update the display  
  pygame.display.update()

  
  clock.tick(25) 
   
  # check if there is something to do 
  readable, writable, exceptional = select.select([sock], [], [], 0) 
  if readable: 
    # tell it ola_client 
    ola_client.SocketReady() 
