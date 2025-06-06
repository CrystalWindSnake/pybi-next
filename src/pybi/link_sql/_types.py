from dataclasses import dataclass
from typing import Any, Dict, List, Literal
from typing_extensions import TypedDict


class TFilterInfo(TypedDict):
    expr: str
    value: Any


TFilters = Dict[str, List[TFilterInfo]]
TQueryReturnType = Literal["records", "columns", "values", "flat_values"]


class TQueryStrInfo(TypedDict):
    sql: str
    params: List[Any]


@dataclass
class DependencyInfo:
    view_names: List[str]
    filters: List
