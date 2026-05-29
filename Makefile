ccred=\033[0;31m
ccyellow=\033[0;33m
ccend=\033[0m
ccgreen=\033[0;32m

.PHONY: install lint lint-fix format format-check typecheck test build clean build-image push-image generate-client

check_dependency_%:
	@printf '\e$(ccyellow)%-40s' "Checking dependency $*... "
	@command -v $* >/dev/null 2>&1 && echo -e "$(ccgreen)found$(ccend)" || (echo -e "$(ccred)$* is not in PATH, please install it$(ccend)" && exit 1)


# Install all workspace dependencies
install:
	uv sync --all-packages --all-groups

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

# Run tests in all packages
test:
	uv run pytest

# Build all workspace packages
build:
	uv build --all-packages

# Export API OpenAPI schema to JSON
applications/api/openapi.json: $(shell find applications/api/src -type f)
	uv run --package api export-openapi applications/api/openapi.json

update-client: generate-client

generate-client: check_dependency_jq applications/api/openapi.json
	@VERSION=$$(jq -r .info.version applications/api/openapi.json) && \
	uvx openapi-generator-cli generate -g python -i applications/api/openapi.json -o packages/api-client --additional-properties generateSourceCodeOnly=false --additional-properties packageName=jats_importexport_client --additional-properties library=httpx --additional-properties use_path_prefixes_for_title_model_names=false --additional-properties buildSystem=hatchling --additional-properties packageVersion=$$VERSION
# Remove build artefacts
clean:
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +

build-image:
	docker build . -t ghcr.io/educorvi/jats-importexport:latest

push-image: build-image
	docker push ghcr.io/educorvi/jats-importexport:latest
