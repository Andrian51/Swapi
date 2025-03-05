import pandas as pd
import requests
from interfaces import DataFetcher, DataProviderInterface
import logging
from interfaces import DataSaver

logger = logging.getLogger(__name__)


class SWAPIClient(DataProviderInterface):
    def __init__(self, path: str):
        self.path = path

    def fetch_data(self, endpoint: str):
        url = f"{self.path}/{endpoint}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['results']


class ExcelSWAPIClient(DataProviderInterface):
    def __init__(self, path: str):
        self.path = path

    def fetch_data(self, endpoint: str):
        return pd.read_excel(self.path, sheet_name=endpoint).to_dict(orient="records")


class ExcelDataSaver(DataSaver):
    def save(self, data: pd.DataFrame, filename: str):
        with pd.ExcelWriter(filename) as writer:
            data.to_excel(writer, index=False)
