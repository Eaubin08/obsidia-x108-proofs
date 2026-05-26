/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        obs: {
          bg:      '#07090e',
          surface: '#0d1117',
          card:    '#111827',
          border:  '#1e2d3d',
          muted:   '#1a2332',
          kernel:  '#d97706',
          proof:   '#8b5cf6',
          brody:   '#3b82f6',
          memory:  '#06b6d4',
          gencoin: '#10b981',
          world:   '#f59e0b',
          audit:   '#6b7280',
          pass:    '#22c55e',
          hold:    '#eab308',
          block:   '#ef4444',
          text:    '#e2e8f0',
          mtext:   '#94a3b8',
          dtext:   '#475569',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
