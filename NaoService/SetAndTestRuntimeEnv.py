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

if len(sys.argv) == 3:
    NAO_HOST = str(sys.argv[1])
    NAO_PORT = int(sys.argv[2])

elif len(sys.argv) == 5:
    SOCKET_HOST = str(sys.argv[1])
    SOCKET_PORT = int(sys.argv[2])
    NAO_HOST = str(sys.argv[3])
    NAO_PORT = int(sys.argv[4])

print 'Working with NAO host =', NAO_HOST, 'and NAO port =', NAO_PORT
print 'Working with SOCKET host =', SOCKET_HOST, 'and SOCKET port =', SOCKET_PORT