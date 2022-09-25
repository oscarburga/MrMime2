from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import cv2
import DetectPoseFunction as dp
pose_video = dp.mp_pose.Pose(static_image_mode = False, min_detection_confidence = 0.5, model_complexity = 1)

class MediaThreadBase(QThread):
    onFrameProcessed = pyqtSignal(QImage, list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hpeOn = False
        self.path = ''
        self.ThreadActive = None
        # self.hpeMutex = QMutex()

    def run(self):
        print('Calling base media thread\'s run. Doing nothing.')
    
    def stop(self):
        self.ThreadActive = False
        self.quit()
    
    def isHpeActive(self) -> bool:
        # self.hpeMutex.lock()
        ret = self._hpeOn
        # self.hpeMutex.unlock()
        return ret

    # toggle Hpe and return its new value
    def toggleHpe(self, newHpe=None) -> bool:
        # self.hpeMutex.lock()
        self._hpeOn = newHpe if newHpe else (not self._hpeOn)
        ret = self._hpeOn
        # self.hpeMutex.unlock()
        return ret

    def hpe(self):
        self.toggleHpe()

    def getFrameAsQtImage(self, frame):
        ConvertToQtFormat = QImage(frame.data, frame.shape[1], frame.shape[0], 
            QImage.Format_RGB888)
        Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
        return Pic


class ImageThread(MediaThreadBase):

    def run(self):
        self.ThreadActive = True
        image = None
        landmarks = []

        try: 
            image = cv2.imread(self.path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.flip(image, 1)
        except Exception as e:
            print(f'ImageThread: failed to read img path="{self.path}"')
            print(f'Exception: {e}')
            return

        if self.isHpeActive():
            image, landmarks = dp.detectPose(image, pose_video, display = False)

        qImage = self.getFrameAsQtImage(frame)
        self.onFrameProcessed.emit(qImage, landmarks)
        self.ThreadActive = False
    

class VideoThreadBase(MediaThreadBase):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.video = None

    def __del__(self):
        if self.video:
            self.video.release()
        
    def open_video_capture_or_quit(self):
        try:
            self.video = cv2.VideoCapture(self.path)
            print(f'Successfully opened video capture {self.path}')
            return True
        except Exception as e:
            print(f'VideoThread: Failed to open video capture with path {self.path}')
            print(f'Error: {e}')
            self.ThreadActive = False
            self.quit()
            return False
    
    def process_single_frame(self):
        ret, frame = self.video.read()
        if ret:
            print(f'processing single frame...')
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1)
            landmarks = []
            if self.isHpeActive():
                print(f'doing pose detection')
                frame, landmarks = dp.detectPose(frame, pose_video, display = False)
            qImage = self.getFrameAsQtImage(frame)
            print(f'emitting frame...')
            self.onFrameProcessed.emit(qImage, landmarks)

    def stop(self):
        super().stop()
        if self.video:
            self.video.release()

    def run(self):
        print('Calling base video thread\'s run. Doing nothing.')
    

class VideoThread(VideoThreadBase):

    def run(self):
        self.ThreadActive = True
        if not self.open_video_capture_or_quit():
            # quitting
            return

        while True:
            # Thread may be paused (stop processing video in the middle)
            if self.ThreadActive:
                self.process_single_frame()
    
    def toggleActive(self):
        self.ThreadActive = not self.ThreadActive
        
    

class WebcamThread(VideoThreadBase):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.path = 0

    def run(self):
        self.ThreadActive = True
        if not self.open_video_capture_or_quit():
            # quitting
            return

        # If thread gets stopped, just stop the whole process
        while self.ThreadActive:
            self.process_single_frame()
