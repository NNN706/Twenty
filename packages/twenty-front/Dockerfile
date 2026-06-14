# ===========================================================================
# Dockerfile.frontend
# Сборка ТОЛЬКО статики Twenty CRM. Без веб-сервера.
# Итог: образ с файлами в /build, которые вы монтируете в свой Nginx.
# ===========================================================================

# Stage 1: Общие зависимости (из оригинального Dockerfile)
FROM node:24-alpine AS common-deps
WORKDIR /app
COPY ./package.json ./yarn.lock ./.yarnrc.yml ./tsconfig.base.json ./nx.json /app/
COPY ./.yarn/releases /app/.yarn/releases
COPY ./.yarn/patches /app/.yarn/patches
COPY ./packages/twenty-emails/package.json /app/packages/twenty-emails/
COPY ./packages/twenty-server/package.json /app/packages/twenty-server/
COPY ./packages/twenty-server/patches /app/packages/twenty-server/patches
COPY ./packages/twenty-ui/package.json /app/packages/twenty-ui/
COPY ./packages/twenty-shared/package.json /app/packages/twenty-shared/
COPY ./packages/twenty-front/package.json /app/packages/twenty-front/
COPY ./packages/twenty-front-component-renderer/package.json /app/packages/twenty-front-component-renderer/
COPY ./packages/twenty-sdk/package.json /app/packages/twenty-sdk/
COPY ./packages/twenty-client-sdk/package.json /app/packages/twenty-client-sdk/
RUN yarn && yarn cache clean && npx nx reset

# Stage 2: Сборка фронтенда
FROM common-deps AS twenty-front-build
COPY ./packages/twenty-front /app/packages/twenty-front
COPY ./packages/twenty-front-component-renderer /app/packages/twenty-front-component-renderer
COPY ./packages/twenty-ui /app/packages/twenty-ui
COPY ./packages/twenty-shared /app/packages/twenty-shared
COPY ./packages/twenty-sdk /app/packages/twenty-sdk
COPY ./packages/twenty-client-sdk /app/packages/twenty-client-sdk

ARG REACT_APP_SERVER_BASE_URL
ENV REACT_APP_SERVER_BASE_URL=${REACT_APP_SERVER_BASE_URL}
ENV VITE_BUILD_SOURCEMAP=false

RUN npx nx run twenty-front:lingui:extract && \
    npx nx run twenty-front:lingui:compile

RUN NODE_OPTIONS="--max-old-space-size=8192" npx nx build twenty-front

# Stage 3: Финальный образ — ТОЛЬКО файлы статики, без веб-сервера
FROM alpine:3.20 AS twenty-front-static

COPY --from=twenty-front-build /app/packages/twenty-front/build /build

LABEL org.opencontainers.image.source=https://github.com/NNN706/Twenty
LABEL org.opencontainers.image.description="Twenty frontend static files only. Mount /build into your own Nginx."

# Ничего не запускаем. Образ — просто хранилище файлов.
CMD ["echo", "This image contains static files in /build. Mount it into your Nginx."]
