from abc import ABC, abstractmethod


class DataFetcher(ABC):
    @abstractmethod
    def fetch_entity(self, endpoint: str):
        pass


class DataProcessor(ABC):
    @abstractmethod
    def apply_filter(self, endpoint: str, columns_to_drop: list):
        pass

    def register_processor(self, entity: str, processor=None):
        pass


class DataSaver(ABC):
    @abstractmethod
    def save_to_excel(self, filename: str):
        pass
