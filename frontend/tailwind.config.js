/** @type {import('tailwindcss').Config} */
export default {
    darkMode: 'class',
    content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
  	extend: {
  		fontFamily: {
  			sans: [
  				'Sora',
  				'sans-serif'
  			],
  			mono: [
  				'JetBrains Mono',
  				'monospace'
  			]
  		},
  		colors: {
  			brand: {
  				'400': '#818cf8',
  				'500': '#6366f1',
  				'600': '#4f46e5',
  				'700': '#4338ca'
  			},
  			surface: {
  				DEFAULT: '#0f1117',
  				card: '#161b27',
  				border: '#1e2535',
  				muted: '#1a2030'
  			},
  			text: {
  				primary: '#f1f5f9',
  				secondary: '#94a3b8',
  				muted: '#475569'
  			},
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
  			}
  		},
  		animation: {
  			'fade-in': 'fadeIn 0.3s ease-out',
  			'slide-up': 'slideUp 0.3s ease-out',
  			'slide-in': 'slideIn 0.25s ease-out'
  		},
  		keyframes: {
  			fadeIn: {
  				from: {
  					opacity: 0
  				},
  				to: {
  					opacity: 1
  				}
  			},
  			slideUp: {
  				from: {
  					opacity: 0,
  					transform: 'translateY(12px)'
  				},
  				to: {
  					opacity: 1,
  					transform: 'translateY(0)'
  				}
  			},
  			slideIn: {
  				from: {
  					opacity: 0,
  					transform: 'translateX(-12px)'
  				},
  				to: {
  					opacity: 1,
  					transform: 'translateX(0)'
  				}
  			}
  		},
  		boxShadow: {
  			card: '0 0 0 1px rgba(99,102,241,0.08), 0 4px 24px rgba(0,0,0,0.4)',
  			glow: '0 0 24px rgba(99,102,241,0.25)'
  		},
  		borderRadius: {
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		}
  	}
  },
  plugins: [require("tailwindcss-animate"),('tailwind-scrollbar-hide')],
}