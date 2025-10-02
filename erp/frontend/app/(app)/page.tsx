export default function HomePage() {
  return (
    <section className="space-y-6">
      <header>
        <h2 className="text-2xl font-semibold text-slate-900">Welcome</h2>
        <p className="text-sm text-slate-600">Select a module from the sidebar to begin.</p>
      </header>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {["Income Statement", "Balance Sheet", "Cash Flow", "Trial Balance", "Budgets", "Approvals"].map((name) => (
          <div key={name} className="rounded-lg border border-border bg-white p-4 shadow-sm">
            <h3 className="text-sm font-semibold text-slate-800">{name}</h3>
            <p className="mt-2 text-xs text-slate-500">View consolidated metrics and drill into supporting activity.</p>
          </div>
        ))}
      </div>
    </section>
  );
}
