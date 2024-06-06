from PyQt5.QtCore import QThread, pyqtSignal

class FlashingThread(QThread):
    finished = pyqtSignal(bool)

    def __init__(self, folder_name, pipeline):
        super().__init__()
        self.folder_name = folder_name
        self.pipeline = pipeline

    def run(self):
        success = self.pipeline.install(self.folder_name)
        self.finished.emit(success)