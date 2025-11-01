import { defineComponent } from "vue";
import { useBindingGetter } from "instaui";
import type {
  TComponentId,
  TFilters,
  TSqlId,
  TSignals,
  TSqlTable,
} from "./types";
import { SqlTableResolver } from "./sql-table-resolver";

type TProps = {
  signals: TSignals;
  sqlTable: TSqlTable;
};

export default defineComponent({
  props: ["signals", "sqlTable"],
  setup(props: TProps, { expose }) {
    const { getValue } = useBindingGetter();
    const sqlTableResolver = new SqlTableResolver(getValue(props.sqlTable));

    expose({
      ...getFiltersExpose(props, sqlTableResolver),
    });
  },
});

function getFiltersExpose(props: TProps, sqlTableResolver: SqlTableResolver) {
  const { getValue } = useBindingGetter();
  const { signals } = props;

  function notifySignal(filterSqlId: TSqlId, excludeComponentId: TComponentId) {
    const realSignals = getValue(signals);
    const depsOfComponentIds = sqlTableResolver.getComponentsToNotify(
      filterSqlId,
      excludeComponentId
    );

    for (const componentId of depsOfComponentIds) {
      realSignals[componentId] = !realSignals[componentId];
    }
  }

  function addFilters(
    filters: TFilters,
    componentId: TComponentId,
    filterTargetId: TSqlId,
    field: string,
    expr: string,
    value: any
  ): TFilters {
    const prevFilterItem = filters[filterTargetId] ?? {};
    const prevComponentFilters = prevFilterItem[componentId] ?? {};

    notifySignal(filterTargetId, componentId);

    return {
      ...filters,
      [filterTargetId]: {
        ...prevFilterItem,
        [componentId]: {
          ...prevComponentFilters,
          [field]: { expr, value },
        },
      },
    };
  }

  function removeFilters(
    filters: TFilters,
    componentId: TComponentId,
    filterTargetId: TSqlId
  ): TFilters {
    const prevFilterItem = filters[filterTargetId];
    if (!prevFilterItem) return filters;

    const prevComponentFilters = prevFilterItem[componentId];
    if (!prevComponentFilters) return filters;

    const { [componentId]: _, ...rest } = prevFilterItem;

    notifySignal(filterTargetId, componentId);
    return {
      ...filters,
      [filterTargetId]: rest,
    };
  }

  return {
    addFilters,
    removeFilters,
  };
}
