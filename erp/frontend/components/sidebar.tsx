"use client";

import clsx from "clsx";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { Badge } from "@/components/badge";

type SidebarProps = {
  approvalsCount?: number;
};

export function Sidebar({ approvalsCount = 0 }: SidebarProps) {
  const pathname = usePathname();
  const [reportingOpen, setReportingOpen] = useState(true);

  const itemClasses = (href: string) =>
    clsx(
      "block rounded-md px-3 py-2 text-sm font-medium transition", // base
      pathname === href ? "bg-accent/10 text-accent" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
    );

  return (
    <aside className="flex h-full w-64 flex-col border-r border-border bg-surface">
      <div className="px-6 py-5">
        <span className="text-lg font-semibold text-slate-900">ERP</span>
        <p className="mt-1 text-sm text-slate-500">Accounting Workspace</p>
      </div>
      <nav className="flex-1 space-y-2 px-4">
        <Link href="/" className={itemClasses("/")}>
          Home
        </Link>
        <div>
          <button
            type="button"
            onClick={() => setReportingOpen((value) => !value)}
            className="flex w-full items-center justify-between rounded-md px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100"
          >
            <span>Reporting</span>
            <span aria-hidden>{reportingOpen ? "-" : "+"}</span>
          </button>
          {reportingOpen && (
            <div className="mt-1 space-y-1 pl-3">
              <Link href="/reports/income-statement" className={itemClasses("/reports/income-statement")}>
                Income Statement
              </Link>
              <Link href="/reports/balance-sheet" className={itemClasses("/reports/balance-sheet")}>
                Balance Sheet
              </Link>
              <Link href="/reports/cash-flow" className={itemClasses("/reports/cash-flow")}>
                Cash Flow
              </Link>
              <Link href="/reports/trial-balance" className={itemClasses("/reports/trial-balance")}>
                Trial Balance
              </Link>
              <Link href="/reports/budgets" className={itemClasses("/reports/budgets")}>
                Budgets
              </Link>
              <Link href="/reports/analytics" className={itemClasses("/reports/analytics")}>
                Reports
              </Link>
            </div>
          )}
        </div>
        <Link href="/revenue" className={itemClasses("/revenue")}>
          Revenue
        </Link>
        <Link href="/accounting" className={itemClasses("/accounting")}>
          Accounting
        </Link>
        <Link href="/cash-management" className={itemClasses("/cash-management")}>
          Cash Management
        </Link>
        <Link href="/close-checklist" className={itemClasses("/close-checklist")}>
          Close Checklist
        </Link>
        <Link href="/approvals" className={itemClasses("/approvals")}>
          <span className="flex items-center justify-between">
            <span>Approvals</span>
            <Badge variant={approvalsCount > 0 ? "default" : "muted"}>{approvalsCount}</Badge>
          </span>
        </Link>
      </nav>
      <div className="space-y-1 border-t border-border px-4 py-4 text-sm">
        <Link href="/settings" className={itemClasses("/settings")}>
          Settings
        </Link>
        <Link href="/help" className={itemClasses("/help")}>
          Help
        </Link>
        <Link href="/logout" className={itemClasses("/logout")}>
          Logout
        </Link>
      </div>
    </aside>
  );
}
