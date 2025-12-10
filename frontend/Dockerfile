# Build stage
# glibc ベースで rollup の optional binary 問題を回避
FROM node:20-bullseye AS builder
# Cache-buster for CI: change this to force rebuilds when code/tests change
ARG FRONTEND_BUILD_ID=dev
LABEL ai-secretary.frontend.build_id=${FRONTEND_BUILD_ID}
WORKDIR /app

COPY package*.json ./
# Prefer reproducible ci, but fall back to install when lock got updated by overrides
RUN npm ci --ignore-scripts || npm install --ignore-scripts
# Workaround for npm optional dependency bug on musl (rollup native binary)
RUN npm install --ignore-scripts --no-save @rollup/rollup-linux-x64-musl@4.46.3 || true

# Allow overriding API origin at build time (default: relative '/api')
ARG VITE_API_URL=/api
ENV VITE_API_URL=${VITE_API_URL}

COPY . .
RUN npm run build

# Runtime stage
FROM nginx:alpine
WORKDIR /usr/share/nginx/html

COPY --from=builder /app/dist ./

# Use conf.d convention for server block
RUN rm -f /etc/nginx/conf.d/default.conf || true
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"] 
