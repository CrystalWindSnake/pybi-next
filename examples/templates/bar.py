from typing import Optional
from instaui import ui

# from pybi.link_sql.data_view import DataView

import pybi
from pybi.link_sql.query import query
from pybi.components.echarts import EChartsOption
from pybi.link_sql._mixin import QueryableMixin


# https://echarts.apache.org/zh/option.html#series-bar
_series_options = {"label": {"show": True, "align": "center"}}

# https://echarts.apache.org/zh/option.html#xAxis
_xAxis_options = {"axisLabel": {"rotate": 30}}

_yAxis_options = {}


_extend_options = {
    "series_options": _series_options,
    "_xAxis_options": _xAxis_options,
    "_yAxis_options": _yAxis_options,
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
        const {series_options,_xAxis_options,_yAxis_options} = extend_options
        
        return {
            dataset: {source},
            xAxis: {..._xAxis_options, type: 'category'},
            yAxis: {..._yAxis_options },
            series: [{
                    ...series_options,
                    type: 'bar',
                    encode: {x,y},
                }]
        }
    }""",
    )

    return EChartsOption(opt)
