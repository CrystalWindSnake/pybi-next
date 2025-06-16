import { type SetupContext } from "vue";

type TFilterExcludeKey = string;
type TFilterOption = { expr: string; value: any };
type TFilters = Record<TFilterExcludeKey, TFilterOption>;
type TSqlMapValue = { sql: string; filters: TFilters; parents: string[] };
type TSqlMap = Map<string, TSqlMapValue>;
type TExcludeInfo = { view: string; keys: TFilterExcludeKey[] };

type TProps = {
  sql_map: Record<string, TSqlMapValue>;
  notify_list: Record<
    string,
    { source: string; exclude_infos: TExcludeInfo[] }
  >;
};

export default {
  props: ["sql_map", "notify_list"],

  setup(props: TProps, { expose, emit }: SetupContext) {
    const sqlMap = new Map(Object.entries(props.sql_map));

    const { view2notify, notifyName2views, notify2ExcludeInfos } =
      createNotifyMap(props.notify_list, sqlMap);

    const emitSqlMap = () => {
      emit("update:sql_map", Object.fromEntries(sqlMap.entries()));
    };

    emitSqlMap();

    // console.log('notifyMap', sqlMap, view2notify)
    const emit_notify = (view_name: string) => {
      view2notify.get(view_name)?.forEach((notifyName) => {
        const eventData = notifyName2views.get(notifyName)?.map((viewName) => {
          const { filters } = sqlMap.get(viewName)!;

          const filtersWithoutExclude = Object.fromEntries(
            Object.entries(filters).filter(([key]) => {
              return !notify2ExcludeInfos
                .get(notifyName)!
                .get(viewName)
                ?.includes(key);
            })
          );

          return {
            view: viewName,
            filters: filtersWithoutExclude,
          };
        });
        emit(`notify:${notifyName}`, eventData ?? {});
      });
    };

    function addFilter(
      view_name: string,
      query_key: string,
      option: TFilterOption
    ) {
      const viewInfo = sqlMap.get(view_name)!;

      const snapshot = filtersSnapshot(viewInfo.filters);
      viewInfo.filters = {
        ...viewInfo.filters,
        [query_key]: option,
      };

      if (snapshot.isDiff(viewInfo.filters)) {
        emit_notify(view_name);
        emitSqlMap();
      }
    }

    function removeFilter(view_name: string, query_key: string) {
      const viewInfo = sqlMap.get(view_name)!;
      const snapshot = filtersSnapshot(viewInfo.filters);
      delete viewInfo.filters[query_key];

      if (snapshot.isDiff(viewInfo.filters)) {
        emit_notify(view_name);
        emitSqlMap();
      }
    }

    expose({
      addFilter,
      removeFilter,
    });
  },
};

function createNotifyMap(
  notifyList: Record<string, { source: string; exclude_infos: TExcludeInfo[] }>,
  sqlMap: TSqlMap
) {
  const view2notify: Map<string, string[]> = new Map();
  const notifyName2views: Map<string, string[]> = new Map();
  const notify2ExcludeInfos: Map<string, Map<string, string[]>> = new Map();

  for (const [notifyName, { source, exclude_infos }] of Object.entries(
    notifyList
  )) {
    const viewNames = get_upstream_views_with_self(sqlMap, source);
    notifyName2views.set(notifyName, viewNames);

    if (!notify2ExcludeInfos.has(notifyName)) {
      notify2ExcludeInfos.set(notifyName, new Map());
    }

    exclude_infos.forEach(({ view, keys }) => {
      notify2ExcludeInfos.get(notifyName)!.set(view, keys);
    });

    viewNames.forEach((viewName) => {
      if (!view2notify.has(viewName)) {
        view2notify.set(viewName, []);
      }
      view2notify.get(viewName)!.push(notifyName);
    });
  }

  return {
    view2notify,
    notifyName2views,
    notify2ExcludeInfos,
  };
}

function get_upstream_views_with_self(sqlMap: TSqlMap, source: string) {
  const stack = [source];
  const result: string[] = [];

  while (stack.length > 0) {
    const current = stack.pop()!;

    if (get_source_type(current) === "view") {
      result.push(current);
    }

    const parents = sqlMap.get(current)!.parents;
    stack.push(...parents);
  }

  return result;
}

function get_source_type(source: string): "view" | "query" {
  return source.slice(3, 4) === "v" ? "view" : "query";
}

function filtersSnapshot(filters: TFilters) {
  const snapshot = JSON.stringify(filters);

  function isDiff(filters: TFilters) {
    return JSON.stringify(filters) !== snapshot;
  }

  return {
    isDiff,
  };
}
