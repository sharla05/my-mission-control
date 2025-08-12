uv venv --python 3.13

uv lock

uv add fastapi uvicorn structlog python-multipart tomli

uv add pytest pytest-cov httpx pre-commit ruff isort pyright bandit --dev

