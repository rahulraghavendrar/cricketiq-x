/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        csk: {
          yellow:  '#F9A825',
          gold:    '#FFD600',
          amber:   '#FF8F00',
          navy:    '#0D1B5E',
          dark:    '#1A1A2E',
          cream:   '#FEFBF0',
          warm:    '#FFF8DC',
          light:   '#FFFDE7',
          muted:   '#FFF3C4',
          border:  '#F0D060',
        }
      },
      fontFamily: {
        sans:    ['Inter', 'system-ui', 'sans-serif'],
        display: ['Playfair Display', 'Georgia', 'serif'],
      },
      boxShadow: {
        'gold-sm':  '0 2px 8px rgba(249,168,37,0.20)',
        'gold-md':  '0 4px 20px rgba(249,168,37,0.25)',
        'gold-lg':  '0 8px 40px rgba(249,168,37,0.30)',
        'card':     '0 1px 4px rgba(26,26,46,0.08), 0 4px 16px rgba(26,26,46,0.06)',
        'card-hover': '0 4px 12px rgba(26,26,46,0.12), 0 8px 32px rgba(26,26,46,0.08)',
      },
      backgroundImage: {
        'gold-gradient': 'linear-gradient(135deg, #F9A825 0%, #FFD600 50%, #FF8F00 100%)',
        'cream-gradient': 'linear-gradient(180deg, #FEFBF0 0%, #FFF8DC 100%)',
        'hero-pattern': 'radial-gradient(circle at 20% 50%, rgba(249,168,37,0.08) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(255,214,0,0.06) 0%, transparent 40%)',
      }
    },
  },
  plugins: [],
} 