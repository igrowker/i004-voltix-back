#!/bin/bash
#Ejecuta los servicios
docker-compose up -d
#Ejecuta las migraciones
docker-compose exec -it web python3 site_app/manage.py migrate
docker-compose exec -it web python3 site_app/manage.py makemigrations
#Crea superusuario
docker-compose exec -it web python3 site_app/manage.py  createsuperuser --noinput
