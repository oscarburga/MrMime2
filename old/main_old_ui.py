import sys

from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from MediaThreads import *
from MediaThreadQObjects import *
from NaoProxy import *


class GUI(QMainWindow):
    OnStopThread = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MrMime2")
        self.setGeometry(60, 60, 960, 540)
        self.setFixedSize(960, 540)
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)
        self.design = QGridLayout()

        # Use video
        ## Open video button
        self.useVideo = QPushButton("Use Video")
        self.useVideo.clicked.connect(self.open_video)
        self.Video = Video()
        self.Video.ImageUpdate.connect(self.ImageUpdateSlot)
        self.design.addWidget(self.useVideo, 0, 0, 1, 0)

        # Use webcam
        ## Open webcam button
        self.useWebCam = QPushButton("Use WebCam")
        self.useWebCam.clicked.connect(self.openWebCam)
        self.WebCam = WebCam()
        self.design.addWidget(self.useWebCam, 1, 0, 1, 0)
         
        # Use image
        ## Open image button
        self.useImage = QPushButton("Use Image")
        self.useImage.clicked.connect(self.openImage)
        self.Image = Image()
        self.design.addWidget(self.useImage, 2, 0, 1, 0)

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
        self.hostname_input.setPlaceholderText('Insert Hostname')
        self.naoLayout.addWidget(self.hostname_input, 1, 1)
        ##  Port label
        self.port_label = QLabel()
        self.port_label.setFont(QFont('Arial', 15, QFont.Bold))
        self.port_label.setStyleSheet("color : black; ")
        self.port_label.setText("Port")
        self.naoLayout.addWidget(self.port_label, 2, 0)
        ##  Port input
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText('Insert Port')
        self.naoLayout.addWidget(self.port_input, 2, 1)
        ## Connect button
        self.connect = QPushButton("Connect")
        self.connect.clicked.connect(self.updateConnection)
        self.naoLayout.addWidget(self.connect, 3, 0, 1, 0)
        ## Connection state
        self.connected = False
        self.connection = QLabel()
        self.connection.setPixmap(QPixmap('icon2.png').scaled(50, 50, Qt.KeepAspectRatio))
        self.naoLayout.addWidget(self.connection, 4, 0)
        self.connection_text = QLabel()
        self.connection_text.setFont(QFont('Arial', 15, QFont.Bold))
        self.connection_text.setStyleSheet("color : black; ")
        self.connection_text.setText("Not Connected")
        self.naoLayout.addWidget(self.connection_text, 4, 1)
        ## Activar HPE
        self.hpe = False
        self.hpe_text = ["Activar HPE", "Desactivar HPE"]
        self.hpe_button = QPushButton("Activar HPE")
        self.hpe_button.clicked.connect(self.updateHPE)
        self.naoLayout.addWidget(self.hpe_button, 5, 0, 1, 0)

        # Details
        self.feed = QLabel()
        self.design.addWidget(self.feed, 3, 0)
        self.design.setColumnStretch(0, 2)
        self.design.setColumnStretch(1, 1)
        self.design.addLayout(self.naoLayout, 3, 1)
        self.widget.setLayout(self.design)

        self.naoProxy = None
        self.activeThread: BaseHpeThread = None

    def updateConnection(self):
        if not self.naoProxy:
            self.naoProxy = NaoProxy()
            self.connected = True
            self.connection.setPixmap(QPixmap('icon1.png').scaled(50, 50, Qt.KeepAspectRatio))
            self.connection_text.setText("Connected")
            print(self.hostname_input.text())
            print(self.port_input.text())

    @pyqtSlot()
    def update_hpe(self):
        self.hpeOn = not self.hpeOn
        self.hpe_button.setText(self.hpe_text[int(self.hpeOn)])
        if self.activeThread:
            self.activeThread.hpe()

    def remove_widget(self):
        if self.activeThread:
            self.activeThread.stop()
            self.design.removeWidget(self.feed)
            self.activeThread = None

    def openVideo(self):
        self.remove_widget()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Movie", QDir.homePath())
        if file_name:
            self.Video.path = file_name
            self.activeThread = self.Video
            self.Video.start()

    def openWebCam(self):
        self.remove_widget()
        # self.feed.setStyleSheet("border : solid black;" "border-width : 20px 1px 20px 1px;")
        self.activeThread = self.WebCam
        self.activeThread.hpe(self.hpe)
        self.WebCam.start()

    def ImageUpdateSlot(self, Image, landmarks):
        if self.feed:
            self.feed.setPixmap(QPixmap.fromImage(Image))
        if len(landmarks) and self.naoProxy:
            self.naoProxy.process_landmark_list(landmarks)

    def openImage(self):
        self.remove_widget()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                                                  QDir.homePath())
        if fileName:
            self.Image.path = fileName
            self.Image.start()

    def open_video(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                                                  QDir.homePath())
        if fileName:
            self.Video.path = fileNme
            self.Video.start()

    def play(self):
        self.Video.play()

    def stop(self):
        self.Video.stop()

    def closeEvent(self, event):
        print('closing thread')
        for i, thread in enumerate([self.Video, self.Image, self.WebCam]):
            if thread:
                print(f'closing thread {i}')
                thread.shouldExit = True
                thread.stop()
                thread.quit()
                thread.wait()
        
        print('closing nao proxy')
        if self.naoProxy:
            self.naoProxy.close()
            self.naoProxy = None

        print('accept event')
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