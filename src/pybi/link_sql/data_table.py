from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence

from ._mixin import DataTableMixin

if TYPE_CHECKING:
    from .data_view import DataView
    from .query import Query


class DataViewTable(DataTableMixin):
    def __init__(
        self, data_view: DataView, fields: Optional[Sequence[str]] = None
    ) -> None:
        self.__source_name = data_view.name
        self.__dataset_id = data_view.dataset_id
        self.__fields = fields or []

    def get_query_sql(self) -> str:
        return f'SELECT {", ".join(self.__fields)} FROM {self.__source_name}'

    @property
    def source_name(self) -> str:
        return self.__source_name

    def get_source_type(self):
        return "view"

    @property
    def dataset_id(self) -> Optional[int]:
        return self.__dataset_id


class DataQueryTable(DataTableMixin):
    def __init__(self, query: Query, fields: Optional[Sequence[str]] = None) -> None:
        self.__source_name = query.name
        self.__fields = fields or []

    def get_query_sql(self) -> str:
        return f'SELECT {", ".join(self.__fields)} FROM {self.__source_name}'

    @property
    def source_name(self) -> str:
        return self.__source_name

    def get_source_type(self):
        return "query"

    @property
    def dataset_id(self) -> Optional[int]:
        return None
