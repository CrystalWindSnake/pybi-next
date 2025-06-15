from __future__ import annotations
from contextvars import ContextVar
from typing import Any, Dict, TYPE_CHECKING, Optional, cast
from instaui import ui
from instaui.components.element import Element
from instaui.vars.state import RefProxy
from collections import defaultdict
from pybi.link_sql import sql_stem
from pybi.link_sql import _types

if TYPE_CHECKING:
    from pybi.link_sql.data_view import DataView

_TViewName = str


class Store(Element):
    _store_context: ContextVar[Optional[Store]] = ContextVar(
        "_store_context", default=None
    )

    def __init__(self):
        super().__init__("template")
        self._sql_map: _types.TSqlMap = {}
        self.sql_orders = ui.data({})
        self.sql_map: _types.TSqlMap = ui.state({})
        self._field_query_id_count: Dict[str, int] = defaultdict(lambda: 0)
        self._view_obj_map: Dict[_TViewName, DataView] = {}

        self._add_filters_js_handler = ui.js_fn(r"""(filters, query_key, args)=> {
            return {...filters, [query_key]: args}   
    }""")

        self._remove_filters_js_handler = ui.js_fn(r"""(filters, query_key)=> {
            const {[query_key]:_, ...rest} = filters
            return rest
    }""")

    @property
    def server_sql_map(self):
        return self._sql_map

    def get_sql(self, name: str):
        return self._sql_map[name]["sql"]

    def gen_field_query_id(self, field: str):
        self._field_query_id_count[field] += 1
        return self._field_query_id_count[field]

    def store_view(self, view: DataView, sql: str):
        self._sql_map[view.name] = {
            "sql": sql,
            "filters": {},
            "parents": sql_stem.extract_names(sql),
        }
        self._view_obj_map[view.name] = view

    def get_view(self, view_name: str) -> DataView:
        return self._view_obj_map[view_name]

    def store_query(self, query_name: str, sql: str):
        self._sql_map[query_name] = {
            "sql": sql,
            "filters": {},
            "parents": sql_stem.extract_names(sql),
        }

    def get_filters(self, view_name: str):
        return self.sql_map[view_name]["filters"]

    @classmethod
    def get(cls) -> Store:
        dv = cls._store_context.get()
        if dv is None:
            dv = cls()
            cls._store_context.set(dv)

        return cls._store_context.get()  # type: ignore

    def _to_json_dict(self):
        cast(RefProxy, self.sql_map)._ref_.value = self._sql_map
        self.sql_orders.value = sql_stem.get_sql_execution_order(self._sql_map)
        return super()._to_json_dict()


def get_store():
    return Store.get()
