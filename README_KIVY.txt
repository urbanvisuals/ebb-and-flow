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

* To get xTide running on my Mac I had to install MacPorts (or at least this seemed
to be the easiest way to get it onto my machine): https://www.macports.org/install.php

Once that package was installed I had to run:
