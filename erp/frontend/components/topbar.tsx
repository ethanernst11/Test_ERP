"use client";

import { useSelectedLayoutSegments } from "next/navigation";

function formatTitle(segments: string[]): string {
  if (segments.length === 0) {
    return "Home";
  }
  const labels = segments.map((segment) =>
    segment
      .split("-")
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(" "),
  );
  return labels.join(" / ");
}

type TopbarProps = {
  rightSlot?: React.ReactNode;
};

export function Topbar({ rightSlot }: TopbarProps) {
  const segments = useSelectedLayoutSegments();
  const title = formatTitle(segments);

  return (
    <header className="flex items-center justify-between border-b border-border bg-white px-6 py-4 shadow-sm">
      <div>
        <h1 className="text-lg font-semibold text-slate-900">{title}</h1>
        <p className="text-sm text-slate-500">Financial operations overview</p>
      </div>
      {rightSlot}
    </header>
  );
}
