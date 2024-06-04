from PyQt5.QtCore import QThread, pyqtSignal

class FlashingThread(QThread):
    finished = pyqtSignal(bool)

    def __init__(self, folder_name, install_pipeline):
        super().__init__()
        self.folder_name = folder_name
        self.install_pipeline = install_pipeline

    def run(self):
        success = self.install_pipeline.install(self.folder_name)
        self.finished.emit(success)