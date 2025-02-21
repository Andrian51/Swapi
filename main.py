import pandas as pd
import requests
import logging
import os
import argparse

# Налаштування логера
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Базовий клієнт для роботи з API
class SWAPIClient:
    def __init__(self, path: str):
        self.base_url = path

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


# Клієнт для роботи з даними з Excel
class ExcelSWAPIClient(SWAPIClient):
    def __init__(self, path: str):
        """
        Ініціалізація з шляхом до Excel-файлу.
        """
        super().__init__(path)
        self.data = pd.read_excel(path, sheet_name=None)

    def fetch_json(self, endpoint: str) -> list:
        """
        Завантажує дані з Excel-файлу для вказаного endpoint.

        :param endpoint: Назва листа в Excel (наприклад, "people")
        :return: список всіх сутностей у вигляді JSON
        """
        if endpoint not in self.data:
            logger.warning(f"Endpoint {endpoint} not found in {self.path}")
            return []

        return self.data[endpoint].to_dict(orient='records')


# Менеджер даних
class SWAPIDataManager:
    def __init__(self, client):
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


# Функція для вибору клієнта
def get_client(input_source: str):
    if input_source.startswith("http"):
        return SWAPIClient(input_source)
    elif input_source.endswith(".xlsx"):
        return ExcelSWAPIClient(input_source)
    else:
        raise ValueError("Невідомий формат джерела даних")


# Основна функція
def main():
    parser = argparse.ArgumentParser(description="SWAPI Data Manager")
    parser.add_argument('--input', required=True, help="URL або шлях до Excel файлу")
    parser.add_argument('--endpoint', required=True, help="Кома-розділений список endpoint'ів")
    parser.add_argument('--output', required=True, help="Шлях до вихідного Excel файлу")

    args = parser.parse_args()

    # Вибір клієнта для підключення до джерела
    client = get_client(args.input)
    manager = SWAPIDataManager(client)

    # Завантаження даних з зазначених endpoint'ів
    for endpoint in args.endpoint.split(','):
        manager.fetch_entity(endpoint)

    # Запис результатів у Excel файл
    manager.save_to_excel(args.output)


if __name__ == "__main__":
    main()
