/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#0f1419',
          surface: '#1a1f2e',
          elevated: '#242b3d',
          border: '#2d3548',
        },
        primary: {
          DEFAULT: '#3b82f6',
          hover: '#2563eb',
          light: '#60a5fa',
        },
        success: {
          DEFAULT: '#10b981',
          light: '#34d399',
        },
        warning: {
          DEFAULT: '#f59e0b',
          light: '#fbbf24',
        },
        danger: {
          DEFAULT: '#ef4444',
          light: '#f87171',
        },
        severity: {
          low: '#10b981',
          medium: '#fbbf24',
          high: '#f97316',
          critical: '#dc2626',
        },
      },
    },
  },
  plugins: [],
};
