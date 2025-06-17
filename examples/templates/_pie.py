from typing import Optional
from pybi.components.echarts import EChartsOption
from pybi.link_sql._mixin import QueryableMixin


# https://echarts.apache.org/zh/option.html#series-pie
_series_options = {
    "radius": "50%",
}


_extend_options = {
    "series_options": _series_options,
    "legend": {},
    "tooltip": {"trigger": "item"},
}


def make_pie(
    source: QueryableMixin,
    *,
    name: str,
    value: str,
    groupId: Optional[str] = None,
    subGroupId: Optional[str] = None,
    agg="avg",
):
    select_exprs = [
        name,
        f"ROUND({agg}({value}),2) as {value}",
    ]
    group_by_exprs = [name]

    if groupId:
        select_exprs.append(f"{groupId} as groupId")
        group_by_exprs.append(groupId)
    if subGroupId:
        select_exprs.append(f"{subGroupId} as subGroupId")
        group_by_exprs.append(subGroupId)

    sql = f"SELECT {', '.join(select_exprs)} FROM {source} GROUP BY {', '.join(group_by_exprs)} ORDER BY {name} ASC"

    option_fn_code = r"""(query_result, groupId, subGroupId,name,value,extend_options)=>{
        const source = [query_result.columns,...query_result.values]
        const {series_options, ...others_options} = extend_options
        const dimensions = [name,value, ...(groupId? ['groupId', 'subGroupId'] : [])]
        const encode = {itemName:name,value, ...(groupId? {itemGroupId: "groupId",itemChildGroupId: "subGroupId"} : {})}
        const universalTransition = groupId ? {"enabled": true, "divideShape": "clone"} : {}

        return {
            ...others_options,
            dataset: {dimensions,source},
            series: [{
                    ...series_options,
                    type: 'pie',
                    encode,
                    universalTransition,
                }]
        }
    }"""

    return EChartsOption(
        sql=sql,
        option_fn_code=option_fn_code,
        args=[groupId, subGroupId, name, value, _extend_options],
    )
