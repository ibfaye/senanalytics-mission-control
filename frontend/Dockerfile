# Sen'Analytics Mission Control — Frontend Dockerfile
# Next.js 16 production build + serve

FROM node:22-alpine AS deps
WORKDIR /app

RUN corepack enable && corepack prepare pnpm@latest --activate
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile --ignore-scripts

FROM node:22-alpine AS builder
WORKDIR /app

RUN corepack enable && corepack prepare pnpm@latest --activate
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile --ignore-scripts

COPY . .

# BACKEND_URL baked at build time for server-side rewrites
ARG BACKEND_URL=http://backend:8000
ENV BACKEND_URL=${BACKEND_URL}

RUN pnpm build

FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV BACKEND_URL=http://backend:8000

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
