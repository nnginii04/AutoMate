/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        app: '#F4F5F7',
        surface: '#FFFFFF',
        'surface-soft': '#F8FAFC',
        'surface-muted': '#DDE2E8',
        foreground: '#111827',
        secondary: '#667085',
        muted: '#98A2B3',
        border: '#DDE2E8',
        primary: '#005BAC',
        'primary-soft': '#E6F0FA',
        cyan: '#00A3B5',
        'cyan-soft': '#E0F7FA',
        success: '#12B76A',
        'success-soft': '#D1FADF',
        warning: '#F79009',
        'warning-soft': '#FEF0C7',
        danger: '#F04438',
        'danger-soft': '#FEE4E2',
        graphite: '#1F2937',
        background: '#F4F5F7',
        card: '#FFFFFF',
      },
      boxShadow: {
        card: '0 1px 2px 0 rgb(16 24 40 / 0.05)',
        'card-hover': '0 2px 8px 0 rgb(16 24 40 / 0.08)',
      },
      maxWidth: {
        console: '1440px',
      },
    },
  },
  plugins: [],
};
