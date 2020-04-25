.PHONY: docs
init:
	pip install pipenv --upgrade
	pipenv install --dev

test:
	pipenv run py.test

ci:
	pipenv run py.test --junitxml=report.xml

container:
	docker-compose up --abort-on-container-exit --exit-code-from tests --build
flake8:
	pipenv run flake8 --ignore=E501 breaker # ignore max line length

coverage:
	pipenv run py.test --cov-config .coveragerc --verbose --cov-report term --cov-report xml --cov=requests_circuit_breaker tests

publish:
	pip install 'twine>=1.5.0'
	python setup.py sdist bdist_wheel
	twine upload dist/*
	rm -fr build dist .egg breaker.egg-info

docs:
	cd website && npm install && npm run build
	@echo "\033[95m\n\nBuild successful! View the docs homepage at website/build/circuit-breaker-python/index.html.\n\033[0m"