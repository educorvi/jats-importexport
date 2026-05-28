.PHONY: install lint format format-check typecheck build clean

# Install all workspace dependencies
install:
	uv sync --all-packages

# Lint with ruff
lint:
	uv run ruff check .

# Lint with ruff
lint-fix:
	uv run ruff check --fix .

# Format in-place with ruff
format:
	uv run ruff format .

# Check formatting without modifying files
format-check:
	uv run ruff format --check .

# Type-check with ty
typecheck:
	uv run ty check

# Build all workspace packages
build:
	uv build --all-packages

# Remove build artefacts
clean:
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
