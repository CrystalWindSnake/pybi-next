from __future__ import annotations
from typing import Optional
import weakref

from .page_state import PageState
from ._types import TComponentId, TSqlId
from ._mixins import SqlQueryProtocol, DataSetMixin
from pybi.systems import sql_system


class DataField(SqlQueryProtocol):
    def __init__(
        self,
        field: str,
        *,
        sql: str,
        dataset: DataSetMixin,
    ) -> None:
        page_state = PageState.get()
        central = page_state.central
        sql_store = page_state.sql_store
        qid, refs, template = sql_store.gen_query_info(sql, dataset_id=dataset.id)
        central.add_sql(qid, "query", template, refs)

        self.__sql_id = qid
        self._field = field
        self._component_store = page_state.component_store
        self._dataset = weakref.ref(dataset)

    @property
    def sql_id(self) -> TSqlId:
        return self.__sql_id

    @property
    def dataset(self) -> DataSetMixin:
        obj = self._dataset()
        assert obj is not None, "dataset has been garbage collected"
        return obj

    @property
    def field(self) -> str:
        return self._field

    def __str__(self):
        return f"Query({self.__sql_id})"

    def __repr__(self):
        return str(self)

    def distinct(self, *, order_by: Optional[str] = None) -> DataField:
        return DataField(
            self._field,
            sql=f"select distinct {self._field} from {self}{sql_system.create_order_by(order_by)}",
            dataset=self.dataset,
        )

    def bind_component(self, component_id: TComponentId):
        PageState.get().central.bind_component_to_source(self.__sql_id, component_id)
