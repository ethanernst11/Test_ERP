"use client";

import clsx from "clsx";

type BadgeProps = {
  children: React.ReactNode;
  variant?: "default" | "muted" | "danger";
};

const variants: Record<NonNullable<BadgeProps["variant"]>, string> = {
  default: "bg-accent/10 text-accent border border-accent/20",
  muted: "bg-muted/20 text-muted-foreground border border-muted/30",
  danger: "bg-danger/10 text-danger border border-danger/20",
};

export function Badge({ children, variant = "default" }: BadgeProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium",
        variants[variant],
      )}
    >
      {children}
    </span>
  );
}
