API_VERSION=$(shell python3 -c "import sys; sys.path.insert(0, 'applications/api/src'); from api.config import APIConfig; print(APIConfig.API_VERSION)")

ccred=\033[0;31m
ccyellow=\033[0;33m
ccend=\033[0m
ccgreen=\033[0;32m

.PHONY: install lint lint-fix format format-check typecheck test build clean build-image push-image generate-client get-api-version

check_dependency_%:
	@printf '$(ccyellow)%-40s' "Checking dependency $*... "
	@command -v $* >/dev/null 2>&1 && echo -e "$(ccgreen)found$(ccend)" || (echo -e "$(ccred)$* is not in PATH, please install it$(ccend)" && exit 1)


# Install all workspace dependencies
install: check_dependency_uv
	uv sync --all-packages --all-groups

# Lint with ruff
lint: check_dependency_uv
	uv run ruff check .

# Lint with ruff
lint-fix: check_dependency_uv
	uv run ruff check --fix .

# Format in-place with ruff
format: check_dependency_uv
	uv run ruff format .

# Check formatting without modifying files
format-check: check_dependency_uv
	uv run ruff format --check .

# Type-check with ty
typecheck: check_dependency_uv
	uv run ty check

# Run tests in all packages
test: check_dependency_uv
	uv run pytest

# Build all workspace packages
build: check_dependency_uv
	uv build --all-packages

# Export API OpenAPI schema to JSON
applications/api/openapi.json: check_dependency_uv $(shell find applications/api/src -type f)
	uv run --package api export-openapi applications/api/openapi.json

update-client: generate-client

generate-client: check_dependency_jq check_dependency_uvx applications/api/openapi.json
	@VERSION=$$(jq -r .info.version applications/api/openapi.json) && \
	uvx openapi-generator-cli generate -g python -i applications/api/openapi.json -o packages/api-client --additional-properties generateSourceCodeOnly=false --additional-properties packageName=jats_importexport_client --additional-properties use_path_prefixes_for_title_model_names=false --additional-properties buildSystem=setuptools --additional-properties packageVersion=$$VERSION

# Remove build artefacts
clean:
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +

get-api-version:
	@echo $(API_VERSION)

build-image: check_dependency_docker
	docker buildx build --platform linux/amd64 . -t ghcr.io/educorvi/jats-importexport:latest
	docker buildx build --platform linux/amd64 . -t ghcr.io/educorvi/jats-importexport:$(API_VERSION)

push-image: check_dependency_docker build-image
	docker push ghcr.io/educorvi/jats-importexport:latest
	docker push ghcr.io/educorvi/jats-importexport:$(API_VERSION)
