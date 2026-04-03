FROM node:20-slim

WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy application code
COPY . .

# Expose port 5173
EXPOSE 5173

# Command to run the development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
