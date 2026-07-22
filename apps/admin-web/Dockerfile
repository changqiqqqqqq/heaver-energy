# syntax=docker/dockerfile:1.7

FROM node:20-alpine AS build

ENV PNPM_HOME=/pnpm
ENV PATH="$PNPM_HOME:$PATH"

WORKDIR /workspace

RUN npm install -g pnpm@8.15.9 --registry=https://registry.npmmirror.com

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
COPY apps/admin-web/package.json apps/admin-web/package.json

RUN --mount=type=cache,id=heaver-admin-pnpm-store,target=/pnpm/store \
    pnpm config set store-dir /pnpm/store \
    && pnpm config set registry https://registry.npmmirror.com \
    && pnpm install --frozen-lockfile --filter @heaver-energy/admin-web...

COPY apps/admin-web apps/admin-web

ARG VITE_API_BASE_URL=
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN pnpm --filter @heaver-energy/admin-web build

FROM nginx:1.27-alpine AS runtime

COPY apps/admin-web/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /workspace/apps/admin-web/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1/health || exit 1
