import Link from "next/link";
import { notFound } from "next/navigation";

import { InvoicePaymentForm } from "@/components/invoice-payment-form";
import { getInvoice } from "@/lib/invoices";
import { formatCurrency } from "@/lib/utils";

export default async function InvoiceDetailPage({ params }: { params: { invoiceId: string } }) {
  let invoice;
  try {
    invoice = await getInvoice(params.invoiceId);
  } catch (error) {
    notFound();
  }

  const issued = new Date(invoice.issue_date).toLocaleDateString();
  const due = new Date(invoice.due_date).toLocaleDateString();
  const balance = Number(invoice.balance_due);

  return (
    <section className="space-y-6">
      <Link href="/revenue/invoices" className="text-sm text-accent hover:underline">
        ← Back to Invoices
      </Link>

      <div className="rounded-lg border border-border bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">Invoice #{invoice.number}</h1>
            <p className="text-sm text-slate-600">
              {invoice.customer.name} · {invoice.customer.email}
            </p>
          </div>
          <div className="text-right text-sm text-slate-500">
            <p>Issued: {issued}</p>
            <p>Due: {due}</p>
            <p>Status: <span className="font-medium capitalize text-slate-700">{invoice.status}</span></p>
          </div>
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          <SummaryCard label="Invoice Total" value={formatCurrency(invoice.total)} />
          <SummaryCard label="Paid" value={formatCurrency(invoice.amount_paid)} />
          <SummaryCard label="Balance Due" value={formatCurrency(invoice.balance_due)} />
        </div>

        <div className="mt-6">
          <InvoicePaymentForm invoiceId={invoice.id} balance={balance} />
        </div>
      </div>

      <div className="overflow-hidden rounded-lg border border-border bg-white shadow-sm">
        <header className="bg-surface px-6 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
          Line Items
        </header>
        <table className="min-w-full divide-y divide-border">
          <thead className="bg-surface text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-6 py-3 text-left">Description</th>
              <th className="px-6 py-3 text-right">Amount</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border text-sm text-slate-700">
            {invoice.line_items.map((line) => (
              <tr key={line.id}>
                <td className="px-6 py-4">{line.description}</td>
                <td className="px-6 py-4 text-right">{formatCurrency(line.amount)}</td>
              </tr>
            ))}
            <tr>
              <td className="px-6 py-4 text-right font-semibold">Total</td>
              <td className="px-6 py-4 text-right font-semibold">{formatCurrency(invoice.total)}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="overflow-hidden rounded-lg border border-border bg-white shadow-sm">
        <header className="bg-surface px-6 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
          Payments
        </header>
        <table className="min-w-full divide-y divide-border">
          <thead className="bg-surface text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-6 py-3 text-left">Date</th>
              <th className="px-6 py-3 text-left">Method</th>
              <th className="px-6 py-3 text-left">Reference</th>
              <th className="px-6 py-3 text-right">Amount</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border text-sm text-slate-700">
            {invoice.payments.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-6 py-4 text-sm text-slate-500">
                  No payments recorded.
                </td>
              </tr>
            ) : (
              invoice.payments.map((payment) => (
                <tr key={payment.id}>
                  <td className="px-6 py-4">{new Date(payment.date).toLocaleDateString()}</td>
                  <td className="px-6 py-4">{payment.method ?? ""}</td>
                  <td className="px-6 py-4">{payment.reference ?? ""}</td>
                  <td className="px-6 py-4 text-right">{formatCurrency(payment.amount)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function SummaryCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-border bg-surface px-4 py-3">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-2 text-lg font-semibold text-slate-900">{value}</p>
    </div>
  );
}
