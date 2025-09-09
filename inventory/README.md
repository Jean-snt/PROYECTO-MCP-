# Inventory - Aplicación Principal de Inventario Médico

La aplicación `inventory` es el núcleo funcional del sistema Reflexo, implementando toda la lógica de negocio para la gestión inteligente de inventario médico. Integra tecnologías de inteligencia artificial, interfaces web modernas y protocolos de comunicación avanzados para proporcionar una solución completa de gestión farmacéutica.

## 🏗️ Arquitectura de la Aplicación

Esta aplicación sigue el patrón MVT (Model-View-Template) de Django, implementando:
- **Modelos de datos** optimizados para inventario médico
- **Vistas inteligentes** con integración de IA
- **Templates responsivos** para interfaz web
- **APIs RESTful** para comunicación con sistemas externos
- **Comandos personalizados** para operaciones especializadas

## 📁 Estructura Detallada de Archivos

### `models.py` - Modelos de Datos
Define la estructura de datos para el inventario médico con el modelo `Item`:

#### Campos del Modelo Item
```python
class Item(models.Model):
    sku = models.CharField(max_length=50, unique=True)           # Código único del producto
    name = models.CharField(max_length=200)                      # Nombre del medicamento
    medicine_type = models.CharField(max_length=100)             # Tipo de medicamento
    disease_category = models.CharField(max_length=100)          # Categoría de enfermedad
    price = models.DecimalField(max_digits=10, decimal_places=2) # Precio del medicamento
    stock = models.IntegerField()                                # Cantidad en inventario
    created_at = models.DateTimeField(auto_now_add=True)         # Fecha de creación
    updated_at = models.DateTimeField(auto_now=True)             # Fecha de actualización
```

#### Características del Modelo
- **Validación automática**: Campos con restricciones de integridad
- **Timestamps automáticos**: Seguimiento de creación y modificación
- **SKU único**: Identificador único para cada medicamento
- **Campos optimizados**: Tipos de datos apropiados para cada campo

### `views.py` - Lógica de Negocio y Endpoints
Contiene toda la lógica de la aplicación, incluyendo:

#### Vistas Principales
- **`dashboard(request)`**: Vista principal del sistema con inventario completo
- **`chatbot_endpoint(request)`**: Endpoint para el chatbot básico
- **`ChatbotIntelligentView.post(request)`**: Chatbot inteligente con IA
- **`mcp_tool_use(request)`**: Endpoint para herramientas MCP

#### Herramientas de Gestión
- **`create_medicine_tool()`**: Creación inteligente de medicamentos con Gemini AI
- **`get_item_tool(sku)`**: Búsqueda de medicamentos por SKU
- **`delete_medicine_tool(identifier)`**: Eliminación segura de medicamentos
- **`modify_medicine_tool()`**: Modificación interactiva de medicamentos

#### Funciones de Utilidad
- **`normalize_text(text)`**: Normalización de texto para procesamiento
- **`recognize_intent(text)`**: Reconocimiento de intenciones del usuario
- **`get_help_message()`**: Sistema de ayuda contextual

### `urls.py` - Configuración de Rutas
Define el sistema de enrutamiento de la aplicación:

```python
urlpatterns = [
    path('', views.dashboard, name='dashboard'),                    # Dashboard principal
    path('chatbot/', views.chatbot_endpoint, name='chatbot'),       # Chatbot básico
    path('chatbot/intelligent/', views.ChatbotIntelligentView.as_view(), name='chatbot_intelligent'), # Chatbot IA
    path('mcp/tool_use/', views.mcp_tool_use, name='mcp_tool_use'), # Herramientas MCP
]
```

### `admin.py` - Configuración Administrativa
Configura la interfaz de administración de Django:

```python
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'medicine_type', 'price', 'stock']
    list_filter = ['medicine_type', 'disease_category']
    search_fields = ['name', 'sku']
    ordering = ['name']
```

### `apps.py` - Configuración de la Aplicación
Define la configuración de la aplicación Django:

```python
class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'
    verbose_name = 'Inventario Médico'
```

### `tests.py` - Pruebas Unitarias
Contiene las pruebas para validar el funcionamiento de la aplicación:
- Pruebas de modelos
- Pruebas de vistas
- Pruebas de integración con IA
- Pruebas de herramientas MCP

## 📂 Directorios Especializados

### `migrations/` - Migraciones de Base de Datos
Contiene el historial de cambios en la estructura de la base de datos:
- **`0001_initial.py`**: Migración inicial con el modelo Item
- **`README.md`**: Documentación específica de migraciones

#### Gestión de Migraciones
```bash
# Crear nueva migración
python manage.py makemigrations inventory

# Aplicar migraciones
python manage.py migrate inventory

# Ver estado de migraciones
python manage.py showmigrations inventory
```

### `management/commands/` - Comandos Personalizados
Contiene comandos Django personalizados:

