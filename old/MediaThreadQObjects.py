from PyQt5.QtCore import *
from PyQt5.QtGui import *

import cv2
import DetectPoseFunction as dp

pose_video = dp.mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, model_complexity=2)
global_pose_mutex = QMutex()

class BaseHpeWorker(QObject):
    ImageUpdate = pyqtSignal(QImage, list)

    def __init__(self, parent, path):
        super().__init__(parent)
        self.hpeOn = False
        self.ThreadActive = None
        self.IsTickable = False
        self.path = path
        self.timerId = None

    def setup_on_thread(self, thread=None) -> QThread:
        pass
        # if not thread:
        #     thread = QThread()

        # self.moveToThread(thread)
        # thread.started.connect(self.on_thread_start)
        # thread.finished.connect(self.on_thread_end)
        # thread.finished.connect(thread.deleteLater)

        # return thread

    @pyqtSlot()
    def on_thread_start(self):
        if self.IsTickable:
            self.timerId = self.startTimer(0)

    @pyqtSlot(bool)
    def toggle_hpe(self, new_hpe=None):
        self.hpeOn = new_hpe if new_hpe else not self.hpeOn

    @pyqtSlot()
    def on_thread_end(self):
        if self.IsTickable and self.timerId:
            self.killTimer(self.timerId)
        self.deleteLater()

    def timerEvent(self, event):
        if self.timerId == event.timerId():
            self.tick()

    @staticmethod
    def process_single_frame(image, hpe):
        landmarks = []
        if hpe:
            global_pose_mutex.lock()
            image, landmarks = dp.detectPose(image, pose_video, display=False)
            global_pose_mutex.unlock()

        convert_to_qt_format = QImage(image.data, image.shape[1], image.shape[0],
                                      QImage.Format_RGB888).scaled(640, 480, Qt.KeepAspectRatio)
        return convert_to_qt_format, landmarks

    def tick(self):
        print('base worker tick - do nothing')
        pass


class ImageWorker(BaseHpeWorker):

    def __init__(self, parent=None, path=''):
        super().__init__(parent, path)
        self.IsTickable = False

    @pyqtSlot()
    def on_thread_start(self):
        print('ImageWorker on_thread_start')
        try:
            image = cv2.imread(self.path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.flip(image, 1)
            img, landmarks = self.process_single_frame(image, self.hpeOn)
            self.ImageUpdate.emit(img, landmarks)
        except Exception as e:
            print(f'ImageWorker.on_thread_start: {e}')

    @pyqtSlot(bool)
    def toggle_hpe(self, new_hpe=None):
        super().toggle_hpe(new_hpe)
        self.on_thread_start()


class BaseVideoWorker(BaseHpeWorker):
    def __init__(self, parent=None, path=''):
        super().__init__(parent, path)
        self.IsTickable = True
        self.Capture = None

    @pyqtSlot()
    def on_thread_start(self):
        super().on_thread_start()
        self.Capture = cv2.VideoCapture(0)

    @pyqtSlot()
    def on_thread_end(self):
        if self.Capture:
            self.Capture.release()

    def on_valid_tick(self):
        if self.Capture:
            ret, frame = self.Capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.flip(frame, 1)
                print('emitting pic and landmarks')
                pic, landmarks = self.process_single_frame(frame, self.hpeOn)
                self.ImageUpdate.emit(pic, landmarks)
            else:
                print('failed to read from capture')


class WebCamWorker(BaseVideoWorker):
    def __init__(self, parent=None, path=''):
        super().__init__(parent, path)

    @pyqtSlot()
    def tick(self):
        print('webcamworker tick')
        self.on_valid_tick()

class VideoWorker(ImageWorker):
    path = ''

    def run(self):
        self.ThreadActive = True
        video = cv2.VideoCapture(self.path)
        while True:
            if self.ThreadActive:
                ret, frame = video.read()
                if ret:
                    # Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.flip(frame, 1)

                    # Obtener la anchura y la altura del frame
                    frame_height, frame_width, _ = frame.shape

                    # Cambia el tamaño del cuadro manteniendo la relación de aspecto.
                    # frame = cv2.resize(frame, (int(frame_width * (640 / frame_height)), 640))
                    # Realice la detección de puntos de referencia de la pose.
                    landmarks = []
                    if self.hpeOn:
                        frame, landmarks = dp.detectPose(frame, pose_video, display=False)
                    ConvertToQtFormat = QImage(frame.data, frame.shape[1], frame.shape[0],
                                               QImage.Format_RGB888)

                    Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                    self.ImageUpdate.emit(Pic, landmarks)
        video.release()

    def stop(self):
        self.ThreadActive = False
        # self.quit()

    def play(self):
        self.ThreadActive = True
        # self.quit()
