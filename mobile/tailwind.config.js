/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
  ],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        turquoise: '#20b2aa',
        pink: '#ec4899',
        coral: '#f97316',
      },
    },
  },
  plugins: [],
};
