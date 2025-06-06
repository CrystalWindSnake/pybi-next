from dataclasses import dataclass
from typing import Any, Dict, List
from typing_extensions import TypedDict


class TFilterInfo(TypedDict):
    expr: str
    value: Any


TFilters = Dict[str, List[TFilterInfo]]


class TQueryStrInfo(TypedDict):
    sql: str
    params: List[Any]


@dataclass
class DependencyInfo:
    view_names: List[str]
    filters: List
