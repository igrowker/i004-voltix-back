# Run the server

### 1. Crear un entorno virtual

Primero, crea y activa un entorno virtual para gestionar las dependencias del proyecto de manera aislada.

```bash
    # Crear el entorno virtual
    python3 -m venv venv

    # Activar el entorno virtual
    # En macOS/Linux
    source venv/bin/activate
    # En Windows
    venv\Scripts\activate

    #Después de activar el entorno virtual, instala las dependencias necesarias:
    pip install -r requirements.txt
    # Actualizar la lista de paquetes del sistema
    sudo apt-get update

    # Instalar PostgreSQL y sus componentes adicionales (Si no esta instalado )
    sudo apt-get install -y postgresql postgresql-contrib

    # Verificar la instalación
    psql --version

    sudo service postgresql start
    sudo service postgresql status

    #Ruta de nuestra base de datos
    #Conectar con nuestra base de datos
    psql 'postgres://avnadmin:AVNS_KMlR6yxJcuqiTSYfkny@miluz-i004-voltix-back.e.aivencloud.com:22219/defaultdb?sslmode=require'
    
        #Para listar todas las bases de datos: 
        \l
        #Para listar todas las tablas de la base de datos conectada: 
        \dt
   
   #Ejecutar el Servidor de Desarrollo
    python3 site_app/manage.py runserver


    #para renovar requirements
    pip freeze > requirements.txt




# Notas Importantes
    #acuedase del punto .ENV
    #Asegúrate de que tu archivo .env esté configurado correctamente con las variables de entorno necesarias. Este archivo debe contener credenciales de base de datos, claves secretas y otras configuraciones esenciales.

# Comandos Útiles para PostgreSQL en `psql`

A continuación, se presenta una tabla con comandos útiles para explorar y administrar bases de datos en PostgreSQL utilizando el cliente `psql`.

| **Comando**         | **Descripción**                                                                                                   | **Ejemplo**                |
|----------------------|-------------------------------------------------------------------------------------------------------------------|----------------------------|
| `\l`                | Lista todas las bases de datos disponibles.                                                                      | `\l`                       |
| `\dn`               | Lista todos los esquemas presentes en la base de datos actual.                                                   | `\dn`                      |
| `\dt`               | Lista todas las tablas disponibles en el esquema actual.                                                        | `\dt`                      |
| `\dv`               | Lista todas las vistas definidas en la base de datos actual.                                                     | `\dv`                      |
| `\d nombre_tabla`   | Muestra información detallada sobre la estructura de una tabla.                                                  | `\d usuarios`              |
| `\di nombre_tabla`  | Lista los índices asociados a una tabla específica.                                                              | `\di usuarios`             |
| `\df`               | Muestra todas las funciones definidas por el usuario en la base de datos actual.                                 | `\df`                      |
| `\ds`               | Lista todas las secuencias disponibles en la base de datos.                                                     | `\ds`                      |
| `\du`               | Muestra todos los roles de usuario creados en el sistema de bases de datos.                                      | `\du`                      |
| `\dt+`              | Lista todas las tablas junto con información adicional, como su tamaño.                                          | `\dt+`                     |
| `\dt *.*`           | Muestra todas las tablas en todos los esquemas, incluidas las del sistema.                                       | `\dt *.*`                  |
| `\h nombre_comando` | Proporciona información detallada sobre la sintaxis y uso de un comando SQL específico.                          | `\h SELECT`                |
| `\?`                | Lista todos los metacomandos disponibles en `psql`.                                                              | `\?`                       |
```
---

### Notas Adicionales:
- **Comando de Ayuda General:** Si necesitas más información sobre todos los comandos disponibles en `psql`, puedes ejecutar el comando `\?`.
- **Documentación Oficial:** Consulta la [documentación oficial de PostgreSQL](https://www.postgresql.org/docs/current/app-psql.html) para obtener una referencia más completa.

Este conjunto de comandos puede facilitar tareas como explorar bases de datos, analizar estructuras de tablas, y obtener detalles sobre roles y permisos.

---

# Soporte para Docker

### 1. Modifica el .env para conexion a la base de datos y super usuario de django
### 2. Ejecuta el comando run.sh

Este ejecutable realiza las siguientes acciones:


- Elimina el servicio actual:  `doker-compose down -v`
- Reconstruye la imagen  `docker-compose build`
- Ejecuta y construye los servicios de django y la base de datos:  `docker-compose up -d`
- Crea las migraciones de la base de datos `docker-compose exec -it voltix-back python3 site_app/manage.py makemigrations`  y `docker-compose exec -it voltix-back python3 site_app/manage.py migrate`
- Crea el super usuario `docker-compose exec -it voltix-back python3 site_app/manage.py  createsuperuser --noinput`

Para acceder a tu servicio de docker desplegado `http://host:8800`

Para realizar pruebas:

- En la carpeta OCR está la factura de prueba, en la misma se va a generar un output.txt donde están los datos obtenidos
- `docker-compose exec -it voltix-back tesseract ocr/factura_demo.png output --psm 11 --oem 3  -l spa`
- Opciones de tesseract para análisis de la imagen:
```
output: genera un archivo output.txt
stdout: alternativa a output que imprime directamente la salida a pantalla(o variable)

-l selecciona el idioma.

--oem selecciona el algoritmo OCR.

--psm selecciona el modo de segmentación de página.

```

Para mas info de los Modos de segmentación de página (PSM): https://pyimagesearch.com/2021/11/15/tesseract-page-segmentation-modes-psms-explained-how-to-improve-your-ocr-accuracy/

