/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          300: '#60a5fa',
          500: '#2563eb',
          900: '#1e3a5f',
        },
        accent: '#f59e0b',
        success: '#22c55e',
        danger: '#ef4444',
        warning: '#f97316',
      }
    },
  },
  plugins: [],
}
