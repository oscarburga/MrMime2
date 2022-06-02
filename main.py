from naoqi import ALProxy

NAO_HOST = "127.0.0.1"
NAO_PORT = 9559

Motion = ALProxy("ALMotion", NAO_HOST, NAO_PORT)
Speech = ALProxy("ALTextToSpeech", NAO_HOST, NAO_PORT)

names = ['LElbowRoll', 'LShoulderRoll', 'LShoulderPitch']
times = [[1.0], [1.2], [1.3]]

Motion.wakeUp()
Motion.moveInit()
Motion.post.moveTo(0.5, 0, 0)
Speech.say("Hola a todos!!")
for i in range(3):
    Motion.angleInterpolation(names, [-3.0, 1.2, -0.7], times, True)
    Motion.angleInterpolation(names, [-1.0, 1.2, -0.7], times, True)
Motion.rest()