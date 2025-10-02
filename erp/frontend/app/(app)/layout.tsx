import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { Shell } from "@/components/shell";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const hasToken = cookies().get("auth_token")?.value;
  if (!hasToken) {
    redirect("/login");
  }

  return <Shell>{children}</Shell>;
}
