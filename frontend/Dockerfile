# Build stage
FROM node:20-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci

ARG VITE_API_URL=/api
ENV VITE_API_URL=${VITE_API_URL}

COPY . .
RUN npm run build

# Runtime
FROM nginx:alpine
EXPOSE 80
COPY --from=builder /app/dist /usr/share/nginx/html
# ← conf.d/default.conf に “server ブロックだけ” を置く
COPY nginx.conf /etc/nginx/conf.d/default.conf
CMD ["nginx", "-g", "daemon off;"]
