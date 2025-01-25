import pandas as pd
import requests
import logging

# Налаштування логера
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class SWAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def fetch_json(self, endpoint: str) -> list:
        all_data = []
        url = f"{self.base_url}{endpoint}"

        while url:
            logger.info(f"Отримання даних з: {url}")
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            all_data.extend(data['results'])
            url = data.get('next')

        return all_data


class SWAPIDataManager:
    def __init__(self, client: SWAPIClient):
        self.client = client
        self.data = {}

    def fetch_entity(self, endpoint: str):
        logger.info(f"Завантаження даних для endpoint: {endpoint}")
        self.data[endpoint] = pd.DataFrame(self.client.fetch_json(endpoint))

    def apply_filter(self, endpoint: str, columns_to_drop: list):
        if endpoint in self.data:
            logger.info(f"Видалення стовпців {columns_to_drop} з endpoint: {endpoint}")
            self.data[endpoint].drop(columns=columns_to_drop, inplace=True)
        else:
            logger.warning(f"Дані для endpoint {endpoint} не знайдено.")

    def save_to_excel(self, filename: str):
        logger.info(f"Запис даних у Excel файл: {filename}")
        with pd.ExcelWriter(filename) as writer:
            for endpoint, dataframe in self.data.items():
                sheet_name = endpoint.rstrip('/')
                dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
        logger.info("Дані успішно записано у Excel.")


client = SWAPIClient(base_url="https://swapi.dev/api/")
manager = SWAPIDataManager(client)

manager.fetch_entity("people")
manager.fetch_entity("planets")

manager.apply_filter("people", ["films", "species"])

manager.save_to_excel("swapi_data.xlsx")
