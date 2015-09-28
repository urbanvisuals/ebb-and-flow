import os
import pygame
from pygame.locals import *
#import time
#import random
#import numpy
import math
#import signal
#import threading
import array
from ola import OlaClient 
#import subprocess as sp
import cv2
import cv2.cv as cv
import select 
from os.path import exists
from PIL import Image

import shlex
#from subprocess import Popen, PIPE


#
#   FUNCTIONS   #################################################################################
# 

#
#   SEND DMX    #################################
# 

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

    # send
    ola_client.SendDmx(11, data1, DmxSent)

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


def gamma(input):
  return gammaLUT[input]

#
#   VARS   #################################################################################
# 

os.environ["SDL_FBDEV"] = "/dev/fb1"
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
os.environ["SDL_MOUSEDRV"] = "TSLIB"
#os.putenv('SDL_NOMOUSE', '1')

pixels = None

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
DMX_RECEIVE_EVENT = pygame.USEREVENT + 1 
SEND_DMX_EVENT_TIMER = pygame.USEREVENT + 2 

#init
pygame.init()
pygame.display.init()
size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
print "Framebuffer size: %d x %d" % (size[0], size[1])
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
print "init clock"
clock = pygame.time.Clock() 
# set a timer to send dmx. 
print "timer"
pygame.time.set_timer(SEND_DMX_EVENT_TIMER, 40) 
# Hide the mouse
pygame.mouse.set_visible(0)
# Clear the screen to start
screen.fill((0, 0, 0))        
# Initialise font support
pygame.font.init()
# loading image
# loadImg = pygame.image.load("/home/pi/loading.png")
# self.screen.blit(loadImg, (0, 0))
# Render the screen
pygame.display.update()
# self.stream= cv2.VideoCapture('bigbuckbunny320p.mp4')
# print self.stream.get(cv.CV_CAP_PROP_FRAME_HEIGHT)
# print self.stream.get(cv.CV_CAP_PROP_FRAME_COUNT)
# self.totalFrames = self.stream.get(cv.CAP_PROP_FRAME_COUNT)
# print self.totalFrames

# Load video file and print some info about it

stream= cv2.VideoCapture('waves.mp4')
print stream.get(cv.CV_CAP_PROP_FRAME_HEIGHT)
print "format"
print stream.get(cv.CV_CAP_PROP_FORMAT)
print stream.get(cv.CV_CAP_PROP_FPS)
print stream.get(cv.CV_CAP_PROP_FRAME_COUNT)

frames = stream.get(cv.CV_CAP_PROP_FRAME_COUNT)
totalFrames = stream.get(cv.CV_CAP_PROP_FRAME_COUNT)
count=0

# load screen title graphic
swellTitle = Image.open("swellTitle.png")

count = 1
mouseBool = False

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
    if event.type == MOUSEBUTTONDOWN:
      print mouseBool
      mouseBool = not mouseBool

  count = count + 1

  if count == stream.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT):
    count = 0 #Or whatever as long as it is the same as next line
    stream.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, 0)
    print "looping video file"

  if stream.isOpened():
    rval, frame = stream.read()
    #cv2.imwrite(str(c) + '.jpg',frame)

    cv2.waitKey(10)
    img = Image.new("RGB", (72, 1), "black")
    pixels = img.load()
    # mode = 'RGB'
    # size = (320,180)
    # data = Img.tostring()
    # print data.len()
    if rval:
      frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      if mouseBool:
        swellImg = pygame.image.frombuffer(frame.tostring(), frame.shape[1::-1], "RGB")
        for x in range (0,72):
          pixels[x,0] = gamma(frame[80,x+124,0]),gamma(frame[80,x+124,1]),gamma(frame[80,x+124,2])
      else:
        swellImg = pygame.image.frombuffer(frameRGB.tostring(), frameRGB.shape[1::-1], "RGB")
        for x in range (0,72):
          pixels[x,0] = gamma(frameRGB[80,x+124,0]),gamma(frameRGB[80,x+124,1]),gamma(frameRGB[80,x+124,2])
      screen.blit(swellImg, (0, 0))
      
      mode = swellTitle.mode
      size = swellTitle.size
      data = swellTitle.tostring()
      TitleImg = pygame.image.fromstring(data, size, mode)
      screen.blit(TitleImg, (0, 180))
      pygame.display.update()
      # 25 fps 
      clock.tick(25) 
       
      # check if there is something to do 
      readable, writable, exceptional = select.select([sock], [], [], 0) 
      if readable: 
        # tell it ola_client 
        ola_client.SocketReady() 
