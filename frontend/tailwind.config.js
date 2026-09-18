/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        tactical: {
          bg: "#080D1A",
          panel: "#0D1527",
          card: "#121D36",
          border: "#1E2C4F",
          accent: "#38BDF8",
          glow: "#0284C7",
          green: "#10B981",
          amber: "#F59E0B",
          red: "#EF4444",
          text: "#F8FAFC",
          muted: "#94A3B8"
        }
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', '"Fira Code"', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
