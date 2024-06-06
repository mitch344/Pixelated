import json
from PyQt5.QtCore import QThread, pyqtSignal
from src.rom_data_fetcher import ROMDataFetcher

class DataRefreshThread(QThread):
    data_refreshed = pyqtSignal(list)

    def __init__(self, channel):
        super().__init__()
        self.channel = channel
        self.rom_data_fetcher = ROMDataFetcher()

    def run(self):
        device_data = self.rom_data_fetcher.fetch_channel_updates(self.channel)
        with open(f"./device_data_{self.channel}.json", "w") as file:
            json.dump(device_data, file, indent=4)
        self.data_refreshed.emit(device_data)