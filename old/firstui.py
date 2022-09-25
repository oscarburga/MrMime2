from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cv2
import sys


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

        self.playButton = QPushButton()
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.openButton = QPushButton("Open Video")
        self.openButton.clicked.connect(self.openFile)

        self.CancelBTN = QPushButton("Cancel")
        self.CancelBTN.clicked.connect(self.CancelFeed)
        self.Layout.addWidget(self.CancelBTN)
        self.Layout.addWidget(self.videoWidget)
        self.Layout.addWidget(self.openButton)
        self.Layout.addWidget(self.playButton)
        self.WebCam = WebCam()

        self.WebCam.start()
        self.WebCam.ImageUpdate.connect(self.ImageUpdateSlot)
        self.Widget.setLayout(self.Layout)
        self.mediaPlayer.setVideoOutput(self.videoWidget)

    def ImageUpdateSlot(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def CancelFeed(self):
        self.WebCam.stop()

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                                                  QDir.homePath())

        if fileName != '':
            self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(fileName)))

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()


class WebCam(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ThreadActive = None

    def run(self):
        self.ThreadActive = True
        Capture = cv2.VideoCapture(0)
        while self.ThreadActive:
            ret, frame = Capture.read()
            if ret:
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                FlippedImage = cv2.flip(Image, 1)
                ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0],
                                           QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic)

    def stop(self):
        self.ThreadActive = False
        self.quit()


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
