import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#FF6B6B',
          light: '#FFA07A',
        },
        background: '#FFF9F5',
        text: {
          DEFAULT: '#2D3748',
          light: '#718096',
        },
        accent: '#14B8A6',
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #FF6B6B 0%, #FFA07A 100%)',
      },
    },
  },
  plugins: [],
  darkMode: 'class',
}
export default config

