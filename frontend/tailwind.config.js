/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef4ff",
          100: "#dbe6fe",
          200: "#bfd3fe",
          300: "#93b4fd",
          400: "#6090fa",
          500: "#3d6ef5",
          600: "#2650e9",
          700: "#1f3fd4",
          800: "#2035ab",
          900: "#203287",
        },
      },
    },
  },
  plugins: [],
};
