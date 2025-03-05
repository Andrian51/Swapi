import argparse
import pandas as pd
from interfaces import DataFetcher, DataProcessor, DataSaver, DataProviderInterface
from clients import SWAPIClient, ExcelSWAPIClient
from processors import PeopleProcessor, PlanetsProcessor
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class SWAPIDataManager:
    def __init__(self, data_provider: DataProviderInterface, processors: dict = None, saver: DataSaver = None):
        self.data_provider = data_provider  # Тепер залежність від абстракції
        self.data = {}
        self.processors = processors if processors else {}
        self.saver = saver

    def fetch_entity(self, endpoint: str):
        raw_data = self.data_provider.fetch_data(endpoint)  # Використовуємо абстракцію
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

    def process_data(self, endpoint: str):
        if endpoint in self.processors:
            processor = self.processors[endpoint]
            self.data[endpoint] = processor.process(self.data[endpoint])

    def save_to_file(self, filename: str):
        if self.saver:
            for endpoint, df in self.data.items():
                self.saver.save(df, filename)
                logger.info(f"Збережено дані {endpoint} в таблицю.")
        else:
            logger.error("DataSaver не визначено.")

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

    # Визначаємо джерело даних
    if args.input.startswith('http'):
        data_provider = SWAPIClient(path=args.input)
    else:
        data_provider = ExcelSWAPIClient(path=args.input)

    manager = SWAPIDataManager(data_provider)

    # Реєструємо процесори
    manager.register_processor("people", PeopleProcessor())
    manager.register_processor("planets", PlanetsProcessor())

    # Отримуємо дані з вказаних endpoint-ів
    endpoints = args.endpoint.split(',')
    for endpoint in endpoints:
        manager.fetch_entity(endpoint)

    # Зберігаємо результат в Excel
    manager.save_to_excel(args.output)

    logger.info("Процес завершено.")


if __name__ == "__main__":
    main()
