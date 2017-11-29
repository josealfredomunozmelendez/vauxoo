# Gastos

Al instalar el módulo *Expense Tracker* (odoo/addons/hr_expense) agrega un
nuevo menú llamado **Expenses** en el dashboard principal donde todos los
empleados podrán ingresar y acceder a su historial de gastos para procesar
reembolsos o notificar relación de gastos al departamento administrativo.

## Configuraciones

### Configuraciones Básicas

1. El correo que se usará para que los empleados envíen sus expenses y que
automáticamente generarán un gasto en el sistema.Este valor puede se configura
en la sección **Expenses > Configuration > Settings** y por defecto es
*expense@pima.com*

2. _Necesitamos configurar_ un diario de gastos, para ello creamos un diario
llamado **Expense Journal** el cual tiene que ser de tipo **Purchase** para
ser tomado en cuenta a la hora de evaluar los reportes de Gastos. Sin este
Diario el usuario Contador no puede Postear/Pagar los expenses a los
empleados: aparece el error _“Expenses must have an expense journal specified
to generate
accounting entries"_.

3. Necesitamos crear una cuenta de gastos y asociarla a los productos de
gastos. Este es importante porque automáticamente se agrega en cuando se crea
un nuevo expense y es tomando en cuenta en el reporte final de gastos y así
poder postear los journal entries asociados: si esta no existe al intentar
generar la entrada del diario el sistema dará problemas.

4. Solo el **Accounting Adviser** (el de mayor estatus) tiene la potestad de
ver y agregar las cuentas para los accounting entries. Entonces no podemos
procesar nada contable hasta que el contador lo vea y agregue las cuentas.

### Configuración de Usuarios

1. Existen dos grupos de permisos relacionados a los Expenses configurables
desde el formulario de usuarios:
 * **Nulo**: Ve el Menú My Expenses donde tiene acceso a al menú My Expenses y
sus 3 sub-menús: Expenses to Submit, Refused Expenses & Expenses Reports.
 * **Officer**: En adición ven un menú llamado To Approve, que tiene un único
sub me. Expense Reports To Approve que le permite a estos usuarios
 * **Manager**: Todos los menús, los anteriores, más, el menú Accountant,
Reporting y Configuration.
2. **NOTA IMPORTANTE:** El Manager de un empleado tiene que ser un **Expense
Officer** para así poder ver el menú **To Approve** y poder aprobar los
reportes de gastos de sus subordinados.

3. Los Officer solo pueden ver los expenses que son suyos y todos aquellos que
están pendiente por ser aprobados

4. Los Manager pueden ver **todos los issues** del sistema, **no importa en
qué estado se encuentren**, para ello necesitan irse al menú **Reporting >
All Expenses**: allí tienen la vista de gráfica y la vista lista.

5. **IMPORTANTE:** Los usuarios empleados tienen que tener su dirección de
   casa configurada, y una cuenta bancaria, ya que estas serán utilizadas para
   regresar el dinero cuando el reporte de gastos es validado por el contador
   al dar click el en botón **Post Journal Entries**, de lo contrario
   aparecerá un error _"No Home Address found for the employee Employee,
   please configure one.”_ cuando el expense es de tipo empleado.

### Configuración de Productos

1. Al crear un expense requiere que tengamos un producto asociado, dicho
__producto es de tipo expense (boolean) y debe tener asociado una cuenta de
expenses__. Si no lo tiene, entonces al momento de procesar el gasto
(contabilidad) tendremos errores.

2. Existe un producto expense genérico por defecto en el sistema que es tomado
por defecto como el producto asociado a un expense creado desde website. Este
funciona así a nivel de código y no debe ser borrado: lo que podemos es
cambiarle el nombre a uno que mejor nos convenga.

3. Los gastos que podemos tener son:
 * Expense (Genérico) renombrado a **Gasto pendiente por Categorizar**
 * Gastos de Comida
 * Gastos de Transporte
 * Gastos de Alojamiento

## Flujo del Expense Básico

1. Crear el registro en estado New

 * Se puede crear en la misma instancia en el menu Expenses > My Expenses
 * Crear registro de expenses vía correo electrónico enviando un mensaje a la
dirección de correo de gastos configurada.

2. Periódicamente enviarlo al Manager, Esto se puede hacer de dos maneras:
 * Dando click al botón **Submit to Manager** en el expense lo cual crea un
**Expense Reports**.
 * Creando directamente un Expense Report desde el menú correspondiente.
 * Si un empleado tiene un Manager, entonces dicho Manager aparecerá como
