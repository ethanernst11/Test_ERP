"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { env } from "@/lib/env";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await fetch(`${env.apiBase.replace(/\/$/, "")}/auth/login/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail || "Unable to login");
      }

      const data = await response.json();
      const token = data?.token as string | undefined;

      if (token) {
        const maxAge = 60 * 60 * 24 * 7; // 7 days
        const secure = window.location.protocol === "https:" ? "; Secure" : "";
        document.cookie = `auth_token=${encodeURIComponent(token)}; Path=/; Max-Age=${maxAge}${secure}`;
      }

      router.replace("/reports/income-statement");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-surface px-4">
      <div className="w-full max-w-md rounded-lg border border-border bg-white p-6 shadow-lg">
        <h1 className="text-xl font-semibold text-slate-900">Sign in</h1>
        <p className="mt-1 text-sm text-slate-500">Use one of the seeded demo accounts to continue.</p>
        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          <div className="space-y-2">
            <label htmlFor="username" className="block text-sm font-medium text-slate-700">
              Username
            </label>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              required
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              className="w-full rounded-md border border-border px-3 py-2 text-sm text-slate-900 focus:border-accent focus:outline-none"
            />
          </div>
          <div className="space-y-2">
            <label htmlFor="password" className="block text-sm font-medium text-slate-700">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="w-full rounded-md border border-border px-3 py-2 text-sm text-slate-900 focus:border-accent focus:outline-none"
            />
          </div>
          {error ? (
            <p className="text-sm text-danger">{error}</p>
          ) : (
            <p className="text-sm text-slate-500">
              Demo accounts: <code className="rounded bg-surface px-1">admin</code>, <code className="rounded bg-surface px-1">accountant</code>,
              <code className="rounded bg-surface px-1">viewer</code>. Password:
              <code className="ml-1 rounded bg-surface px-1">changeme123</code>
            </p>
          )}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-accent px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-accent/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>
      </div>
    </main>
  );
}
