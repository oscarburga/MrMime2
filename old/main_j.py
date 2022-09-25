from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import cv2
import DetectPoseFunction as dp

from NaoProxy import *


# Inicialización del modelo

pose_video = dp.mp_pose.Pose(static_image_mode = False, min_detection_confidence = 0.5, model_complexity = 1)


class GUI(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MrMime2")
        self.setGeometry(60, 60, 960, 540)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()
        self.Widget = QWidget(self)
        self.setCentralWidget(self.Widget)

        self.Layout = QVBoxLayout()
        self.FeedLabel = QLabel()
        self.Layout.addWidget(self.FeedLabel)

        self.stopButton = QPushButton()
        self.stopButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stopButton.clicked.connect(self.stop)

        self.playButton = QPushButton()
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.hpeButton = QPushButton("HPE")
        self.hpeButton.clicked.connect(self.hpe)

        self.openCameraButton = QPushButton("Open Camera")
        self.openCameraButton.clicked.connect(self.openCamera)

        self.openVideoButton = QPushButton("Open Video")
        self.openVideoButton.clicked.connect(self.openVideo)
        
        self.openImageButton = QPushButton("Open Image")
        self.openImageButton.clicked.connect(self.openImage)

        #self.CancelBTN = QPushButton("Cancel")
        #self.CancelBTN.clicked.connect(self.CancelFeed)
        #self.Layout.addWidget(self.CancelBTN)
        self.Layout.addWidget(self.videoWidget)
        self.Layout.addWidget(self.openCameraButton)
        self.Layout.addWidget(self.openVideoButton)
        self.Layout.addWidget(self.openImageButton)
        self.Layout.addWidget(self.hpeButton)
        self.Layout.addWidget(self.playButton)
        self.Layout.addWidget(self.stopButton)
        self.WebCam = WebCam()
        self.Video = Video()
        self.Image = Image()
        self.Widget.setLayout(self.Layout)

        self.naoProxy = NaoProxy()

    def ImageUpdateSlot(self, Image, landmarks):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))
        if len(landmarks):
            self.naoProxy.process_landmark_list(landmarks)

    def CancelFeed(self):
        self.WebCam.stop()

    def openCamera(self):
        self.WebCam.ImageUpdate.connect(self.ImageUpdateSlot)
        self.WebCam.start()


    def openVideo(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                                                  QDir.homePath())

        print(fileName)
        self.Video.ImageUpdate.connect(self.ImageUpdateSlot)
        self.Video.path = fileName
        self.Video.start()
        '''
        if fileName != '':
            self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(fileName)))

        '''

    def openImage(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                                                  QDir.homePath())

        print(fileName)
        self.Image.ImageUpdate.connect(self.ImageUpdateSlot)
        self.Image.path = fileName
        self.Image.start()

    def play(self):
        self.Video.play_pressed()

    def stop(self):
        self.Video.stop()

    def hpe(self):
        self.Video.hpe()
        self.WebCam.hpe()
        self.Image.hpe()
    



stylesheet = """
    GUI {
        background-image: url("mrmime.jpeg");
    }
"""

App = QApplication(sys.argv)
App.setStyleSheet(stylesheet)
Root = GUI()
Root.show()
sys.exit(App.exec())