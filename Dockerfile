FROM node:22-alpine AS build
ARG VITE_API_URL
ARG VITE_API_BUILD_MODE=production
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_API_BUILD_MODE=$VITE_API_BUILD_MODE
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci
COPY . .

RUN node scripts/validate-api-config.mjs
RUN npm run build

FROM nginx:1.29.2-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.production.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx","-g","daemon off;"]