#### `run_mcp.py` - Servidor MCP
Comando para ejecutar el servidor MCP (Model Context Protocol):
```bash
python manage.py run_mcp --port 3000
```

**Funcionalidades del Servidor MCP:**
- Comunicación con herramientas de IA
- Protocolo de intercambio de mensajes
- Gestión de sesiones de herramientas
- Logging y monitoreo de operaciones

### `templates/inventory/` - Templates Web
Contiene las plantillas HTML para la interfaz web:

#### `dashboard.html` - Template Principal
- **Interfaz responsiva**: Adaptable a diferentes dispositivos
- **Dashboard interactivo**: Vista completa del inventario
- **Chatbot integrado**: Interfaz de chat en tiempo real
- **Tabla de medicamentos**: Lista completa con funcionalidades de búsqueda

**Características del Template:**
```html
<!-- Estructura principal -->
<div class="dashboard-container">
    <div class="inventory-section"><!-- Lista de medicamentos --></div>
    <div class="chatbot-section"><!-- Interfaz del chatbot --></div>
</div>
```

## 🤖 Integración con Inteligencia Artificial

### Gemini AI Integration
La aplicación utiliza Google Gemini AI para:

#### Creación Inteligente de Medicamentos
```python
def create_medicine_tool(name, medicine_type, disease_category, price, stock):
    # Configuración de Gemini AI
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-pro')
    
    # Generación de contenido inteligente
    prompt = f"Genera información detallada para el medicamento: {name}"
    response = model.generate_content(prompt)
```

#### Capacidades de IA
- **Generación automática**: Información completa de medicamentos
- **Validación inteligente**: Verificación de datos médicos
- **Sugerencias contextuales**: Recomendaciones basadas en patrones
- **Procesamiento de lenguaje natural**: Comprensión de comandos del usuario

### Reconocimiento de Intenciones
Sistema inteligente para interpretar comandos del usuario:

```python
def recognize_intent(text):
    # Patrones de intención
    create_patterns = ['crear', 'agregar', 'añadir', 'nuevo']
    search_patterns = ['buscar', 'encontrar', 'ver', 'mostrar']
    modify_patterns = ['modificar', 'cambiar', 'actualizar', 'editar']
    delete_patterns = ['eliminar', 'borrar', 'quitar', 'remover']
```

## 🔧 Herramientas MCP (Model Context Protocol)

La aplicación implementa herramientas especializadas para diferentes operaciones:

### Herramientas Disponibles

#### 1. `create_medicine_tool`
- **Propósito**: Crear nuevos medicamentos con IA
- **Parámetros**: name, medicine_type, disease_category, price, stock
- **Funcionalidades**: Generación automática de SKU, validación de datos, integración con Gemini AI

#### 2. `get_item_tool`
- **Propósito**: Buscar medicamentos por SKU
- **Parámetros**: sku (código del medicamento)
- **Funcionalidades**: Búsqueda exacta, información detallada, manejo de errores

#### 3. `delete_medicine_tool`
- **Propósito**: Eliminar medicamentos del inventario
- **Parámetros**: identifier (SKU o nombre)
- **Funcionalidades**: Búsqueda flexible, confirmación de seguridad, logging de operaciones

#### 4. `modify_medicine_tool`
- **Propósito**: Modificar medicamentos existentes
- **Parámetros**: identifier, field, new_value, step
- **Funcionalidades**: Modificación interactiva, validación de campos, proceso paso a paso

### Protocolo de Comunicación
```python
# Estructura de mensaje MCP
{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "create_medicine_tool",
        "arguments": {
            "name": "Paracetamol",
            "medicine_type": "Analgésico",
            "disease_category": "Dolor",
            "price": "5.50",
            "stock": "100"
        }
    }
}
```

## 🌐 Endpoints y APIs

### Endpoints Principales

#### Dashboard (`/`)
- **Método**: GET
- **Propósito**: Mostrar interfaz principal
- **Respuesta**: Template HTML con inventario completo

#### Chatbot Básico (`/chatbot/`)
- **Método**: POST
- **Propósito**: Procesamiento básico de comandos
- **Formato**: JSON con mensaje del usuario

#### Chatbot Inteligente (`/chatbot/intelligent/`)
- **Método**: POST
- **Propósito**: Procesamiento avanzado con IA
- **Características**: Reconocimiento de intenciones, estados conversacionales

#### Herramientas MCP (`/mcp/tool_use/`)
- **Método**: POST
- **Propósito**: Comunicación con herramientas MCP
- **Protocolo**: JSON-RPC 2.0

### Formato de Respuestas
```python
# Respuesta exitosa
{
    "success": True,
    "message": "Operación completada exitosamente",
    "data": {
        "item": {
            "sku": "MED001",
            "name": "Paracetamol",
            "price": "5.50"
        }
    }
}

# Respuesta de error
{
    "success": False,
    "message": "Error en la operación",
    "error": "Descripción detallada del error"
}
```

