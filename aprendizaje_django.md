🧠 Historial técnico de JascEcommerce

Este documento resume el proceso completo de desarrollo del proyecto JascEcommerce, desde su inicio como tienda virtual en Django hasta su preparación para producción. Incluye decisiones técnicas, comandos clave, configuraciones, correcciones y aprendizajes.

🚀 1. Inicio del proyecto

Crear entorno virtual:

python -m venv jascenv
source jascenv/bin/activate

Crear proyecto Django:

django-admin startproject JascEcommerce

Crear apps:

python manage.py startapp store
python manage.py startapp home
python manage.py startapp usuario
python manage.py startapp pedidos

🧱 2. Estructura base

Configuración de settings.py: apps instaladas, rutas de templates, archivos estáticos, base de datos.

Creación de base.html con bloques {% block %} reutilizables.

Configuración de urls.py principal y por app.

Primeras vistas y templates: portada, navegación, estructura modular.

🛒 3. Lógica de tienda

Modelos: Product, Factura, DetalleFactura con propiedades para lógica DRY.

Admin personalizado: ProductAdmin con discount, final_price, prepopulated_fields, búsqueda.

Vista de tienda (store.html) con herencia, Swiper, filtros, paginación, vista rápida.

Estilos flotantes en vista_rapida.css, validación visual desde consola.

🎨 4. Estilos y experiencia visual

Archivos CSS organizados por app: store/css, home/css.

Banner full-bleed con Swiper y caption.

Botón "Agregar" con lógica de descuento y estilos responsive.

Validación visual desde consola: ancho, clases, contenedores.

🔐 5. Autenticación y usuarios

App usuario con login, logout, registro, dashboard.

Templates en templates/account/ y registration/.

Decoradores @login_required, redirecciones con LOGIN_URL, LOGIN_REDIRECT_URL.

Namespace account registrado en urls.py principal.

📧 6. Envío de correos

Configuración de SendGrid con API Key.

Verificación de remitente en SendGrid.

Plantilla emails/factura.html simplificada para correo.

Validación desde Django shell con send_mail().

Corrección de errores 401, validación de .env, uso de EmailMessage.

📦 7. Archivos estáticos y producción

Configuración de STATICFILES_DIRS, STATIC_ROOT, STATICFILES_STORAGE.

Uso de Whitenoise con CompressedManifestStaticFilesStorage.

Comando:

python manage.py collectstatic
rm -rf staticfiles/

Validación de carga de CSS con {% static %}.

Eliminación de duplicados, renombrado de archivos, limpieza de rutas.

🧪 8. Pruebas y depuración

Validación de errores en consola y logs.

Corrección de NoReverseMatch por namespace y rutas mal resueltas.

Limpieza de duplicados en estáticos.

Confirmación de flujo completo: login → tienda → pedido → correo.

🧭 9. Próximos pasos

Integrar pagos por Wempi.

Actualizar RUT para credenciales.

Agregar SEO y metatags.

Documentar flujo de despliegue completo.

Crear checklist de producción y pruebas finales.

✅ Comandos útiles

# Activar entorno virtual
source jascenv/bin/activate

# Migraciones
python manage.py makemigrations
python manage.py migrate

# Superusuario
python manage.py createsuperuser

# Recopilar estáticos
python manage.py collectstatic
rm -rf staticfiles/

# Enviar correo desde shell
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail(...)

Este historial refleja el crecimiento técnico del proyecto y sirve como base para futuras mejoras, documentación oficial y portafolio profesional.

📚 Aprendizaje Django

Este documento recopila toda la documentación, aprendizajes y procesos técnicos relacionados con el desarrollo del proyecto Django para JascEcommerce. Incluye desde la creación del entorno y estructura base, hasta la configuración avanzada para producción y despliegue.

🚀 Inicio del proyecto

Creación de entorno virtual y activación.

Inicio del proyecto Django y creación de apps principales.

🧱 Estructura base

Configuración de settings, urls y templates.

Creación de base.html con bloques reutilizables.

🛒 Lógica de tienda

Modelos principales con propiedades para lógica DRY.

Admin personalizado para gestión eficiente.

Vistas y templates con filtros, paginación y vista rápida.

🎨 Estilos y experiencia visual

Organización de CSS por app.

Uso de Swiper para banners y elementos interactivos.

Validación visual y estilos responsive.

🔐 Autenticación y usuarios

Implementación de login, logout, registro y dashboard.

Uso de decoradores y redirecciones.

📧 Envío de correos

Configuración y validación con SendGrid.

Plantillas de correo y pruebas desde Django shell.

📦 Archivos estáticos y producción

Configuración de staticfiles y uso de Whitenoise.

Comandos para recopilación y limpieza.

🧪 Pruebas y depuración

Validación de errores y corrección de rutas.

Confirmación de flujo completo.

🧭 Próximos pasos

Integración de pagos.

SEO y metatags.

Documentación y checklist de producción.

Este archivo servirá como referencia centralizada para el aprendizaje y evolución del proyecto Django en JascEcommerce, facilitando futuras mejoras y documentación profesional.