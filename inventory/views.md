# views.py - El Traductor del Chatbot

Este archivo es el "traductor" entre el chatbot y las herramientas MCP. Actúa como un "intérprete inteligente" que entiende los comandos del usuario y decide qué herramienta activar para ejecutar la acción correcta.

## ¿Qué son las Vistas?

Las vistas son como "recepcionistas especializadas" que:
- Reciben peticiones del chatbot
- Interpretan qué quiere hacer el usuario
- Llaman a la herramienta correcta
- Devuelven la respuesta al chatbot
- Manejan errores de forma elegante

## Vista Principal: `chatbot_api`

Es la función principal que maneja todas las interacciones del chatbot.

### ¿Cómo Funciona?

#### 1. Recepción de Peticiones
- **Método HTTP**: Solo acepta POST (para enviar datos)
- **Formato**: Recibe datos en formato JSON
- **Validación**: Verifica que la petición sea válida

#### 2. Procesamiento de Datos
```python
data = json.loads(request.body)
message = data.get('message', '')
```
- Extrae el mensaje del usuario
- Convierte el JSON en datos utilizables
- Prepara la información para procesamiento

#### 3. Interpretación Inteligente
La vista analiza el mensaje del usuario para determinar la intención:

**Palabras Clave para CREAR:**
- "crear", "create", "nuevo", "agregar", "añadir"
- **Acción**: Llama a `create_medicine_tool`
- **Resultado**: Nuevo medicamento en el inventario

**Palabras Clave para BUSCAR:**
- "buscar", "search", "encontrar", "ver", "mostrar"
- **Acción**: Llama a `get_item_tool`
- **Resultado**: Información del medicamento solicitado

**Palabras Clave para MODIFICAR:**
- "modificar", "modify", "cambiar", "actualizar", "editar"
- **Acción**: Llama a `modify_medicine_tool`
- **Resultado**: Medicamento actualizado con nuevos datos

**Palabras Clave para ELIMINAR:**
- "eliminar", "delete", "borrar", "quitar", "remover"
- **Acción**: Llama a `delete_medicine_tool`
- **Resultado**: Medicamento eliminado del inventario

#### 4. Extracción de Parámetros
La vista es inteligente y extrae automáticamente los parámetros necesarios:

**Para CREAR medicamentos:**
- Busca: nombre, tipo, categoría, precio, stock
- Ejemplo: "Crear aspirina tableta analgésico 15.50 100"
- Extrae: name="aspirina", type="tableta", category="analgésico", price=15.50, stock=100

**Para BUSCAR medicamentos:**
- Busca: SKU o nombre del medicamento
- Ejemplo: "Buscar MED001" o "Buscar aspirina"
- Extrae: sku="MED001" o name="aspirina"

**Para MODIFICAR medicamentos:**
- Busca: identificador, campo a cambiar, nuevo valor
- Ejemplo: "Modificar MED001 precio 20.00"
- Extrae: identifier="MED001", field="precio", value="20.00"

**Para ELIMINAR medicamentos:**
- Busca: SKU del medicamento
- Ejemplo: "Eliminar MED001"
- Extrae: sku="MED001"

#### 5. Comunicación con MCP
La vista se conecta con el servidor MCP:

```python
with mcp.ClientSession(transport) as session:
    result = await session.call_tool(tool_name, arguments)
```

**Proceso de Comunicación:**
1. **Establece conexión**: Se conecta al servidor MCP
2. **Envía petición**: Llama a la herramienta específica
3. **Recibe respuesta**: Obtiene el resultado de la operación
4. **Cierra conexión**: Termina la comunicación de forma segura

#### 6. Procesamiento de Respuestas
La vista procesa las respuestas del servidor MCP:

**Respuestas Exitosas:**
- Extrae el contenido útil
- Formatea la información para el usuario
- Devuelve mensaje de confirmación

**Respuestas con Error:**
- Identifica el tipo de error
- Genera mensaje de error amigable
- Registra el problema para diagnóstico

#### 7. Respuesta al Chatbot
Finalmente, devuelve la respuesta en formato JSON:

```python
return JsonResponse({
    'response': mensaje_para_usuario,
    'status': 'success' o 'error'
})
```

## Manejo de Errores

### Tipos de Errores Manejados

