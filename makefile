export PATH := venv/bin:$(PATH)

all: pep8 test

clean:
	rm -rf venv

venv:
	virtualenv venv
	venv/bin/pip install -r requirements.txt

pep8:
	pep8 .

test: venv
	rm -f /tmp/dyli.db
	venv/bin/python manage.py syncdb --noinput
	venv/bin/pip install honcho
	venv/bin/honcho --env .env.test --procfile Procfile.test start

heroku: test
	pip install django-herokuapp
	venv/bin/python manage.py heroku_audit
	git push heroku master
	heroku run python manage.py makemigrations

migrate:
	heroku run python manage.py migrate

secret: heroku
	heroku config:set SECRET_KEY=`openssl rand -base64 32`
	heroku config:set PYTHONHASHSEED=random

run: venv
	venv/bin/pip install honcho
	venv/bin/honcho start
