# 公式 Playwright イメージ（必要な依存一式入り）で高速＆安定
FROM mcr.microsoft/playwright:v1.44.1-jammy

WORKDIR /workspace

# 作業時はホスト側をボリュームマウントする想定
# ただし初回キャッシュ効かせるため package*.json を先にコピーして npm ci
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm ci

# Playwright ブラウザはイメージに同梱だが、念のため更新に追従
RUN npx playwright install --with-deps

# 待機＆起動スクリプト
COPY docker/e2e/entry.sh /e2e/entry.sh
RUN chmod +x /e2e/entry.sh

ENV API_BASE=http://backend:8000 \
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 \
    CI=1

CMD ["/e2e/entry.sh"]
