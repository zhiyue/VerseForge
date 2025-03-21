/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1677ff',
          dark: '#0958d9',
          light: '#4096ff',
        },
        secondary: {
          DEFAULT: '#666666',
          dark: '#333333',
          light: '#999999',
        },
        success: {
          DEFAULT: '#52c41a',
          dark: '#389e0d',
          light: '#73d13d',
        },
        warning: {
          DEFAULT: '#faad14',
          dark: '#d48806',
          light: '#ffc53d',
        },
        error: {
          DEFAULT: '#ff4d4f',
          dark: '#f5222d',
          light: '#ff7875',
        },
      },
      spacing: {
        'header': '64px',
        'sidebar': '200px',
        'sidebar-collapsed': '80px',
      },
      zIndex: {
        'header': 1000,
        'sidebar': 900,
        'modal': 1100,
        'notification': 1200,
      },
      animation: {
        'spin-slow': 'spin 3s linear infinite',
      },
    },
  },
  plugins: [],
  // 与Ant Design配合使用
  corePlugins: {
    preflight: false,
  },
  important: true,
}