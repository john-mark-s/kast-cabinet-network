/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bg-dark': '#0F172A',
        'panel': '#1E293B',
        'border': '#334155',
        'chile-red': '#CE1126',
        'chile-blue': '#0039A6',
      },
    },
  },
  plugins: [],
}
