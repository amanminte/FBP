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
        canvas: "#080A0F",
        surface: "#111622",
        "surface-elevated": "#161D2E",
        "surface-card": "#0D111A",
        border: {
          subtle: "rgba(255, 255, 255, 0.07)",
          medium: "rgba(255, 255, 255, 0.12)",
          bright: "rgba(255, 255, 255, 0.20)",
        },
        brand: {
          emerald: "#10B981",
          cyan: "#06B6D4",
          amber: "#F59E0B",
          rose: "#EF4444",
          violet: "#8B5CF6",
          blue: "#3B82F6",
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      boxShadow: {
        'glow-emerald': '0 0 25px -5px rgba(16, 185, 129, 0.25)',
        'glow-cyan': '0 0 25px -5px rgba(6, 182, 212, 0.25)',
        'glow-violet': '0 0 25px -5px rgba(139, 92, 246, 0.25)',
        'glow-blue': '0 0 25px -5px rgba(59, 130, 246, 0.35)',
      }
    },
  },
  plugins: [],
}
