# from typing import TYPE_CHECKING, Dict, Optional, Sequence
# from instaui import ui

# from pybi.link_sql._mixin import DataSetMixin
# from pybi.link_sql.models import ExcludeFilterInfo
# from pybi.link_sql.sql import create_sql
# from .data_set_store import get_data_set
# from .data_view_store import DataViewStore, get_dependency_views

# if TYPE_CHECKING:
#     from pybi.link_sql.data_view import DataView


# def sql_query(
#     sql: str,
#     *,
#     dataset: Optional[DataSetMixin] = None,
#     exclude_info: Optional[ExcludeFilterInfo] = None,
# ):
#     dep_views = get_dependency_views(sql)
#     exclude_query_key = None if exclude_info is None else exclude_info.query_key

#     view_names = [view.str_name for view in dep_views]
#     filters = [
#         view._get_filters(exclude_query_key=exclude_query_key) for view in dep_views
#     ]
#     dataset_id = dataset.get_id() if dataset is not None else None

#     dataset_id, from_views = _get_any_dataset_id(dep_views, dataset)

#     if (not from_views) and (dataset_id is None):
#         raise ValueError(f"Must specify at least one view or dataset:{sql=}")

#     @ui.computed(
#         inputs=[
#             sql,
#             dataset_id,
#             from_views,
#             DataViewStore.get().data,
#             exclude_info,
#             view_names,
#             *filters,
#         ],
#         deep_compare_on_input=True,
#     )
#     def query_result(
#         sql,
#         dataset_id: int,
#         from_views: bool,
#         data_view_store: Dict,
#         exclude_info: Optional[ExcludeFilterInfo],
#         view_names: Sequence[str],
#         *filters,
#     ):
#         dataset = get_data_set(dataset_id)

#         if not from_views:
#             return dataset.query(sql)

#         sql_info = create_sql(
#             main_sql=sql,
#             data_view_store=data_view_store,
#             exclude_info=exclude_info,
#             dep_view_names=view_names,
#             dep_filters=filters,
#         )

#         result = dataset.query(sql_info.sql, sql_info.params)
#         return result

#     return query_result


# def _get_any_dataset_id(
#     dep_views: Sequence["DataView"], dataset: Optional[DataSetMixin]
# ):
#     id_from_dep_views = None
#     from_views = False

#     for view in dep_views:
#         if view._dataset_id is not None:
#             id_from_dep_views = view._dataset_id
#             from_views = True
#             break
#     else:
#         if dataset is not None:
#             id_from_dep_views = dataset.get_id()

#     return id_from_dep_views, from_views
