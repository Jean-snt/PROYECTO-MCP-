# run_mcp.py - Servidor de Herramientas MCP

Este archivo es el "servidor de herramientas" que permite que el chatbot se comunique con la base de datos de manera segura y controlada. Es como un "traductor especializado" que entiende las peticiones del chatbot y las convierte en acciones específicas.

## ¿Qué es MCP?

MCP (Model Context Protocol) es un sistema que permite que diferentes programas se comuniquen entre sí de forma segura. En nuestro caso:
- El chatbot hace peticiones
- El servidor MCP las procesa
- Se ejecutan las acciones en la base de datos
- Se devuelven los resultados al chatbot

## Componentes Principales

### Clase Command
Es la estructura principal que Django utiliza para ejecutar comandos personalizados. Permite:
- Configurar el servidor (puerto, host)
- Inicializar las herramientas disponibles
- Mostrar información del sistema

### Recursos MCP
Define qué "recursos" están disponibles:
- **inventory**: Gestión del inventario de medicamentos

Cada recurso tiene:
- Nombre descriptivo
- URI única para identificarlo
- Métodos permitidos (GET, POST, PUT, DELETE)

### Herramientas MCP
Son los "asistentes especializados" que ejecutan tareas específicas:

#### `get_item`
- **Propósito**: Buscar información de un medicamento
- **Entrada**: SKU del medicamento
- **Salida**: Información completa del medicamento
- **Uso**: Para consultar antes de modificar o eliminar

#### `create_medicine`
- **Propósito**: Crear nuevos medicamentos
- **Entrada**: Nombre, tipo, categoría, precio, stock
- **IA Integrada**: Usa Gemini AI para generar información completa
- **Salida**: Confirmación de creación y datos del medicamento

#### `delete_medicine`
- **Propósito**: Eliminar medicamentos del inventario
- **Entrada**: SKU del medicamento
- **Validaciones**: Verifica que el medicamento exista
- **Salida**: Confirmación de eliminación

#### `modify_medicine`
- **Propósito**: Modificar información de medicamentos existentes
- **Entrada**: Identificador, campo a modificar, nuevo valor
- **Flexibilidad**: Permite cambiar cualquier campo
- **Salida**: Confirmación de modificación

## Integración con Gemini AI

### ¿Qué es Gemini?
Gemini es la inteligencia artificial de Google que actúa como "asistente inteligente" para ayudar a crear medicamentos con información completa y profesional.

### Cómo Funciona
1. **Recibe parámetros básicos**: Nombre, tipo, categoría, precio, stock
2. **Genera prompt inteligente**: Crea una solicitud específica para la IA
3. **Procesa respuesta**: Convierte la respuesta de IA en datos estructurados
4. **Crea medicamento**: Guarda la información en la base de datos
5. **Devuelve resultado**: Confirma la creación exitosa

### Beneficios de la IA
- **Consistencia**: Genera información estandarizada
- **Completitud**: Asegura que no falten datos importantes
- **Profesionalismo**: Crea descripciones médicas apropiadas
- **Eficiencia**: Reduce el tiempo de creación manual

## Funciones de Herramientas

### `create_medicine_tool()`
Función que maneja la creación de medicamentos:
- Configura la conexión con Gemini AI
- Genera prompts específicos para medicamentos
- Procesa respuestas JSON de la IA
- Crea instancias del modelo Item
- Maneja errores de forma elegante

### `get_item_tool()`
Función que busca medicamentos:
- Busca por SKU en la base de datos
- Devuelve información completa
- Maneja casos de medicamentos no encontrados
- Formatea fechas para mejor legibilidad

### `delete_medicine_tool()`
Función que elimina medicamentos:
- Verifica existencia antes de eliminar
- Valida que no haya dependencias
- Ejecuta eliminación segura
- Confirma la operación

### `modify_medicine_tool()`
Función que modifica medicamentos:
- Busca el medicamento por identificador
- Valida el campo a modificar
- Aplica el nuevo valor
- Confirma los cambios

## Configuración y Ejecución

### Variables de Entorno
- **GEMINI_API_KEY**: Clave para acceder a la IA de Gemini
- Se carga desde archivo `.env` para seguridad

### Parámetros de Ejecución
- **--host**: Dirección donde ejecutar el servidor (default: localhost)
- **--port**: Puerto de comunicación (default: 8080)

### Comando de Ejecución
```bash
python manage.py run_mcp --host localhost --port 8080
```

## Seguridad y Validaciones

### Validación de Datos
- Verifica que los parámetros requeridos estén presentes
- Valida tipos de datos (números, texto)
- Confirma existencia de medicamentos antes de operaciones

### Manejo de Errores
- Captura errores de conexión con IA
- Maneja problemas de base de datos
- Devuelve mensajes de error claros
- Registra problemas para diagnóstico

### Transacciones Atómicas
- Usa transacciones de Django para operaciones críticas
- Asegura consistencia de datos
- Permite rollback en caso de errores

## Relación con Otros Archivos

### Con `views.py`
- Las vistas llaman a las herramientas MCP
- Procesan las respuestas para el chatbot
- Manejan la interfaz web

### Con `models.py`
- Utiliza los modelos Item, Order, OrderLine
- Crea y modifica instancias de medicamentos
- Respeta las reglas de negocio definidas

### Con el Chatbot
- Recibe peticiones del sistema de chat
- Procesa comandos de usuario
- Devuelve respuestas estructuradas

Este servidor es fundamental porque actúa como el "puente inteligente" entre el chatbot y la base de datos, asegurando que todas las operaciones se realicen de forma segura y eficiente.