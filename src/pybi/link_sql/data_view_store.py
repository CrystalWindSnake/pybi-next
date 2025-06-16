from __future__ import annotations
from contextvars import ContextVar
from typing import Any, Dict, TYPE_CHECKING, Optional
from instaui import ui
from instaui.components.element import Element
from collections import defaultdict
from pybi.link_sql import sql_stem
from pybi.link_sql import _types

if TYPE_CHECKING:
    from pybi.link_sql.data_view import DataView

_TViewName = str


class Store(Element, esm="./data_view_store.js"):
    _store_context: ContextVar[Optional[Store]] = ContextVar(
        "_store_context", default=None
    )

    def __init__(self):
        super().__init__()
        self._sql_map: _types.TSqlMap = {}
        self._notify_list: Dict[str, Any] = {}
        self._notify_count: int = 0
        self.sql_orders = ui.data({})
        self.sql_map: _types.TSqlMap = ui.state({})
        self._field_query_id_count: Dict[str, int] = defaultdict(lambda: 0)
        self._view_obj_map: Dict[_TViewName, DataView] = {}

        self._element_ref = ui.element_ref()
        self.element_ref(self._element_ref)

        self.on(
            "update:sql_map",
            ui.js_event(
                inputs=[ui.event_context.e()], outputs=[self.sql_map], code="e=>e"
            ),
        )

        self._add_filters_js_handler = ui.js_fn(r"""(filters, query_key, args)=> {
            return {method: 'addFilter', args: [filters, query_key, args]}
    }""")
        """
        Example:
            addFilter('view_name', 'query_key', {expr: 'Name = ?', value: 'foo1'})
        """

        self._remove_filters_js_handler = ui.js_fn(r"""(filters, query_key)=> {
            return {method: 'removeFilter', args: [filters, query_key]}
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

    def build_related_filters(
        self,
        source_name: str,
        *,
        exclude_filter: Optional[_types.TExcludeFilter] = None,
    ):
        exclude_infos = []
        if exclude_filter:
            exclude_infos.append(
                {
                    "view": exclude_filter["view_name"],
                    "keys": [exclude_filter["query_key"]],
                }
            )

        id = f"n{self._notify_count}"
        self._notify_list[id] = {
            "source": source_name,
            "exclude_infos": exclude_infos,
        }
        self._notify_count += 1

        data = ui.state({}, deep_compare=True)

        on_notify = ui.js_event(
            inputs=[ui.event_context.e()], outputs=[data], code="e=>e"
        )

        self.on(f"notify:{id}", on_notify)

        return data

    def get_view(self, view_name: str) -> DataView:
        return self._view_obj_map[view_name]

    def store_query(self, sql: str):
        query_name = sql_stem.gen_query_name()
        self._sql_map[query_name] = {
            "sql": sql,
            "filters": {},
            "parents": sql_stem.extract_names(sql),
        }
        return query_name

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
        self.props({"sql_map": self._sql_map, "notify_list": self._notify_list})
        self.sql_orders.value = sql_stem.get_sql_execution_order(self._sql_map)
        return super()._to_json_dict()


def get_store():
    return Store.get()
