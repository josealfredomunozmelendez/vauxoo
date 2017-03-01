# Manejo de Proyectos

## Equipos de Trabajo

Todo el manejo de proyectos se hará a través de los equipos de proyecto.
Dentro de cada equipo de proyecto encontrarás una lista de proyectos que
delimitan para quien o donde afecta una actividad que estamos realizado.

Equipo | Descripción | Ejemplos
--- | --- | ---
1. Implementación | Representa todos los proyectos que tenemos actualmente con los clientes donde hacemos una implementación como tal
2. Entrenamiento | Todas las actividades de entrenamiento interno, investigación, generación de información y documentos de base de conocimiento. | Self-Driven Learning, Herramientas Técnicas, Introducción a Programadores, Introducción a Vendedores, Migración a git del equipo,
3. Gestión Interna | Tiene que ver con los proyectos de Gestión de Oficina y Ventas (ya que los vendedores necesitan cargar timesheet) | Gestión Oficina León, Gestión Oficina Colima, Gestión Oficina Valencia, Gestión de Ventas Vauxoo, Gestión de Portafolios de Proyectos
4. Investigación + Desarrollo | Aquí manejaremos todos las herramientas, módulos, desarrollos e investigación que realizamos y no son para un cliente como tal. Esto incluye los proyectos públicos o de la comunidad | Addons-Vauxoo, Localización Mexicana, Localización Venezolana, Localización Peruana, Localización Panameña, RMA, Forecast, OCA,
5. Consultoría | Es todo ese entrenamiento externo que damos y cobramos | Curso Funcional, Curso Técnico
6. Soporte | El soporte se dará por la herramienta del Helpdesk, no obstante en este proyecto es donde tendremos las tareas asociado a cada ticket del cliente que nos permite regitrar las horas empleadas | Soporte Lodigroup, Soporte Abasotal, 30 Horas Soporte a Cliente XY

Estos serán visibles por todos los empleados, no obstante existen equipos de
proyectos que solo serán visibles por invitación, por ejemplo: La Gestión
Interna no necesita ser visible para todos los empleados, solo para los
vendedores o personal administrativo.

## Proyectos

Los proyectos en versión 8.0 eran representados por el objeto project.project
pero para la versión 10.0 son representados por los pedidos de ventas.

```
Proyecto = Pedido de Venta
```

Estos pedidos de ventas ahora son el contrato que existe con el cliente y
a través del cual se venderán paquetes de horas los cuales se verán traducidos
en nuevas tareas las cuales son creadas al confirmar el pedido de venta.

Las tareas generadas a partir del pedido de venta serán las historias de
usuario relacionadas al proyecto.

Podemos identificar las historias de usuario o criterios de aceptación de un
proyecto ya que estos poseen el identificador del proyecto en la tarea:
dicho identificador es el numero del pedido de venta el cual tiene
como nombre "SO<number>" como por ejemplo "SO0005".

Las tareas generadas via pedido de venta tienen configurado el cliente del
pedido de venta que las genero.

Por ejemplos estos proyectos de la
versión 8.0 serían:

Nombre Proyecto en versión 8.0 | Nombre del Proyecto en versión 10.0
--- | ---
[P70-13] Yoytec Ventas | SO0006: Ventas
[P70-6] Yoytec RMA | SO00070: RMA

## Historias de Usuario

Los proyectos en su mayoría son planificados usando historias de usuario, estos
son las sub-tareas de nuestros proyectos. Serán representadas en la instancia
con el color azul. Estos tienen le prefijo `[US###]` en el nombre para mostrar.

## Criterios de Aceptación

Cada Historia de usuario tiene sub-tareas que son los Criterios de Aceptación,
estos son representados por tareas de color rojo con el prefijo `[AC]`

## Tareas

Las tareas las podrán crear cualquier empleado vía instancia.

> **NOTA:** La opción de crear tareas vía email ha quedado deshabilitada. La
única manera que podemos crear algo vía email son tickets de soporte, los
cuales son revisados primero y al ser procesados son asignados a un usuario que
se le crea una tarea a partir de la asignación.

