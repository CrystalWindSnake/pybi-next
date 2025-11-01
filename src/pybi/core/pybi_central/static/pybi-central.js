import { defineComponent } from "vue";
import { useBindingGetter } from "instaui";

//#region src/sql-table-resolver.ts
var SqlTableResolver = class {
	downstreamComponentMap;
	constructor(sqlTable) {
		this.sqlTable = sqlTable;
		this.downstreamComponentMap = /* @__PURE__ */ new Map();
		this.buildDownstreamComponentMap();
	}
	buildDownstreamComponentMap() {
		const sqlDependencyMap = /* @__PURE__ */ new Map();
		for (const [sqlId, record] of Object.entries(this.sqlTable)) for (const refId of record.references) {
			if (!sqlDependencyMap.has(refId)) sqlDependencyMap.set(refId, /* @__PURE__ */ new Set());
			sqlDependencyMap.get(refId).add(sqlId);
		}
		for (const [sqlId, _] of Object.entries(this.sqlTable)) {
			const componentIds = /* @__PURE__ */ new Set();
			const visited = /* @__PURE__ */ new Set();
			const queue = [...sqlDependencyMap.get(sqlId) || []];
			while (queue.length > 0) {
				const currentId = queue.shift();
				visited.add(currentId);
				for (const componentId of this.sqlTable[currentId].components || []) componentIds.add(componentId);
				for (const nextId of sqlDependencyMap.get(currentId) || []) if (!visited.has(nextId)) queue.push(nextId);
			}
			this.downstreamComponentMap.set(sqlId, componentIds);
		}
	}
	getDownstreamComponentIds(sqlId) {
		return this.downstreamComponentMap.get(sqlId) || /* @__PURE__ */ new Set();
	}
	getComponents(sqlId) {
		const record = this.sqlTable[sqlId];
		return record?.components ? new Set(record.components) : /* @__PURE__ */ new Set();
	}
	getComponentsToNotify(sqlId, excludeComponentId) {
		const components = /* @__PURE__ */ new Set();
		for (const id of this.getComponents(sqlId)) if (id !== excludeComponentId) components.add(id);
		for (const id of this.getDownstreamComponentIds(sqlId)) if (id !== excludeComponentId) components.add(id);
		return components;
	}
};

//#endregion
//#region src/index.ts
var src_default = defineComponent({
	props: ["signals", "sqlTable"],
	setup(props, { expose }) {
		const { getValue } = useBindingGetter();
		expose({ ...getFiltersExpose(props, new SqlTableResolver(getValue(props.sqlTable))) });
	}
});
function getFiltersExpose(props, sqlTableResolver) {
	const { getValue } = useBindingGetter();
	const { signals } = props;
	function notifySignal(filterSqlId, excludeComponentId) {
		const realSignals = getValue(signals);
		const depsOfComponentIds = sqlTableResolver.getComponentsToNotify(filterSqlId, excludeComponentId);
		for (const componentId of depsOfComponentIds) realSignals[componentId] = !realSignals[componentId];
	}
	function addFilters(filters, componentId, filterTargetId, field, expr, value) {
		const prevFilterItem = filters[filterTargetId] ?? {};
		const prevComponentFilters = prevFilterItem[componentId] ?? {};
		notifySignal(filterTargetId, componentId);
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
	function removeFilters(filters, componentId, filterTargetId) {
		const prevFilterItem = filters[filterTargetId];
		if (!prevFilterItem) return filters;
		if (!prevFilterItem[componentId]) return filters;
		const { [componentId]: _,...rest } = prevFilterItem;
		notifySignal(filterTargetId, componentId);
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