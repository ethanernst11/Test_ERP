"use client";

import clsx from "clsx";

export type TableColumn = {
  key: string;
  label: string;
  align?: "left" | "right";
};

export type TableRowData = {
  key: string;
  label: string;
  values: string[];
  children?: TableRowData[];
};

type CollapsibleRowProps = {
  row: TableRowData;
  columns: TableColumn[];
  level: number;
  expanded: boolean;
  onToggle: (key: string) => void;
  formatValue: (value: string, columnKey: string) => string;
};

export function CollapsibleRow({ row, columns, level, expanded, onToggle, formatValue }: CollapsibleRowProps) {
  const hasChildren = (row.children?.length ?? 0) > 0;

  return (
    <tr className="border-b border-border/70">
      <td className="whitespace-nowrap py-2 pl-2 pr-4 text-sm text-slate-700" style={{ paddingLeft: `${level * 1.25 + 0.5}rem` }}>
        {hasChildren ? (
          <button
            type="button"
            aria-expanded={expanded}
            onClick={() => onToggle(row.key)}
            className="mr-2 inline-flex h-5 w-5 items-center justify-center rounded border border-border bg-white text-xs font-medium text-slate-600"
          >
            {expanded ? "-" : "+"}
          </button>
        ) : (
          <span className="mr-7 inline-flex w-5 justify-center text-slate-300" aria-hidden="true">-</span>
        )}
        <span className={clsx("font-medium", hasChildren ? "text-slate-800" : "text-slate-600")}>{row.label}</span>
      </td>
      {columns.map((column, index) => (
        <td
          key={`${row.key}-${column.key}`}
          className={clsx(
            "whitespace-nowrap py-2 pr-4 text-sm",
            (column.align ?? "right") === "right" ? "text-right" : "text-left",
            "font-medium text-slate-700",
          )}
        >
          {formatValue(row.values[index] ?? "0", column.key)}
        </td>
      ))}
    </tr>
  );
}
