"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { recordPayment } from "@/lib/invoices";
import { formatCurrency } from "@/lib/utils";

export function InvoicePaymentForm({
  invoiceId,
  balance,
  onSuccess,
}: {
  invoiceId: number;
  balance: number;
  onSuccess?: (payload: { amount: number }) => void;
}) {
  const router = useRouter();
  const [amount, setAmount] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    const numericAmount = Number(amount || "0");
    if (Number.isNaN(numericAmount) || numericAmount <= 0) {
      setError("Enter a valid amount greater than zero");
      return;
    }
    if (numericAmount > balance) {
      setError(`Amount cannot exceed ${formatCurrency(balance)}`);
      return;
    }
    try {
      setSubmitting(true);
      await recordPayment(invoiceId, numericAmount);
      onSuccess?.({ amount: numericAmount });
      router.refresh();
      setAmount("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to record payment");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form className="inline-flex items-center gap-2" onSubmit={handleSubmit}>
      <input
        type="number"
        min="0"
        max={balance}
        step="0.01"
        value={amount}
        onChange={(event) => setAmount(event.target.value)}
        className="w-24 rounded-md border border-border px-2 py-1 text-sm"
        placeholder="0.00"
        disabled={submitting || balance <= 0}
      />
      <button
        type="submit"
        disabled={submitting || balance <= 0}
        className="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-white shadow-sm disabled:bg-accent/40"
      >
        {submitting ? "Saving..." : "Pay"}
      </button>
      {error && <span className="text-xs text-danger">{error}</span>}
    </form>
  );
}
