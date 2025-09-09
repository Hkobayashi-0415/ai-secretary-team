# Build stage
FROM node:20-alpine AS builder
WORKDIR /app

COPY package*.json ./
# devDeps 必須（tsc/vite 用）
RUN npm ci

# ★ ここで API 基点を受け取る（デフォルトはローカル）
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=${VITE_API_URL}

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
# Nginx は 80 で待受け
EXPOSE 80

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
CMD ["nginx", "-g", "daemon off;"]
