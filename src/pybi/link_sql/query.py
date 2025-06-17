import typing
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from instaui.vars.mixin_types.observable import ObservableMixin
from pybi.link_sql import _mixin
from pybi.link_sql.data_column import DataQueryColumn
from pybi.link_sql.data_table import DataQueryTable
from pybi.link_sql import _server_query
from pybi.link_sql.data_view_store import get_store as _get_store


class Query(
    _mixin.QueryableMixin,
    _mixin.QueryResultMixin,
    ElementBindingMixin,
    ObservableMixin,
    _mixin.DataTableMixin,
):
    def __init__(
        self, sql: str, *, dataset: typing.Optional[_mixin.DataSetMixin] = None
    ) -> None:
        self.__sql = sql
        self.__name = _get_store().gen_query(sql)
        # self._dataset_id = self.__try_get_dataset_id(dataset, sql)

        self.__dataset_id = dataset.get_id() if dataset else None

        self.__server_info = _server_query.create_source(
            self.__name,
            dataset_id=self.__dataset_id,
        )

    @property
    def name(self) -> str:
        return self.__name

    def _to_sql(self):
        return self.__sql

    @typing.overload
    def __getitem__(self, field: typing.List[str]) -> _mixin.DataTableMixin: ...

    @typing.overload
    def __getitem__(self, field: str) -> _mixin.DataColumnMixin: ...

    def __getitem__(
        self, field: typing.Union[str, typing.List[str]]
    ) -> typing.Union[_mixin.DataColumnMixin, _mixin.DataTableMixin]:
        if isinstance(field, str):
            return DataQueryColumn(self.__name, field)

        elif isinstance(field, list):
            return DataQueryTable(self, field)

        raise ValueError(f"Invalid field type: {type(field)}")

    def flat_values(
        self,
    ):
        return self.__server_info.flat_values()

    def _to_observable_config(self):
        return self.__server_info.source._to_observable_config()

    def _to_element_binding_config(self) -> typing.Dict:
        return self.__server_info.source._to_element_binding_config()

    def __str__(self) -> str:
        return self.__name

    def get_query_name(self) -> str:
        return self.__name

    @property
    def source_name(self) -> str:
        return self.__name

    @property
    def dataset_id(self) -> typing.Optional[int]:
        return self.__dataset_id

    def get_source_type(self):
        return "query"

    def values(self):
        return self.__server_info.flat_values()

    def columns(self):
        return self.__server_info.columns()


query = Query
