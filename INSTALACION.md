# 🚀 Guía de Instalación - Proyecto Reflexo

## 📋 Requisitos Previos

Antes de instalar el proyecto, asegúrate de tener instalado:

- **Python 3.8+** ([Descargar Python](https://www.python.org/downloads/))
- **MySQL Server 8.0+** ([Descargar MySQL](https://dev.mysql.com/downloads/mysql/))
- **Git** ([Descargar Git](https://git-scm.com/downloads))

## 📥 Instalación Paso a Paso

### 1. Clonar el Repositorio
```bash
git clone <URL_DEL_REPOSITORIO>
cd reflexo
```

### 2. Crear y Activar Entorno Virtual

#### En Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### En Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos MySQL

#### 4.1 Crear Base de Datos
Conéctate a MySQL y ejecuta:
```sql
CREATE DATABASE BD_REFLEXO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 4.2 Configurar Credenciales
Edita el archivo `reflexo/settings.py` y actualiza la configuración de la base de datos:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'BD_REFLEXO',
        'USER': 'tu_usuario_mysql',
        'PASSWORD': 'tu_contraseña_mysql',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 5. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:
```bash
# API Key para Google Gemini AI
GEMINI_API_KEY=tu_api_key_aqui

# Configuración de Base de Datos (Opcional)
DB_NAME=BD_REFLEXO
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=3306

# Configuración de Django
SECRET_KEY=tu_secret_key_aqui
DEBUG=True
```

### 6. Aplicar Migraciones
```bash
python manage.py migrate
```

### 7. Crear Superusuario (Opcional)
```bash
python manage.py createsuperuser
```

### 8. Verificar Instalación
```bash
# Verificar conexión a la base de datos
python test_db_connection.py

# Verificar configuración de Django
python manage.py check
```

### 9. Ejecutar Servidor de Desarrollo
```bash
python manage.py runserver
```

El servidor estará disponible en: http://127.0.0.1:8000/

## 🔧 Configuración Adicional

### Obtener API Key de Google Gemini
1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea una nueva API Key
3. Cópiala al archivo `.env`

### Panel de Administración
Accede al panel de administración en: http://127.0.0.1:8000/admin/

## 🐛 Solución de Problemas Comunes

### Error: "No module named 'MySQLdb'"
```bash
# En Windows, instala Visual C++ Build Tools primero
pip install mysqlclient

# Si persiste el error, prueba:
pip install PyMySQL
# Y agrega en settings.py:
import pymysql
pymysql.install_as_MySQLdb()
```

### Error: "Access denied for user"
- Verifica las credenciales de MySQL en `settings.py`
- Asegúrate de que el usuario tenga permisos en la base de datos

### Error: "Can't connect to MySQL server"
- Verifica que MySQL Server esté ejecutándose
- Comprueba el puerto (por defecto 3306)

### Error: "Invalid API Key"
- Verifica que la GEMINI_API_KEY esté correctamente configurada en `.env`
- Asegúrate de que la API Key sea válida y activa

## 📚 Comandos Útiles

```bash
# Crear nuevas migraciones
python manage.py makemigrations

# Ver estado de migraciones
python manage.py showmigrations

# Ejecutar shell de Django
python manage.py shell

# Recopilar archivos estáticos
python manage.py collectstatic

# Ejecutar pruebas
python manage.py test
```

## 🚀 Despliegue en Producción

Para despliegue en producción:

1. Cambia `DEBUG = False` en `settings.py`
2. Configura `ALLOWED_HOSTS` apropiadamente
3. Usa una `SECRET_KEY` segura
4. Configura un servidor web (Nginx + Gunicorn)
5. Usa variables de entorno para credenciales sensibles

## 📞 Soporte

Si encuentras problemas durante la instalación:
1. Revisa esta guía paso a paso
2. Consulta la documentación en los archivos README.md
3. Verifica los logs de error
4. Contacta al equipo de desarrollo

---

¡Listo! Tu proyecto Reflexo debería estar funcionando correctamente. 🎉