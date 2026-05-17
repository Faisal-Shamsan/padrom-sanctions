// Tailwind CSS v4 shifts configuration to CSS (app/globals.css via @theme{}).
// This file is intentionally minimal — v4 no longer requires content globs
// (automatic content detection) or a JS-based theme definition.
//
// If you need to extend the theme, do it in app/globals.css with:
//   @theme { --color-brand: oklch(…); }
//
// See: https://tailwindcss.com/docs/v4-beta

import type { Config } from "tailwindcss";

const config: Config = {
  content: [], // v4: content scanning is automatic; this list is ignored
};

export default config;