Aquellos proyectos que no necesitan una planificación ni un análisis de
historia de usuarios o de criterios de aceptación a ser revisados por los
clientes serán manejados con `tareas simples`. Estas las llamaremos tareas `sin
categoría` y por defecto se crearán de color blanco.

Para el caso de los proyectos que si utilizan historias de usuario y
criterios de aceptación estos dos elementos son los únicos que manejaremos.
Sin embargo, todos los empleados pueden que participan en un proyecto pueden
crear tareas: estas quedarán en blanco y pueden ser filtradas usando el filtro
`Not Categorized yet`. Los lideres de proyecto tendrán que revisar estas tareas
y asignarles la categoría correcta, moverlas de proyecto a uno de tareas simples
o cancelarlas en tal caso.

# Soporte

El soporte lo daremos a través de una herramienta que se llama helpdesk. Este
será el lugar donde son canalizados los tickets con los issues/bugs/preguntas
de nuestros clientes. En este momento los tickets pueden ser creados:

- vía website a través del formulario de soporte
- vía email enviando un correo al alias configurado en los equipos de soporte.
- nosotros los creamos en el backend de la instancia usando los datos que nos
  proporciona el cliente.

Tenemos dos equipos de soporte:

- Soporte: Soporte general que le brindamos a nuestros clientes.
- Soporte de Infraestructura: Solo requerimientos de infraestructura.

El equipo de soporte se encarga de revisar y asignar los tickets dependiendo de
que resultado obtuvo de su evaluación. En este momento asigna el tipo de
Soporte que aplica agregándole una etiqueta al ticket la cual puede ser:

- Support L1
- Support L2
- Enterprise License: Significa que el ticket salió de nuestro alcance y que se
  le solicitó a Odoo solucionarlo ya que el cliente tiene una licencia comprada
  con Odoo.

Cuando se hace la asignación del ticket automáticamente se crea una tarea
la cual toma la información relevante del ticket y se la asigna a la persona
que lo resolverá. La tarea será el medio que utilizará el asignado para hacer
su investigación, pruebas de concepto, etc y para cargar las horas que le tomo
lograr resolver el ticket.

# Timesheets

Debemos registrar las horas que invertimos en todas las actividades que
realizamos, entre ellas:

- lograr el requerimiento de un cliente
- solventar un ticket
- investigación
- pruebas de concepto
- reuniones
- análisis
- documentación
- revisión funcional

La idea es registrar todo el tiempo y actividades que ejerzamos durante el día,
sin importar su índole. Así los lideres de proyecto y coach podrán ver nuestras
fortalezas y debilidades e implementar cambios que permitan mejorarlas. Debemos
cargar todas las horas, luego las personas encargadas de presentarle estas horas
al cliente las analizarán y en caso de ser necesario nos consultarán sobre ellas
y tomaran la decisión de cuales horas serán cobradas y cuales no.

Esta carga de horas se hará en el módulo de proyectos en las tareas
correspondientes: en este caso los criterios de aceptación.

Esta carga de horas se puede hacer por varios medios

1. Dentro de la tarea en la pestaña timesheet.
2. Ir al menu Timesheets >  Timesheets > Detailed Activities. Ingresando a
   mano los timesheets para luego asignar a cada proyecto y actividad o podemos
   importar los timesheets de una hoja de calculo usando el botón Import desde
   la vista lista de Detailed Activities

    date | user_id | name | project_id | task_id | unit_amount
    --- | --- | --- | --- | --- | ---
    2017/01/02 | Demo User | imported task 1 | Training | Vauxoo 100 | 3
    2017/02/01 | Demo User | imported task 2 | Implementation | Prueba Import | 0.5
    2017/01/02 | Administrator| imported task 3 | Training
    2017/01/02 | Administrator | imported task 4 | Implementation | | 0.25


3. Usando el App para chrome/android/iphone Awesome Timesheet las cuales le
   permite cargar las horas de manera asíncrona y luego sincronizar con la
   instancia.

# Planificación de Proyectos

.. TODO: Project Allow forecast: Pronosticar y planificar el trabajo a realizar.
