# models.py - Estructura de la Información

Este archivo define la "estructura de la información" para los medicamentos y órdenes. Es como crear las "cajas" donde se guardan todos los datos, especificando qué tipo de información puede ir en cada compartimento.

## ¿Qué son los Modelos?

Los modelos son como "moldes" o "plantillas" que definen:
- Qué información se puede guardar
- Qué tipo de datos son (texto, números, fechas)
- Qué reglas deben seguir
- Cómo se relacionan entre sí

## Modelos Principales

### Item - El Medicamento

Es la "caja principal" donde se guarda toda la información de un medicamento:

#### Campos de Información

**`sku` (Código Único)**
- **Tipo**: Texto corto (máximo 50 caracteres)
- **Propósito**: Identificador único como una "cédula" del medicamento
- **Características**: No puede repetirse, se genera automáticamente
- **Ejemplo**: "MED001", "ASPI123"

**`name` (Nombre)**
- **Tipo**: Texto (máximo 255 caracteres)
- **Propósito**: Nombre comercial o científico del medicamento
- **Ejemplo**: "Aspirina", "Paracetamol 500mg"

**`description` (Descripción)**
- **Tipo**: Texto largo (sin límite)
- **Propósito**: Información detallada sobre el medicamento
- **Contenido**: Usos, contraindicaciones, composición
- **Puede estar vacío**: Sí, es opcional

**`price` (Precio)**
- **Tipo**: Número decimal (hasta 10 dígitos, 2 decimales)
- **Propósito**: Precio de venta del medicamento
- **Formato**: 99999999.99
- **Ejemplo**: 15.50, 125.00

**`stock` (Inventario)**
- **Tipo**: Número entero
- **Propósito**: Cantidad disponible en el inventario
- **Valor por defecto**: 0 (sin stock)
- **Ejemplo**: 100, 25, 0

**`category` (Categoría)**
- **Tipo**: Texto (máximo 100 caracteres)
- **Propósito**: Clasificación del medicamento
- **Ejemplo**: "Analgésico", "Antibiótico", "Vitamina"

**`medicine_type` (Tipo de Medicina)**
- **Tipo**: Texto (máximo 50 caracteres)
- **Propósito**: Forma farmacéutica del medicamento
- **Ejemplo**: "Tableta", "Jarabe", "Inyección"

**`created_at` (Fecha de Creación)**
- **Tipo**: Fecha y hora
- **Propósito**: Cuándo se registró el medicamento
- **Automático**: Se asigna automáticamente al crear
- **Ejemplo**: "2024-01-15 14:30:25"

**`updated_at` (Fecha de Actualización)**
- **Tipo**: Fecha y hora
- **Propósito**: Cuándo se modificó por última vez
- **Automático**: Se actualiza cada vez que se modifica
- **Ejemplo**: "2024-01-20 09:15:42"

#### Métodos Especiales

**`__str__()`**
- **Propósito**: Define cómo se muestra el medicamento como texto
- **Formato**: "[SKU] Nombre del Medicamento"
- **Ejemplo**: "[MED001] Aspirina 500mg"

**`save()`**
- **Propósito**: Personaliza cómo se guarda el medicamento
- **Función especial**: Genera SKU automáticamente si no existe
- **Formato SKU**: "MED" + número secuencial (MED001, MED002, etc.)

### Order - La Orden de Compra

Es la "caja" que guarda información sobre las compras realizadas:

#### Campos de Información

**`order_code` (Código de Orden)**
- **Tipo**: Texto único (máximo 20 caracteres)
- **Propósito**: Identificador único de la orden
- **Formato**: "ORD" + timestamp
- **Ejemplo**: "ORD1642234567"

**`total` (Total)**
- **Tipo**: Número decimal (hasta 10 dígitos, 2 decimales)
- **Propósito**: Monto total de la orden
- **Valor por defecto**: 0.00
- **Ejemplo**: 245.75, 89.50

**`created_at` (Fecha de Creación)**
- **Tipo**: Fecha y hora
- **Propósito**: Cuándo se creó la orden
- **Automático**: Se asigna al crear

