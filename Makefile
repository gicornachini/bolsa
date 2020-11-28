PIPENV_RUN = pipenv run

VERSION := 2.0.0

help: ## Show this help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

clean: ## Clean local environment
	@find . -name "*.pyc" | xargs rm -rf
	@find . -name "*.pyo" | xargs rm -rf
	@find . -name "__pycache__" -type d | xargs rm -rf
	@rm -f .coverage
	@rm -rf htmlcov/
	@rm -f coverage.xml
	@rm -f *.log

test: clean ## Run tests
	$(PIPENV_RUN) py.test -svx bolsa

test-coverage: clean ## Run entire test suite with coverage
	$(PIPENV_RUN) pytest --cov=bolsa/ --cov-report=term-missing --cov-report=xml

check-security: ## Checks for security vulnerabilities and against PEP 508 markers provided in Pipfile.
	pipenv check

check-imports: ## Check imports.
	$(PIPENV_RUN) isort --check-only .

fix-imports: ## Fix imports.
	$(PIPENV_RUN) isort .

check-flake8: ## Check flake8 lint.
	$(PIPENV_RUN) flake8 bolsa/ --show-source

check-mypy: ## Check mypy.
	$(PIPENV_RUN) mypy bolsa --ignore-missing-imports

lint: check-imports check-flake8 check-mypy ## Check PEP8 https://www.python.org/dev/peps/pep-0008/.

update-requirements:
	$(PIPENV_RUN) pip freeze > requirements.txt

update-changelog:
	$(PIPENV_RUN) gitchangelog > CHANGELOG.md
	@git add .
	@git commit -m "docs: Update changelog"

release-patch: update-changelog
	$(PIPENV_RUN) bumpversion patch

release-minor: update-changelog
	$(PIPENV_RUN) bumpversion minor

release-major: update-changelog
	$(PIPENV_RUN) bumpversion major

deploy-release: ## Deploy next release.
	$(PIPENV_RUN) python setup.py bdist_wheel
	$(PIPENV_RUN) python -m twine upload dist/*
