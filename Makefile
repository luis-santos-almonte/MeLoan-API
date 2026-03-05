# Variables
PYTHON = venv/bin/python
UVICORN = venv/bin/uvicorn
ALEMBIC = PYTHONPATH=. venv/bin/alembic

.PHONY: install run migrate rev

install:
	pip install -r requirements.txt

run:
	$(UVICORN) app.main:app --reload

migrate:
	$(ALEMBIC) upgrade head

rev:
	@read -p "Nombre de la migracion: " msg; \
	$(ALEMBIC) revision --autogenerate -m "$$msg"

test:
	$(PYTHON) -m pytest