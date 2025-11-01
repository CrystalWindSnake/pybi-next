import { defineConfig } from "tsdown";

export default defineConfig({
  entry: ["./src/index.ts"],
  // unbundle: true,
  // minify: true,
  platform: "browser",
  external: ["instaui"],
  dts: false,

  outputOptions: {
    file: "../static/pybi-central.js",
  },
});
