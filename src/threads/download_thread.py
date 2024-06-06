import os
import requests
from PyQt5.QtCore import QThread, pyqtSignal

class DownloadThread(QThread):
    download_progress_updated = pyqtSignal(int)
    download_completed = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        response = requests.get(self.url, stream=True)
        total_size = int(response.headers.get("Content-Length", 0))
        block_size = 1024

        file_name = self.url.split("/")[-1]
        current_directory = os.getcwd()
        file_path = os.path.join(current_directory, file_name)

        with open(file_path, "wb") as file:
            downloaded_size = 0
            for data in response.iter_content(block_size):
                file.write(data)
                downloaded_size += len(data)
                progress = int(downloaded_size / total_size * 100)
                self.download_progress_updated.emit(progress)

        self.download_completed.emit(file_path)