**Errores de Conexión:**
- Servidor MCP no disponible
- Problemas de red
- Timeout de conexión

**Errores de Datos:**
- Parámetros faltantes
- Formato de datos incorrecto
- Medicamento no encontrado

**Errores del Sistema:**
- Problemas de base de datos
- Errores de la IA Gemini
- Fallos internos del servidor

### Respuestas de Error Amigables

**Para el Usuario:**
- Mensajes claros y comprensibles
- Sugerencias de cómo corregir el problema
- Evita términos técnicos complicados

**Para el Sistema:**
- Logs detallados para diagnóstico
- Información técnica para desarrolladores
- Trazabilidad completa del error

## Flujo de Trabajo Completo

### Ejemplo: Crear un Medicamento

1. **Usuario escribe**: "Crear paracetamol tableta analgésico 12.50 50"
2. **Vista recibe**: Petición POST con el mensaje
3. **Vista interpreta**: Identifica intención "crear"
4. **Vista extrae**: name="paracetamol", type="tableta", etc.
5. **Vista llama**: `create_medicine_tool` con parámetros
6. **MCP procesa**: Usa IA Gemini para crear medicamento completo
7. **MCP responde**: Confirmación de creación exitosa
8. **Vista formatea**: Mensaje amigable para el usuario
9. **Usuario recibe**: "Medicamento paracetamol creado exitosamente con SKU MED123"

### Ejemplo: Buscar un Medicamento

1. **Usuario escribe**: "Buscar aspirina"
2. **Vista recibe**: Petición con mensaje de búsqueda
3. **Vista interpreta**: Identifica intención "buscar"
4. **Vista extrae**: name="aspirina"
5. **Vista llama**: `get_item_tool` con parámetro
6. **MCP busca**: En base de datos por nombre
7. **MCP responde**: Información completa del medicamento
8. **Vista formatea**: Datos organizados para mostrar
9. **Usuario recibe**: Información detallada de la aspirina

## Configuración y Conexión MCP

### Parámetros de Conexión
- **Host**: localhost (servidor local)
- **Puerto**: 8080 (puerto de comunicación)
- **Protocolo**: TCP/IP para comunicación rápida

### Transporte de Datos
```python
transport = StdioServerTransport(
    command="python",
    args=["manage.py", "run_mcp"],
    cwd=settings.BASE_DIR
)
```

## Seguridad y Validaciones

### Validaciones de Entrada
- Verifica que el método HTTP sea POST
- Valida formato JSON de la petición
- Sanitiza datos de entrada
- Previene inyección de código

### Manejo Seguro de Datos
- No expone información sensible
- Valida permisos antes de operaciones
- Registra actividades para auditoría
- Maneja sesiones de forma segura

## Relación con Otros Archivos

### Con `run_mcp.py`
- **Dependencia**: Necesita que el servidor MCP esté ejecutándose
- **Comunicación**: Envía peticiones y recibe respuestas
- **Sincronización**: Debe usar las mismas herramientas definidas

### Con `models.py`
- **Indirecta**: No accede directamente a los modelos
- **A través de MCP**: Las herramientas MCP manejan los modelos
- **Consistencia**: Respeta las reglas de negocio definidas

### Con `urls.py`
- **Registro**: Se registra como endpoint `/mcp_tool_use/`
- **Acceso**: Permite que el chatbot acceda a la funcionalidad
- **Routing**: Django dirige las peticiones a esta vista

## Ventajas de esta Arquitectura

### Separación de Responsabilidades
- **Vista**: Solo maneja comunicación web
- **MCP**: Solo maneja lógica de negocio
- **Modelos**: Solo manejan datos

### Escalabilidad
- Fácil agregar nuevas funcionalidades
- Modificaciones independientes en cada capa
- Reutilización de componentes

### Mantenibilidad
- Código organizado y limpio
- Fácil localización de problemas
- Actualizaciones sin afectar otros componentes

### Flexibilidad
- Puede manejar diferentes tipos de peticiones
- Adaptable a nuevos requerimientos
- Compatible con diferentes interfaces de usuario

Esta vista es fundamental porque actúa como el "cerebro comunicativo" del sistema, interpretando las intenciones del usuario y coordinando todas las operaciones de manera inteligente y segura.