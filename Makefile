
MAKEFLAGS += --no-print-directory
PROGRAM := drnk
PROGRAM_FULLPATH := $(shell which $(PROGRAM) 2>/dev/null)
DEBUG_PORT = 5678
VERBOSE =

all: test typecheck lint

test:
ifdef VERBOSE
	uv run pytest -vvv
else
	@uv run pytest
endif

typecheck:
ifdef VERBOSE
	uv run mypy
else
	@uv run mypy
endif

lint:
ifdef VERBOSE
	uv run flake8 src/pydrink
else
	@uv run flake8 src/pydrink
endif

debug:
	uv run debugpy --wait-for-client --listen 127.0.0.1:$(DEBUG_PORT) \
		$(PROGRAM_FULLPATH) $(OPTS)

push-all: test typecheck lint
	@git remote | xargs -L1 git push --all

build: test typecheck lint
	uv build --wheel

coverage:
	uv run coverage run -m pytest
	uv run coverage report -m

release: build
	uv publish

release-test: build
	uv publish --index test-pypi

clean:
	rm -rf dist
	find . -type d -name __pycache__ -print0 | xargs -0 rm -rf
