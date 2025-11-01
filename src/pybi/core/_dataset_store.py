from typing import Final, Dict
import threading
import re
from ._types import TDatasetId
from pybi.core._mixins import DataSetMixin

# Constants
DATASET_ID_PREFIX: Final[str] = "ds"


class DatasetIdGenerator:
    _instance = None
    _lock: Final = threading.Lock()
    _counter: int = 0
    _datasets: Dict[TDatasetId, DataSetMixin] = {}

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def register_dataset(self, dataset: DataSetMixin) -> TDatasetId:
        """Register a dataset and return its ID.

        Args:
            dataset: The dataset to register

        Returns:
            A new unique dataset ID in format 'ds{counter}'
        """
        with self._lock:
            self._counter += 1
            dataset_id = f"{DATASET_ID_PREFIX}{self._counter}"
            self._datasets[dataset_id] = dataset
            return dataset_id

    def get_dataset(self, dataset_id: TDatasetId) -> DataSetMixin:
        """Get dataset by ID.

        Args:
            dataset_id: The ID of the dataset to retrieve

        Returns:
            The dataset if found, None otherwise
        """
        with self._lock:
            result = self._datasets.get(dataset_id)
            if result is None:
                raise ValueError(f"Dataset {dataset_id} not found")
            return result


# Module-level singleton instance
_dataset_id_generator: Final = DatasetIdGenerator()


def register_dataset(dataset: DataSetMixin) -> TDatasetId:
    """Register a dataset and return its ID.

    Args:
        dataset: The dataset to register

    Returns:
        TDatasetId: A new unique dataset ID in format 'ds{counter}'
    """
    return _dataset_id_generator.register_dataset(dataset)


def get_dataset_by_id(dataset_id: TDatasetId) -> DataSetMixin:
    """Get dataset by ID.

    Args:
        dataset_id: The ID of the dataset to retrieve

    Returns:
        The dataset if found, None otherwise
    """

    return _dataset_id_generator.get_dataset(dataset_id)


def parse_dataset_ids_from_sql(sql: str) -> list[TDatasetId]:
    """Parse SQL statement and extract all dataset IDs used.

    Args:
        sql: The SQL statement to parse

    Returns:
        List of unique dataset IDs found in the SQL

    Examples:
        >>> parse_dataset_ids_from_sql("select * from DataView(ds1_dv1)")
        ['ds1']
        >>> parse_dataset_ids_from_sql("select * from Query(ds2_q1) where Name='name1'")
        ['ds2']
    """

    # Match DataView(dsX...) or Query(dsX...), case insensitive
    pattern = rf"(?:DataView|Query)\(({DATASET_ID_PREFIX}\d+)"
    matches = re.findall(pattern, sql, re.IGNORECASE)
    # Return unique matches
    return list(set(matches))
