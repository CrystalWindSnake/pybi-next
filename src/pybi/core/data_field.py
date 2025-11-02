from __future__ import annotations
from typing import TYPE_CHECKING, Literal, Optional, Sequence, cast
from instaui import ui

from .page_state import PageState
from pybi.core import _utils
from pybi.systems import cache_system
from pybi.core.data_query import DataQuery
from pybi.core.sql_store import get_sql


if TYPE_CHECKING:
    from pybi.core.data_view import DataView


TOrderBy = Literal["asc", "desc"]


class DataField:
    def __init__(
        self,
        field: str,
        *,
        source: DataView,
        distinct: bool = False,
        order_by: Optional[TOrderBy] = None,
    ) -> None:
        self._field = field
        self._source = source
        self._distinct = distinct
        self._order_by = order_by

    @property
    def source(self) -> DataView:
        return self._source

    @property
    def field(self) -> str:
        return self._field

    @cache_system.instance_cache
    def flat_values(self) -> list:
        query = self.build_query()
        cp_id = PageState.get().component_store.gen_component_id()
        query.bind_component(cp_id)

        sourceable_result, dataset = _utils.sourceable(query, cp_id)

        @ui.computed(
            inputs=[
                cp_id,
                query.sql_id,
                *sourceable_result.inputs,
            ]
        )
        def values(
            cp_id: str, sql_id: str, sql_table: dict, filters: dict, _
        ) -> list[str]:
            sql, params = get_sql(
                sql_id, sql_table=sql_table, filters=filters, exclude_components=[cp_id]
            )

            return [row[0] for row in dataset.query(sql, params)["values"]]

        return values

    def distinct(
        self,
    ) -> DataField:
        return DataField(
            self._field,
            source=self._source,
            distinct=True,
            order_by=cast(TOrderBy, self._order_by),
        )

    def order_by(
        self,
        order_by: TOrderBy = "asc",
    ) -> DataField:
        return DataField(
            self._field, source=self._source, order_by=order_by, distinct=self._distinct
        )

    @cache_system.instance_cache
    def build_query(self) -> DataQuery:
        sql = f"SELECT {'DISTINCT ' if self._distinct else ''}{self._field} FROM {self._source}{'' if self._order_by is None else f' ORDER BY {self._field} {self._order_by}'}"
        return DataQuery(sql, self._source.dataset)


class DataFieldSet:
    def __init__(
        self,
        fields: Sequence[str],
        *,
        source: DataView,
        distinct: bool = False,
        order_fields: Optional[Sequence[str]] = None,
        orders: Optional[Sequence[TOrderBy]] = None,
    ) -> None:
        self._fields = fields
        self._source = source
        self._distinct = distinct
        self._order_fields = order_fields
        self._orders = orders

    @property
    def source(self) -> DataView:
        return self._source

    @property
    def fields(self) -> list[str]:
        return list(self._fields)

    def distinct(
        self,
    ) -> DataFieldSet:
        return DataFieldSet(
            self._fields,
            source=self._source,
            distinct=True,
            order_fields=self._order_fields,
            orders=self._orders,
        )

    def order_by(
        self,
        fields: Sequence[str],
        orders: Sequence[TOrderBy],
    ) -> DataFieldSet:
        return DataFieldSet(
            self._fields,
            source=self._source,
            distinct=self._distinct,
            order_fields=fields,
            orders=orders,
        )

    @cache_system.instance_cache
    def build_query(self) -> DataQuery:
        distinct = "DISTINCT " if self._distinct else ""
        fields = ", ".join(self._fields)
        order_by = (
            ""
            if self._order_fields is None or self._orders is None
            else f" ORDER BY {', '.join(f'{field} {order}' for field, order in zip(self._order_fields, self._orders))}"
        )

        sql = f"SELECT {distinct}{fields} FROM {self._source}{order_by}"
        return DataQuery(sql, self._source.dataset)
