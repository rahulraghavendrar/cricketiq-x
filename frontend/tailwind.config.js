/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        csk: {
          yellow: '#F9A825',
          gold:   '#FFD600',
          blue:   '#1A237E',
          navy:   '#0D1B5E',
          dark:   '#0A0F2E',
          light:  '#FFF8E1',
        }
      },
    },
  },
  plugins: [],
}