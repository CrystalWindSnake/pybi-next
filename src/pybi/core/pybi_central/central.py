from typing import Optional
from instaui import custom, ui
from pybi.core._types import TDataViewId, TSqlId, TSqlType


class PybiCentral(custom.element, esm="./static/pybi-central.js"):
    def __init__(self):
        super().__init__()
        self.__org_signals: dict[str, bool] = {}
        self.__signals = ui.state(self.__org_signals)

        self.__org_sql_table = {}
        self.__sql_table = ui.data(self.__org_sql_table)

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

    def add_sql(
        self,
        sql_id: TSqlId,
        type: TSqlType,
        template: str,
        references: Optional[list[TSqlId]] = None,
    ):
        self.__org_sql_table[sql_id] = {
            "type": type,
            "template": template,
            "references": references or [],
        }

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

    def register_signal(self, sql_id: TSqlId):
        self.__org_signals[sql_id] = False

    def signal(self, data_view_ids: set[TDataViewId]):
        real_sids = list(data_view_ids)
        return [self.__signals[sid] for sid in real_sids]
