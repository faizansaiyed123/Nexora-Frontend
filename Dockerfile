FROM node:22.23.3-alpine3.24 AS build
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_API_BUILD_MODE=production
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci
COPY . .

RUN node scripts/validate-api-config.mjs
RUN npm run build

FROM nginx:1.30.5-alpine3.24
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.production.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx","-g","daemon off;"]
