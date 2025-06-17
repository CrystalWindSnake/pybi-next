from __future__ import annotations
from typing import Dict, Optional, Sequence, Union
from abc import ABC, abstractmethod
from instaui import ui
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from pybi.link_sql._server_query import create_chart_source
from pybi.systems import lazy_system


class EChartsOptionMixin(ABC):
    @abstractmethod
    def get_option(self) -> ElementBindingMixin:
        pass


def echarts(option: Union[Dict, EChartsOptionMixin]):
    chart_option = (
        option.get_option() if isinstance(option, EChartsOptionMixin) else option
    )

    chart = ui.echarts(chart_option)

    if isinstance(option, EChartsDrilldownOption):
        max_level = option.level_count
        next_level = ui.js_event(
            inputs=[
                option.current_level,
                max_level,
            ],
            outputs=[option.current_level],
            code=r"""(level,max_level) =>{
    if (level>=max_level){
        return;
    }       
    return level+1;                   
}""",
        )

        chart.on_chart("click", next_level)

    return chart


class EChartsOption(EChartsOptionMixin):
    def __init__(
        self,
        *,
        sql: str,
        option_fn_code: str,
        args: Optional[Sequence] = None,
    ) -> None:
        self._sql = sql
        self._option_fn_code = option_fn_code
        self._args = args

        def builder():
            info = create_chart_source([self._sql])
            fn = ui.js_fn(self._option_fn_code)
            opt = ui.js_computed(
                inputs=[info.source, fn, *(self._args or [])],
                code=r"""(query_result, fn, ...args) => fn(query_result, ...args)""",
            )

            return opt

        self._computed_option_getter = lazy_system.lazy_task(builder)

    def __add__(self, other: EChartsOption) -> EChartsDrilldownOption:
        return EChartsDrilldownOption([self, other])

    def get_option(self) -> ElementBindingMixin:
        return self._computed_option_getter()


class EChartsDrilldownOption(EChartsOptionMixin):
    def __init__(
        self,
        echarts_options: Sequence[EChartsOption],
    ) -> None:
        self.__echarts_options = echarts_options
        self.__current_level = ui.state(1)

    @property
    def current_level(self) -> int:
        return self.__current_level  # type: ignore

    @property
    def level_count(self) -> int:
        return len(self.__echarts_options)

    def __add__(
        self, other: Union[EChartsOption, EChartsDrilldownOption]
    ) -> EChartsDrilldownOption:
        if isinstance(other, EChartsOption):
            return EChartsDrilldownOption([*self.__echarts_options, other])

        return EChartsDrilldownOption(
            [*self.__echarts_options, *other.__echarts_options]
        )

    def get_option(self) -> ElementBindingMixin:
        sqls = [option._sql for option in self.__echarts_options if option._sql]
        js_fns = [ui.js_fn(option._option_fn_code) for option in self.__echarts_options]
        fn_args_array = [
            option._args for option in self.__echarts_options if option._args
        ]
        info = create_chart_source(sqls)

        ui.js_watch(
            inputs=[info.query_index],
            outputs=[self.__current_level],
            code="index => index+1",
        )

        ui.js_watch(
            inputs=[self.__current_level],
            outputs=[info.query_index],
            code="index => index-1",
        )

        return ui.js_computed(
            inputs=[info.source, info.query_index, fn_args_array, *js_fns],
            code=r"""(query_result,index,fn_args_array, ...fns) => fns[index](query_result,...fn_args_array[index])""",
        )
