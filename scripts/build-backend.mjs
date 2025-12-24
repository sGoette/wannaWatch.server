import esbuild from "esbuild";

await esbuild.build({
  entryPoints: ["backend/server.ts"],
  bundle: true,
  platform: "node",
  target: "node20",
  outfile: "dist/backend/server.js",
  sourcemap: false,
  minify: false,
  format: "cjs",
  external: [
    // native deps you don't want bundled
    "better-sqlite3",
    "sqlite3",
    "node:*"
  ],
});

console.log("✅ Backend bundled");
