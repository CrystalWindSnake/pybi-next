import { defineComponent } from "vue";
import { useBindingGetter } from "instaui";

//#region src/index.ts
var src_default = defineComponent({
	props: ["signals", "sqlTable"],
	setup(props, { expose }) {
		expose({ ...getFiltersExpose(props) });
	}
});
function getFiltersExpose(props) {
	const { getValue } = useBindingGetter();
	const { signals } = props;
	function notifySignal(depsOfDataViewIds) {
		const realSignals = getValue(signals);
		for (const sqlId of depsOfDataViewIds) realSignals[sqlId] = !realSignals[sqlId];
	}
	function addFilters(filters, componentId, filterTargetId, depsOfDataViewIds, field, expr, value) {
		const prevFilterItem = filters[filterTargetId] ?? {};
		const prevComponentFilters = prevFilterItem[componentId] ?? {};
		notifySignal(depsOfDataViewIds);
		return {
			...filters,
			[filterTargetId]: {
				...prevFilterItem,
				[componentId]: {
					...prevComponentFilters,
					[field]: {
						expr,
						value
					}
				}
			}
		};
	}
	function removeFilters(filters, componentId, filterTargetId, depsOfDataViewIds) {
		const prevFilterItem = filters[filterTargetId];
		if (!prevFilterItem) return filters;
		if (!prevFilterItem[componentId]) return filters;
		const { [componentId]: _,...rest } = prevFilterItem;
		notifySignal(depsOfDataViewIds);
		return {
			...filters,
			[filterTargetId]: rest
		};
	}
	return {
		addFilters,
		removeFilters
	};
}

//#endregion
export { src_default as default };