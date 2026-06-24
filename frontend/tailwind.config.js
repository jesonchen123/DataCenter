/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#0066CC',
          foreground: '#ffffff',
        },
        brand: {
          900: '#1a1a2e',
        },
        success: {
          DEFAULT: '#52c41a',
          light: '#f6ffed',
          border: '#b7eb8f',
          text: '#389e0d',
        },
        warning: {
          DEFAULT: '#faad14',
          light: '#fff7e6',
          border: '#ffd591',
          text: '#d48806',
        },
        danger: {
          DEFAULT: '#ff4d4f',
          light: '#fff1f0',
          border: '#ffa39e',
          text: '#cf1322',
        },
      },
      fontFamily: {
        sans: ['Inter', 'Noto Sans SC', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
      borderRadius: {
        xl: '12px',
      },
      animation: {
        pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}
