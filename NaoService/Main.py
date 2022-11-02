from SetAndTestRuntimeEnv import *
import socket
from naoqi import ALProxy
import json
from JsonSocket import *

global Motion, stop_loop
Motion = None
stop_loop = False

if __name__ == '__main__':

    def try_get_motion():
        global Motion, stop_loop
        if Motion:
            try:
                Motion.ping()
                return Motion
            except Exception as e:
                print 'Existing Motion proxy failed. Creating new one...'

        try:
            Motion = ALProxy("ALMotion", NAO_HOST, NAO_PORT)
            Motion.ping()
            return Motion
        except Exception as e:
            print 'NC: Cannot obtain connection to Motion ALProxy.'
            return None

    def process_list_of_joint_dicts(object_list, jsonSocket):
        global Motion, stop_loop
        for dic in reversed(object_list):
            if type(dic) == dict:
                names = [name.encode('ascii', 'ignore') for name in dic.keys()]
                m = try_get_motion()
                if not m:
                    stop_loop = True
                    jsonSocket.shouldStop = True
                m.setAngles(names, dic.values(), 1)
                break
    

    while not stop_loop:
        socket = None
        socket = JsonSocket(process_list_of_joint_dicts, host=SOCKET_HOST, port=SOCKET_PORT)
        try:
            socket.accept_wait()
            m = try_get_motion()
            if not m:
                socket.send_to_client('!')
                break
            socket.send_to_client('k')
            m.wakeUp()
            if socket.loop():
                m = try_get_motion()
                if m:
                    m.rest()
                break
        except Exception as e:
            print 'Socket loop ended.\n\tException:', e
    
    print 'Exiting...'


# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.bind(('localhost', 8080))
# server.listen(5)
# 
# 
# 
# print 'Waiting for accept'
# clientsocket, address = server.accept()
# print 'Accepted', address
# msg = ''
# while True:
#     raw = clientsocket.recv(1024*8)
#     if len(raw) == 0:
#         continue
#     dic = json.loads(raw)
#     print '--------'
#     names = dic.keys()
#     names = [name.encode('ascii', 'ignore') for name in names]
#     angles = dic.values()
#     print names
#     print angles
#     print ''
#     Motion.setAngles(names, angles, 1.0)
# 
# Motion.rest()