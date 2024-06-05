import os
import platform
from lineage_os import LineageOS

class InstallPipeline:
    def __init__(self, channel):
        self.channel = channel

    def install(self, folder_name):
        current_directory = os.getcwd()
        folder_path = os.path.join(current_directory, folder_name)

        if self.channel == "LineageOS":
            #return self.install_lineageos(folder_path)

        if platform.system() == "Windows":
            script_file = "flash-all.bat"
        else:
            script_file = "flash-all.sh"

        script_path = self.find_script(folder_path, script_file)

        if script_path:
            os.system(f"cd {os.path.dirname(script_path)} && {script_file}")
            return True
        else:
            return False

    def find_script(self, folder_path, script_name):
        for root, dirs, files in os.walk(folder_path):
            if script_name in files:
                return os.path.join(root, script_name)
        return None

    def install_lineageos(self, folder_path):
        success = True
        for filename, command in LineageOS.fastboot_commands:
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                print(f"{command} {file_path}")
                os.system(f"{command} {file_path}")
            else:
                print(f"No file found for {filename}")
                success = False
        return success
