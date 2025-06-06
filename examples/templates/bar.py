from typing import Optional
from instaui import ui
import pybi
from pybi.components.echarts import EChartsOption
from pybi.link_sql._mixin import QueryableMixin


# https://echarts.apache.org/zh/option.html#series-bar
_series_options = {"label": {"show": True, "align": "center"}}

# https://echarts.apache.org/zh/option.html#xAxis
_xAxis_options = {"axisLabel": {"rotate": 30}, "type": "category"}

_yAxis_options = {}


_extend_options = {
    "series_options": _series_options,
    "xAxis": _xAxis_options,
    "yAxis": _yAxis_options,
    "tooltip": {},
}


def bar_options(
    source: QueryableMixin,
    *,
    x: Optional[str] = None,
    y: Optional[str] = None,
    agg="avg",
):
    sql = f"SELECT {x}, ROUND({agg}({y}),2) as {y} FROM {source} GROUP BY {x} ORDER BY {x} ASC"

    opt = ui.js_computed(
        inputs=[pybi.query(sql), x, y, _extend_options],
        code=r"""(query_result, x,y,extend_options)=>{
        const source = [query_result.columns,...query_result.values]
        const {series_options, ...others_options} = extend_options
        
        return {
            ...others_options,
            dataset: {source},
            series: [{
                    ...series_options,
                    type: 'bar',
                    encode: {x,y},
                }]
        }
    }""",
    )

    return EChartsOption(opt)
