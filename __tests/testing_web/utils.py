from pathlib import Path
import os
import re
import pandas as pd
import duckdb

from __tests.testing_web.context import Context

__DIR__ = Path(__file__).parent / ".dataset"

__DIR__.mkdir(exist_ok=True)


def create_duckdb_file(filename: str, table_name: str, df: pd.DataFrame):
    file_path = __DIR__ / filename
    if file_path.exists():
        os.remove(file_path)

    with duckdb.connect(file_path) as conn:
        conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")

    return file_path
