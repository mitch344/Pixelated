import os
import platform
from pipelines.pipeline import Pipeline

class StockPipeline(Pipeline):
    def install(self, folder_name):
        current_directory = os.getcwd()
        folder_path = os.path.join(current_directory, folder_name)

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