FROM node:24-bookworm-slim AS web
WORKDIR /web
COPY operator/web/package*.json ./
RUN npm ci --ignore-scripts --no-audit --no-fund
COPY operator/web/ ./
RUN npm run build

FROM node:24-bookworm-slim
ENV NODE_ENV=production
WORKDIR /app
COPY operator/gateway/package*.json ./
RUN npm ci --omit=dev --ignore-scripts --no-audit --no-fund && npm cache clean --force
COPY operator/gateway/src ./src
COPY operator/gateway/test ./test
COPY operator/tools ./tools
COPY operator/db/migrations ./migrations
COPY operator/config.acceptance.json ./config.acceptance.json
COPY schemas/event.schema.json ./event.schema.json
COPY config/emulator/vmt-cameras.json ./vmt-cameras.json
COPY --from=web /web/dist ./public
USER node
EXPOSE 3000
CMD ["npm","start"]
