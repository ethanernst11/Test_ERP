import { z } from "zod";

import { env } from "@/lib/env";

const IncomeStatementLeafRowSchema = z.object({
  key: z.string(),
  label: z.string(),
  amounts: z.array(z.string()),
  total: z.string(),
});

type IncomeStatementLeafRow = z.infer<typeof IncomeStatementLeafRowSchema>;
type IncomeStatementRow = IncomeStatementLeafRow & { children: IncomeStatementLeafRow[] };

const IncomeStatementRowSchema: z.ZodType<IncomeStatementRow> = z.lazy(() =>
  IncomeStatementLeafRowSchema.extend({
    children: z.array(IncomeStatementLeafRowSchema).default([]),
  }),
);

const IncomeStatementResponseSchema = z.object({
  periods: z.array(z.string()),
  period_meta: z.array(
    z.object({
      label: z.string(),
      start: z.string(),
      end: z.string(),
    }),
  ),
  rows: z.array(IncomeStatementRowSchema),
  flat: z.array(
    z.object({
      path: z.string(),
      amounts: z.array(z.string()),
      total: z.string(),
    }),
  ),
  summary: z.object({
    gross_profit: z.array(z.string()),
    net_income: z.array(z.string()),
  }),
});

export type { IncomeStatementRow };
export type IncomeStatementResponse = z.infer<typeof IncomeStatementResponseSchema>;

export function getAuthToken(): string | undefined {
  if (typeof window === "undefined") {
    try {
      const { cookies } = require("next/headers") as typeof import("next/headers");
      return cookies().get("auth_token")?.value;
    } catch (error) {
      return undefined;
    }
  }

  const authCookie = document.cookie
    .split(";")
    .map((entry) => entry.trim())
    .find((entry) => entry.startsWith("auth_token="));

  return authCookie ? decodeURIComponent(authCookie.split("=")[1]) : undefined;
}

async function request<T>(path: string, schema: z.ZodSchema<T>, init?: RequestInit): Promise<T> {
  const authToken = getAuthToken();
  const headers: HeadersInit = {
    Accept: "application/json",
    "Content-Type": "application/json",
    ...(authToken ? { Authorization: `Token ${authToken}` } : {}),
    ...(init?.headers ?? {}),
  };

  const res = await fetch(`${env.apiBase.replace(/\/$/, "")}/${path.replace(/^\//, "")}`, {
    cache: "no-store",
    credentials: "include",
    ...init,
    headers,
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`API request failed (${res.status}): ${detail}`);
  }

  const data = await res.json();
  return schema.parse(data);
}

export async function getIncomeStatement(params: {
  startDate: string;
  endDate: string;
  cadence: "monthly" | "quarterly";
}): Promise<IncomeStatementResponse> {
  const search = new URLSearchParams({
    start_date: params.startDate,
    end_date: params.endDate,
    cadence: params.cadence,
  }).toString();
  return request(`reports/income-statement/?${search}`, IncomeStatementResponseSchema);
}
