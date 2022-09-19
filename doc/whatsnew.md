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

