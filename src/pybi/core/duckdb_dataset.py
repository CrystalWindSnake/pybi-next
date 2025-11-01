from pathlib import Path
from typing import Dict, List, Optional
from pybi.core._mixins import DataSetMixin
from pybi.core._types import TDatasetId
from pybi.core.data_view import DataView
from pybi.core import _dataset_store

try:
    import pandas
    import duckdb
except ImportError as e:
    raise e


class DuckdbDataFrameDataSet(DataSetMixin):
    def __init__(self, dataframes: Optional[Dict[str, "pandas.DataFrame"]] = None):
        super().__init__()
        self._conn = duckdb.connect(":default:", read_only=False)
        self.import_dataframe(dataframes or {})
        self._id = _dataset_store.register_dataset(self)

    @property
    def id(self) -> TDatasetId:
        return self._id

    def import_dataframe(self, dataframes: Dict[str, "pandas.DataFrame"]):
        for name, df in dataframes.items():
            _dataframe_import_to_db(self._conn, df, name)

    def __getitem__(self, table: str):
        return DataView(
            f"select * from {table}",
            dataset=self,
        )

    def query(self, sql: str, params: Optional[List] = None):
        return _query(self._conn, sql, params)


class DuckdbFileDataSet(DataSetMixin):
    def __init__(self, file: Path):
        super().__init__()
        self._conn = duckdb.connect(file, read_only=True)
        self._id = _dataset_store.register_dataset(self)

    def __getitem__(self, table: str):
        return DataView(f"select * from {table}", dataset=self)

    @property
    def id(self) -> TDatasetId:
        return self._id

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
