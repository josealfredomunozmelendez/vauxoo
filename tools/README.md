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
 LEGACYHOST="172.17.0.2"
 LEGACYPORT="8072"
 LEGACYDB="vauxoo80"
 LEGACYUSER="admin"
 LEGACYPWD="admin"
 ```

- servidor odoo instancia vauxoo110

 ```bash
 ODOOHOST="0.0.0.0"
 ODOOPORT="8072"
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

Las siguientes anotaciones son importantes:

- Los containers vauxoo80 y vauxoo110 deben tener expuestos los puertos
  de odoo, ssh y postgres.
- Notese que se usa el puerto 8072 en lugar del 8069. Esto se debe a que
  esta herramienta es multi proceso y hacemos consultas que llevaran un
  tiempo considerable. Al utilizar el puerto 8072 estamos usando el
  --longpolling-port que nos permite evitar errores de concurrencia al intentar
  leer o escribir varios conjuntos de registros al mismo tiempo. Esto aplica
  para vauxoo80 y vauxoo110
- Si la instancia esta configurada con nginx, es preferible usar la direccion
  proporcionada por nginx y el puerto 443. Esto debido a que nginx se encarga
  de administrar la carga del multi procesamiento,  y evitar errores (es una
  conexcion json+ssl)

  ```bash
  ODOOHOST="url.nginx"
  ODOOPORT="443"
  ```

Migración
---------

Correr el script de migracion que esta en la carpeta tools de instance.

```console
# cd /home/odoo/instance/extra_addons/instance/tools
# ./migration.sh
```

> **NOTA:** El script de migraciøn debe correrse en la instancia **vauxoo110**.

Post Migración
--------------

Hacer un update de la instancia vauxoo110 con -u all, para verificar que todo
este bien sin errores.

Observaciones
-------------

Al terminar de correr el script este generara en el home del usuario un archivo
log donde muestra que sucedió, este archivo es del formato fecha_migration.log

Cuando ocurre un error en el script de migracion, ese registro o grupo de
registros que no pudieron ser importados se almacenan en un archivo de la
forma "nombre.modelo.csv". Este archivo contiene los registros que estan
pendientes aun por importar. Con este commando podemos importarlos, tras
resolver el error que hubo con ellos.

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
