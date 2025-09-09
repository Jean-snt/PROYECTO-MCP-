# Reflexo - Sistema de Gestión de Inventario Médico

Reflexo es un sistema avanzado de gestión de inventario médico diseñado específicamente para clínicas y centros de salud. Combina la potencia de Django con inteligencia artificial para ofrecer una solución completa y eficiente para la gestión de medicamentos y productos médicos.

## 🚀 Características Principales

### Gestión Inteligente de Inventario
- **Creación Automática**: Utiliza Gemini AI para generar automáticamente información detallada de medicamentos
- **Búsqueda Avanzada**: Sistema de búsqueda inteligente por SKU, nombre o categoría
- **Modificación Flexible**: Permite actualizar cualquier campo de los medicamentos de forma interactiva
- **Eliminación Segura**: Sistema de eliminación con confirmación para evitar pérdidas accidentales

### Interfaz de Usuario Moderna
- **Dashboard Interactivo**: Panel principal con vista completa del inventario
- **Chatbot Inteligente**: Asistente virtual para realizar operaciones mediante lenguaje natural
- **Interfaz Responsiva**: Diseño adaptable para diferentes dispositivos
- **Experiencia Intuitiva**: Navegación simple y eficiente

### Integración con IA
- **Gemini AI**: Integración completa para asistencia inteligente
- **MCP Protocol**: Comunicación avanzada con herramientas de IA
- **Reconocimiento de Intenciones**: El chatbot entiende comandos en lenguaje natural
- **Generación Automática**: Creación inteligente de información de medicamentos

## 🏗️ Arquitectura del Sistema

### Componentes Principales

#### `manage.py`
Punto de entrada principal del sistema Django. Permite ejecutar todos los comandos administrativos y de gestión del proyecto.

#### `reflexo/` - Configuración del Proyecto
Contiene toda la configuración central del sistema:
- Configuración de base de datos
- Configuración de seguridad
- URLs principales
- Configuración de aplicaciones

#### `inventory/` - Aplicación Principal
Corazón del sistema que maneja toda la lógica de inventario:
- Modelos de datos para medicamentos
- Vistas y endpoints de la API
- Templates de la interfaz web
- Comandos personalizados de gestión

## 🛠️ Tecnologías y Herramientas

### Backend
- **Django 4.x**: Framework web robusto y escalable
- **Python 3.11+**: Lenguaje de programación principal
- **SQLite**: Base de datos ligera y eficiente
- **Django REST Framework**: Para APIs RESTful

### Inteligencia Artificial
- **Google Gemini AI**: Modelo de IA para generación de contenido
- **MCP (Model Context Protocol)**: Protocolo de comunicación con IA
- **Natural Language Processing**: Procesamiento de lenguaje natural

### Frontend
- **HTML5/CSS3**: Estructura y estilos modernos
- **JavaScript**: Interactividad y funcionalidades dinámicas
- **Bootstrap**: Framework CSS para diseño responsivo
- **AJAX**: Comunicación asíncrona con el servidor

## 📋 Funcionalidades Detalladas

### 1. Gestión de Medicamentos
- **Crear**: Agregar nuevos medicamentos con información completa
- **Buscar**: Localizar medicamentos por múltiples criterios
- **Modificar**: Actualizar información existente de forma interactiva
- **Eliminar**: Remover medicamentos con confirmación de seguridad

### 2. Chatbot Inteligente
- **Comandos Naturales**: Acepta instrucciones en lenguaje cotidiano
- **Reconocimiento de Intenciones**: Entiende qué operación desea realizar el usuario
- **Respuestas Contextuales**: Proporciona información relevante y útil
- **Ayuda Integrada**: Sistema de ayuda accesible en todo momento

### 3. Dashboard de Control
- **Vista General**: Resumen completo del inventario
- **Estadísticas**: Métricas importantes del sistema
- **Acceso Rápido**: Botones de acceso directo a funciones principales
- **Interfaz Intuitiva**: Diseño centrado en la experiencia del usuario

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.11 o superior
- pip (gestor de paquetes de Python)
- Clave API de Google Gemini

### Pasos de Instalación

1. **Clonar el Repositorio**
   ```bash
   git clone [url-del-repositorio]
   cd reflexo
   ```

2. **Instalar Dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar Variables de Entorno**
   - Crear archivo `.env` en la raíz del proyecto
   - Agregar la clave API de Gemini: `GEMINI_API_KEY=tu_clave_aqui`

4. **Configurar Base de Datos**
   ```bash
   python manage.py migrate
   ```

5. **Iniciar el Servidor**
   ```bash
   python manage.py runserver
   ```

6. **Acceder al Sistema**
   - Abrir navegador en `http://127.0.0.1:8000/`
   - El sistema estará listo para usar

## 📁 Estructura Detallada del Proyecto

```
reflexo/
├── manage.py                    # Comando principal de Django
├── .env                         # Variables de entorno (API keys)
├── README.md                    # Documentación principal
├── requirements.txt             # Dependencias del proyecto
├── reflexo/                     # Configuración del proyecto Django
│   ├── __init__.py
│   ├── settings.py              # Configuración principal
│   ├── urls.py                  # URLs principales
│   ├── wsgi.py                  # Configuración WSGI
│   ├── asgi.py                  # Configuración ASGI
│   └── README.md                # Documentación de configuración
└── inventory/                   # Aplicación principal de inventario
    ├── __init__.py
    ├── admin.py                 # Configuración del admin de Django
    ├── apps.py                  # Configuración de la aplicación
    ├── models.py                # Modelos de datos
    ├── views.py                 # Vistas y lógica de negocio
    ├── urls.py                  # URLs de la aplicación
    ├── tests.py                 # Pruebas unitarias
    ├── README.md                # Documentación de la aplicación
    ├── models.md                # Documentación de modelos
    ├── views.md                 # Documentación de vistas
    ├── management/              # Comandos personalizados
    │   └── commands/
    │       └── run_mcp.py       # Comando MCP
    ├── migrations/              # Migraciones de base de datos
    │   ├── 0001_initial.py
    │   └── README.md
    └── templates/               # Templates HTML
        └── inventory/
            └── dashboard.html   # Template principal
```

## 🔧 Comandos Útiles

### Desarrollo
```bash
# Iniciar servidor de desarrollo
python manage.py runserver

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Ejecutar pruebas
python manage.py test

# Iniciar servidor MCP
python manage.py run_mcp
```

### Producción
```bash
# Recopilar archivos estáticos
python manage.py collectstatic

# Crear superusuario
python manage.py createsuperuser
```

## 📖 Documentación Adicional

Cada componente del sistema cuenta con documentación específica:

- **`reflexo/README.md`**: Configuración del proyecto Django
- **`inventory/README.md`**: Aplicación de inventario médico
- **`inventory/models.md`**: Documentación de modelos de datos
- **`inventory/views.md`**: Documentación de vistas y endpoints
- **`inventory/migrations/README.md`**: Información sobre migraciones

## 🤝 Contribución

Para contribuir al proyecto:
1. Fork el repositorio
2. Crear una rama para tu feature
3. Realizar los cambios necesarios
4. Ejecutar las pruebas
5. Enviar un pull request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo LICENSE para más detalles.

## 🆘 Soporte

Para soporte técnico o preguntas sobre el sistema:
- Revisar la documentación en cada carpeta
- Consultar los archivos .md específicos
- Verificar los logs del sistema
- Contactar al equipo de desarrollo