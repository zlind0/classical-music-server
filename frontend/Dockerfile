FROM node:20

WORKDIR /app

COPY package.json package-lock.json* ./

RUN npm install

EXPOSE 5173

# Default command for development - can be overridden in docker-compose
CMD ["npm", "run", "dev"]
