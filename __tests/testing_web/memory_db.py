from typing import Dict
from pybi.link_sql.duckdb_dataset import DuckdbDataFrameDataSet


try:
    import pandas
except ImportError as e:
    raise e


class MemoryDb:
    def __init__(self):
        self.ds = DuckdbDataFrameDataSet()

    def clear(self):
        conn = self.ds._conn

        tables = [
            n[0]
            for n in conn.execute("SELECT table_name FROM duckdb_tables()").fetchall()
        ]
        for table_name in tables:
            conn.execute(f"DROP TABLE IF EXISTS {table_name};")

    def from_dataframe(
        self, dataframes_map: Dict[str, "pandas.DataFrame"]
    ) -> DuckdbDataFrameDataSet:
        self.ds.import_dataframe(dataframes_map)
        return self.ds
