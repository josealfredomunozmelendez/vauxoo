vxmigration
-----------

Esta herramienta permite migrar la instancia vauxoo de version 8.0 a version
11.0.

Primero antes de la migración es necesario:

1. Tener dos containers con uno corriendo vauxoo80 y otro corriendo vauxoo110.
   Estos containers deben tener expuestos los puertos de odoo, ssh y postgres,

2. Los scripts de migración deben correr en el container con la instancia
   vauxoo110.

3. Antes de correr los scripts es necesario modificar el archivo
   tools/migration.conf: allí debemos configurar la informacion de los
   host/port/user/password de postgres, instancia vauxoo80 e instancia
   vauxoo110.

4. El script se puede correr de varias maneras.

  4.1 migration.sh: Este shell script se encarga de realizar la migración
      completa, incluyendo los pasos previos a la migración y los pasos
      posteriores. Este debe ser corrido con root.

      ```bash
      # ./migration.sh
      ```

      Al correr este comando podremos tener un log completo de todos los pasos
      ejecutados divido en 2 archivos:

      - migration.log: muestra todos los pasos de la migración y almacena
        también cualquier error ocurrido.
      - server.log: almacena el log de la instancia de odoo vauxoo110 mientras
        que el script estuvo activo.

  4.2 vxmigration: esto es mas que todo si ocurre un error, se puede correr 
      posterior al script de migracion el volver a intentar migrar los registros
      que por alguna u otra razon fallaron, claro, tras corregir el problema
      que ocurrio con la data.

      ´´´bash
      $ vxmigration --load-csv FILENAME
      ´´´

      cuando ocurre un error en el script de migracion, ese registro o grupo de
      registros que no pudieron ser importados se almacenan en un archivo de la
      forma "nombre.modelo.csv". Este archivo contiene los registros que estan
      pendientes aun por importar. Con este commando podemos importarlos, tras
      resolver el error que hubo con ellos.

      ´´´bash
      $ vxmigration --model STR --domain STR --defaults STR --context STR
      ´´´

      mas que todo para pruebas de migracion, podemos indicar que modelo, un
      domain y un set defaults para sustituir el mapping necesario, este comando
      permite exportar / mapear / importar un grupo determiando de elementos segun
      se especifique en sus parametros.
