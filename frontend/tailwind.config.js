/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        app: '#F6F7F9',
        surface: '#FFFFFF',
        'surface-soft': '#F1F5F9',
        'surface-muted': '#E5E7EB',
        foreground: '#111827',
        secondary: '#6B7280',
        muted: '#9CA3AF',
        border: '#E5E7EB',
        primary: '#2563EB',
        'primary-soft': '#DBEAFE',
        cyan: '#0891B2',
        'cyan-soft': '#CFFAFE',
        success: '#16A34A',
        'success-soft': '#DCFCE7',
        warning: '#D97706',
        'warning-soft': '#FEF3C7',
        danger: '#DC2626',
        'danger-soft': '#FEE2E2',
        graphite: '#1F2937',
        background: '#F6F7F9',
        card: '#FFFFFF',
      },
      boxShadow: {
        card: '0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px -1px rgb(0 0 0 / 0.06)',
        'card-md': '0 4px 6px -1px rgb(0 0 0 / 0.07), 0 2px 4px -2px rgb(0 0 0 / 0.05)',
      },
    },
  },
  plugins: [],
};
