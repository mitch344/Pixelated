import subprocess
from PyQt5.QtCore import QThread, pyqtSignal

class FastbootThread(QThread):
    command_finished = pyqtSignal(str, bool, str)

    def __init__(self, command, timeout=10):
        super().__init__()
        self.command = command
        self.timeout = timeout

    def run(self):
        try:
            result = subprocess.run(["fastboot", self.command], capture_output=True, text=True, timeout=self.timeout)
            if result.returncode == 0:
                self.command_finished.emit(self.command, True, "")
            else:
                error_message = result.stderr.strip()
                self.command_finished.emit(self.command, False, error_message)
        except subprocess.TimeoutExpired:
            self.command_finished.emit(self.command, False, f"Timeout expired after {self.timeout} seconds. The device may not be in bootloader mode.")
        except FileNotFoundError:
            self.command_finished.emit(self.command, False, "Fastboot is not installed or properly configured.")