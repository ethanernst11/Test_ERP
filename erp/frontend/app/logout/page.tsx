"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { env } from "@/lib/env";

export default function LogoutPage() {
  const router = useRouter();

  useEffect(() => {
    const performLogout = async () => {
      try {
        await fetch(`${env.apiBase.replace(/\/$/, "")}/auth/logout/`, {
          method: "POST",
          credentials: "include",
        });
      } catch (error) {
        // Silent failure is acceptable for logout
      }

      document.cookie = "auth_token=; Path=/; Max-Age=0";
      router.replace("/login");
      router.refresh();
    };

    performLogout();
  }, [router]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-surface">
      <div className="rounded-md border border-border bg-white px-6 py-4 text-sm text-slate-600 shadow-sm">
        Signing you out...
      </div>
    </main>
  );
}
