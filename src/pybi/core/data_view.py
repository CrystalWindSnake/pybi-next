from __future__ import annotations
from typing import Sequence, overload
import weakref
from instaui import ui

from .page_state import PageState
from ._types import DataSetQueryInfo, TComponentId, TSqlId
from ._mixins import SqlQueryProtocol, DataSetMixin
from .data_field import DataField, DataFieldSet
from pybi.core import _utils
from pybi.core.sql_store import get_sql


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

    @overload
    def __getitem__(self, field: str) -> DataField: ...

    @overload
    def __getitem__(self, field: Sequence[str]) -> DataFieldSet: ...

    def __getitem__(self, field: str | Sequence[str]):
        if isinstance(field, str):
            return DataField(field, source=self)
        else:
            return DataFieldSet(field, source=self)

    def __str__(self):
        return f"DataView({self.__sql_id})"

    def __repr__(self):
        return str(self)

    def bind_component(self, component_id: TComponentId):
        PageState.get().central.bind_component_to_source(self.__sql_id, component_id)

    def to_query(self):
        cp_id = PageState.get().component_store.gen_component_id()
        self.bind_component(cp_id)

        sourceable_result, dataset = _utils.sourceable(self, cp_id)

        @ui.computed(
            inputs=[
                cp_id,
                self.sql_id,
                *sourceable_result.inputs,
            ]
        )
        def table(
            cp_id: str, sql_id: str, sql_table: dict, filters: dict, _
        ) -> DataSetQueryInfo:
            sql, params = get_sql(
                sql_id, sql_table=sql_table, filters=filters, exclude_components=[cp_id]
            )

            return dataset.query(sql, params)

        return table
