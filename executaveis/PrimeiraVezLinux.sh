#!/bin/bash

sudo apt update && sudo apt upgrade -y
sudo apt install software-properties-common -y
sudo apt install python3.10
sudo apt install python3.10-venv
apt-get install poppler-utils
python3.10 -m venv ../venvLinux
chown -R $USER ../../65_pin3_form_reader/
source ../venvLinux/bin/activate
pip install --upgrade pip
pip install --upgrade opencv-python
pip install -r ../requirements.txt
python ../manage.py runserver