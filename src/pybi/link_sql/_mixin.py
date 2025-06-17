from __future__ import annotations
from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Union,
    TypedDict,
)
from typing_extensions import overload
from instaui import ui
from . import _const

if TYPE_CHECKING:
    pass


class QueryableMixin(ABC):
    @abstractmethod
    def _to_sql(self) -> ui.TMaybeRef[str]:
        pass

    @overload
    def __getitem__(self, field: List[str]) -> DataTableMixin: ...

    @overload
    def __getitem__(self, field: str) -> DataColumnMixin: ...

    @abstractmethod
    def __getitem__(
        self, field: Union[str, List[str]]
    ) -> Union[DataColumnMixin, DataTableMixin]:
        pass


class QueryResultMixin(ABC):
    @abstractmethod
    def flat_values(self) -> ui.TMaybeRef[List[Any]]:
        pass


class DataSetQueryInfo(TypedDict, total=False):
    columns: List[str]
    values: List[List[Any]]
    sql: str


class DataSetMixin(ABC):
    @abstractmethod
    def query(self, sql: str, params: Optional[List] = None) -> DataSetQueryInfo:
        pass

    @abstractmethod
    def get_id(self) -> int:
        pass


class DataTableMixin(ABC):
    @abstractmethod
    def get_query_name(self) -> str:
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        pass

    @property
    @abstractmethod
    def dataset_id(self) -> Optional[int]:
        pass

    @abstractmethod
    def get_source_type(self) -> _const.TSourceType:
        pass

    @abstractmethod
    def flat_values(self) -> List[Any]:
        pass

    @abstractmethod
    def values(self) -> List[List[Any]]:
        pass

    @abstractmethod
    def columns(self) -> List:
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
    def distinct(self, *, order_by: Optional[Literal["ASC", "DESC"]] = None) -> List:
        pass

    @abstractmethod
    def flat_values(self) -> List:
        pass

    @abstractmethod
    def _to_element_binding_config(self) -> Dict: ...
