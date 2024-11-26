# Soporte para Docker

### 1. Haz una copia del archivo sample_env_file para hacer un .env
### 2. Modifica  el .env para conexion a la base de datos y super usuario de django

#### Acciones para desplegar en ambientes de desarrollo y produccion

##### DEVELOP
- Construye la imagen de docker del backend  `docker-compose -f docker.compose.dev.yml build`
- Despliega el servicio `docker-compose -f docker.compose.dev.yml up -d`
- Crea las migraciones de la base de datos `docker-compose -f docker-compose.dev.yml exec -it voltix-back python3 site_app/manage.py makemigrations`  y `docker-compose -f docker-compose.dev.yml exec -it voltix-back python3 site_app/manage.py migrate`
- Crea el super usuario `docker-compose -f docker-compose.dev.yml exec -it voltix-back python3 site_app/manage.py  createsuperuser --noinput`

NOTA: Incluye una imagen de docker para postgres

##### PRODUCCION
- Construye la imagen de docker del backend  `docker-compose -f docker.compose.dev.yml build`
- Despliega el servicio `docker-compose -f docker.compose.dev.yml up -d`
- Crea las migraciones de la base de datos `docker-compose -f docker-compose.dev.yml exec -it voltix-back python3 site_app/manage.py makemigrations`  y `docker-compose -f docker-compose.dev.yml exec -it voltix-back python3 site_app/manage.py migrate`
- Crea el super usuario `docker-compose -f docker-compose.dev.yml exec -it voltix-back python3 site_app/manage.py  createsuperuser --noinput`

NOTA: El servicio de Postgres se ejecuta fuera de docker