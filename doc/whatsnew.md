v0.1.9
- CssFlexBox Geometric Manager implementado a través del tkinter.place geomanager.
- Permite disponer en el layout widgets cuyas dimensiones no son exactamente pixeles (e.j. label)
- Se crea el "@doc:showcase/cssflexbox_container_properties" que muestra la disposición de los widgets
una vez se utiliza el CssFlexBox.
- Corrección de errores asociados al tipo de selector '.clase > :pseudoattr'.
- Queda por implementar una función que determine cuando un widget es RESPONSiVE de tal manera que 
se pueda ajustar su tamaño sin producir parpadeo en la pantalla. 

v0.1.8
- CssFlexBox Geometric Manager
- Clase CssFlexBox implementa el Css Flex Box geometric manager teniendo como referencia la 
especificación [Css Flexible Box Layout](https://www.w3.org/TR/css-flexbox-1/)
- Despliegue gráfico implementado con tkinter.pack como primera aproximación. Limitado con widgets 
que no aceptan diensiones en pixels (e.j. Label que acepta número de caracteres en "width" y número de 
líneas en "height")
- test_css_flexbox.py, set de tests a la implementación de flex box layout.
- Modificado userinterface para aceptar el nevo layout.

v0.1.7
- Clase CssUnit que hace manejo de las dimensiones en css.
- Integración en cálculo de responsive de CssUnit con dimensiones relativas verificando que en 
los atributos 'grid_templaterows' y 'grid_template_columns' no se tengan CssUnits relativas tales
como '%' o una de las relativas al viewport.
- Corrección de bugs en UIMonitor.

v0.1.6
- Nuevo método CssGrid.availables(linf, lsup, step) entrega las posiciones disponibles en el grid 
para un range(linf, lsup, step). Este método parte de las posiciones tomadas (CssGrid.taken) y 
calcula las posiciones disponibles. 
- Nuevo método CssGrid.grid_template_areas_equiv() que entrega un string con las características 
del "grid-template-areas" que describe la disposición de los items registrados en el grid.
- Clase MapTracks que hace posible el manejo de las dimensiones track y crosst para referirse a las 
dimensiones en la dirección grid-auto-flow y la dirección alterna respectivamente.
- Refactor de las funciones para la utilización de la clase MapTracks.
- Cambio de nombre de algunas variables para hacerlas más parecidas al uso de nombres de atributos de
en la especificación del grid. Ejemplo row_tracks fue renombrada a grid_template_rows.

v0.1.5
- Cycle Class se define como el tipo asignado a las propiedades grid-auto-rows/grid-auto-columns para
permitir crear tracks (row o column) de forma cíclica. Por ejemplo, grid-auto-flow = 10px 20px 30px 
va creando rows primero de 10px, luego 20px, luego 30px y entonces repite el ciclo.
- Se actualiza el algoritmo de posicionamiento de los widgets en el layout, especialmente en el 
ordenamiento de estos de tal manera que posiciona los elementos con priority 1 y 2, luego crea los 
tracks necesarios para acomodar los widgets de priority 3 y 4.
- Resuelto parse del tipo gird-row o grid-column del tipo span 2 / auto
- Creado en el directorio doc, el directorio showcase destinado a guardar layouts que demuestran la
operación de ciertos aspectos del desarrollo, en este caso del cssgrid.

v0.1.4
- Se creó la property self.master, de solo lectura, para guardar la referencia al master configurado.
- Unificación del registro inicial de responsive, para:
  - Hacer el row_tracks/column_tracks igual a ''
  - La función de arranque entrega los parámetros para la construcción de la función que generara
  para una longitud dada (ancho o largo) el valor adecuado de row_tracks/column_tracks.
- Se generaliza la ejecución de las funciones de configuración responsive.
- Solo la función resize necesita el ancho y altura de la ventana en que se va a desplegar el layout, 
de esta manera se elimina la propagación de estas dimensiones a otros methodos de la clase como see hacía 
antes.
- Se corrigió el error que se presentaba cuado se tenia grid-column/grid-column apuntando a un nombre 
de área.
- Se agregaron nuevos métodos a CssGrid: columnconfigure, rowconfigure, gridbbox, isResponsive, 
responsive_intervals
- Tests actualizados y corriendo perfectamente.

v0.1.3
- Se registra los atributos de los slaves en atributos básicos.
- Se corrigió problema en responsive auto que se presentaba cuando la longitud era menor 
que el min_size del track mediante el acotamiento de la respuesta en este caso a 1 como mínimo.

v0.1.2
- Se optimiza la ejecución de los comandos responsive para actualizar el container solo
cuando cambian las condiciones que definen el número y naturaleza de los tracks ya sea 
en max_size (responsive minmax) o número de tracks (auto-fill/auto-fit). 

v0.1.1
- Operativo la opción repeat(auto-fit, exp) y repeat(auto-fill, exp) en 
grid-template-columns/grid-template-rows.

v0.1.0
- Primera versión de la herramienta UiMonitor que permite cargar un layout y monitorea 
todos los archivos asociados (archivos css, menu, etc) para su despliegue de tal manera que 
modificando uno de estos archivos se vuelve a cargar el layout mostrando el efecto de las 
modificaciones efectuadas.
- Problemas para recargar layout que utilicen variables.

v0.0.3
- Funcionando responsive minmax que permite definir valores para cualquier track de la 
forma 'minmax(min, max), mediante el cual el track tiene un ancho de 'min' y puede crecer hasta 'max'.

v0.0.2
- Funcionando z-index. Se probó con un equivalente al ejemplo https://drafts.csswg.org/css-grid/#z-order.
- Se implementó en css que para el XML parser se interprete el name como id, por tanto ya es posible en 
archivos xml colocar selectores de id. 

v0.0.1
- Inicio la versión del whatsnew.md.
- Funcionando justify-content, align-content y place-content con excepción del caso 
place-content: stretch / stretch; en el que falla el posicionamiento del container.
- Se agrega la variable DEBUG para ejecutarr código solo durante el desarrollo.
- Despliegue de las líneas de grid durante DEBUG.

