from abc import ABC, abstractmethod
import pandas as pd


class DataFetcher(ABC):
    @abstractmethod
    def fetch_entity(self, endpoint: str):
        pass


class DataProviderInterface(ABC):
    @abstractmethod
    def fetch_data(self, endpoint: str):
        pass


class DataProcessor(ABC):
    @abstractmethod
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        pass


class DataSaver(ABC):
    @abstractmethod
    def save(self, data: pd.DataFrame, filename: str):
        pass
