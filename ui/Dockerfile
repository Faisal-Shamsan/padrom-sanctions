# Multi-stage Next.js build.
# Requires output: "standalone" in next.config.ts for the standalone copy step.

# ── deps ─────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS deps
WORKDIR /app

# Pin pnpm to 10.15.0 — the last major version that supports Node 20.
# pnpm 11+ requires Node 22+ (uses node:sqlite builtin).
RUN corepack enable && corepack prepare pnpm@10.15.0 --activate

COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile

# ── builder ───────────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app

RUN corepack enable && corepack prepare pnpm@10.15.0 --activate

COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
RUN pnpm build

# ── runtime ───────────────────────────────────────────────────────────────────
FROM node:20-alpine AS runtime
WORKDIR /app

RUN addgroup --system nodejs && adduser --system nextjs --ingroup nodejs

# next build --output standalone produces a self-contained server.js
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
# public/ directory must be copied separately (not included in standalone)
COPY --from=builder /app/public ./public

USER nextjs

EXPOSE 3000
ENV PORT=3000 HOSTNAME="0.0.0.0" NEXT_TELEMETRY_DISABLED=1

CMD ["node", "server.js"]