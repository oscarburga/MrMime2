# MrMime2

MrMime2 is an image-based human-to-robot motion imitation project for the NAO robot. This was an university undergraduate thesis project for my bachelor's degree in Computer Science.

## Brief explanation of how it works
MrMime2 uses [Google's MediaPipe](https://github.com/google/mediapipe) pose estimation solution to perform 3D human pose estimation on image/video/webcam input, 
and then employs analytical geometry methods and calculations to estimate the joint angles from the detected pose 
(all of which is implemented in Python 3).

The estimated joint angles are then sent to the NAO service (implemented in Python2 using the NAO's official 
[NAOqi framework](http://doc.aldebaran.com/2-8/index_dev_guide.html)) through a socket. 

Finally, the NAO service will parse and redirect the joint angle data to the connected NAO robot
(which can be either a real NAO robot or a simulated NAO robot from the [Choregraphe](http://doc.aldebaran.com/2-8/software/choregraphe/index.html) software).

All the software components of MrMime2 are integrated through a simple user interface implemented using [PyQt5](https://pypi.org/project/PyQt5/) for testing and demonstration.
