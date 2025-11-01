from typing import Optional, Union
import pandas as pd
import duckdb

from ._mixins import TableSetMixin
from .data_view import DataView
from ._component_store import ComponentStore


class PandasTableSet(TableSetMixin):
    def __init__(self, dataframes: dict[str, pd.DataFrame]):
        self._component_store = ComponentStore()
        self._table_names = set(dataframes.keys())
        self._conn = duckdb.connect(":default:", read_only=False)

        for name, df in dataframes.items():
            _dataframe_import_to_db(self._conn, df, name)

    def query_table(self, sql: str):
        return _query(self._conn, sql)

    def __getitem__(self, table: str) -> DataView:
        assert table in self._table_names, f"table {table} not found in table set"
        return DataView(
            f"select * from {table}",
            component_store=self._component_store,
            table_set=self,
        )


def from_pandas(dataframes: Union[pd.DataFrame, dict[str, pd.DataFrame]]):
    dataframes = dataframes if isinstance(dataframes, dict) else {"default": dataframes}
    return PandasTableSet(dataframes)


def _dataframe_import_to_db(
    conn: duckdb.DuckDBPyConnection, df: pd.DataFrame, table_name: str
):
    cursor = conn.cursor()
    cursor.execute(f"create table if not exists {table_name} as select * from df")


def _query(conn: duckdb.DuckDBPyConnection, sql: str, params: Optional[list] = None):
    local_con = conn.cursor()

    try:
        query = local_con.sql(sql, params=params)
        columns = query.columns
        values = query.fetchall()
    except duckdb.ParserException as e:
        raise ValueError(f"Invalid SQL:{e}. {sql=} , {params=}") from e

    return {
        "columns": columns,
        "values": values,
    }
