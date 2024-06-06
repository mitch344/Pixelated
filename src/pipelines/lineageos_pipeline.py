from pipelines.pipeline import Pipeline

class LineageOSPipeline(Pipeline):
    def install(self, folder_name):
        print("LineageOS")
        return True