import { Sidebar } from "@/components/sidebar";
import { Topbar } from "@/components/topbar";

export function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen w-full bg-background">
      <Sidebar approvalsCount={3} />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Topbar />
        <main className="flex-1 overflow-y-auto bg-surface px-8 py-6">{children}</main>
      </div>
    </div>
  );
}
