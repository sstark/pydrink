
MAKEFLAGS += --no-print-directory
PROGRAM := drnk
PROGRAM_FULLPATH := $(shell which $(PROGRAM) 2>/dev/null)
DEBUG_PORT = 5678

all: test typecheck

test:
	@pytest

typecheck:
	@mypy

debug:
	python -m debugpy --wait-for-client --listen 127.0.0.1:$(DEBUG_PORT) \
		$(PROGRAM_FULLPATH) $(OPTS)

shell:
	poetry shell
