from __future__ import annotations
import weakref

from .page_state import PageState
from ._types import TComponentId, TSqlId
from ._mixins import SqlQueryProtocol, DataSetMixin
from .data_field import DataField


class DataView(SqlQueryProtocol):
    """
    Holder of query id used to reference SQL
    """

    def __init__(
        self,
        sql: str,
        *,
        dataset: DataSetMixin,
    ):
        page_state = PageState.get()
        central = page_state.central
        sql_store = page_state.sql_store
        dv_id, refs, template = sql_store.gen_data_view_info(sql, dataset_id=dataset.id)
        central.add_sql(dv_id, "data_view", template, refs)

        self.__sql_id = dv_id
        self._dataset = weakref.ref(dataset)

    @property
    def sql_id(self) -> TSqlId:
        return self.__sql_id

    @property
    def dataset(self) -> DataSetMixin:
        obj = self._dataset()
        assert obj is not None, "datasethas been garbage collected"
        return obj

    def __getitem__(self, field: str):
        return DataField(
            field,
            sql=f'select "{field}" from {self}',
            dataset=self.dataset,
        )

    def __str__(self):
        return f"DataView({self.__sql_id})"

    def __repr__(self):
        return str(self)

    def bind_component(self, component_id: TComponentId):
        PageState.get().central.bind_component_to_source(self.__sql_id, component_id)
