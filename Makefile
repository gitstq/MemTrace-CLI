# MemTrace-CLI Makefile

.PHONY: install dev test clean build lint

# Install package in development mode
install:
	pip install -e . --break-system-packages

# Development install with testing tools
dev: install
	pip install pytest pytest-cov --break-system-packages

# Run tests
test:
	python -m pytest tests/ -v --tb=short

# Run tests with coverage
test-cov:
	python -m pytest tests/ -v --cov=memtrace --cov-report=term-missing

# Build distribution packages
build:
	pip install build --break-system-packages
	python -m build

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ __pycache__/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete

# Lint with available tools
lint:
	@echo "Checking Python syntax..."
	python -W ignore -m py_compile memtrace/*.py tests/*.py 2>/dev/null; true

# Quick smoke test
smoke:
	python -c "
from memtrace import MemoryStore, SessionCapture, MemorySearch
s = MemoryStore(db_dir='/tmp/memtrace_test')
sid = s.create_session('test-agent')
print(f'✅ Session created: {sid}')
s.add_message(sid, 'user', 'Hello, World!')
s.add_message(sid, 'assistant', 'Hi there!')
s.add_tag(sid, 'test')
s.end_session(sid)
results = s.search('Hello')
print(f'✅ Search results: {len(results)}')
stats = s.stats()
print(f'✅ Stats: {stats}')
s.close()
print('All smoke tests passed!')
"

# Run the CLI
run:
	memtrace

# Help
help:
	@echo "MemTrace-CLI Makefile targets:"
	@echo "  install   - Install package in dev mode"
	@echo "  dev       - Install with dev dependencies"
	@echo "  test      - Run tests"
	@echo "  build     - Build distribution packages"
	@echo "  clean     - Clean build artifacts"
	@echo "  lint      - Syntax check"
	@echo "  smoke     - Quick smoke test"
	@echo "  run       - Run the CLI"