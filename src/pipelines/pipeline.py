from abc import ABC, abstractmethod

class Pipeline(ABC):
    @abstractmethod
    def install(self, folder_name):
        pass