import { expect, test, describe } from "vitest";
import { SqlTableResolver } from "./sql-table-resolver";
import type { TSqlTable } from "./types";

describe("getDownstreamComponentIds", () => {
  test("returns empty array for sql id with no downstream", () => {
    const sqlTable: TSqlTable = {
      q1: {
        template: "",
        type: "query",
        references: [],
        components: ["c1"],
      },
    };
    const resolver = new SqlTableResolver(sqlTable);
    expect(Array.from(resolver.getDownstreamComponentIds("q1"))).toEqual([]);
  });

  test("returns direct downstream component ids", () => {
    const sqlTable: TSqlTable = {
      q1: {
        template: "",
        type: "query",
        references: [],
        components: [],
      },
      q2: {
        template: "",
        type: "query",
        references: ["q1"],
        components: ["c2", "c3"],
      },
      q3: {
        template: "",
        type: "query",
        references: ["q1"],
        components: ["c3", "c4"],
      },
    };
    const resolver = new SqlTableResolver(sqlTable);
    expect(Array.from(resolver.getDownstreamComponentIds("q1")).sort()).toEqual(
      ["c2", "c3", "c4"]
    );
  });

  test("returns all downstream component ids in complex dependency graph", () => {
    const sqlTable: TSqlTable = {
      q1: {
        template: "",
        type: "query",
        references: [],
        components: [],
      },
      q2: {
        template: "",
        type: "query",
        references: ["q1"],
        components: ["c1", "c2"],
      },
      q3: {
        template: "",
        type: "query",
        references: ["q2"],
        components: ["c2", "c3"],
      },
      q4: {
        template: "",
        type: "query",
        references: ["q1", "q3"],
        components: ["c3", "c4"],
      },
    };
    const resolver = new SqlTableResolver(sqlTable);
    expect(Array.from(resolver.getDownstreamComponentIds("q1")).sort()).toEqual(
      ["c1", "c2", "c3", "c4"]
    );
  });

  test("deduplicates component ids", () => {
    const sqlTable: TSqlTable = {
      q1: {
        template: "",
        type: "query",
        references: [],
        components: [],
      },
      q2: {
        template: "",
        type: "query",
        references: ["q1"],
        components: ["c1", "c2"],
      },
      q3: {
        template: "",
        type: "query",
        references: ["q1"],
        components: ["c2", "c3"],
      },
      q4: {
        template: "",
        type: "query",
        references: ["q2", "q3"],
        components: ["c1", "c3", "c4"],
      },
    };
    const resolver = new SqlTableResolver(sqlTable);
    expect(Array.from(resolver.getDownstreamComponentIds("q1")).sort()).toEqual(
      ["c1", "c2", "c3", "c4"]
    );
  });
});

describe("getComponents", () => {
  test("returns empty set for sql id with no components", () => {
    const sqlTable: TSqlTable = {
      q1: {
        template: "",
        type: "query",
        references: [],
        components: [],
      },
    };
    const resolver = new SqlTableResolver(sqlTable);
    expect(Array.from(resolver.getComponents("q1"))).toEqual([]);
  });

  test("returns direct component ids", () => {
    const sqlTable: TSqlTable = {
      q1: {
        template: "",
        type: "query",
        references: [],
        components: ["c1", "c2"],
      },
    };
    const resolver = new SqlTableResolver(sqlTable);
    expect(Array.from(resolver.getComponents("q1")).sort()).toEqual([
      "c1",
      "c2",
    ]);
  });

  test("returns empty set for non-existent sql id", () => {
    const sqlTable: TSqlTable = {
      q1: {
        template: "",
        type: "query",
        references: [],
        components: ["c1"],
      },
    };
    const resolver = new SqlTableResolver(sqlTable);
    expect(Array.from(resolver.getComponents("invalid_id"))).toEqual([]);
  });
});

describe("getComponentsToNotify", () => {
  test("returns components excluding specified id", () => {
    const sqlTable: TSqlTable = {
      q1: {
        template: "",
        type: "query",
        references: [],
        components: ["c1", "c2"],
      },
      q2: {
        template: "",
        type: "query",
        references: ["q1"],
        components: ["c2", "c3"],
      },
    };
    const resolver = new SqlTableResolver(sqlTable);
    expect(Array.from(resolver.getComponentsToNotify("q1", "c2")).sort()).toEqual(["c1", "c3"]);
  });

  test("returns all components when exclude id not present", () => {
    const sqlTable: TSqlTable = {
      q1: {
        template: "",
        type: "query",
        references: [],
        components: ["c1", "c2"],
      },
    };
    const resolver = new SqlTableResolver(sqlTable);
    expect(Array.from(resolver.getComponentsToNotify("q1", "c3")).sort()).toEqual(["c1", "c2"]);
  });

  test("handles complex dependency graph", () => {
    const sqlTable: TSqlTable = {
      q1: {
        template: "",
        type: "query",
        references: [],
        components: ["c1"],
      },
      q2: {
        template: "",
        type: "query",
        references: ["q1"],
        components: ["c2", "c3"],
      },
      q3: {
        template: "",
        type: "query",
        references: ["q2"],
        components: ["c3", "c4"],
      },
    };
    const resolver = new SqlTableResolver(sqlTable);
    expect(Array.from(resolver.getComponentsToNotify("q1", "c3")).sort()).toEqual(["c1", "c2", "c4"]);
  });
});
