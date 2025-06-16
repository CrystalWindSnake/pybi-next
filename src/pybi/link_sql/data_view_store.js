import "vue";
const j = {
  props: ["sql_map", "notify_list"],
  setup(s, { expose: r, emit: t }) {
    const e = new Map(Object.entries(s.sql_map)), { view2notify: n, notifyName2views: i, notify2ExcludeInfos: g } = O(s.notify_list, e), a = () => {
      t("update:sql_map", Object.fromEntries(e.entries()));
    };
    a();
    const p = (l) => {
      var u;
      (u = n.get(l)) == null || u.forEach((o) => {
        var h;
        const f = (h = i.get(o)) == null ? void 0 : h.map((w) => {
          const { filters: v } = e.get(w), E = Object.fromEntries(
            Object.entries(v).filter(([M]) => {
              var _;
              return !((_ = g.get(o).get(w)) != null && _.includes(M));
            })
          );
          return {
            view: w,
            filters: E
          };
        });
        t(`notify:${o}`, f ?? {});
      });
    };
    function c(l, u, o) {
      const f = e.get(l), h = d(f.filters);
      f.filters = {
        ...f.filters,
        [u]: o
      }, h.isDiff(f.filters) && (p(l), a());
    }
    function y(l, u) {
      const o = e.get(l), f = d(o.filters);
      delete o.filters[u], f.isDiff(o.filters) && (p(l), a());
    }
    r({
      addFilter: c,
      removeFilter: y
    });
  }
};
function O(s, r) {
  const t = /* @__PURE__ */ new Map(), e = /* @__PURE__ */ new Map(), n = /* @__PURE__ */ new Map();
  for (const [i, { source: g, exclude_infos: a }] of Object.entries(
    s
  )) {
    const p = m(r, g);
    e.set(i, p), n.has(i) || n.set(i, /* @__PURE__ */ new Map()), a.forEach(({ view: c, keys: y }) => {
      n.get(i).set(c, y);
    }), p.forEach((c) => {
      t.has(c) || t.set(c, []), t.get(c).push(i);
    });
  }
  return {
    view2notify: t,
    notifyName2views: e,
    notify2ExcludeInfos: n
  };
}
function m(s, r) {
  const t = [r], e = [];
  for (; t.length > 0; ) {
    const n = t.pop();
    q(n) === "view" && e.push(n);
    const i = s.get(n).parents;
    t.push(...i);
  }
  return e;
}
function q(s) {
  return s.slice(3, 4) === "v" ? "view" : "query";
}
function d(s) {
  const r = JSON.stringify(s);
  function t(e) {
    return JSON.stringify(e) !== r;
  }
  return {
    isDiff: t
  };
}
export {
  j as default
};
