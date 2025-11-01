import { type TComponentId, type TSqlId, type TSqlTable } from "./types";

export class SqlTableResolver {
  private downstreamComponentMap: Map<TSqlId, Set<TComponentId>>;

  constructor(private sqlTable: TSqlTable) {
    this.downstreamComponentMap = new Map();
    this.buildDownstreamComponentMap();
  }

  private buildDownstreamComponentMap(): void {
    // First build dependency graph of sql ids
    const sqlDependencyMap = new Map<TSqlId, Set<TSqlId>>();
    for (const [sqlId, record] of Object.entries(this.sqlTable)) {
      for (const refId of record.references) {
        if (!sqlDependencyMap.has(refId)) {
          sqlDependencyMap.set(refId, new Set());
        }
        sqlDependencyMap.get(refId)!.add(sqlId);
      }
    }

    // Then build component map for each sql id
    for (const [sqlId, _] of Object.entries(this.sqlTable)) {
      const componentIds = new Set<TComponentId>();
      const visited = new Set<TSqlId>();
      const queue = [...(sqlDependencyMap.get(sqlId) || [])];

      while (queue.length > 0) {
        const currentId = queue.shift()!;
        visited.add(currentId);

        // Add components of current sql id
        for (const componentId of this.sqlTable[currentId].components || []) {
          componentIds.add(componentId);
        }

        // Add dependencies to queue
        for (const nextId of sqlDependencyMap.get(currentId) || []) {
          if (!visited.has(nextId)) {
            queue.push(nextId);
          }
        }
      }

      this.downstreamComponentMap.set(sqlId, componentIds);
    }
  }

  public getDownstreamComponentIds(sqlId: TSqlId): Set<TComponentId> {
    return this.downstreamComponentMap.get(sqlId) || new Set();
  }

  public getComponents(sqlId: TSqlId): Set<TComponentId> {
    const record = this.sqlTable[sqlId];
    return record?.components ? new Set(record.components) : new Set();
  }

  public getComponentsToNotify(sqlId: TSqlId, excludeComponentId: TComponentId): Set<TComponentId> {
    const components = new Set<TComponentId>();
    
    // Add current components
    for (const id of this.getComponents(sqlId)) {
      if (id !== excludeComponentId) {
        components.add(id);
      }
    }

    // Add downstream components
    for (const id of this.getDownstreamComponentIds(sqlId)) {
      if (id !== excludeComponentId) {
        components.add(id);
      }
    }

    return components;
  }
}
