from __future__ import annotations
from contextvars import ContextVar
from typing import Any, Dict, TYPE_CHECKING, Optional, cast
from instaui import ui
from instaui.components.element import Element
from instaui.vars.state import RefProxy
from collections import defaultdict
from pybi.link_sql import sql_stem


if TYPE_CHECKING:
    from pybi.link_sql.data_view import DataView

_TViewName = str
_TFilter = Dict[str, Any]


class Store(Element):
    _store_context: ContextVar[Optional[Store]] = ContextVar(
        "_store_context", default=None
    )

    def __init__(self):
        super().__init__("template")
        self._sql_map: Dict[str, str] = {}
        self._view_filters: Dict[_TViewName, _TFilter] = {}
        self.sql_orders = ui.data({})
        self.sql_map = ui.state({})
        self._field_query_id_count: Dict[str, int] = defaultdict(lambda: 0)
        self._view_obj_map: Dict[_TViewName, DataView] = {}

    @property
    def server_sql_map(self):
        return self._sql_map

    def gen_field_query_id(self, field: str):
        self._field_query_id_count[field] += 1
        return self._field_query_id_count[field]

    def store_view(self, view: DataView, sql: str):
        self._sql_map[view.name] = sql
        self._view_filters[view.name] = ui.state({})
        self._view_obj_map[view.name] = view

    def get_view(self, view_name: str) -> DataView:
        return self._view_obj_map[view_name]

    def store_query(self, query_name: str, sql: str):
        self._sql_map[query_name] = sql

    def get_filters(self, view_name: str):
        assert view_name in self._view_filters, f"{view_name} not found"
        return self._view_filters[view_name]

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
