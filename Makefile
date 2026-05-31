SHELL := /bin/bash
.PHONY: help env format install lint test run build

help:
	@grep '^\.PHONY' Makefile | cut -d' ' -f2- | tr ' ' '\n'

# usage: `source $(make env)`
env:
	@poetry env activate | cut -d' ' -f2

format:
	poetry run isort .
	poetry run black .

install:
	poetry install

lint:
	poetry run isort -c --diff .
	poetry run black --check .
	poetry run flake8 .

test:
	poetry run pytest --cov=. --cov-report term --cov-report xml ./tests

run:
	python main.py

build:
	@echo "TODO"
