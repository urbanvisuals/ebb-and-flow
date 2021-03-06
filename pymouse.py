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
#   SEND DMX    #################################################################################
# 

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


#
#   TIDE RUNNER   #################################################################################
# 

def xtideRunner():
  """ xtideRunner runs xtide and generates the output image for pygame to display """
  
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
  if previousF == 0.0
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

previousF = 0.0
currentF  = 0.0

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
pygame.mouse.set_visible(0)
# Clear the screen to start
screen.fill((0, 0, 0))        
# Initialise font support
pygame.font.init()
# loading image
loadImg = pygame.image.load("/home/pi/loading.png")
screen.blit(loadImg, (0, 0))
# Render the screen
pygame.display.update()
#cmd = 'tide -l "Middle Arm, British Columbia" -em pMm -m g -gh 240 -gw 320 -f p > /tmp/pytide.png'
#os.system( cmd )

xtideRunner()
previousF = CurrentF

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


  screen.blit(ebbImg, (0, 0))
  pygame.display.update()

    
  clock.tick(25) 
   
  # check if there is something to do 
  readable, writable, exceptional = select.select([sock], [], [], 0) 
  if readable: 
    # tell it ola_client 
    ola_client.SocketReady() 
