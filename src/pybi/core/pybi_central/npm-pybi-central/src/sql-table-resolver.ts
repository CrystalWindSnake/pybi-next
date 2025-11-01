import {
  type SqlParserOptions,
  type TSqlId,
  type TSqlTable,
  type TSqlTableRecordType,
} from "./types";

export class SqlTableResolver {
  private sqlTable: TSqlTable;
  private options: SqlParserOptions;
  private dependencyMap: Record<TSqlId, Set<TSqlId>> = {};

  constructor(sqlTable: TSqlTable, options: SqlParserOptions) {
    this.sqlTable = sqlTable;
    this.options = options;

    // 初始化依赖关系
    this.buildDependencies();
  }

  /**
   * 从模板中提取依赖项（如 DataView(dv1) 或 Query(q1)）
   */
  private extractDependencies(template: string): string[] {
    const deps: string[] = [];
    const regex = new RegExp(
      `\\b(?:${this.options.dataViewTagName}|${this.options.queryTagName})\\s*\\(([^)]+)\\)`,
      "g"
    );
    let match;
    while ((match = regex.exec(template))) {
      deps.push(match[1].trim());
    }
    return deps;
  }

  /**
   * 构建完整依赖图
   */
  private buildDependencies() {
    for (const [id, record] of Object.entries(this.sqlTable)) {
      const deps = new Set<TSqlId>([
        ...(record.references || []),
        ...this.extractDependencies(record.template),
      ]);
      this.dependencyMap[id] = deps;
    }
  }

  /**
   * 获取指定 SqlId 的所有依赖（深度优先搜索）
   * @param targetId 目标 SQL ID
   * @param filterType 可选，仅返回指定类型的依赖（如 "data_view"）
   */
  public getAllDependenciesOf(
    targetId: TSqlId,
    filterType?: TSqlTableRecordType
  ): TSqlId[] {
    const visited = new Set<TSqlId>();
    const result: TSqlId[] = [];

    const dfs = (id: TSqlId) => {
      const deps = this.dependencyMap[id];
      if (!deps) return;
      for (const dep of deps) {
        if (visited.has(dep)) continue;
        visited.add(dep);
        if (!filterType || this.sqlTable[dep]?.type === filterType) {
          result.push(dep);
        }
        dfs(dep);
      }
    };

    dfs(targetId);
    return result;
  }
}
