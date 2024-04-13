#!/bin/sh
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install boto3 python-dotenv dnspython
