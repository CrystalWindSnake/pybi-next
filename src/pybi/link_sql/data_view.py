from __future__ import annotations
from contextvars import ContextVar
from typing import Any, Dict, List, Optional, cast
from typing_extensions import overload
from instaui import ui
from instaui.components.element import Element
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from instaui.vars.mixin_types.observable import ObservableMixin
from instaui.vars.state import RefProxy
from collections import defaultdict
from pybi.link_sql import sql_stem
from .data_column import DataViewColumn

from pybi.link_sql._mixin import (
    CanGetitem,
    DataColumnMixin,
    QueryableMixin,
    DataSetMixin,
)

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
        self.sql_orders = ui.data([])
        self.sql_map = ui.state({})
        self._field_query_id_count: Dict[str, int] = defaultdict(lambda: 0)
        self._view_obj_map: Dict[_TViewName, DataView] = {}

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


class DataView(QueryableMixin, ElementBindingMixin, ObservableMixin):
    def __init__(self, sql: str, *, dataset: Optional[DataSetMixin] = None):
        self.__sql = sql
        self.__name = sql_stem.gen_view_name()
        get_store().store_view(self, sql)
        self._dataset_id = self.__try_get_dataset_id(dataset, sql)

    def __try_get_dataset_id(self, dataset: Optional[DataSetMixin], sql: str):
        if dataset is None:
            for name in sql_stem.iter_extract_names(sql):
                if sql_stem.get_source_type(name) == "view":
                    return get_store().get_view(name).dataset_id

            raise ValueError("dataset is None and no view found in sql")

        return dataset.get_id()

    @property
    def name(self) -> str:
        return self.__name

    @property
    def dataset_id(self) -> int:
        return self._dataset_id

    def _to_observable_config(self):
        raise NotImplementedError

    def _to_element_binding_config(self) -> Dict:
        raise NotImplementedError

    def _to_sql(
        self,
    ):
        raise NotImplementedError

    @overload
    def __getitem__(self, field: List[str]): ...

    @overload
    def __getitem__(self, field: str) -> DataColumnMixin: ...

    def __getitem__(self, field: str | List[str]) -> DataColumnMixin:
        if isinstance(field, str):
            return DataViewColumn(self.__name, field)

        raise NotImplementedError

    @property
    def result(self) -> CanGetitem:
        raise NotImplementedError

    def flat_values(
        self,
    ):
        raise NotImplementedError

    def __str__(self) -> str:
        return self.name


def data_view(sql: str) -> DataView:
    return DataView(sql)


def get_store():
    return Store.get()
