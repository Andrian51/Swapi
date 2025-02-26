import argparse
import pandas as pd
from interfaces import DataFetcher, DataProcessor, DataSaver
from clients import SWAPIClient, ExcelSWAPIClient
from processors import PeopleProcessor, PlanetsProcessor
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class SWAPIDataManager(DataFetcher, DataProcessor, DataSaver):
    def __init__(self, client: DataFetcher):
        self.client = client
        self.data = {}
        self.processors = {}

    def fetch_entity(self, endpoint: str):
        raw_data = self.client.fetch_entity(endpoint)
        self.data[endpoint] = pd.DataFrame(raw_data)
        logger.info(f"Отримано {len(raw_data)} записів для {endpoint}")

    def register_processor(self, entity: str, processor: DataProcessor):
        self.processors[entity] = processor

    def apply_filter(self, endpoint: str, columns_to_drop: list):
        if endpoint in self.data:
            self.data[endpoint] = self.data[endpoint].drop(columns=columns_to_drop, errors='ignore')
            logger.info(f"Застосовано фільтр для {endpoint}, видалено стовпці: {columns_to_drop}")
        else:
            logger.warning(f"Дані для {endpoint} не знайдено.")

    def save_to_excel(self, filename: str):
        with pd.ExcelWriter(filename) as writer:
            for endpoint, df in self.data.items():
                df.to_excel(writer, sheet_name=endpoint, index=False)
                logger.info(f"Збережено дані {endpoint} в таблицю.")
        logger.info(f"Дані успішно збережено в {filename}.")


def main():
    parser = argparse.ArgumentParser(description="SWAPI Data Manager")
    parser.add_argument('--input', required=True, help="URL або шлях до .xlsx файлу")
    parser.add_argument('--endpoint', required=True,
                        help="Кома розділені імена endpoint-ів (наприклад, 'people,planets')")
    parser.add_argument('--output', required=True, help="Шлях до файлу для збереження результатів")

    args = parser.parse_args()

    if args.input.startswith('http'):
        client = SWAPIClient(path=args.input)
    else:
        client = ExcelSWAPIClient(path=args.input)

    manager = SWAPIDataManager(client)

    manager.register_processor("people", PeopleProcessor())
    manager.register_processor("planets", PlanetsProcessor())

    endpoints = args.endpoint.split(',')
    for endpoint in endpoints:
        manager.fetch_entity(endpoint)

    manager.save_to_excel(args.output)

    logger.info("Процес завершено.")


if __name__ == "__main__":
    main()