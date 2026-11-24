/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      colors: {
        command: {
          base: '#090d16',
          surface: '#111827',
          elevated: '#151e2e',
          line: '#263247',
        },
      },
      boxShadow: {
        panel: '0 12px 32px rgba(0, 0, 0, 0.22)',
      },
    },
  },
  plugins: [],
}
