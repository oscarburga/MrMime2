import naoqi
import os
import sys

def assert_paths(bPrint):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    imported_naoqi_path = os.path.abspath(naoqi.__file__)
    local_naoqi_path = os.path.join(this_dir, 'pynaoqi', 'lib', 'naoqi.pyc')

    if bPrint:
        print "local naoqi: ", local_naoqi_path
        print "imported naoqi: ", imported_naoqi_path

    assert os.path.isfile(local_naoqi_path)
    assert imported_naoqi_path == local_naoqi_path, imported_naoqi_path + str(' != ')  + local_naoqi_path

# assert_paths(__name__ == '__main__')

# Set NAO host and port
# assert len(sys.argv) == 3, "Should run with 2 params: host and port" 

SOCKET_HOST = "localhost"
SOCKET_PORT = 8083
NAO_HOST = "127.0.0.1"
NAO_PORT = 9559
REPLY_LOCATIONS = False

def set_args():
    global REPLY_LOCATIONS
    args = sys.argv

    if '--reply' in args:
        print('Replying locations')
        REPLY_LOCATIONS = True
        args.remove('--reply')
        
    if len(args) == 3:
        NAO_HOST = str(args[1])
        NAO_PORT = int(args[2])

    elif len(args) == 5:
        SOCKET_HOST = str(args[1])
        SOCKET_PORT = int(args[2])
        NAO_HOST = str(args[3])
        NAO_PORT = int(args[4])
    
set_args()

print 'Working with NAO host =', NAO_HOST, 'and NAO port =', NAO_PORT
print 'Working with SOCKET host =', SOCKET_HOST, 'and SOCKET port =', SOCKET_PORT