import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  build: {
    sourcemap: false,
    lib: {
      entry: path.resolve(__dirname, "src/data_view_store.ts"),
      name: "data_view_store",
      fileName: "data_view_store",
    },
    outDir: "../src/pybi/link_sql",
    emptyOutDir: false,
    rollupOptions: {
      external: ["vue"],
      output: [
        {
          format: "es",
        },
      ],
    },
  },
});
