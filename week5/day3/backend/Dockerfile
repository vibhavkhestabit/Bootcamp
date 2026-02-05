FROM node:18-alpine
WORKDIR /app
COPY package.json ./
RUN npm install express
COPY . .
CMD ["node", "index.js"]