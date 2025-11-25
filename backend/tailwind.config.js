/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        // Monochrome palette - strictly black, white, and grays
        'mono-bg': '#ffffff',
        'mono-text': '#000000',
        'mono-border': '#e4e4e7', // zinc-200
        'mono-gray-50': '#fafafa',
        'mono-gray-100': '#f4f4f5',
        'mono-gray-200': '#e4e4e7',
        'mono-gray-300': '#d4d4d8',
        'mono-gray-400': '#a1a1aa',
        'mono-gray-500': '#71717a',
        'mono-gray-600': '#52525b',
        'mono-gray-700': '#3f3f46',
        'mono-gray-800': '#27272a',
        'mono-gray-900': '#18181b',
      },
    },
  },
  plugins: [],
}
