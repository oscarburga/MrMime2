from shutil import move
import numpy as np
import sys
import motion
import argparse
import qi
import time

from naoqi import ALProxy

Motion = ALProxy("ALMotion","127.0.0.1",9559)
Spech = ALProxy("ALTextToSpeech","127.0.0.1",9559)
names = ['LElbowRoll', 'LShoulderRoll', 'LShoulderPitch']
times = [[1.0], [1.2], [1.3]]

Motion.wakeUp()
Motion.moveInit()
Motion.post.moveTo(0.5, 0, 0)
Spech.say("Hola a todos!!")
for i in range(3):
    Motion.angleInterpolation(names, [-3.0, 1.2, -0.7], times, True)
    Motion.angleInterpolation(names, [-1.0, 1.2, -0.7], times, True)
Motion.rest()