import { defineComponent } from "vue";
import { useBindingGetter } from "instaui";
import type {
  TComponentId,
  TFilters,
  TSqlId,
  TSignals,
  TSqlTable,
} from "./types";

type TProps = {
  signals: TSignals;
  sqlTable: TSqlTable;
};

export default defineComponent({
  props: ["signals", "sqlTable"],
  setup(props: TProps, { expose }) {
    expose({
      ...getFiltersExpose(props),
    });
  },
});

function getFiltersExpose(props: TProps) {
  const { getValue } = useBindingGetter();
  const { signals } = props;

  function notifySignal(depsOfDataViewIds: TSqlId[]) {
    const realSignals = getValue(signals);

    for (const sqlId of depsOfDataViewIds) {
      realSignals[sqlId] = !realSignals[sqlId];
    }
  }

  function addFilters(
    filters: TFilters,
    componentId: TComponentId,
    filterTargetId: TSqlId,
    depsOfDataViewIds: TSqlId[],
    field: string,
    expr: string,
    value: any
  ): TFilters {
    const prevFilterItem = filters[filterTargetId] ?? {};
    const prevComponentFilters = prevFilterItem[componentId] ?? {};

    notifySignal(depsOfDataViewIds);

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
    filterTargetId: TSqlId,
    depsOfDataViewIds: TSqlId[]
  ): TFilters {
    const prevFilterItem = filters[filterTargetId];
    if (!prevFilterItem) return filters;

    const prevComponentFilters = prevFilterItem[componentId];
    if (!prevComponentFilters) return filters;

    const { [componentId]: _, ...rest } = prevFilterItem;

    notifySignal(depsOfDataViewIds);
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
