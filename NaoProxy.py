import subprocess
import socket
import json
import time
import threading
from ProcessMpPose import *
from AsyncWorkerBase import *
time.time()


class NaoSocketWorker(AsyncWorkerBase):
    on_connected_status_updated = pyqtSignal(bool)

    def __init__(self, proxy_host, proxy_port):
        super().__init__()
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.socket = None
        self.trying_to_connect = False
        self.connected_to_service = False

    @pyqtSlot(dict)
    def send_pose_data(self, dic):
        if self.socket:
            msg = json.dumps(dic).encode('ascii')
            self.send_raw(msg)
        else:
            log_safe('NaoSocketWorker: No socket.')

    @pyqtSlot()
    def on_thread_start(self):
        self.try_connect_to_service()

    @pyqtSlot()
    def on_thread_end(self):
        log_safe('socket worker on_thread_end')
        self.close()
        super().on_thread_end()

    def close(self):
        if self.socket:
            try:
                self.send_raw('!')
            except Exception as e:
                pass
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            except Exception as e:
                pass
            self.socket = None

    def try_connect_to_service(self):
        self.close()
        self.trying_to_connect = True
        start_time = time.time()
        while self.trying_to_connect and time.time() - start_time < 5.0:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.proxy_host, self.proxy_port))
                self.socket = sock
                log_safe(f'Connected to socket')
                self.connected_to_service = True
                # wait for confirmation:
                self.socket.settimeout(5.0)
                service_confirm_msg = self.socket.recv(1024)
                if len(service_confirm_msg) > 0:
                    decoded = service_confirm_msg.decode('utf-8')
                    self.trying_to_connect = False
                    if decoded != 'k':
                        log_safe(f'Connected to service but not to robot.')
                    self.on_connected_status_updated.emit(decoded == 'k')
                    return
            except Exception as e:
                self.socket = None
        log_safe(f'Failed to connect to service.')
        self.trying_to_connect = False
        self.on_connected_status_updated.emit(False)

    def send_raw(self, msg):
        total_sent = 0
        while total_sent < len(msg):
            sent = self.socket.send(msg[total_sent:])
            if sent == 0:
                log_safe('connection broken')
                break
            total_sent += sent


class NaoProxy(QObject):
    on_pose_available = pyqtSignal(dict)

    def __init__(self, parent=None,
                 proxy_host='localhost',
                 proxy_port=8083,
                 nao_host='127.0.0.1',
                 nao_port=9559,
                 connection_status_slot=None,
                 poseProcessorClass=MpPoseProcessorMath3D):
        super().__init__(parent)

        cmd = f'ServiceBuild/Main.exe {proxy_host} {proxy_port} {nao_host} {nao_port}'
        cmd_list = cmd.split(' ')
        self.naoServiceProcess = None

        try:
            log_safe(f'trying Popen nao service')
            startupInfo = subprocess.STARTUPINFO()
            startupInfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.naoServiceProcess = subprocess.Popen(cmd_list,
                                                      stdout=subprocess.PIPE,
                                                      stderr=subprocess.PIPE,
                                                      startupinfo=startupInfo
                                                      )

            def read_from_service(proc):
                for line in iter(proc.stdout.readline, b''):
                    log_safe('NaoService: ', line.decode('utf-8'), end='')

            # Spawn a simple async thread to just spam log output from the service
            self.serviceReader = threading.Thread(target=read_from_service,
                                                  args=(self.naoServiceProcess,))
            self.serviceReader.start()
            log_safe(f'Popen nao service and reader ok')
            pass
        except Exception as e:
            log_safe(f'Failed to Popen: {e}')

        self.naoSocketWorker = NaoSocketWorker(proxy_host, proxy_port)
        self.socketThread = self.naoSocketWorker.setup_on_thread()
        self.on_pose_available.connect(self.naoSocketWorker.send_pose_data)
        if connection_status_slot:
            self.naoSocketWorker.on_connected_status_updated.connect(connection_status_slot)

        self.poseProcessor = poseProcessorClass()
        log_safe('starting naoService socket thread')
        self.socketThread.start()

    def close(self):
        if self.socketThread:
            self.socketThread.quit()
            self.socketThread.wait()
            self.socketThread = None
            log_safe('killed nao socket thread')
        if self.naoServiceProcess:
            if self.naoServiceProcess.poll() is None:
                self.naoServiceProcess.terminate()
                log_safe('killed nao service process')
            self.naoServiceProcess = None

    def __del__(self):
        self.close()
    
    def process_landmark_list(self, landmarks: list):
        if len(landmarks):
            pose_dict = self.poseProcessor.get_pose_dict(landmarks)
            self.on_pose_available.emit(pose_dict)
