v0.0.1
- Inicio la versión del whatsnew.md.
- Funcionando justify-content, align-content y place-content con excepción del caso 
place-content: stretch / stretch; en el que falla el posicionamiento del container.
- Se agrega la variable DEBUG para ejecutarr código solo durante el desarrollo.
- Despliegue de las líneas de grid durante DEBUG.

v0.0.2
- Funcionando z-index. Se probó con un equivalente al ejemplo https://drafts.csswg.org/css-grid/#z-order.
- Se implementó en css que para el XML parser se interprete el name como id, por tanto ya es posible en 
archivos xml colocar selectores de id. 