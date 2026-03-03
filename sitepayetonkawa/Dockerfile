FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 4321
CMD ["node_modules/.bin/astro", "dev", "--host", "0.0.0.0"]
