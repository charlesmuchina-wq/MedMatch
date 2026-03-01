/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: ["class"],
    content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
        extend: {
                borderRadius: {
                        lg: 'var(--radius)',
                        md: 'calc(var(--radius) - 2px)',
                        sm: 'calc(var(--radius) - 4px)'
                },
                colors: {
                        background: 'hsl(var(--background))',
                        foreground: 'hsl(var(--foreground))',
                        card: {
                                DEFAULT: 'hsl(var(--card))',
                                foreground: 'hsl(var(--card-foreground))'
                        },
                        popover: {
                                DEFAULT: 'hsl(var(--popover))',
                                foreground: 'hsl(var(--popover-foreground))'
                        },
                        primary: {
                                DEFAULT: 'hsl(var(--primary))',
                                foreground: 'hsl(var(--primary-foreground))'
                        },
                        secondary: {
                                DEFAULT: 'hsl(var(--secondary))',
                                foreground: 'hsl(var(--secondary-foreground))'
                        },
                        muted: {
                                DEFAULT: 'hsl(var(--muted))',
                                foreground: 'hsl(var(--muted-foreground))'
                        },
                        accent: {
                                DEFAULT: 'hsl(var(--accent))',
                                foreground: 'hsl(var(--accent-foreground))'
                        },
                        destructive: {
                                DEFAULT: 'hsl(var(--destructive))',
                                foreground: 'hsl(var(--destructive-foreground))'
                        },
                        border: 'hsl(var(--border))',
                        input: 'hsl(var(--input))',
                        ring: 'hsl(var(--ring))',
                        chart: {
                                '1': 'hsl(var(--chart-1))',
                                '2': 'hsl(var(--chart-2))',
                                '3': 'hsl(var(--chart-3))',
                                '4': 'hsl(var(--chart-4))',
                                '5': 'hsl(var(--chart-5))'
                        },
                        karau: {
                                bg: '#0a0e1a',
                                card: '#111827',
                                panel: '#0f1629',
                                surface: '#1e2340',
                                border: '#2a2f4a',
                                accent: '#6c3ce0',
                                'accent-bright': '#8b5cf6',
                                emerald: '#10b981',
                                amber: '#eab308',
                                text: '#f5f5f5',
                                muted: '#94a3b8',
                                danger: '#ef4444',
                                blue: '#3b82f6',
                                'deep-blue': '#1e3a5f',
                                purple: '#6c3ce0',
                                'deep-purple': '#2d1b69',
                                green: '#10b981'
                        }
                },
                keyframes: {
                        'accordion-down': {
                                from: {
                                        height: '0'
                                },
                                to: {
                                        height: 'var(--radix-accordion-content-height)'
                                }
                        },
                        'accordion-up': {
                                from: {
                                        height: 'var(--radix-accordion-content-height)'
                                },
                                to: {
                                        height: '0'
                                }
                        },
                        'float-up': {
                                '0%': { opacity: '1', transform: 'translateY(0) scale(1)' },
                                '50%': { opacity: '0.8', transform: 'translateY(-120px) scale(1.2)' },
                                '100%': { opacity: '0', transform: 'translateY(-260px) scale(0.6)' }
                        },
                        'speaker-glow': {
                                '0%, 100%': { boxShadow: '0 0 8px 2px rgba(139, 92, 246, 0.3)' },
                                '50%': { boxShadow: '0 0 20px 6px rgba(139, 92, 246, 0.5)' }
                        }
                },
                animation: {
                        'accordion-down': 'accordion-down 0.2s ease-out',
                        'accordion-up': 'accordion-up 0.2s ease-out',
                        'float-up': 'float-up 2.8s ease-out forwards',
                        'speaker-glow': 'speaker-glow 2s ease-in-out infinite'
                }
        }
  },
  plugins: [require("tailwindcss-animate")],
};