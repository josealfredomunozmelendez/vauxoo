Pasos Migración
===============

Esta herramienta permite migrar la instancia vauxoo de version 8.0 a version
11.0.

Pasos a seguir desde instancia de updates:

Pre Migración
-------------

Modificar el archivo de configuración del script de migración en
`instance/tools/migration.conf` para que este se pueda ejecutar posteriormente
con los datos correctos. Estos son los valores a configurar:

- servidor postgres instancia legacy vauxoo80

 ```bash
 LEGACYPGHOST="172.17.0.1"
 LEGACYPGPORT="5432"
 LEGACYPGUSER='odoo'
 LEGACYPGPASSWORD='odoo'
 ```

- servidor odoo instancia vauxoo80

 ```bash
 LEGACYHOST="nginx.url"
 LEGACYPORT="433"
 LEGACYDB="vauxoo80"
 LEGACYUSER="admin"
 LEGACYPWD="admin"
 ```

- servidor odoo instancia vauxoo110

 ```bash
 ODOOHOST="nginx.url"
 ODOOPORT="443"
 ADMINLOGIN='admin'
 ADMINPASSWORD='admin'

 MIGRATIONLOGIN='migration'
 MIGRATIONPWD='migration'
 ```

 El usuario migración no existe, ese será creado en el proceso y será con el
 cual se creen todos los registros.

Los datos del servidor postgres vauxoo110, no necesitan ser configurados ya
que estos se toman automaticamente de las variables de entorno activas. Lo
mismo aplica para el path del filerstore de vauxo110 y los workers que utiliza.

```bash
$PGHOST
$PGPORT
$PGUSER
$PGPASSWORD
$PGDATABASE
$WORKERS
$ODOO_FILESTORE_PATH
```

> **NOTA**: Si alguna de estas variables hace falta por definir en el entorno
> actual e intentas correr el script indicará un mensaje como:
>
```bash
./migration.sh: line 12: ODOO_FILESTORE_PATH: parameter null or not set
```
>
Lo unico necesario es que exportes/asignes la variable en tu consola y vuelvas
a correr el script.

Las siguientes anotaciones son importantes:

- Si la instancia esta configurada con nginx, es preferible usar la direccion
  proporcionada por nginx y el puerto 443. Esto debido a que nginx se encarga
  de administrar la carga del multi procesamiento, y evitar errores (es una
  conexcion json+ssl)

  ```bash
  ODOOHOST="url.nginx"
  ODOOPORT="443"
  LEGACYHOST="nginx.url"
  LEGACYPORT="433"
  ```

- Si no se esta usando nginx, usar el puerto 8072 en lugar del 8069.
  Esto se debe a que esta herramienta es multi proceso y hacemos consultas que
  llevaran un tiempo considerable. Al utilizar el puerto 8072 estamos usando el
  --longpolling-port de odoo que nos permite evitar errores de concurrencia al
  intentar leer o escribir varios conjuntos de registros al mismo tiempo.

  ```bash
  ODOOHOST="0.0.0.0"
  ODOOPORT="8072"
  LEGACYHOST="172.17.0.1"
  LEGACYPORT="8072"
  ```

  Notese que el host puede ser cualquier ip valida que sea accesible de donde
  estas corriendo el script: local, ip interna de un container vecino, una ip
  accesible desde internet, un dominio accesible desde internet.

Migración
---------

Correr el script de migracion que esta en la carpeta tools de instance.

```console
# cd /home/odoo/instance/extra_addons/instance/tools
# ./migration.sh
```

> **NOTA:** El script de migraciøn debe correrse en la instancia **vauxoo110**.

Al terminar de correr el script este generara en el home del usuario un archivo
log donde muestra que sucedió, este archivo es del formato fecha_migration.log

Post Migración
--------------

Hacer un update de la instancia vauxoo110 con -u all, para verificar que todo
este bien sin errores.

Observaciones
-------------

Mas que todo para pruebas de migracion y ambiente de desarrollo, cuando ocurre
un error en el script de migracion, los registros que no pudieron ser
importados se almacenan en un archivo de la forma "import.nombre.modelo.csv".
Este archivo contiene los registros que estan pendientes aun por importar ya
mapeados solo esperando por ser importados neuvamente, tras resolver el error
que hubo con ellos.

```bash
# cd /home/odoo/instance/extra_addons/instance/tools
$ python3.5 import_data.py --load-csv FILENAME
```

Mas que todo para pruebas de migracion y ambiente de desarrollo, podemos
indicar a la herramienta un modelo, un domain y un set defaults (que sustituyen
el mapping necesario) y asi poder exportar / mapear / importar un grupo
determinado de elementos segun se especifique en sus parametros, solo este sub
grupo sin tener que procesar todo el universo de registros de ese modelo.

```bash
# cd /home/odoo/instance/extra_addons/instance/tools
$ python3.5 import_data.py --model STR --domain STR --defaults STR --context STR
```
> **NOTA:** Si vas a correr el script de migración varias veces tener en cuenta de
que el filestore no se llene con archivos basura.
