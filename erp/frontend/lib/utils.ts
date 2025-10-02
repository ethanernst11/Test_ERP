export function formatCurrency(value: string | number, currency = "USD"): string {
  const numeric = typeof value === "number" ? value : Number(value);
  const formatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  });
  return formatter.format(Number.isFinite(numeric) ? numeric : 0);
}

export function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function parseDate(value: string | undefined, fallback: Date): Date {
  if (!value) return fallback;
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? fallback : parsed;
}

export function toIsoDate(value: Date): string {
  return value.toISOString().slice(0, 10);
}
