.PHONY: install lint lint-fix format format-check typecheck build clean

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

# Export API OpenAPI schema to JSON
applications/api/openapi.json: $(shell find applications/api/src -type f)
	uv run --package api export-openapi applications/api/openapi.json

update-client: applications/api/openapi.json
	uvx openapi-generator-cli generate -g python -i applications/api/openapi.json -o packages/api-client --additional-properties generateSourceCodeOnly=false --additional-properties packageName=jats_importexport_client --additional-properties library=httpx --additional-properties use_path_prefixes_for_title_model_names=false --additional-properties buildSystem=hatchling

# Remove build artefacts
clean:
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
