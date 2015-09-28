from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import ListProperty
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.config import Config

from Queue import Queue
import random

import os
import shlex
from subprocess import Popen, PIPE

Config.set('graphics','width', 320)
Config.set('graphics','height', 240)
Window.size = (320, 240)

'''
The following XML looking stuff is Kivy template language. It is pretty straight forward
as far as layout but the data binding is a little strange. Ultimiately this whole
framework was written for touch so there are lots of ways to bind events to these
widgets and as they are declared. I can't stress enough that it is a good idea to spend
some time learnign about Kivy before trying to jump in.

The following template language is usually in its own file but I am just trying to get
the first sample iteration going so am being cheap.
'''
Builder.load_string('''
<Root>:

    search_results: label_1

    Button:
        id: label_1
        text: "Temp"
        background_color: 0,0,0,1
        font_size: 150
        pos: 300, 300

''')

'''
This is the main widget where we are going to be doing most of the things. You will
notice that the there is a Clock object that can schedule asynchronous method
calls which are much better than a sleep (they don't block and return when succesful).
The binding between variables in the asynchronous calls and the UI is not intuitive
but rather simple if you read this book:

The data binding I mention above is explained in detail within the first 30 or 40
pages of that book... well worth spending some time learing this stuff before trying to
jump in and figure it out (trust me - hard won experience with this framework talking).
'''
class Root(Widget):
    random_number = StringProperty()

    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)
        Clock.schedule_interval(self.search_location, 2)

    def search_location(self, *args):
        cmd = 'tide -mr -l "Middle Arm, British Columbia" -s "96:00"'
        exitcode, out, err = get_exitcode_stdout_stderr(cmd)
        tTime, val = out.split()
        currentF = float(val)
        #print err
        print "Current Value: %f" %currentF
        self.search_results.text = str(currentF)

def get_exitcode_stdout_stderr(cmd):
    """
    Execute the external command and get its exitcode, stdout and stderr.
    """
    args = shlex.split(cmd)

    proc = Popen(args, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    exitcode = proc.returncode

    print "Returning from system call..."
    return exitcode, out, err

runTouchApp(Root())
