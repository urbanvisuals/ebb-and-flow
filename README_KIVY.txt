Install Kivy (assuming fresh Rasbian install)
----------------------------------------------------
sudo apt-get clean
sudo apt-get update
sudo apt-get upgrade

* when finished restart

sudo reboot

sudo apt-get install python-setuptools python-pygame python-opengl python-gst0.10 python-enchant gstreamer0.10-plugins-good python-dev build-essential libgl1-mesa-dev libgles2-mesa-dev python-pip

* if this single command above fails to run through then break the command up into
individual commands and run them one at a time.

* if the above fails you may have to run this: install libwayland0=0.85.0-2

* probably not a bad time to reboot

sudo reboot

sudo pip install --upgrade cython

* if you made it this far you are ready to install Kivy

git clone git://github.com/kivy/kivy.git

* compile that mofo... this will take a long time - not a bad thing to kick off
before you go to bed (just dont sit around and wait for it to finish and you will be fine)

python setup.py build_ext --inplace -f
sudo python setup.py install

* If you make it through all of that without anything blowing up you can
try running some of the examples.

cd ~/kivy/examples/3Drendering
python main.py

* if everything is working you should see a 3D animation on the screen of the
device that is hosting the code (assuming it has a display attached).

Once you see one of the Kivy examples running, and assuming you have XTide & the OLA
code installed, you are good to go.

************** PiTFT *********************
The following are some extra instructions that I had to implement to get the
the 2.8" PiTFT touchscreen working from AdaFruit
********************************************

sudo apt-get install cmake

* cd into the directory then create a directory called build
* cd into build and run:

cmake ..

make

* After this I followed some more of the Adafruit instructions when I realized that
I did not have the screen installed correctly yet

sudo nano /etc/udev/rules.d/95-stmpe.rules

* and then added the following:

SUBSYSTEM=="input", ATTRS{name}=="stmpe-ts", ENV{DEVNAME}=="*event*", SYMLINK+="input/touchscreen"

sudo rmmod stmpe_ts; sudo modprobe stmpe_ts

* then type: ls -l /dev/input/touchscreen

 sudo apt-get install evtest tslib libts-bin

 * Now lets run a test:

 sudo evtest /dev/input/touchscreen

 * sweet... lets calibrate

 sudo adafruit-pitft-touch-cal

 *** Other Stuff

  sudo nano /boot/cmdline.txt

* At the end of the line, find the text that says rootwait and right after that, enter in:
fbcon=map:10 fbcon=font:VGA8x8 then save the file.

https://learn.adafruit.com/adafruit-pitft-28-inch-resistive-touchscreen-display-raspberry-pi/using-the-console
https://learn.adafruit.com/adafruit-pitft-28-inch-resistive-touchscreen-display-raspberry-pi/playing-videos

GAH! It is getting late but I finally got this working... do plan to clean this up BUT
this git repo's section on framebuffer mirroring is what finally got me going:

https://github.com/notro/fbtft/wiki/Framebuffer-use

************** MAC OSX *********************
The following are some extra instructions that I had to implement to get the
simple_kivy.py running on my laptop.
********************************************

* To get xTide running on my Mac I had to install MacPorts (or at least this seemed
to be the easiest way to get it onto my machine): https://www.macports.org/install.php

Once I ran the installation package I had to restart the terminal to see xtide.

Once that package was installed I had to run: sudo port install xtide

Realized I did not have the harmonics file where it supposed to be so installed it on
OSX at the following: /opt/local/share/xtide/harmonics

** I still need to go run whatever command I remember nathan posted to get rid of the
info notification from xtide...

*********************************************
OTHER stuff
*********************************************

* In order to start the desktop on the little touch screen I used this command:
