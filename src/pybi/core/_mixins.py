from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Protocol
from ._types import TSqlId, TComponentId, DataSetQueryInfo


class DataSetMixin(ABC):
    @abstractmethod
    def query(self, sql: str, params: Optional[list] = None) -> DataSetQueryInfo:
        pass


class SqlQueryProtocol(Protocol):
    @property
    def sql_id(self) -> TSqlId: ...

    @property
    def dataset(self) -> DataSetMixin: ...

    def gen_component_id(self) -> TComponentId: ...
