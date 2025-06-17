from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from instaui.vars.mixin_types.observable import ObservableMixin
from ._mixin import DataTableMixin
from pybi.link_sql.data_view_store import get_store
from pybi.link_sql import _server_query

if TYPE_CHECKING:
    from .data_view import DataView
    from .query import Query


class DataViewTable(DataTableMixin, ObservableMixin, ElementBindingMixin):
    def __init__(
        self, data_view: DataView, fields: Optional[Sequence[str]] = None
    ) -> None:
        if fields:
            sql = f"SELECT {', '.join(fields)} FROM {data_view.name}"
            query_name = get_store().gen_query(sql)
        else:
            query_name = data_view.name

        self.__source_name = query_name
        self.__dataset_id = data_view.dataset_id

        self.__source = _server_query.create_source(query_name)

    def get_query_name(self) -> str:
        return self.__source_name

    @property
    def source_name(self) -> str:
        return self.__source_name

    def get_source_type(self):
        return "view"

    @property
    def dataset_id(self) -> Optional[int]:
        return self.__dataset_id

    def _to_element_binding_config(self):
        return self.__source.source._to_element_binding_config()

    def _to_observable_config(self):
        return self.__source.source._to_observable_config()

    def flat_values(self):
        return self.__source.flat_values()

    def values(self):
        return self.__source.values()

    def columns(self):
        return self.__source.columns()


class DataQueryTable(DataTableMixin, ObservableMixin, ElementBindingMixin):
    def __init__(self, query: Query, fields: Optional[Sequence[str]] = None) -> None:
        if fields:
            sql = f"SELECT {', '.join(fields)} FROM {query.name}"
            query_name = get_store().gen_query(sql)
        else:
            query_name = query.name

        self.__source_name = query_name
        self.__dataset_id = query.dataset_id

        self.__source = _server_query.create_source(query_name)

    def get_query_name(self) -> str:
        return self.__source_name

    @property
    def source_name(self) -> str:
        return self.__source_name

    def get_source_type(self):
        return "query"

    @property
    def dataset_id(self) -> Optional[int]:
        return self.__dataset_id

    def _to_element_binding_config(self):
        return self.__source.source._to_element_binding_config()

    def _to_observable_config(self):
        return self.__source.source._to_observable_config()

    def flat_values(self):
        return self.__source.flat_values()

    def values(self):
        return self.__source.values()

    def columns(self):
        return self.__source.columns()
