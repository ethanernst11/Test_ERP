"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { createInvoice, listCustomers } from "@/lib/invoices";
import { formatCurrency, toIsoDate } from "@/lib/utils";

type LineItemInput = { description: string; unit_price: string; quantity: string };

export default function NewInvoicePage() {
  const router = useRouter();
  const [customers, setCustomers] = useState<Array<{ id: number; name: string; email?: string | null }>>([]);
  const [customerId, setCustomerId] = useState<number | undefined>();
  const [issueDate, setIssueDate] = useState<string>(() => toIsoDate(new Date()));
  const [dueDate, setDueDate] = useState<string>(() => toIsoDate(new Date()));
  const [lineItems, setLineItems] = useState<LineItemInput[]>([{ description: "", unit_price: "0", quantity: "1" }]);
  const [description, setDescription] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const loadCustomers = async () => {
      try {
        const data = await listCustomers();
        setCustomers(data);
        if (!customerId && data.length > 0) {
          setCustomerId(data[0].id);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load customers");
      }
    };
    loadCustomers();
  }, [customerId]);

  const total = useMemo(() => {
    return lineItems.reduce((acc, item) => {
      const unit = Number(item.unit_price || 0);
      const qty = Number(item.quantity || 1);
      return acc + unit * qty;
    }, 0);
  }, [lineItems]);

  const handleAddLine = () => {
    setError(null);
    setLineItems((items) => [...items, { description: "", unit_price: "0", quantity: "1" }]);
  };

  const handleRemoveLine = (index: number) => {
    setError(null);
    setLineItems((items) => items.filter((_, i) => i !== index));
  };

  const handleChangeLine = (index: number, field: keyof LineItemInput, value: string) => {
    setError(null);
    setLineItems((items) => items.map((item, i) => (i === index ? { ...item, [field]: value } : item)));
  };

  const handleSubmit = async () => {
    if (!customerId) {
      setError("Customer is required");
      return;
    }
    if (new Date(dueDate) < new Date(issueDate)) {
      setError("Due date cannot be earlier than issue date");
      return;
    }
    const prepared = lineItems
      .filter((item) => item.description.trim() && Number(item.unit_price) > 0)
      .map((item) => ({
        description: item.description.trim(),
        unit_price: Number(item.unit_price),
        quantity: Number(item.quantity || "1") || 1,
      }));

    if (prepared.length === 0) {
      setError("Add at least one line item with an amount");
      return;
    }

    try {
      setSaving(true);
      await createInvoice({
        customer_id: customerId,
        issue_date: issueDate,
        due_date: dueDate,
        description: description.trim() || undefined,
        notes: notes.trim() || undefined,
        line_items: prepared,
      });
      router.replace("/revenue/invoices");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create invoice");
    } finally {
      setSaving(false);
    }
  };

  const estimatedTotal = formatCurrency(total);

  return (
    <section className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-slate-900">Create Invoice</h1>
        <p className="text-sm text-slate-600">Define the billing customer, issued and due dates, and itemize the work being invoiced.</p>
      </header>

        <div className="space-y-6 rounded-lg border border-border bg-white p-6 shadow-sm">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500">Customer</label>
            <select
              className="mt-2 w-full rounded-md border border-border px-3 py-2 text-sm"
              value={customerId}
              onChange={(event) => setCustomerId(Number(event.target.value))}
            >
              {customers.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.name}
                  {customer.email ? ` · ${customer.email}` : ""}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500">Issued Date</label>
            <input
              type="date"
              value={issueDate}
              onChange={(event) => {
                const value = event.target.value;
                setIssueDate(value);
                if (new Date(dueDate) < new Date(value)) {
                  setDueDate(value);
                }
              }}
              className="mt-2 w-full rounded-md border border-border px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500">Due Date</label>
            <input
              type="date"
              value={dueDate}
              onChange={(event) => setDueDate(event.target.value)}
              className="mt-2 w-full rounded-md border border-border px-3 py-2 text-sm"
              min={issueDate}
            />
          </div>
          <div className="sm:col-span-2">
            <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500">Estimated Total</label>
            <div className="mt-2 rounded-md border border-border bg-surface px-3 py-2 text-sm font-semibold text-slate-800">
              {estimatedTotal}
            </div>
          </div>
          <div className="sm:col-span-2">
            <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500">Description</label>
            <textarea
              className="mt-2 h-20 w-full rounded-md border border-border px-3 py-2 text-sm"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
            />
          </div>
          <div className="sm:col-span-2">
            <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500">Notes</label>
            <textarea
              className="mt-2 h-20 w-full rounded-md border border-border px-3 py-2 text-sm"
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
            />
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-700">Line Items</h2>
            <button
              type="button"
              onClick={handleAddLine}
              className="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-white shadow-sm"
            >
              Add Item
            </button>
          </div>
          <div className="space-y-3">
            {lineItems.map((item, index) => (
              <div key={index} className="grid gap-3 rounded-md border border-border p-3 sm:grid-cols-12">
                <div className="sm:col-span-6">
                  <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500">Description</label>
                  <input
                    type="text"
                    value={item.description}
                    onChange={(event) => handleChangeLine(index, "description", event.target.value)}
                    className="mt-2 w-full rounded-md border border-border px-3 py-2 text-sm"
                    placeholder="e.g. Platform subscription"
                  />
                </div>
                <div className="sm:col-span-3">
                  <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500">Quantity</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={item.quantity}
                    onChange={(event) => handleChangeLine(index, "quantity", event.target.value)}
                    className="mt-2 w-full rounded-md border border-border px-3 py-2 text-sm"
                  />
                </div>
                <div className="sm:col-span-3">
                  <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500">Amount (USD)</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={item.unit_price}
                    onChange={(event) => handleChangeLine(index, "unit_price", event.target.value)}
                    className="mt-2 w-full rounded-md border border-border px-3 py-2 text-sm"
                  />
                </div>
                {lineItems.length > 1 && (
                  <div className="sm:col-span-12 text-right">
                    <button
                      type="button"
                      onClick={() => handleRemoveLine(index)}
                      className="text-sm text-danger hover:underline"
                    >
                      Remove
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {error && <div className="rounded-md border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">{error}</div>}

        <div className="flex justify-end gap-3">
          <button
            type="button"
            className="rounded-md border border-border px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
            onClick={() => router.back()}
            disabled={saving}
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={saving || !customerId}
            className="rounded-md bg-accent px-4 py-2 text-sm font-semibold text-white shadow-sm disabled:bg-accent/50"
          >
            {saving ? "Creating..." : "Create Invoice"}
          </button>
        </div>
      </div>
    </section>
  );
}
