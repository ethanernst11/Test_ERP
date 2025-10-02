"use client";

import clsx from "clsx";
import { useRouter, useSearchParams } from "next/navigation";

export type DropdownOption = {
  label: string;
  value: string;
};

type DropdownProps = {
  name: string;
  label?: string;
  options: DropdownOption[];
  value: string;
  queryParam?: string;
};

export function Dropdown({ name, label, options, value, queryParam }: DropdownProps) {
  const router = useRouter();
  const search = useSearchParams();

  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    if (!queryParam) return;
    const params = new URLSearchParams(search.toString());
    params.set(queryParam, event.target.value);
    router.push(`?${params.toString()}`);
  };

  return (
    <label className="flex items-center gap-2 text-sm font-medium text-slate-600">
      {label && <span>{label}</span>}
      <select
        name={name}
        value={value}
        onChange={handleChange}
        className={clsx(
          "rounded-md border border-border bg-white px-2.5 py-1.5 text-sm text-slate-900 shadow-sm",
          "focus:border-accent focus:outline-none"
        )}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}
