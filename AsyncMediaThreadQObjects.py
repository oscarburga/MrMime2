from AsyncWorkerBase import *
from PyQt5.QtGui import *

import cv2
import DetectPoseFunction as dp

pose_img = dp.mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5, model_complexity=2)
pose_video = dp.mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, model_complexity=2)
global_pose_mutex = QMutex()


class BaseHpeWorker(AsyncWorkerBase):
    ImageUpdate = pyqtSignal(QImage, list, object)

    def __init__(self, parent, path):
        super().__init__(parent)
        self.hpeOn = False
        self.path = path
        self.done = False

    def setup_on_thread(self, thread=None) -> QThread:
        thread = super().setup_on_thread(thread)
        thread.started.connect(self.on_thread_start)
        thread.finished.connect(self.on_thread_end)
        thread.finished.connect(thread.deleteLater)
        return thread

    @pyqtSlot(bool)
    def toggle_hpe(self, new_hpe=None):
        self.hpeOn = new_hpe if new_hpe else not self.hpeOn

    @pyqtSlot(bool)
    def toggle_play_state(self, new_play_state=None):
        pass

    @staticmethod
    def process_single_frame(image, hpe, is_img=False) -> (QImage, list, object):
        landmarks = []
        if hpe:
            global_pose_mutex.lock()
            image, landmarks = dp.detectPose(image, pose_img if is_img else pose_video, display=False)
            global_pose_mutex.unlock()

        convert_to_qt_format = QImage(image.data, image.shape[1], image.shape[0],
                                      QImage.Format_RGB888).scaled(640, 480, Qt.KeepAspectRatio)
        return convert_to_qt_format, landmarks, image

    def on_valid_tick(self):
        pass


class ImageWorker(BaseHpeWorker):

    def __init__(self, parent=None, path=''):
        super().__init__(parent, path)
        self.IsTickable = False

    @pyqtSlot()
    def on_thread_start(self):
        log_safe('ImageWorker on_thread_start')
        try:
            image = cv2.imread(self.path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.flip(image, 1)
            img, landmarks, raw = self.process_single_frame(image, self.hpeOn, is_img=True)
            self.ImageUpdate.emit(img, landmarks, raw)
        except Exception as e:
            log_safe(f'ImageWorker.on_thread_start failed with path {self.path}')

    @pyqtSlot(bool)
    def toggle_hpe(self, new_hpe=None):
        super().toggle_hpe(new_hpe)
        self.on_thread_start()


class BaseVideoWorker(BaseHpeWorker):
    def __init__(self, parent=None, path=''):
        super().__init__(parent, path)
        self.IsTickable = True
        self.Capture = None
        self.LastTickTime = None

    @pyqtSlot()
    def on_thread_start(self):
        super().on_thread_start()
        try:
            self.Capture = cv2.VideoCapture(self.path)
        except Exception as e:
            log_safe(f'Failed to open video capture - {e}')
        global_pose_mutex.lock()
        pose_video.reset()
        global_pose_mutex.unlock()

    @pyqtSlot()
    def on_thread_end(self):
        if self.Capture:
            self.Capture.release()
        super().on_thread_end()

    def on_valid_tick(self):
        if self.Capture:
            ret, frame = self.Capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.flip(frame, 1)
                # log_safe('emitting pic and landmarks')
                pic, landmarks, raw = self.process_single_frame(frame, self.hpeOn, is_img=False)
                self.ImageUpdate.emit(pic, landmarks, raw)
            else:
                log_safe('failed to read from capture')


class WebCamWorker(BaseVideoWorker):

    def __init__(self, parent=None, path=''):
        super().__init__(parent, path)
        self.path = 0

    @pyqtSlot()
    def tick(self):
        # print('webcamworker tick')
        self.on_valid_tick()


class VideoWorker(BaseVideoWorker):

    def __init__(self, parent=None, path=''):
        super().__init__(parent, path)
        self.videoPaused = True

    @pyqtSlot()
    def tick(self):
        if not self.videoPaused:
            # print('videoworker tick')
            self.on_valid_tick()

    @pyqtSlot(bool)
    def toggle_play_state(self, new_play_state=None):
        self.videoPaused = not new_play_state
