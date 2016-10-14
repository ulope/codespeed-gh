#!/usr/bin/env bash

set +e
set +x

cd /codespeed

if [ ! -z ${MIGRATE} ]; then
	/venv/bin/python /codespeed/manage.py migrate --noinput
fi

exec /venv/bin/python /codespeed/manage.py "$@"
