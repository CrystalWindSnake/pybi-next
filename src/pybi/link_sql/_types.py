from typing import Dict, List
from typing_extensions import TypedDict


class TSqlMapValue(TypedDict):
    sql: str
    filters: Dict
    parents: List[str]


TSqlMap = Dict[str, TSqlMapValue]


class TExcludeFilter(TypedDict):
    view_name: str
    query_key: str
