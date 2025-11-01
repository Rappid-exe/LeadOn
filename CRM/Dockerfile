# syntax=docker/dockerfile:1
FROM node:20-bullseye AS build
WORKDIR /app
COPY packages/twenty-front/package.json packages/twenty-front/yarn.lock ./
RUN yarn install --frozen-lockfile
COPY packages/twenty-front /app
# build with API base configurable at runtime via env-injected file
ARG VITE_HACKATHON_CRM_API_URL=/hackathon/crm
ENV VITE_HACKATHON_CRM_API_URL=$VITE_HACKATHON_CRM_API_URL
RUN yarn build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY packages/twenty-front/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD wget -qO- http://127.0.0.1/ || exit 1
