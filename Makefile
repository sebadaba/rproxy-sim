VENV := .venv
PY   := $(VENV)/bin/python
PIP  := $(VENV)/bin/pip

.PHONY: setup test notebook clean help

help:
	@echo "Targets disponibles:"
	@echo "  make setup     crea venv, instala deps + jupyter, registra kernel"
	@echo "  make test      corre pytest"
	@echo "  make notebook  abre Jupyter Notebook"
	@echo "  make clean     borra venv y artefactos de build"

setup:
	@if [ ! -d "$(VENV)" ]; then \
		python3 -m venv $(VENV); \
	fi
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	$(PY) -m ipykernel install --user --name=proxy-sim

test:
	$(PY) -m pytest -v

notebook:
	$(PY) -m jupyter notebook

clean:
	rm -rf $(VENV) build/ dist/
	rm -rf src/*.egg-info src/proxy_sim.egg-info
	find src tests -type d -name "__pycache__" -prune -exec rm -rf {} +