seguidor del documento expense report una vez haya sido enviado.

3. El Officer, lo evalúa y lo aprueba o rechaza:
 * Este ve un menú llamado **To Approve** donde aparecen todos los reportes
expenses qué necesitan ser revisados o aprobados/rechazados. Todos, incluso si
los empleados que reportar no son subordinados.

4. De ser aprobado el reporte usando el botón Aprobar, este lo puede ver el
contador desde el menú **Accountant > Expense Reports To Post / To Pay**

5. El contador valida los valores y hace el reembolso dando click al botón
**Post Journal Entries** y posterior al botón **Register Payment**

### Pruebas de Concepto

### Crear Expense vía correo + Flujo simple

1. Cree un expense desde correo, con usuario empleado Katherine Zaoral
(Developer), título y contenido básico, y con imagen adjunta. Resultados: El
issue fue correctamente creado con el producto genérico.

2. El usuario Developer se va al módulo es Expenses > My Expenses
3. El usuario Developer selecciona el issue creado desde email y revisa los
valores cargados en el issue
 * El Producto por defecto seteado es [EXP] Expenses
 * Date: Fecha que fue enviada el correo
 * Empleado: Hace el link al empleado relacionado a la dirección de correo
donde se envió el correo d. El adjunto del correo se ve en le log de mensajes y
se puede consultar en un Stat Info Button llamado Documents
 * El contenido/body del correo se agrega en el message log del expense.
 * El campo Notas queda vacío
 * El campo Bill Reference queda vacío

4. Luego le da click al botón **Submit to Manager** que lo cambia de Estado
**To Submit** a **Reported**

5. A esta altura ya el usuario Developer deja de ver por defecto el Expense, y
puede ver sus Expense Reports. Si quita el filtro por defecto de la vista
entonces podrá ver el historial de todos sus expenses.

6. Ahora el **Expense Report** (hr_expense_sheet) generado lo puede ver el
usuario que fue configurado como el Manager en la ficha de Empleado de
Katherine Zaoral, en este caso es Gabriela Quilarque. Gabriela puede ver este
reporte en el menú **Expense > To Approve > Expense Reports to Approve**,
Gabriela es agregada como seguidora del documento reporte de gastos.

7. Trazabilidad Expense Report: El log del reporte muestra la información tanto
de quién lo envió como de quien lo aprobó.

8. Luego que ha sido aprobado, el **Manager** del empleado puede ir el menú
**Expense** **Reports to Approve** y quitar el filtro **To Approve** y allí
puede ver el historial de los expense report que ha aprobado y puede
identificarlos ya que en la vista lista muestra el campo estado.

9. Luego el usuario contador que debe ser configurado como un **Expense
Manager**, revisa el expense le da click al botón **Post Journal Entries**,
Allí el expense report paso a estado **Posted**.

10. Luego el mismo usuario contador podrá ver el botón **Register Payment** el
cual permitirá hacer el pago del gasto y al llenar la información de la
transacción el expense pasa a estado pagado

## Preguntas Frecuentes

### Crear Expense vía email

1. Con una dirección de correo no registrada
 * Crear un expense con una cuenta de correo no afiliada al sistema y ver que
pasa: El resultado es que el expense no fue creado, ni siquiera veo rastro del
email que fue enviado por la persona extraña a la instancia
2. Intentar crear un Expense con una cuenta tipo Cliente
 * Mandar un correo a expenses pero como usuario Customer. ¿Crea el expense?
No. no crea el expense lo cual esta bien, solo los empleados pueden crear
expenses.
3. Con la cantidad del gasto en el asunto del correo
 * Colocando la cantidad asociada al gasto en el título de correo y ver si
realmente coloca el amount en el issue. Esto es efectivo. Realmente ocurre
4. ¿Cuando no agregó el internal number del producto en el correo, como elige
Odoo el producto por defecto a colocar en el gasto?
 * Cuando hay un solo producto [EXP] Expense, toma este producto como defecto.
 * Cuando hay varios productos que pasa? Toma el mismo EXP, el exp por defecto,
esta configurado así via código.
5. Nombrado [REF-IN] del producto en el asunto
 * Si tenemos registrado los productos tipo Expenses y en el email le colocamos
de título la referencia interna del producto entre corchetes y le pasamos en el
título. Si esto está funcionando.
6. De un usuario que no tiene Manager configurado
 * Crear un issue con un usuario que no tenga manager ¿Quien Aprueba? No pasa
nada malo. No se agrega el manager automáticamente al reporte de gastos, pero
este queda en estado submitted y cualquier usuario que tenga permisos para
aprobar gastos puede tomarlo.

