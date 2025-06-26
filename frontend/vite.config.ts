import { defineConfig } from "vite";
import { nodePolyfills } from "vite-plugin-node-polyfills";

import svgr from 'vite-plugin-svgr';
import react from "@vitejs/plugin-react-swc";
import path from "path";

export default defineConfig({
  server: {
    port: 8000,
    allowedHosts: [""]
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  plugins: [
    react(),
    svgr({
      svgrOptions: {
        exportType: 'default',
      },
      include: '**/*.svg',
    }),
    nodePolyfills({
      include: ["path", "stream", "util"],
      exclude: ["http"],
      globals: {
        Buffer: true,
        global: true,
        process: true,
      },
      overrides: {
        fs: "memfs",
      },
      protocolImports: true,
    }),
  ],
  build: {
    minify: "esbuild",
    rollupOptions: {
      treeshake: true,
      output: {
        manualChunks: (id) => {
          if (id.includes("node_modules")) {
            if (id.includes("react")) return "vendor-react";
            if (id.includes("lodash")) return "vendor-lodash";
            if (id.includes("axios")) return "vendor-axios";
            if (id.includes("@lottiefiles")) return "vendor-lottie";
            return "vendor";
          }
          if (id.includes("@pages")) return "pages";
          if (id.includes("@components")) return "components";
        },
      },
    },
    commonjsOptions: {
      include: [/node_modules/],
    },
  },
});