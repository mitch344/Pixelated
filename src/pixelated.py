import sys
import json
import os
import zipfile
import subprocess

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QLabel, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

from threads.data_refresh_thread import DataRefreshThread
from threads.download_thread import DownloadThread
from threads.flashing_thread import FlashingThread
from threads.fastboot_thread import FastbootThread

from pipelines.lineageos_pipeline import LineageOSPipeline
from pipelines.stock_pipeline import StockPipeline


class DeviceInfoGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.device_data = {}
        self.downloaded_files = {}
        self.fastboot_thread = None
        self.initUI()
        self.download_queue = []
        self.current_folder_name = None
        self.install_pipelines = {
            "LineageOS": LineageOSPipeline(),
            "Google Play Services": StockPipeline(),
            "GrapheneOS": StockPipeline(),
            "GrapheneOSBeta": StockPipeline()
        }

    def initUI(self):
        layout = QVBoxLayout()

        self.fastboot_version_label = QLabel()
        layout.addWidget(self.fastboot_version_label)

        self.fastboot_devices_label = QLabel()
        layout.addWidget(self.fastboot_devices_label)

        self.flashing_lock_label = QLabel()
        layout.addWidget(self.flashing_lock_label)

        fastboot_layout = QHBoxLayout()
        fastboot_label = QLabel("Commands:")
        fastboot_layout.addWidget(fastboot_label)

        reboot_button = QPushButton("Reboot")
        reboot_button.clicked.connect(lambda: self.run_fastboot_command("reboot"))
        fastboot_layout.addWidget(reboot_button)

        reboot_bootloader_button = QPushButton("Reboot Bootloader")
        reboot_bootloader_button.clicked.connect(lambda: self.run_fastboot_command("reboot-bootloader"))
        fastboot_layout.addWidget(reboot_bootloader_button)

        oem_unlock_button = QPushButton("OEM Unlock")
        oem_unlock_button.clicked.connect(lambda: self.run_fastboot_command("oem unlock"))
        fastboot_layout.addWidget(oem_unlock_button)

        oem_lock_button = QPushButton("OEM Lock")
        oem_lock_button.clicked.connect(lambda: self.run_fastboot_command("oem lock"))
        fastboot_layout.addWidget(oem_lock_button)

        flashing_unlock_button = QPushButton("Flashing Unlock")
        flashing_unlock_button.clicked.connect(lambda: self.run_fastboot_command("flashing unlock"))
        fastboot_layout.addWidget(flashing_unlock_button)

        flashing_lock_button = QPushButton("Flashing Lock")
        flashing_lock_button.clicked.connect(lambda: self.run_fastboot_command("flashing lock"))
        fastboot_layout.addWidget(flashing_lock_button)

        layout.addLayout(fastboot_layout)

        channel_layout = QHBoxLayout()
        self.channel_combo_box = QComboBox()
        self.channel_combo_box.addItem("Select Channel")
        self.channel_combo_box.addItem("Google Play Services")
        self.channel_combo_box.addItem("GrapheneOS")
        self.channel_combo_box.addItem("GrapheneOSBeta")
        self.channel_combo_box.addItem("LineageOS")
        channel_layout.addWidget(QLabel("Channel:"))
        channel_layout.addWidget(self.channel_combo_box)
        layout.addLayout(channel_layout)

        self.combo_box = QComboBox()
        self.combo_box.addItem("Select Device")
        layout.addWidget(self.combo_box)

        refresh_button = QPushButton("Refresh Channel")
        refresh_button.clicked.connect(self.refresh_data)
        layout.addWidget(refresh_button)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Version", "Download/Install"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.setSelectionMode(QTableWidget.NoSelection)
        self.table_widget.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(self.table_widget)

        self.channel_combo_box.currentTextChanged.connect(self.load_device_data)
        self.combo_box.currentIndexChanged.connect(self.update_table)

        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self.setWindowTitle("Pixelated")
        self.setGeometry(100, 100, 800, 600)

        icon = QIcon("Pixelated.png")
        self.setWindowIcon(icon)

        self.check_fastboot_version()
        self.check_fastboot_devices()

        self.fetching_timer = QTimer()
        self.fetching_timer.timeout.connect(self.update_fetching_dots)
        self.fetching_dots = 0
    
    def start_flashing(self, folder_name):
        channel = self.channel_combo_box.currentText()

        if channel == "LineageOS":
            install_pipeline = LineageOSPipeline()
        else:
            install_pipeline = StockPipeline()

        self.status_label.setText("Installing image...")
        self.flashing_thread = FlashingThread(folder_name, install_pipeline)
        self.flashing_thread.finished.connect(self.flashing_finished)
        self.flashing_thread.start()

    def flashing_finished(self, success):
        if success:
            self.status_label.setText("Installation completed successfully.")
        else:
            self.status_label.setText("Installation failed. Installation script not found.")

    def check_fastboot_version(self):
        try:
            result = subprocess.run(["fastboot", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                version_line = lines[0]
                version = version_line.split(" ")[2]
                self.fastboot_version_label.setText(f"Fastboot Version: {version}")
            else:
                self.fastboot_version_label.setText("Fastboot: Unexpected error")
        except FileNotFoundError:
            self.fastboot_version_label.setText("Fastboot: Not installed or properly configured")

    def check_fastboot_devices(self):
        try:
            result = subprocess.run(["fastboot", "devices"], capture_output=True, text=True)
            if result.returncode == 0:
                devices = result.stdout.strip().split("\n")
                device_ids = [device.split("\t")[0] for device in devices if device]
                if device_ids:
                    self.fastboot_devices_label.setText(f"Devices: {', '.join(device_ids)}")

                    flashing_lock_result = subprocess.run(["fastboot", "flashing", "get_unlock_ability"], capture_output=True, text=True)
                    if flashing_lock_result.returncode == 0:
                        flashing_lock_status = "locked" if "get_unlock_ability: 0" in flashing_lock_result.stdout else "Unlocked"
                        self.flashing_lock_label.setText(f"Flashing: {flashing_lock_status}")
                    else:
                        self.flashing_lock_label.setText("Flashing: Unknown")
                else:
                    self.fastboot_devices_label.setText("Fastboot Devices: No devices found")
                    self.flashing_lock_label.setText("Flashing Lock: Unknown")
            else:
                self.fastboot_devices_label.setText("Fastboot Devices: Unexpected error")
                self.flashing_lock_label.setText("Flashing Lock: Unknown")
        except FileNotFoundError:
            self.fastboot_devices_label.setText("Fastboot: Not installed or properly configured")
            self.flashing_lock_label.setText("Flashing Lock: Unknown")

    def run_fastboot_command(self, command):
        self.status_label.setText(f"Executing Fastboot command: {command}")
        self.fastboot_thread = FastbootThread(command)
        self.fastboot_thread.command_finished.connect(self.fastboot_command_finished)
        self.fastboot_thread.start()

    def fastboot_command_finished(self, command, success, error_message):
        if success:
            QMessageBox.information(self, "Fastboot Command", f"Fastboot command '{command}' executed successfully.")
        else:
            QMessageBox.warning(self, "Fastboot Command", f"Fastboot command '{command}' failed:\n{error_message}")
        self.status_label.setText("Ready")

    def load_device_data(self, channel):
        if channel != "Select Channel":
            file_name = f"./device_data_{channel}.json"
            if os.path.exists(file_name):
                with open(file_name, "r") as file:
                    self.device_data[channel] = json.load(file)
            else:
                self.device_data[channel] = []
                self.refresh_data()

            self.update_device_combo_box()
            
    def update_device_combo_box(self):
        channel = self.channel_combo_box.currentText()
        if channel in self.device_data:
            device_names = sorted(set(item["device_name"] for item in self.device_data[channel]))
            
            self.combo_box.clear()
            self.combo_box.addItem("Select Device")
            self.combo_box.addItems(device_names)
            
            for i in range(1, self.combo_box.count()):
                device_name = self.combo_box.itemText(i)
                codename = next((item["code_name"] for item in self.device_data[channel] if item["device_name"] == device_name), "N/A")
                self.combo_box.setItemData(i, codename, Qt.ToolTipRole)

    def refresh_data(self):
        channel = self.channel_combo_box.currentText()
        if channel != "Select Channel":
            self.status_label.setText("Fetching data.")
            self.fetching_timer.start(500)
            self.refresh_thread = DataRefreshThread(channel)
            self.refresh_thread.data_refreshed.connect(self.update_data)
            self.refresh_thread.start()

    def update_fetching_dots(self):
        dots = "." * self.fetching_dots
        self.status_label.setText(f"Fetching data{dots}")
        self.fetching_dots = (self.fetching_dots + 1) % 4

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_data(self, device_data):
        self.fetching_timer.stop()
        channel = self.channel_combo_box.currentText()
        self.device_data[channel] = device_data
        self.update_device_combo_box()
        self.status_label.setText("Data fetched successfully")

    def update_table(self, index):
        channel = self.channel_combo_box.currentText()
        if channel in self.device_data:
            if index == 0:
                self.table_widget.setRowCount(0)
                return

            selected_device = self.combo_box.currentText()
            filtered_data = [item for item in self.device_data[channel] if item["device_name"] == selected_device]

            self.table_widget.setRowCount(len(filtered_data))

            for row, item in enumerate(filtered_data):
                version_item = QTableWidgetItem(item["version"])
                self.table_widget.setItem(row, 0, version_item)

                folder_name = f"{item['device_name']}_{item['version']}"

                if channel == "LineageOS":
                    if os.path.exists(folder_name):
                        button_text = "Install"
                        button_callback = lambda _, folder=folder_name: self.install_image(folder, channel)
                    else:
                        button_text = "Download"
                        button_callback = lambda _, item=item: self.download_lineageos_files(item)
                else:
                    if os.path.exists(folder_name):
                        button_text = "Install"
                        button_callback = lambda _, folder=folder_name: self.install_image(folder, channel)
                    else:
                        button_text = "Download"
                        button_callback = lambda _, url=item["link"], folder=folder_name: self.download_file(url, folder)

                download_button = QPushButton(button_text)
                if button_callback:
                    download_button.clicked.connect(button_callback)
                self.table_widget.setCellWidget(row, 1, download_button)

    def download_file(self, url, folder_name):
        self.status_label.setText("Downloading file...")
        self.download_thread = DownloadThread(url)
        self.download_thread.download_progress_updated.connect(self.update_download_progress)
        self.download_thread.download_completed.connect(lambda file_path: self.download_completed(file_path, folder_name))
        self.download_thread.start()
    
    def update_download_progress(self, progress):
        self.status_label.setText(f"Downloading file... {progress}%")

    def download_completed(self, file_path, folder_name):
        if file_path:
            self.status_label.setText(f"Download completed. File saved to: {file_path}")

            if zipfile.is_zipfile(file_path):
                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    zip_ref.extractall(folder_name)
                os.remove(file_path)
            else:
                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)
                
                new_path = os.path.join(folder_name, os.path.basename(file_path))
                os.rename(file_path, new_path)

            button = self.table_widget.cellWidget(self.table_widget.currentRow(), 1)
            button.setText("Install")
            button.clicked.disconnect()
            channel = self.channel_combo_box.currentText()
            button.clicked.connect(lambda: self.install_image(folder_name, channel))
        else:
            self.status_label.setText("Download failed.")

        self.start_next_download()

    def install_image(self, folder_name, channel):
        channel = self.channel_combo_box.currentText()

        warning_message = "Warning: Flashing a new image will wipe all data on your device and install a fresh image. " \
                        "Make sure your device is compatible with the image you are about to flash. " \
                        "Flashing an incompatible image may cause issues or render your device unusable. " \
                        "Additionally, ensure that you are able to upgrade or downgrade to the version you are flashing. " \
                        "Do you want to proceed with the installation?"

        reply = QMessageBox.question(self, "Installation Warning", warning_message,
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.start_flashing(folder_name, channel)
        else:
            self.status_label.setText("Installation canceled.")

    def start_flashing(self, folder_name, channel):
        install_pipeline = self.install_pipelines[channel]

        self.status_label.setText("Installing image...")
        self.flashing_thread = FlashingThread(folder_name, install_pipeline)
        self.flashing_thread.finished.connect(self.flashing_finished)
        self.flashing_thread.start()            
    
    def download_lineageos_files(self, item):
        device_name = item["device_name"]
        version = item["version"]
        files = item["files"]

        self.current_folder_name = f"{device_name}_{version}"
        os.makedirs(self.current_folder_name, exist_ok=True)

        self.download_queue = list(files.items())
        self.start_next_download()

    def start_next_download(self):
        if self.download_queue:
            file_name, url = self.download_queue.pop(0)
            self.status_label.setText(f"Downloading {file_name}...")
            self.download_thread = DownloadThread(url)
            self.download_thread.download_progress_updated.connect(self.update_download_progress)
            self.download_thread.download_completed.connect(
                lambda file_path: self.download_completed(file_path, self.current_folder_name)
            )
            self.download_thread.start()
        else:
            self.status_label.setText("All files downloaded.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = DeviceInfoGUI()
    gui.show()
    sys.exit(app.exec_())