#### Métodos Especiales

**`__str__()`**
- **Formato**: "Orden [CÓDIGO] - $TOTAL"
- **Ejemplo**: "Orden [ORD1642234567] - $245.75"

### OrderLine - Línea de Orden

Es la "caja" que conecta las órdenes con los medicamentos específicos:

#### Campos de Información

**`order` (Orden)**
- **Tipo**: Relación con Order
- **Propósito**: A qué orden pertenece esta línea
- **Comportamiento**: Si se elimina la orden, se eliminan sus líneas

**`item` (Medicamento)**
- **Tipo**: Relación con Item
- **Propósito**: Qué medicamento se está comprando
- **Comportamiento**: Si se elimina el medicamento, se eliminan sus líneas

**`quantity` (Cantidad)**
- **Tipo**: Número entero positivo
- **Propósito**: Cuántas unidades se están comprando
- **Mínimo**: 1
- **Ejemplo**: 2, 5, 10

**`unit_price` (Precio Unitario)**
- **Tipo**: Número decimal (hasta 10 dígitos, 2 decimales)
- **Propósito**: Precio por unidad al momento de la compra
- **Ejemplo**: 15.50, 8.25

**`total_price` (Precio Total)**
- **Tipo**: Número decimal (hasta 10 dígitos, 2 decimales)
- **Propósito**: Precio total de esta línea (cantidad × precio unitario)
- **Ejemplo**: 31.00 (2 × 15.50)

#### Métodos Especiales

**`__str__()`**
- **Formato**: "CANTIDAD × MEDICAMENTO"
- **Ejemplo**: "2 × Aspirina 500mg"

## Relaciones Entre Modelos

### Item ↔ OrderLine
- **Tipo**: Uno a Muchos
- **Significado**: Un medicamento puede estar en muchas líneas de orden
- **Ejemplo**: La Aspirina puede comprarse en diferentes órdenes

### Order ↔ OrderLine
- **Tipo**: Uno a Muchos
- **Significado**: Una orden puede tener muchas líneas (diferentes medicamentos)
- **Ejemplo**: Una orden puede incluir Aspirina, Paracetamol y Vitamina C

## Validaciones y Reglas

### Reglas de Negocio
- Los SKU deben ser únicos
- Los precios no pueden ser negativos
- El stock no puede ser negativo
- Las cantidades en órdenes deben ser positivas

### Validaciones Automáticas
- Django valida tipos de datos automáticamente
- Los campos requeridos no pueden estar vacíos
- Los números decimales respetan el formato especificado
- Las fechas se validan automáticamente

## Analogías para Entender Mejor

### Item (Medicamento) = Ficha de Producto
Como una ficha en una farmacia que contiene:
- Código de barras (SKU)
- Nombre del producto
- Descripción de qué sirve
- Precio de venta
- Cuántos quedan en el estante
- En qué sección está (categoría)
- Qué tipo de medicina es

### Order (Orden) = Recibo de Compra
Como un recibo que muestra:
- Número de recibo único
- Total a pagar
- Fecha y hora de la compra

### OrderLine (Línea de Orden) = Línea del Recibo
Como cada línea en un recibo que muestra:
- Qué producto se compró
- Cuántas unidades
- Precio por unidad
- Total de esa línea

## Importancia de los Modelos

### Organización
- Mantienen los datos estructurados y organizados
- Evitan información duplicada o inconsistente
- Facilitan la búsqueda y modificación de datos

### Seguridad
- Validan que los datos sean correctos antes de guardarlos
- Previenen errores comunes (precios negativos, etc.)
- Mantienen la integridad de la información

### Escalabilidad
- Permiten agregar nuevos campos fácilmente
- Facilitan la creación de nuevas funcionalidades
- Mantienen el código organizado y mantenible

Estos modelos son la base fundamental del sistema, definiendo cómo se almacena y organiza toda la información de medicamentos y órdenes de manera segura y eficiente.