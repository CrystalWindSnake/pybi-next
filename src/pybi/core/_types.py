from __future__ import annotations
from typing import Any, Literal, TypedDict

TDatasetId = str
TDataViewId = str
TQueryId = str

TSqlId = TDataViewId | TQueryId
TComponentId = str

TSqlType = Literal["query", "data_view"]


class DataSetQueryInfo(TypedDict, total=True):
    columns: list[str]
    values: list[list[Any]]
