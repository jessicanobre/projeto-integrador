VENV=.venv

.PHONY: venv install backend frontend all

venv:
	python3 -m venv $(VENV)
	@echo "Created venv at $(VENV). Activate with: source $(VENV)/bin/activate"

install: venv
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt

backend:
	./scripts/run_backend.sh

frontend:
	./scripts/run_frontend.sh

all: backend
