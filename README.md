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

# Nota Importante
    #acuedase del punto .ENV
    #Asegúrate de que tu archivo .env esté configurado correctamente con las variables de entorno necesarias. Este archivo debe contener credenciales de base de datos, claves secretas y otras configuraciones esenciales.


    #Ruta de nuestra base de datos
    #Conectar con nuestra base de datos, con su terminal, <PASSWORD> que tenemos en archivo .env
    psql 'postgres://avnadmin:<PASSWORD>@miluz-i004-voltix-back.e.aivencloud.com:22219/defaultdb?sslmode=require'
    
    
    
        #Para listar todas las bases de datos: 
        \l
        #Para listar todas las tablas de la base de datos conectada: 
        \dt
   
   #Ejecutar el Servidor de Desarrollo
    python3 site_app/manage.py runserver

    # para instalar requiremetns:
    pip install -r requirements.txt
    
    #para renovar requirements
    pip freeze > requirements.txt


#* si falta una libreria en invoices.views.py
pip install pymupdf opencv-python-headless




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

---

### Notas Adicionales:
- **Comando de Ayuda General:** Si necesitas más información sobre todos los comandos disponibles en `psql`, puedes ejecutar el comando `\?`.
- **Documentación Oficial:** Consulta la [documentación oficial de PostgreSQL](https://www.postgresql.org/docs/current/app-psql.html) para obtener una referencia más completa.

Este conjunto de comandos puede facilitar tareas como explorar bases de datos, analizar estructuras de tablas, y obtener detalles sobre roles y permisos.


# Cuando añades una medición en data_measurements.json, hay que correr el siguiente comando para que se suba la medición a la base de datos:

python site_app/measurements/scripts/load_measurements.py


|--------------------------------------------------- INSRTUCCIONES PARA GENERAR EL PDF ----------------------------------------------------------|

# Guía para la descarga del reporte PDF en el front-end

El endpoint `/api/measurements/report/download/` permite descargar un reporte en formato PDF, recibiendo como parámetro el `id` de la medición asociada. A continuación, se explica cómo gestionar la solicitud desde el front-end.

## 1. Construcción del URL

Para realizar la solicitud al backend, el front-end debe construir el URL con el parámetro `id`. El formato correcto es el siguiente:


{{base_url}}/api/measurements/report/download/?id=<ID_MEDICION>

    {{base_url}}: Es la URL base de tu servidor backend (por ejemplo: https://example.com).

    Ejemplo de URL: {{base_url}}: Es la URL base de tu servidor backend (por ejemplo: https://example.com).

    <ID_MEDICION>: El ID de la medición que quieres incluir en el reporte.

# Ejemplo de URL:

https://example.com/api/measurements/report/download/?id=1