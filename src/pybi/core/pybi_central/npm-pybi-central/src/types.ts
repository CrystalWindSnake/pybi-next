export type TSqlId = string;
export type TComponentId = string;

export type TFilterItem = Record<
  TComponentId,
  {
    field: string;
    expr: string;
    value: any;
  }
>;

export type TFilters = Record<TSqlId, TFilterItem>;
export type TSignals = Record<TComponentId, boolean>;
export type TSqlTableRecordType = "data_view" | "query";

export interface TSqlTableRecord {
  template: string;
  type: TSqlTableRecordType;
  references: TSqlId[];
  components?: TComponentId[];
}

export type TSqlTable = Record<TSqlId, TSqlTableRecord>;
