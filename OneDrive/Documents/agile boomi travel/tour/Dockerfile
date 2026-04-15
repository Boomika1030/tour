# Use Node.js base image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files first
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy all project files
COPY . .

# Expose app port (change if needed)
EXPOSE 3000

# Start the app (CHANGE THIS if needed)
CMD ["node", "app.js"]
