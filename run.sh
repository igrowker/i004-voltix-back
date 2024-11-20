#!/bin/bash

#limpia primero el servicio anterior
docker-compose down -v

# hace un rebuild
docker-compose build

#Ejecuta los servicios
docker-compose up -d


#Ejecuta las migraciones
docker-compose exec -it voltix-back python3 manage.py collectstatic --noinput
docker-compose exec -it voltix-back python3 manage.py makemigrations

docker-compose exec -it voltix-back python3 manage.py migrate
#Crea superusuario
docker-compose exec -it voltix-back python3 manage.py  createsuperuser --noinput
