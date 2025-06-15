from dataclasses import dataclass
from typing import Any, Dict, List
from typing_extensions import TypedDict


class TSqlMapValue(TypedDict):
    sql: str
    filters: Dict
    parents: List[str]


TSqlMap = Dict[str, TSqlMapValue]


class TExcludeFilter(TypedDict):
    view_name: str
    query_key: str


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
