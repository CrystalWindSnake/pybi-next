from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, List, Optional, Protocol, Sequence, Union
from typing_extensions import overload
from dataclasses import dataclass
from instaui import ui
from . import _const

if TYPE_CHECKING:
    from .data_view import DataView
    from .query import QueryInfo


class CanGetitem(Protocol):
    def __getitem__(self, item: str) -> Any: ...


class QueryableMixin(ABC):
    @abstractmethod
    def _to_sql(self) -> ui.TMaybeRef[str]:
        pass

    @overload
    def __getitem__(self, field: List[str]) -> QueryInfo: ...

    @overload
    def __getitem__(self, field: str) -> DataColumnMixin: ...

    @abstractmethod
    def __getitem__(
        self, field: Union[str, List[str]]
    ) -> Union[DataColumnMixin, QueryInfo]:
        pass

    @property
    @abstractmethod
    def result(self) -> CanGetitem:
        pass

    @abstractmethod
    def flat_values(self) -> ui.TMaybeRef[List[Any]]:
        pass

    def values(self):
        return self.result["values"]

    def columns(self):
        return self.result["columns"]


@dataclass
class DataSetQueryInfo:
    columns: List[str]
    values: List[List[Any]]

    def flat_values(self):
        return [v[0] for v in self.values]


class DataSetMixin(ABC):
    @abstractmethod
    def query(self, sql: str, params: Optional[List] = None) -> DataSetQueryInfo:
        pass

    @abstractmethod
    def get_id(self) -> int:
        pass


class DataTableMixin(ABC):
    @property
    @abstractmethod
    def fields(self) -> Sequence[str]:
        pass

    @abstractmethod
    def get_element_ref(self) -> ui.element_ref:
        pass

    @abstractmethod
    def get_data_view(self) -> DataView:
        pass


class DataColumnMixin(ABC):
    @property
    @abstractmethod
    def field(self) -> str:
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        pass

    @abstractmethod
    def get_source_type(self) -> _const.TSourceType:
        pass

    @abstractmethod
    def get_element_ref(self) -> ui.element_ref:
        pass
