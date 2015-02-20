.PHONY: clean secret heroku all accept

SHOULDIT := node_modules/shouldit/bin/shouldit
VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
PEP8 := $(VENV)/bin/pep8
HONCHO := $(VENV)/bin/honcho

PYSRC := $(shell find {doyoulikeit,things,manage.py,tests} -iname '*.py')
TARGET := $(PWD)/target

all: $(TARGET)/pep8.errors $(TARGET)/unit-tests.xml

clean:
	rm -rf venv results node_modules target

$(TARGET):
	mkdir -p $(TARGET)

$(VENV)/deps.touch: $(PIP) requirements.txt
	$(PIP) install -r requirements.txt
	touch $(VENV)/deps.touch

$(VENV)/bin/%: $(PIP)
	$(PIP) install $*

$(VENV)/bin/nosetests: $(PIP)
	$(PIP) install -e 'git+https://github.com/nose-devs/nose#egg=nose'

$(PYTHON) $(PIP):
	virtualenv -p python3 venv

$(TARGET)/pep8.errors: $(TARGET) $(PEP8) $(PYSRC)
	$(PEP8) --exclude="venv,node_modules" . | tee $(TARGET)/pep8.errors || true

$(TARGET)/unit-tests.xml: $(PIP) $(VENV)/deps.touch $(PYSRC) $(PYTEST)
	$(PIP) install pytest-cov
	DEBUG=True SECRET_KEY=abc py.test -vv -n 4 --ds=doyoulikeit.settings --cov things --cov-report term-missing --cov-report html --junit-xml $(TARGET)/unit-tests.xml test

$(TARGET)/results/test-output.xml: $(PIP) .env.test Procfile.test $(HONCHO) $(VENV)/deps.touch $(PYSRC) $(VENV)/bin/gunicorn $(PYTEST)
	mkdir -p $(TARGET)/results
	rm -f /tmp/dyli.db
	$(PYTHON) manage.py syncdb --noinput
	PATH=$(VENV)/bin:$(PATH) $(HONCHO) --env .env.test --procfile Procfile.test start

heroku: test
	pip install django-herokuapp
	$(PYTHON) manage.py heroku_audit
	git push heroku master
	heroku run python manage.py makemigrations

migrate:
	heroku run python manage.py migrate

secret: heroku
	heroku config:set SECRET_KEY=`openssl rand -base64 32`
	heroku config:set PYTHONHASHSEED=random
