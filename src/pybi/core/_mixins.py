from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Protocol
from ._types import TSqlId, TComponentId, DataSetQueryInfo, TDatasetId


class DataSetMixin(ABC):
    @property
    @abstractmethod
    def id(self) -> TDatasetId:
        pass

    @abstractmethod
    def query(self, sql: str, params: Optional[list] = None) -> DataSetQueryInfo:
        pass


class SqlQueryProtocol(Protocol):
    @property
    def sql_id(self) -> TSqlId: ...

    @property
    def dataset(self) -> DataSetMixin: ...

    def bind_component(self, component_id: TComponentId): ...
