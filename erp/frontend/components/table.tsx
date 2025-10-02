"use client";

import React, { forwardRef, useEffect, useImperativeHandle, useMemo, useState } from "react";

import { CollapsibleRow, TableColumn, TableRowData } from "@/components/collapsible-row";

export type TableHandle = {
  expandAll: () => void;
  collapseAll: () => void;
};

type TableProps = {
  columns: TableColumn[];
  rows: TableRowData[];
  formatValue?: (value: string, columnKey: string) => string;
};

export const Table = forwardRef<TableHandle, TableProps>(function Table({ columns, rows, formatValue }, ref) {
  const expandableKeys = useMemo(() => collectExpandableKeys(rows), [rows]);
  const [expandedKeys, setExpandedKeys] = useState<Set<string>>(new Set(expandableKeys));

  useEffect(() => {
    setExpandedKeys(new Set(expandableKeys));
  }, [expandableKeys, rows]);

  useImperativeHandle(ref, () => ({
    expandAll: () => setExpandedKeys(new Set(expandableKeys)),
    collapseAll: () => setExpandedKeys(new Set()),
  }));

  const toggle = (key: string) => {
    setExpandedKeys((prev) => {
      const next = new Set(prev);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

  const flatRows = useMemo(() => flattenRows(rows, expandedKeys), [rows, expandedKeys]);
  const formatter = formatValue ?? ((value: string) => value);

  return (
    <div className="overflow-hidden rounded-lg border border-border bg-white shadow-sm">
      <table className="min-w-full divide-y divide-border">
        <thead className="bg-surface">
          <tr>
            <th scope="col" className="py-3 pl-4 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Line Item
            </th>
            {columns.map((column) => (
              <th
                key={column.key}
                scope="col"
                className="py-3 pr-4 text-right text-xs font-semibold uppercase tracking-wide text-slate-500"
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border/70">
          {flatRows.map(({ row, level }) => (
            <CollapsibleRow
              key={row.key}
              row={row}
              columns={columns}
              level={level}
              expanded={expandedKeys.has(row.key)}
              onToggle={toggle}
              formatValue={(value, columnKey) => formatter(value, columnKey)}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
});

type FlattenedRow = { row: TableRowData; level: number };

function flattenRows(rows: TableRowData[], expandedKeys: Set<string>, level = 0): FlattenedRow[] {
  const result: FlattenedRow[] = [];
  for (const row of rows) {
    result.push({ row, level });
    const hasChildren = (row.children?.length ?? 0) > 0;
    if (hasChildren && expandedKeys.has(row.key)) {
      result.push(...flattenRows(row.children!, expandedKeys, level + 1));
    }
  }
  return result;
}

function collectExpandableKeys(rows: TableRowData[]): string[] {
  const keys: string[] = [];
  for (const row of rows) {
    if (row.children && row.children.length > 0) {
      keys.push(row.key);
      keys.push(...collectExpandableKeys(row.children));
    }
  }
  return keys;
}
