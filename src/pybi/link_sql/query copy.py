# from __future__ import annotations
# from typing import Dict, List, Optional, Union
# from typing_extensions import overload
# from instaui import ui
# from instaui.vars.web_computed import WebComputed
# from instaui.vars.mixin_types.observable import ObservableMixin
# from instaui.vars.mixin_types.element_binding import ElementBindingMixin

# from ._mixin import DataSetMixin, DataColumnMixin, QueryableMixin
# from .duckdb_utils import sql_query
# from pybi.link_sql.models import ExcludeFilterInfo


# class QueryInfo(ObservableMixin, ElementBindingMixin, QueryableMixin):
#     def __init__(
#         self,
#         sql: str,
#         *,
#         dataset: Optional[DataSetMixin] = None,
#         exclude_info: Optional[ExcludeFilterInfo] = None,
#     ) -> None:
#         self.__result_getter = _ready_result(
#             sql,
#             dataset=dataset,
#             exclude_info=exclude_info,
#         )

#         self.__sql_str = sql

#     @property
#     def result(self):
#         return self.__result_getter()

#     def flat_values(self):
#         return ui.js_computed(
#             inputs=[self.result],
#             code=r"""result=>{
#     const values = result.values;
#     return values.flat();
# }""",
#         )

#     def values(self):
#         return self.result["values"]

#     def columns(self):
#         return self.result["columns"]

#     def _to_observable_config(self):
#         return self.values()._to_observable_config()

#     def _to_element_binding_config(self) -> Dict:
#         return self.values()._to_element_binding_config()

#     def _to_sql(self) -> ui.TMaybeRef[str]:
#         raise NotImplementedError

#     @overload
#     def __getitem__(self, field: List[str]) -> QueryInfo: ...

#     @overload
#     def __getitem__(self, field: str) -> DataColumnMixin: ...

#     def __getitem__(
#         self, field: Union[str, List[str]]
#     ) -> Union[DataColumnMixin, QueryInfo]:
#         if isinstance(field, str):
#             field = [field]

#         select_stem = ", ".join(field) if field else "*"
#         return QueryInfo(f"SELECT {select_stem} FROM ({self})")

#     def __str__(self) -> str:
#         return self.__sql_str


# def _ready_result(
#     sql: str,
#     *,
#     dataset: Optional[DataSetMixin] = None,
#     exclude_info: Optional[ExcludeFilterInfo] = None,
# ):
#     result = None

#     def fn() -> WebComputed:
#         nonlocal result
#         if result is None:
#             result = sql_query(sql, dataset=dataset, exclude_info=exclude_info)
#         return result

#     return fn


# query = QueryInfo
