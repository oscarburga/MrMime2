import sys

from PyQt5.QtWidgets import *
from AsyncMediaThreadQObjects import *
from NaoProxy import *

CONN_IMG_PATHS = ['not_connected.jpg', 'connected.jpg']
CONN_TEXTS = ['Not connected', 'Connected', 'Attempting to connect...']
CONN_STATUS_NC = 0
CONN_STATUS_OK = 1
CONN_STATUS_WIP = 2

class GUI(QMainWindow):
    toggle_hpe_signal = pyqtSignal(bool)
    toggle_play_state = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MrMime2")
        self.setGeometry(60, 60, 960, 540)
        self.setFixedSize(960, 540)
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)
        self.design = QGridLayout()

        current_row = 0
        # Use webcam
        ## Open webcam button
        self.useWebCam = QPushButton("Use WebCam")
        self.useWebCam.clicked.connect(self.open_web_cam)
        self.design.addWidget(self.useWebCam, current_row, 0, 1, 0)

        current_row += 1
        # Use image
        ## Open image button
        self.useImage = QPushButton("Use Image")
        self.useImage.clicked.connect(self.open_image)
        self.design.addWidget(self.useImage, current_row, 0, 1, 0)

        current_row += 1
        # Use video
        ## Open video button
        self.useVideo = QPushButton("Use Video")
        self.useVideo.clicked.connect(self.open_video)
        self.design.addWidget(self.useVideo, current_row, 0, 1, 0)

        current_row += 1

        self.videoButtonLayout = QGridLayout()
        # Play video button
        self.playButton = QPushButton()
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play_pressed)
        self.playButton.setEnabled(False)
        self.videoButtonLayout.addWidget(self.playButton, 0, 0)

        # Stop video button
        self.stopButton = QPushButton()
        self.stopButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stopButton.clicked.connect(self.stop_pressed)
        self.stopButton.setEnabled(False)
        self.videoButtonLayout.addWidget(self.stopButton, 0, 1)

        self.design.addLayout(self.videoButtonLayout, current_row, 0)

        current_row += 1
        # NAO Layout
        self.naoLayout = QGridLayout()
        ## Title
        self.title = QLabel()
        self.title.setFont(QFont('Arial', 25, QFont.Bold))
        self.title.setStyleSheet("color : black; ")
        self.title.setText("NAO Settings")
        self.naoLayout.addWidget(self.title, 0, 0)
        ##  Hostname label
        self.hostname_label = QLabel()
        self.hostname_label.setFont(QFont('Arial', 15, QFont.Bold))
        self.hostname_label.setStyleSheet("color : black; ")
        self.hostname_label.setText("Hostname")
        self.naoLayout.addWidget(self.hostname_label, 1, 0)
        ##  Hostname input
        self.hostname_input = QLineEdit()
        self.hostname_input.setText('127.0.0.1')
        self.naoLayout.addWidget(self.hostname_input, 1, 1)
        ##  Port label
        self.port_label = QLabel()
        self.port_label.setFont(QFont('Arial', 15, QFont.Bold))
        self.port_label.setStyleSheet("color : black; ")
        self.port_label.setText("Port")
        self.naoLayout.addWidget(self.port_label, 2, 0)
        ##  Port input
        self.port_input = QLineEdit()
        self.port_input.setText('9559')
        self.naoLayout.addWidget(self.port_input, 2, 1)
        ## Connect button
        self.connect = QPushButton("Connect")
        self.connect.clicked.connect(self.update_connection)
        self.naoLayout.addWidget(self.connect, 3, 0, 1, 0)
        ## Connection state
        self.connection_status = CONN_STATUS_NC
        self.connection = QLabel()
        self.connection.setPixmap(QPixmap(CONN_IMG_PATHS[0]).scaled(50, 50, Qt.KeepAspectRatio))
        self.naoLayout.addWidget(self.connection, 4, 0)
        self.connection_text = QLabel()
        self.connection_text.setFont(QFont('Arial', 15, QFont.Bold))
        self.connection_text.setStyleSheet("color : black; ")
        self.connection_text.setText(CONN_TEXTS[0])
        self.naoLayout.addWidget(self.connection_text, 4, 1)
        ## Activar HPE
        self.hpeOn = False
        self.hpe_text = ["Activar HPE", "Desactivar HPE"]
        self.hpe_button = QPushButton("Activar HPE")
        self.hpe_button.clicked.connect(self.update_hpe)
        self.naoLayout.addWidget(self.hpe_button, 5, 0, 1, 0)

        # Details
        self.feed = QLabel()
        self.feedWidgetLoc = (current_row, 0)
        self.design.addWidget(self.feed, current_row, 0)
        self.design.setColumnStretch(0, 2)
        self.design.setColumnStretch(1, 1)
        self.design.addLayout(self.naoLayout, current_row, 1)
        self.widget.setLayout(self.design)

        # Tools
        self.naoProxy = None
        self.mediaThread = None
        self.hpeWorker = None

    @pyqtSlot(bool)
    def on_connection_status_updated(self, new_status):
        new_status = int(new_status)
        self.connection.setPixmap(QPixmap(CONN_IMG_PATHS[new_status]).scaled(50, 50, Qt.KeepAspectRatio))
        self.connection.show()
        self.connection_text.setText(CONN_TEXTS[new_status])

    def update_connection(self):
        if not self.naoProxy:
            self.connection_status = CONN_STATUS_NC
            self.connection.hide()
            try:
                host, port = self.hostname_input.text(), self.port_input.text()
                port = int(port)
                log_safe(f'Creating nao proxy with host={host}, port={port}')
                self.naoProxy = NaoProxy(parent=self,
                                         nao_host=host,
                                         nao_port=port,
                                         connection_status_slot=self.on_connection_status_updated,
                                         poseProcessorClass=MpPoseProcessorMath3D)
                self.connection_text.setText(CONN_TEXTS[CONN_STATUS_WIP])
            except Exception as e:
                log_safe(f'Failed to create NAO Proxy: {e}')

    def set_video_buttons_enabled(self, enabled: bool):
        for btn in [self.playButton, self.stopButton]:
            if btn:
                btn.setEnabled(enabled)
                if enabled:
                    btn.show()
                else:
                    btn.hide()

    def remove_widget(self):
        if self.feed:
            self.design.removeWidget(self.feed)
        self.set_video_buttons_enabled(False)

    @pyqtSlot(QImage, list, object)
    def image_update_slot(self, image: QImage, landmarks, raw):
        if self.feed and image:
            self.feed.setPixmap(QPixmap.fromImage(image))
            if self.feed.isHidden():
                self.feed.show()
        if len(landmarks) and self.naoProxy:
            self.naoProxy.process_landmark_list(landmarks)

    def create_hpe_worker(self, worker_class, path=''):
        if self.mediaThread:
            qDebug('quitting media thread')
            self.mediaThread.quit()
            self.mediaThread.wait()

        self.hpeWorker = None
        # Set to true so update_hpe sets it back to False
        self.hpeOn = True
        self.update_hpe()
        self.mediaThread = QThread()
        self.hpeWorker = worker_class(path=path)
        self.hpeWorker.setup_on_thread(self.mediaThread)
        self.hpeWorker.ImageUpdate.connect(self.image_update_slot)
        self.toggle_hpe_signal.connect(self.hpeWorker.toggle_hpe)
        self.toggle_play_state.connect(self.hpeWorker.toggle_play_state)
        qDebug(f'starting media thread of type {str(worker_class)}')
        self.mediaThread.start()
        self.remove_widget()
        self.design.addWidget(self.feed, *self.feedWidgetLoc)

    @pyqtSlot()
    def open_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", QDir.homePath())
        if file_name:
            self.create_hpe_worker(ImageWorker, file_name)

    @pyqtSlot()
    def open_web_cam(self):
        # self.feed.setStyleSheet(
        # "border : solid black;" "border-width : 20px 1px 20px 1px;")
        self.create_hpe_worker(WebCamWorker)

    @pyqtSlot()
    def open_video(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video", QDir.homePath())
        if file_name:
            self.create_hpe_worker(VideoWorker, file_name)
            self.set_video_buttons_enabled(True)

    @pyqtSlot()
    def update_hpe(self):
        self.hpeOn = not self.hpeOn
        self.hpe_button.setText(self.hpe_text[int(self.hpeOn)])
        self.toggle_hpe_signal.emit(self.hpeOn)

    @pyqtSlot()
    def play_pressed(self):
        self.toggle_play_state.emit(True)
        pass

    @pyqtSlot()
    def stop_pressed(self):
        self.toggle_play_state.emit(False)
        pass

    def closeEvent(self, event):
        if self.mediaThread:
            qDebug('closing media thread')
            self.mediaThread.quit()
            self.mediaThread.wait()

        if self.naoProxy:
            qDebug('closing nao proxy')
            self.naoProxy.close()
            self.naoProxy = None
        qDebug('accept event')
        super().closeEvent(event)

stylesheet = """
    GUI {
        background-image: url("mrmime.jpeg");
        background-repeat: no-repeat; 
        background-position: center;
        background-color: #ed859e;
    }
"""

App = QApplication(sys.argv)
App.setStyleSheet(stylesheet)
Root = GUI()
Root.show()
sys.exit(App.exec())