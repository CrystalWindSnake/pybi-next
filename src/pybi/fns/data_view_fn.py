from pybi.core.data_view import DataView
from pybi.core import _dataset_store


def data_view(sql: str):
    dataset_ids = _dataset_store.parse_dataset_ids_from_sql(sql)
    assert len(dataset_ids) == 1, "Only one dataset is allowed in data view"

    if len(dataset_ids) < 1:
        raise ValueError("No dataset found in data view")

    return DataView(sql, dataset=_dataset_store.get_dataset_by_id(dataset_ids[0]))
