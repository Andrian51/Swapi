import pandas as pd
from interfaces import DataProcessor


class EntityProcessor(DataProcessor):
    def apply_filter(self, endpoint: str, columns_to_drop: list):
        pass

    def register_processor(self, entity: str, processor):
        pass


class PeopleProcessor(EntityProcessor):
    def process(self, json_data: list) -> pd.DataFrame:
        df = pd.DataFrame(json_data)
        df['full_name'] = df['name']
        return df


class PlanetsProcessor(EntityProcessor):
    def process(self, json_data: list) -> pd.DataFrame:
        df = pd.DataFrame(json_data)
        df['population'] = pd.to_numeric(df['population'], errors='coerce')
        return df
