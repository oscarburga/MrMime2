from sqlite3 import connect
import cv2
import sys

from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from MediaThreads import *

class GUI(QMainWindow):
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
        self.useVideo.clicked.connect(self.openVideo)
        self.design.addWidget(self.useVideo, 0, 0, 1, 0)
        ## Reserve PlayVideo button
        self.playVideo = None

        # Use webcam
        ## Open webcam button
        self.useWebCam = QPushButton("Use WebCam")
        self.useWebCam.clicked.connect(self.openWebCam)
        self.design.addWidget(self.useWebCam, 1, 0, 1, 0)
         
        # Use image
        ## Open image button
        self.useImage = QPushButton("Use Image")
        self.useImage.clicked.connect(self.openImage)
        self.design.addWidget(self.useImage, 2, 0, 1, 0)

        # NAO Layout
        self.naoLayoutWidget = QWidget(self.widget)
        self.naoLayoutWidget.setStyleSheet("background-color:#60e0e0e0;")
        self.naoLayout = QGridLayout(self.naoLayoutWidget)
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
        self.connection.setPixmap(QPixmap('icon2.jpg').scaled(50, 50, Qt.KeepAspectRatio))
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
        self.naoLayoutWidget.setLayout(self.naoLayout)

        # Details
        self.design.setColumnStretch(0, 2)
        self.design.setColumnStretch(1, 1)
        # self.design.addLayout(self.naoLayout, 3, 1)
        self.design.addWidget(self.naoLayoutWidget, 3, 1)
        self.widget.setLayout(self.design)

        self.mediaThread = None
        self.feed = QLabel()
        self.feed.setStyleSheet("border : solid black;" "border-width : 20px 1px 20px 1px;")
        self.design.addWidget(self.feed, 3, 0, 3, 0)
        self.feed.hide()
    
    def updateConnection(self):
        self.connected = True
        self.connection.setPixmap(QPixmap('icon1.jpg').scaled(50, 50, Qt.KeepAspectRatio))
        self.connection_text.setText("Connected")
        print(self.hostname_input.text())
        print(self.port_input.text())

    def updateHPE(self):
        if self.hpeThread:
            self.hpe = self.hpeThread.toggleHpe(self.hpe)

        if self.hpe:
            self.hpe_button.setText(self.hpe_text[1])
        else:
            self.hpe_button.setText(self.hpe_text[0])
        print(f'main HPE = {self.hpe}')

    def stopMediaAndClear(self):
        if self.playVideo:
            self.design.removeWidget(self.playVideo)
            self.playVideo.deleteLater()
            self.playVideo = None

        if self.mediaThread:
            self.mediaThread.stop()
            self.mediaThread = None

        if self.feed:
            self.feed.hide()
    
    def recreateFeed(self):
        self.stopMediaAndClear()
        self.feed.show()
        # self.feed = QLabel()
        # self.feed.setStyleSheet("border : solid black;" "border-width : 20px 1px 20px 1px;")
        # self.design.addWidget(self.feed, 3, 0, 3, 0)
    
    def recreateMediaThread(self, mediaThreadType, path=None):
        self.mediaThread = mediaThreadType()
        if path:
            self.mediaThread.path = path
        self.mediaThread.onFrameProcessed.connect(self.onFrameProcessed)

    def openVideo(self):
        self.stopMediaAndClear()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie", QDir.homePath())
        if len(fileName):
            self.recreateFeed()
            self.recreateMediaThread(VideoThread, fileName)

            self.playVideo = QPushButton()
            self.playVideo.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.playVideo.clicked.connect(self.mediaThread.toggleActive)
            self.design.addWidget(playVideo, 6, 0)
            self.mediaThread.start()
            print(fileName)
        else:
            print(f'Did not input a valid fileName')

    def openWebCam(self):
        self.recreateFeed()
        self.recreateMediaThread(WebcamThread)
        self.mediaThread.start()

    def openImage(self):
        self.stopMediaAndClear()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie", QDir.homePath())
        if len(fileName):
            self.recreateFeed()
            self.recreateMediaThread(ImageThread, fileName)
            self.mediaThread.start()
            print(fileName)

    def onFrameProcessed(self, Image, landmarks):
        self.feed.setPixmap(QPixmap.fromImage(Image))
        return
        if self.feed:
            print('updating img')
            if len(landmarks):
                pass
        else:
            print('no feed?')
            assert False



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