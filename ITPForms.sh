#!/bin/bash
apt-get install poppler-utils
pip install --upgrade pip
pip install --upgrade opencv-python
chown -R your_username:your_group /home/max/projets/65_pin3_form_reader/
source venvLinux/bin/activate
python manage.py runserver