### Expense Reports

Los estados del Expense Report son Submitted, Approved, Posted, Paid

1. ¿Al crear un Expense Report dando click al botón Submit to Manager agrupa
   todos los Expenses en estado To Submit?
 * Cuando tengo varios expenses en estado New y le doy Submit a uno de ellos,
   completa el Expense report con los demás expenses en estado New? No. pero
   si me deja seguir editando y agregar cualquier otro gasto que necesite
     - No puedo agregar gastos de diferente tipos en un mismo expense report.
     - Si paso dos gastos en el reporte, y luego el manager aprueba. El
       empleado puede seguir agregando expenses al reporte de gastos, y no hay
       control de decir hasta aquí si y hasta acá no: no puede editar los que
       ya creo, pero si puede agregar nuevas líneas.  toma en cuenta los
       gastos que fueron agregados pos aprobación. Este reporte le llega al
       contador y este paga sin preguntas, lo cual no está bien: no hay
       notificación ni al manager ni al contador para que revise los nuevos
       expenses reportados
     - Si tengo gastos con total = 0 y el contador intenta hacerle post da un
       error “The payment amount must be strictly positive.”
     - Después que un gasto ha sido reportado al contador “Aprobado por el
       manager” el gasto pasa a estado Reported y apartir de aca ya el usuario
       no puede editar su gasto, puede modificar solo los campos bill
       reference, account y notes. Tambíen puede ver un botón VIew Report que
       muestra el expense report que el envío y que está asociado a ese gasto.
     - Luego que el reporte de gastos ha sido aprobado el empleado no tiene
       potestad de editarlo, solo esperar.
     - El contador o el manager que aprueba pueden hacer refuse del reporte de
       gastos, en los estados submited y approved respectivamente, tiene que
       suministrar una razón de porque fue rechazado, El correo con la
       información del refuse le llega a ambos al Aprobador del expense y a al
       empleado que lo generó. Cualquiera de estos dos puede editar los gastos
       y darle click al botón Resubmit que aparece en el reporte de gastos.
       Para así sacarlo del estado refused y pasarlo a estando submited de
       nuevo.

         1. Hice Resubmit con el usuario empleado y quedo esperando por
            aprobación del manager, pero esta vez no le llegó ningún correo al
            manager.
         2. Cuando ha sido rechazado llega un correo avisa

2. ¿Cuántas veces podemos reportar un expense?
 * Create various expenses, then add part of them to a expense report A, then
create a new expense report B and try to add the same expenses already added in
Expense A.

     - Esto está bloqueado a nivel de interfaz, a que solo podemos agregar
       gastos que no están en los estados posted o done.
     - Si intentas usar el wizard para crear un reporte de gastos, en un gasto
       que ya ha sido reportado, te aparecerá un mensaje diciendo _“You cannot
       report twice the same line!”_

### Expense

1. ¿Que identifica de manera única a un Expense de otro? Nada visible al
usuario, el id solamente.
2. ¿Puedo volver enviar un Expense que ha sido rechazado? Si, vuelve a pasar
por el proceso de aprobación luego de ser corregido
3. ¿Cual es la diferencia en el flujo si seleccionó la opción **Employee (to
remburse)** or **Company** en **Payment By**? El tipo de cuenta donde se
registra el move es distinta:

 * Si es empleado necesitamos tener la dirección de casa del empleado para
poder procesar el pago, puesto que toma la cuenta personal del empleado para el
reembolso
 * Si es tipo compañía pasa directo a estado pagado.

4. Un usuario que no es Expense Officer or Manager o Accountant puede ver el
menu de Expenses? Si, todos los empleados pueden verlo entrar y agregar gastos
allí.

## Notas técnicas

- Automáticamente instala (sale_expense) el módulo Sales Expenses (el cual es
automáticamente instalado al tener sale y hr_expense instalado)
- Según lo que pude ver solo los usuarios Expense Officer, Expense Manager y
Accountant tiene el poder absoluto para leer/crear/modificar/eliminar expenses.
  * Tenemos un ACL que permite a todos los usuarios empleados CRUD los expenses
y expense reports
  * Tenemos un IR rule que delimita que los empleados pueden hacer CRUD pero
solo sobre sus propios Expenses.
  * Los Expense Officer y superiores pueden hacer CRUD con todos los expenses.

> **NOTA:** No hay regla que limite que un usuario CRUD un expense report de
otra persona

Para mayor información puede ver videos funcionales relacionados en
https://www.youtube.com/results?search_query=odoo+expenses
