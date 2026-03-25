# Build Next.js Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/aegis-portal
COPY aegis-portal/package*.json ./
RUN npm install
COPY aegis-portal/ ./
RUN npm run build

# Final Stage
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/aegis-portal/.next /app/aegis-portal/.next
COPY --from=frontend-builder /app/aegis-portal/public /app/aegis-portal/public
COPY --from=frontend-builder /app/aegis-portal/node_modules /app/aegis-portal/node_modules

# Expose ports
EXPOSE 8000 3000

# Start script
RUN echo '#!/bin/bash\n\
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 &\n\
cd aegis-portal && npm start -- -p 3000\n\
wait -n\n\
exit $?' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
