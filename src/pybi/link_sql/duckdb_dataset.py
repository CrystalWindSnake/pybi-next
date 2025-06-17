from pathlib import Path
from typing import Dict, List, Optional

from pybi.link_sql import data_set_store
from pybi.link_sql._mixin import DataSetMixin
from pybi.link_sql.data_view import DataView

try:
    import pandas
    import duckdb
except ImportError as e:
    raise e


class DuckdbDataFrameDataSet(DataSetMixin):
    def __init__(self, dataframes: Optional[Dict[str, "pandas.DataFrame"]] = None):
        super().__init__()
        self._conn = duckdb.connect(":default:", read_only=False)
        self._id = data_set_store.store_data_set(self)

        self.import_dataframe(dataframes or {})

    def import_dataframe(self, dataframes: Dict[str, "pandas.DataFrame"]):
        for name, df in dataframes.items():
            _dataframe_import_to_db(self._conn, df, name)

    def get_id(self) -> int:
        return self._id

    def __getitem__(self, table: str):
        return DataView(f"select * from {table}", dataset=self)

    def query(self, sql: str, params: Optional[List] = None):
        return _query(self._conn, sql, params)


class DuckdbFileDataSet(DataSetMixin):
    def __init__(self, file: Path):
        super().__init__()
        self._conn = duckdb.connect(file, read_only=True)
        self._id = data_set_store.store_data_set(self)

    def get_id(self) -> int:
        return self._id

    def __getitem__(self, table: str):
        return DataView(f"select * from {table}", dataset=self)

    def query(self, sql: str, params: Optional[List] = None):
        return _query(self._conn, sql, params)


def _dataframe_import_to_db(
    conn: duckdb.DuckDBPyConnection, df: "pandas.DataFrame", table_name: str
):
    cursor = conn.cursor()
    cursor.execute(f"create table if not exists {table_name} as select * from df")


def _query(conn: duckdb.DuckDBPyConnection, sql: str, params: Optional[List] = None):
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


class Facade:
    def __call__(self, db: Path):
        """
        Create a DuckdbFileDataSet instance from a database file path.

        Args:
            db (Path): Path to the DuckDB database file.

        Examples:
        .. code-block:: python
        ds = pybi.duckdb("path/to/database.db")
        """
        self.db = db
        return DuckdbFileDataSet(db)

    @classmethod
    def from_pandas(
        cls, dataframes_map: Optional[Dict[str, "pandas.DataFrame"]] = None
    ) -> DuckdbDataFrameDataSet:
        ds = DuckdbDataFrameDataSet(dataframes_map or {})
        return ds


_facade = Facade()
