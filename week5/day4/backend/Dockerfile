FROM node:18-alpine

WORKDIR /app

# 1. Install dependencies first (Caching layer)
COPY package.json ./
RUN npm install

# 2. Copy the rest of the code
COPY . .

EXPOSE 3000

CMD ["node", "index.js"]