# Stage 1: Build React static assets
FROM node:20-alpine AS builder

WORKDIR /app

# Copy lock files and install dependencies cleanly
COPY package*.json ./
RUN npm ci --no-audit --no-fund

# Copy code and build production bundle
COPY . .
RUN npm run build

# Stage 2: Clean runtime stage using tiny Nginx Alpine server (~20MB size!)
FROM nginx:1.25-alpine

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose HTTP port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
