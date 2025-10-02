import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "hsl(0 0% 99%)",
        surface: "hsl(210 20% 98%)",
        border: "hsl(210 15% 90%)",
        accent: "hsl(210 90% 55%)",
        muted: "hsl(210 10% 60%)",
        "muted-foreground": "hsl(210 15% 35%)",
        danger: "hsl(0 70% 50%)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
