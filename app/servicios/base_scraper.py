from abc import ABC, abstractmethod

class BaseScraper(ABC):


    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    @abstractmethod
    async def fetch(self, url: str) -> str:
        pass

    @abstractmethod
    async def close(self):
        pass