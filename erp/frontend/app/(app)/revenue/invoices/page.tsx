import Link from "next/link";

import { listInvoices } from "@/lib/invoices";
import { InvoicePaymentForm } from "@/components/invoice-payment-form";
import { formatCurrency } from "@/lib/utils";

export default async function InvoicesPage() {
  const invoices = await listInvoices();
  const outstanding = invoices.reduce((acc, invoice) => acc + Number(invoice.balance_due), 0);

  return (
    <section className="space-y-6">
      <header className="flex flex-col gap-2 rounded-lg border border-border bg-white p-6 shadow-sm sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Accounts Receivable</h1>
          <p className="text-sm text-slate-600">Total outstanding: {formatCurrency(outstanding)}</p>
        </div>
        <Link
          href="/revenue/invoices/new"
          className="inline-flex items-center justify-center rounded-md bg-accent px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-accent/90"
        >
          New Invoice
        </Link>
      </header>

      <div className="overflow-hidden rounded-lg border border-border bg-white shadow-sm">
        <table className="min-w-full divide-y divide-border">
          <thead className="bg-surface text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-6 py-3">Customer</th>
              <th className="px-6 py-3">Invoice Total</th>
              <th className="px-6 py-3">Paid</th>
              <th className="px-6 py-3">Balance Due</th>
              <th className="px-6 py-3">Issued</th>
              <th className="px-6 py-3">Due</th>
              <th className="px-6 py-3 text-right">Record Payment</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border text-sm text-slate-700">
            {invoices.map((invoice) => (
              <tr key={invoice.id} className="hover:bg-surface/60">
                <td className="px-6 py-4">
                  <div className="flex flex-col">
                    <Link href={`/revenue/invoices/${invoice.id}`} className="font-medium text-accent">
                      {invoice.customer.name}
                    </Link>
                    <span className="text-xs text-slate-500">{invoice.customer.email}</span>
                  </div>
                </td>
                <td className="px-6 py-4">{formatCurrency(invoice.total)}</td>
                <td className="px-6 py-4">{formatCurrency(invoice.amount_paid)}</td>
                <td className="px-6 py-4 font-semibold">{formatCurrency(invoice.balance_due)}</td>
                <td className="px-6 py-4 text-slate-500">{new Date(invoice.issue_date).toLocaleDateString()}</td>
                <td className="px-6 py-4 text-slate-500">{new Date(invoice.due_date).toLocaleDateString()}</td>
                <td className="px-6 py-4 text-right">
                  <InvoicePaymentForm
                    invoiceId={invoice.id}
                    balance={Number(invoice.balance_due)}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {invoices.length === 0 && (
          <div className="p-6 text-sm text-slate-500">No invoices yet. Create one to get started.</div>
        )}
      </div>
    </section>
  );
}
