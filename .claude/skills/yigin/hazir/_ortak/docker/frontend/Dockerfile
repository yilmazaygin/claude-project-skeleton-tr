# Next.js. Build bağlamı proje köküdür.
# dev: kod ./frontend klasöründen bağlanır. prod: standalone çıktı; next.config içinde output: "standalone" gerekir.

FROM node:24-alpine AS base
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1

FROM base AS dev
# node kullanıcısı bilgisayardaki kullanıcıyla aynı kimliği alır; ./frontend altında izinler bozulmaz.
ARG UID=1000
ARG GID=1000
RUN apk add --no-cache shadow \
 && groupmod -o -g "$GID" node \
 && usermod -o -u "$UID" -g "$GID" node \
 && mkdir -p /app/node_modules /app/.next && chown -R node:node /app
USER node
EXPOSE 3000
CMD ["sh", "-c", "npm install && npm run dev -- -H 0.0.0.0"]

FROM base AS deps
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

FROM base AS build
COPY --from=deps /app/node_modules ./node_modules
COPY frontend/ ./
# NEXT_PUBLIC_ ile başlayan değerler build sırasında koda gömülür; canlı compose dosyasında build.args ile verilir.
# Verilmeyenler boş kalır ve ilgili bileşen (Umami, GA4) hiçbir şey yüklemez.
ARG NEXT_PUBLIC_UMAMI_URL=""
ARG NEXT_PUBLIC_UMAMI_WEBSITE_ID=""
ARG NEXT_PUBLIC_GA_ID=""
ARG NEXT_PUBLIC_CEREZ_ONAY_KAYDI=""
ENV NEXT_PUBLIC_UMAMI_URL=$NEXT_PUBLIC_UMAMI_URL \
    NEXT_PUBLIC_UMAMI_WEBSITE_ID=$NEXT_PUBLIC_UMAMI_WEBSITE_ID \
    NEXT_PUBLIC_GA_ID=$NEXT_PUBLIC_GA_ID \
    NEXT_PUBLIC_CEREZ_ONAY_KAYDI=$NEXT_PUBLIC_CEREZ_ONAY_KAYDI
RUN npm run build

FROM base AS prod
ENV NODE_ENV=production HOSTNAME=0.0.0.0 PORT=3000
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static
COPY --from=build --chown=node:node /app/public ./public
USER node
EXPOSE 3000
CMD ["node", "server.js"]
