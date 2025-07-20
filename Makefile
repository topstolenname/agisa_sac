.PHONY: install dev test test-federation test-chaos lint format clean run-federation run-chaos docs docs-serve

install:
	pip install -e .

dev:
	pip install -e ".[dev,federation,chaos,gcp]"
	pre-commit install

test:
	pytest tests/ -v

test-federation:
	pytest tests/federation/ -v --timeout=300

test-chaos:
	pytest tests/chaos/ -v

lint:
	ruff check src/ tests/
	mypy src/

format:
	black src/ tests/
	ruff check --fix src/ tests/

clean:
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info/

run-federation:
	docker-compose -f docker/federation/docker-compose.yml up

run-chaos:
	python -m agisa_sac.chaos.orchestrator --scenario all

docs:
	cd docs && make html

docs-serve:
	cd docs/_build/html && python -m http.server 8080
