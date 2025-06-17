from typing import Optional
from pybi.components.echarts import EChartsOption
from pybi.link_sql._mixin import QueryableMixin


# https://echarts.apache.org/zh/option.html#series-bar
_series_options = {"label": {"show": True}}

# https://echarts.apache.org/zh/option.html#xAxis
_xAxis_options = {"axisLabel": {"rotate": 30}, "type": "category"}

_yAxis_options = {}


_extend_options = {
    "series_options": _series_options,
    "xAxis": _xAxis_options,
    "yAxis": _yAxis_options,
    "tooltip": {},
}


def make_line(
    source: QueryableMixin,
    *,
    x: str,
    y: str,
    groupId: Optional[str] = None,
    subGroupId: Optional[str] = None,
    agg="avg",
):
    select_exprs = [
        x,
        f"ROUND({agg}({y}),2) as {y}",
    ]
    group_by_exprs = [x]

    if groupId:
        select_exprs.append(f"{groupId} as groupId")
        group_by_exprs.append(groupId)
    if subGroupId:
        select_exprs.append(f"{subGroupId} as subGroupId")
        group_by_exprs.append(subGroupId)

    sql = f"SELECT {', '.join(select_exprs)} FROM {source} GROUP BY {', '.join(group_by_exprs)} ORDER BY {x} ASC"

    option_fn_code = r"""(query_result, groupId,subGroupId,x,y,extend_options)=>{
        const source = [query_result.columns,...query_result.values]
        const {series_options, ...others_options} = extend_options
        const dimensions = [x,y, ...(groupId? ['groupId', 'subGroupId'] : [])]
        const encode = {x,y, ...(groupId? {itemGroupId: "groupId",itemChildGroupId: "subGroupId"} : {})}
        const universalTransition = groupId ? {"enabled": true, "divideShape": "clone"} : {}
        
        return {
            ...others_options,
            dataset: {dimensions,source},
            series: [{
                    ...series_options,
                    type: 'line',
                    encode,
                    universalTransition,
                }]
        }
    }"""

    return EChartsOption(
        sql=sql,
        option_fn_code=option_fn_code,
        args=[groupId, subGroupId, x, y, _extend_options],
    )
