#!/bin/bash

#limpia primero el servicio anterior
docker-compose down -v

# hace un rebuild
docker-compose build

#Ejecuta los servicios
docker-compose up -d


#Ejecuta las migraciones
docker-compose exec -it voltix-back python3 site_app/manage.py makemigrations

docker-compose exec -it voltix-back python3 site_app/manage.py migrate
#Crea superusuario
docker-compose exec -it voltix-back python3 site_app/manage.py  createsuperuser --noinput
