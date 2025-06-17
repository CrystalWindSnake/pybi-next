from __future__ import annotations
from typing import Dict, Literal, Optional
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from instaui.vars.mixin_types.observable import ObservableMixin

from pybi.link_sql import _server_query
from pybi.link_sql.data_view_store import get_store
from ._mixin import DataColumnMixin, QueryResultMixin


class DataViewColumn(
    DataColumnMixin, QueryResultMixin, ObservableMixin, ElementBindingMixin
):
    def __init__(self, source_name: str, field: str) -> None:
        self._source_name = source_name
        self.__field = field

        query_name = get_store().gen_query(f"SELECT {field} FROM {source_name}")
        self.__source = _server_query.create_source(query_name)

    @property
    def field(self) -> str:
        return self.__field

    @property
    def source_name(self) -> str:
        return self._source_name

    def get_source_type(self):
        return "view"

    def _to_element_binding_config(self) -> Dict:
        return self.__source.flat_values()._to_element_binding_config()

    def _to_observable_config(self):
        return self.__source.flat_values()._to_observable_config()

    def flat_values(
        self,
    ):
        return self.__source.flat_values()

    def distinct(self, *, order_by: Optional[Literal["ASC", "DESC"]] = None):
        sql = f"SELECT DISTINCT {self.field} FROM {self.source_name}{f' ORDER BY {self.field} {order_by}' if order_by else ''}"
        query_name = get_store().gen_query(sql)
        return _server_query.create_source(query_name).flat_values()


class DataQueryColumn(
    DataColumnMixin, QueryResultMixin, ObservableMixin, ElementBindingMixin
):
    def __init__(self, source_name: str, field: str) -> None:
        self._source_name = source_name
        self.__field = field
        self._sql = f"SELECT {field} FROM {source_name}"

        query_name = get_store().gen_query(self._sql)
        self.__source = _server_query.create_source(query_name)

    def _to_element_binding_config(self) -> Dict:
        return self.__source.flat_values()._to_element_binding_config()

    def _to_observable_config(self):
        return self.__source.flat_values()._to_observable_config()

    def flat_values(
        self,
    ):
        return self.__source.flat_values()

    @property
    def field(self) -> str:
        return self.__field

    @property
    def source_name(self) -> str:
        return self._source_name

    def get_source_type(self):
        return "query"

    def distinct(self, *, order_by: Optional[Literal["ASC", "DESC"]] = None):
        sql = f"SELECT DISTINCT {self.field} FROM {self.source_name}{f' ORDER BY {self.field} {order_by}' if order_by else ''}"
        query_name = get_store().gen_query(sql)
        return _server_query.create_source(query_name).flat_values()
