"use client";

import { useRouter, useSearchParams } from "next/navigation";

import { toIsoDate } from "@/lib/utils";

type DateRangePickerProps = {
  startDate: Date;
  endDate: Date;
  startParam?: string;
  endParam?: string;
};

export function DateRangePicker({ startDate, endDate, startParam = "start_date", endParam = "end_date" }: DateRangePickerProps) {
  const router = useRouter();
  const search = useSearchParams();

  const handleChange = (value: string, key: string) => {
    const params = new URLSearchParams(search.toString());
    params.set(key, value);
    router.push(`?${params.toString()}`);
  };

  return (
    <div className="flex items-center gap-2 text-sm">
      <label className="flex items-center gap-2">
        <span className="text-slate-600">From</span>
        <input
          type="date"
          className="rounded-md border border-border bg-white px-2 py-1 text-sm"
          value={toIsoDate(startDate)}
          onChange={(event) => handleChange(event.target.value, startParam)}
        />
      </label>
      <label className="flex items-center gap-2">
        <span className="text-slate-600">To</span>
        <input
          type="date"
          className="rounded-md border border-border bg-white px-2 py-1 text-sm"
          value={toIsoDate(endDate)}
          onChange={(event) => handleChange(event.target.value, endParam)}
        />
      </label>
    </div>
  );
}
