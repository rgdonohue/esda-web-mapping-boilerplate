FROM node:18-slim

# Set working directory
WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY frontend ./frontend
COPY scripts ./scripts

# Make scripts executable
RUN chmod +x scripts/run_frontend.sh

# Expose port
EXPOSE 3000

# Run the application
CMD ["./scripts/run_frontend.sh"] 