
MAKEFLAGS += --no-print-directory
PROGRAM := drnk
PROGRAM_FULLPATH := $(shell which $(PROGRAM) 2>/dev/null)
DEBUG_PORT = 5678
VERBOSE =

all: test typecheck

test:
ifdef VERBOSE
	poetry run pytest -vvv
else
	@poetry run pytest
endif

typecheck:
ifdef VERBOSE
	poetry run mypy
else
	@poetry run mypy
endif

debug:
	python -m debugpy --wait-for-client --listen 127.0.0.1:$(DEBUG_PORT) \
		$(PROGRAM_FULLPATH) $(OPTS)

shell:
	poetry shell

push-all: test typecheck
	@git remote | xargs -L1 git push --all

build: test typecheck
	poetry build -f wheel

coverage:
	coverage run -m pytest
	coverage report -m

clean:
	rm -rf dist
	find . -type d -name __pycache__ -print0 | xargs -0 rm -rf
