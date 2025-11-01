from __future__ import annotations
import weakref

from .page_state import PageState
from ._types import TComponentId, TSqlId
from ._mixins import SqlQueryProtocol, DataSetMixin


class DataQuery(SqlQueryProtocol):
    def __init__(
        self,
        sql: str,
        dataset: DataSetMixin,
    ) -> None:
        page_state = PageState.get()
        central = page_state.central
        sql_store = page_state.sql_store
        qid, refs, template = sql_store.gen_query_info(sql, dataset_id=dataset.id)
        central.add_sql(qid, "query", template, refs)

        self.__sql_id = qid
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

    def __str__(self):
        return f"Query({self.__sql_id})"

    def __repr__(self):
        return str(self)

    def bind_component(self, component_id: TComponentId):
        PageState.get().central.bind_component_to_source(self.__sql_id, component_id)
