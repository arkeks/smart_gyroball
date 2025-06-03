.PHONY: setup venv install clean run-publisher run-subscriber run-all run-gui

# Python version
PYTHON = python3
VENV = venv
VENV_BIN = $(VENV)/bin

setup: venv install

venv:
	$(PYTHON) -m venv $(VENV)

install:
	$(VENV_BIN)/pip install -r requirements.txt

clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

run-publisher:
	$(VENV_BIN)/python sender/speed_publisher.py

run-subscriber:
	$(VENV_BIN)/python recv/speed_subscriber.py

run-gui:
	$(VENV_BIN)/python gui/speed_monitor.py

run-all: run-subscriber run-publisher 