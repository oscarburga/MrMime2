from PyQt5.QtCore import *

global_log_lock = QMutex()

def log_safe(*args, **kwargs):
    global_log_lock.lock()
    print(*args, **kwargs)
    global_log_lock.unlock()


class AsyncWorkerBase(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.IsTickable = False
        self.timerId = None

    def setup_on_thread(self, thread=None) -> QThread:
        if not thread:
            thread = QThread()
        self.moveToThread(thread)
        thread.started.connect(self.on_thread_start)
        thread.finished.connect(self.on_thread_end)
        thread.finished.connect(thread.deleteLater)
        return thread

    @pyqtSlot()
    def on_thread_start(self):
        if self.IsTickable:
            self.timerId = self.startTimer(0)

    @pyqtSlot()
    def on_thread_end(self):
        if self.IsTickable and self.timerId:
            self.killTimer(self.timerId)
        self.deleteLater()

    def timerEvent(self, event):
        if self.timerId == event.timerId():
            self.tick()

    def tick(self):
        pass
