from __future__ import annotations
from typing import Dict, List, Optional, Union
from typing_extensions import overload
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from instaui.vars.mixin_types.observable import ObservableMixin
from pybi.link_sql import sql_stem
from pybi.link_sql.data_column import DataViewColumn
from pybi.link_sql.data_table import DataViewTable
from pybi.link_sql.data_view_store import get_store as _get_store
from pybi.link_sql import _server_query


from pybi.link_sql._mixin import (
    DataColumnMixin,
    QueryableMixin,
    DataSetMixin,
    DataTableMixin,
)


class DataView(QueryableMixin, ElementBindingMixin, ObservableMixin, DataTableMixin):
    def __init__(self, sql: str, *, dataset: Optional[DataSetMixin] = None):
        self.__sql = sql

        self._dataset_id = self.__try_get_dataset_id(dataset, sql)
        self.__name = _get_store().gen_view(sql, self._dataset_id)

        self.__source = _server_query.create_source(
            self.__name,
            dataset_id=self._dataset_id,
        )

    def __try_get_dataset_id(self, dataset: Optional[DataSetMixin], sql: str):
        if dataset is None:
            for name in sql_stem.iter_extract_names(sql):
                if sql_stem.get_source_type(name) == "view":
                    return _get_store().get_view_dataset_id(name)

            raise ValueError("dataset is None and no view found in sql")

        return dataset.get_id()

    @property
    def name(self) -> str:
        return self.__name

    @property
    def dataset_id(self) -> int:
        return self._dataset_id

    def _to_observable_config(self):
        return self.__source.source._to_observable_config()

    def _to_element_binding_config(self) -> Dict:
        return self.__source.source._to_element_binding_config()

    def _to_sql(
        self,
    ):
        return self.__sql

    @overload
    def __getitem__(self, field: List[str]) -> DataTableMixin: ...

    @overload
    def __getitem__(self, field: str) -> DataColumnMixin: ...

    def __getitem__(
        self, field: str | List[str]
    ) -> Union[DataColumnMixin, DataTableMixin]:
        if isinstance(field, str):
            return DataViewColumn(self.__name, field)

        elif isinstance(field, list):
            return DataViewTable(self, field)

        raise ValueError("field must be str or list[str]")

    def __str__(self) -> str:
        return self.name

    def get_query_name(self) -> str:
        return self.name

    @property
    def source_name(self) -> str:
        return self.__name

    def get_source_type(self):
        return "view"

    def flat_values(self):
        return self.__source.flat_values()

    def values(self):
        return self.__source.values()

    def columns(self):
        return self.__source.columns()


def data_view(sql: str) -> DataView:
    return DataView(sql)
