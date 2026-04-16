/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        brand: {
          50:  '#edfcf9',
          100: '#d2f8f0',
          200: '#a9efe3',
          300: '#6fe2d1',
          400: '#35ccba',
          500: '#1bb0a0',
          600: '#138d83',
          700: '#13716a',
          800: '#145a55',
          900: '#154b47',
          950: '#062e2c',
        },
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px -1px rgb(0 0 0 / 0.06)',
        'card-hover': '0 4px 12px 0 rgb(0 0 0 / 0.10), 0 2px 4px -1px rgb(0 0 0 / 0.06)',
        'float': '0 8px 24px -4px rgb(0 0 0 / 0.14)',
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.25rem',
      },
    },
  },
  plugins: [],
}
