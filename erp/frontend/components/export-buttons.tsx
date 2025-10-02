"use client";

type ExportButtonsProps = {
  onExportCsv?: () => void;
  onExportPdf?: () => void;
};

export function ExportButtons({ onExportCsv, onExportPdf }: ExportButtonsProps) {
  return (
    <div className="flex items-center gap-2">
      <button
        type="button"
        onClick={onExportCsv}
        className="rounded-md border border-border bg-white px-3 py-1.5 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
      >
        Export CSV
      </button>
      <button
        type="button"
        onClick={onExportPdf}
        className="rounded-md border border-border bg-white px-3 py-1.5 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
        title="PDF export coming soon"
      >
        Export PDF
      </button>
    </div>
  );
}
