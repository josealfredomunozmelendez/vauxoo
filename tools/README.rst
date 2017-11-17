vxmigration
===========

Esta herramienta permite migrar la instancia vauxoo de version 8.0 a version
11.0. Pasos a seguir:

Premigración
------------

1. Tener dos containers uno corriendo vauxoo80 y otro corriendo vauxoo110.
   Estos containers deben tener expuestos los puertos de odoo, ssh y postgres.
   Estas instancias pueden tener su servidor postgres en un container separado.

2. Los scripts de migración deben correr en el container con la instancia
   vauxoo110.

3. Modificar el config file de odoo del container vauxoo110 para incrementar
   --limit-time-cpu  y --limit-time-real a su consideración.

4. Levantar instancia y crear la base datos de vauxoo110 instalando el modulo
   vauxoo sin data demo y pais mexico en contexto.

5. Parar el servidor de odoo y aplicar parche al branch de odoo, el cual nos
   permitira escribir tanto el create_date, write_date, create_uid y write_uid
   que vienen de la instancia vauxoo80 en la nueva base da datos migrada.

   ```bash
   git apply /home/odoo/instance/extra_addons/instance/tools/odoo-saas14-magic-fields.patch
   ```

6. Modificar el archivo de configuración del script en instance/tools/migration.conf
   para que este se pueda ejecutar posteriormente con los datos correctos.
   Estos datos son host/port/user/password de:

   - servidor postgres instancia vauxoo80
   - servidor postgres instancia vauxoo110
   - servidor odoo instancia vauxoo80
   - servidor odoo instancia vauxoo110
   - workers que esta usando la instancia vauxoo110.

7. Reiniciar el servidor odoo vauxoo110 para que se hagan efectivo los cambios

Migración
---------

1. Correr el script de migracion que esta en la carpeta tools de instance.
   Este debe ser corrido con root.

    ```bash
    cd /home/odoo/instance/extra_addons/instance/tools
    ./migration.sh
    ```

Post Migración
--------------

1. Al terminar el script, detener la instancia vauxoo110.

2. Revertir el parche aplicado en dooo

    ```bash
    cd /home/odoo/instance/odoo
    git reset --hard en odoo-11.0
    ```

3. Copiar el filerstore de vauxoo80 al container de vauxoo110. y de alli copiar
   los archivos de vauxoo80 a la carpeta del filerstore de vauxoo110 dejando los
   archivos que ya existan y solo agregando los que estan en vauxoo80 que no
   estan en vauxoo110. Ejemplo:

    ```bash
    rsync -Pavhe cp --ignore-existing $LEGACYDB/ $DATABASE/
    ```

4. Hacer un update de la instancia vauxoo110 con -u all para que los odoo magic
   fields regresen a la normalidad.

Observaciones
-------------

Al terminar de correr el script este generara en el home del usuario un archivo
log donde muestra que sucedió, este archivo es del formato fecha_migration.log

Cuando ocurre un error en el script de migracion, ese registro o grupo de
registros que no pudieron ser importados se almacenan en un archivo de la
forma "nombre.modelo.csv". Este archivo contiene los registros que estan
pendientes aun por importar. Con este commando podemos importarlos, tras
resolver el error que hubo con ellos.

    ´´´bash
    $ vxmigration --load-csv FILENAME
    ´´´

Mas que todo para pruebas de migracion y ambiente de desarrollo, podemos
indicar a la herramienta un modelo, un domain y un set defaults (que sustituyen
el mapping necesario) y asi poder exportar / mapear / importar un grupo
determinado de elementos segun se especifique en sus parametros, solo este sub
grupo sin tener que procesar todo el universo de registros de ese modelo.

    ´´´bash
    $ vxmigration --model STR --domain STR --defaults STR --context STR
    ´´´

NOTA: Si vas a correr el script de migración varias veces tener en cuenta de
que el filterstore no se llene con archivos basura.
