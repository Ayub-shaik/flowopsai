/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}"
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0b1020",
        card: "#0f1630",
        brand: "#7c9cff"
      }
    }
  },
  plugins: []
};
