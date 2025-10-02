"use client";

import { useMemo, useRef } from "react";

import { DateRangePicker } from "@/components/date-range-picker";
import { Dropdown } from "@/components/dropdown";
import { ExportButtons } from "@/components/export-buttons";
import { Table, TableHandle } from "@/components/table";
import type { TableColumn, TableRowData } from "@/components/collapsible-row";
import type { IncomeStatementResponse } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

const cadenceOptions = [
  { label: "Monthly", value: "monthly" },
  { label: "Quarterly", value: "quarterly" },
];

const viewOptions = [
  { label: "Summary", value: "summary" },
  { label: "Detail", value: "detail" },
];

type IncomeStatementViewProps = {
  data: IncomeStatementResponse;
  startDateIso: string;
  endDateIso: string;
  cadence: "monthly" | "quarterly";
  view: string;
};

export function IncomeStatementView({ data, startDateIso, endDateIso, cadence, view }: IncomeStatementViewProps) {
  const tableRef = useRef<TableHandle>(null);
  const startDate = useMemo(() => new Date(startDateIso), [startDateIso]);
  const endDate = useMemo(() => new Date(endDateIso), [endDateIso]);

  const columns: TableColumn[] = useMemo(
    () => [...data.periods.map((label, index) => ({ key: `period-${index}`, label })), { key: "total", label: "Total" }],
    [data.periods],
  );

  const rows: TableRowData[] = useMemo(() => data.rows.map((row) => mapRow(row)), [data.rows]);

  const handleExportCsv = () => {
    const header = ["Line Item", ...data.periods, "Total"];
    const lines = data.flat.map((row) => [row.path, ...row.amounts, row.total]);
    const csvContent = [header, ...lines]
      .map((line) => line.map((value) => `"${value.replace(/"/g, '""')}"`).join(","))
      .join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "income-statement.csv";
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-slate-900">Income Statement</h2>
          <p className="text-sm text-slate-600">Monitor revenue, cost of goods sold, operating expenses, and profitability.</p>
        </div>
        <ExportButtons onExportCsv={handleExportCsv} onExportPdf={() => console.warn("PDF export pending")} />
      </header>
      <div className="flex flex-wrap items-center gap-4 rounded-lg border border-border bg-white p-4 shadow-sm">
        <DateRangePicker startDate={startDate} endDate={endDate} />
        <Dropdown name="cadence" label="Cadence" options={cadenceOptions} value={cadence} queryParam="cadence" />
        <button
          type="button"
          className="rounded-md border border-border bg-white px-3 py-1.5 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
        >
          Filters
        </button>
        <Dropdown name="view" label="Report View" options={viewOptions} value={view} queryParam="view" />
        <div className="ml-auto flex items-center gap-2">
          <button
            type="button"
            onClick={() => tableRef.current?.expandAll()}
            className="rounded-md border border-border bg-white px-3 py-1.5 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
          >
            Expand All
          </button>
          <button
            type="button"
            onClick={() => tableRef.current?.collapseAll()}
            className="rounded-md border border-border bg-white px-3 py-1.5 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
          >
            Collapse All
          </button>
        </div>
      </div>
      <Table ref={tableRef} rows={rows} columns={columns} formatValue={(value) => formatCurrency(value)} />
    </div>
  );
}

type BackendRow = IncomeStatementResponse["rows"][number];

type BackendChild = BackendRow["children"][number];

function mapRow(row: BackendRow): TableRowData {
  return {
    key: row.key,
    label: row.label,
    values: [...row.amounts, row.total],
    children: row.children?.map((child: BackendChild) => ({
      key: child.key,
      label: child.label,
      values: [...child.amounts, child.total],
    })),
  };
}
