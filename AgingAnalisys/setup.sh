#!/usr/bin/env bash

python3 -m venv venv

venv/bin/python -m pip install --upgrade pip

venv/bin/pip install pipreqs

venv/bin/pipreqs .

venv/bin/python -m pip install -r requirements.txt

echo "ative o venv python agora!"