## 🎨 Interfaz de Usuario

### Dashboard Interactivo
- **Diseño responsivo**: Compatible con móviles y escritorio
- **Tabla dinámica**: Lista de medicamentos con búsqueda en tiempo real
- **Chatbot integrado**: Interfaz de chat moderna y funcional
- **Indicadores visuales**: Estados de operaciones y feedback del usuario

### Características de UX
- **Navegación intuitiva**: Flujo de usuario optimizado
- **Feedback inmediato**: Respuestas en tiempo real
- **Manejo de errores**: Mensajes claros y útiles
- **Accesibilidad**: Cumple estándares de accesibilidad web

## 🔍 Funcionalidades Avanzadas

### Sistema de Búsqueda
- **Búsqueda por SKU**: Identificación única exacta
- **Búsqueda por nombre**: Coincidencias parciales
- **Filtros avanzados**: Por tipo, categoría, precio
- **Búsqueda inteligente**: Tolerancia a errores tipográficos

### Validación de Datos
- **Validación de SKU**: Formato y unicidad
- **Validación de precios**: Rangos válidos y formato decimal
- **Validación de stock**: Números enteros positivos
- **Validación de nombres**: Caracteres permitidos y longitud

### Logging y Auditoría
- **Registro de operaciones**: Todas las acciones quedan registradas
- **Timestamps automáticos**: Seguimiento temporal de cambios
- **Identificación de usuarios**: Trazabilidad de modificaciones
- **Logs de errores**: Registro detallado para debugging

## 🧪 Testing y Calidad

### Pruebas Implementadas
- **Pruebas unitarias**: Validación de funciones individuales
- **Pruebas de integración**: Verificación de flujos completos
- **Pruebas de API**: Validación de endpoints y respuestas
- **Pruebas de IA**: Verificación de integración con Gemini

### Comandos de Testing
```bash
# Ejecutar todas las pruebas de inventory
python manage.py test inventory

# Ejecutar pruebas específicas
python manage.py test inventory.tests.TestItemModel

# Ejecutar con coverage
coverage run --source='.' manage.py test inventory
coverage report
```

## 📊 Métricas y Monitoreo

### Métricas del Sistema
- **Operaciones por minuto**: Seguimiento de carga del sistema
- **Tiempo de respuesta**: Monitoreo de rendimiento
- **Tasa de errores**: Identificación de problemas
- **Uso de IA**: Estadísticas de llamadas a Gemini

### Dashboards de Monitoreo
- **Estado del inventario**: Resumen de medicamentos
- **Actividad del chatbot**: Interacciones y comandos
- **Rendimiento del sistema**: Métricas técnicas
- **Errores y alertas**: Monitoreo proactivo

## 🚀 Optimizaciones y Rendimiento

### Optimizaciones de Base de Datos
- **Índices optimizados**: En campos de búsqueda frecuente
- **Consultas eficientes**: Uso de select_related y prefetch_related
- **Cache de consultas**: Para datos frecuentemente accedidos

### Optimizaciones de IA
- **Cache de respuestas**: Evitar llamadas duplicadas a Gemini
- **Timeouts configurables**: Manejo de latencia de API
- **Fallbacks inteligentes**: Respuestas alternativas en caso de fallo

## 🔒 Seguridad y Privacidad

### Medidas de Seguridad
- **Validación de entrada**: Sanitización de todos los inputs
- **Protección CSRF**: Tokens de seguridad en formularios
- **Rate limiting**: Prevención de abuso de APIs
- **Logging de seguridad**: Registro de intentos sospechosos

### Privacidad de Datos
- **Encriptación de datos sensibles**: Información médica protegida
- **Cumplimiento GDPR**: Manejo apropiado de datos personales
- **Auditoría de accesos**: Registro de quién accede a qué información

## 📚 Documentación Adicional

- **`models.md`**: Documentación detallada de modelos de datos
- **`views.md`**: Documentación de vistas y endpoints
- **`migrations/README.md`**: Información sobre migraciones de base de datos

## 🤝 Contribución y Desarrollo

### Guías de Desarrollo
- **Estándares de código**: PEP 8 para Python
- **Documentación**: Docstrings para todas las funciones
- **Testing**: Cobertura mínima del 80%
- **Code review**: Revisión obligatoria de cambios

### Estructura de Commits
```
feat: agregar nueva funcionalidad de búsqueda
fix: corregir error en validación de SKU
docs: actualizar documentación de API
test: agregar pruebas para herramientas MCP
```

Esta aplicación representa el núcleo tecnológico del sistema Reflexo, combinando las mejores prácticas de desarrollo web con tecnologías de inteligencia artificial para crear una solución robusta y escalable de gestión de inventario médico.