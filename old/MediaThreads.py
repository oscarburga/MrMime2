from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cv2
import DetectPoseFunction as dp

pose_video = dp.mp_pose.Pose(static_image_mode = False, min_detection_confidence = 0.5, model_complexity = 1)
global_pose_mutex = QMutex()

class BaseHpeThread(QThread):
    ImageUpdate = pyqtSignal(QImage, list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ThreadActive = None
        self.shouldExit = False
        self.hpeOn = False

    def hpe(self, newVal=None):
        if newVal:
            self.hpeOn = newVal
        else:
            self.hpeOn = not self.hpeOn

    def process_single_frame(image, hpe):
        landmarks = []
        if hpe:
            global_pose_mutex.lock()
            image, landmarks = dp.detectPose(image, pose_video, display=False)
            global_pose_mutex.unlock()

        ConvertToQtFormat = QImage(image.data, image.shape[1], image.shape[0], 
            QImage.Format_RGB888).scaled(640, 480, Qt.KeepAspectRatio)

        return ConvertToQtFormat, landmarks

    def stop(self):
        pass


class Image(BaseHpeThread):
    path = ''

    def run(self):
        self.ThreadActive = True
        image = cv2.imread(self.path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.flip(image, 1)
        landmarks = []
        if self.hpeOn:
            image, landmarks = dp.detectPose(image, pose_video, display = False)
        ConvertToQtFormat = QImage(image.data, image.shape[1], image.shape[0],
                                QImage.Format_RGB888)

        Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
        self.ImageUpdate.emit(Pic, landmarks)

    def hpe(self, newVal=None):
        super().hpe(newVal)
        if self.ThreadActive:
            self.run()

class Video(BaseHpeThread):
    path = ''

    def run(self):
        self.ThreadActive = True
        video = cv2.VideoCapture(self.path)
        while not self.shouldExit:
            if self.ThreadActive:
                ret, frame = video.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.flip(frame, 1)

                    # Obtener la anchura y la altura del frame
                    frame_height, frame_width, _ =  frame.shape

                    # Cambia el tamaño del cuadro manteniendo la relación de aspecto.
                    #frame = cv2.resize(frame, (int(frame_width * (640 / frame_height)), 640))
                    # Realice la detección de puntos de referencia de la pose.
                    landmarks = []
                    if self.hpeOn:
                        frame, landmarks = dp.detectPose(frame, pose_video, display = False)
                    ConvertToQtFormat = QImage(frame.data, frame.shape[1], frame.shape[0],
                                            QImage.Format_RGB888)

                    Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                    self.ImageUpdate.emit(Pic, landmarks)
                    self.eventDispatcher().processEvents(QEventLoop.AllEvents)
        video.release()

    def stop(self):
        self.ThreadActive = False

    def play(self):
        self.ThreadActive = True

class WebCam(BaseHpeThread):
    hpeOn = False

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ThreadActive = None

    def run(self):
        self.ThreadActive = True
        Capture = cv2.VideoCapture(0)
        while not self.shouldExit:
            ret, frame = Capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.flip(frame, 1)
                frame_height, frame_width, _ =  frame.shape
                landmarks = []
                if self.hpeOn:
                    frame, landmarks = dp.detectPose(frame, pose_video, display = False)
                ConvertToQtFormat = QImage(frame.data, frame.shape[1], frame.shape[0],
                                           QImage.Format_RGB888)

                Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic, landmarks)
        Capture.release()

    def stop(self):
        self.ThreadActive = False
        self.shouldExit = True
