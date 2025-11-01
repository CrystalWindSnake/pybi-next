import re
from queue import SimpleQueue
from typing import Any, Generator, Literal, Optional
from ._types import TDatasetId, TQueryId, TSqlId, TDataViewId, TSqlType

_SUBQUERY_PATTERN = re.compile(
    r"(?:DataView|Query)\s*\(\s*([a-zA-Z_]\w*)\s*\)", re.IGNORECASE
)


class SqlStore:
    """
    SqlStore:
    - Generate unique query IDs
    - Store raw SQL containing DataView(sid)
    - Maintain reference dependency table
    - Resolve clean SQL recursively
    - Support injecting filters by component_id
    """

    def __init__(self):
        self._data_view_counter = 0
        self._query_counter = 0
        self._dependencies: dict[TSqlId, set[TSqlId]] = {}
        self._sql_types: dict[TSqlId, TSqlType] = {}

    def gen_data_view_info(
        self, sql: str, *, dataset_id: TDatasetId
    ) -> tuple[TDataViewId, list[TSqlId], str]:
        """
        Generate unique DataView ID, record dependencies, and create template
        """
        self._data_view_counter += 1
        dv_id = f"{dataset_id}_dv{self._data_view_counter}"
        ref_ids = _extract_subquery_ids(sql)
        template = _replace_subquery_templates(sql)
        self._dependencies[dv_id] = ref_ids
        self._sql_types[dv_id] = "data_view"
        return dv_id, list(ref_ids), template

    def gen_query_info(
        self, sql: str, *, dataset_id: TDatasetId
    ) -> tuple[TQueryId, list[TSqlId], str]:
        """
        Generate unique Query ID, record dependencies, and create template
        """
        self._query_counter += 1
        qid = f"{dataset_id}_q{self._query_counter}"
        ref_ids = _extract_subquery_ids(sql)
        template = _replace_subquery_templates(sql)
        self._dependencies[qid] = ref_ids
        self._sql_types[qid] = "query"
        return qid, list(ref_ids), template

    def _iter_all_dependencies_of(
        self,
        sid: TSqlId,
        type: Literal["data_view", "query", "all"] = "all",
    ) -> Generator[TSqlId, None, None]:
        if sid not in self._dependencies:
            raise KeyError(f"Query ID not found: {sid}")

        queue = SimpleQueue()
        queue.put(sid)

        visited = set()
        while not queue.empty():
            curr_sid = queue.get()
            if curr_sid in visited:
                continue
            visited.add(curr_sid)

            if type == "all" or self._sql_types[curr_sid] == type:
                yield curr_sid

            for ref_sid in self._dependencies[curr_sid]:
                if ref_sid not in visited:
                    queue.put(ref_sid)

    def get_dependency_of_first_data_view(self, sid: TSqlId) -> TSqlId:
        if sid in self._sql_types and self._sql_types[sid] == "data_view":
            return sid

        next_sid = next(self._iter_all_dependencies_of(sid, "data_view"), None)
        if next_sid is None:
            raise ValueError(f"No data view found for query {sid}")
        return next_sid


def _extract_subquery_ids(sql: str) -> set[str]:
    """
    Extract referenced subquery IDs from SQL, e.g. DataView(dv1), Query(q2)
    """
    return set(_SUBQUERY_PATTERN.findall(sql))


def _replace_subquery_templates(sql: str) -> str:
    """
    Replace occurrences of DataView(xxx) / Query(xxx) into {xxx}
    Used to create a clean SQL template string
    """

    def _replacer(match: re.Match) -> str:
        subquery_id = match.group(1)
        return f"{{{subquery_id}}}"

    return _SUBQUERY_PATTERN.sub(_replacer, sql)


def get_sql(
    sql_id: TSqlId,
    sql_table: dict,
    filters: Optional[dict] = None,
    exclude_components: Optional[list[str]] = None,
) -> tuple[str, list[Any] | None]:
    if sql_id not in sql_table:
        raise KeyError(f"SQL ID not found: {sql_id}")

    def build_sql(sid: TSqlId) -> tuple[str, list[Any]]:
        entry = sql_table[sid]
        template = entry["template"]
        params = []

        if not entry["references"]:
            if entry["type"] == "data_view" and filters and sid in filters:
                valid_filters = []
                for comp_id, conditions in filters[sid].items():
                    if exclude_components and comp_id in exclude_components:
                        continue
                    for condition in conditions.values():
                        valid_filters.append(condition["expr"])
                        if "value" in condition:
                            params.append(condition["value"])

                if valid_filters:
                    where_clause = " where " + " and ".join(valid_filters)
                    return template + where_clause, params

            return template, params

        subqueries = {}
        all_params = []
        for ref_id in entry["references"]:
            sub_sql, sub_params = build_sql(ref_id)
            subqueries[ref_id] = f"({sub_sql})"
            all_params.extend(sub_params)

        sql = template.format(**subqueries)
        return sql, all_params

    sql, params = build_sql(sql_id)
    return sql, params or None
