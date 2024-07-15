from abc import ABC, abstractmethod

class BaseChatLogsManager(ABC):
    @abstractmethod
    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def log(self, **kwargs) -> None:
        pass