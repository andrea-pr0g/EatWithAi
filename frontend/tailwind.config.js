/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        orbitron: ['Orbitron', 'sans-serif'],
        space: ['Space Grotesk', 'sans-serif'],
        sans: ['Plus Jakarta Sans', 'Inter', 'sans-serif'],
      },
      colors: {
        cosmos: {
          950: '#030712',
          900: '#060b1e',
          850: '#0a102b',
          800: '#0f172a',
          700: '#1e293b',
          600: '#334155',
        },
        nebula: {
          cyan: '#06b6d4',
          brightCyan: '#22d3ee',
          violet: '#8b5cf6',
          brightViolet: '#a855f7',
          pink: '#ec4899',
          amber: '#f59e0b',
        }
      },
      backgroundImage: {
        'radial-gradient': 'radial-gradient(circle at center, var(--tw-gradient-stops))',
        'stars-gradient': 'linear-gradient(to bottom, #030712, #070e28, #030712)',
        'cosmic-glow': 'radial-gradient(ellipse at 50% -20%, rgba(120, 119, 198, 0.25), transparent 70%)',
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float-slow': 'float 6s ease-in-out infinite',
        'glow-pulse': 'glow 3s ease-in-out infinite alternate',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 15px rgba(6, 182, 212, 0.3)' },
          '100%': { boxShadow: '0 0 35px rgba(139, 92, 246, 0.6)' },
        }
      },
      boxShadow: {
        'neon-cyan': '0 0 20px -3px rgba(6, 182, 212, 0.45)',
        'neon-violet': '0 0 25px -3px rgba(139, 92, 246, 0.45)',
        'cosmic-card': '0 20px 50px -10px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(255, 255, 255, 0.08)',
      }
    },
  },
  plugins: [],
}
