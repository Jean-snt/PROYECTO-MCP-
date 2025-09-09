# Reflexo - Configuración del Proyecto Django

Este directorio contiene la configuración central del proyecto Django Reflexo. Actúa como el núcleo del sistema, definiendo la arquitectura, configuraciones de seguridad, enrutamiento y la integración entre todos los componentes del sistema de gestión de inventario médico.

## 🏗️ Arquitectura del Proyecto

Esta carpeta implementa el patrón de arquitectura Django estándar, proporcionando:
- **Configuración centralizada** del proyecto
- **Enrutamiento principal** de URLs
- **Configuración de despliegue** para diferentes entornos
- **Integración de aplicaciones** Django

## 📁 Estructura de Archivos

### `__init__.py`
Archivo que marca este directorio como un paquete Python, permitiendo la importación de módulos.

### `settings.py` - Configuración Principal
Archivo central de configuración que define:

#### Configuración de Base de Datos
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

#### Aplicaciones Instaladas
- `django.contrib.admin` - Panel de administración
- `django.contrib.auth` - Sistema de autenticación
- `django.contrib.contenttypes` - Framework de tipos de contenido
- `django.contrib.sessions` - Framework de sesiones
- `django.contrib.messages` - Framework de mensajes
- `django.contrib.staticfiles` - Gestión de archivos estáticos
- `inventory` - Aplicación principal de inventario médico

#### Configuración de Seguridad
- **SECRET_KEY**: Clave secreta para operaciones criptográficas
- **DEBUG**: Modo de depuración (False en producción)
- **ALLOWED_HOSTS**: Hosts permitidos para el despliegue
- **CSRF_TRUSTED_ORIGINS**: Orígenes confiables para CSRF

#### Configuración de Internacionalización
- **LANGUAGE_CODE**: 'es-es' (Español de España)
- **TIME_ZONE**: 'UTC' (Tiempo Universal Coordinado)
- **USE_I18N**: Internacionalización habilitada
- **USE_TZ**: Soporte de zonas horarias habilitado

#### Configuración de Archivos Estáticos
- **STATIC_URL**: URL base para archivos estáticos
- **STATICFILES_DIRS**: Directorios adicionales de archivos estáticos
- **STATIC_ROOT**: Directorio para archivos estáticos en producción

### `urls.py` - Configuración de Enrutamiento
Define el sistema de enrutamiento principal del proyecto:

#### Rutas Principales
```python
urlpatterns = [
    path('admin/', admin.site.urls),           # Panel de administración Django
    path('', include('inventory.urls')),       # Aplicación de inventario (raíz)
]
```

#### Funcionalidades de Enrutamiento
- **Enrutamiento jerárquico**: Delega rutas específicas a aplicaciones
- **Inclusión de URLs**: Permite modularidad en la definición de rutas
- **Configuración de admin**: Acceso al panel administrativo de Django

### `wsgi.py` - Configuración WSGI
Interfaz de servidor web para aplicaciones Python síncronas:

#### Características
- **Compatibilidad con servidores web**: Apache, Nginx, Gunicorn
- **Configuración de producción**: Optimizada para despliegue
- **Gestión de aplicaciones**: Punto de entrada para servidores WSGI

#### Uso en Producción
```bash
# Ejemplo con Gunicorn
gunicorn reflexo.wsgi:application
```

### `asgi.py` - Configuración ASGI
Interfaz de servidor web para aplicaciones Python asíncronas:

#### Características
- **Soporte asíncrono**: Manejo de conexiones WebSocket
- **Compatibilidad moderna**: Servidores como Daphne, Uvicorn
- **Escalabilidad**: Mejor rendimiento para aplicaciones en tiempo real

#### Uso en Producción
```bash
# Ejemplo con Uvicorn
uvicorn reflexo.asgi:application
```

## 🔧 Configuraciones Específicas del Sistema

### Integración con Gemini AI
El sistema está configurado para trabajar con la API de Google Gemini:
- Variables de entorno para claves API
- Configuración de timeouts y límites de rate
- Manejo de errores de conectividad

### Configuración de MCP (Model Context Protocol)
- Endpoints específicos para comunicación con herramientas de IA
- Configuración de serialización JSON
- Manejo de protocolos de comunicación

### Configuración de Seguridad Médica
- Cumplimiento con estándares de privacidad de datos médicos
- Configuración de logs de auditoría
- Protección de información sensible

## 🌐 Configuración de Entornos

### Desarrollo
```python
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

### Producción
```python
DEBUG = False
ALLOWED_HOSTS = ['tu-dominio.com']
SECURE_SSL_REDIRECT = True
```

### Testing
```python
DATABASES['default']['NAME'] = ':memory:'
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
```

## 🔗 Integración con Aplicaciones

### Aplicación Inventory
- **Modelos**: Integración con modelos de medicamentos
- **URLs**: Inclusión de rutas de inventario
- **Templates**: Configuración de directorios de plantillas
- **Static Files**: Gestión de archivos CSS/JS específicos

### Sistema de Administración
- **Django Admin**: Panel administrativo personalizado
- **Permisos**: Configuración de roles y permisos
- **Interfaz**: Personalización de la interfaz administrativa

## 📊 Monitoreo y Logging

### Configuración de Logs
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'reflexo.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Métricas del Sistema
- Seguimiento de operaciones de inventario
- Monitoreo de uso de IA
- Análisis de rendimiento de endpoints

## 🚀 Comandos de Gestión

### Configuración Inicial
```bash
# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recopilar archivos estáticos
python manage.py collectstatic
```

### Desarrollo
```bash
# Servidor de desarrollo
python manage.py runserver

# Shell interactivo
python manage.py shell

# Verificar configuración
python manage.py check
```

### Producción
```bash
# Verificar despliegue
python manage.py check --deploy

# Limpiar sesiones expiradas
python manage.py clearsessions
```

## 🔒 Consideraciones de Seguridad

### Variables de Entorno
Todas las configuraciones sensibles deben definirse en el archivo `.env`:
```env
SECRET_KEY=tu_clave_secreta_aqui
GEMINI_API_KEY=tu_clave_gemini_aqui
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com
```

### Mejores Prácticas
- **Nunca** commitear claves API al repositorio
- Usar HTTPS en producción
- Configurar CSRF protection adecuadamente
- Implementar rate limiting para APIs
- Mantener Django actualizado

## 📈 Escalabilidad

### Base de Datos
- Configuración para PostgreSQL en producción
- Índices optimizados para consultas frecuentes
- Connection pooling para mejor rendimiento

### Cache
- Configuración de Redis para cache
- Cache de sesiones y consultas frecuentes
- Invalidación inteligente de cache

### Load Balancing
- Configuración para múltiples instancias
- Sesiones compartidas entre servidores
- Archivos estáticos servidos por CDN

## 🧪 Testing

### Configuración de Pruebas
```python
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
```

### Comandos de Testing
```bash
# Ejecutar todas las pruebas
python manage.py test

# Ejecutar pruebas específicas
python manage.py test inventory.tests

# Ejecutar con coverage
coverage run --source='.' manage.py test
```

## 📚 Referencias

- [Documentación oficial de Django](https://docs.djangoproject.com/)
- [Django Settings Reference](https://docs.djangoproject.com/en/stable/ref/settings/)
- [Django URL Dispatcher](https://docs.djangoproject.com/en/stable/topics/http/urls/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)