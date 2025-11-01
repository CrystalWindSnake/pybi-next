from typing import Optional, cast
from instaui import custom, ui
from instaui.common.jsonable import Jsonable
from pybi.core._types import TSqlId, TSqlType, TComponentId


class PybiCentral(custom.element, esm="./static/pybi-central.js"):
    def __init__(self):
        super().__init__()
        self.__org_signals: dict[TComponentId, bool] = {}
        self.__signals = ui.state(self.__org_signals)

        self.__org_sql_table = SqlTable()
        self.__sql_table = cast(dict, ui.data(self.__org_sql_table))

        self.props(
            {
                "sqlTable": custom.convert_reference(self.__sql_table),
                "signals": custom.convert_reference(self.__signals),
            }
        )

        self.__filters = ui.state({})

        self._ref = ui.element_ref()
        self.element_ref(self._ref)

    @property
    def sql_table(self):
        return self.__sql_table

    def bind_component_to_source(self, sql_id: TSqlId, component_id: TComponentId):
        self.__org_sql_table.bind_component_to_source(sql_id, component_id)

    def add_sql(
        self,
        sql_id: TSqlId,
        type: TSqlType,
        template: str,
        references: Optional[list[TSqlId]] = None,
    ):
        self.__org_sql_table.record_sql(sql_id, type, template, references)

    @property
    def component_ref(self):
        '''
        code=r"""(central,filters,sql_id)=> {
            return central.addFilters(filters, componentId, sql_id, field, expr, referencedIds);
            return central.removeFilters(filters, componentId, sql_id, referencedIds);
        }""",
        '''
        return self._ref

    @property
    def filters_state(self):
        return self.__filters

    @property
    def signal_state(self):
        return self.__signals

    def register_signal(self, component_id: TComponentId):
        self.__org_signals[component_id] = False

    def signal(self, component_id: TComponentId):
        return self.__signals[component_id]


class SqlTableRecord(Jsonable):
    def __init__(self, type: TSqlType, template: str, references: list[TSqlId]) -> None:
        self.type = type
        self.template = template
        self.references = references
        self.components = set()

    def add_component(self, component_id: TComponentId):
        self.components.add(component_id)

    def _to_json_dict(self):
        data: dict = {
            "type": self.type,
            "template": self.template,
            "references": self.references,
        }

        if self.components:
            data["components"] = list(self.components)

        return data


class SqlTable(Jsonable):
    def __init__(self) -> None:
        self._data: dict[TSqlId, SqlTableRecord] = {}

    def record_sql(
        self,
        sql_id: TSqlId,
        type: TSqlType,
        template: str,
        references: Optional[list[TSqlId]] = None,
    ):
        self._data[sql_id] = SqlTableRecord(
            type=type, template=template, references=references or []
        )

    def bind_component_to_source(self, sql_id: TSqlId, component_id: TComponentId):
        assert sql_id in self._data, f"sql_id {sql_id} not found in sql_table"
        self._data[sql_id].add_component(component_id)

    def _to_json_dict(self):
        return self._data
