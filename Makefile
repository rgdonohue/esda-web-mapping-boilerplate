.PHONY: install start build test lint clean

# Default target
all: install build

# Install dependencies
install:
	npm install

# Start development server
start:
	npm start

# Build for production
build:
	npm run build

# Run tests
test:
	npm test

# Run linting
lint:
	npm run lint

# Clean build artifacts and dependencies
clean:
	rm -rf node_modules
	rm -rf build
	rm -rf coverage

# Help command
help:
	@echo "Available commands:"
	@echo "  make install  - Install project dependencies"
	@echo "  make start    - Start development server"
	@echo "  make build    - Build for production"
	@echo "  make test     - Run tests"
	@echo "  make lint     - Run linting"
	@echo "  make clean    - Clean build artifacts and dependencies"