import { z } from "zod";

import { env } from "@/lib/env";
import { getAuthToken } from "@/lib/api";

const InvoiceLineSchema = z.object({
  id: z.number(),
  description: z.string(),
  quantity: z.string(),
  unit_price: z.string(),
  amount: z.string(),
});

const PaymentSchema = z.object({
  id: z.number(),
  date: z.string(),
  amount: z.string(),
  method: z.string().nullable().optional(),
  reference: z.string().nullable().optional(),
  notes: z.string().nullable().optional(),
});

const CustomerSchema = z.object({
  id: z.number(),
  name: z.string(),
  email: z.string().nullable().optional(),
  billing_address: z.string().nullable().optional(),
});

const InvoiceSchema = z.object({
  id: z.number(),
  number: z.string(),
  description: z.string().nullable().optional(),
  status: z.string(),
  currency: z.string(),
  issue_date: z.string(),
  due_date: z.string(),
  notes: z.string().nullable().optional(),
  customer: CustomerSchema,
  line_items: z.array(InvoiceLineSchema),
  payments: z.array(PaymentSchema),
  total: z.string(),
  amount_paid: z.string(),
  balance_due: z.string(),
});

export type Invoice = z.infer<typeof InvoiceSchema>;

const AgingBucketSchema = z.object({
  count: z.number(),
  balance: z.string(),
});

const AgingResponseSchema = z.object({
  reference_date: z.string(),
  summary: z.record(AgingBucketSchema),
  rows: z.array(
    z.object({
      id: z.number(),
      number: z.string(),
      customer: z.string(),
      balance: z.string(),
      due_date: z.string(),
      days_past_due: z.number(),
      bucket: z.string(),
    }),
  ),
});

async function fetchJson<T>(path: string, schema: z.ZodSchema<T>, options?: { expectResults?: boolean }): Promise<T> {
  const token = getAuthToken();
  const headers: HeadersInit = {
    Accept: "application/json",
    ...(token ? { Authorization: `Token ${token}` } : {}),
  };

  const res = await fetch(`${env.apiBase.replace(/\/$/, "")}/${path.replace(/^\//, "")}`, {
    credentials: "include",
    headers,
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`API request failed (${res.status}): ${detail}`);
  }

  const data = await res.json();
  const payload = options?.expectResults && data && typeof data === "object" && Array.isArray((data as any).results)
    ? (data as any).results
    : data;
  return schema.parse(payload);
}

export async function listInvoices(): Promise<Invoice[]> {
  return fetchJson("invoices/", z.array(InvoiceSchema), { expectResults: true });
}

export async function getInvoice(id: string): Promise<Invoice> {
  return fetchJson(`invoices/${id}/`, InvoiceSchema);
}

export async function recordPayment(invoiceId: number, amount: number): Promise<void> {
  const token = getAuthToken();
  const res = await fetch(`${env.apiBase.replace(/\/$/, "")}/payments/`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(token ? { Authorization: `Token ${token}` } : {}),
    },
    body: JSON.stringify({ invoice: invoiceId, date: new Date().toISOString().slice(0, 10), amount }),
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Payment failed (${res.status}): ${detail}`);
  }
}

export async function createInvoice(payload: {
  customer_id: number;
  issue_date: string;
  due_date: string;
  description?: string;
  notes?: string;
  line_items: Array<{ description: string; unit_price: number; quantity?: number }>;
}): Promise<void> {
  const token = getAuthToken();
  const res = await fetch(`${env.apiBase.replace(/\/$/, "")}/invoices/`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(token ? { Authorization: `Token ${token}` } : {}),
    },
    body: JSON.stringify({ ...payload, number: `INV-${Date.now()}` }),
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Invoice creation failed (${res.status}): ${detail}`);
  }
}

export async function listCustomers(): Promise<z.infer<typeof CustomerSchema>[]> {
  return fetchJson("customers/", z.array(CustomerSchema), { expectResults: true });
}

export async function getAgingBuckets() {
  return fetchJson("reports/ar-aging/", AgingResponseSchema);
}
