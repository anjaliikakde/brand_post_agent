FROM node:18-alpine

WORKDIR /app

# Copy package files first for better layer caching
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Start Vite dev server — host 0.0.0.0 so Docker exposes it correctly
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]