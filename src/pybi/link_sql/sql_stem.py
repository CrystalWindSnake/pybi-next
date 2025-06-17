from contextvars import ContextVar
import re
from typing import Dict, List, Set
from pybi.systems.graph_system import topological_sort_kahn
from pybi.link_sql import _const, _types

view_id_count: ContextVar[int] = ContextVar("view_id_count", default=0)
query_id_count: ContextVar[int] = ContextVar("query_id_count", default=0)

_name_pattern = re.compile(r"'@_[vq]\d+_@'")


def gen_view_name():
    view_id_count.set(view_id_count.get() + 1)
    return f"'@_v{view_id_count.get()}_@'"


def gen_query_name():
    query_id_count.set(query_id_count.get() + 1)
    return f"'@_q{query_id_count.get()}_@'"


def get_source_type(name: str) -> _const.TSourceType:
    if name.startswith("'@_v"):
        return "view"

    return "query"


def iter_extract_names(sql: str):
    return (m.group() for m in _name_pattern.finditer(sql))


def extract_names(sql: str):
    return list(set(m.group() for m in _name_pattern.finditer(sql)))


def get_upstream_dataview_names(target_name: str, sql_map: _types.TSqlMap):
    stack = [target_name]
    views: Set[str] = set()

    while stack:
        name = stack.pop()
        if get_source_type(name) == "view":
            views.add(name)
        sql = sql_map[name]["sql"]
        stack.extend(
            name for name in extract_names(sql) if get_source_type(name) == "view"
        )

    return list(views)


def extract_any_view_name(sql: str, sql_map: _types.TSqlMap):
    stack = [sql]

    while stack:
        sql = stack.pop()
        for name in iter_extract_names(sql):
            if get_source_type(name) == "view":
                return name

            stack.append(sql_map[name]["sql"])

    raise ValueError(f"No view name found in sql[{sql}]")


def get_sql_execution_order(sql_map: _types.TSqlMap):
    graph = {name: extract_names(value["sql"]) for name, value in sql_map.items()}
    return topological_sort_kahn(graph)


def build_sql(
    *,
    main_query_name: str,
    filters: List,
    sql_map: Dict[str, _types.TSqlMapValue],
    sql_orders: Dict[str, int],
):
    """
    main_query_name='@_q1_@',
    filters=[{'view': "'@_v3_@'", 'filters': {'f1': {'expr': 'Name = ?', 'value': 'foo1'}}}, {'view': "'@_v1_@'", 'filters': {}}],
    sql_map={'@_v1_@': {'sql':'select * from df',}, '@_q1_@': 'SELECT DISTINCT name FROM @_v1_@'},
    sql_orders=['@_v1_@' :2, '@_q1_@':1]
    """

    view2filters = {f["view"]: f["filters"] for f in filters}

    orders_without_main = _get_orders_without_main(sql_orders, main_query_name)
    params = []

    cte_query = [
        f"{name} AS ({_sql_with_filters(name, view2filters, sql_map=sql_map, params=params)})"
        for name in orders_without_main
    ]

    cte_stem = "WITH " + ", ".join(cte_query) if cte_query else ""

    return (
        f"{cte_stem}{_sql_with_filters(main_query_name, view2filters, sql_map=sql_map, params=params)}",
        params,
    )


def _get_orders_without_main(sql_orders: Dict[str, int], target_query_name: str):
    target_level = sql_orders[target_query_name]
    return [name for name, level in sql_orders.items() if level > target_level]


def _sql_with_filters(
    name: str, filters: Dict, *, sql_map: Dict[str, _types.TSqlMapValue], params: List
) -> str:
    filter = filters.get(name, {})
    where_stem = ""
    if filter:
        where_stem = " WHERE " + " AND ".join(v["expr"] for v in filter.values())
        params.extend(v["value"] for v in filter.values())

    sql = sql_map[name]["sql"]
    if not where_stem:
        return sql

    return f"SELECT * FROM ({sql}){where_stem}"
