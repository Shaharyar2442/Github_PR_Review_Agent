.PHONY: run dev install clean test

# Run the FastAPI server in production mode
run:
	python -m api.main

# Run the FastAPI server in development (auto-reload) mode
dev:
	uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

# Install dependencies
install:
	pip install -r requirements.txt
	pip install loguru tenacity

# Clean up pycache
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run a quick test of the LangGraph flow directly
test-graph:
	python -m agent.graph
