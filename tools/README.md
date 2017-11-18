Pasos Migración
===============

Esta herramienta permite migrar la instancia vauxoo de version 8.0 a version
11.0.

Pasos a seguir desde instancia de updates:

Pre Migración
-------------

Modificar el archivo de configuración del script de migración en
`instance/tools/migration.conf` para que este se pueda ejecutar posteriormente
con los datos correctos. Los datos a configurar son host/port/user/password de:

- servidor postgres instancia vauxoo80
- servidor postgres instancia vauxoo110
- servidor odoo instancia vauxoo80
- servidor odoo instancia vauxoo110
- y los workers que esta usando la instancia vauxoo110.

*NOTA:* Los containers vauxoo80 y vauxoo110 deben tener expuestos los puertos
de odoo, ssh y postgres.

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
